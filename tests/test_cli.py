import subprocess
import sys
from pathlib import Path

from deploy_tools import __version__


def test_cli_version() -> None:
    cmd = [sys.executable, "-m", "deploy_tools", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


def test_cli_reports_domain_error_without_traceback(tmp_path: Path) -> None:
    # compare on an existing area with no snapshot raises SnapshotError, a
    # DeployToolsError. Run the real entry point and confirm the message is presented as
    # a clean 'Error: ...' on stderr with exit 1, and no traceback is dumped.
    cmd = [sys.executable, "-m", "deploy_tools", "compare", str(tmp_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 1
    assert "Error:" in result.stderr
    assert "snapshot not found" in result.stderr
    assert "Traceback" not in result.stderr
