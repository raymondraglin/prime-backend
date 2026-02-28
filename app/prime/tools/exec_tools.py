"""
PRIME Exec Tools
File: app/prime/tools/exec_tools.py

Sandboxed code execution for verification (the 'prove it' layer).

Backends:
  LocalSubprocessBackend  — spawns a subprocess with strict limits
  (ContainerBackend)      — future: Docker isolation for untrusted code

Safety rules (configurable via env vars):
  EXEC_TIMEOUT_SECONDS    — max wall-clock seconds per run (default: 10)
  EXEC_MAX_OUTPUT_BYTES   — max stdout+stderr bytes returned (default: 8192)
  EXEC_ALLOWED_COMMANDS   — comma-separated allowlist for run_command

run_python:  executes Python via sys.executable in a fresh temp dir
run_command: executes shell commands from the allowlist only

Returns structured results: {stdout, stderr, exit_code, duration_ms}
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_TIMEOUT_SECONDS  = int(os.getenv("EXEC_TIMEOUT_SECONDS",  "10"))
_MAX_OUTPUT_BYTES = int(os.getenv("EXEC_MAX_OUTPUT_BYTES", "8192"))

_DEFAULT_ALLOWED = {"pytest", "ruff", "mypy", "python", "python3", "node", "npm", "pip"}
_ALLOWED_COMMANDS: set[str] = set(
    c.strip()
    for c in os.getenv("EXEC_ALLOWED_COMMANDS", ",".join(_DEFAULT_ALLOWED)).split(",")
    if c.strip()
)


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

def _run_subprocess(cmd: list[str], cwd: str | None = None) -> dict[str, Any]:
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=_TIMEOUT_SECONDS,
            cwd=cwd,
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONIOENCODING": "utf-8",
            },
        )
        duration_ms = round((time.monotonic() - start) * 1000, 1)
        stdout = proc.stdout[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
        stderr = proc.stderr[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
        return {
            "stdout":      stdout,
            "stderr":      stderr,
            "exit_code":   proc.returncode,
            "duration_ms": duration_ms,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout":      "",
            "stderr":      f"Execution timed out after {_TIMEOUT_SECONDS}s",
            "exit_code":   -1,
            "duration_ms": float(_TIMEOUT_SECONDS * 1000),
        }
    except Exception as exc:
        return {
            "stdout":      "",
            "stderr":      str(exc),
            "exit_code":   -1,
            "duration_ms": 0.0,
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_python(code: str) -> dict[str, Any]:
    """
    Execute a Python snippet in a fresh temp directory.
    Returns: {stdout, stderr, exit_code, duration_ms}
    """
    with tempfile.TemporaryDirectory(prefix="prime_exec_") as tmpdir:
        script_path = os.path.join(tmpdir, "script.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        return _run_subprocess([sys.executable, script_path], cwd=tmpdir)


def run_command(command: str) -> dict[str, Any]:
    """
    Execute a whitelisted shell command.
    Returns: {stdout, stderr, exit_code, duration_ms}
    """
    parts = command.strip().split()
    if not parts:
        return {"stdout": "", "stderr": "Empty command", "exit_code": -1, "duration_ms": 0.0}

    base_cmd = os.path.basename(parts[0]).lower().rstrip(".exe")
    if base_cmd not in _ALLOWED_COMMANDS:
        return {
            "stdout":      "",
            "stderr":      (
                f"Command '{parts[0]}' is not in the allowed list. "
                f"Allowed: {sorted(_ALLOWED_COMMANDS)}"
            ),
            "exit_code":   -1,
            "duration_ms": 0.0,
        }

    return _run_subprocess(parts)
