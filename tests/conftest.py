from pathlib import Path

import pytest
from typer.testing import CliRunner

from deploy_tools.__main__ import app

runner = CliRunner()


def run_cli(*args: str | Path):
    result = runner.invoke(app, [str(x) for x in args])
    if result.exception:
        raise result.exception
    assert result.exit_code == 0, result


@pytest.fixture
def schemas():
    return Path(__file__).parent.parent / "src" / "deploy_tools" / "models" / "schemas"


@pytest.fixture
def samples():
    return Path(__file__).parent / "samples"


@pytest.fixture
def demo_config():
    return Path(__file__).parent.parent / "src" / "deploy_tools" / "demo_configuration"
