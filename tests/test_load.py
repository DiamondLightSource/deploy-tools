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
