import os
import pathlib


class StorageRoot:
    """
    Abstracts the storage system. This allows us to use paths relative to a root.
    This of this as a simple chroot jail (just not for security).
    """

    def __init__(self, path: pathlib.Path):
        """
        Uses `path` as the root. All files opened are in subdirectories of `path`.
        """
        self.__path = pathlib.Path(path)
        self.__dir_fd = None

    @property
    def path(self) -> pathlib.Path:
        """
        `pathlib.Path` representation of the storage root.
        """
        return pathlib.Path(self.__path)

    def open(self, *args, **kwargs):
        """
        Takes the same arguments as built-in `open`.
        """
        return open(*args, **kwargs, opener=self.__opener)

    def __opener(self, path, flags):
        """The opener, used internally"""
        if not self.__dir_fd:
            self.open_dir()
        return os.open(path, flags, dir_fd=self.__dir_fd)

    def open_dir(self):
        """
        Open the storage root directory. Note that this is done automatically when
        opening a file using the `open` method.
        """
        try:
            self.__dir_fd = os.open(self.path, os.O_RDONLY)
        except FileNotFoundError:
            os.makedirs(self.path)
            self.__dir_fd = os.open(self.path, os.O_RDONLY)

    def close(self):
        """Close the storage root"""
        os.close(self.__dir_fd)
        self.__dir_fd = None

    def __enter__(self):
        """Enter of with statement"""
        self.open_dir()
        return self

    def __exit__(self, *args):
        """Exit of with statement"""
        self.close()

    def grant_access(user):
        """
        This method is not implemented for `nytid.cli.storage.StorageRoot`.
        """
        raise NotImplementedError

    def revoke_access(user):
        """
        This method is not implemented for `nytid.cli.storage.StorageRoot`.
        """
        raise NotImplementedError


def open_root(*args, **kwargs) -> StorageRoot:
    """
    Takes arguments (`*args` and `**kwargs`), determines which submodule is the
    best and passes the arguments onto the `StorageRoot` constructor of that
    module.
    """
    if args[0].startswith("/afs"):
        import nytid.storage.afs as storage_module
    if args[0].endswith(".git"):
        import nytid.storage.git as storage_module
    try:
        root = storage_module.StorageRoot(*args, **kwargs)
    except NameError:
        root = StorageRoot(*args, **kwargs)

    return root
