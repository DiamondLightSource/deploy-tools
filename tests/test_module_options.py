"""Tests for Module/app options that drive otherwise-untested template branches.

These CLI-driven ``sync`` tests build a config from typed models, set each option to a
representative value, and assert the rendered output.
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
from deploy_tools.models.module import EnvVar, Module, ModuleDependency, Release
from deploy_tools.models.save_and_load import (
    DEPLOYMENT_SETTINGS,
    YAML_FILE_SUFFIX,
    save_as_yaml,
)
from deploy_tools.models.shell_app import ShellApp


def _sync(tmp_path: Path, *releases: Release) -> Path:
    """Serialise a config of the given releases under ``tmp_path`` and ``sync`` it.

    Args:
        tmp_path: The per-test scratch directory.
        releases: The Releases to deploy from scratch.

    Returns:
        The deployment root the modules were synced into.
    """
    config_folder = tmp_path / "config"
    save_as_yaml(DeploymentSettings(), config_folder / DEPLOYMENT_SETTINGS, True)
    for release in releases:
        module = release.module
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


def test_dependencies_render_module_load_lines(tmp_path: Path) -> None:
    # The modulefile dependency block branches on whether a version is given: a pinned
    # dependency renders `name/version`, while a version-less one renders the bare name.
    pinned = Release(
        module=Module(
            name="example-pinned-dep",
            version="1.0",
            description="Managed module referenced with a pinned version",
            applications=[],
        )
    )
    default = Release(
        module=Module(
            name="example-default-dep",
            version="1.0",
            description="Managed module referenced without a version",
            applications=[],
        )
    )
    dependent = Release(
        module=Module(
            name="example-dependent",
            version="1.0",
            description="Module with a pinned and a version-less managed dependency",
            dependencies=[
                ModuleDependency(name="example-pinned-dep", version="1.0"),
                ModuleDependency(name="example-default-dep"),
            ],
            applications=[],
        )
    )
    deployment_root = _sync(tmp_path, pinned, default, dependent)

    modulefile = (
        deployment_root / "modules/example-dependent/1.0/modulefile"
    ).read_text()

    # Pinned dependency renders with its version; the version-less one renders the bare
    # module name (and loads the default).
    assert "module load example-pinned-dep/1.0" in modulefile
    assert "module load example-default-dep\n" in modulefile


def test_env_vars_render_setenv(tmp_path: Path) -> None:
    # env_vars render as setenv lines in the modulefile; assert one is emitted.
    release = Release(
        module=Module(
            name="example-env-vars",
            version="1.0",
            description="Module exercising environment variable rendering",
            env_vars=[EnvVar(name="EXAMPLE_VAR", value="example-value")],
            applications=[],
        )
    )
    deployment_root = _sync(tmp_path, release)

    modulefile = (
        deployment_root / "modules/example-env-vars/1.0/modulefile"
    ).read_text()

    assert 'setenv EXAMPLE_VAR "example-value"' in modulefile
