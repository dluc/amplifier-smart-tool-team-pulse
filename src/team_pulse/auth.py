# SPDX-License-Identifier: MIT
"""Authentication strategies for TeamPulseClient.

TeamPulseClient depends only on the AuthStrategy protocol; it never branches
on a concrete strategy. Two implementations are provided:

* ApiKeyAuth -- attaches the API key via the ``X-Team-Pulse-Key`` request header.
* AzCredentialAuth -- attaches an Azure AD bearer token via the ``Authorization``
  header. ``azure-identity`` is imported lazily, only when this strategy is
  actually used with no injected credential -- so `import team_pulse` and the
  deterministic key-auth path never require it to be installed.
"""

from __future__ import annotations

import base64
import json
import time
from typing import Any, Protocol, runtime_checkable

from team_pulse.errors import TeamPulseAuthError


@runtime_checkable
class AuthStrategy(Protocol):
    """Minimal protocol every authentication strategy must satisfy."""

    async def headers(self) -> dict[str, str]: ...


def is_valid_key(key: str | None) -> bool:
    """N1 rule: a key is 'present' iff non-empty after strip AND prefixed 'tp_'.

    Anything else (empty, whitespace-only, or not tp_-prefixed) is treated as
    absent (= 'malformed') and triggers Azure fallback.
    """
    if not key:
        return False
    stripped = key.strip()
    return bool(stripped) and stripped.startswith("tp_")


class ApiKeyAuth:
    """Authentication via a static API key in the ``X-Team-Pulse-Key`` header."""

    def __init__(self, key: str | None) -> None:
        if not is_valid_key(key):
            raise TeamPulseAuthError(
                "API key missing or malformed: it must be non-empty and start with 'tp_'."
            )
        assert key is not None
        self._key = key.strip()

    async def headers(self) -> dict[str, str]:
        return {"X-Team-Pulse-Key": self._key}


# ---------------------------------------------------------------------------
# Azure credential factory -- single seam for test/prod injection
# ---------------------------------------------------------------------------


def _build_credential(credential: Any | None) -> Any:
    """Return *credential* verbatim if provided; otherwise construct AzureCliCredential.

    This factory is the single seam that lets tests inject a fake credential while
    production code always gets the real AzureCliCredential. Deliberately narrower than
    azure-identity's DefaultAzureCredential: that chain ranks ManagedIdentityCredential
    (and EnvironmentCredential / WorkloadIdentityCredential) ahead of AzureCliCredential,
    so on any host where those resolve ambiently -- e.g. an Azure VM with a managed
    identity assigned -- it silently authenticates as the host/service instead of the
    signed-in developer. This is developer-facing interactive tooling; the human's
    `az login` session is always what we want by default. A caller that genuinely needs
    a different credential (managed identity, a service principal, VS Code sign-in, ...)
    injects it explicitly via the `credential` parameter.
    """
    if credential is not None:
        return credential
    from azure.identity.aio import AzureCliCredential

    return AzureCliCredential()


# ---------------------------------------------------------------------------
# JWT claim peek -- display-only, no signature verification
# ---------------------------------------------------------------------------


def _decode_bearer_identity_hint(token: str) -> str | None:
    """Best-effort, display-only read of a JWT's identity claim.

    Decodes the token's payload segment WITHOUT verifying its signature. This
    is never a security decision -- the token was already minted for us by
    Azure and already validated by whatever service accepts it; we are only
    reading a claim back out for human-readable provenance (e.g.
    ``status()``). Returns the first present claim of ``upn``,
    ``preferred_username``, ``unique_name``, or ``appid`` (service-principal
    fallback), or ``None`` if the token isn't a parseable JWT or carries none
    of those claims.
    """
    try:
        payload_segment = token.split(".")[1]
        padding = "=" * (-len(payload_segment) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload_segment + padding))
    except Exception:  # noqa: BLE001 -- display-only; never raise on a malformed token
        return None
    if not isinstance(claims, dict):
        return None
    for claim in ("upn", "preferred_username", "unique_name", "appid"):
        value = claims.get(claim)
        if isinstance(value, str) and value:
            return value
    return None


# ---------------------------------------------------------------------------
# AzCredentialAuth -- Azure AD bearer-token strategy
# ---------------------------------------------------------------------------


class AzCredentialAuth:
    """Emits ``Authorization: Bearer <token>`` from an Azure AD credential.

    Tokens are acquired lazily on the first ``headers()`` call and cached
    until within ``_SKEW_SECONDS`` of their reported expiry. TeamPulseClient
    acquires eagerly at ``__aenter__`` by calling ``headers()`` once before
    the session starts.
    """

    _SKEW_SECONDS = 300

    def __init__(self, *, api_app_id: str, credential: Any | None = None) -> None:
        # Fail loud immediately -- an empty api_app_id builds scope "api:///.default"
        # which Entra rejects with AADSTS500011. There is no shipped default: the
        # application registration belongs to whoever deployed the Team Pulse server,
        # so the caller must supply it.
        if not api_app_id or not str(api_app_id).strip():
            raise ValueError(
                "AzCredentialAuth requires a non-empty api_app_id. "
                "An empty value would produce scope 'api:///.default' which Entra rejects "
                "(AADSTS500011). Set TEAM_PULSE_API_APP_ID or 'api_app_id' in "
                "your config file -- ask whoever operates your Team Pulse server for "
                "the value. See CONFIGURATION.md."
            )
        self._api_app_id = str(api_app_id).strip()
        self._scope = f"api://{self._api_app_id}/.default"
        self._credential = _build_credential(credential)
        self._token: str | None = None
        self._expires_at: float = 0.0

    @property
    def api_app_id(self) -> str:
        """Read-only: the Azure AD application ID used for scope construction."""
        return self._api_app_id

    async def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {await self._get_token()}"}

    async def close(self) -> None:
        """Close the underlying Azure credential to release its aiohttp session.

        ``azure.identity.aio.DefaultAzureCredential`` holds an ``aiohttp.ClientSession``
        internally. Failing to call ``close()`` produces ``Unclosed client session``
        warnings at process exit. This method is idempotent -- safe to call multiple times.
        """
        if hasattr(self._credential, "close"):
            await self._credential.close()

    async def _get_token(self) -> str:
        now = time.time()
        if self._token and now < self._expires_at - self._SKEW_SECONDS:
            return self._token
        try:
            access = await self._credential.get_token(self._scope)
        except Exception as exc:
            raise TeamPulseAuthError(
                f"No Azure credential available -- run `az login`. To use a different "
                f"credential (managed identity, a service principal, etc.), construct "
                f"AzCredentialAuth(credential=...) yourself. Underlying error: {exc}"
            ) from exc
        token_str: str = access.token
        self._token = token_str
        self._expires_at = float(access.expires_on)
        return token_str

    @property
    def az_identity_hint(self) -> str | None:
        """Best-effort, display-only AZURE identity read from the last-fetched token.

        This is the raw Azure AD token's own claim -- NOT team-pulse's resolved
        identity. The server resolves its own view of who you are at request
        time, and the two need not match. ``None`` before the first ``headers()``
        call, or if the token carries none of the recognised claims (``upn``
        / ``preferred_username`` / ``unique_name`` / ``appid``). Never used
        for authorization -- this is provenance for humans (e.g. ``status()``),
        not a security decision; the signature is never checked.
        """
        if self._token is None:
            return None
        return _decode_bearer_identity_hint(self._token)
