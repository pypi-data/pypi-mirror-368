"""This module defines a CLI using Click for version incrementing and
CHANGELOG initialization. The following commands are provided:

  - init: Initialize a fresh CHANGELOG.md file if one does not exist.
  - add: Increment the project's version and update the changelog accordingly.

Typical usage example:

    changelogbump init

The CLI commands automatically handle errors and print
concise messages via Click exceptions.
"""

import os

import click
from click import Command

from changelogbump import header_path, pyproject
from changelogbump.Changelog import Changelog
from changelogbump.Metadata import _PyPiMetadata
from changelogbump.PyProject import PyProject
from changelogbump.Version import Version


class OrderCommands(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        return list(self.commands)


@click.group(cls=OrderCommands)
def cli() -> Command:
    """Click-based CLI for application version incrementing and CHANGELOG management."""
    pass


@cli.command()
def version():
    """Display the current changelogbump version"""
    import importlib.metadata

    pkg_version = Version.from_string(importlib.metadata.version("changelogbump"))
    remote_version = Version.from_string(_PyPiMetadata.version())
    kwargs_a: dict = {"bold": True}
    kwargs_b: dict = {}
    if remote_version == pkg_version:
        kwargs_a["fg"] = "green"
    if remote_version.is_greater_than(pkg_version):
        kwargs_b["fg"] = "red"
    click.echo(click.style(f"Installed: {pkg_version}", **kwargs_a))
    click.echo(click.style(f"Available: {remote_version}", **kwargs_b))


@cli.command()
def init():
    """Initialize a fresh CHANGELOG.md in the project root."""
    if os.path.isfile(Changelog.path):
        raise click.ClickException(
            click.style(f"{Changelog.path} already exists. ", fg="red")
            + click.style("Aborting.", fg="red", bold=True)
        )
    with open(Changelog.path, "w") as changelog:
        with open(header_path, "r") as header:
            changelog.write(header.read())
    click.echo(
        click.style("Changelog initialized: ", fg="green", bold=True)
        + str(Changelog.path.absolute())
    )


@cli.command()
@click.option("--major", "-M", is_flag=True, help="Increment major version number.")
@click.option("--minor", "-m", is_flag=True, help="Increment minor version number.")
@click.option("--patch", "-p", is_flag=True, help="Increment patch version number.")
@click.option(
    "--summary", "-s", is_flag=False, help="Version descriptive summary header."
)
def add(major, minor, patch, summary):
    """Increment version by one of the semantic parts (major|minor|patch)."""
    if sum([major, minor, patch]) > 1:
        raise click.ClickException(
            click.style(
                "Only one of --major, --minor, or --patch is allowed.", fg="red"
            )
        )
    if not any([major, minor, patch]):
        raise click.ClickException(
            click.style("Specify one of --major, --minor, or --patch.", fg="red")
        )

    _version = Version.from_string(pyproject.current_version)
    click.echo("Current version: " + click.style(_version.current, fg="bright_black"))
    _version.bump(major, minor, patch)
    click.echo("Incrementing to: " + click.style(_version.current, fg="blue"))
    Changelog.update(_version.current, summary)
    PyProject.update(_version.current)


if __name__ == "__main__":
    cli()
