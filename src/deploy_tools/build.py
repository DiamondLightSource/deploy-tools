import shutil

from .layout import Layout
from .models.changes import DeploymentChanges
from .models.module import Release
from .module_builder import ModuleBuilder
from .templater import Templater


def clean_build_area(layout: Layout) -> None:
    build_path = layout.build_layout.build_root

    if build_path.exists():
        shutil.rmtree(build_path)


def build(changes: DeploymentChanges, layout: Layout) -> None:
    """Build all modules that are to be added or updated."""
    release_changes = changes.release_changes

    _build_releases(release_changes.to_add, layout)
    _build_releases(release_changes.to_update, layout)


def _build_releases(releases: list[Release], layout: Layout) -> None:
    if not releases:
        return

    templater = Templater()
    module_builder = ModuleBuilder(templater, layout)

    for release in releases:
        module_builder.create_module(release.module)
