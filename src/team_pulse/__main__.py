"""Allow running the CLI as ``python -m team_pulse``.

A fallback for when the ``team-pulse`` console script isn't on PATH -- which
happens whenever the distribution was installed into an environment whose
``bin/`` isn't exported (an Amplifier environment, a container layer, a venv
that was never activated). The caller always has a working invocation as long
as the package is importable at all, so "command not found" never becomes a
question the user has to answer.
"""

from team_pulse.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
