"""The nytid course management module"""

import typerconf

import pathlib
from nytid.courses import registry
from nytid import storage
import typing


def new(
    name: str,
    register: str = None,
    kwdata: dict = None,
    config: typerconf.Config = typerconf,
):
    """
    Creates a new course. It takes the following arguments:

    - `name` (mandatory), which is the human readable nickname of the course. This
      is used to refer to the course with other parts of nytid.

    - `register` is the name of the course register to use. Required if there are
      more than one course register in the config. Default is `None`, which selects
      the only available course register. If more registers, raises exception
      `ValueError`.

    - `kwdata` is a dictionary containing key-value pairs for the course
      configuration. `kwdata` expect the following:

        - `contact` contains the contact information for the course responsible, it can
          be any format, but we recommend "Firstname Lastname <email>". The default
          value is built from values in the main config file:

            - `me.name` contains the name,
            - `me.email` contains the email address.

        - `code`, which is the course code. This is to relate the course to other
          courses through `related_codes`. However, it's not mandatory.

        - `related_codes`, a list of related course codes. Courses with one of these
          course codes can share TAs.

        - `ics` (optional, default None), a URL to an ICS file with the schedule of the
          course. E.g. a URL to a TimeEdit export/subscription.

        - `data_path` is the path to the course's data directory. If not supplied,
          we append `/data` to the course's config directory.


      Any other key--value pairs will simply be written to the course configuration
      as is.

    The default `config` is the default config of the `typerconf` package.
    """
    if not register:
        registers = registry.ls(config=config)

        if len(registers) > 1:
            raise ValueError(f"Must specify a course register: {registers}")
        elif len(registers) < 1:
            raise ValueError(f"There are no course registers in the config.")
        else:
            register = registers[0]

    register_path = registry.get(register, config=config)

    with storage.open_root(f"{register_path}/{name}") as root:
        try:
            with root.open("config.json", "r") as course_conf_file:
                pass
        except FileNotFoundError:
            course_conf = typerconf.Config()
        else:
            raise FileExistsError(
                f"The config for {name} already exists: "
                f"{register_path}/{name}/config.json"
            )

        if not kwdata:
            kwdata = {}

        try:
            contact = kwdata["contact"]
        except KeyError:
            contact = None

        if not contact:
            try:
                contact = config.get("me.name")
            except KeyError:
                contact = ""

            try:
                email = config.get("me.email")
            except KeyError:
                pass
            else:
                if contact:
                    contact += f" <{email}>"
                else:
                    contact = email

        kwdata["contact"] = contact
        if "code" not in kwdata:
            kwdata["code"] = None
        if "related_codes" not in kwdata:
            kwdata["related_codes"] = None
        if "ics" not in kwdata:
            kwdata["ics"] = None
        try:
            data_path = kwdata["data_path"]
        except KeyError:
            data_path = None

        if not data_path:
            data_path = str(root.path / "data")

        kwdata["data_path"] = data_path

        for key, value in kwdata.items():
            course_conf.set(key, value)

        with root.open("config.json", "w") as course_conf_file:
            course_conf.write_config(course_conf_file)


def get_course_config(
    course: str, register: str = None, config: typerconf.Config = typerconf
) -> typerconf.Config:
    """
    Returns a typerconf.Config object for the course's configuration. Writeback
    is enabled meaning that any changes made to the config object will be written
    back to the config file.

    `course` identifies the course in the `register`. If `register` is None,
    search through all registers in the registry, use the first one found
    (undefined in which order duplicates are sorted).

    The default `config` is the default config of the `typerconf` package.
    """
    if register:
        register_map = {register: registry.get(register, config=config)}
    else:
        register_map = {
            register: registry.get(register, config=config)
            for register in registry.ls(config=config)
        }
    try:
        conf_path = get_course_conf_path(course, register_map)
    except KeyError as err:
        raise KeyError(
            f"Couldn't uniquely identify {course} in "
            f"registers {register_map.keys()}: {err}"
        )

    conf = typerconf.Config(conf_file=conf_path)
    return conf


def get_course_conf_path(course, register_map):
    """
    Find the course named `course` among all the courses in the registers found
    in `register_map`, a list of (name, path)-tuples.

    If `course` is not a unique match, it raises a `KeyError`.
    """
    hits_from_register_dirs = []
    conf_path = None

    for register_name, register_path in register_map.items():
        courses = all_courses(register_path)
        matching_courses = list(filter(lambda x: x == course, courses))
        if len(matching_courses) > 0:
            conf_path = f"{register_path}/{course}/config.json"
            hits_from_register_dirs.append(register_name)

    if not conf_path:
        raise KeyError(f"Couldn't find course {course}.")
    elif len(hits_from_register_dirs) > 1:
        raise KeyError(
            f"Course `{course}` found in "
            f"several course registers: {hits_from_register_dirs}."
        )

    return conf_path


def all_courses(register_path: pathlib.Path) -> typing.List[str]:
    """
    Returns a list (generator) of all courses found in `register_path`.
    """
    for file in pathlib.Path(register_path).iterdir():
        if file.is_dir():
            yield file.name


def get_course_data(
    course: str, register: str = None, config: typerconf.Config = typerconf
) -> storage.StorageRoot:
    """
    Returns a StorageRoot object for the data directory of the course `course`.

    If `register` is `None` (default), the first occurence of `course` in all
    registers will be used.
    """
    course_conf = get_course_config(course, register, config)
    return storage.open_root(course_conf.get("data_path"))
