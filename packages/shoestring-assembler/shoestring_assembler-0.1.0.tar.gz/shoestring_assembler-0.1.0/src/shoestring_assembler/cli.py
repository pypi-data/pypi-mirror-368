"""Console script for shoestring_assembler."""

import shoestring_assembler
from shoestring_assembler.model.recipe import Recipe
from shoestring_assembler.display import Display
from shoestring_assembler.interface.signals import Action

import typer
from typing_extensions import Annotated
import os
import sys
import asyncio

typer_app = typer.Typer(name="Shoestring Assembler", no_args_is_help=True)


@typer_app.command()
def check_recipe(
    recipe_location: Annotated[
        str, typer.Argument(help="Path to recipe file")
    ] = "./recipe.toml",
):
    Display.print_top_header("Checking Recipe")
    Recipe.load(recipe_location)
    Display.print_top_header("Finished")


@typer_app.command()
def download(
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Show extra logs.")
    ] = False,
):
    """
    Downloads the specified solution
    """
    execute(Action.DOWNLOAD,verbose=verbose)


@typer_app.command()
def update(
    version: Annotated[
        str, typer.Argument(help="Update to this version. (optional)")
    ] = "",
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Show extra logs.")
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes", "-y", help="Automatically download and assemble the latest version"
        ),
    ] = False,
    recipe_location: Annotated[
        str, typer.Argument(help="Path to recipe file")
    ] = "./recipe.toml",
):
    """
    Updates the solution to the specified version. If a version is not specified - it lists the available versions that you can choose from.
    """
    execute(Action.UPDATE,version=version,no_prompt=yes,recipe_location=recipe_location,verbose=verbose)


@typer_app.command()
def assemble(
    recipe_location: Annotated[
        str, typer.Argument(help="Path to recipe file")
    ] = "./recipe.toml",
    download: bool = True,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Show extra logs.")
    ] = False,
):
    """
    Assembles the solution using the provided recipe
    """
    execute(Action.ASSEMBLE, recipe_location=recipe_location, verbose=verbose,download=download)


@typer_app.command()
def reconfigure(
    recipe_location: Annotated[
        str, typer.Argument(help="Path to recipe file")
    ] = "./recipe.toml",
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Show extra logs.")
    ] = False,
):
    execute(Action.RECONFIGURE, recipe_location=recipe_location, verbose=verbose)


@typer_app.command()
def build():
    execute(Action.BUILD)


@typer_app.command()
def setup():
    execute(Action.SETUP)


@typer_app.command()
def start():
    execute(Action.START)


@typer_app.command()
def stop():
    execute(Action.STOP)


@typer_app.command()
def restart():
    execute(Action.RESTART)

@typer_app.command()
def app():
    from shoestring_assembler.view.cli_app import SolutionAssemblerApp
    app = SolutionAssemblerApp()
    app.run()

@typer_app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool, typer.Option("--version", "-v", help="Assembler version")
    ] = False,
):
    if version:
        Display.print_log(
            f"Shoestring Assembler version {shoestring_assembler.__version__}"
        )
    else:
        pass #todo


from .engine.engine import Engine
from shoestring_assembler.view.plain_cli import PlainCLI


def execute(action,*,recipe_location=None,verbose=False,**kwargs):
    if verbose:
        Display.log_level = 5

    ui = PlainCLI(action)
    loop = asyncio.get_event_loop()
    ui_task = loop.create_task(ui.run())
    try:
        loop.run_until_complete(ui_task)
    except asyncio.CancelledError:
        Display.print_error("Closing")
    
def app():
    try:
        if os.geteuid() == 0:
            Display.print_error(
                "To try prevent you from accidentally breaking things, this program won't run with sudo or as root! \nRun it again without sudo or change to a non-root user."
            )
            sys.exit(255)
        typer_app()
    finally:
        Display.finalise_log()


if __name__ == "__main__":
    app()
