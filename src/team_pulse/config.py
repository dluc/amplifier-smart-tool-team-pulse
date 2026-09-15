# SPDX-License-Identifier: MIT
"""Single config-resolution path for team_pulse.

Every setting has exactly one resolution order, high -> low:

  1. Explicit argument -- applied by the client, not this module.
  2. ``<state dir>/.env`` -- the file ``configure()`` writes, and the only
     user-editable config file.
  3. Real environment variable
  4. ``default-config.yaml``, shipped inside this package (model names only).

The config file beats the environment on purpose: the file is deliberate, an
environment variable is often ambient. ``TEAM_PULSE_DIR`` is the exception --
it locates the file, so it is read from the real environment only.

There is ONE user-editable config file, and it is a ``.env``. Settings use the
same ``TEAM_PULSE_*`` names whether they come from the environment or the file,
so there is one vocabulary to learn, not two.

This module owns tiers 2-4. Tier 1 is applied by TeamPulseClient.

Every environment variable this tool reads is named ``TEAM_PULSE_*``, except
the two provider keys (``OPENAI_API_KEY`` / ``ANTHROPIC_API_KEY``) which are
the providers' own conventional names.

Auth strategy is INFERRED from the credentials present: a usable key means key
auth, otherwise Azure AD. There is no override -- a caller selects the strategy
by supplying a key or not.

See CONFIGURATION.md for the user-facing reference.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from team_pulse.auth import (
    ApiKeyAuth,
    AuthStrategy,
    AzCredentialAuth,
    is_valid_key,
)

#: This package, for locating packaged data files.
PACKAGE: str = "team_pulse"

# ---------------------------------------------------------------------------
# Environment variable names
# ---------------------------------------------------------------------------

ENV_URL: str = "TEAM_PULSE_URL"
ENV_KEY: str = "TEAM_PULSE_KEY"
ENV_API_APP_ID: str = "TEAM_PULSE_API_APP_ID"
ENV_TIMEOUT: str = "TEAM_PULSE_TIMEOUT"
ENV_OPENAI_MODEL: str = "TEAM_PULSE_OPENAI_MODEL"
ENV_ANTHROPIC_MODEL: str = "TEAM_PULSE_ANTHROPIC_MODEL"

#: Provider keys keep the providers' own conventional names.
ENV_OPENAI_KEY: str = "OPENAI_API_KEY"
ENV_ANTHROPIC_KEY: str = "ANTHROPIC_API_KEY"

#: State-directory override. Defaults to ~/.team-pulse.
ENV_DIR: str = "TEAM_PULSE_DIR"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

#: Name of the defaults file shipped inside this package.
_DEFAULTS_NAME: str = "default-config.yaml"


def _packaged_defaults() -> dict[str, Any]:
    """The shipped ``default-config.yaml``, the lowest-precedence tier.

    Values live in that file rather than as literals here so a deployment can
    see and change every default in one readable place. There is deliberately
    no default for ``api_app_id``: an Azure AD application registration is
    specific to whoever deployed the Team Pulse server, so it is configuration,
    never a shipped constant.
    """
    from importlib.resources import files

    try:
        raw = yaml.safe_load(
            (files(PACKAGE) / _DEFAULTS_NAME).read_text(encoding="utf-8")
        )
    except (FileNotFoundError, OSError, yaml.YAMLError):
        return {}
    return raw if isinstance(raw, dict) else {}


def model_for(provider: str) -> str:
    """Return the configured model name for ``provider`` ('openai'|'anthropic').

    Resolution is the standard order: real env var, then ``.env``, then the
    shipped ``default-config.yaml``. No model name is hardcoded in Python.
    """
    key = f"{provider}_model"
    env_name = {"openai": ENV_OPENAI_MODEL, "anthropic": ENV_ANTHROPIC_MODEL}[provider]
    env_value = load_env().get(env_name, "").strip()
    if env_value:
        return env_value
    shipped = str(_packaged_defaults().get(key) or "").strip()
    if not shipped:
        raise ValueError(
            f"No model configured for {provider}: set {env_name}, or add "
            f"'{key}' to your config file. See CONFIGURATION.md."
        )
    return shipped


# ---------------------------------------------------------------------------
# Where the config file lives, and how it is read
# ---------------------------------------------------------------------------


def _state_dir() -> Path:
    """The tool's state directory. ``TEAM_PULSE_DIR``, else ``~/.team-pulse``."""
    env_dir = os.environ.get(ENV_DIR, "").strip()
    return Path(env_dir) if env_dir else Path.home() / ".team-pulse"


def _env_file_path() -> Path:
    """The config file: ``.env`` in the state directory.

    One fixed location, so the same command reads the same file no matter which
    directory it is run from. ``TEAM_PULSE_DIR`` moves it.
    """
    return _state_dir() / ".env"


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse simple ``KEY=value`` lines. A missing file contributes nothing."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def load_env() -> dict[str, str]:
    """The process environment overlaid by the ``.env`` file, which wins.

    The file beats the environment deliberately: the file is something the user
    wrote on purpose, whereas an environment variable is often ambient,
    inherited from a parent process or a shell profile nobody remembers.

    ``TEAM_PULSE_DIR`` is the one exception: it says where this file lives, so
    setting it inside the file is meaningless and is ignored. A blank value is
    treated as unset, so a template copied verbatim cannot mask a real
    environment variable.
    """
    file_values = _parse_env_file(_env_file_path())
    file_values.pop(ENV_DIR, None)
    file_values = {k: v for k, v in file_values.items() if v.strip()}
    merged = dict(os.environ)
    merged.update(file_values)
    return merged


# ---------------------------------------------------------------------------
# The configuration object
# ---------------------------------------------------------------------------


def _as_seconds(raw: str | None, default: float = 60.0) -> float:
    """Parse a timeout value. Fails loud on garbage rather than silently defaulting."""
    if raw is None:
        return default
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{ENV_TIMEOUT} must be a number of seconds, got {raw!r}."
        ) from exc
    if value <= 0:
        raise ValueError(f"{ENV_TIMEOUT} must be greater than 0, got {value}.")
    return value


@dataclass(frozen=True)
class Config:
    """Every setting this tool has, as plain values.

    One object, one reader. :meth:`from_env` is the ONLY place in the package
    that consults the environment or the ``.env`` file -- construct a ``Config``
    directly and nothing ambient is read, which is what lets a library caller
    configure this without touching ``os.environ``.

    Holds no live objects: the auth strategy is built on demand by
    :meth:`build_auth`, so a ``Config`` is cheap, comparable and safe to keep.
    """

    url: str = ""
    key: str | None = None
    api_app_id: str | None = None
    openai_key: str | None = None
    anthropic_key: str | None = None
    openai_model: str = ""
    anthropic_model: str = ""
    #: HTTP timeout in seconds for calls to the Team Pulse server.
    timeout: float = 60.0

    # -- construction -------------------------------------------------------

    @classmethod
    def from_env(cls) -> Config:
        """Read the environment and the ``.env`` file. The only reader."""
        env = load_env()
        shipped = _packaged_defaults()

        def pick(name: str) -> str | None:
            return env.get(name, "").strip() or None

        return cls(
            url=(pick(ENV_URL) or ""),
            key=pick(ENV_KEY),
            api_app_id=pick(ENV_API_APP_ID),
            timeout=_as_seconds(pick(ENV_TIMEOUT)),
            openai_key=pick(ENV_OPENAI_KEY),
            anthropic_key=pick(ENV_ANTHROPIC_KEY),
            openai_model=(
                pick(ENV_OPENAI_MODEL) or str(shipped.get("openai_model") or "").strip()
            ),
            anthropic_model=(
                pick(ENV_ANTHROPIC_MODEL)
                or str(shipped.get("anthropic_model") or "").strip()
            ),
        )

    def with_overrides(self, **fields: Any) -> Config:
        """A copy with *fields* replaced. ``None`` values are ignored."""
        from dataclasses import replace

        given = {k: v for k, v in fields.items() if v is not None}
        return replace(self, **given) if given else self

    # -- derived values -----------------------------------------------------

    def require_url(self) -> str:
        """The server URL, or a ValueError naming exactly how to set it."""
        if not self.url:
            raise ValueError(
                f"base_url is required: set {ENV_URL} in the environment or in "
                f"{_env_file_path()}, or run `team-pulse configure --url ...`. "
                "See CONFIGURATION.md."
            )
        return self.url

    def model_for(self, provider: str) -> str:
        """The configured model name for 'openai' or 'anthropic'."""
        name = {"openai": self.openai_model, "anthropic": self.anthropic_model}[
            provider
        ]
        if not name:
            env_name = {
                "openai": ENV_OPENAI_MODEL,
                "anthropic": ENV_ANTHROPIC_MODEL,
            }[provider]
            raise ValueError(
                f"No model configured for {provider}: set {env_name}. "
                "See CONFIGURATION.md."
            )
        return name

    def provider(self) -> tuple[str, str] | None:
        """(provider_name, key) for whichever model provider is configured."""
        if self.openai_key:
            return ("openai", self.openai_key)
        if self.anthropic_key:
            return ("anthropic", self.anthropic_key)
        return None

    def build_auth(
        self, *, credential: Any | None = None
    ) -> tuple[AuthStrategy, Literal["key", "az"]]:
        """Construct the auth strategy: (strategy, mode).

        A usable key means key auth; otherwise Azure AD. No override exists --
        supply a key, or don't.
        """
        return _select(self, credential)


# ---------------------------------------------------------------------------
# Strategy selection
# ---------------------------------------------------------------------------


def _select(
    settings: Config,
    credential: Any | None = None,
) -> tuple[AuthStrategy, Literal["key", "az"]]:
    """Return (strategy, mode). One rule: a usable key means key auth.

    There is deliberately no override. Which strategy runs follows from which
    credentials are present, so a caller selects it by supplying a key or not
    -- explicitly in a `Config`, or through the environment.
    """
    mode: Literal["key", "az"] = "key" if is_valid_key(settings.key) else "az"

    auth: AuthStrategy
    if mode == "key":
        auth = ApiKeyAuth(settings.key)
    else:
        if settings.api_app_id is None:
            raise ValueError(
                "Azure AD auth needs the app registration id of your Team Pulse "
                f"server. Set {ENV_API_APP_ID} in the environment or in "
                f"{_env_file_path()}, or set {ENV_KEY} to use key auth instead. "
                "See CONFIGURATION.md."
            )
        auth = AzCredentialAuth(api_app_id=settings.api_app_id, credential=credential)

    return auth, mode


def save_config(
    url: str,
    *,
    api_app_id: str | None = None,
    path: str | Path | None = None,
) -> Path:
    """Persist the endpoint (and optional app id) to the ``.env`` file.

    Merge semantics: any existing file is read first and only the provided
    keys are updated, so unrelated lines -- including a ``TEAM_PULSE_KEY`` the
    user put there -- survive untouched. Comments are not preserved. The write
    is atomic: a crash mid-write leaves the original file intact.

    Parameters
    ----------
    url:
        Team Pulse server URL. Required.
    api_app_id:
        Azure AD application registration id of the server. When absent, any
        existing value in the file is preserved.
    path:
        Where to write. Defaults to ``<state dir>/.env`` (``~/.team-pulse/.env``
        unless ``TEAM_PULSE_DIR`` says otherwise).

    Returns
    -------
    pathlib.Path
        The path written.
    """
    if not url or not url.strip():
        raise ValueError("url is required and must not be empty.")
    target = Path(path) if path is not None else _env_file_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    # READ existing file (merge semantics: preserve keys not provided)
    current = _parse_env_file(target)

    current[ENV_URL] = url.strip()
    if api_app_id is not None:
        current[ENV_API_APP_ID] = api_app_id.strip()

    body = "".join(f"{k}={v}\n" for k, v in sorted(current.items()))

    # ATOMIC WRITE: tempfile -> write -> os.replace (crash-safe)
    fd, temp_path_str = tempfile.mkstemp(dir=target.parent, suffix=".env.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(body)
        os.replace(temp_path_str, target)
    except BaseException:
        try:
            os.unlink(temp_path_str)
        except OSError:
            pass
        raise

    return target
