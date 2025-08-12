def needed_TAs(event, group_size=12):
    """
    Takes an event and returns the number of TAs needed
    """
    num_groups = event.description.split().count("grupp")
    if num_groups == 0:
        num_groups = event.description.split().count("group")

    num_rooms = len(event.location.split(","))

    if "laboration" in event.name or "Laboration" in event.name:
        if num_groups:
            num_students = num_groups * group_size
        else:
            num_students = group_size

        num_TAs = round(num_students / 12)
    elif "Övning" in event.name or "Exercise" in event.name or "Tutorial" in event.name:
        num_TAs = num_rooms
    else:
        num_TAs = max(num_rooms, num_groups)

    return num_TAs
