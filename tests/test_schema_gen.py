import tempfile
from pathlib import Path

from conftest import run_cli


def test_schema_gen(schemas: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Generate up to date schema files
        run_cli("schema", tmp_path)

        # Compare with the expected schema files
        for schema in tmp_path.glob("*.json"):
            expected = schemas / schema.name
            if schema.read_text() != expected.read_text():
                raise AssertionError(f"Schema file {expected} is out of date.")
