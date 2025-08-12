import logging
import typer
import typerconf
import typing
from typing_extensions import Annotated

import datetime
from nytid.schedules import read_calendar
import csv
import sys

cli = typer.Typer(name="rooms", help="Finding free rooms for courses")

BOOKED_ROOMS_URL = "utils.rooms.url"
INTERESTING_ROOMS = "utils.rooms.interesting_rooms"
DATE_FORMAT = "%Y-%m-%d %H:%M"


def free_rooms(ics_url: str) -> typing.List[typing.Tuple]:
    """
    Given a URL or path to a TimeEdit ICS file (`ics_url`),
    return a CSV (list of tuples) of the free rooms:

    [(start, end, unbooked_rooms), ...]

    where start and end are datetime objects and unbooked_rooms is a set of
    strings.
    """
    results = []
    all_rooms = set(typerconf.get(INTERESTING_ROOMS))

    schedule = read_calendar(ics_url)
    for event in schedule.events:
        start = event.begin.datetime
        end = event.end.datetime

        booked_rooms = event.location.split(",")
        if len(booked_rooms) == 1 and booked_rooms[0].strip() == "":
            booked_rooms = set()
        else:
            booked_rooms = set(map(lambda x: x.strip(), booked_rooms))

        # If there are no booked rooms, we can skip this event.
        if not booked_rooms:
            continue

        unbooked_rooms = all_rooms - booked_rooms
        results.append((start, end, unbooked_rooms))

    time_dict = {}
    for start, end, unbooked_rooms in results:
        if (start, end) in time_dict:
            time_dict[(start, end)] |= unbooked_rooms
        else:
            time_dict[(start, end)] = unbooked_rooms

    results = [
        (start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT), unbooked_rooms)
        for (start, end), unbooked_rooms in time_dict.items()
    ]
    results.sort()
    return results


def booked_rooms(ics_url: str) -> typing.List[typing.Tuple]:
    """
    Given a URL or path to a TimeEdit ICS file ([[ics_url]]),
    return a ics (list of tuples) of the booked rooms:

    [(start, end, booked_rooms), ...]

    where start and end are datetime objects and booked_rooms is a set of
    strings.
    """
    results = []

    schedule = read_calendar(ics_url)
    for event in schedule.events:
        start = event.begin.datetime
        end = event.end.datetime

        booked_rooms = event.location.split(",")
        if len(booked_rooms) == 1 and booked_rooms[0].strip() == "":
            booked_rooms = set()
        else:
            booked_rooms = set(map(lambda x: x.strip(), booked_rooms))

        # If there are no booked rooms, we can skip this event.
        if not booked_rooms:
            continue

        results.append((start, end, booked_rooms))

    time_dict = {}
    for start, end, unbooked_rooms in results:
        if (start, end) in time_dict:
            time_dict[(start, end)] |= unbooked_rooms
        else:
            time_dict[(start, end)] = unbooked_rooms

    results = [
        (start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT), unbooked_rooms)
        for (start, end), unbooked_rooms in time_dict.items()
    ]
    results.sort()
    return results


delimiter_opt = Annotated[
    str,
    typer.Option(
        "-d", "--delimiter", help="CSV delimiter, default tab.", show_default=False
    ),
]


@cli.command(name="set-url")
def set_url_cmd(
    url: Annotated[
        str,
        typer.Argument(
            help="URL to TimeEdit export, " "ICS format for subscribing.",
            show_default=False,
        ),
    ],
    interesting_rooms: Annotated[
        typing.List[str],
        typer.Argument(
            help="Space-separated list of "
            "rooms in the schedule, e.g.: "
            "D1 D2 D3 D37",
            show_default=False,
        ),
    ],
):
    """
    Search for all the rooms that you're interested in in TimeEdit,
    e.g. D1, D2, D3 and D37.
    Set the relevant time intervals to something future proof: you
    don't want it to be too short, then you have to update the URL
    too often. Use a relative time frame. Get the URL for subscribing,
    ICS format, make sure to select the right time frame.
    """
    try:
        typerconf.set(BOOKED_ROOMS_URL, url)
    except Exception as err:
        logging.error(f"Can't set URL: {err}")
        raise typer.Exit(1)
    try:
        typerconf.set(INTERESTING_ROOMS, interesting_rooms)
    except Exception as err:
        logging.error(f"Can't set interesting rooms: {err}")
        raise typer.Exit(1)


@cli.command(name="unbooked")
def unbooked_cmd(
    delimiter: delimiter_opt = "\t",
):
    """
    Shows date and time and which rooms are free. Note that if a time is NOT in the
    list, it means that all rooms are FREE.
    """
    try:
        rooms_url = typerconf.get(BOOKED_ROOMS_URL)
    except Exception as err:
        logging.error(f"Can't get URL from config: {err}")
        logging.info("Please set it with " "'nytid utils rooms set-url <url>'")
        raise typer.Exit(1)
    try:
        csv_out = csv.writer(sys.stdout, delimiter=delimiter)

        for start, end, rooms in free_rooms(rooms_url):
            csv_out.writerow([start, end, ", ".join(sorted(rooms))])
    except Exception as err:
        logging.error(f"Can't get free rooms: {err}")
        raise typer.Exit(1)


@cli.command(name="booked")
def booked_cmd(
    delimiter: delimiter_opt = "\t",
):
    """
    Shows date and time and which rooms are booked.
    """
    try:
        rooms_url = typerconf.get(BOOKED_ROOMS_URL)
    except Exception as err:
        logging.error(f"Can't get URL from config: {err}")
        logging.info("Please set it with " "'nytid utils rooms set-url <url>'")
        raise typer.Exit(1)
    try:
        csv_out = csv.writer(sys.stdout, delimiter=delimiter)

        for start, end, rooms in booked_rooms(rooms_url):
            csv_out.writerow([start, end, ", ".join(sorted(rooms))])
    except Exception as err:
        logging.error(f"Can't get booked rooms: {err}")
        raise typer.Exit(1)


if __name__ == "__main__":
    cli()
