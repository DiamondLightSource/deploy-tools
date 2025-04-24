import subprocess
import sys
import tempfile
from pathlib import Path

from conftest import run_cli
from deploy_tools import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "deploy_tools", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


def test_schema(schemas: Path):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Generate up to date schema files
        run_cli("schema", tmp_path)
        # Compare with the expected schema files
        for schema in tmp_path.glob("*.json"):
            expected = schemas / schema.name
            if schema.read_text() != expected.read_text():
                raise AssertionError(f"Schema file {expected} is out of date.")
