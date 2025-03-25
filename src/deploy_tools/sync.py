import logging
from pathlib import Path

from git import Repo

from .build import build, clean_build_area
from .deploy import deploy_changes
from .layout import Layout
from .models.save_and_load import load_deployment
from .snapshot import create_snapshot, load_snapshot
from .templater import Templater, TemplateType
from .validate import (
    validate_deployment_changes,
)

logger = logging.getLogger(__name__)

IGNORE_DIRS = ["/build", "/modules/*/*/sif_files"]


def synchronise(
    deployment_root: Path,
    config_folder: Path,
    allow_all: bool = False,
    from_scratch: bool = False,
) -> None:
    """Synchronise the deployment folder with the current configuration."""
    logger.info("Loading deployment configuration from: %s", config_folder)
    deployment = load_deployment(config_folder)

    logger.info("Loading deployment snapshot")
    layout = Layout(deployment_root)
    snapshot = load_snapshot(layout, from_scratch)

    logger.info("Validating deployment changes")
    deployment_changes = validate_deployment_changes(deployment, snapshot, allow_all)

    logger.info("Cleaning build area")
    clean_build_area(layout)
    logger.info("Building modules")
    build(deployment_changes, layout)

    repo: Repo
    if from_scratch:
        logger.info("Creating git repository in deployment area")
        repo = _initialise_git_repo(layout.deployment_root, IGNORE_DIRS)
    else:
        repo = Repo(layout.deployment_root)

    logger.info("Creating snapshot")
    create_snapshot(deployment, layout)

    logger.info("Deploying changes")
    deploy_changes(deployment_changes, layout)

    logger.info("Committing changes to git (for reference)")
    repo.git.add("--all")
    commit = repo.index.commit("Performed sync process")

    logger.info("Commit SHA: %s", commit.hexsha)


def _initialise_git_repo(path: Path, ignore_dirs: list[str]) -> Repo:
    repo = Repo.init(path, mkdir=False, initial_branch="main")
    t = Templater()
    params = {"ignore_dirs": ignore_dirs}
    t.create(path / ".gitignore", TemplateType.GITIGNORE, params)

    repo.git.add("--all")
    repo.index.commit("Initial commit")

    return repo
