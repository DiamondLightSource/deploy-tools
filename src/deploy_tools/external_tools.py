import subprocess
from pathlib import Path
from typing import Any

from .errors import DeployToolsError


class ExternalToolError(DeployToolsError):
    """Raised when a required external command-line tool is missing or fails."""


def run_command(
    command: list[str | Path],
    *,
    check: bool = False,
    capture_output: bool = False,
    text: bool = False,
) -> subprocess.CompletedProcess[Any]:
    """Run an external command, surfacing tool problems as clean domain errors.

    Wraps ``subprocess.run`` so that a missing executable (or, when ``check`` is set, a
    non-zero exit) is reported as an ``ExternalToolError`` rather than a raw
    ``FileNotFoundError``/``CalledProcessError`` traceback.

    Args:
        command: The command to run, as a list whose first element is the executable.
        check: If True, raise when the command exits with a non-zero status.
        capture_output: If True, capture the command's stdout and stderr.
        text: If True, decode captured output as text rather than bytes.

    Returns:
        The ``subprocess.CompletedProcess`` for the finished command.

    Raises:
        ExternalToolError: If the executable cannot be found, or ``check`` is set and
            the command exits with a non-zero status.
    """
    executable = str(command[0])
    try:
        return subprocess.run(
            command, check=check, capture_output=capture_output, text=text
        )
    except FileNotFoundError as exc:
        raise ExternalToolError(
            f"Required external tool not found: '{executable}'.\n"
            f"Ensure it is installed and available on PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise ExternalToolError(
            f"External tool '{executable}' failed with exit status {exc.returncode}."
        ) from exc
