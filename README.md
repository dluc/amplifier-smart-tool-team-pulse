# team-pulse-reports

Manage a Team Pulse lens connection and use `ask-local` for model-backed, grounded answers. The public CLI capability surface is intentionally small:

- `ask-local` — answer a question with the active model-backed workflow
- `status` — report configuration and server reachability
- `configure` — persist the Team Pulse endpoint and optional app id
- `manifest` — return the machine-readable tool description

The lower-level corpus operations are hidden from the public catalog and CLI, but remain available internally to `ask-local` so it can retrieve evidence and return citations.

- [INSTALL.md](INSTALL.md)
- [CONFIGURATION.md](CONFIGURATION.md)

```bash
team-pulse-reports status
team-pulse-reports configure --url https://team-pulse.example.com
team-pulse-reports ask-local --question "What did we decide about the rename?"
team-pulse-reports manifest
```

## Active capabilities

| Verb | What it does | Library | Requirements |
|---|---|---|---|
| `ask-local` | Retrieves from the Team Pulse corpus with internal tools and returns a model-backed answer with citations. | `ask_local()` | Team Pulse configuration and an OpenAI or Anthropic provider key |
| `status` | Reports effective settings and whether the server is reachable. It does not expose secrets and does not raise for a broken setup. | `status()` | None; useful before configuration |
| `configure` | Saves the Team Pulse endpoint URL and optional Azure AD app id to the local settings file. | `configure()` | A valid HTTPS endpoint |
| `manifest` | Returns this tool's structured description, requirements, and capability metadata. | `manifest()` | None |

`ask-local` uses your configured model provider and may consume provider tokens. It is the only active capability that requires a model provider. Its internal retrieval tools remain enabled even though their public verbs are hidden. The tool performs no shared-data writes through the active surface.

## Configuration and behavior

- **One JSON document per call on stdout.** Failures use `{"error": {"type", "message", "remedy"}}` plus one stderr line and exit 1.
- **Configuration is explicit.** Run `team-pulse-reports status` first, then use `team-pulse-reports configure --url <url>` or set the environment variables described in [CONFIGURATION.md](CONFIGURATION.md).
- **Provider preconditions are checked first.** `ask-local` fails immediately if its provider key or Team Pulse configuration is missing.
- **Importing costs nothing.** `import team_pulse` succeeds in an empty environment; credentials resolve only when a capability is called.

## As a library

```python
import team_pulse as tp
from team_pulse import Config

cfg = Config(url="https://your-team-pulse-host", key="tp_...")
result = tp.ask_local("What did we decide about the rename?", config=cfg)
print(result.answer)
```

Pass a `Config` to avoid ambient environment settings. The active library surface mirrors the four capabilities above; the retained API implementations are not advertised until re-enabled in the catalog.
