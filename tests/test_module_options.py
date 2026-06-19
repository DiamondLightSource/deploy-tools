"""Tests for Module/app options that drive otherwise-untested template branches.

These CLI-driven ``sync`` tests build a config from typed models, set each option to a
representative value, and assert the rendered output. They are kept out of the
golden master tests to avoid bloat.
"""

from pathlib import Path

from conftest import run_cli
from deploy_tools.models.apptainer_app import (
    ApptainerApp,
    ContainerImage,
    Entrypoint,
    EntrypointOptions,
)
from deploy_tools.models.deployment import DeploymentSettings
from deploy_tools.models.module import Module, Release
from deploy_tools.models.save_and_load import (
    DEPLOYMENT_SETTINGS,
    YAML_FILE_SUFFIX,
    save_as_yaml,
)
from deploy_tools.models.shell_app import ShellApp


def _sync(tmp_path: Path, release: Release) -> Path:
    """Serialise a single-module config under ``tmp_path`` and ``sync`` it from scratch.

    Args:
        tmp_path: The per-test scratch directory.
        release: The Release to deploy as the sole module.

    Returns:
        The deployment root the module was synced into.
    """
    module = release.module
    config_folder = tmp_path / "config"
    save_as_yaml(DeploymentSettings(), config_folder / DEPLOYMENT_SETTINGS, True)
    save_as_yaml(
        release,
        config_folder / module.name / f"{module.version}{YAML_FILE_SUFFIX}",
        True,
    )

    deployment_root = tmp_path / "deployment"
    deployment_root.mkdir()
    run_cli("sync", "--from-scratch", deployment_root, config_folder)
    return deployment_root


def test_load_and_unload_scripts_render_tcl_blocks(tmp_path: Path) -> None:
    release = Release(
        module=Module(
            name="example-scripted",
            version="1.0",
            description="Module exercising load/unload script hooks",
            load_script=["set example_loaded 1"],
            unload_script=["unset example_loaded"],
            applications=[
                ShellApp(app_type="shell", name="example-cmd", script=["echo hello"])
            ],
        )
    )
    deployment_root = _sync(tmp_path, release)

    modulefile = (
        deployment_root / "modules/example-scripted/1.0/modulefile"
    ).read_text()

    # The unload-mode guard is produced only by the unload_script branch, so its
    # presence confirms that branch rendered; the script lines confirm both blocks
    # carry content.
    assert "if { [module-info mode unload] } {" in modulefile
    assert "set example_loaded 1" in modulefile
    assert "unset example_loaded" in modulefile


def test_apptainer_options_merge_global_and_entrypoint(
    tmp_path: Path, stub_apptainer_pull: None
) -> None:
    # The Apptainer entrypoint combines global_options with per-entrypoint options
    release = Release(
        module=Module(
            name="example-apptainer-opts",
            version="1.0",
            description="Module exercising apptainer entrypoint option merge",
            applications=[
                ApptainerApp(
                    app_type="apptainer",
                    container=ContainerImage(
                        path="docker://ghcr.io/apptainer/lolcow",  # type: ignore[arg-type]
                        version="latest",
                    ),
                    global_options=EntrypointOptions(
                        mounts=["/global/mount"],
                        host_binaries=["globalbin"],
                        apptainer_args="--global-arg",
                        command_args="--global-cmd",
                    ),
                    entrypoints=[
                        Entrypoint(
                            name="example-cmd",
                            command="realcmd",
                            options=EntrypointOptions(
                                mounts=["/local/mount"],
                                host_binaries=["localbin"],
                                apptainer_args="--local-arg",
                                command_args="--local-cmd",
                            ),
                        )
                    ],
                )
            ],
        )
    )
    deployment_root = _sync(tmp_path, release)

    entrypoint = (
        deployment_root / "modules/example-apptainer-opts/1.0/entrypoints/example-cmd"
    ).read_text()

    # Global and per-entrypoint values are concatenated, global first: comma-joined for
    # mounts, space-joined for host_binaries and the arg strings.
    assert 'mounts="/global/mount,/local/mount"' in entrypoint
    assert 'apptainer_args="--global-arg --local-arg"' in entrypoint
    assert 'command_args="--global-cmd --local-cmd"' in entrypoint
    assert "for i in globalbin localbin; do" in entrypoint
    assert 'command="realcmd"' in entrypoint
