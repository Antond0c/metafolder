import enum
import os
import shutil
import zipfile
from pathlib import Path

from .filesystem_utils import safe_copy_dir, copy_file_to_dir_relative
from .normal import normal_path, item_not_found
from .objects_utils import ControllerUser
from .remove_ops_utils import remove_current_dir, remove_current_file
from .cache_utils import autosave_cache, save_cache


class FileManager(ControllerUser):

    def get(self, file_path):
        get_file(self.controller, file_path)

    def get_alias(self, file_path, alias):
        get_path_alias(self.controller, file_path, alias)

    def put(self, destination_path):
        put_file(destination_path, self.controller.data.cache, self.controller.container.file)

    def put_alias(self, alias, alias_or_destination_path):
        put_file_alias(alias, alias_or_destination_path, self.controller.data.cache)


def get_file(controller, file_path):
    """Saves a file as the current file
        :returns: new file path"""

    file_path = normal_path(file_path)

    if os.path.isdir(file_path):
        remove_current_dir(controller.data.cache, controller.container.dir)
        controller.data.cache["current_dir_name"] = normal_path(file_path).name
        current_dir_path = os.path.join(controller.container.dir, controller.data.cache["current_dir_name"])
        safe_copy_dir(file_path, current_dir_path)
        autosave_cache(controller, True)
        return current_dir_path

    # if the extension is missing
    check = Path(str(file_path) + ".txt")
    if check.is_file():
        file_path = check

    if os.path.isfile(file_path):
        remove_current_file(controller.data.cache, controller.container.file)
        controller.data.cache["current_file_name"] = normal_path(file_path).name
        current_file_path = os.path.join(controller.container.file, controller.data.cache["current_file_name"])
        shutil.copy(file_path, current_file_path)
        autosave_cache(controller, True)
        return current_file_path

    return item_not_found("path", file_path)


def get_path_alias(controller, normal_path, alias):
    normal_path = normal_path(normal_path)
    if normal_path.is_file():
        return get_with_alias(controller, controller.container.file, "file", "file_map", normal_path, alias)
    if normal_path.is_dir():
        return get_with_alias(controller, controller.container.dir, "dir", "dir_map", normal_path, alias)
    return item_not_found("path", normal_path)


def get_with_alias(controller, container_path, file_type, map_type, file_path, alias):
    controller.data.cache[map_type][alias] = os.path.join(container_path, os.path.basename(file_path))
    if file_type == "file":
        shutil.copy(file_path, controller.data.cache[map_type][alias])
    else:
        # create_folder_if_missing()
        safe_copy_dir(file_path, controller.data.cache[map_type][alias])
    # autosave_cache()
    save_cache(controller)
    # print("get {}:{} with alias:{}".format(file_type, file_path, alias))
    return controller.data.cache[map_type][alias]


def put_file(destination_path, cache_data, file_container_path):
    """Copies the current file to a specific destination"""
    # get_current_file_path()
    destination_path = os.path.abspath(destination_path)
    if not os.path.isdir(destination_path): return item_not_found("dir", destination_path)
    file_path = os.path.join(file_container_path, cache_data["current_file_name"])
    shutil.copy(file_path, destination_path)
    # print("put {}:{} with alias:{}".format(file_type.., file_path.., alias..))
    print("put file in {}".format(destination_path))


def put_file_alias(alias, alias_or_destination_path, cache_data):
    """Copies the current file to a specific destination alias or folder path"""

    # todo: alias of folders NOT under archive folder!
    # todo: put file with same name (attach number at the end // overwrite if configuration option)

    class FileType(enum.Enum):
        file = 1
        dir = 2

    class Source():
        def __init__(self, path):
            self.path = path
            self.normalized_path = normal_path(path)

            if self.normalized_path.is_file():
                self.type = FileType.file
            elif self.normalized_path.is_dir():
                self.type = FileType.dir
            else:
                print("error with alias")

    class Destination():
        def __init__(self, path):
            self.path = path
            self.normalized_path = normal_path(path)

    def create_source(input_alias_or_path):
        if input_alias_or_path in list(cache_data["file_map"].keys()):
            return Source(cache_data["file_map"][input_alias_or_path])
        elif input_alias_or_path in list(cache_data["dir_map"].keys()):
            return Source(cache_data["dir_map"][input_alias_or_path])
        else:
            return Source(normal_path(input_alias_or_path))

    def create_destination(input_alias_or_path):
        if alias_or_destination_path in list(cache_data["dir_map"].keys()):
            return Destination(cache_data["dir_map"][alias_or_destination_path])
        else:
            return Destination(alias_or_destination_path)

    def copy(source, destination):
        if source.type == FileType.file:
            shutil.copy(source.path, destination.path)
        elif source.type == FileType.dir:
            # fixme: copies dir (dir_name) to DIR_CONTAINER_PATH/destination_path_name??/source_path_name??
            # safe_copy_dir(source.path, os.path.join(DIR_CONTAINER_PATH, destination.normalized_path.name, source.normalized_path.name))

            # safe_copy_dir(source.path, os.path.join(DIR_CONTAINER_PATH, source.normalized_path.name))
            safe_copy_dir(source.path, destination.path)
        else:
            print("error in copy source to path")

    source = create_source(alias)
    destination = create_destination(alias_or_destination_path)
    copy(source, destination)


### ZIP ARCHIVIATION

def zip_file(destination_path_with_name, unzipped_dir_path):
    shutil.make_archive(destination_path_with_name, 'zip', unzipped_dir_path)
    return "%s.zip" % destination_path_with_name


def unzip_file_to_temp(zip_path, ZIPS_TEMP_CONTAINER_PATH):
    zip_name = Path(zip_path).stem
    zip_temp_dir = os.path.join(ZIPS_TEMP_CONTAINER_PATH, zip_name)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(zip_temp_dir)
    return zip_temp_dir


### ZIP

def get_from_zip(zip_relative_path, zip_path, alias, cache_data, ZIPS_TEMP_CONTAINER_PATH, FILE_CONTAINER_PATH):
    temp_zip_dir = unzip_file_to_temp(zip_path)
    file_path = Path(os.path.join(ZIPS_TEMP_CONTAINER_PATH, temp_zip_dir, zip_relative_path))
    result_file_path = shutil.copy(file_path, FILE_CONTAINER_PATH)
    cache_data["file_map"][alias] = result_file_path
    autosave_cache()


def put_to_zip(file_path_or_alias, zip_path, zip_relative_path, ZIPS_TEMP_CONTAINER_PATH):
    file_path = file_path_or_alias  # convert_to_path(file_path_or_alias)
    unzipped_dir_path = unzip_file_to_temp(zip_path)
    zip_name = Path(zip_path).stem
    copy_file_to_dir_relative(file_path, unzipped_dir_path, zip_relative_path)
    destination_path_with_name = os.path.join(ZIPS_TEMP_CONTAINER_PATH, zip_name)
    new_zipped_file_path = zip_file(destination_path_with_name, unzipped_dir_path)
    original_zip_parent_path = os.path.dirname(file_path)
    shutil.copy(new_zipped_file_path, original_zip_parent_path)  # overwrite always?
    print("done!")
