"""The CLI of nytid"""

import typer
import importlib
import pathlib
import os
import typerconf

MODULE_EXTENSIONS = importlib.machinery.SOURCE_SUFFIXES

import logging
import sys

logging.basicConfig(format=f"nytid: %(levelname)s: %(message)s")

cli = typer.Typer(
    help="""
                       A CLI for managing TAs and courses.
                       """,
    epilog="Copyright (c) 2022--2025 Daniel Bosk, " "2022 Alexander Baltatzis.",
)


def package_contents(package_name, recurse=False):
    """
    Find all modules in a package. Recurse through subpackages if recurse is True
    (defualt False).
    """
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return set()

    pathname = pathlib.Path(spec.origin).parent

    modules = set()
    with os.scandir(pathname) as entries:
        for entry in entries:
            if entry.name.startswith("__"):
                continue
            current = ".".join((package_name, entry.name.partition(".")[0]))
            if entry.is_file():
                if any(
                    [entry.name.endswith(extension) for extension in MODULE_EXTENSIONS]
                ):
                    modules.add(current)
            elif entry.is_dir():
                modules.add(current)
                if recurse:
                    modules |= package_contents(current, recurse=True)

    return modules


modules = package_contents(__name__)
for module_name in modules:
    try:
        module = importlib.import_module(module_name)
        cli.add_typer(module.cli)
    except Exception as err:
        logging.warning(f"Trying to add {module_name} yields: {err}")
        continue
typerconf.add_config_cmd(cli)

if __name__ == "__main__":
    cli()
