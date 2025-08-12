import datetime
from enum import Enum
import ics.icalendar
import logging
import os
import sys
import typer
from typing_extensions import Annotated

from nytid.cli import courses as coursescli
from nytid import courses as courseutils
from nytid import schedules as schedutils
from nytid.cli.signupsheets import SIGNUPSHEET_URL_PATH

from nytid.signup import sheets
import os
import functools
import ics.icalendar
from ics.grammar.parse import ContentLine
import csv
import sys

cli = typer.Typer(name="schedule", help="Working with course schedules")


def map_drop_exceptions(func, iterable):
    """
    Same as map, but ignores exceptions from `func`.
    Logs a warning when an item is dropped.
    """
    for item in iterable:
        try:
            yield func(item)
        except Exception as err:
            logging.warning(f"Dropped {item}: {err}")


def add_reserve_to_title(ta, event):
    """
    Input: an event in CSV form.
    Ouput: the same CSV data, but with title prepended "RESERVE: " if TA is
    among the reserves.
    """
    _, reserves = sheets.get_booked_TAs_from_csv(event)
    if ta in reserves:
        event[0] = "RESERVE: " + event[0]

    return event


def update_end_date(start, end):
    """
    Returns a correct end date.
    """
    if end < start:
        return start + datetime.timedelta(weeks=1)
    return end


try:
    default_username = os.environ["USER"]
except KeyError:
    default_username = None

username_opt = typer.Option(
    help="Username to filter sign-up sheet for, "
    "defaults to logged in user's username."
)
start_date_opt = typer.Option(help="The start date", formats=["%Y-%m-%d"])
end_date_opt = typer.Option(help="The end date", formats=["%Y-%m-%d"])


class GroupByDayOrWeek(str, Enum):
    week = "week"
    day = "day"


group_by_day_or_week = typer.Option(
    help="Choose whether to group events " "by day or week", case_sensitive=False
)
week_opt = typer.Option(help="Print week number and day of week")
location_opt = typer.Option(help="Print location of event")
delimiter_opt = typer.Option(help="Delimiter for CSV output")


@cli.command(name="ics")
def ics_cmd(
    course: Annotated[str, coursescli.course_arg_regex] = ".*",
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    user: Annotated[str, username_opt] = default_username,
):
    """
    Prints ICS data to stdout. Redirect to a .ics file, preferably in
    ~/public_html, and add it to your calendar.
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

    schedule = ics.icalendar.Calendar()
    schedule.method = "PUBLISH"
    schedule.extra += [ContentLine("X-PUBLISHED-TTL", {}, "PT20M")]

    booked = []
    for (course, register), config in courses.items():
        try:
            try:
                url = config.get(SIGNUPSHEET_URL_PATH)
                if "docs.google.com" in url:
                    url = sheets.google_sheet_to_csv_url(url)
                booked += sheets.read_signup_sheet_from_url(url)
            except KeyError as err_signupsheet:
                logging.warning(
                    f"Can't read sign-up sheet for {course} ({register}): "
                    f"{err_signupsheet}"
                )
                course_schedule = schedutils.read_calendar(config.get("ics"))
                schedule.events.update(schedutils.event_filter(course_schedule.events))
        except Exception as err:
            logging.error(
                f"Can't read sign-up sheet nor ICS for " f"{course} ({register}): {err}"
            )
            continue

    if user:
        booked = sheets.filter_events_by_TA(user, booked)
        booked = map(functools.partial(add_reserve_to_title, user), booked)

    schedule.events.update(set(map_drop_exceptions(sheets.EventFromCSV, booked)))
    schedule.name = "Nytid"
    if user:
        schedule.name = f"{user}'s nytid"
    schedule.extra += [ContentLine("X-WR-CALNAME", {}, schedule.name)]
    schedule.description = "Nytid export"
    if user:
        schedule.description = f"Nytid export for {user}"
    schedule.extra += [ContentLine("X-WR-CALDESC", {}, schedule.description)]
    print(schedule.serialize())


@cli.command()
def show(
    course: Annotated[str, coursescli.course_arg_regex] = ".*",
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    user: Annotated[str, username_opt] = default_username,
    start: Annotated[datetime.datetime, start_date_opt] = str(datetime.date.today()),
    end: Annotated[datetime.datetime, end_date_opt] = str(
        datetime.date.today() + datetime.timedelta(weeks=1)
    ),
    group_by: Annotated[GroupByDayOrWeek, group_by_day_or_week] = "week",
    week: Annotated[bool, week_opt] = False,
    location: Annotated[bool, location_opt] = True,
    delimiter: Annotated[str, delimiter_opt] = "\t",
):
    """
    Shows schedule for courses in human readable format. If there is a sign-up
    sheet for a course, it is used instead of the ICS.
    """
    end = update_end_date(start, end)
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

    schedule = ics.icalendar.Calendar()
    schedule.method = "PUBLISH"
    schedule.extra += [ContentLine("X-PUBLISHED-TTL", {}, "PT20M")]

    booked = []
    for (course, register), config in courses.items():
        try:
            try:
                url = config.get(SIGNUPSHEET_URL_PATH)
                if "docs.google.com" in url:
                    url = sheets.google_sheet_to_csv_url(url)
                booked += sheets.read_signup_sheet_from_url(url)
            except KeyError as err_signupsheet:
                logging.warning(
                    f"Can't read sign-up sheet for {course} ({register}): "
                    f"{err_signupsheet}"
                )
                course_schedule = schedutils.read_calendar(config.get("ics"))
                schedule.events.update(schedutils.event_filter(course_schedule.events))
        except Exception as err:
            logging.error(
                f"Can't read sign-up sheet nor ICS for " f"{course} ({register}): {err}"
            )
            continue

    if user:
        booked = sheets.filter_events_by_TA(user, booked)
        booked = map(functools.partial(add_reserve_to_title, user), booked)

    schedule.events.update(set(map_drop_exceptions(sheets.EventFromCSV, booked)))
    schedule.name = "Nytid"
    if user:
        schedule.name = f"{user}'s nytid"
    schedule.extra += [ContentLine("X-WR-CALNAME", {}, schedule.name)]
    schedule.description = "Nytid export"
    if user:
        schedule.description = f"Nytid export for {user}"
    schedule.extra += [ContentLine("X-WR-CALDESC", {}, schedule.description)]
    first = True
    if group_by == GroupByDayOrWeek.week:
        group_by_idx = 1
    elif group_by == GroupByDayOrWeek.day:
        group_by_idx = 2
    csvout = csv.writer(sys.stdout, delimiter=delimiter)
    for event in schedule.timeline:
        if event.end.date() < start.date():
            continue
        elif event.begin.date() > end.date():
            continue
        if first:
            first = False
            current_epoc = event.begin.isocalendar()[group_by_idx]
        elif event.begin.isocalendar()[group_by_idx] != current_epoc:
            print("\n")
            current_epoc = event.begin.isocalendar()[group_by_idx]
        csvout.writerow(schedutils.format_event_csv(event, week, location))
