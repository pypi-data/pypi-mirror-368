"""The nytid courses command and subcommands"""

import typerconf

from nytid import courses
import logging
import os
import pathlib
from nytid.courses import registry
import re
from nytid import storage
import subprocess
import sys
import typer
import typing
from typing_extensions import Annotated

import os
import subprocess

MINE = "mine"

cli = typer.Typer(name="courses", help="Manage courses")


def complete_register_arg(incomplete):
    """
    Returns all matching register names that can complete `incomplete`.
    """
    return filter(lambda x: x.startswith(incomplete), registry.ls())


def complete_register(ctx, param, incomplete: str):
    """
    Returns list of matching register names available.
    """
    return filter(lambda x: x.startswith(incomplete), registry.ls())


def complete_course_name(ctx: typer.Context, incomplete: str):
    """
    Returns a list of course names matching `incomplete`.
    """
    registers = register_pairs(ctx.params.get("register"))
    for register, register_path in registers:
        courses_in_reg = courses.all_courses(register_path)
        matching_courses = filter(lambda x: x.startswith(incomplete), courses_in_reg)
        return map(lambda x: (x, f"from {register}"), matching_courses)


def register_pairs(register=None):
    """
    Returns a list of (name, path)-tuples (pairs) for registers to use.

    If `register` is None, we use all existing registers found
    in the config. Otherwise, we look up the path of the one specified and return
    a list containing only that name--path-tuple.
    """
    if register:
        return [(register, registry.get(register))]
    else:
        return [(register, registry.get(register)) for register in registry.ls()]


def complete_config_path(ctx: typer.Context, incomplete: str):
    """
    Returns all valid paths in the config starting with `incomplete`.
    """
    register = ctx.params.get("register")
    course = ctx.params.get("course")
    try:
        conf = courses.get_course_config(course, register)
    except:
        return []

    return filter(lambda x: x.startswith(incomplete), conf.paths())


def print_config(conf: typerconf.Config, path: str = ""):
    """
    Prints the config tree contained in `conf` to stdout.
    Optional `path` is prepended.
    """
    try:
        for key in conf.keys():
            if path:
                print_config(conf[key], f"{path}.{key}")
            else:
                print_config(conf[key], key)
    except AttributeError:
        print(f"{path} = {conf}")


def complete_my_course_arg(incomplete: str) -> typing.List[str]:
    """
    Returns a list of courses in my courses that match `incomplete`.
    """
    mine_path = registry.get(MINE)
    for course in courses.all_courses(mine_path):
        if course.startswith(incomplete):
            yield course


def registers_regex(regex: str) -> typing.List[str]:
    """
    Returns a list of registers matching the `regex`.

    Matching is done `re.match`.
    """
    pattern = re.compile(regex)

    registers = registry.ls()
    for register in registers:
        if pattern.match(register):
            yield register


def courses_regex(
    regex: str, registers: typing.List[str] = None
) -> typing.List[typing.Tuple[str, str]]:
    """
    Returns a list of course--register pairs matching the `regex`.

    Matching is done `re.match`.
    """
    pattern = re.compile(regex)

    if not registers:
        registers = registry.ls()

    for register in registers:
        the_courses = courses.all_courses(registry.get(register))
        for course in the_courses:
            if pattern.match(course):
                yield (course, register)


def complete_course_regex(ctx: typer.Context, regex: str) -> typing.List[str]:
    """ """
    register_regex = ctx.params.get("register")
    registers = registers_regex(register_regex)

    return courses_regex(regex, registers)


new_register_arg = typer.Argument(help="A name to refer to the register.")
register_path_arg = typer.Argument(
    help="The absolute path to the register " "directory."
)
register_arg = typer.Argument(
    help="The name of the register.", autocompletion=complete_register_arg
)
alias_opt = typer.Option(help="Alias to use instead of " "the original course name")
my_course_arg = typer.Argument(
    help="The course in my courses.", autocompletion=complete_my_course_arg
)
register_opt_regex = typer.Option(
    help="Regex for register names to use.", shell_complete=registers_regex
)
course_arg_regex = typer.Argument(
    help="Regex matching courses.", autocompletion=complete_course_regex
)
registrycli = typer.Typer(name="registry", help="Manage course registers")

cli.add_typer(registrycli)


@registrycli.command(name="ls")
def registry_ls():
    """
    Lists registers added to the configuration.
    """
    for register in registry.ls():
        print(f"{register}\t{registry.get(register)}")


@registrycli.command(name="add")
def registry_add(
    name: Annotated[str, new_register_arg],
    register_path: Annotated[pathlib.Path, register_path_arg],
):
    """
    Adds a register to the configuration.
    """
    try:
        registry.add(name, register_path)
    except KeyError as err:
        logging.error(f"Can't add {name}: {err}")
        sys.exit(1)


@registrycli.command(name="rm")
def registry_rm(name: Annotated[str, register_arg]):
    """
    Removes a register from the configuration.
    """
    try:
        registry.remove(name)
    except KeyError as err:
        logging.error(f"Can't remove {name}: {err}")
        sys.exit(1)


course_arg = typer.Argument(help="A name used to refer to the course.")
register_option = typer.Option(
    help="Name of register to use. "
    "Must be used if there are more than "
    "one register in the config.",
    shell_complete=complete_register,
)
contact_opt = typer.Option(
    help="The course responsible's contact info. "
    "Default can be set using "
    "`nytid config me.name --set 'First Last'"
    " and "
    "`nytid config me.email --set x@y.z."
)
code_opt = typer.Option(
    help="The course code, " "to relate it to similar courses using " "`related`."
)
related_opt = typer.Option(
    help="List of related course codes, "
    "courses with any of these codes can "
    "share TAs."
)
ics_opt = typer.Option(
    help="A URL to an ICS file containing the "
    "schedule. E.g. an export/subscription from "
    "TimeEdit."
)
data_path_opt = typer.Option(
    help="Path to the course's data directory, "
    "default is to append `/data` to the "
    "course's config directory."
)
num_students_opt = typer.Option(help="The total number of students " "in the course.")
num_groups_opt = typer.Option(
    help="The number of groups that the class " "will be divided into."
)


@cli.command()
def new(
    name: Annotated[str, course_arg],
    register: Annotated[str, register_option] = MINE,
    contact: Annotated[str, contact_opt] = None,
    code: Annotated[str, code_opt] = None,
    related: Annotated[typing.List[str], related_opt] = [],
    ics: Annotated[str, ics_opt] = None,
    data_path: Annotated[pathlib.Path, data_path_opt] = None,
    num_students: Annotated[int, num_students_opt] = None,
    num_groups: Annotated[int, num_groups_opt] = None,
):
    """
    Creates a new course.
    """
    kwdata = {
        "contact": contact,
        "code": code,
        "related_codes": related,
        "ics": ics,
        "data_path": data_path,
        "num_students": num_students,
        "num_groups": num_groups,
    }
    courses.new(name, register, kwdata)


course_arg_autocomplete = typer.Argument(
    help="Name (nickname) of the target " "course.", autocompletion=complete_course_name
)
path_arg = typer.Argument(
    help="Path in config, e.g. 'courses.datintro22'. "
    "Empty string is root of config. Defaults to "
    "the empty string.",
    autocompletion=complete_config_path,
)
value_arg = typer.Option(
    "-s",
    "--set",
    help="Values to store. "
    "More than one value makes a list. "
    "Values are treated as JSON if possible.",
)


@cli.command(name="config")
def config_cmd(
    course: Annotated[str, course_arg_autocomplete],
    register: Annotated[str, register_option] = MINE,
    path: Annotated[str, path_arg] = "",
    values: Annotated[typing.List[str], value_arg] = None,
):
    """
    Reads values from or writes `values` to the config of `course` at `path`.
    """
    try:
        conf = courses.get_course_config(course, register)
    except KeyError as err:
        logging.error(err)
        sys.exit(1)
    except PermissionError as err:
        logging.error(f"You don't have access to {course} in {register}: {err}")
        sys.exit(1)
    if values:
        if len(values) == 1:
            values = values[0]
        if values == "":
            values = None
        conf.set(path, values)
    else:
        try:
            print_config(conf.get(path), path)
        except KeyError as err:
            logging.error(f"{path} doesn't exist in the config: {err}")
            sys.exit(1)


@cli.command()
def ls(register: Annotated[str, register_option] = MINE):
    """
    Lists all available courses in all registers in the registry. Output format:

      register<tab>course

    If `register` (a register name) is provided, only courses from that register
    are listed.
    """
    if register:
        try:
            for course in courses.all_courses(registry.get(register)):
                print(f"{register}\t{course}")
        except KeyError as err:
            logging.error(err)
            sys.exit(1)
    else:
        for register in registry.ls():
            for course in courses.all_courses(registry.get(register)):
                print(f"{register}\t{course}")


datacli = typer.Typer(name="data", help="Access the raw course data")

cli.add_typer(datacli)


@datacli.command()
def shell(
    course: Annotated[str, course_arg_autocomplete],
    register: Annotated[str, register_arg] = MINE,
):
    """
    Spawns a shell in the data directory of a course.
    """
    try:
        data_dir = courses.get_course_data(course, register)
    except KeyError as err:
        logging.error(err)
        sys.exit(1)
    except PermissionError as err:
        logging.error(f"You don't have access to {course} in {register}: {err}")
        sys.exit(1)
    try:
        print(f"--- {course}/data shell ---")
        env = os.environ.copy()
        if "PS1" in env:
            env["PS1"] = f"{course}/data {env['PS1']}"
        else:
            env["PS1"] = f"{course}/data \w\n$ "

        subprocess.run(
            [os.environ["SHELL"]],
            cwd=data_dir.path,
            env=env,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except FileNotFoundError as err:
        logging.warning(f"The data directory doesn't exist: {err}")
        try:
            os.makedirs(data_dir.path)
            logging.warning(f"Created {data_dir.path}")
            env = os.environ.copy()
            if "PS1" in env:
                env["PS1"] = f"{course}/data {env['PS1']}"
            else:
                env["PS1"] = f"{course}/data \w\n$ "

            subprocess.run(
                [os.environ["SHELL"]],
                cwd=data_dir.path,
                env=env,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        except Exception as err:
            logging.error(f"Can't create directory: {err}")
            sys.exit(1)
    except KeyError as err:
        logging.error(err)
        sys.exit(1)
    except PermissionError as err:
        logging.error(f"You don't have access to {course} in {register}: {err}")
        sys.exit(1)
    finally:
        print(f"--- {course}/data shell terminated ---")


minecli = typer.Typer(name=MINE, help="Manage my courses")

cli.add_typer(minecli)


@minecli.command(name="add")
def mine_add(
    course: Annotated[str, course_arg_autocomplete],
    register: Annotated[str, register_arg] = None,
    alias: Annotated[str, alias_opt] = None,
):
    """
    Adds a course to my courses.
    """
    if not register:
        register_map = {register: registry.get(register) for register in registry.ls()}

        matching_registers = []
        for register, register_path in register_map.items():
            matching_courses = filter(
                lambda x: x == course, courses.all_courses(register_path)
            )
            if len(list(matching_courses)) > 0:
                matching_registers.append(register)

        num_matches = len(matching_registers)
        if num_matches == 1:
            register = matching_registers[0]
        elif num_matches < 1:
            logging.error(f"Can't find course {course} in any register")
            sys.exit(1)
        elif num_matches > 1:
            logging.error(
                f"Too many matches for {course}, "
                f"specify one of the registers {matching_registers}."
            )
            sys.exit(1)

    if not alias:
        alias = course

    try:
        mine_path = registry.get(MINE)
    except KeyError:
        home_path = pathlib.Path(os.environ["HOME"])
        registry.add(MINE, home_path / ".nytid/mine")
        mine_path = registry.get(MINE)
        os.makedirs(mine_path)
        logging.warning(f"Added register {MINE} and created its path {mine_path}.")
        mine_path = registry.get(MINE)
    for my_course in mine_path.iterdir():
        if my_course == alias:
            logging.error(f"{alias} is already among your courses.")
            sys.exit(1)

    course_path = registry.get(register) / course
    try:
        os.symlink(course_path, mine_path / alias)
    except FileExistsError:
        logging.error(f"{alias} is already in {MINE}")
        sys.exit(1)


@minecli.command(name="ls")
def mine_ls():
    """
    Lists my courses.
    """
    mine_path = registry.get(MINE)
    for course in mine_path.iterdir():
        print(course.name)


@minecli.command(name="rm")
def mine_rm(course: Annotated[str, my_course_arg]):
    """
    Removes a course from my courses.
    """
    mine_path = registry.get(MINE)
    try:
        os.unlink(mine_path / course)
    except FileNotFoundError as err:
        logging.error(f"Couldn't find {course}: {err}")
        sys.exit(1)
    except IsADirectoryError as err:
        logging.error(
            f"{course} is a directory, not a symlink: "
            f"We can't remove the directory without permanent data loss; "
            f"this seems to be actual course data, not just a link to it! "
            f"So you'll have to remove it manually to proceed. "
            f"The directory you want to remove is {mine_path / course}."
        )
        sys.exit(1)


if __name__ == "__main__":
    cli()
