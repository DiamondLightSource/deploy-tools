import re
from collections import defaultdict

from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .templater import Templater, TemplateType

type ModuleVersionsByName = dict[str, list[str]]

VERSION_GLOB = f"*/[!{Layout.DEFAULT_VERSION_FILENAME}]*"

DEFAULT_VERSION_REGEX = "^set ModulesVersion (.*)$"


def deprecate_modulefile_link(name: str, version: str, layout: Layout) -> None:
    mf_link = layout.get_modulefile_link(name, version)
    deprecated_mf_link = layout.get_modulefile_link(name, version, from_deprecated=True)

    deprecated_mf_link.parent.mkdir(parents=True, exist_ok=True)
    mf_link.rename(deprecated_mf_link)


def restore_modulefile_link(name: str, version: str, layout: Layout) -> None:
    mf_link = layout.get_modulefile_link(name, version)
    deprecated_mf_link = layout.get_modulefile_link(name, version, from_deprecated=True)

    mf_link.parent.mkdir(parents=True, exist_ok=True)
    deprecated_mf_link.rename(mf_link)


def get_default_modulefile_version(name: str, layout: Layout) -> str | None:
    version_regex = re.compile(DEFAULT_VERSION_REGEX)
    default_version_file = layout.get_default_version_file(name)

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
        default_version_file = layout.get_default_version_file(name)

        if name in default_versions:
            params = {"version": default_versions[name]}

            templater.create(
                default_version_file,
                TemplateType.MODULEFILE_VERSION,
                params,
                overwrite=True,
            )
        else:
            default_version_file.unlink(missing_ok=True)


def get_deployed_modulefile_versions(
    layout: Layout, from_deprecated: bool = False
) -> ModuleVersionsByName:
    """Return list of modulefiles that have been deployed."""
    modulefiles_root = layout.get_modulefiles_root(from_deprecated)
    found_modules: ModuleVersionsByName = defaultdict(list)

    for version_path in modulefiles_root.glob(VERSION_GLOB):
        found_modules[version_path.parent.name].append(version_path.name)

    return found_modules
