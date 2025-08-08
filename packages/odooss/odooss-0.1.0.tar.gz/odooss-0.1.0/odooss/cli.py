import click
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .main import create_all

@click.group()
def cli():
    pass


@cli.command()
@click.argument("path", type=click.Path())
@click.option("--odoo_version", default="18.0", help="Odoo version to use (e.g. 18.0)")
@click.option("--python", default="3.10", help="Python version to use (e.g. 3.10)")
def create(path, odoo_version, python):

    """Create the Odoo standard folder structure at PATH."""
    logger.info(f"Please make sure your virtual environment is activated.")
    create_all(path, odoo_version, python)


if __name__ == "__main__":
    cli()
