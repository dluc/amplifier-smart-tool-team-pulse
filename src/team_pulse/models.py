# SPDX-License-Identifier: MIT
"""Data / wire contract for team_pulse.

These shapes are part of the **public API**. A breaking change to any field
name, type, or default is a **MAJOR version bump**. Additive changes (new
optional fields) are MINOR.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Question:
    """A reflection question retrieved from the Team Pulse server."""

    question_id: str
    question: str
    lookback_days: int | None = None


@dataclass
class AnswerUpload:
    """Payload sent to the server when submitting an AI-synthesised answer."""

    question_id: str
    user_id: str
    answer: str
    generated_at: str  # ISO-8601 UTC string, e.g. "2026-06-25T17:00:00Z"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientInfo:
    """Snapshot of the resolved client configuration and credential state."""

    base_url: str
    auth_mode: Literal["key", "az"]  # active identity mode
    api_app_id: str | None  # None when auth_mode == "key"
    credential_type: Literal["api_key", "azure_default_credential"]
    resolved: bool  # False before __aenter__, True after credential materialises
    az_identity_hint: str | None = (
        None  # RAW Azure AD token claim (upn/appid), unverified,
    )
    # NOT team-pulse identity
