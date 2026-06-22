"""Direct-call unit tests for ``modulefile`` helpers."""

from pathlib import Path

from deploy_tools.layout import Layout
from deploy_tools.modulefile import apply_default_versions


def test_apply_default_versions_removes_default_for_unlisted_module(
    tmp_path: Path,
) -> None:
    # apply_default_versions removes the stale default (.version) file for a deployed
    # module that is absent from the default map. The CLI never reaches this branch
    # because validate_default_versions assigns a default to every deployed module
    # (raising otherwise), so call the function directly to pin its cleanup contract.
    layout = Layout(tmp_path)
    name, version = "example", "1.0"

    # A deployed module: a live modulefile link plus an existing default (.version)
    # file.
    mf_link = layout.get_modulefile_link(name, version)
    mf_link.parent.mkdir(parents=True, exist_ok=True)
    mf_link.touch()
    default_file = layout.get_default_version_file(name)
    default_file.write_text("#%Module1.0\nset ModulesVersion 1.0\n")

    apply_default_versions({}, layout)

    assert not default_file.exists()
