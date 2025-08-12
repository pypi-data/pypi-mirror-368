import csv
from datetime import datetime
import dateutil.tz
import ics.attendee
import ics.event
import nytid.schedules
import nytid.signup.utils
import os
from nytid.signup import sheets
import re
import requests

SIGNUP_SHEET_HEADER = ["Event", "Start", "End", "Rooms", "#Needed TAs"]
DATETIME_FORMAT = "YYYY-MM-DD HH:mm"
STRPTIME_FORMAT = "%Y-%m-%d %H:%M"


class EventFromCSV(ics.event.Event):
    """A class to create an ics.event.Event from an event in CSV format"""

    def __init__(self, csv_row):
        """
        Input: a row from a calendar in CSV format (e.g. the sign-up sheet).
        """
        kwargs = dict()

        kwargs["name"] = csv_row[SIGNUP_SHEET_HEADER.index("Event")]

        tz = dateutil.tz.tzlocal()

        begin = datetime.strptime(
            csv_row[SIGNUP_SHEET_HEADER.index("Start")], STRPTIME_FORMAT
        )
        begin.replace(tzinfo=tz)
        kwargs["begin"] = begin.astimezone(dateutil.tz.UTC)

        end = datetime.strptime(
            csv_row[SIGNUP_SHEET_HEADER.index("End")], STRPTIME_FORMAT
        )
        end.replace(tzinfo=tz)
        kwargs["end"] = end.astimezone(dateutil.tz.UTC)

        rooms = csv_row[SIGNUP_SHEET_HEADER.index("Rooms")]
        kwargs["location"] = rooms
        needed_TAs = csv_row[SIGNUP_SHEET_HEADER.index("#Needed TAs")]
        kwargs["description"] = f"Needed TAs: {needed_TAs}\n"

        kwargs["attendees"] = [
            ics.attendee.Attendee(f"{user}@kth.se")
            for user in csv_row[len(SIGNUP_SHEET_HEADER) :]
            if user
        ]
        booked, reserves = sheets.get_booked_TAs_from_csv(csv_row)

        kwargs["description"] += "Booked TAs:"
        if booked:
            for username in booked:
                kwargs["description"] += f" {username}"
        else:
            kwargs["description"] += " None"
        kwargs["description"] += "\n"

        if reserves:
            kwargs["description"] += "Reserve TAs:"
            for username in reserves:
                kwargs["description"] += f" {username}"
            kwargs["description"] += "\n"

        super().__init__(**kwargs)


def generate_signup_sheet(
    outfile,
    url,
    needed_TAs=nytid.signup.utils.needed_TAs,
    event_filter=nytid.schedules.event_filter,
    digital_separately=True,
):
    """
    Input:
    - outfile is a string containing the file name used for output.
    - url is the URL to the ICS-formatted calendar.
    - needed_TAs is a function computing the number of needed TAs based on the
      event. The default is the needed_TAs function in this module,
    - event_filter is a function that filters events, takes a list of events as
      argument and returns a filtered list.
    - digital_separately is a bool indicating whether to separate digital
      events from physical ones. If True, the digital events will be separated into
      their own rows in the sign-up sheet. Default is True.

    Output:
    Returns nothing. Writes output to {outfile}.csv.
    """
    try:
        out = open(outfile, "w")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        out = open(outfile, "w")
    with out:
        csvout = csv.writer(out, delimiter="\t")
        calendar = nytid.schedules.read_calendar(url)

        max_num_TAs = 0
        rows = []

        for event in event_filter(calendar.timeline):
            num_TAs = needed_TAs(event)

            if num_TAs > max_num_TAs:
                max_num_TAs = num_TAs

            if digital_separately and "digital" in event.location.casefold():
                TAs_per_room = num_TAs // (event.location.count(",") + 1)
                event.location = re.sub(
                    r"(,\s*digital|digital,\s*|digital)",
                    "",
                    event.location,
                    flags=re.IGNORECASE,
                ).strip()
                if event.location:  # check if digital was the only room
                    rows.append(
                        [*event_to_CSV(event), max(num_TAs - TAs_per_room, 1)]
                    )  # at least one TA
                event.location = "Digital"
                rows.append([*event_to_CSV(event), max(TAs_per_room, 1)])
            else:
                rows.append([*event_to_CSV(event), num_TAs])

        csvout.writerow(
            SIGNUP_SHEET_HEADER + [f"TA username" for n in range(max_num_TAs)] + ["..."]
        )

        csvout.writerows(rows)


def event_to_CSV(event):
    """
    Input: event is an ics.event.Event object.

    Output: a list of strings containing the event's attributes in the order
    specified in SIGNUP_SHEET_HEADER.
    """
    return [
        event.name,
        event.begin.to("local").format(DATETIME_FORMAT),
        event.end.to("local").format(DATETIME_FORMAT),
        event.location,
    ]


def read_signup_sheet_from_file(filename):
    """
    Input: filename is a string containing the file name of the CSV file of the
    sign-up sheet.

    Output: All the rows of the CSV as a Python list.
    """
    with open(filename, "r") as f:
        csvfile = csv.reader(f)
        return list(filter(any, list(csvfile)[1:]))


def read_signup_sheet_from_url(url):
    """
    Input: url is a string containing the URL of the CSV file of the sign-up
    sheet.

    Output: All the rows of the CSV as a Python list.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(response.text)

    response.encoding = response.apparent_encoding
    csvdata = response.text.splitlines()
    return list(filter(any, list(csv.reader(csvdata))[1:]))


def google_sheet_to_csv_url(share_url):
    """
    Input: The share URL of a Google Sheets sheet.

    Output: A URL that downloads (exports) the sheet in CSV format.
    """
    match = re.search("/edit.*$", share_url)
    if not match:
        raise ValueError(f"{share_url} doesn't seem like a Google Sheets URL.")

    url = share_url[: match.start()]
    return url + "/export?format=csv"


def get_TAs_from_csv(csv_row):
    """
    Input: takes a CSV data row as from a csv.reader.

    Output: returns the list of signed TAs. Ensures casefold for TA IDs.
    """
    return list(
        map(
            lambda x: x.casefold().strip(),
            filter(lambda x: x.strip(), csv_row[len(SIGNUP_SHEET_HEADER) :]),
        )
    )


def get_booked_TAs_from_csv(csv_row):
    """
    Input: takes a CSV data row as from a csv.reader.

    Output: returns the list of signed TAs, the first N, where N is the number of
    needed TAs specified in the CSV data.
    """
    TAs = get_TAs_from_csv(csv_row)
    num_needed_TAs = int(csv_row[SIGNUP_SHEET_HEADER.index("#Needed TAs")])

    return TAs[:num_needed_TAs], TAs[num_needed_TAs:]


def filter_events_by_TA(ta_id, csv_rows):
    """
    Input: ta_id is the string to (exactly) match the TAs' identifiers against;
    csv_rows is a list of CSV rows, as from csv.reader.

    Output: a list of CSV rows containing only the rows containing ta_id.
    """
    return list(filter(lambda x: ta_id.casefold() in get_TAs_from_csv(x), csv_rows))


def filter_events_by_title(event_title, csv_rows):
    """
    Input: event_title is the substring to match the event title against;
    csv_rows is a list of CSV rows, as from csv.reader.

    Output: a list of CSV rows containing only the rows with an event title
    having event_title as substring.
    """
    return list(
        filter(lambda x: event_title in x[SIGNUP_SHEET_HEADER.index("Event")], csv_rows)
    )


def filter_events_by_date(csv_rows, start_date=None, end_date=None):
    """
    Input: start_date and end_date are datetime.date objects; csv_rows is a list
    of CSV rows, as from csv.reader.

    Output: a list of CSV rows containing only the rows with an event starting
    between start_date and end_date.
    """
    filtered = csv_rows.copy()

    if start_date:
        filtered = filter(
            lambda x: start_date.date()
            <= datetime.strptime(
                x[SIGNUP_SHEET_HEADER.index("Start")], STRPTIME_FORMAT
            ).date(),
            csv_rows,
        )
    if end_date:
        filtered = filter(
            lambda x: end_date.date()
            > datetime.strptime(
                x[SIGNUP_SHEET_HEADER.index("End")], STRPTIME_FORMAT
            ).date(),
            csv_rows,
        )

    return list(filtered)
