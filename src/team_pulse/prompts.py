"""Loads the model-facing prompt text as package data.

Two documents, both shipped verbatim and both handed to the model that
`ask_local` drives -- exactly what the bundle gave its expert agent:

* `prompts/retrieval-strategy.md` -- the agent's instruction.
* the manifest's "Data model reference" section -- the data model, endpoint
  surface and common query patterns. The bundle @-mentioned this from the
  instruction, so its agent received both; porting only the instruction left
  the model told to consult a reference it could not reach.

The reference lives in `SMART_TOOL.md` rather than beside this module so that
one copy serves both readers: the model driven by `ask_local`, and anyone --
human or agent -- who reads the manifest to learn how to call the tool. A
pointer would have served neither, since the packaged copy is not a path a
shell can open.

Nothing in this module paraphrases either.

Mirrors `team_pulse.manifest`'s packaged-copy-with-source-fallback pattern: a
wheel carries only package data, so the build force-includes a copy at
`team_pulse/_packaged/retrieval-strategy.md` (see pyproject.toml); this module
reads that copy first, falling back to the source tree for editable installs.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

PACKAGE = "team_pulse"
_STRATEGY_NAME = "retrieval-strategy.md"
_REFERENCE_HEADING = "## Data model reference"


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


def data_model_reference() -> str:
    """Return the manifest's data-model reference section, verbatim."""
    from team_pulse.manifest import manifest

    body = manifest().body
    _, sep, reference = body.partition(_REFERENCE_HEADING)
    if not sep:
        raise PromptUnavailable(
            f"the manifest body has no {_REFERENCE_HEADING!r} section. "
            "Reinstall the distribution."
        )
    return reference.strip()


def retrieval_strategy() -> str:
    """Return the system prompt: the strategy, then the reference it cites.

    The strategy's closing section says the reference follows below, so the
    two are concatenated rather than left for a caller to assemble.
    """
    return f"{_read(_STRATEGY_NAME).rstrip()}\n\n{data_model_reference()}"
