import enum
import os
import shutil
import zipfile
from pathlib import Path

from .cache_manager import save_cache
from ..ControllerUser import ControllerUser
from ..methods import item_not_found, safe_get_from_dict
from ..path_normalizer import normal_path


class FileManager(ControllerUser):

    def get(self, file_path, alias=None):
        get_file(self.controller, normal_path(file_path), alias)

    def put(self, destination_path):
        put_file(self.controller.data.cache, destination_path)

    def put_source(self, src_alias_or_path, dst_alias_or_path):
        if src_alias_or_path == "":
            # specific action in this case
            return
        put_file(self.controller.data.cache, dst_alias_or_path, src_alias_or_map=src_alias_or_path)

    def get_from_zip(self, zip_path, relative_path, alias=None):
        get_from_zip(self.controller, normal_path(zip_path), relative_path, alias)

    def put_to_zip(self, src_alias_or_path, zip_path, relative_path=None):
        put_to_zip(self.controller, src_alias_or_path, zip_path, relative_path)


def get_file(controller, source: Path, alias=None):
    """Saves a file as the current file or if alias specified saves with alias
        :returns: new file path"""

    destination = FileType.get_destination_from_path(source, controller.cache_data, controller.container, alias)
    remove_resource(destination.path)

    # assign new value to cache data
    destination.map[alias or destination.current_name] = str(destination.path)

    if not (destination := copy_resource(source, destination.path)):
        print("could not execute copy")
        return

    save_cache(controller)
    normal_path(destination).exists() or item_not_found("path", str(destination))


def put_file(cache_data, dest_alias_or_path, src_alias_or_map=None):
    """Copies the current file or alias to a specific destination"""

    if src_alias_or_map:
        # if has 2 params: put SRC in DST
        source = get_alias_or_path(cache_data, src_alias_or_map)
        destination = get_alias_or_path(cache_data, dest_alias_or_path, FileType.dir)
    else:
        # if has 1 param: put DST (put current_file in)
        source = cache_data["current_file_name"]
        destination = get_alias_or_path(cache_data, dest_alias_or_path, FileType.dir)

    source, destination = normal_path(source), normal_path(destination)

    # check on source and destination
    src_not_exists = not source.exists()
    dst_not_exists_and_dir = not (destination.exists() and destination.is_dir())
    if src_not_exists or dst_not_exists_and_dir:
        if src_not_exists:
            print("source does not exist:", source)
        if dst_not_exists_and_dir:
            print("destination does not exist or not a dir:", destination)
        return None

    if not (destination := copy_resource(source, destination)):
        print("could not execute copy")
        return

    print("put: {}\n in: {}".format(str(source), str(destination)))
    normal_path(destination).exists() or item_not_found("path", str(destination))


def get_from_zip(controller, zip_path, zip_relative_path, alias=None):
    cache_data = controller.data.cache
    file_archive = controller.container.file
    zip_archive = controller.container.zip

    unzipped_dir = normal_path(zip_archive).joinpath(normal_path(zip_path).name)
    if not unzip_to(zip_path, unzipped_dir):
        print("could not unzip file")
        return

    file_path = normal_path(os.path.join(unzipped_dir, zip_relative_path))
    copied_file = shutil.copy(file_path, file_archive)

    if alias:
        cache_data["file_map"][alias] = copied_file
    else:
        cache_data["current_file_name"] = copied_file
    save_cache(controller)


def put_to_zip(controller, file_path_or_alias, zip_path, zip_relative_path=None):
    if zip_relative_path:
        destination_zip_path = normal_path(zip_path)
    else:
        path_parts = normal_path(zip_path).parts

        # takes the index of the first element contianing ".zip"
        extension_index = [index for index, item in enumerate(path_parts) if '.zip' in item][0]

        # elements before .zip included
        destination_zip_path = normal_path("\\".join(path_parts[0:extension_index + 1]))
        # elements after .zip
        zip_relative_path = "\\".join(path_parts[extension_index + 1:])

    source = normal_path(get_alias_or_path(controller.data.cache, file_path_or_alias))
    unzipped_path = normal_path(os.path.join(controller.container.zip, destination_zip_path.stem))

    if unzipped_path.exists():
        print("removing existing path for temp unzipping")
        remove_resource(unzipped_path)

    unzip_to(destination_zip_path, unzipped_path)
    copy_file_to_dir_relative(source, unzipped_path, zip_relative_path)
    temp_zip = zip_file(unzipped_path, unzipped_path)

    if normal_path(temp_zip).exists():
        print("overriding the zip file in zip archive", temp_zip)

    # currently tested with file, not dir
    shutil.copy(temp_zip, destination_zip_path.parent)

    print("done!")


class FileType(enum.Enum):
    file = 1,
    dir = 2,

    # maybe extend FileType in another Enum?
    def __init__(self, ordinal):
        self.is_dir = None
        self.current_name = None

        self.container = None
        self.path = None

        self.map = None

    @classmethod
    def get_simple_from_path(cls, file_path):
        if file_path.is_dir():
            return cls.dir
        elif file_path.is_file():
            return cls.file
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for input path")

    def with_current_data(self, source, map_data, container, alias):
        self.is_dir = self == self.dir
        self.current_name = "current_dir_name" if self.is_dir else "current_file_name"
        self.container = container.dir if self.is_dir else container.file
        self.map = map_data[self.name + "_map"] if alias else map_data
        base_path = normal_path(self.container).joinpath(normal_path(source).name)

        def get_name(path: Path):
            """Adds a suffix to paths stem name if file already exists with that name\n
            for example:\n
            if file.txt exists -> file1.txt\n
            if file.txt exists and file1.txt exists -> file2.txt"""
            print("path already exist in file archive", path)
            i = 0
            current_path = path
            while current_path.exists():
                current_path = path.parent.joinpath(path.stem + str(i) + path.suffix)
                i += 1

            return current_path

        self.path = base_path if not base_path.exists() else get_name(base_path)

        return self

    @classmethod
    def get_destination_from_path(cls, source_path: Path, map_data, container, alias):
        """Gets information basing on file type passed as parameter.\n
        Can be used to retrieve the current file or dir."""
        if source_path.is_dir():
            return cls.dir.with_current_data(source_path, map_data, container, alias)
        elif source_path.is_file():
            return cls.file.with_current_data(source_path, map_data, container, alias)
        elif source_path := get_file_with_name_only_from_dir(source_path.parent, source_path.stem):
            return cls.file.with_current_data(source_path, map_data, container, alias)
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for input path")


def get_file_with_name_only_from_dir(parent_dir, file_name):
    """Returns file in a directory with a specific name without extension"""
    children = parent_dir.glob('**/*')
    children_files = [x for x in children if x.is_file()]

    # list(normal_path(parent_dir).iterdir())
    for child in children_files:
        if child.name == file_name:
            return child

        # # if name matches but not the extension
        # if child.stem == file_name
        #     return "something"

    return None


def get_alias_or_path(cache_data, alias_or_path, type_filter: FileType = None):
    file_map, dir_map = cache_data["file_map"], cache_data["dir_map"]

    # check all possible types
    if not type_filter:
        if alias_or_path in file_map: return file_map[alias_or_path] or alias_or_path
        if alias_or_path in dir_map: return dir_map[alias_or_path] or alias_or_path
        return alias_or_path

    # check only one type
    return {
        FileType.dir: safe_get_from_dict(dir_map, alias_or_path) or alias_or_path,
        FileType.file: safe_get_from_dict(file_map, alias_or_path) or alias_or_path
    }.get(type_filter, alias_or_path)  # add other cases (not only plain path)


def zip_file(unzipped_dir_path, destination_path_with_name):
    """Zips file to destination\n
    Currently supports .zip files"""
    shutil.make_archive(destination_path_with_name, 'zip', unzipped_dir_path)
    return "%s.zip" % destination_path_with_name


def unzip_to(zip_path, destination_path):
    """Unzips a file to specific dir"""

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path)

    if normal_path(destination_path).exists():
        return destination_path

    return None


def copy_file_to_dir_relative(src_file_path, dest_dir_path, relative_path):
    """Put something here"""

    def safe_create_path(base_path, relative_path):
        """create subdirectories route\n
        supported format: a/b/c"""

        # check on relative format
        current_relative_path = ""
        current_sub_dir_path = None

        parts = relative_path.split("/") if "/" in relative_path else relative_path.split("\\")
        for part in parts:
            current_relative_path += part if not current_relative_path else "/" + part
            current_sub_dir_path = normal_path(base_path).joinpath(current_relative_path)
            if not current_sub_dir_path.is_dir():
                os.mkdir(current_sub_dir_path)

        return current_sub_dir_path

    full_path = safe_create_path(dest_dir_path, relative_path)
    shutil.copy(src_file_path, full_path)


def remove_current(current: FileType, controller):
    """Removes current file or dir"""
    if not current.current_name:
        print("there is no current", current.name)
        return

    try:
        if current.is_dir:
            shutil.rmtree(current.path)
        else:
            os.remove(current.path)
    except FileNotFoundError:
        print("could not delete current", "dir" if current.is_dir else "file")

    # cleaning cache property
    controller.data.cache[current.current_name] = ""

    # save new cache state
    save_cache(controller)


def remove_resource(resource):
    # required normal_path

    if not (resource := normal_path(resource)).exists(): return

    is_dir = resource.is_dir()
    try:
        if is_dir:
            shutil.rmtree(resource)
        else:
            os.remove(resource)
    except FileNotFoundError:
        # with dir?
        print("could not delete", "dir" if is_dir else "file", resource)


def copy_resource(source, destination):
    source, destination = normal_path(source), normal_path(destination)
    if destination.exists(): print("destination file already exists")
    try:
        if source.is_dir():
            return safe_copy_dir(source, destination)
        else:
            return shutil.copy(source, destination)
    except FileNotFoundError:
        print("could not copy", FileType.get_simple_from_path(source).name)
        print(str(source))

    return None


def safe_copy_dir(source, destination):
    source, destination = normal_path(source), normal_path(destination)

    if source == destination:
        print("you are copying a path to the same path, this could cause trouble")
        print("aborting..")
        return None

    # source has to be a directory
    if not source.is_dir():
        print("source is not a directory")
        return None

    # if destination path exists clean it
    if destination.exists() and destination.is_dir():
        print("destination file already exists! remothing..")
        shutil.rmtree(destination)

    return shutil.copytree(source, destination)


##### ##### #####
def remove_file_alias(controller, alias):
    remove(controller.data.cache, controller.container.file, alias)


def remove_dir_alias(controller, alias):
    remove(controller.data.cache, controller.container.dir, alias)


def remove(data, container, alias):
    if alias in data[container]:
        del data[container][alias]
