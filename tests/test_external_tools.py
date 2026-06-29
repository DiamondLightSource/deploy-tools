import pytest

from deploy_tools.external_tools import ExternalToolError, run_command


def test_run_command_reports_missing_tool():
    # A required external tool that is not installed must surface as a clean
    # ExternalToolError naming the tool, not a raw FileNotFoundError traceback.
    with pytest.raises(ExternalToolError, match="deploy-tools-no-such-binary"):
        run_command(["deploy-tools-no-such-binary"])


def test_run_command_reports_failed_tool():
    # With check=True, a non-zero exit is reported as an ExternalToolError rather than a
    # raw CalledProcessError.
    with pytest.raises(ExternalToolError, match="exit status"):
        run_command(["bash", "-c", "exit 3"], check=True)
