"""Console script for shoestring_assembler."""

import shoestring_setup as shoestring_setup_top
from shoestring_setup import display, shoestring_setup

import os
import sys
import typer
from typing_extensions import Annotated


typer_app = typer.Typer(name="Shoestring Setup Utility", no_args_is_help=True)


@typer_app.command()
def main(
    update: Annotated[
        bool, typer.Option("--update", help="Attempt to update all dependencies")
    ] = False,
    force: Annotated[
        bool, typer.Option("--force", help="Ignore existing versions and perform install")
    ] = False,
    version: Annotated[
        bool, typer.Option("--version", "-v", help="Setup Utility version")
    ] = False,
):
    if version:
        display.print_log(
            f"Shoestring Setup Utility version {shoestring_setup_top.__version__}"
        )
    else:
        display.print_top_header("Installing Dependencies")
        shoestring_setup.install(update, force)
        display.print_top_header("Finished")


def app():
    if os.geteuid() == 0:
        typer_app()
    else:
        display.print_error(
            "This program needs to be run with sudo or as root so that it can write to files in [white]/etc[/white] and make calls to [white]apt-get[/white]! \nPlease run it again with sudo."
        )
        sys.exit(255)


if __name__ == "__main__":
    app()


"""
* shoestring
    * assemble
    * update
    * check-recipe
    * install_docker
    * check_docker
    * bootstrap (maybe for a separate developer focussed tool?)
"""
