"""The three assertions that are not negotiable by a scope or style argument.

These are the project's only mechanical guarantees. Everything else is discipline, so if one of
these starts failing, the correct response is to fix the code rather than to relax the test.

  1. No code path can submit an application.          docs/adr/0010, CLAUDE.md
  2. Stage 1 ships no network code.                   docs/adr/0005
  3. Posting text is data, never instruction.         docs/planning/10-build-plan.md
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def _python_files() -> list[Path]:
    return sorted(SRC.rglob("*.py"))


def test_source_tree_is_not_empty() -> None:
    """Guard the other tests: all three pass trivially against no files."""
    assert _python_files(), f"No Python files under {SRC} - the other assertions prove nothing."


# ---------------------------------------------------------------------------
# 1. No submit-capable code path.
# ---------------------------------------------------------------------------

SUBMIT_CALLS = {
    # HTTP verbs that could post an application form.
    "post",
    "put",
    "patch",
    # Browser-driving actions that could press a button.
    "click",
    "submit",
    "press",
    "tap",
    "dblclick",
    "check",
    "select_option",
    "set_input_files",
}


def test_no_module_exposes_a_submit_operation() -> None:
    """No function named like a submit, and no call to one.

    The reframing that "filling the form is the applying, the submit button is the human's" does
    not survive contact with real portals: attaching a resume or finishing step one persists state
    the employer can see, with no submit event to detect. So the boundary is this test.
    """
    offenders: list[str] = []

    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                name = node.name.lstrip("_")
                if name.startswith("submit") or name.endswith("_submit"):
                    offenders.append(f"{path.name}:{node.lineno} defines {node.name}()")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in SUBMIT_CALLS:
                    offenders.append(f"{path.name}:{node.lineno} calls .{node.func.attr}()")

    assert not offenders, (
        "Submit-capable code found. This is the project's hardest rule and the only "
        "mechanical guarantee behind it:\n  " + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# 2. No network code in stages 1 and 2.
# ---------------------------------------------------------------------------

FORBIDDEN_IMPORTS = {
    "httpx",
    "requests",
    "playwright",
    "aiohttp",
    "urllib3",
    "urllib.request",
    "selenium",
    "socket",
}


def test_no_module_imports_a_network_library() -> None:
    """Stage 1 has no network surface at all, which is also why it has no injection surface.

    Lift this only when stage 3's source-policy ADR exists - not before, and not for a
    "structured, documented, public" API, which is still a fetch.
    """
    offenders: list[str] = []

    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                root = name.split(".")[0]
                if name in FORBIDDEN_IMPORTS or root in FORBIDDEN_IMPORTS:
                    offenders.append(f"{path.name}:{node.lineno} imports {name}")

    assert not offenders, (
        "Network import found. Stage 1 and 2 ship no network code, and every fetch waits for "
        "the source-policy ADR (docs/adr/0006):\n  " + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# 3. Posting text is data, never instruction.
# ---------------------------------------------------------------------------

DANGEROUS_SINKS = re.compile(
    r"\b(eval|exec|compile|system|popen|check_output|call|run)\s*\(",
)


def test_no_dynamic_execution_anywhere() -> None:
    """Posting text comes from a stranger. It must never reach an interpreter or a shell.

    A broad check on purpose: this codebase has no legitimate reason to evaluate a string, so
    anything matching is either a mistake or needs an explicit exemption argued in review.
    """
    offenders: list[str] = []

    for path in _python_files():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if DANGEROUS_SINKS.search(stripped):
                offenders.append(f"{path.name}:{lineno} {stripped[:70]}")

    assert not offenders, (
        "Dynamic execution found. Posting text is untrusted data and must never become an "
        "instruction, a path, a filename, or a shell argument:\n  " + "\n  ".join(offenders)
    )


def test_no_shell_true() -> None:
    """`shell=True` turns any string that reaches it into a command line."""
    offenders = [
        f"{path.name}:{lineno}"
        for path in _python_files()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if "shell=True" in line and not line.strip().startswith("#")
    ]
    assert not offenders, "shell=True found: " + ", ".join(offenders)
