"""Private provider helper for this distribution's model-backed capability.

Deliberately local to this distribution: a smart tool is independently
installable, so it does not share a provider package with anything else.

Credentials are read at CALL time, never at import time. That is what lets
the deterministic paths import and run with no provider configured.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from team_pulse.config import Config

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

# Model names are NOT hardcoded here. They resolve through team_pulse.config:
# TEAM_PULSE_OPENAI_MODEL / TEAM_PULSE_ANTHROPIC_MODEL, then the user's
# then the shipped default-config.yaml. See CONFIGURATION.md.


class NoProviderConfigured(RuntimeError):
    """No model provider credentials were found for a model-backed path."""

    def __init__(self, capability: str) -> None:
        self.remedy = "Set OPENAI_API_KEY or ANTHROPIC_API_KEY, then retry."
        super().__init__(
            f"No model provider configured for the model-backed capability {capability!r}.\n"
            f"{self.remedy}"
        )


class ModelCallFailed(RuntimeError):
    """The provider was reachable but the call failed."""

    def __init__(self, message: str, remedy: str) -> None:
        super().__init__(message)
        self.remedy = remedy


def ensure_provider(capability: str, config: Config) -> None:
    """Raise `NoProviderConfigured` if neither provider key is set.

    Used to fail fast, BEFORE any other work (including deterministic
    precondition calls), so a caller with no provider never pays for partial
    work it cannot finish.
    """
    if config.provider() is None:
        raise NoProviderConfigured(capability)


@dataclass(frozen=True)
class ToolCall:
    """A tool call the provider validated against the schema we supplied."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ModelTurn:
    """One provider turn: either tool calls to run, or final text."""

    text: str | None
    tool_calls: tuple[ToolCall, ...]


def converse(
    *,
    capability: str,
    config: Config,
    system: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    timeout: float = 60.0,
) -> ModelTurn:
    """One turn of a native tool-calling conversation.

    The provider validates tool names and arguments against *tools*, so an
    unparseable response or an unknown action is not a case this code has to
    handle. Messages are provider-neutral here and converted per provider.
    """
    found = config.provider()
    if found is None:
        raise NoProviderConfigured(capability)
    provider, key = found
    if provider == "openai":
        return _turn_openai(config, key, system, messages, tools, timeout)
    return _turn_anthropic(config, key, system, messages, tools, timeout)


def _turn_openai(
    config: Config,
    key: str,
    system: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    timeout: float,
) -> ModelTurn:
    wire: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for m in messages:
        if m["role"] == "user":
            wire.append({"role": "user", "content": m["content"]})
        elif m["role"] == "assistant":
            entry: dict[str, Any] = {"role": "assistant", "content": m.get("text")}
            if m.get("tool_calls"):
                entry["tool_calls"] = [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {
                            "name": c.name,
                            "arguments": json.dumps(c.arguments),
                        },
                    }
                    for c in m["tool_calls"]
                ]
            wire.append(entry)
        else:  # tool result
            wire.append(
                {
                    "role": "tool",
                    "tool_call_id": m["tool_call_id"],
                    "content": m["content"],
                }
            )
    payload = {
        "model": config.model_for("openai"),
        "messages": wire,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ],
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            OPENAI_URL, headers={"Authorization": f"Bearer {key}"}, json=payload
        )
        _raise_for_provider(resp, "openai")
        message = resp.json()["choices"][0]["message"]
    calls = tuple(
        ToolCall(
            id=c["id"],
            name=c["function"]["name"],
            arguments=_loads_arguments(c["function"].get("arguments")),
        )
        for c in (message.get("tool_calls") or [])
    )
    return ModelTurn(text=message.get("content"), tool_calls=calls)


def _turn_anthropic(
    config: Config,
    key: str,
    system: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    timeout: float,
) -> ModelTurn:
    wire: list[dict[str, Any]] = []
    for m in messages:
        if m["role"] == "user":
            wire.append({"role": "user", "content": m["content"]})
        elif m["role"] == "assistant":
            blocks: list[dict[str, Any]] = []
            if m.get("text"):
                blocks.append({"type": "text", "text": m["text"]})
            for c in m.get("tool_calls") or []:
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": c.id,
                        "name": c.name,
                        "input": c.arguments,
                    }
                )
            wire.append({"role": "assistant", "content": blocks})
        else:  # tool result -- Anthropic carries these as user-turn blocks, and
            # consecutive results must share one turn.
            block = {
                "type": "tool_result",
                "tool_use_id": m["tool_call_id"],
                "content": m["content"],
            }
            if (
                wire
                and wire[-1]["role"] == "user"
                and isinstance(wire[-1]["content"], list)
            ):
                wire[-1]["content"].append(block)
            else:
                wire.append({"role": "user", "content": [block]})
    payload = {
        "model": config.model_for("anthropic"),
        "max_tokens": 4096,
        "system": system,
        "messages": wire,
        "tools": [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["input_schema"],
            }
            for t in tools
        ],
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
            json=payload,
        )
        _raise_for_provider(resp, "anthropic")
        content = resp.json().get("content", [])
    text = "".join(b.get("text", "") for b in content if b.get("type") == "text")
    calls = tuple(
        ToolCall(id=b["id"], name=b["name"], arguments=b.get("input") or {})
        for b in content
        if b.get("type") == "tool_use"
    )
    return ModelTurn(text=text or None, tool_calls=calls)


def _loads_arguments(raw: Any) -> dict[str, Any]:
    """OpenAI sends tool arguments as a JSON string; Anthropic sends an object."""
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _raise_for_provider(resp: httpx.Response, provider: str) -> None:
    if resp.status_code == 401:
        raise ModelCallFailed(
            f"{provider} rejected the credentials.",
            f"Check the {provider.upper()}_API_KEY value. See CONFIGURATION.md.",
        )
    if resp.status_code == 429:
        raise ModelCallFailed(
            f"{provider} rate-limited this request.",
            "Wait and retry, or use a key with higher limits.",
        )
    if resp.status_code >= 400:
        raise ModelCallFailed(
            f"{provider} returned HTTP {resp.status_code}: {resp.text[:200]}",
            "Retry; if it persists, check provider status and the configured model name.",
        )
