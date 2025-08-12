import arrow
import csv
import datetime
from enum import Enum
import ics.icalendar
import json
import logging
import pathlib
import os
import sys
import typer
from typing_extensions import Annotated

from nytid.signup import hr
from nytid.signup import sheets
import operator

from nytid.cli import courses as coursescli
from nytid.cli.signupsheets import SIGNUPSHEET_URL_PATH
from nytid import courses as courseutils
from nytid import schedules as schedutils
from nytid.signup import hr
from nytid.signup import sheets

import appdirs

try:
    import canvasapi
    import canvaslms.cli

    dirs_canvas = appdirs.AppDirs("canvaslms", "dbosk@kth.se")

    canvaslms_config = canvaslms.cli.read_configuration(
        f"{dirs_canvas.user_config_dir}/config.json"
    )

    CANVAS_SERVER, CANVAS_TOKEN = canvaslms.cli.login.load_credentials(canvaslms_config)

    if CANVAS_SERVER and CANVAS_TOKEN:
        canvas_session = canvasapi.Canvas(
            os.environ["CANVAS_SERVER"], os.environ["CANVAS_TOKEN"]
        )
    else:
        canvas_session = None
        logging.warning("Can't load Canvas credentials, run `canvaslms login`")
except ImportError as err:
    logging.warning(f"Can't import Canvas: {err}")
    canvas_session = None
except Exception as err:
    logging.warning(f"Can't load Canvas credentials: {err}")
    canvas_session = None
try:
    import ladok3
    import ladok3.cli

    dirs_ladok = appdirs.AppDirs("ladok", "dbosk@kth.se")

    LADOK_INST, LADOK_VARS = ladok3.cli.load_credentials(
        "f{dirs_ladok.user_config_dir}/config.json"
    )

    if LADOK_INST and LADOK_VARS:
        ladok_session = ladok3.LadokSession(LADOK_INST, LADOK_VARS)
    else:
        ladok_session = None
        logging.warning("Can't load LADOK credentials, run `ladok login`")
except ImportError as err:
    logging.warning(f"Can't import ladok3, not using LADOK data: {err}")
    ladok_session = None
except Exception as err:
    logging.warning(f"Can't load LADOK credentials: {err}")
    ladok_session = None
import cachetools
from nytid.signup import sheets
from nytid.signup import hr
import re
import typerconf
from nytid.signup.hr import timesheet

AMANUENSIS_CONTRACT_PATH = "hr.amanuensis.contract_dir"
TIMESHEETS_DIR_PATH = "hr.timesheets.timesheets_dir"

cli = typer.Typer(name="hr", help="Manage sign-up sheets for teaching")


@cachetools.cached(cache={})
def get_canvas_courses(course_regex):
    """
    Returns a list of Canvas course objects matching the given course_regex.
    """
    courses = list(canvaslms.cli.courses.filter_courses(canvas_session, course_regex))
    return courses


@cachetools.cached(cache={})
def get_canvas_users(username_regex, course_regex):
    """
    Returns a list of Canvas user objects matching the given username_regex.
    Searches for username_regex in the courses matching course_regex.
    """
    courses = get_canvas_courses(course_regex)
    users = list(canvaslms.cli.users.filter_users(courses, username_regex))
    return users


def get_canvas_user(username, course_regex):
    """
    Takes a username and returns a Canvas user object.
    Searches for username in the courses matching course_regex.
    """
    users = get_canvas_users(".*", course_regex)
    username = username.strip()
    users_without_login_id = []

    for user in users:
        try:
            if user.login_id.split("@")[0] == username or user.login_id == username:
                return user
        except AttributeError:
            users_without_login_id.append(user)
    users_without_login_id_str = "\n  ".join(map(str, users_without_login_id))
    raise ValueError(
        f"Can't find {username} in Canvas, but the following users "
        f"don't have a login ID: {users_without_login_id_str}"
    )


def get_ladok_user(canvas_user):
    """
    Takes a Canvas user object and returns a LADOK student object.
    """
    try:
        return ladok_session.get_student(canvas_user.integration_id)
    except KeyError as err:
        raise KeyError(f"can't look up {canvas_user} in LADOK: {err}")


def to_hours(td):
    return td.total_seconds() / 60 / 60


def push_forward(start, end, push_start):
    """
    Takes a start and end date and pushes them forward so that start becomes
    push_start.
    """
    if push_start > start:
        end += push_start - start
        start = push_start

    return start, end


def get_valid_contracts(user_regex):
    """
    Returns a list of valid contracts matching `user_regex`.
    """
    contracts = []

    try:
        contracts_path = pathlib.Path(typerconf.get(AMANUENSIS_CONTRACT_PATH))
    except KeyError as err:
        logging.warning(
            f"Can't find {AMANUENSIS_CONTRACT_PATH} in config, "
            f"looking for contract data in `./`. Set by running "
            f"`nytid config {AMANUENSIS_CONTRACT_PATH} -s <path>`."
        )
        contracts_path = pathlib.Path("./")
    users = set()
    user_pattern = re.compile(user_regex)
    for contract in contracts_path.glob("*.json"):
        username = contract.name.split(".")[0]
        if user_pattern.match(username):
            users.add(username)
    for user in users:
        user_contracts = []

        contract_files = sorted(
            contracts_path.glob(f"{user}.*.json"), key=lambda x: x.name
        )
        prev_contract = None
        for contract_file in contract_files:
            try:
                with open(contract_file) as infile:
                    contract = json.load(infile)
            except Exception as err:
                logging.warning(f"Can't read {contract_file}, skipping: {err}")
                continue

            if prev_contract:
                if not contract_overlap(prev_contract, contract):
                    user_contracts.append(prev_contract)

            prev_contract = contract

        user_contracts.append(contract)

        contracts += user_contracts

    return contracts


def contract_overlap(contract1, contract2):
    """
    Returns True if the contracts overlap, False otherwise.

    We define overlap as having at least one event in common.
    """
    for event1 in contract1["events"]:
        for event2 in contract2["events"]:
            if event_overlap(event1, event2):
                return True
    return False


def event_overlap(event1, event2):
    """
    Returns True if the events overlap, False otherwise.

    We define overlap as overlapping in time.
    """
    start1 = datetime.datetime.fromisoformat(event1[1])
    end1 = datetime.datetime.fromisoformat(event1[2])
    start2 = datetime.datetime.fromisoformat(event2[1])
    end2 = datetime.datetime.fromisoformat(event2[2])

    return start1 < end2 and start2 < end1


def remove_events(events, events_to_remove):
    """
    Removes the events in `events_to_remove` from `events`.
    """
    return list(filter(lambda x: x not in events_to_remove, events))


def salary_difference(added_events, removed_events):
    """
    Returns the difference in salary between the added and removed events.
    """
    return sum(map(lambda x: x["belopp"], added_events)) - sum(
        map(lambda x: x["belopp"], removed_events)
    )


def summarize_user(user, course_events, salary=150):
    """
    Returns events where TA worked.
    - `user` is the TA's username.
    - `course_events` is a list of events.
    - Optional `salary` is the hourly salary.
    """
    start_idx = sheets.SIGNUP_SHEET_HEADER.index("Start")
    end_idx = sheets.SIGNUP_SHEET_HEADER.index("End")
    type_idx = sheets.SIGNUP_SHEET_HEADER.index("Event")
    try:
        hours = to_hours(hr.hours_per_TA(course_events)[user])
    except KeyError:
        hours = 0
    events = sheets.filter_events_by_TA(
        user, sorted(course_events, key=operator.itemgetter(start_idx))
    )
    events = filter(lambda x: user in sheets.get_booked_TAs_from_csv(x)[0], events)
    events = list(
        map(lambda x: x[0 : len(sheets.SIGNUP_SHEET_HEADER)] + [user], events)
    )

    xl_events = []

    for event in events:
        end = arrow.get(event[end_idx])
        start = arrow.get(event[start_idx])
        event_type = event[type_idx]
        time = end - start
        time_with_prep = to_hours(
            hr.round_time(hr.add_prep_time(time, event_type, date=start.date()))
        )
        course = ""
        codes = re.findall(r"[A-Z]{2,4}\d{3,4}[A-Z]?", event_type)
        if codes:
            course = ", ".join(codes)

        xl_events.append(
            {
                "datum": str(start.date()),
                "tid": str(start.time()),
                "kurskod": course,
                "typ": event_type,
                "timmar": to_hours(time),
                "koeff": hr.prep_factor(
                    event_type, date=start.date(), amanuensis=False
                ),
                "omr_tid": time_with_prep,
                "belopp": time_with_prep * salary,
            }
        )

    return xl_events


detailed_opt = typer.Option(help="Output detailed user data.")
course_summary_opt = typer.Option(help="Print a summary of the course.")
amanuensis_summary_opt = typer.Option(help="Print a summary of the " "amanuensis.")
hourly_summary_opt = typer.Option(help="Print a summary of the hourly TAs.")
draft_opt = typer.Option(help="Create a draft, " "don't store the generated contract.")
user_regex_opt = typer.Option(
    "--user", help="Regex to match TAs' usernames that " "should be included."
)
start_date_opt = typer.Option(
    help="The start date (inclusive, <=), "
    "when unset includes "
    "everything in the sign-up sheet. "
    "Set this to decide what to include from "
    "the sign-up sheet.",
    formats=["%Y-%m-%d"],
)
end_date_opt = typer.Option(
    help="The end date (not inclusive, <), "
    "when unset includes "
    "everything in the sign-up sheet. "
    "Set this to decide what to include from "
    "the sign-up sheet.",
    formats=["%Y-%m-%d"],
)
delimiter_opt = typer.Option(help="Delimiter to use in CSV output.")
event_summary_opt = typer.Option(help="Print a summary of the hours per event " "type.")
push_start_opt = typer.Option(
    help="Push the dates of the contract so that it "
    "starts at this date. "
    "This keeps the same percentage.",
    formats=["%Y-%m-%d"],
)
set_start_opt = typer.Option(
    help="Force the start date of the contract to "
    "this date. Might modify percentage.",
    formats=["%Y-%m-%d"],
)
set_end_opt = typer.Option(
    help="Force the end date of the contract to " "this date. Might modify percentage.",
    formats=["%Y-%m-%d"],
)
user_regex_arg = typer.Argument(
    help="Regex to match TAs' usernames that " "should be included."
)
events_opt = typer.Option(help="Print the events used to compute the " "contract.")
updates_opt = typer.Option(
    help="Also show a draft contract based on the " "current bookings."
)
diff_opt = typer.Option(
    help="diff: Only generate time sheets when there's a "
    "difference in salary. "
    "no-diff: Always generate time sheets when there "
    "are changes, even if there is no change in "
    "salary to be paid. "
    "(E.g. it's a change of dates.) "
    "No time sheets will be generated if there "
    "are no new events."
)
draft_opt = typer.Option(
    help="Print a draft of the time sheet to stdout. " "Don't generate any timesheet."
)
store_opt = typer.Option(help="Store the time sheet data as reported.")
amanuensis_opt = typer.Option(
    help="Include only amanuenses, i.e. generate "
    "mertid time sheets. no-amanuensis "
    "include only hourly TAs."
)
sign_opt = typer.Option(help="Include the course responsible's signature.")
course_responsible_opt = typer.Option(
    help="The course responsible's name; "
    "If no default is set, we try to extract the value from the courses' config. "
    "You can set the default by running `nytid config ...` or "
    "`nytid courses config <course> me.name -s <name>`."
)
try:
    default_course_responsible = typerconf.get("me.name")
except KeyError:
    default_course_responsible = ""
course_responsible_email_opt = typer.Option(
    help="The course responsible's "
    "email; "
    "If no default is set, we try to extract the value from the courses' config. "
    "You can set the default by running `nytid config ...` or "
    "`nytid courses config <course> me.email -s <email>`."
)
try:
    default_email = typerconf.get("me.email")
except KeyError:
    default_email = ""
course_responsible_signature_opt = typer.Option(
    help="Path to a picture of "
    "the course "
    "responsible's "
    "signature; "
    "If no default is set, we try to extract the value from the courses' config. "
    "You can set the default by running `nytid config ...` or "
    "`nytid courses config <course> me.signature -s <path>`."
)
try:
    default_signature_file = pathlib.Path(typerconf.get("me.signature"))
except KeyError:
    default_signature_file = None
manager_opt = typer.Option(
    help="The manager's name; "
    "If no default is set, we try to extract the value from the courses' config. "
    "You can set the default by running `nytid config ...` or "
    "`nytid courses config <course> hr.manager -s <name>`."
)
try:
    default_manager = typerconf.get("hr.manager")
except KeyError:
    default_manager = ""
org_opt = typer.Option(
    help="The organization code for accounting; "
    "If no default is set, we try to extract the value from the courses' config. "
    "You can set the default by running `nytid config ...` or "
    "`nytid courses config <course> hr.organization -s <code>`."
)
try:
    default_organization = typerconf.get("hr.organization")
except KeyError:
    default_organization = ""
project_opt = typer.Option(
    help="The project number for accounting; "
    "If no default is set, we try to extract the value from the courses' config. "
    "You can set the default by running `nytid config ...` or "
    "`nytid courses config <course> hr.project -s <code>`."
)
try:
    default_project = typerconf.get("hr.project")
except KeyError:
    default_project = ""
reverse_opt = typer.Option(help="Reverse the sort order.")
all_opt = typer.Option(
    "--all/--newest", help="Show all time sheets or just the newest."
)
date_regex_opt = typer.Option(
    help="Filter time sheets by date. This is a "
    "regex matching the date of the time "
    "sheet."
)


@cli.command()
def users(
    course_regex: Annotated[str, coursescli.course_arg_regex],
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    detailed: Annotated[bool, detailed_opt] = False,
):
    """
    Prints the list of all usernames booked on the course.
    """
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course_regex, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)
    booked = []
    for (course, register), config in courses.items():
        try:
            url = config.get(SIGNUPSHEET_URL_PATH)
        except KeyError as err:
            logging.warning(
                f"Can't find sign-up sheet URL for {course} in {register}: " f"{err}"
            )
            continue
        if "docs.google.com" in url:
            url = sheets.google_sheet_to_csv_url(url)
        booked += sheets.read_signup_sheet_from_url(url)

    for user in hr.hours_per_TA(booked):
        if detailed:
            user_obj = user
            try:
                user_obj = get_canvas_user(user, course_regex)
            except Exception as err:
                logging.warning(f"Can't look up {user} in Canvas: {err}")
            else:
                try:
                    email = user_obj.email
                    user_obj = get_ladok_user(user_obj)
                    user_obj.email = email
                except Exception as err:
                    logging.warning(
                        f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                    )
                    pass
        else:
            user_obj = user
        try:
            if detailed and "@" not in str(user_obj):
                print(f"{user_obj} <{user_obj.email}>")
            else:
                print(user_obj)
        except AttributeError:
            print(user_obj)


@cli.command()
def time(
    course_regex: Annotated[str, coursescli.course_arg_regex],
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    detailed: Annotated[bool, detailed_opt] = False,
    course_summary: Annotated[bool, course_summary_opt] = True,
    amanuensis_summary: Annotated[bool, amanuensis_summary_opt] = True,
    hourly_summary: Annotated[bool, hourly_summary_opt] = True,
):
    """
    Summarizes the time spent on teaching the course(s).
    """
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course_regex, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)
    booked = []
    for (course, register), config in courses.items():
        try:
            url = config.get(SIGNUPSHEET_URL_PATH)
        except KeyError as err:
            logging.warning(
                f"Can't find sign-up sheet URL for {course} in {register}: " f"{err}"
            )
            continue
        if "docs.google.com" in url:
            url = sheets.google_sheet_to_csv_url(url)
        booked += sheets.read_signup_sheet_from_url(url)
    csvout = csv.writer(sys.stdout, delimiter="\t")
    if course_summary:
        h_per_student = hr.hours_per_student(booked)

        for event, hours in h_per_student.items():
            csvout.writerow([event, to_hours(hours), "h/student"])

        csvout.writerow(
            [
                "Booked (h)",
                to_hours(hr.total_hours(booked)),
                to_hours(hr.max_hours(booked)),
            ]
        )
    if amanuensis_summary:
        if course_summary:
            csvout.writerow([])
        if hourly_summary:
            csvout.writerow(["# Amanuensis"])

        amanuensis = hr.compute_amanuensis_data(booked)

        for user, data in amanuensis.items():
            if not user:
                continue
            if detailed:
                user_obj = user
                try:
                    user_obj = get_canvas_user(user, course_regex)
                except Exception as err:
                    logging.warning(f"Can't look up {user} in Canvas: {err}")
                else:
                    try:
                        email = user_obj.email
                        user_obj = get_ladok_user(user_obj)
                        user_obj.email = email
                    except Exception as err:
                        logging.warning(
                            f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                        )
                        pass
            else:
                user_obj = user
            csvout.writerow(
                [
                    user_obj,
                    f"{data[2]:.2f} h",
                    f"{100*hr.compute_percentage(*data):.1f}%",
                    f"{data[0].format('YYYY-MM-DD')}",
                    f"{data[1].format('YYYY-MM-DD')}",
                ]
            )
    if hourly_summary:
        if amanuensis_summary:
            csvout.writerow([])
            csvout.writerow(["# Hourly"])
        elif course_summary:
            csvout.writerow([])

        for user, hours in hr.hours_per_TA(booked).items():
            if not user or user in amanuensis:
                continue
            if detailed:
                user_obj = user
                try:
                    user_obj = get_canvas_user(user, course_regex)
                except Exception as err:
                    logging.warning(f"Can't look up {user} in Canvas: {err}")
                else:
                    try:
                        email = user_obj.email
                        user_obj = get_ladok_user(user_obj)
                        user_obj.email = email
                    except Exception as err:
                        logging.warning(
                            f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                        )
                        pass
            else:
                user_obj = user

            try:
                user_text = (
                    f"{user_obj} <{user_obj.email}>"
                    if "@" not in str(user_obj)
                    else str(user_obj)
                )
            except AttributeError:
                user_text = str(user_obj)

            csvout.writerow([user_text, to_hours(hours), "h"])


amanuensis = typer.Typer(name="amanuensis", help="Manage amanuensis employment")
cli.add_typer(amanuensis)


@amanuensis.command(name="create")
def cli_amanuens_create(
    user_regex: Annotated[str, user_regex_opt] = ".*",
    start: Annotated[datetime.datetime, start_date_opt] = None,
    end: Annotated[datetime.datetime, end_date_opt] = None,
    push_start: Annotated[datetime.datetime, push_start_opt] = None,
    set_start: Annotated[datetime.datetime, set_start_opt] = None,
    set_end: Annotated[datetime.datetime, set_end_opt] = None,
    course_regex: Annotated[str, coursescli.course_arg_regex] = ".*",
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    detailed: Annotated[bool, detailed_opt] = True,
    event_summary: Annotated[bool, event_summary_opt] = False,
    draft: Annotated[bool, draft_opt] = False,
    delimiter: Annotated[str, delimiter_opt] = "\t",
):
    """
    Computes amanuensis data for a TA.
    """
    if start:
        start = start.astimezone()
    if push_start:
        push_start = push_start.astimezone()
    if set_start:
        set_start = set_start.astimezone()
    if end:
        end = end.astimezone()
    if set_end:
        set_end = set_end.astimezone()
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course_regex, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)
    booked = []
    for (course, register), config in courses.items():
        try:
            url = config.get(SIGNUPSHEET_URL_PATH)
        except KeyError as err:
            logging.warning(
                f"Can't find sign-up sheet URL for {course} in {register}: " f"{err}"
            )
            continue
        if "docs.google.com" in url:
            url = sheets.google_sheet_to_csv_url(url)
        booked += sheets.read_signup_sheet_from_url(url)
    booked = sheets.filter_events_by_date(booked, start, end)

    amanuensis = hr.compute_amanuensis_data(booked, begin_date=start, end_date=end)

    user_pattern = re.compile(user_regex)
    first_print = True
    csvout = csv.writer(sys.stdout, delimiter=delimiter)
    path = pathlib.Path("./")
    try:
        path = pathlib.Path(typerconf.get(AMANUENSIS_CONTRACT_PATH))
    except KeyError as err:
        logging.warning(
            f"Can't find {AMANUENSIS_CONTRACT_PATH} in config, "
            f"storing contract data in `{path}`. Set by running "
            f"`nytid config {AMANUENSIS_CONTRACT_PATH} -s <path>`."
        )
    for user in amanuensis:
        if not user_pattern.match(user):
            continue
        if first_print:
            first_print = False
        else:
            print("\n")

        data = amanuensis[user]

        start = data[0]
        end = data[1]
        hours = data[2]
        if push_start:
            push_start = arrow.Arrow(push_start.year, push_start.month, push_start.day)
            start, end = push_forward(start, end, push_start)
        data = list(data)
        if set_start:
            start = data[0] = set_start
        if set_end:
            end = data[1] = set_end

        if detailed:
            user_obj = user
            try:
                user_obj = get_canvas_user(user, course_regex)
            except Exception as err:
                logging.warning(f"Can't look up {user} in Canvas: {err}")
            else:
                try:
                    email = user_obj.email
                    user_obj = get_ladok_user(user_obj)
                    user_obj.email = email
                except Exception as err:
                    logging.warning(
                        f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                    )
                    pass
        else:
            user_obj = user

        try:
            user_text = (
                f"{user_obj} <{user_obj.email}>"
                if "@" not in str(user_obj)
                else str(user_obj)
            )
        except AttributeError:
            user_text = str(user_obj)

        row = [
            user_text,
            start.date(),
            end.date(),
            f"{round(100*hr.compute_percentage(*data))}%",
        ]

        if event_summary:
            row.append(f"{hours:.2f} h")

        csvout.writerow(row)

        user_events = sheets.filter_events_by_TA(user, booked)
        user_events = filter(
            lambda x: user in sheets.get_booked_TAs_from_csv(x)[0], booked
        )
        user_events = list(
            map(lambda x: x[0 : len(sheets.SIGNUP_SHEET_HEADER)] + [user], user_events)
        )
        if event_summary:
            for event, hours in hr.hours_per_event(user_events).items():
                csvout.writerow([event, to_hours(hours), "h"])
        if not draft:
            filename = f"{user}.{datetime.datetime.now().isoformat()}.json"

            path.mkdir(parents=True, exist_ok=True)

            with open(path / filename, "w") as outfile:
                json.dump(
                    {
                        "user": user,
                        "start": start.isoformat() if start else None,
                        "set_start": set_start.isoformat() if set_start else None,
                        "push_start": push_start.isoformat() if push_start else None,
                        "end": end.isoformat() if end else None,
                        "set_end": set_end.isoformat() if set_end else None,
                        "course_regex": course_regex,
                        "events": user_events,
                    },
                    outfile,
                    indent=2,
                )


@amanuensis.command(name="show")
def cli_amanuens_show(
    user_regex: Annotated[str, user_regex_arg] = ".*",
    detailed: Annotated[bool, detailed_opt] = False,
    event_summary: Annotated[bool, event_summary_opt] = True,
    delimiter: Annotated[str, delimiter_opt] = "\t",
    updates: Annotated[bool, updates_opt] = False,
    events: Annotated[bool, events_opt] = False,
):
    """
    Shows stored amanuesis contracts for TAs.
    """
    try:
        contracts_path = pathlib.Path(typerconf.get(AMANUENSIS_CONTRACT_PATH))
    except KeyError as err:
        logging.warning(
            f"Can't find {AMANUENSIS_CONTRACT_PATH} in config, "
            f"looking for contract data in `./`. Set by running "
            f"`nytid config {AMANUENSIS_CONTRACT_PATH} -s <path>`."
        )
        contracts_path = pathlib.Path("./")
    contracts = get_valid_contracts(user_regex)

    user_pattern = re.compile(user_regex)
    first_print = True
    csvout = csv.writer(sys.stdout, delimiter=delimiter)
    path = pathlib.Path("./")
    try:
        path = pathlib.Path(typerconf.get(AMANUENSIS_CONTRACT_PATH))
    except KeyError as err:
        logging.warning(
            f"Can't find {AMANUENSIS_CONTRACT_PATH} in config, "
            f"storing contract data in `{path}`. Set by running "
            f"`nytid config {AMANUENSIS_CONTRACT_PATH} -s <path>`."
        )
    for contract in contracts:
        user = contract["user"]
        booked = contract["events"]

        start = (
            datetime.datetime.fromisoformat(contract["start"])
            if "start" in contract and contract["start"]
            else None
        )
        push_start = (
            datetime.datetime.fromisoformat(contract["push_start"])
            if "push_start" in contract and contract["push_start"]
            else None
        )
        set_start = (
            datetime.datetime.fromisoformat(contract["set_start"])
            if "set_start" in contract and contract["set_start"]
            else None
        )
        end = (
            datetime.datetime.fromisoformat(contract["end"])
            if "end" in contract and contract["end"]
            else None
        )
        set_end = (
            datetime.datetime.fromisoformat(contract["set_end"])
            if "set_end" in contract and contract["set_end"]
            else None
        )

        amanuensis = hr.compute_amanuensis_data(booked, begin_date=start, end_date=end)

        try:
            course_regex = contract["course_regex"]
        except KeyError:
            code_pattern = re.compile(r"[A-Z]{2,4}\d{3,4}[A-Z]?")
            for event in booked:
                match = code_pattern.search(event[0])
                if match:
                    course_regex = match.group(0)
                    break
            else:
                course_regex = ".*"

        if first_print:
            first_print = False
        else:
            print("\n")

        data = amanuensis[user]

        start = data[0]
        end = data[1]
        hours = data[2]
        if push_start:
            push_start = arrow.Arrow(push_start.year, push_start.month, push_start.day)
            start, end = push_forward(start, end, push_start)
        data = list(data)
        if set_start:
            start = data[0] = set_start
        if set_end:
            end = data[1] = set_end

        if detailed:
            user_obj = user
            try:
                user_obj = get_canvas_user(user, course_regex)
            except Exception as err:
                logging.warning(f"Can't look up {user} in Canvas: {err}")
            else:
                try:
                    email = user_obj.email
                    user_obj = get_ladok_user(user_obj)
                    user_obj.email = email
                except Exception as err:
                    logging.warning(
                        f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                    )
                    pass
        else:
            user_obj = user

        try:
            user_text = (
                f"{user_obj} <{user_obj.email}>"
                if "@" not in str(user_obj)
                else str(user_obj)
            )
        except AttributeError:
            user_text = str(user_obj)

        row = [
            user_text,
            start.date(),
            end.date(),
            f"{round(100*hr.compute_percentage(*data))}%",
        ]

        if event_summary:
            row.append(f"{hours:.2f} h")

        csvout.writerow(row)

        user_events = sheets.filter_events_by_TA(user, booked)
        user_events = filter(
            lambda x: user in sheets.get_booked_TAs_from_csv(x)[0], booked
        )
        user_events = list(
            map(lambda x: x[0 : len(sheets.SIGNUP_SHEET_HEADER)] + [user], user_events)
        )
        if event_summary:
            for event, hours in hr.hours_per_event(user_events).items():
                csvout.writerow([event, to_hours(hours), "h"])
        if events:
            print()
            csvout = csv.writer(sys.stdout, delimiter="\t")
            for event in contract["events"]:
                csvout.writerow(event)
        if updates:
            print()
            try:
                start = (
                    datetime.datetime.fromisoformat(contract["start"])
                    if contract["start"]
                    else None
                )
            except KeyError:
                start = None

            try:
                end = (
                    datetime.datetime.fromisoformat(contract["end"])
                    if contract["end"]
                    else None
                )
            except KeyError:
                end = None

            try:
                push_start = (
                    datetime.datetime.fromisoformat(contract["push_start"])
                    if contract["push_start"]
                    else None
                )
            except KeyError:
                push_start = None

            try:
                set_start = (
                    datetime.datetime.fromisoformat(contract["set_start"])
                    if contract["set_start"]
                    else None
                )
            except KeyError:
                set_start = None

            try:
                set_end = (
                    datetime.datetime.fromisoformat(contract["set_end"])
                    if contract["set_end"]
                    else None
                )
            except KeyError:
                set_end = None

            cli_amanuens_create(
                user_regex=contract["user"],
                course_regex=".*",
                start=start,
                end=end,
                push_start=push_start,
                set_start=set_start,
                set_end=set_end,
                detailed=detailed,
                event_summary=event_summary,
                draft=True,
                delimiter=delimiter,
            )


timesheets = typer.Typer(name="timesheets", help="Manage timesheets for TAs")
cli.add_typer(timesheets)


@timesheets.command(name="generate")
def cli_generate_timesheets(
    user_regex: Annotated[str, user_regex_opt] = ".*",
    start: Annotated[datetime.datetime, start_date_opt] = None,
    end: Annotated[datetime.datetime, end_date_opt] = None,
    course_responsible: Annotated[
        str, course_responsible_opt
    ] = default_course_responsible,
    course_responsible_email: Annotated[
        str, course_responsible_email_opt
    ] = default_email,
    course_responsible_signature: Annotated[
        pathlib.Path, course_responsible_signature_opt
    ] = default_signature_file,
    manager: Annotated[str, manager_opt] = default_manager,
    organization: Annotated[str, org_opt] = default_organization,
    project: Annotated[str, project_opt] = default_project,
    course_regex: Annotated[str, coursescli.course_arg_regex] = ".*",
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    store: Annotated[bool, store_opt] = True,
    amanuensis: Annotated[bool, amanuensis_opt] = False,
    sign: Annotated[bool, sign_opt] = True,
    diff: Annotated[bool, diff_opt] = True,
    draft: Annotated[bool, draft_opt] = False,
):
    """
    Generates time sheets for TAs in courses.
    """
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course_regex, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)
    managers = []
    orgs = []
    projects = []
    for _, course_config in courses.items():
        try:
            managers.append(course_config.get("hr.manager"))
        except KeyError:
            pass
        try:
            orgs.append(course_config.get("hr.organization"))
        except KeyError:
            pass
        try:
            projects.append(course_config.get("hr.project"))
        except KeyError:
            pass

    if len(set(managers)) == 1:
        manager = managers[0]
    if len(set(orgs)) == 1:
        organization = orgs[0]
    if len(set(projects)) == 1:
        project = projects[0]
    booked = []
    for (course, register), config in courses.items():
        try:
            url = config.get(SIGNUPSHEET_URL_PATH)
        except KeyError as err:
            logging.warning(
                f"Can't find sign-up sheet URL for {course} in {register}: " f"{err}"
            )
            continue
        if "docs.google.com" in url:
            url = sheets.google_sheet_to_csv_url(url)
        booked += sheets.read_signup_sheet_from_url(url)
    booked = sheets.filter_events_by_date(booked, start, end)

    user_pattern = re.compile(user_regex)
    users = hr.hours_per_TA(booked)
    csvout = csv.writer(sys.stdout, delimiter="\t")
    first_print = True
    for user in users:
        if not user_pattern.match(user):
            continue
        contracts = get_valid_contracts(user)
        if amanuensis and not contracts:
            continue
        elif not amanuensis and contracts:
            continue
        ta_events = summarize_user(user, booked)
        all_prev_events = []

        user_contracts = get_valid_contracts(user)
        for contract in user_contracts:
            contract_events = summarize_user(
                user, sheets.filter_events_by_date(contract["events"], start, end)
            )
            all_prev_events += contract_events
        timesheets_dir = pathlib.Path(typerconf.get(TIMESHEETS_DIR_PATH))
        for timesheet_file in timesheets_dir.glob(f"{user}.*.json"):
            try:
                with open(timesheet_file) as infile:
                    timesheet_data = json.load(infile)
            except Exception as err:
                logging.warning(f"Can't read {timesheet_file}, skipping: {err}")
                continue

            all_prev_events += timesheet_data["added_events"]
            all_prev_events = remove_events(
                all_prev_events, timesheet_data["removed_events"]
            )

        added_events = remove_events(ta_events, all_prev_events)
        removed_events = remove_events(all_prev_events, ta_events)
        salary_diff = salary_difference(added_events, removed_events)

        if (diff and salary_diff != 0) or not diff:
            if draft:
                if not (added_events or removed_events):
                    continue

                if first_print:
                    first_print = False
                else:
                    csvout.writerow([])
                    csvout.writerow([])

                if added_events or removed_events:
                    csvout.writerow([user])

                if added_events and removed_events:
                    csvout.writerow(["Added events"])

                for event in added_events:
                    csvout.writerow(event.values())

                if removed_events:
                    csvout.writerow([])
                    csvout.writerow(["Removed events"])

                for event in removed_events:
                    event["timmar"] = -event["timmar"]
                    event["omr_tid"] = -event["omr_tid"]
                    event["belopp"] = -event["belopp"]
                    csvout.writerow(event.values())
            else:
                if not added_events and not removed_events:
                    logging.warning(f"No events for {user}, skipping.")
                    continue

                user_obj = user
                try:
                    user_obj = get_canvas_user(user, course_regex)
                except Exception as err:
                    logging.warning(f"Can't look up {user} in Canvas: {err}")
                else:
                    try:
                        email = user_obj.email
                        user_obj = get_ladok_user(user_obj)
                        user_obj.email = email
                    except Exception as err:
                        logging.warning(
                            f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                        )
                        pass
                try:
                    personnummer = user_obj.personnummer
                    name = f"{user_obj.first_name} {user_obj.last_name}"
                except AttributeError as err:
                    logging.warning(f"can't access {user}'s LADOK data: {err}")
                    personnummer = "-"
                    name = str(user_obj)

                output_filename = f"timesheet-{user}.xlsx"

                timesheet.make_xlsx(
                    personnummer,
                    name,
                    f"{user}@kth.se" if not "@" in user else user,
                    added_events,
                    removed_events=removed_events,
                    course_leader=(course_responsible, course_responsible_email),
                    HoD=manager,
                    org=organization,
                    project=project,
                    course_leader_signature=(
                        course_responsible_signature if sign else None
                    ),
                    output=output_filename,
                )

        if store and not draft:
            timesheets_dir = pathlib.Path(typerconf.get(TIMESHEETS_DIR_PATH))
            filename = f"{user}.{datetime.datetime.now().isoformat()}.json"
            with open(timesheets_dir / filename, "w") as outfile:
                json.dump(
                    {
                        "user": user,
                        "added_events": added_events,
                        "removed_events": removed_events,
                    },
                    outfile,
                    indent=2,
                )


@timesheets.command(name="show")
def cli_show_timesheets(
    user_regex: Annotated[str, user_regex_arg] = ".*",
    reverse: Annotated[bool, reverse_opt] = False,
    all: Annotated[bool, all_opt] = False,
    delimiter: Annotated[str, delimiter_opt] = "\t",
    date_regex: Annotated[str, date_regex_opt] = None,
):
    """
    Shows stored time sheets for TAs.
    """
    timesheets_dir = pathlib.Path(typerconf.get(TIMESHEETS_DIR_PATH))

    user_pattern = re.compile(user_regex)
    if date_regex:
        date_pattern = re.compile(date_regex)
    printed_users = set()
    csvout = csv.writer(sys.stdout, delimiter=delimiter)
    first_print = True
    if not all:
        reverse = True

    timesheets = sorted(
        timesheets_dir.glob(f"*.json"), key=lambda x: x.name, reverse=reverse
    )
    for timesheet in timesheets:
        username = timesheet.name.split(".")[0]
        if not user_pattern.match(username):
            continue
        if date_regex and not date_pattern.match(timesheet.name.split(".")[1]):
            continue
        if username in printed_users and not all:
            continue
        else:
            printed_users.add(username)
        if first_print:
            first_print = False
        else:
            csvout.writerow([])
            csvout.writerow([])

        csvout.writerow([timesheet.name])

        with open(timesheet) as infile:
            timesheet_data = json.load(infile)

        added_events = timesheet_data["added_events"]
        removed_events = timesheet_data["removed_events"]

        if added_events and removed_events:
            csvout.writerow(["Added events"])

        for event in added_events:
            csvout.writerow(event.values())

        if removed_events:
            csvout.writerow([])
            csvout.writerow(["Removed events"])

        for event in removed_events:
            csvout.writerow(event.values())
