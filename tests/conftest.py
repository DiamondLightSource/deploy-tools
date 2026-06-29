from pathlib import Path

import pytest
from typer.testing import CliRunner

from deploy_tools.__main__ import app

runner = CliRunner()


def run_cli(*args: str | Path) -> str:
    result = runner.invoke(app, [str(x) for x in args])
    if result.exception:
        raise result.exception
    assert result.exit_code == 0, result
    return result.stdout


@pytest.fixture
def schemas() -> Path:
    return Path(__file__).parent.parent / "src" / "deploy_tools" / "models" / "schemas"


@pytest.fixture
def samples() -> Path:
    return Path(__file__).parent / "samples"


@pytest.fixture
def configs() -> Path:
    return Path(__file__).parent / "configs"


@pytest.fixture
def stub_apptainer_pull(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the external ``apptainer pull`` so builds need no binary or network.

    Only the external command is replaced; ``create_sif_file``'s own logic (path
    validation, parent-directory creation) still runs. The golden-master comparison
    ignores ``.sif`` files, so a no-op suffices. Without this, building an Apptainer
    module hard-fails on a runner without apptainer or does a real registry pull.

    Args:
        monkeypatch: The pytest ``monkeypatch`` fixture.
    """

    def _no_pull(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr("deploy_tools.apptainer.run_command", _no_pull)
