import hashlib
import uuid
from itertools import chain
from pathlib import Path
from urllib.request import urlretrieve

from deploy_tools.models.binary_app import BinaryApp, HashType

from .apptainer import create_sif_file
from .layout import ModuleBuildLayout
from .models.apptainer_app import ApptainerApp
from .models.module import Application, Module
from .models.shell_app import ShellApp
from .templater import Templater, TemplateType

ALL_READ_EXECUTE_PERMISSIONS = 0o555


class AppBuilderError(Exception):
    pass


class AppBuilder:
    """Class for creating application entrypoints and associated files."""

    def __init__(self, templater: Templater, build_layout: ModuleBuildLayout) -> None:
        self._templater = templater
        self._build_layout = build_layout

    def create_application_files(self, app: Application, module: Module):
        match app:
            case ApptainerApp():
                self._create_apptainer_files(app, module)
            case ShellApp():
                self._create_shell_file(app, module)
            case BinaryApp():
                self._create_binary_file(app, module)

    def _create_apptainer_files(self, app: ApptainerApp, module: Module) -> None:
        """Create apptainer entrypoints using a specified image and commands."""
        self._generate_sif_file(app, module)
        entrypoints_folder = self._build_layout.get_entrypoints_folder(
            module.name, module.version
        )
        relative_sif_file = self._get_sif_file_path(app, module).relative_to(
            entrypoints_folder, walk_up=True
        )

        global_options = app.global_options
        for entrypoint in app.entrypoints:
            options = entrypoint.options
            entrypoint_file = entrypoints_folder / entrypoint.name

            mounts = ",".join(chain(global_options.mounts, options.mounts)).strip()
            host_binaries = " ".join(
                chain(global_options.host_binaries, options.host_binaries)
            ).strip()

            apptainer_args = f"{global_options.apptainer_args} {options.apptainer_args}"
            apptainer_args = apptainer_args.strip()

            command = entrypoint.command if entrypoint.command else entrypoint.name

            command_args = f"{global_options.command_args} {options.command_args}"
            command_args = command_args.strip()

            params = {
                "mounts": mounts,
                "host_binaries": host_binaries,
                "apptainer_args": apptainer_args,
                "relative_sif_file": relative_sif_file,
                "command": command,
                "command_args": command_args,
            }

            self._templater.create(
                entrypoint_file,
                TemplateType.APPTAINER_ENTRYPOINT,
                params,
                executable=True,
                create_parents=True,
            )

    def _generate_sif_file(self, app: ApptainerApp, module: Module) -> None:
        sif_file_path = self._get_sif_file_path(app, module)
        create_sif_file(sif_file_path, app.container.url, create_parents=True)

    def _get_sif_file_path(self, app: ApptainerApp, module: Module) -> Path:
        sif_folder = self._build_layout.get_sif_files_folder(
            module.name, module.version
        )
        file_name = uuid.uuid3(uuid.NAMESPACE_URL, app.container.url).hex
        return sif_folder / f"{file_name}.sif"

    def _create_shell_file(self, app: ShellApp, module: Module) -> None:
        """Create shell script using Bash for improved functionality."""
        entrypoint_file = (
            self._build_layout.get_entrypoints_folder(module.name, module.version)
            / app.name
        )

        parameters = {"script": app.script}

        self._templater.create(
            entrypoint_file,
            TemplateType.SHELL_ENTRYPOINT,
            parameters,
            executable=True,
            create_parents=True,
        )

    def _create_binary_file(self, app: BinaryApp, module: Module) -> None:
        """
        Download a URL, validate it against its hash, make it executable
        and add it to PATH
        """
        binary_folder = self._build_layout.get_entrypoints_folder(
            module.name, module.version
        )
        binary_path = binary_folder / app.name
        binary_path.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(app.url, binary_path)

        match app.hash_type:
            case HashType.SHA256:
                h = hashlib.sha256()
            case HashType.SHA512:
                h = hashlib.sha512()
            case HashType.MD5:
                h = hashlib.md5()
            case HashType.NONE:
                h = None

        if h is not None:
            with open(binary_path, "rb") as fh:
                while True:
                    data = fh.read(4096)
                    if len(data) == 0:
                        break
                    h.update(data)
            if h.hexdigest() != app.hash:
                raise AppBuilderError(f"Downloaded Binary {app.url} hash check failed")

        binary_path.chmod(ALL_READ_EXECUTE_PERMISSIONS)
