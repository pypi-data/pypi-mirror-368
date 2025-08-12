import importlib
import logging
from nytid.cli import package_contents
import typer

cli = typer.Typer(
    name="utils",
    help="Various utilities",
)

modules = package_contents(__name__)
for module_name in modules:
    try:
        module = importlib.import_module(module_name)
        cli.add_typer(module.cli)
    except Exception as err:
        logging.warning(f"Trying to add {module_name} yields: {err}")
        continue

if __name__ == "__main__":
    cli()
