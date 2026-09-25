# Install

```bash
uv tool install 'team-pulse-reports @ git+https://github.com/microsoft/amplifier-smart-tool-team-pulse'
team-pulse-reports status
```

No virtual environment is needed, and none should be created — `uv tool install`
builds the tool in its own environment and puts `team-pulse-reports` on PATH. Do **not**
use `uv pip install` for the CLI: that is a library install and fails with
`No virtual environment found` when no venv is active.

`status` runs with nothing configured and reports `"configured": false` on a
fresh install. That is success. Configure it next — see
[CONFIGURATION.md](CONFIGURATION.md).

Requires Python ≥ 3.12 and [uv](https://docs.astral.sh/uv/).

## Variants

| | |
|---|---|
| Upgrade | same command, add `--force` |
| From a local checkout | `uv tool install /path/to/repo` |
| Run without installing | `uvx --from git+https://github.com/dluc/amplifier-smart-tool-team-pulse team-pulse-reports status` |
| Uninstall | `uv tool uninstall team-pulse-reports` |

If `team-pulse-reports` isn't found after installing, `uv tool update-shell` and open a
new shell, or invoke it as `python -m team_pulse`.

## Developing on the tool

```bash
uv venv && source .venv/bin/activate
uv pip install -e . pytest
pytest tests/
```

An editable install tracks your edits; `uv tool install` from a local path
builds a snapshot and does not.
