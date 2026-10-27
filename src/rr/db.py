"""Database engine and session, scoped to one user's data root."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import event
from sqlmodel import Session, create_engine

from rr.paths import DataRoot


def engine_for(path: Path):
    """Build an engine for one database file.

    WAL mode so a reader is never blocked by a writer, and foreign keys on because SQLite leaves
    them off by default and a dangling reference here would be a lost application record.
    """
    eng = create_engine(f"sqlite:///{path}", echo=False)

    @event.listens_for(eng, "connect")
    def _set_pragmas(dbapi_connection, _record):  # pragma: no cover - driver callback
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return eng


@contextmanager
def session_for(root: DataRoot) -> Iterator[Session]:
    """Open a session against one user's database."""
    eng = engine_for(root.database)
    with Session(eng) as session:
        yield session
    eng.dispose()
