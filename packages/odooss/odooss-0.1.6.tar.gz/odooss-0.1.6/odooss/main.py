import logging

from .folder_structure import (
    create_addons,
    create_docker_compose,
    create_dockerfile,
    create_dockerignore,
    create_gitignore,
    create_readme,
    create_requirement,
    create_ruff,
)
from .precommit import create_precommit_config, install_precommit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_all(path, odoo_version, python):
    """Create the Odoo standard folder structure at PATH."""
    logger.info("Please make sure your virtual environment is activated.")
    create_dockerfile(path, odoo_version=odoo_version, python=python)
    create_dockerignore(path)
    create_docker_compose(path)

    create_gitignore(path)
    create_requirement(path)
    create_ruff(path)
    create_readme(path)
    create_addons(path)
    create_precommit_config(path)
    install_precommit(path)


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    version = 18.0
    python = 3.10
    create_all(path, version, python)
