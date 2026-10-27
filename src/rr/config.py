"""Loading configuration files, with the schema check that keeps a stale file from being guessed at.

Alembic migrates database tables. Nothing migrates YAML, so the `schema:` integer every config
file carries is the only defense against silently mis-reading an old one - a mismatch is refused
with a message rather than parsed on a best-effort basis.

Environments are configuration, not code: `config/run.yaml` holds shared defaults and
`run.<profile>.yaml` overlays it. See docs/agent/coding-standards.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from rr.paths import DataRoot

#: Config shapes this version of the code understands. Bump one when its file's shape changes,
#: and the loader will refuse older files rather than mis-parsing them.
EXPECTED_SCHEMA: dict[str, int] = {
    "run": 1,
    "profile": 1,
    "voice": 1,
    "families": 1,
}

DEFAULT_PROFILE = "prod"
VALID_PROFILES = ("dev", "demo", "prod")


class ConfigError(Exception):
    """A config file is missing, malformed, or declares an unexpected schema."""


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"Missing config file: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} is not valid YAML: {exc}") from exc
    if raw is None:
        raise ConfigError(f"{path} is empty.")
    if not isinstance(raw, dict):
        raise ConfigError(f"{path} must be a mapping at the top level, got {type(raw).__name__}.")
    return raw


def _check_schema(path: Path, raw: dict[str, Any], kind: str) -> None:
    expected = EXPECTED_SCHEMA[kind]
    declared = raw.get("schema")
    if declared != expected:
        raise ConfigError(
            f"{path} declares schema {declared!r}, this code expects {expected}. "
            "Refusing to read it - the file's shape may have changed. "
            "Update the file, or check out a version of the code that matches."
        )


def load(root: DataRoot, kind: str, *, filename: str | None = None) -> dict[str, Any]:
    """Load and schema-check one config file by kind (`profile`, `voice`, `families`, `run`)."""
    if kind not in EXPECTED_SCHEMA:
        raise ConfigError(f"Unknown config kind {kind!r}. Known: {', '.join(EXPECTED_SCHEMA)}")
    path = root.config / (filename or f"{kind}.yaml")
    raw = _load_yaml(path)
    _check_schema(path, raw, kind)
    return raw


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Overlay wins. Nested mappings merge; everything else replaces."""
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_run(root: DataRoot, profile: str = DEFAULT_PROFILE) -> dict[str, Any]:
    """Load `run.yaml`, overlaid with `run.<profile>.yaml` when that file exists.

    The overlay is optional: a profile with no overrides is a valid profile.
    """
    if profile not in VALID_PROFILES:
        raise ConfigError(f"Unknown profile {profile!r}. Valid: {', '.join(VALID_PROFILES)}")

    base = load(root, "run")
    overlay_path = root.config / f"run.{profile}.yaml"
    if not overlay_path.is_file():
        return base

    overlay = _load_yaml(overlay_path)
    _check_schema(overlay_path, overlay, "run")
    return _deep_merge(base, overlay)


def active_persona(profile_config: dict[str, Any], name: str | None = None) -> dict[str, Any]:
    """Pick one persona from the profile.

    One person, several presentations: contact details and headline vary by what the role is.
    An application picks exactly one, and the facts elsewhere in the profile never vary by it.
    """
    personas = profile_config.get("personas") or {}
    chosen = name or profile_config.get("default_persona")
    if not chosen:
        raise ConfigError("profile.yaml has no `default_persona` and none was given.")
    if chosen not in personas:
        raise ConfigError(
            f"No persona {chosen!r} in profile.yaml. Available: {', '.join(sorted(personas))}"
        )
    return personas[chosen]
