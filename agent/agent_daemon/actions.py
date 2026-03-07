from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import List


class ActionExecutionError(RuntimeError):
    pass


def run_action(command_template: str, *, file_path: Path, context: dict | None = None) -> subprocess.CompletedProcess:
    context = context or {}
    context = {**context, "file": str(file_path)}
    formatted = command_template.format(**context)
    cmd_parts: List[str] = shlex.split(formatted)
    if not cmd_parts:
        raise ActionExecutionError("Empty command")
    try:
        print("!!!! calling action:")
        print(cmd_parts)
        result = subprocess.run(cmd_parts, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - actual execution
        raise ActionExecutionError(exc.stderr or exc.stdout or str(exc)) from exc
    return result
