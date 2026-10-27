"""Config loading, and the schema check that refuses a stale file rather than guessing at it."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from rr import config as config_mod
from rr import paths


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A minimal project: top-level config, one user, valid files."""
    (tmp_path / "rr.yaml").write_text(
        yaml.safe_dump({"schema": 1, "default_user": "someone"}), encoding="utf-8"
    )
    cfg = tmp_path / "users" / "someone" / "config"
    cfg.mkdir(parents=True)
    (tmp_path / "users" / "someone" / "knowledge").mkdir()

    (cfg / "run.yaml").write_text(
        yaml.safe_dump({"schema": 1, "limits": {"max_drafts": 20}, "area": {"zip": "00000"}}),
        encoding="utf-8",
    )
    (cfg / "profile.yaml").write_text(
        yaml.safe_dump(
            {
                "schema": 1,
                "default_persona": "software",
                "personas": {
                    "software": {"name": "A Person", "email": "a@example.com"},
                    "food": {"name": "A Person", "email": "b@example.com"},
                },
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_resolves_default_user(repo: Path) -> None:
    root = paths.resolve(repo_root=repo)
    assert root.user == "someone"
    assert root.database == repo / "users" / "someone" / "roborecruiter.db"


def test_explicit_user_overrides_default(repo: Path) -> None:
    (repo / "users" / "other").mkdir()
    assert paths.resolve("other", repo_root=repo).user == "other"


def test_unknown_user_is_refused_and_lists_what_exists(repo: Path) -> None:
    with pytest.raises(paths.DataRootError, match="someone"):
        paths.resolve("nobody", repo_root=repo)


@pytest.mark.parametrize("name", ["../escape", "a/b", "..", "a\\b"])
def test_user_name_cannot_escape_the_users_directory(repo: Path, name: str) -> None:
    with pytest.raises(paths.DataRootError, match="Invalid user name"):
        paths.resolve(name, repo_root=repo)


def test_wrong_top_level_schema_is_refused(repo: Path) -> None:
    (repo / "rr.yaml").write_text(
        yaml.safe_dump({"schema": 99, "default_user": "someone"}), encoding="utf-8"
    )
    with pytest.raises(paths.DataRootError, match="schema"):
        paths.resolve(repo_root=repo)


def test_wrong_config_schema_is_refused_not_guessed(repo: Path) -> None:
    """The whole point: a stale file stops the run rather than being parsed on a hunch.

    Alembic migrates tables. Nothing migrates YAML, so this check is the only thing standing
    between an old file and a silent misread.
    """
    root = paths.resolve(repo_root=repo)
    path = root.config / "run.yaml"
    path.write_text(yaml.safe_dump({"schema": 2, "limits": {}}), encoding="utf-8")

    with pytest.raises(config_mod.ConfigError) as exc:
        config_mod.load_run(root)
    assert "schema 2" in str(exc.value)
    assert "Refusing" in str(exc.value)


def test_missing_schema_key_is_refused(repo: Path) -> None:
    root = paths.resolve(repo_root=repo)
    (root.config / "run.yaml").write_text(yaml.safe_dump({"limits": {}}), encoding="utf-8")
    with pytest.raises(config_mod.ConfigError, match="declares schema None"):
        config_mod.load_run(root)


def test_profile_overlay_wins_over_base(repo: Path) -> None:
    root = paths.resolve(repo_root=repo)
    (root.config / "run.demo.yaml").write_text(
        yaml.safe_dump({"schema": 1, "limits": {"max_drafts": 2}}), encoding="utf-8"
    )
    merged = config_mod.load_run(root, "demo")
    assert merged["limits"]["max_drafts"] == 2
    # Untouched keys survive the overlay rather than being replaced wholesale.
    assert merged["area"]["zip"] == "00000"


def test_missing_overlay_is_not_an_error(repo: Path) -> None:
    """A profile with no overrides is a valid profile."""
    root = paths.resolve(repo_root=repo)
    assert config_mod.load_run(root, "dev")["limits"]["max_drafts"] == 20


def test_unknown_profile_is_refused(repo: Path) -> None:
    root = paths.resolve(repo_root=repo)
    with pytest.raises(config_mod.ConfigError, match="Unknown profile"):
        config_mod.load_run(root, "uat")


def test_persona_selection(repo: Path) -> None:
    root = paths.resolve(repo_root=repo)
    profile = config_mod.load(root, "profile")
    assert config_mod.active_persona(profile)["email"] == "a@example.com"
    assert config_mod.active_persona(profile, "food")["email"] == "b@example.com"


def test_unknown_persona_lists_what_exists(repo: Path) -> None:
    root = paths.resolve(repo_root=repo)
    profile = config_mod.load(root, "profile")
    with pytest.raises(config_mod.ConfigError, match="food, software"):
        config_mod.active_persona(profile, "nope")
