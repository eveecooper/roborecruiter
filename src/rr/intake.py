"""Taking a posting in by hand: step 1.1.

Manual intake is a posting source rather than a special case, so this module does what every
later source will do - produce a `Posting` carrying the whole text and a content hash. It fetches
nothing; the text arrives already pasted. See docs/adr/0001-phased-delivery.md.

Posting text is untrusted data. It is hashed, written to a file, and stored - never used as a
path, a filename, or an instruction. The folder name is built from a slug that keeps only
`[a-z0-9-]`, so nothing in a posting can reach outside the applications directory.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlmodel import Session, select

from rr.models import Posting
from rr.paths import DataRoot

#: Anything outside this set becomes a separator in a folder slug. Kept as a pattern string
#: rather than a compiled object because `tests/test_safety.py` forbids `compile(` outright, and
#: that assertion is not relaxed to suit a caller. `re` caches patterns internally anyway.
_SLUG_DISALLOWED = r"[^a-z0-9]+"
_SLUG_MAX = 48

#: Query parameters that carry the employer's own posting ID. Checked in this order, so a link
#: with more than one wins on the most specific. Guessing from the link is deliberate: forgetting
#: to pass the ID is the expected human error, and a flagged guess beats a missing value.
_JOB_ID_PARAMS = ("jobid", "gh_jid", "job_id", "requisitionid", "req_id", "reqid", "pid")

#: Stands in when no employer can be worked out. A placeholder the applicant can see and fix
#: beats inventing a name that would end up in a document.
UNKNOWN_EMPLOYER = "unknown-employer"

#: Host labels that name a hiring page rather than the employer, stripped before guessing.
_HOST_NOISE = frozenset({"www", "careers", "career", "jobs", "job", "apply", "boards", "hiring"})

#: Second-level labels that are part of a public suffix, so the employer is one label further in.
_PUBLIC_SECOND_LEVEL = frozenset({"co", "com", "org", "net", "ac", "gov", "edu"})

#: A guessed title longer than this is almost certainly a paragraph, not a title.
_TITLE_MAX = 120

#: Labels a careers page puts above the requisition number. Matched case-insensitively against a
#: whole line, with the value either after a colon on the same line or on the next non-blank line.
_JOB_ID_LABELS = (
    "job id",
    "job no",
    "job number",
    "job req id",
    "requisition id",
    "requisition number",
    "requisition",
    "req id",
    "req no",
    "req #",
    "req",
    "posting id",
    "reference number",
    "reference id",
    "ref id",
    "ref #",
)

#: Labels a careers page puts above the role name.
_TITLE_LABELS = ("job title", "position title", "position", "job", "title", "role")

#: Labelled fields sit in the header of a posting. Searching the whole body would match prose
#: about how to apply and pick up a number that is not a requisition.
_LABEL_SCAN_LINES = 25

#: A value this long is prose that followed a label, not an identifier.
_JOB_ID_MAX = 40

#: Query parameters that identify where a link was copied from rather than which job it is.
#: Dropping them is what makes the same posting reached from a search result and from a direct
#: link one posting. Everything not listed here is kept - `jobId` is the job.
_TRACKING_PARAMS = frozenset(
    {
        "source",
        "src",
        "ref",
        "referrer",
        "gh_src",
        "trackingid",
        "trk",
        "origin",
        "mc_cid",
        "mc_eid",
        "fbclid",
        "gclid",
    }
)


@dataclass(frozen=True)
class Intake:
    """What one `add` did, so the caller can report it without re-querying."""

    posting: Posting
    #: False when this posting was already known, so the caller can say so rather than
    #: imply a new row.
    created: bool
    folder: Path
    #: True when a known posting came back with different text - the employer edited it.
    text_changed: bool = False
    #: Fields a repeat paste corrected on an existing row, so the caller can report them.
    fields_changed: tuple[str, ...] = ()
    #: Fields filled by guess rather than given. Flagged so a wrong one is visible, per ADR 0003.
    guessed: tuple[str, ...] = ()
    #: The link's job ID when it disagrees with the one the posting prints. Reported rather than
    #: resolved: one of the two is wrong and only the applicant can say which.
    job_id_conflict: str | None = None


def content_hash(text: str) -> str:
    """Hash the posting text, after normalising whitespace that carries no meaning.

    A posting pasted twice differs in line endings and trailing spaces far more often than in
    content, and treating those as different postings would defeat the duplicate check.
    """
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def normalize_url(url: str | None) -> str | None:
    """Strip the parts of a link that say where it was copied from, not which job it is.

    Lowercases the host, drops the fragment and any `utm_*` or known tracking parameter, and
    sorts what remains so parameter order cannot make one posting look like two.
    """
    if not url or not url.strip():
        return None
    parsed = urlsplit(url.strip())
    kept = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in _TRACKING_PARAMS and not key.lower().startswith("utm_")
    ]
    path = parsed.path.rstrip("/") or parsed.path
    return urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, urlencode(sorted(kept)), "")
    )


def normalize_text(text: str) -> str:
    """Line endings to `\\n`, trailing whitespace off each line, blank edges trimmed."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip()


def read_labelled_field(text: str, labels: tuple[str, ...]) -> str | None:
    """The value of the first of `labels` that appears in the posting's header, if any.

    Careers pages lay a posting out as a label and then its value - "Job ID" on one line and the
    number on the next, or "Job ID: 132846" on one. Both forms are read. Only the first
    `_LABEL_SCAN_LINES` lines are searched, because the same words appear in prose further down.

    Rules, not a model: stage 1 ships neither a model nor network access
    (docs/adr/0005-stage1-no-model-no-network.md), so a label the posting already prints is the
    only reliable thing to read.
    """
    lines = [line.strip() for line in normalize_text(text).split("\n")]
    header = lines[:_LABEL_SCAN_LINES]

    for index, line in enumerate(header):
        bare = line.rstrip(":").strip().lower()
        for label in labels:
            if bare == label:
                # Label alone on its line: the value is the next line with anything on it.
                for following in lines[index + 1 :]:
                    if following:
                        return following
                return None
            if bare.startswith(label):
                remainder = line[len(label) :].lstrip(" :#\t-").strip()
                if remainder:
                    return remainder
    return None


def read_job_id(text: str) -> str | None:
    """The requisition number the posting prints for itself, if it labels one."""
    value = read_labelled_field(text, _JOB_ID_LABELS)
    if not value or len(value) > _JOB_ID_MAX:
        return None
    # An identifier, not a sentence. Anything with spaces in it is the latter.
    return value if value and " " not in value else None


def guess_title(text: str) -> str:
    """The role name: a labelled title if the posting prints one, else the first non-blank line.

    The fallback is wrong on a posting whose first line is the word "Job Title", which is exactly
    how a copied careers page tends to start - hence the labels first.
    """
    labelled = read_labelled_field(text, _TITLE_LABELS)
    if labelled:
        return labelled[:_TITLE_MAX]
    for line in normalize_text(text).split("\n"):
        candidate = line.strip().lstrip("#").strip()
        if candidate:
            return candidate[:_TITLE_MAX]
    return "untitled posting"


def employer_key(employer: str) -> str:
    """An employer name reduced to a comparable key: letters and digits, lowercased.

    `ibm`, `IBM` and `I.B.M.` are one employer. The name itself is a guess the applicant can
    correct, so the duplicate key must not depend on how it happened to be written.
    """
    return re.sub(r"[^a-z0-9]+", "", employer.lower())


def guess_job_id(url: str | None) -> str | None:
    """The employer's posting ID from the link's query string, if it is in there.

    Query parameters only. A number sitting in a path segment is as likely to be a page index or
    a category as a requisition, and a wrong ID is worse than none - it would group two unrelated
    postings under one duplicate key.
    """
    if not url:
        return None
    params = {key.lower(): value for key, value in parse_qsl(urlsplit(url).query)}
    for name in _JOB_ID_PARAMS:
        value = params.get(name, "").strip()
        if value:
            return value
    return None


def guess_employer(url: str | None) -> str:
    """The employer's name from the link's host, or the placeholder when there is no link.

    A heuristic, not a lookup: `jobs.lever.co/acme` gives "lever", which is the hosting platform
    rather than the employer. That is why the result is reported as a guess.
    """
    if not url:
        return UNKNOWN_EMPLOYER
    host = urlsplit(url).netloc.split("@")[-1].split(":")[0].lower()
    labels = [label for label in host.split(".") if label and label not in _HOST_NOISE]
    if len(labels) < 2:
        return labels[0] if labels else UNKNOWN_EMPLOYER
    if labels[-2] in _PUBLIC_SECOND_LEVEL and len(labels) >= 3:
        return labels[-3]
    return labels[-2]


def slug(*parts: str) -> str:
    """A short folder-safe label. Returns `"posting"` when nothing usable survives."""
    joined = "-".join(parts).lower()
    cleaned = re.sub(_SLUG_DISALLOWED, "-", joined).strip("-")
    return cleaned[:_SLUG_MAX].strip("-") or "posting"


def add(
    session: Session,
    root: DataRoot,
    *,
    url: str | None,
    text: str,
    title: str | None = None,
    employer: str | None = None,
    job_id: str | None = None,
    source: str = "manual",
) -> Intake:
    """Record one pasted posting: a row carrying the full text, and a `posting.md` beside it.

    A posting already known - by employer plus job ID, by URL, or by text hash - is updated
    rather than duplicated, so pasting the same posting twice is safe and says so. A missing
    title, employer or job ID is guessed and reported rather than asked for, because no step of
    this pipeline halts for a person (ADR 0003).
    """
    canonical = normalize_url(url)

    guessed: list[str] = []
    if not title:
        title = guess_title(text)
        guessed.append("title")
    if not employer:
        employer = guess_employer(canonical)
        guessed.append("employer")
    # The posting's own printed requisition number beats the one in the link: it is what the
    # employer calls this opening. A link that disagrees is flagged, not silently discarded.
    from_link = guess_job_id(canonical)
    conflict: str | None = None
    if not job_id:
        job_id = read_job_id(text) or from_link
        if job_id:
            guessed.append("job_id")
    if from_link and job_id and from_link != job_id:
        conflict = from_link

    known = find_existing(session, url=canonical, text=text, employer=employer, job_id=job_id)
    if known is not None:
        return _seen_again(
            session,
            root,
            known,
            url=canonical,
            text=text,
            title=title if "title" not in guessed else None,
            employer=employer if "employer" not in guessed else None,
            job_id=job_id,
            conflict=conflict,
        )

    posting = Posting(
        employer_name=employer,
        employer_key=employer_key(employer),
        title=title,
        source_posting_id=job_id,
        url=canonical,
        text=text,
        text_hash=content_hash(text),
        source=source,
    )
    session.add(posting)
    # Flush rather than commit: the row id is part of the folder name, and a failed file write
    # should not leave a posting row pointing at a folder that was never created.
    session.flush()

    folder = root.applications / f"{posting.id:04d}-{slug(employer, title)}"
    _write_posting_file(folder, posting)
    session.commit()
    session.refresh(posting)
    return Intake(
        posting=posting,
        created=True,
        folder=folder,
        guessed=tuple(guessed),
        job_id_conflict=conflict,
    )


def _seen_again(
    session: Session,
    root: DataRoot,
    posting: Posting,
    *,
    url: str | None,
    text: str,
    title: str | None = None,
    employer: str | None = None,
    job_id: str | None = None,
    conflict: str | None = None,
) -> Intake:
    """Fold a repeat paste into the row that already exists.

    Seeing a posting again is information - it was still open on this date - so `last_seen`
    moves. If the body changed, the employer edited the posting, and the newer text replaces
    the old one because the database is the truth for posting text (ADR 0009).

    A title or employer passed explicitly corrects what was stored, because `add` tells the
    applicant to re-run with those flags to fix a guess. Omitting them changes nothing: the
    guess is never re-run over a value that is already there.
    """
    new_hash = content_hash(text)
    changed = new_hash != posting.text_hash

    posting.last_seen = datetime.now(UTC)
    if changed:
        posting.text = text
        posting.text_hash = new_hash
        posting.updated_at = posting.last_seen
    fields: list[str] = []
    if url and not posting.url:
        posting.url = url
        fields.append("url")
    if title and title != posting.title:
        posting.title = title
        fields.append("title")
    if employer and employer != posting.employer_name:
        posting.employer_name = employer
        posting.employer_key = employer_key(employer)
        fields.append("employer")
    # Filling in a job ID that was missing is the case this was asked for. A *different* ID is
    # left alone: it is the strongest duplicate key, and silently repointing it would merge two
    # requisitions under one row.
    if job_id and not posting.source_posting_id:
        posting.source_posting_id = job_id
        fields.append("job_id")
    if fields:
        posting.updated_at = posting.last_seen

    session.add(posting)
    folder = folder_for(root, posting)
    _write_posting_file(folder, posting)
    session.commit()
    session.refresh(posting)
    return Intake(
        posting=posting,
        created=False,
        folder=folder,
        text_changed=changed,
        fields_changed=tuple(fields),
        job_id_conflict=conflict,
    )


def folder_for(root: DataRoot, posting: Posting) -> Path:
    """This posting's folder, found by its id prefix.

    The id is in the name and the id never changes, so the folder is found rather than rebuilt -
    a later edit to the title cannot strand the files under a name nothing computes any more.
    """
    assert posting.id is not None, "posting must be flushed before it has a folder"
    prefix = f"{posting.id:04d}-"
    if root.applications.is_dir():
        for candidate in sorted(root.applications.glob(f"{prefix}*")):
            if candidate.is_dir():
                return candidate
    return root.applications / f"{prefix}{slug(posting.employer_name, posting.title)}"


def _write_posting_file(folder: Path, posting: Posting) -> bool:
    """Bring `posting.md` into agreement with the row. Returns True if it was written.

    Tool-owned: the database is the truth for posting text and this file is the readable copy,
    so it is reconciled on every add rather than only when something looks changed. A file left
    disagreeing with its row would never be noticed, because nothing after this reads it back.
    """
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "posting.md"
    body = _render_posting_file(posting)
    if path.is_file() and path.read_text(encoding="utf-8") == body:
        return False
    path.write_text(body, encoding="utf-8")
    return True


def _render_posting_file(posting: Posting) -> str:
    """The exact contents `posting.md` should have for this row."""
    header = [
        "<!-- Written by `rr add`. The database is authoritative for this text;",
        "     edits here are not read back. -->",
        "",
        f"# {posting.title}",
        "",
        f"- **Employer:** {posting.employer_name}",
        f"- **Job ID:** {posting.source_posting_id or '(not recorded)'}",
        f"- **URL:** {posting.url or '(none given)'}",
        f"- **Added:** {posting.first_seen.isoformat(timespec='seconds')}",
        f"- **Source:** {posting.source}",
        f"- **Text hash:** `{posting.text_hash}`",
        "",
        "---",
        "",
    ]
    return "\n".join(header) + normalize_text(posting.text) + "\n"


def find_existing(
    session: Session,
    *,
    url: str | None,
    text: str,
    employer: str | None,
    job_id: str | None,
) -> Posting | None:
    """The posting this paste refers to, if it is already known.

    Three keys, strongest first. **Employer plus the employer's own posting ID** holds when the
    link has been rewritten and the body edited, which neither of the others survive. **The URL**
    catches a re-paste of the same link. **The text hash** catches the same posting reached
    through two different links. `url` is expected already normalised, because that is what is
    stored.

    Queries go through SQLAlchemy's `scalars` rather than SQLModel's own query method, whose name
    collides with the dynamic-execution assertion in `tests/test_safety.py`. That assertion is
    worth more than the idiom, so `scalars` is the convention for every query here.
    """
    if job_id and employer:
        by_job_id = session.scalars(
            select(Posting).where(
                Posting.employer_key == employer_key(employer),
                Posting.source_posting_id == job_id,
            )
        ).first()
        if by_job_id:
            return by_job_id

    if url:
        by_url = session.scalars(select(Posting).where(Posting.url == url)).first()
        if by_url:
            return by_url

    return session.scalars(select(Posting).where(Posting.text_hash == content_hash(text))).first()
