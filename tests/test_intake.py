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
    assert set(result.guessed) == {"title", "employer"}


def test_a_given_title_is_not_overridden_by_a_guess(session: Session, root: paths.DataRoot) -> None:
    result = intake.add(session, root, url=POSTING_URL, text=POSTING_TEXT, title="Dishwasher")
    assert result.posting.title == "Dishwasher"
    assert result.guessed == ("employer",)


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
