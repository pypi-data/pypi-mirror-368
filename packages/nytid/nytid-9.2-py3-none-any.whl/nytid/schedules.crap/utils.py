import arrow
import csv
import datetime
import ics.attendee
import ics.event
import nytid.schedules
import re
import requests

SIGNUP_SHEET_HEADER = [
  "Event", "Start", "End", "#Rooms",
  "#Needed TAs"
]
class EventFromCSV(ics.event.Event):
  """A class to create an ics.event.Event from an event in CSV format"""
  def __init__(self, csv_row):
    """
    Input: a row from a calendar in CSV format (e.g. the sign-up sheet).
    """
    attribute_map = {
      SIGNUP_SHEET_HEADER.index("Event"): "name",
      SIGNUP_SHEET_HEADER.index("Start"): "begin",
      SIGNUP_SHEET_HEADER.index("End"): "end",
      SIGNUP_SHEET_HEADER.index("#Rooms"): "description",
      SIGNUP_SHEET_HEADER.index("#Needed TAs"): "description"
    }
    for idx in range(len(SIGNUP_SHEET_HEADER), len(csv_row)):
      attribute_map[idx] = "attendees"

    kwargs = dict()

    for column, attribute in attribute_map.items():
      try:
        value = csv_row[column]

        if attribute == "description":
          if attribute in kwargs:
            value = kwargs[attribute] + "\n" + value
        elif attribute == "attendees":
          if not value:
            continue

          value = ics.attendee.Attendee(f"{value}@kth.se")

          if attribute not in kwargs:
            value = [value]
          else:
            value = kwargs[attribute] + [value]
        elif attribute in ["begin", "end"]:
          value = arrow.get(value, tzinfo="local")

        kwargs[attribute] = value
      except AttributeError:
        pass

    super().__init__(**kwargs)
def needed_TAs(event):
  """
  Takes an event and returns the number of TAs needed
  """
  num_groups = event.description.split().count("grupp")
  if num_groups == 0:
    num_groups = event.description.split().count("group")

  num_rooms = len(event.location.split(","))

  num_TAs = max(num_rooms, num_groups)

  if "laboration" in event.name or "Laboration" in event.name:
    num_TAs = round(num_TAs * 1.5)

  return num_TAs

def event_filter(events):
  """
  Takes a list of events, returns a filtered list of events (generator).
  The events to include are the teaching events.
  """
  events_whitelist = [
    "Datorlaboration", "Laboration",
    "Övning",
    "Seminarium", "Redovisning", "Examination",
    "Föreläsning"
  ]

  for event in events:
    for event_type in events_whitelist:
      if event_type in event.name:
        yield event
        break
  
def generate_signup_sheet(course, url,
  needed_TAs=needed_TAs, event_filter=event_filter):
  """
  Input:
  - course is a string containing the file name used for output.
  - url is the URL to the ICS-formatted calendar.
  - needed_TAs is a function computing the number of needed TAs based on the 
    event. The default is the needed_TAs function in this module,
  - event_filter is a function that filters events, takes a list of events as 
    argument and returns a filtered list.

  Output:
  Returns nothing. Writes output to {course}.csv.
  """
  with open(f"{course}.csv", "w") as out:
    csvout = csv.writer(out)
    calendar = nytid.schedules.read_calendar(url)

    max_num_TAs = 0
    rows = []

    for event in event_filter(calendar.timeline):
      num_TAs = needed_TAs(event)

      if num_TAs > max_num_TAs:
        max_num_TAs = num_TAs

      rows.append([
        event.name,
        event.begin.to("local").format("YYYY-MM-DD HH:mm"),
        event.end.to("local").format("YYYY-MM-DD HH:mm"),
        len(event.location.split(",")),
        num_TAs
      ])

    csvout.writerow(SIGNUP_SHEET_HEADER +
      [f"TA username" for n in range(max_num_TAs)] +
        ["..."])

    csvout.writerows(rows)
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

  url = share_url[:match.start()]
  return url + "/export?format=csv"
def get_TAs_from_csv(csv_row):
  """
  Input: takes a CSV data row as from a csv.reader.

  Output: returns the list of signed TAs. Ensures casefold for TA IDs.
  """
  return list(
    map(lambda x: x.casefold(),
      filter(lambda x: x.strip(),
        csv_row[len(SIGNUP_SHEET_HEADER):]))
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
  return list(
    filter(lambda x: ta_id.casefold() in get_TAs_from_csv(x),
      csv_rows))
def filter_events_by_title(event_title, csv_rows):
  """
  Input: event_title is the substring to match the event title against;
  csv_rows is a list of CSV rows, as from csv.reader.

  Output: a list of CSV rows containing only the rows with an event title 
  having event_title as substring.
  """
  return list(filter(
    lambda x: event_title in x[SIGNUP_SHEET_HEADER.index("Event")],
    csv_rows))
def time_for_event(event, amanuensis=False):
  """
  Input: an event of type ics.event.Event and an optional bool amanuensis 
  specifying whether the computation is for an amanuensis or not.

  Output: Returns a datetime.timedelta corresponding to the time including prep 
  time for the event.
  """
  return add_prep_time(
    round_time(event.end-event.begin), event.name, event.begin, amanuensis)
def round_time(time):
  """
  Input: A datetime.timedelta object time.

  Output: The time object rounded according to KTH rules. Currently round up to 
  nearest quarter of an hour.
  """
  HOUR = 60*60
  QUARTER = 15*60

  total_seconds = time.total_seconds()
  full_hours = (total_seconds // HOUR) * HOUR
  part_hour = total_seconds % HOUR

  if part_hour > 3*QUARTER:
    return datetime.timedelta(seconds=full_hours+HOUR)
  elif part_hour > 2*QUARTER:
    return datetime.timedelta(seconds=full_hours+3*QUARTER)
  elif part_hour > QUARTER:
    return datetime.timedelta(seconds=full_hours+2*QUARTER)
  elif part_hour > 0:
    return datetime.timedelta(seconds=full_hours+QUARTER)

  return datetime.timedelta(seconds=full_hours)
def add_prep_time(time, event_type,
  date=datetime.date.today(), amanuensis=False):
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
  if isinstance(date, arrow.Arrow):
    date = date.datetime
  if isinstance(date, datetime.datetime):
    date = date.date()

  if date > datetime.date(2023, 1, 1) or \
    (date > datetime.date(2022, 10, 1) and not amanuensis):
    if check_substrings(
          ["laboration", "seminarium", "redovisning"],
          event_type.casefold()):
      time *= 1.5
    elif "övning" in event_type.casefold():
      time *= 2
  else:
    if check_substrings(
          ["laboration", "seminarium", "redovisning"],
          event_type.casefold()):
      time *= 1.33
    elif "övning" in event_type.casefold():
      time *= 2

  return round_time(time)

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
    time = round_time(arrow.get(row[end_index], "YYYY-MM-DD HH:mm") - \
      arrow.get(row[start_index], "YYYY-MM-DD HH:mm"))
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

    booked, _ = get_booked_TAs_from_csv(row)

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
    time = round_time(arrow.get(row[end_index], "YYYY-MM-DD HH:mm") - \
      arrow.get(row[start_index], "YYYY-MM-DD HH:mm"))

    if row[event_index] in event_hours:
      event_hours[row[event_index]] += time
    else:
      event_hours[row[event_index]] = time

  return event_hours
def compute_amanuensis_data(csv_rows, low_percentage=0.04, min_days=25,
    add_prep_time=add_prep_time, round_time=round_time, begin_date=None):
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

  ta_hours = hours_per_TA(csv_rows, add_prep_time, round_time)
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

    hours = ta_hours[ta].total_seconds()/60/60

    july = arrow.get(earliest_date.year, 7, 1)

    if earliest_date < july:
      semester_start = arrow.get(earliest_date.year, 1, 1)
      semester_end = arrow.get(earliest_date.year, 6, 30)
    else:
      semester_start = arrow.get(earliest_date.year, 8, 1)
      semester_end = arrow.get(earliest_date.year+1, 1, 31)

    earliest_month = arrow.get(earliest_date.year, earliest_date.month, 1)
    latest_month = arrow.get(
      latest_date.year, latest_date.month, 1).shift(months=1, seconds=-1)

    if begin_date:
      semester_start = earliest_date = earliest_month = begin_date

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
      continue # skip to next TA

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
  days = (end - start).total_seconds()/60/60/24
  return (hours / 1600) * (365 / days)

def main():
  COURSES = {
    "DD1310": 
    "https://cloud.timeedit.net/kth/web/public01/ri.ics?sid=7&p=0.w%2C12.n&objects=453080.10&e=220609&enol=t&ku=29&k=1B9F3AD696BCA5C434C68950EFD376DD",
    "DD1317": 
    "https://cloud.timeedit.net/kth/web/public01/ri.ics?sid=7&p=0.w%2C12.n&objects=455995.10&e=220609&enol=t&ku=29&k=BA4400E3C003685549BC65AD9EAD3DC58E"
  }

  for course, url in COURSES.items():
    generate_signup_sheet(course, url)

if __name__ == "__main__":
    main()
