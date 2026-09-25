---
smart_tool_format: 1
name: team-pulse-reports
version: 0.1.0
description: >
  Configures and inspects a Team Pulse lens connection, exposes its active
  capability metadata, and answers factual team questions through a model-backed
  retrieval workflow with citations.
use_cases:
  - Answer factual team questions with grounded citations
  - Inspect configuration and server reachability
  - Configure the Team Pulse endpoint locally
  - Discover the active capability surface as structured data
platforms:
  - linux
  - macos
requires:
  - name: network access to the lens API
    purpose: >
      The configured Team Pulse endpoint URL must be reachable over HTTPS.
      Required for `ask-local` and the reachability check in `status`.
    install: CONFIGURATION.md
  - name: team-pulse credentials
    purpose: >
      `ask-local` needs either a per-user Azure AD bearer token (az login)
      or a shared API key. Without either, every capability raises with a remedy.
    install: CONFIGURATION.md
  - name: model provider credentials
    purpose: >
      Only `ask-local` needs OPENAI_API_KEY or ANTHROPIC_API_KEY. Every deterministic
      capability runs with no provider configured at all.
    optional: true
    install: CONFIGURATION.md
---
# team-pulse-reports

Team Pulse connection tooling, with `ask-local` as the active model-backed retrieval capability.

## Active capability surface

Only these four capabilities are currently advertised by the catalog, CLI, manifest, and model tool list:

| Verb | Purpose | Requirements |
|---|---|---|
| `ask-local` | Retrieve from the corpus with internal tools and return a model-backed answer with citations. | Team Pulse configuration plus `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` |
| `status` | Report effective settings and server reachability without exposing secrets. | None |
| `configure` | Persist the Team Pulse endpoint URL and optional Azure AD app id locally. | Endpoint URL |
| `manifest` | Return this tool's structured metadata and active capability descriptions. | None |

The lower-level retrieval implementations are hidden from the advertised surface and unavailable as CLI verbs, but remain internal tools for `ask-local`.

## Install

```bash
uv tool install 'team-pulse-reports @ git+https://github.com/dluc/amplifier-smart-tool-team-pulse'
team-pulse-reports status
```

A virtual environment is not required. For local development, use an editable install:

```bash
uv tool install --editable /path/to/amplifier-smart-tool-team-pulse
team-pulse-reports status
```

## Worked invocations

```bash
team-pulse-reports status
team-pulse-reports configure --url https://team-pulse.example.com
team-pulse-reports ask-local --question "What did we decide about the rename?"
team-pulse-reports manifest
```

## Sharp edges

- **`ask-local` costs tokens.** It uses your configured OpenAI or Anthropic provider and the model decides when it has enough to answer.
- **Configuration is checked before model work.** `ask-local` fails immediately when the provider key or Team Pulse endpoint is missing.
- **The active surface does not write shared team data.**
- **Importing costs nothing.** Credentials are read at call time, not import time.

## Which call answers which question

The active surface has one question-answering capability:

| Question | Call |
|---|---|
| "What did we decide about X, and why?" | `ask-local --question "..."` — retrieves internal evidence and cites the resource IDs used |
| "Is the tool configured?" | `status` |
| "How do I save the endpoint?" | `configure --url <url>` |
| "What does this tool expose?" | `manifest` |

Raw corpus browsing is available only inside `ask-local`; it is not exposed as public CLI capability.

## Using it well

1. Use `status` first to inspect configuration and reachability.
2. Use `configure` to persist the endpoint when it is not already configured.
3. Use `ask-local` for factual questions that should be grounded in the team's corpus.
4. Use `manifest` when a program needs to discover the active surface.
