import arrow
import datetime
from nytid.signup import sheets
from nytid.signup.sheets import SIGNUP_SHEET_HEADER


def time_for_event(event, amanuensis=False):
    """
    Input: an event of type ics.event.Event and an optional bool amanuensis
    specifying whether the computation is for an amanuensis or not.

    Output: Returns a datetime.timedelta corresponding to the time including prep
    time for the event.
    """
    return add_prep_time(
        round_time(event.end - event.begin), event.name, event.begin, amanuensis
    )


def round_time(time):
    """
    Input: A datetime.timedelta object time.

    Output: The time object rounded according to KTH rules. Currently round up to
    nearest quarter of an hour.
    """
    HOUR = 60 * 60
    QUARTER = 15 * 60

    total_seconds = time.total_seconds()
    full_hours = (total_seconds // HOUR) * HOUR
    part_hour = total_seconds % HOUR

    if part_hour > 3 * QUARTER:
        return datetime.timedelta(seconds=full_hours + HOUR)
    elif part_hour > 2 * QUARTER:
        return datetime.timedelta(seconds=full_hours + 3 * QUARTER)
    elif part_hour > QUARTER:
        return datetime.timedelta(seconds=full_hours + 2 * QUARTER)
    elif part_hour > 0:
        return datetime.timedelta(seconds=full_hours + QUARTER)

    return datetime.timedelta(seconds=full_hours)


def add_prep_time(time, event_type, date=datetime.date.today(), amanuensis=False):
    """
    Input:
    - a datetime.timedelta object time,
    - a string containing the title of the event,
    - an optional date (datetime or arrow object) indicating the date of the
      event. If no date is given, today's date is assumed, meaning the latest
      prep-time policy will be used.
    - an optional bool indicating amanuensis employment or hourly.

    Output: the time object rounded according to KTH rules.
    """
    time *= prep_factor(event_type, date=date, amanuensis=amanuensis)
    return round_time(time)


def prep_factor(event_type, date, amanuensis):
    """
    Computes the prep time factor for the event type and date.
    This should implement the rules found at

      https://www.kth.se/social/group/tcs-teaching/page/assistenter/.

    Input:
    - event_type: a string containing the type of event, e.g. "exercise",
      "seminar", "laboration", etc.
    - date: a datetime.date or arrow.Arrow object indicating the date of the
      event.
    - amanuensis: a bool indicating whether the event is for an amanuensis or
      hourly.
    """
    if isinstance(date, arrow.Arrow):
        date = date.datetime
    if isinstance(date, datetime.datetime):
        date = date.date()

    event_type = event_type.casefold()

    if "övning" in event_type or "exercise" in event_type:
        return 2

    tutoring = ["laboration", "seminar", "redovisning", "presentation"]

    if date < datetime.date(2023, 1, 1) or (
        date < datetime.date(2022, 10, 1) and not amanuensis
    ):
        if check_substrings(tutoring, event_type):
            return 1.33
    else:
        if check_substrings(tutoring, event_type):
            if "online" in event_type or amanuensis:
                return 1.5
            return 1.8

    return 1


def check_substrings(substrings, string):
    """
    Check if any of the substrings (list) is a substring of string.
    Return bool.
    """
    for substring in substrings:
        if substring in string:
            return True

    return False


def hours_per_student(csv_rows, round_time=round_time):
    """
    Input: The schedule as rows of CSV data as from csv.reader.

    Output: A dictionary mapping event type to the total number of hours per
    student.
    """

    start_index = SIGNUP_SHEET_HEADER.index("Start")
    end_index = SIGNUP_SHEET_HEADER.index("End")
    event_index = SIGNUP_SHEET_HEADER.index("Event")

    event_hours = dict()

    for row in csv_rows:
        time = round_time(
            arrow.get(row[end_index], "YYYY-MM-DD HH:mm")
            - arrow.get(row[start_index], "YYYY-MM-DD HH:mm")
        )
        event_type = row[event_index]

        if event_type not in event_hours:
            event_hours[event_type] = time
        else:
            event_hours[event_type] += time

    return event_hours


def hours_per_TA(csv_rows, add_prep_time=add_prep_time, round_time=round_time):
    """
    Input:
    - Rows of CSV data as from csv.reader.
    - add_prep_time allows using a different function for adding prep time than
      the default.
    - round_time allows using a different function for rounding that the default.

    Output: a dictionary mapping a TA to the number of hours they signed up for
    (not counting slots where they're in reserve position) in the sign-up sheet,
    {TA: hours}. The hours as datetime.timedelta objects.
    """
    TA_hours = {}

    start_index = SIGNUP_SHEET_HEADER.index("Start")
    end_index = SIGNUP_SHEET_HEADER.index("End")
    event_index = SIGNUP_SHEET_HEADER.index("Event")

    for row in csv_rows:
        start_date = arrow.get(row[start_index], "YYYY-MM-DD HH:mm")
        time = arrow.get(row[end_index], "YYYY-MM-DD HH:mm") - start_date

        time = round_time(time)
        time = add_prep_time(time, row[event_index], start_date)

        booked, _ = sheets.get_booked_TAs_from_csv(row)

        for assistant in booked:
            if assistant in TA_hours:
                TA_hours[assistant] += time
            else:
                TA_hours[assistant] = time

    return TA_hours


def total_hours(csv_rows, add_prep_time=add_prep_time, round_time=round_time):
    """
    Input:
    - Rows of CSV data as from csv.reader.
    - add_prep_time allows using a different function for adding prep time than
      the default.
    - round_time allows using a different function for rounding that the default.

    Output: Total number of hours spent on the course, as a datetime.timedelta
    object.
    """
    total = datetime.timedelta(0)
    TA_hours = hours_per_TA(csv_rows, add_prep_time, round_time)

    for _, hours in TA_hours.items():
        total += hours

    return total


def max_hours(csv_rows, add_prep_time=add_prep_time, round_time=round_time):
    """
    Input:
    - takes the rows of CSV as output from csv.reader.
    - add_prep_time allows using a different function for adding prep time than
      the default.
    - round_time allows using a different function for rounding that the default.

    Output: returns the maximum number of hours (using maximum TAs needed), as a
    detetime.timedelta object.
    """
    start_index = SIGNUP_SHEET_HEADER.index("Start")
    end_index = SIGNUP_SHEET_HEADER.index("End")
    event_index = SIGNUP_SHEET_HEADER.index("Event")
    needed_TAs_index = SIGNUP_SHEET_HEADER.index("#Needed TAs")

    max_hours = datetime.timedelta()

    for row in csv_rows:
        start_date = arrow.get(row[start_index], "YYYY-MM-DD HH:mm")
        time = arrow.get(row[end_index], "YYYY-MM-DD HH:mm") - start_date

        time = round_time(time)
        time = add_prep_time(time, row[event_index], start_date)

        max_num_TAs = int(row[needed_TAs_index])

        max_hours += time * max_num_TAs

    return max_hours


def hours_per_event(csv_rows, round_time=round_time):
    """
    Input:
    - Rows of CSV data as from csv.reader.
    - round_time allows using a different function for rounding that the default.

    Output: a dictionary mapping an event type to the number of hours assigned to
    that type of event in the sign-up sheet, {event: hours}. The hours as
    datetime.timedelta objects.
    """
    event_hours = {}

    start_index = SIGNUP_SHEET_HEADER.index("Start")
    end_index = SIGNUP_SHEET_HEADER.index("End")
    event_index = SIGNUP_SHEET_HEADER.index("Event")

    for row in csv_rows:
        time = round_time(
            arrow.get(row[end_index], "YYYY-MM-DD HH:mm")
            - arrow.get(row[start_index], "YYYY-MM-DD HH:mm")
        )

        if row[event_index] in event_hours:
            event_hours[row[event_index]] += time
        else:
            event_hours[row[event_index]] = time

    return event_hours


def compute_amanuensis_data(
    csv_rows,
    low_percentage=0.05,
    min_days=25,
    add_prep_time=add_prep_time,
    round_time=round_time,
    begin_date=None,
    end_date=None,
):
    """
    Input:
    - csv_rows, the CSV rows as output from csv.reader.
    - low_percentage, the lowest acceptable percentage of an amanuensis
      contract.
    - min_days is the minimum number of days we accept for an amanuensis
      contract.
    - add_prep_time allows using a different function for adding prep time than
      the default.
    - round_time allows using a different function for rounding that the default.
    - begin_date means that we will force this date as a start date, None means
      we will compute the start date.

    Output: a dictionary {TA: (start, end, hours)} mapping the TA username to a
    tuple (start, end, hours) with the start and end time and the total number of
    hours.
    """
    start_index = SIGNUP_SHEET_HEADER.index("Start")
    end_index = SIGNUP_SHEET_HEADER.index("End")
    event_index = SIGNUP_SHEET_HEADER.index("Event")
    needed_TAs_index = SIGNUP_SHEET_HEADER.index("#Needed TAs")

    amanuensis_prep_time = lambda time, event_type, date: add_prep_time(
        time, event_type, date, amanuensis=True
    )

    ta_hours = hours_per_TA(csv_rows, amanuensis_prep_time, round_time)
    ta_data = {}

    for ta in ta_hours.keys():
        earliest_date = arrow.get(csv_rows[0][start_index], "YYYY-MM-DD")
        latest_date = arrow.get(csv_rows[0][end_index], "YYYY-MM-DD")

        for row in csv_rows:
            start_date = arrow.get(row[start_index], "YYYY-MM-DD")
            end_date = arrow.get(row[end_index], "YYYY-MM-DD")

            if start_date < earliest_date:
                earliest_date = start_date
            if end_date > latest_date:
                latest_date = end_date

        hours = ta_hours[ta].total_seconds() / 60 / 60

        july = arrow.get(earliest_date.year, 7, 1)

        if earliest_date < july:
            semester_start = arrow.get(earliest_date.year, 1, 1)
            semester_end = arrow.get(earliest_date.year, 6, 30)
        else:
            semester_start = arrow.get(earliest_date.year, 8, 1)
            semester_end = arrow.get(earliest_date.year + 1, 1, 31)

        earliest_month = arrow.get(earliest_date.year, earliest_date.month, 1)
        latest_month = arrow.get(latest_date.year, latest_date.month, 1).shift(
            months=1, seconds=-1
        )

        if begin_date:
            semester_start = earliest_date = earliest_month = begin_date
        if end_date:
            semester_end = latest_date = latest_month = end_date

        if latest_date > semester_end:
            semester_end = latest_month

        if compute_percentage(semester_start, semester_end, hours) >= low_percentage:
            earliest_date = semester_start
            latest_date = semester_end
        elif compute_percentage(semester_start, latest_month, hours) >= low_percentage:
            earliest_date = earliest_month
            latest_date = latest_month
        elif compute_percentage(earliest_month, semester_end, hours) >= low_percentage:
            earliest_date = earliest_month
            latest_date = latest_month
        elif compute_percentage(earliest_month, latest_month, hours) >= low_percentage:
            earliest_date = earliest_month
            latest_date = latest_month
        elif compute_percentage(earliest_date, latest_month, hours) >= low_percentage:
            latest_date = latest_month
        elif compute_percentage(earliest_date, latest_date, hours) >= low_percentage:
            pass
        else:
            continue  # skip to next TA

        if latest_date - earliest_date < datetime.timedelta(days=min_days):
            continue

        ta_data[ta] = (earliest_date, latest_date, hours)

    return ta_data


def compute_percentage(start, end, hours):
    """
    Input: start and end as arrow.arrow.Arrow or datetime.date objects,
      hours as a float.

    Output: a float in the interval [0, 1], which is the percentage of full time.
    """
    days = (end - start).total_seconds() / 60 / 60 / 24
    return (hours / 1600) * (365 / days)
