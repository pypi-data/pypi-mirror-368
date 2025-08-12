from nytid import storage
import sys
import subprocess

VALID_PERMISSIONS = "rlidwka"


class AFSfsError(Exception):
    pass


class AFSACLError(Exception):
    pass


class AFSPermissionError(Exception):
    pass


class AFSGroupError(Exception):
    pass


def set_acl(path, user_or_group, permissions):
    """
    Sets the access control list for directory `path` for user or group
    `user_or_group` to permissions in `permissions`.

    `permissions` is a list of one-letter permissions. (A string of letters and a
    list of one-letter strings are equivalent.)
    """
    valid_permissions = ""
    invalid_permissions = ""

    for permission in permissions:
        if permission in VALID_PERMISSIONS:
            valid_permissions += permission
        else:
            invalid_permissions += permission

    if invalid_permissions:
        raise AFSPermissionError(f"{invalid_permissions} are invalid permissions.")
    cmd = ["fs", "sa", path, user_or_group, permissions]
    try:
        fssa = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        errmsg = str(err.stderr, encoding=sys.getdefaultencoding())
        raise AFSACLError(
            f"Error while setting AFS ACL: " f"`{err.cmd}` resulted in '{errmsg}'"
        )


def revoke_all(path, user_or_group):
    """
    Revokes all access to `path` for `user_or_group`.
    """
    set_acl(path, user_or_group, "")


def grant_dropbox(path, user_or_group):
    """
    Lets `user_or_group` use `path` as a dropbox, i.e. can insert files, but not
    list, read or modify them.
    """
    set_acl(path, user_or_group, "i")


def grant_lookup(path, user_or_group):
    """
    Lets `user_or_group` list/lookup files in `path`.
    """
    set_acl(path, user_or_group, "l")


def grant_reader(path, user_or_group):
    """
    Lets `user_or_group` list, read and lock files in `path`.
    """
    set_acl(path, user_or_group, "rlk")


def grant_writer(path, user_or_group):
    """
    Lets `user_or_group` list, read, lock, write, delete files in `path`.
    """
    set_acl(path, user_or_group, "rlidwk")


def grant_admin(path, user_or_group):
    """
    Lets `user_or_group` do anything to `path` and files in it.
    """
    set_acl(path, user_or_group, VALID_PERMISSIONS)


def get_acl(path):
    """
    Returns a dictionary containing the access control list:
    users or groups as key, permissions as value.
    """
    acl = {}
    cmd = ["fs", "la", path]
    try:
        fsla = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        errmsg = str(err.stderr, encoding=sys.getdefaultencoding())
        raise AFSfsError(f"`fs la {path}` returned with error: {errmsg}")
    lines = str(fsla.stdout, encoding=sys.getdefaultencoding()).split("\n")
    pos_permissions = {}
    neg_permissions = {}

    while lines:
        line = lines.pop(0)
        if line == "Normal rights:":
            pos_permissions.update(pop_permissions(lines))
        elif line == "Negative rights:":
            neg_permissions.update(pop_permissions(lines))

    for key, value in pos_permissions.items():
        try:
            acl[key] = (value, neg_permissions[key])
        except KeyError:
            acl[key] = (value, None)

    for key, value in neg_permissions.items():
        if key in acl:
            continue
        else:
            acl[key] = (None, value)
    return acl


def pop_permissions(lines):
    """
    Pops all indented lines from front in `lines`. Returns dictionary containing
    username (or group) as keys, permissions as values.
    """
    acl = {}

    while lines:
        if not lines[0].startswith("  "):
            return acl

        user_or_group, permissions = lines.pop(0).split()

        acl[user_or_group] = permissions

    return acl


def create_group(group_name):
    """
    Creates a group in AFS named `group_name`.
    """
    cmd = ["pts", "creategroup", group_name]
    try:
        pts = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        pts_lines = str(err.stderr, encoding=sys.getdefaultencoding()).split("\n")
        raise AFSGroupError(f"`{' '.join(cmd)}` returned an error: {pts_lines[0]}")
    else:
        pts_lines = str(pts.stdout, encoding=sys.getdefaultencoding()).split("\n")


def add_user_to_group(username, group_name):
    """
    Adds user `username` to the AFS group `group_name`.
    """
    cmd = ["pts", "adduser", username, group_name]
    try:
        pts = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        pts_lines = str(err.stderr, encoding=sys.getdefaultencoding()).split("\n")
        raise AFSGroupError(f"`{' '.join(cmd)}` returned an error: {pts_lines[0]}")
    else:
        pts_lines = str(pts.stdout, encoding=sys.getdefaultencoding()).split("\n")


def list_users_in_group(group_name):
    """
    Lists the members of the group `group_name`.
    """
    cmd = ["pts", "membership", group_name]
    try:
        pts = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        pts_lines = str(err.stderr, encoding=sys.getdefaultencoding()).split("\n")
        raise AFSGroupError(f"`{' '.join(cmd)}` returned an error: {pts_lines[0]}")
    else:
        pts_lines = str(pts.stdout, encoding=sys.getdefaultencoding()).split("\n")

    first_line = pts_lines.pop(0)
    if first_line.startswith("pts: "):
        raise AFSGroupError(f"`{' '.join(cmd)}` returned an error: {first_line}")

    return [user.strip() for user in pts_lines]


def remove_user_from_group(username, group_name):
    """
    Removes user `username` from the AFS group `group_name`.
    """
    cmd = ["pts", "removeuser", username, group_name]
    try:
        pts = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        pts_lines = str(err.stderr, encoding=sys.getdefaultencoding()).split("\n")
        raise AFSGroupError(f"`{' '.join(cmd)}` returned an error: {pts_lines[0]}")
    else:
        pts_lines = str(pts.stdout, encoding=sys.getdefaultencoding()).split("\n")


def delete_group(group_name):
    """
    Deletes the AFS group `group_name`.
    """
    cmd = ["pts", "delete", group_name]
    try:
        pts = subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        pts_lines = str(err.stderr, encoding=sys.getdefaultencoding()).split("\n")
        raise AFSGroupError(f"`{' '.join(cmd)}` returned an error: {pts_lines[0]}")
    else:
        pts_lines = str(pts.stdout, encoding=sys.getdefaultencoding()).split("\n")
    pts_lines = str(pts.stderr, encoding=sys.getdefaultencoding()).split("\n")
    if pts_lines[0].startswith("pts: "):
        raise AFSGroupError(f"`{' '.join(cmd)}` returned an error: {pts_lines[0]}")


class StorageRoot(storage.StorageRoot):
    """
    Manages a storage root in the AFS system.
    """

    def revoke_access(self, user_or_group):
        """
        Revokes access to storage root for a user or group. Returns nothing.
        """
        revoke_all(self.path, user_or_group)

    def grant_access(self, user_or_group, permissions):
        """
        Sets `permissions` as access rights for `user_or_group`.

        `permissions` is a substring of the AFS permissions: "rlidwka".

        l -- Lookup: Note that a user needs Lookup to a parent directory
                     as well as access to a subdirectory to access files in
                     the subdirectory.
        r -- Read:   Allows user to read or copy any file in the directory.
        w -- Write:  Allows user to modify any existing file in the directory.
        k -- Lock:   Allows user to flock a file.
        i -- Insert: Allows user to add new files and create new subdirectories.
        d -- Delete: Allows user to remove files and empty subdirectories.
        a -- Admin:  Allows user to change the ACL for a directory.
        """
        set_acl(self.path, user_or_group, permissions)
