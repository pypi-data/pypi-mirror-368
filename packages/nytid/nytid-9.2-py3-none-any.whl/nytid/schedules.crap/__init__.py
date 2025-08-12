SCHEDULE_API_URL = "https://www.kth.se/social/api/schema/v2"
import arrow.arrow as arrow
import calendar
import dateutil
import ics.event
import ics.icalendar
import requests
import ics.attendee
import locale
import ics.parse
class EventFromKTH(ics.event.Event):
  def __init__(self, json_data):
    """
    Input: json_data is the data returned from the KTH API
    """
    attribute_map = {
      "url": "url",
      "start": "begin",
      "end": "end",
      "type_name": "name",
      "info": "description",
      "group": "attendees",
      "locations": "location"
    }

    kwargs = dict()

    for attribute, kw in attribute_map.items():
      try:
        value = json_data.pop(attribute)

        if attribute == "type_name":
          try:
            value = value[locale.getlocale()[0][:2]]
          except AttributeError:
            value = value["sv"]
        elif attribute == "locations":
          locations = value
          value = ""

          for location in locations:
            if value:
              value += f", {location['name']}"
            else:
              value += location["name"]

        kwargs[kw] = value
      except AttributeError:
        pass

    self.extra = json_to_ics(json_data)

    super().__init__(**kwargs)
def format_header(event):
    """
    Formats the event header, a one-line representation (week, date, time, 
    event title)
    """
    header = f"Week {event.begin.isocalendar()[1]} " + \
            calendar.day_name[event.begin.weekday()] + " " + \
            event.begin.to(dateutil.tz.tzlocal()).format('DD/MM HH:mm')

    header += f" {event.name}"

    return header

def format_event(event):
    """
    Takes event (ics.event.Event) object,
    returns long string representation (header, location, description over 
    several lines)
    """
    header = format_header(event)
    location = event.location
    description = "\n".join(filter(lambda x: "http" not in x,
            event.description.splitlines()))

    return f"{header}\n{location}\n{description}".strip()
def filter_event_description(event_desc, ignore=[
        "http", "grupp", "group", "ID ", "Daniel Bosk"
    ], separator="; "):
    """
    Takes event description event_desc as string,
    returns filtered string with newlines replaced by semicolons.
    Rows of description containing any term in list ignore, will not appear in 
    the returned string.
    The filtered rows of the description are joined again by the string in 
    separator.
    """
    desc_parts = event_desc.splitlines()
    desc_parts_keep = []

    for part in desc_parts:
        found = False
        for term in ignore:
            if term in part:
                found = True
                break

        if not found:
            desc_parts_keep.append(part)

    return separator.join(desc_parts_keep)

def format_event_short(event):
    """Takes event (ics.event.Event) object,
    returns a short string representation (one line)"""
    header = format_header(event)
    description = filter_event_description(event.description)

    return f"{header} {description}".strip()
def course_query(course_code, /, **kwargs):
  """
  Input:
  course_code is the LADOK course code, e.g. DD1301;
  keyword arguments:
  start_term is the LADOK start term, e.g. 2022HT or 2023VT;
  course_round is the LADOK course round code, e.g. 50855;
  start_time and end_time are the dates, e.g. 2022-06-08;
  type specifies which type of entry to fetch, e.g. TEN or all.

  Output:
  """
  path = course_code

  parameter_map = {
    "start_term": "startterm",
    "course_round": "courseroundcode",
    "start_time": "startTime",
    "end_time": "endTime",
    "type": "type"
  }

  parameters = ""

  for kw, param in parameter_map.items():
    try:
      if not parameters:
        parameters += f"{param}={kwargs[kw]}"
      else:
        parameters += f"&{param}={kwargs[kw]}"
    except KeyError:
      pass

  if parameters:
    path += f"?{parameters}"
  response = requests.get(f"{SCHEDULE_API_URL}/course/{path}")
  if response.status_code == 200:
    results = response.json()
  else:
    raise Exception(response.text)

  events = set()
  for event_json in results["entries"]:
    events.add(EventFromKTH(event_json))
  return ics.icalendar.Calendar(events=events)
def json_to_ics(json_data):
  """
  Input:
  json_data being output from json.loads, a directory with lists and values.

  Output:
  List of ics.parse.Container or ics.parse.ContentLine
  """
  items = []

  for kw, value in json_data.items():
    if isinstance(value, dict):
      items.append(ics.parse.Container(kw, json_to_ics(value)))
    else:
      items.append(ics.parse.ContentLine(name=kw, value=value))

  return items
def read_calendar(url):
  """
  Input: url is a string containing the URL to the ICS-formatted calendar.
  Output: an [[ics.icalendar.Calendar]] object.
  """
  response = requests.get(url)
  if response.status_code == 200:
    return ics.icalendar.Calendar(imports=response.text)
  raise Exception(response.text)
