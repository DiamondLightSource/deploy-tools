import re
from collections import defaultdict
from pathlib import Path

from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .templater import Templater, TemplateType

type ModuleVersionsByName = dict[str, list[str]]

DEFAULT_VERSION_FILENAME = ".version"
VERSION_GLOB = f"*/[!{DEFAULT_VERSION_FILENAME}]*"

DEFAULT_VERSION_REGEX = "^set ModulesVersion (.*)$"


def deprecate_modulefile(name: str, version: str, layout: Layout) -> None:
    _move_modulefile_link(
        name,
        version,
        layout.modulefiles_root,
        layout.deprecated_modulefiles_root,
    )


def restore_modulefile(name: str, version: str, layout: Layout) -> None:
    _move_modulefile_link(
        name,
        version,
        layout.deprecated_modulefiles_root,
        layout.modulefiles_root,
    )


def _move_modulefile_link(
    name: str, version: str, src_folder: Path, dest_folder: Path
) -> None:
    src_path = src_folder / name / version
    dest_path = dest_folder / name / version

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.rename(dest_path)


def get_deployed_modulefile_versions(
    layout: Layout, from_deprecated: bool = False
) -> ModuleVersionsByName:
    """Return list of modulefiles that have been deployed."""
    modulefiles_root = layout.get_modulefiles_root(from_deprecated)
    found_modules: ModuleVersionsByName = defaultdict(list)

    for version_path in modulefiles_root.glob(VERSION_GLOB):
        found_modules[version_path.parent.name].append(version_path.name)

    return found_modules


def is_modulefile_deployed(
    name: str, version: str, layout: Layout, in_deprecated: bool = False
) -> bool:
    modulefile = layout.get_modulefile_link(
        name, version, from_deprecated=in_deprecated
    )
    return modulefile.exists()


def get_default_modulefile_version(name: str, layout: Layout) -> str | None:
    version_regex = re.compile(DEFAULT_VERSION_REGEX)
    default_version_file = layout.modulefiles_root / name / DEFAULT_VERSION_FILENAME

    with open(default_version_file) as f:
        for line in f.readlines():
            r = version_regex.search(line)
            if r is not None:
                return r.group(1)


def apply_default_versions(
    default_versions: DefaultVersionsByName, layout: Layout
) -> None:
    """Update .version files for current default version settings."""
    templater = Templater()
    deployed_module_versions = get_deployed_modulefile_versions(layout)

    for name in deployed_module_versions:
        version_file = layout.modulefiles_root / name / DEFAULT_VERSION_FILENAME

        if name in default_versions:
            params = {"version": default_versions[name]}

            templater.create(
                version_file,
                TemplateType.MODULEFILE_VERSION,
                params,
                overwrite=True,
            )
        else:
            version_file.unlink(missing_ok=True)
