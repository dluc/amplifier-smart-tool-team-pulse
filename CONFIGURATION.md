# Configuration

`team-pulse-reports status` reports what is and isn't configured. It runs with nothing
set and never fails — describing a broken setup is its job. Use it whenever you
are unsure.

## Quick start

```bash
team-pulse-reports configure --url https://your-team-pulse-host
az login                                    # or: export TEAM_PULSE_KEY=tp_...
team-pulse-reports status
```

## Authentication

Two ways in. Do one.

**Azure AD**, for a person at a terminal:

```bash
az login
export TEAM_PULSE_API_APP_ID=<your server's app registration id>
```

`TEAM_PULSE_API_APP_ID` identifies the *server*, not you: the tool asks Azure
for the scope `api://<app-id>/.default`. It is not a secret and has no default —
ask whoever runs your Team Pulse server.

Only `az login` sessions are used. An ambient managed identity will not be
picked up instead, which is deliberate.

**API key**, for automation:

```bash
export TEAM_PULSE_KEY=tp_...
```

Nothing else is needed.

**Which one runs is inferred.** A `TEAM_PULSE_KEY` starting `tp_` selects key
auth and Azure is never tried; anything else — unset, blank, or missing the
prefix — falls through to Azure without an error. If you set a key and see
Azure being used, check the prefix.

## Settings

| Env var | What it is |
|---|---|
| `TEAM_PULSE_URL` | **Required.** Your endpoint. Also `team-pulse-reports configure --url`. |
| `TEAM_PULSE_KEY` | API key. See above. |
| `TEAM_PULSE_API_APP_ID` | Azure app registration. Also `configure --client-id`. |
| `TEAM_PULSE_DIR` | Directory holding the config file. Default `~/.team-pulse`. Environment only. |
| `TEAM_PULSE_TIMEOUT` | Seconds to wait on the Team Pulse server. Default 60. Raise it if a Team Pulse request used by `ask-local` times out. |
| `TEAM_PULSE_OPENAI_MODEL` | Model `ask-local` uses with OpenAI. |
| `TEAM_PULSE_ANTHROPIC_MODEL` | Model `ask-local` uses with Anthropic. |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Only `ask-local` needs one. |

## The config file

One file, `~/.team-pulse/.env`, using the same names as the environment:

```
TEAM_PULSE_URL=https://your-team-pulse-host
TEAM_PULSE_API_APP_ID=00000000-0000-0000-0000-000000000000
TEAM_PULSE_KEY=tp_...
```

Always read from that one path, whatever directory you run in. `TEAM_PULSE_DIR`
moves it. `team-pulse-reports configure` writes it, merging — an existing key survives,
and `configure` never writes a key itself.

## Using it as a library

Every capability takes an optional `config`. Pass one and no environment
variable or file is consulted:

```python
from team_pulse import Config, ask_local

cfg = Config(url="https://your-team-pulse-host", key="tp_...")
ask_local("What did we decide about onboarding?", config=cfg)
```

`Config.from_env()` is the only thing in the package that reads the environment
or the `.env` file. Omitting `config` calls it for you.

## Precedence

1. An explicit CLI flag or function argument
2. `~/.team-pulse/.env`
3. Environment variable
4. `default-config.yaml`, shipped in the package — model names only

**The file beats the environment.** A file value is one you wrote on purpose; an
environment variable is often ambient. A blank line in the file counts as unset,
so it never masks the environment.

`TEAM_PULSE_DIR` is the exception: environment only, ignored inside the file,
since it says where the file is.

## Network

Outbound HTTPS, and nothing else:

| Host | When |
|---|---|
| your configured endpoint | `ask-local` and server reachability checks from `status` |
| `login.microsoftonline.com` | Azure AD auth only |
| `api.openai.com` / `api.anthropic.com` | `ask-local` only |
