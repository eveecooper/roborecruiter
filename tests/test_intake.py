"""Pasting a posting in: step 1.1.

The step's promise is that the posting text survives verbatim and that re-pasting the same
posting is recognised rather than duplicated. Both are tested at `intake.add`, which is the
public boundary; the normalising helpers behind it are not tested directly.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from sqlmodel import Session, SQLModel, create_engine, select
from typer.testing import CliRunner

from rr import cli as cli_mod
from rr import intake, paths
from rr.cli import app
from rr.models import Posting

#: sha256 of the empty string, from an independent source rather than recomputed here.
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

POSTING_URL = "https://careers.example.com/en_US/careers/JobDetail?jobId=132846"
POSTING_TEXT = """Solution Architect - Entry Level
Somewhere, Ontario, Canada

Your role and responsibilities
Work closely with customers to understand directives.
"""


@pytest.fixture
def root(tmp_path: Path) -> paths.DataRoot:
    """A minimal project with one user, enough to resolve paths."""
    (tmp_path / "rr.yaml").write_text(
        yaml.safe_dump({"schema": 1, "default_user": "someone"}), encoding="utf-8"
    )
    (tmp_path / "users" / "someone" / "config").mkdir(parents=True)
    return paths.resolve(repo_root=tmp_path)


@pytest.fixture
def session(root: paths.DataRoot) -> Iterator[Session]:
    """Tables straight from the models. `test_migrations.py` covers the migration path."""
    engine = create_engine(f"sqlite:///{root.database}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as open_session:
        yield open_session
    engine.dispose()


@pytest.fixture
def cli(root: paths.DataRoot, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    """A runner whose working directory is a real project with a migrated-shape database."""
    engine = create_engine(f"sqlite:///{root.database}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()
    monkeypatch.chdir(root.base.parents[1])
    return CliRunner()


def test_cli_add_records_the_posting_and_reports_where(
    cli: CliRunner, root: paths.DataRoot
) -> None:
    pasted = root.base / "pasted.txt"
    pasted.write_text(POSTING_TEXT, encoding="utf-8")

    result = cli.invoke(app, ["add", POSTING_URL, "--file", str(pasted)])

    assert result.exit_code == 0, result.output
    assert "Solution Architect" in result.output
    folders = sorted(p.name for p in root.applications.iterdir())
    assert len(folders) == 1
    assert (root.applications / folders[0] / "posting.md").is_file()


def test_cli_add_reads_the_posting_from_stdin(cli: CliRunner, root: paths.DataRoot) -> None:
    """So a posting can be piped in without first saving it to a file."""
    result = cli.invoke(app, ["add", POSTING_URL], input=POSTING_TEXT)
    assert result.exit_code == 0, result.output
    assert len(list(root.applications.iterdir())) == 1


def test_cli_add_twice_says_already_known_and_adds_nothing(
    cli: CliRunner, root: paths.DataRoot
) -> None:
    cli.invoke(app, ["add", POSTING_URL], input=POSTING_TEXT)
    result = cli.invoke(app, ["add", POSTING_URL], input=POSTING_TEXT)

    assert result.exit_code == 0, result.output
    assert "already" in result.output.lower()
    assert len(list(root.applications.iterdir())) == 1


def test_cli_add_flags_what_it_guessed(cli: CliRunner, root: paths.DataRoot) -> None:
    """A guess nobody can see is decoration, so the command has to say what it guessed."""
    result = cli.invoke(app, ["add", POSTING_URL], input=POSTING_TEXT)
    assert "guessed" in result.output.lower()
    assert "employer" in result.output.lower()


def test_cli_add_accepts_the_posting_text_as_an_argument(
    cli: CliRunner, root: paths.DataRoot
) -> None:
    """No file, no pipe: the text comes straight in on the command line."""
    result = cli.invoke(app, ["add", POSTING_URL, POSTING_TEXT])

    assert result.exit_code == 0, result.output
    assert len(list(root.applications.iterdir())) == 1


def test_cli_add_prompts_and_reads_an_interactive_paste(
    cli: CliRunner, root: paths.DataRoot, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The default path: run the command, paste, end the input. No file is ever written.

    An interactive run must say how to end the paste, or the terminal just sits there looking
    broken.
    """
    monkeypatch.setattr(cli_mod, "_is_interactive", lambda: True)

    result = cli.invoke(app, ["add", POSTING_URL], input=LABELLED_PASTE)

    assert result.exit_code == 0, result.output
    assert "paste" in result.output.lower()
    assert "Ctrl" in result.output
    assert len(list(root.applications.iterdir())) == 1


def test_cli_add_needs_no_flags_for_a_labelled_paste(cli: CliRunner, root: paths.DataRoot) -> None:
    """The point of the whole thing: nothing typed but the URL, and the ID still lands."""
    result = cli.invoke(app, ["add", POSTING_URL], input=LABELLED_PASTE)

    assert result.exit_code == 0, result.output
    assert "137572" in result.output
    assert "Solution Architect - Entry Level Sales Program 2027" in result.output


def test_cli_add_reports_a_job_id_conflict(cli: CliRunner, root: paths.DataRoot) -> None:
    """The link says one requisition and the posting says another. Say so."""
    result = cli.invoke(app, ["add", POSTING_URL], input=LABELLED_PASTE)
    # POSTING_URL carries jobId=132846; the pasted text says 137572.
    assert "132846" in result.output
    assert "conflict" in result.output.lower() or "disagree" in result.output.lower()


def test_cli_add_takes_and_reports_the_job_id(cli: CliRunner, root: paths.DataRoot) -> None:
    result = cli.invoke(app, ["add", POSTING_URL, "--job-id", "R-4821"], input=POSTING_TEXT)

    assert result.exit_code == 0, result.output
    assert "R-4821" in result.output
    folder = next(root.applications.iterdir())
    assert "R-4821" in (folder / "posting.md").read_text(encoding="utf-8")


def test_cli_add_on_an_unmigrated_user_creates_no_database_file(
    root: paths.DataRoot, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A mistyped --user must not leave an empty database behind. Checking is not writing."""
    monkeypatch.chdir(root.base.parents[1])
    assert not root.database.exists()

    result = CliRunner().invoke(app, ["add", POSTING_URL], input=POSTING_TEXT)

    assert result.exit_code == 1
    assert "alembic" in result.output
    assert not root.database.exists()


def test_cli_add_refuses_empty_posting_text(cli: CliRunner, root: paths.DataRoot) -> None:
    """An empty paste is a mistake, not a posting with no words in it."""
    result = cli.invoke(app, ["add", POSTING_URL], input="   \n\n")
    assert result.exit_code != 0
    assert not root.applications.exists() or not list(root.applications.iterdir())


def test_the_posting_text_is_kept_verbatim(session: Session, root: paths.DataRoot) -> None:
    """Full text, not a hash and a URL. This is stage 5's corpus."""
    result = intake.add(
        session, root, url=POSTING_URL, text=POSTING_TEXT, title="Solution Architect", employer="Ex"
    )

    assert result.created
    stored = session.exec(select(Posting)).one()
    assert stored.text == POSTING_TEXT
    assert stored.title == "Solution Architect"
    assert stored.employer_name == "Ex"


def test_the_hash_covers_the_text(session: Session, root: paths.DataRoot) -> None:
    result = intake.add(session, root, url=POSTING_URL, text="", title="t", employer="e")
    assert result.posting.text_hash == EMPTY_SHA256


def test_re_pasting_the_same_url_does_not_create_a_second_posting(
    session: Session, root: paths.DataRoot
) -> None:
    """Step 1.1's exit criterion. A second paste is the same posting seen again."""
    first = intake.add(
        session, root, url=POSTING_URL, text=POSTING_TEXT, title="Solution Architect", employer="Ex"
    )
    again = intake.add(
        session, root, url=POSTING_URL, text=POSTING_TEXT, title="Solution Architect", employer="Ex"
    )

    assert not again.created
    assert again.posting.id == first.posting.id
    assert len(session.exec(select(Posting)).all()) == 1
    # Seeing it again is information: the posting was still being looked at on this date.
    assert again.posting.last_seen >= first.posting.first_seen


def test_re_pasting_identical_text_under_a_different_url_is_recognised(
    session: Session, root: paths.DataRoot
) -> None:
    """The same posting reached by two links is one posting, caught by the text hash."""
    intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="T", employer="Ex")
    again = intake.add(
        session,
        root,
        url="https://jobs.example.org/other-link",
        text=POSTING_TEXT,
        title="T",
        employer="Ex",
    )

    assert not again.created
    assert len(session.exec(select(Posting)).all()) == 1


def test_a_changed_posting_body_is_recorded_on_the_existing_row(
    session: Session, root: paths.DataRoot
) -> None:
    """An employer edited the posting. Same URL, so same posting - with the newer text."""
    intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="T", employer="Ex")
    revised = POSTING_TEXT + "\nNow also requires Kubernetes.\n"
    again = intake.add(session, root, url=POSTING_URL, text=revised, title="T", employer="Ex")

    assert not again.created
    assert again.text_changed
    assert again.posting.text == revised
    assert len(session.exec(select(Posting)).all()) == 1


#: The shape a posting actually arrives in when copied off a careers page: labelled fields
#: stacked above the body, with the value on the line after its label.
LABELLED_PASTE = """Job Title
Solution Architect - Entry Level Sales Program 2027
Job ID
137572
Markham, Ontario, Canada
Entry Level

Introduction
At IBM, Solution Architects work to understand needs.
"""


def test_a_labelled_paste_yields_the_role_not_the_label(
    session: Session, root: paths.DataRoot
) -> None:
    """ "First non-blank line" returns "Job Title" on this shape, which is the wrong answer."""
    result = intake.add(session, root, url=None, text=LABELLED_PASTE, employer="IBM")

    assert result.posting.title == "Solution Architect - Entry Level Sales Program 2027"
    assert result.posting.source_posting_id == "137572"


def test_a_job_id_in_the_text_is_preferred_over_the_one_in_the_link(
    session: Session, root: paths.DataRoot
) -> None:
    """The posting's own displayed requisition number is what the employer means by "job ID"."""
    result = intake.add(
        session,
        root,
        url="https://careers.ibm.com/en_US/careers/JobDetail?jobId=999999",
        text=LABELLED_PASTE,
        employer="IBM",
    )
    assert result.posting.source_posting_id == "137572"
    # A disagreement between link and text is reported rather than quietly resolved.
    assert result.job_id_conflict == "999999"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Job ID: 44821", "44821"),
        ("Requisition ID  R-2025-11", "R-2025-11"),
        ("Req #: 7781", "7781"),
        ("Posting ID: ABC-123", "ABC-123"),
    ],
)
def test_job_id_labels_on_the_same_line(
    session: Session, root: paths.DataRoot, line: str, expected: str
) -> None:
    text = f"Line Cook\n{line}\nSome body text.\n"
    result = intake.add(session, root, url=None, text=text, employer="Ex")
    assert result.posting.source_posting_id == expected


def test_a_job_id_label_deep_in_the_body_is_ignored(session: Session, root: paths.DataRoot) -> None:
    """Labels sit near the top. Matching anywhere would pick up prose about applying."""
    body = "Line Cook\n" + ("Filler sentence about the role.\n" * 60) + "Job ID 99999\n"
    result = intake.add(session, root, url=None, text=body, employer="Ex")
    assert result.posting.source_posting_id is None


def test_the_job_id_catches_a_duplicate_that_url_and_text_both_miss(
    session: Session, root: paths.DataRoot
) -> None:
    """The employer's own posting ID is the duplicate key that survives everything else changing.

    The link was rewritten and the posting was edited, so neither the URL nor the text hash can
    recognise this. The requisition number can.
    """
    intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, employer="IBM", job_id="132846")
    again = intake.add(
        session,
        root,
        url="https://ibm.wd5.myworkdayjobs.com/entirely/different/path",
        text="A completely rewritten posting body with nothing in common.",
        employer="IBM",
        job_id="132846",
    )

    assert not again.created
    assert len(session.exec(select(Posting)).all()) == 1


def test_the_same_job_id_at_a_different_employer_is_a_different_posting(
    session: Session, root: paths.DataRoot
) -> None:
    """A job ID is unique inside one hiring system, not across them. Small integers collide."""
    intake.add(session, root, url=None, text="first", employer="IBM", job_id="1001")
    other = intake.add(session, root, url=None, text="second", employer="Shopify", job_id="1001")

    assert other.created
    assert len(session.exec(select(Posting)).all()) == 2


def test_the_employer_key_ignores_case_and_punctuation(
    session: Session, root: paths.DataRoot
) -> None:
    """The employer is a guessed string, so the key has to tolerate how it was written.

    Without this, the guessed "ibm" and a corrected "IBM" would be two employers and the job-ID
    check would miss the duplicate it exists to catch.
    """
    intake.add(session, root, url=None, text="first", employer="ibm", job_id="132846")
    again = intake.add(session, root, url=None, text="second", employer="I.B.M. ", job_id="132846")

    assert not again.created
    assert len(session.exec(select(Posting)).all()) == 1


def test_the_job_id_is_guessed_from_the_link(session: Session, root: paths.DataRoot) -> None:
    """Most boards put the requisition number in the URL, and forgetting to pass it is the
    expected human error. A guess beats a missing value, and it is flagged."""
    result = intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, employer="IBM")

    assert result.posting.source_posting_id == "132846"
    assert "job_id" in result.guessed


def test_an_explicit_job_id_is_not_overridden_by_a_guess(
    session: Session, root: paths.DataRoot
) -> None:
    result = intake.add(
        session, root, url=POSTING_URL, text=POSTING_TEXT, employer="IBM", job_id="R-999"
    )
    assert result.posting.source_posting_id == "R-999"
    assert "job_id" not in result.guessed


def test_no_job_id_anywhere_is_left_empty_rather_than_invented(
    session: Session, root: paths.DataRoot
) -> None:
    result = intake.add(
        session, root, url="https://example.com/careers/some-role", text=POSTING_TEXT, employer="Ex"
    )
    assert result.posting.source_posting_id is None
    assert "job_id" not in result.guessed


def test_a_job_id_added_on_a_later_paste_corrects_the_row(
    session: Session, root: paths.DataRoot
) -> None:
    """The applicant forgot it the first time. That is the case this feature was asked for."""
    first = intake.add(session, root, url=None, text=POSTING_TEXT, employer="IBM")
    assert first.posting.source_posting_id is None

    corrected = intake.add(
        session, root, url=None, text=POSTING_TEXT, employer="IBM", job_id="132846"
    )
    assert not corrected.created
    assert corrected.posting.source_posting_id == "132846"
    assert corrected.fields_changed == ("job_id",)


def test_an_explicit_title_corrects_an_earlier_guess(
    session: Session, root: paths.DataRoot
) -> None:
    """`add` tells the applicant to re-run with --employer to fix a guess, so that has to work.

    An explicitly passed value is the applicant speaking, not a file edit, so it wins over what
    was guessed. Omitting it leaves the stored value alone rather than re-guessing over it.
    """
    first = intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT)
    assert first.posting.employer_name == "example"

    corrected = intake.add(
        session, root, url=POSTING_URL, text=POSTING_TEXT, employer="Example Industries"
    )
    assert not corrected.created
    assert corrected.posting.employer_name == "Example Industries"
    # The title was not passed, so the earlier guess stands rather than being overwritten.
    assert corrected.posting.title == "Solution Architect - Entry Level"
    assert len(session.exec(select(Posting)).all()) == 1

    # The correction has to reach the file too, or posting.md quietly disagrees with the database.
    assert "Example Industries" in (corrected.folder / "posting.md").read_text(encoding="utf-8")
    assert corrected.fields_changed == ("employer",)


def test_a_stale_posting_file_is_brought_back_into_agreement(
    session: Session, root: paths.DataRoot
) -> None:
    """Nothing downstream reads `posting.md` back, so a file disagreeing with its row is silent.

    Reconciling on every add is what keeps the readable copy honest.
    """
    first = intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="T", employer="Ex")
    written = first.folder / "posting.md"
    written.write_text("stale rubbish", encoding="utf-8")

    intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="T", employer="Ex")

    body = written.read_text(encoding="utf-8")
    assert "stale rubbish" not in body
    assert POSTING_TEXT.strip() in body


def test_a_repeat_with_nothing_new_reports_no_change(
    session: Session, root: paths.DataRoot
) -> None:
    intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="T", employer="Ex")
    again = intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="T", employer="Ex")
    assert again.fields_changed == ()
    assert not again.text_changed


def test_a_tracking_parameter_does_not_make_it_a_new_posting(
    session: Session, root: paths.DataRoot
) -> None:
    """The same link copied from a search result carries `&source=...`. Same posting.

    The body is changed deliberately, so the text hash cannot be what rescues this - only URL
    normalisation can.
    """
    intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="T", employer="Ex")
    again = intake.add(
        session,
        root,
        url=POSTING_URL + "&source=WEB_Search_NA&utm_campaign=x",
        text=POSTING_TEXT + "\nrevised\n",
        title="T",
        employer="Ex",
    )

    assert not again.created
    assert len(session.exec(select(Posting)).all()) == 1


def test_a_meaningful_query_parameter_is_kept(session: Session, root: paths.DataRoot) -> None:
    """Two different jobs on one host differ only by `jobId`. They must stay two postings."""
    intake.add(session, root, url=POSTING_URL, text="first job", title="T", employer="Ex")
    other = intake.add(
        session,
        root,
        url="https://careers.example.com/en_US/careers/JobDetail?jobId=999999",
        text="second job",
        title="T2",
        employer="Ex",
    )

    assert other.created
    assert len(session.exec(select(Posting)).all()) == 2


def test_title_and_employer_are_guessed_rather_than_demanded(
    session: Session, root: paths.DataRoot
) -> None:
    """Nothing halts for a person. An uncertain field proceeds as a flagged guess (ADR 0003)."""
    result = intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT)

    assert result.posting.title == "Solution Architect - Entry Level"
    assert result.posting.employer_name == "example"
    # The fixture URL carries `jobId`, so the requisition number is guessed from it as well.
    assert set(result.guessed) == {"title", "employer", "job_id"}


def test_a_given_title_is_not_overridden_by_a_guess(session: Session, root: paths.DataRoot) -> None:
    result = intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="Dishwasher")
    assert result.posting.title == "Dishwasher"
    assert result.guessed == ("employer", "job_id")


def test_a_posting_with_no_url_still_records(session: Session, root: paths.DataRoot) -> None:
    """Some postings arrive as text alone. The employer is then unknown, not invented."""
    result = intake.add(session, root, url=None, text=POSTING_TEXT)
    assert result.created
    assert result.posting.url is None
    assert result.posting.employer_name == intake.UNKNOWN_EMPLOYER


def test_a_hostile_title_cannot_escape_the_applications_directory(
    session: Session, root: paths.DataRoot
) -> None:
    """Posting text is untrusted in every stage, and a title is posting text.

    This is the third non-negotiable assertion applied to the one place in step 1.1 where
    posting-derived text reaches the filesystem.
    """
    result = intake.add(
        session,
        root,
        url=POSTING_URL,
        text=POSTING_TEXT,
        title="../../../../etc/passwd",
        employer="..\\..\\windows",
    )

    assert result.folder.parent == root.applications
    assert result.folder.resolve().is_relative_to(root.applications.resolve())
    assert (result.folder / "posting.md").is_file()


def test_posting_md_is_written_into_the_posting_folder(
    session: Session, root: paths.DataRoot
) -> None:
    result = intake.add(
        session, root, url=POSTING_URL, text=POSTING_TEXT, title="Solution Architect", employer="Ex"
    )

    written = result.folder / "posting.md"
    assert written.is_file()
    body = written.read_text(encoding="utf-8")
    assert POSTING_TEXT.strip() in body
    assert POSTING_URL in body
