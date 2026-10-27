"""The migration chain applies cleanly to an empty database.

Early for a narrow reason: until the first real submission the database can be deleted and
recreated. The moment an application is sent, the row holding that file's hash is the one record
that cannot be regenerated - and that lands inside stage 1.
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from sqlmodel import SQLModel

from rr import models  # noqa: F401 - imported to register the tables on SQLModel.metadata

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def scratch_project(tmp_path: Path) -> Path:
    """A throwaway project with one empty user, so migrations run against nothing."""
    (tmp_path / "rr.yaml").write_text(
        yaml.safe_dump({"schema": 1, "default_user": "scratch"}), encoding="utf-8"
    )
    (tmp_path / "users" / "scratch" / "config").mkdir(parents=True)
    return tmp_path


def _alembic_upgrade(scratch_project: Path) -> subprocess.CompletedProcess[str]:
    """Run `alembic upgrade head` against a scratch project.

    Run from the repository root, because Alembic resolves `script_location` against the working
    directory. The target project is passed with `-x root=` instead of changing directory.
    """
    return subprocess.run(  # noqa: S603 - fixed argv, no shell, no external input
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(REPO / "alembic.ini"),
            "-x",
            f"root={scratch_project}",
            "upgrade",
            "head",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )


def test_upgrade_head_applies_to_an_empty_database(scratch_project: Path) -> None:
    result = _alembic_upgrade(scratch_project)
    assert result.returncode == 0, (
        f"alembic upgrade head failed (exit {result.returncode})\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert (scratch_project / "users" / "scratch" / "roborecruiter.db").is_file()


def test_every_model_table_exists_after_upgrade(scratch_project: Path) -> None:
    """Catches a model added without a matching migration."""
    result = _alembic_upgrade(scratch_project)
    assert result.returncode == 0, result.stderr

    db = scratch_project / "users" / "scratch" / "roborecruiter.db"
    with sqlite3.connect(db) as conn:
        present = {
            row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }

    missing = set(SQLModel.metadata.tables) - present
    assert not missing, f"Models with no table after migration: {sorted(missing)}"
