"""Loads the model-facing retrieval strategy as package data.

The strategy is the only model-facing document shipped with the active
capability surface. It is packaged with the wheel and read verbatim, with a
source-tree fallback for editable installs.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

PACKAGE = "team_pulse"
_STRATEGY_NAME = "retrieval-strategy.md"


class PromptUnavailable(RuntimeError):
    """A packaged prompt document could not be located."""


def _read(name: str) -> str:
    """Return a packaged prompt document, verbatim."""
    packaged = resources.files(PACKAGE) / "_packaged" / name
    if packaged.is_file():
        return packaged.read_text(encoding="utf-8")
    # Editable install: src/<pkg>/prompts.py -> distribution root is parents[2].
    source = Path(__file__).resolve().parents[2] / "prompts" / name
    if source.is_file():
        return source.read_text(encoding="utf-8")
    raise PromptUnavailable(
        f"{name} was not found in the installed package or the source tree. "
        "Reinstall the distribution."
    )


def retrieval_strategy() -> str:
    """Return the system prompt for the active `ask_local` capability."""
    return _read(_STRATEGY_NAME).rstrip()
