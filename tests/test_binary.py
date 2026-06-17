import hashlib
from pathlib import Path

import pytest
import yaml

from conftest import run_cli
from deploy_tools.app_builder import AppBuilderError

# A small payload served as a local file:// "download" source, so the binary builder's
# real urlretrieve and hashing run with no network access.
BINARY_CONTENT = b"#!/bin/sh\necho 'hello from a binary module'\n"

DIGESTS = {
    "sha256": hashlib.sha256(BINARY_CONTENT).hexdigest(),
    "sha512": hashlib.sha512(BINARY_CONTENT).hexdigest(),
    "md5": hashlib.md5(BINARY_CONTENT).hexdigest(),
}


def _write_binary_deployment(
    tmp_path: Path, hash_type: str, hash_value: str
) -> tuple[Path, Path]:
    """Build a deployment root and a single binary-module config under ``tmp_path``.

    Binary modules download from a URL and verify a hash, so the config must reference a
    real file whose digest is known at test time. A committed config cannot carry such a
    machine-specific ``file://`` path, so it is generated per test.

    Args:
        tmp_path: The per-test scratch directory.
        hash_type: The ``hash_type`` to record in the config.
        hash_value: The hash to record in the config.

    Returns:
        The ``(deployment_root, config_folder)`` pair to pass to ``sync``.
    """
    source = tmp_path / "downloads" / "example-tool"
    source.parent.mkdir()
    source.write_bytes(BINARY_CONTENT)

    config_folder = tmp_path / "config"
    module_dir = config_folder / "example-binary"
    module_dir.mkdir(parents=True)
    (config_folder / "settings.yaml").write_text("default_versions: {}\n")

    release = {
        "module": {
            "name": "example-binary",
            "version": "1.0",
            "description": "Single binary module for builder coverage",
            "applications": [
                {
                    "app_type": "binary",
                    "name": "example-tool",
                    "url": source.as_uri(),
                    "hash": hash_value,
                    "hash_type": hash_type,
                }
            ],
        }
    }
    (module_dir / "1.0.yaml").write_text(yaml.safe_dump(release))

    deployment_root = tmp_path / "deployment"
    deployment_root.mkdir()
    return deployment_root, config_folder


@pytest.mark.parametrize("hash_type", ["sha256", "sha512", "md5"])
def test_sync_builds_binary_with_hash_check(tmp_path: Path, hash_type: str) -> None:
    # Each supported algorithm should validate the download and deploy an executable
    # binary entrypoint with the original contents.
    deployment_root, config_folder = _write_binary_deployment(
        tmp_path, hash_type, DIGESTS[hash_type]
    )
    run_cli("sync", "--from-scratch", deployment_root, config_folder)

    binary = deployment_root / "modules/example-binary/1.0/entrypoints/example-tool"
    assert binary.read_bytes() == BINARY_CONTENT
    assert binary.stat().st_mode & 0o111, "deployed binary is not executable"


def test_sync_builds_binary_without_hash_check(tmp_path: Path) -> None:
    # hash_type "none" skips verification; the binary is still downloaded and deployed.
    deployment_root, config_folder = _write_binary_deployment(tmp_path, "none", "")
    run_cli("sync", "--from-scratch", deployment_root, config_folder)

    binary = deployment_root / "modules/example-binary/1.0/entrypoints/example-tool"
    assert binary.read_bytes() == BINARY_CONTENT


def test_sync_rejects_binary_with_wrong_hash(tmp_path: Path) -> None:
    # A digest that does not match the download must fail the build rather than deploy
    # an unverified binary.
    deployment_root, config_folder = _write_binary_deployment(
        tmp_path, "sha256", "0" * 64
    )
    with pytest.raises(AppBuilderError, match="hash check failed"):
        run_cli("sync", "--from-scratch", deployment_root, config_folder)
