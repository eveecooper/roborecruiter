"""Command line entry point.

Every command takes `--user` and `--profile`. `doctor` reports on a data root; `add` takes a
posting in by hand. Drafting and submitting arrive in 1.2 and 1.3.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from sqlalchemy import inspect

from rr import config as config_mod
from rr import db, intake, paths

app = typer.Typer(
    add_completion=False,
    help="An assisted job application pipeline. It prepares materials; you submit them.",
)

UserOption = Annotated[
    str | None,
    typer.Option(
        "--user", "-u", help="Which data root to use. Defaults to rr.yaml's default_user."
    ),
]
ProfileOption = Annotated[
    str,
    typer.Option("--profile", "-p", help="Config profile: dev, demo, or prod."),
]


@app.callback()
def main() -> None:
    """An assisted job application pipeline."""


def _resolve_or_exit(user: str | None) -> paths.DataRoot:
    try:
        return paths.resolve(user)
    except paths.DataRootError as exc:
        typer.secho(f"FAIL  {exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc


def _require_migrated(root: paths.DataRoot) -> None:
    """Stop with an instruction rather than a driver error on an un-migrated database.

    The missing-file case is answered without connecting, because SQLite creates the file on
    connect and a check that writes would leave a stray empty database behind every mistyped
    `--user`.
    """

    def _refuse() -> None:
        typer.secho(
            f"No tables in {root.database}.\nRun:  uv run alembic -x user={root.user} upgrade head",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if not root.database.exists():
        _refuse()

    engine = db.engine_for(root.database)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()
    if "postings" not in tables:
        _refuse()


def _is_interactive() -> bool:
    """Whether a person is typing at this command rather than a pipe feeding it."""
    return sys.stdin.isatty()


_END_OF_PASTE = "Ctrl+Z then Enter" if sys.platform == "win32" else "Ctrl+D"


def _posting_text(text: str | None, file: Path | None) -> str:
    """The posting, from an argument, a file, or whatever is pasted at the prompt.

    Pasting is the default because it is the fewest actions: one command, one paste, one
    keystroke to end it, and no intermediate file to save and then name.
    """
    if text:
        return text

    if file is not None:
        try:
            return file.read_text(encoding="utf-8")
        except OSError as exc:
            typer.secho(f"Cannot read {file}: {exc}", fg=typer.colors.RED)
            raise typer.Exit(1) from exc

    if _is_interactive():
        # Without this the terminal looks hung, because the command is simply waiting on input.
        typer.secho(
            f"Paste the posting, then press {_END_OF_PASTE} to finish:", fg=typer.colors.CYAN
        )
    return sys.stdin.read()


@app.command()
def add(
    url: Annotated[
        str | None, typer.Argument(help="The posting's link. Tracking parameters are stripped.")
    ] = None,
    text: Annotated[
        str | None,
        typer.Argument(help="The posting text. Omit it to paste at the prompt instead."),
    ] = None,
    file: Annotated[
        Path | None, typer.Option("--file", "-f", help="File holding the posting text.")
    ] = None,
    title: Annotated[
        str | None,
        typer.Option("--title", "-t", help="Job title. Guessed from the text if omitted."),
    ] = None,
    employer: Annotated[
        str | None, typer.Option("--employer", "-e", help="Employer. Guessed from the URL host.")
    ] = None,
    job_id: Annotated[
        str | None,
        typer.Option(
            "--job-id",
            "-j",
            help="The employer's own posting ID. The strongest duplicate check: pass it.",
        ),
    ] = None,
    user: UserOption = None,
    profile: ProfileOption = config_mod.DEFAULT_PROFILE,
) -> None:
    """Take a posting in by hand: store the full text and write `posting.md`.

    Fetches nothing - the text is pasted. Run it with just the link and paste at the prompt; the
    job ID, title and employer are read out of the posting where it labels them, so there is
    usually nothing else to type. Re-adding the same posting is recognised rather than
    duplicated, so running this twice is safe.
    """
    root = _resolve_or_exit(user)
    _require_migrated(root)

    text = _posting_text(text, file)
    if not intake.normalize_text(text):
        typer.secho("The posting text is empty. Nothing added.", fg=typer.colors.RED)
        raise typer.Exit(1)

    with db.session_for(root) as session:
        result = intake.add(
            session, root, url=url, text=text, title=title, employer=employer, job_id=job_id
        )
        posting = result.posting
        if result.created:
            typer.secho(f"Added #{posting.id}  {posting.title}", fg=typer.colors.GREEN)
        else:
            updates = list(result.fields_changed)
            if result.text_changed:
                updates.insert(0, "posting text")
            detail = f"updated {', '.join(updates)}" if updates else "nothing changed"
            typer.secho(
                f"Already known as #{posting.id} - {detail}.",
                fg=typer.colors.YELLOW if updates else typer.colors.BLUE,
            )

        typer.echo(f"employer  {posting.employer_name}")
        typer.echo(f"job id    {posting.source_posting_id or '(none - pass --job-id)'}")
        typer.echo(f"folder    {result.folder}")
        typer.echo(f"words     {len(posting.text.split())}")
        if result.guessed:
            typer.secho(
                f"guessed   {', '.join(result.guessed)} - check it, and pass "
                "--title/--employer/--job-id to correct it",
                fg=typer.colors.YELLOW,
            )
        if result.job_id_conflict:
            typer.secho(
                f"conflict  the link says job ID {result.job_id_conflict}, the posting text says "
                f"{posting.source_posting_id}. Used the posting's. Pass --job-id to settle it.",
                fg=typer.colors.YELLOW,
            )


@app.command()
def doctor(
    user: UserOption = None,
    profile: ProfileOption = config_mod.DEFAULT_PROFILE,
) -> None:
    """Check that this user's data root and config files are readable and current."""
    try:
        root = paths.resolve(user)
    except paths.DataRootError as exc:
        typer.secho(f"FAIL  {exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc

    typer.secho(f"user      {root.user}", fg=typer.colors.GREEN)
    typer.echo(f"root      {root.base}")
    typer.echo(f"database  {root.database} {'(exists)' if root.database.exists() else '(not yet)'}")

    problems = 0

    try:
        run = config_mod.load_run(root, profile)
        typer.secho(f"run       {profile} profile loaded ({len(run)} keys)", fg=typer.colors.GREEN)
    except config_mod.ConfigError as exc:
        typer.secho(f"run       {exc}", fg=typer.colors.YELLOW)
        problems += 1

    try:
        prof = config_mod.load(root, "profile")
        persona = config_mod.active_persona(prof)
        names = ", ".join(sorted(prof.get("personas", {})))
        typer.secho(
            f"profile   persona {persona.get('name')!r} of [{names}]", fg=typer.colors.GREEN
        )
        for label, key in (("conflicts", "conflicts"), ("gaps", "gaps")):
            count = len(prof.get(key) or [])
            colour = typer.colors.YELLOW if count else typer.colors.GREEN
            typer.secho(f"          {count} unresolved {label}", fg=colour)
    except config_mod.ConfigError as exc:
        typer.secho(f"profile   {exc}", fg=typer.colors.YELLOW)
        problems += 1

    try:
        voice = config_mod.load(root, "voice")
        missing = [
            name
            for doc_type in ("resume", "cover_letter")
            for files in (voice.get(doc_type) or {}).values()
            for name in files or []
            if not (root.knowledge / name).is_file()
        ]
        if missing:
            typer.secho(f"voice     missing from knowledge/: {missing}", fg=typer.colors.RED)
            problems += 1
        else:
            typer.secho("voice     all samples present", fg=typer.colors.GREEN)
    except config_mod.ConfigError as exc:
        typer.secho(f"voice     {exc}", fg=typer.colors.YELLOW)
        problems += 1

    if problems:
        typer.secho(f"\n{problems} thing(s) need attention.", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    typer.secho("\nAll good.", fg=typer.colors.GREEN)


if __name__ == "__main__":  # pragma: no cover
    app()
