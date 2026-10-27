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

#: Stands in when no employer can be worked out. A placeholder the applicant can see and fix
#: beats inventing a name that would end up in a document.
UNKNOWN_EMPLOYER = "unknown-employer"

#: Host labels that name a hiring page rather than the employer, stripped before guessing.
_HOST_NOISE = frozenset({"www", "careers", "career", "jobs", "job", "apply", "boards", "hiring"})

#: Second-level labels that are part of a public suffix, so the employer is one label further in.
_PUBLIC_SECOND_LEVEL = frozenset({"co", "com", "org", "net", "ac", "gov", "edu"})

#: A guessed title longer than this is almost certainly a paragraph, not a title.
_TITLE_MAX = 120

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


def guess_title(text: str) -> str:
    """The first non-blank line. Job postings lead with the title far more often than not."""
    for line in normalize_text(text).split("\n"):
        candidate = line.strip().lstrip("#").strip()
        if candidate:
            return candidate[:_TITLE_MAX]
    return "untitled posting"


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
    source: str = "manual",
) -> Intake:
    """Record one pasted posting: a row carrying the full text, and a `posting.md` beside it.

    A posting already known by URL or by text hash is updated rather than duplicated, so pasting
    the same link twice is safe and says so. A missing title or employer is guessed and reported
    rather than asked for, because no step of this pipeline halts for a person (ADR 0003).
    """
    canonical = normalize_url(url)
    known = find_by_url_or_hash(session, url=canonical, text=text)
    if known is not None:
        return _seen_again(
            session, root, known, url=canonical, text=text, title=title, employer=employer
        )

    guessed: list[str] = []
    if not title:
        title = guess_title(text)
        guessed.append("title")
    if not employer:
        employer = guess_employer(canonical)
        guessed.append("employer")

    posting = Posting(
        employer_name=employer,
        title=title,
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
    return Intake(posting=posting, created=True, folder=folder, guessed=tuple(guessed))


def _seen_again(
    session: Session,
    root: DataRoot,
    posting: Posting,
    *,
    url: str | None,
    text: str,
    title: str | None = None,
    employer: str | None = None,
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
        fields.append("employer")
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
        f"- **URL:** {posting.url or '(none given)'}",
        f"- **Added:** {posting.first_seen.isoformat(timespec='seconds')}",
        f"- **Source:** {posting.source}",
        f"- **Text hash:** `{posting.text_hash}`",
        "",
        "---",
        "",
    ]
    return "\n".join(header) + normalize_text(posting.text) + "\n"


def find_by_url_or_hash(session: Session, *, url: str | None, text: str) -> Posting | None:
    """The posting this paste refers to, if it is already known.

    `url` is expected already normalised, because that is what is stored.

    Queries go through SQLAlchemy's `scalars` rather than SQLModel's own query method, whose name
    collides with the dynamic-execution assertion in `tests/test_safety.py`. That assertion is
    worth more than the idiom, so `scalars` is the convention for every query here.
    """
    if url:
        existing = session.scalars(select(Posting).where(Posting.url == url)).first()
        if existing:
            return existing
    return session.scalars(select(Posting).where(Posting.text_hash == content_hash(text))).first()
