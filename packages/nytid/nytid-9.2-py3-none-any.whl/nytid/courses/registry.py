"""The nytid course registry"""

import typerconf

import pathlib
from nytid import storage

REGISTERS = "registers"


def add(name: str, register_path: pathlib.Path, config: typerconf.Config = typerconf):
    """
    Adds a course register.

    - `name` is the name to refer to this course register
    - `register_path` is the actual path to the directory

    The default `config` is the default config of the `typerconf` package.
    """
    if "." in name:
        raise ValueError(f"`{name}` can't contain a period due to config addressing")
    config.set(f"{REGISTERS}.{name}", str(register_path))


def ls(config: typerconf.Config = typerconf):
    """
    Lists course registers added to configuration `config`. Returns a list of all
    register names.

    The default `config` is the default config of the `typerconf` package.
    """
    try:
        return list(config.get(REGISTERS).keys())
    except KeyError:
        return []


def get(name: str, config: typerconf.Config = typerconf) -> pathlib.Path:
    """
    Returns the path of the course register named by `name`.

    The default `config` is the default config of the `typerconf` package.
    """
    try:
        return pathlib.Path(config.get(REGISTERS)[name])
    except KeyError as err:
        raise KeyError(f"Can't find register named `{name}`: {err}")


def remove(name, config: typerconf.Config = typerconf):
    """
    Removes a course register.

    - `name` is the name of the course register entry


    The default `config` is the default config of the `typerconf` package.
    """
    if "." in name:
        raise ValueError(f"`{name}` can't contain a period due to config addressing")
    current_dirs = config.get(REGISTERS)
    try:
        del current_dirs[name]
    except KeyError:
        raise KeyError(f"There is no such register: {name}")
    else:
        config.set(REGISTERS, current_dirs)
