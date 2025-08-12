import datetime
from enum import Enum
import ics.icalendar
import logging
import pathlib
import sys
import typer
from typing_extensions import Annotated

from nytid.cli import courses as coursescli
from nytid import courses as courseutils
from nytid import schedules as schedutils
from nytid.signup import hr
from nytid.signup import sheets

from nytid.signup import sheets
from nytid.signup import utils
import os, platform, subprocess

SIGNUPSHEET_URL_PATH = "signupsheet.url"

cli = typer.Typer(name="signupsheets", help="Manage sign-up sheets for teaching")

outpath_opt = typer.Option(
    help="Path where to write the sign-up sheet "
    "files. Default is in each course's "
    "data path."
)
edit_opt = typer.Option(help="If specified, opens each generated sheet " "for editing.")
url_arg = typer.Argument(
    help="The URL for the sign-up sheet. "
    "For Google Sheets, it's the same URL as the "
    "one shared with TAs to sign up. "
    "For others, it's a URL to a CSV file."
)


@cli.command(name="generate")
def generate_signup_sheet(
    course: Annotated[str, coursescli.course_arg_regex],
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    outpath: Annotated[pathlib.Path, outpath_opt] = None,
    edit: Annotated[bool, edit_opt] = False,
):
    """
    Generates a sign-up sheet to be used with Google Sheets or similar for TAs to
    sign up.
    """
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M")
    for (course, register), course_conf in courses.items():
        try:
            num_students = int(course_conf.get("num_students"))
        except ValueError as err:
            logging.warning(
                f"num_students for {course} in {register} is not an integer: " f"{err}"
            )
            continue

        try:
            num_groups = int(course_conf.get("num_groups"))
        except ValueError as err:
            logging.warning(
                f"num_groups for {course} in {register} is not an integer: " f"{err}"
            )
            continue

        try:
            group_size = round(num_students / num_groups)
        except ZeroDivisionError as err:
            logging.warning(f"num_groups for {course} in {register} is zero: {err}")
            continue

        def needed_TAs(event):
            return utils.needed_TAs(event, group_size=group_size)

        if not outpath:
            try:
                data_root = courseutils.get_course_data(course, register)
            except KeyError as err:
                logging.warning(err)
            except PermissionError as err:
                logging.warning(
                    f"You don't have access to {course} in {register}: {err}"
                )
                outfile = f"./signup-{course}-{timestamp}.csv"
                logging.warning(f"Writing file to current working directory: {outfile}")
            else:
                outfile = data_root.path / f"signup-{course}-{timestamp}.csv"
        else:
            outfile = outpath / f"signup-{course}-{timestamp}.csv"

        url = course_conf.get("ics")
        sheets.generate_signup_sheet(outfile, url, needed_TAs)
        if edit:
            the_os = platform.system()
            if the_os == "Darwin":
                subprocess.call(["open", outfile])
            elif the_os == "Windows":
                os.startfile(outfile)
            else:
                subprocess.call(["xdg-open", outfile])


@cli.command()
def set_url(
    course: Annotated[str, coursescli.course_arg_regex],
    url: Annotated[str, url_arg],
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
):
    """
    Sets the URL of the sign-up sheet for the course(s).
    """
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)
    for _, conf in courses.items():
        conf.set(SIGNUPSHEET_URL_PATH, url)
