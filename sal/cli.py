# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_cli.ipynb.

# %% auto 0
__all__ = ['main', 'render']

# %% ../nbs/03_cli.ipynb 4
import click
from pathlib import Path
from typing import Any
from .codegen import Sal
from .utils import is_notebook

# %% ../nbs/03_cli.ipynb 7
# TODO support filters from config file


def _render(file: str, directories: list[Path]) -> str | Any:
    sal = Sal.from_config(template_directories=directories)
    return sal.process_xml_from_filename(file)

# %% ../nbs/03_cli.ipynb 10
@click.group()
def main() -> None:
    pass

# %% ../nbs/03_cli.ipynb 11
# TODO : init command
# - create : sal.xml file
# - create : sal folder
# - create : sal/templates folder

# - snapshots


@main.command()
@click.option("--filename", type=click.Path(exists=True), default="./sal.xml")
@click.option("--folder", type=click.Path(exists=True), default="./sal")
def render(filename: str, folder: str) -> None:
    click.echo(f"⚠️ {filename=}")
    click.echo(f"⚠️ {folder=}")
    _render(filename, [Path(folder) / "templates"])


# TODO snapshot
# TODO check.snapshot

# %% ../nbs/03_cli.ipynb 12
if __name__ == "__main__" and not is_notebook():
    main()
