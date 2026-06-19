from pathlib import Path

import pytest

from conftest import run_cli
from deploy_tools.models.save_and_load import LoadError

# Configs whose on-disk layout is malformed: loading must fail with a clear LoadError
# before any validation logic runs. Each maps a folder under configs/invalid to a
# substring expected in the error.
MALFORMED_CONFIGS = [
    ("stray-file", "Unexpected file in configuration directory"),
    ("name-mismatch", "Module name .* does not match path"),
    ("version-mismatch", "Module version .* does not match path"),
]


@pytest.mark.parametrize("config_name, message", MALFORMED_CONFIGS)
def test_load_rejects_malformed_config_layout(
    tmp_path: Path, configs: Path, config_name: str, message: str
) -> None:
    with pytest.raises(LoadError, match=message):
        run_cli(
            "validate", "--from-scratch", tmp_path, configs / "invalid" / config_name
        )


def test_load_surfaces_invalid_field_in_error(tmp_path: Path, configs: Path) -> None:
    # A config that fails model validation must raise a clean LoadError that names the
    # offending field; the top-level handler hides the traceback, so the field detail is
    # only visible if carried in the message.
    with pytest.raises(LoadError) as exc_info:
        run_cli(
            "validate",
            "--from-scratch",
            tmp_path,
            configs / "invalid" / "invalid-module-name",
        )
    message = str(exc_info.value)
    assert "Module configuration is invalid" in message
    assert "module.name" in message
