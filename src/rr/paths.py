"""Resolving the user-scoped data root.

Every path in the codebase resolves through here rather than being relative to the repository.
One directory and one database per user: isolation is structural, so no query can forget a filter
and nothing leaks between people. See docs/adr/0011-user-scoped-data-roots.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

TOP_LEVEL_CONFIG = "rr.yaml"
USERS_DIR = "users"
EXPECTED_TOP_LEVEL_SCHEMA = 1


class DataRootError(Exception):
    """The data root could not be resolved, or does not look like one."""


@dataclass(frozen=True)
class DataRoot:
    """Every location the tool reads or writes, for one user."""

    user: str
    base: Path

    @property
    def config(self) -> Path:
        return self.base / "config"

    @property
    def styles(self) -> Path:
        return self.config / "styles"

    @property
    def knowledge(self) -> Path:
        return self.base / "knowledge"

    @property
    def applications(self) -> Path:
        return self.base / "applications"

    @property
    def database(self) -> Path:
        return self.base / "roborecruiter.db"

    @property
    def inbox(self) -> Path:
        return self.base / "inbox.yaml"

    def application_dir(self, application_id: str) -> Path:
        return self.applications / application_id


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from `start` looking for the top-level config file."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / TOP_LEVEL_CONFIG).is_file():
            return candidate
    raise DataRootError(
        f"No {TOP_LEVEL_CONFIG} found in {current} or any parent. "
        "Run from inside the project, or create it with a `default_user` key."
    )


def default_user(repo_root: Path) -> str:
    """Read the default user from the top-level config.

    Refuses rather than guessing: a wrong default would silently write one person's application
    history into another person's directory.
    """
    config_path = repo_root / TOP_LEVEL_CONFIG
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    schema = raw.get("schema")
    if schema != EXPECTED_TOP_LEVEL_SCHEMA:
        raise DataRootError(
            f"{config_path} declares schema {schema!r}, expected {EXPECTED_TOP_LEVEL_SCHEMA}. "
            "Refusing to read a file whose shape may have changed."
        )

    user = raw.get("default_user")
    if not user:
        raise DataRootError(f"{config_path} has no `default_user`. Pass --user explicitly.")
    return str(user)


def resolve(user: str | None = None, repo_root: Path | None = None) -> DataRoot:
    """Resolve the data root for `user`, falling back to the configured default."""
    root = repo_root or find_repo_root()
    name = user or default_user(root)

    # A user name becomes a directory name, so reject anything that could escape the users dir.
    if "/" in name or "\\" in name or name in {".", ".."}:
        raise DataRootError(f"Invalid user name: {name!r}")

    base = root / USERS_DIR / name
    if not base.is_dir():
        available = sorted(p.name for p in (root / USERS_DIR).iterdir() if p.is_dir())
        raise DataRootError(f"No data root for user {name!r}. Available: {', '.join(available)}")
    return DataRoot(user=name, base=base)
