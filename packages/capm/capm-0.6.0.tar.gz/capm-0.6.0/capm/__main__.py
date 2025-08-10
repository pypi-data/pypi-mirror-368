import os
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from typer import Context
from typer.core import TyperGroup

from capm.config import load_config_from_file, save_config_to_file
from capm.entities.PackageConfig import PackageConfig
from capm.package import run_package, load_packages
from capm.utils.utils import fail, succeed
from capm.version import version

CONFIG_FILE = Path('.capm.yml')


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        return list(self.commands)


cli = typer.Typer(cls=OrderCommands, no_args_is_help=True, add_completion=False)


@cli.command(help="Run code analysis")
def run():
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} does not exist.")
        sys.exit(1)
    packages = load_packages()
    config = load_config_from_file(CONFIG_FILE)
    for package_config in config.packages:
        package = packages[package_config.id]
        exit_code = run_package(package, package_config)
        if exit_code != 0:
            sys.exit(exit_code)


@cli.command(help="Add a package")
def add(package: Annotated[str, typer.Argument(help="Package name")]):
    packages = load_packages()
    if package not in packages:
        fail(f"Package '{package}' not found.")
        sys.exit(1)
    config = load_config_from_file(CONFIG_FILE)
    for p in config.packages:
        if p.id == package:
            fail(f"Package '{package}' is already added.")
            sys.exit(1)
    config.packages.append(PackageConfig(package))
    save_config_to_file(config, CONFIG_FILE)
    succeed(f'Package \'{package}\' added successfully.')


@cli.command(help="Remove a package")
def remove(package: Annotated[str, typer.Argument(help="Package name")]):
    config = load_config_from_file(CONFIG_FILE)
    config.packages = [p for p in config.packages if p.id != package]
    save_config_to_file(config, CONFIG_FILE)
    succeed(f'Package \'{package}\' removed successfully.')


@cli.command(name="list", help="List packages")
def list_packages():
    config = load_config_from_file(CONFIG_FILE)
    if not config.packages:
        print("No packages found.")
        return
    for package in config.packages:
        print(f"{package.id}")


def _version_callback(show: bool):
    if show:
        print(f"CAPM version: {version}")
        raise typer.Exit()


@cli.callback()
def main(
        version: Annotated[
            Optional[bool],
            typer.Option(
                "--version", "-V", help="Show version", callback=_version_callback
            ),
        ] = None,
):
    """CAPM: Code Analysis Package Manager"""

    if version:
        raise typer.Exit()


if __name__ == "__main__":
    cli()
