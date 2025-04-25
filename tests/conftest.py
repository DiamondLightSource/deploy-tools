import os
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from deploy_tools.__main__ import app

runner = CliRunner()


def run_cli(*args):
    result = runner.invoke(app, [str(x) for x in args])
    if result.exception:
        raise result.exception
    assert result.exit_code == 0, result


# Prevent pytest from catching exceptions when debugging in vscode so that break on
# exception works correctly (see: https://github.com/pytest-dev/pytest/issues/7409)
if os.getenv("PYTEST_RAISE", "0") == "1":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call: pytest.CallInfo[Any]):
        if call.excinfo is not None:
            raise call.excinfo.value
        else:
            raise RuntimeError(
                f"{call} has no exception data, an unknown error has occurred"
            )

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo: pytest.ExceptionInfo[Any]):
        raise excinfo.value


@pytest.fixture
def schemas():
    return Path(__file__).parent.parent / "src" / "deploy_tools" / "models" / "schemas"
