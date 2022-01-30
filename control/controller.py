import enum
import json
import os
import os.path
import shutil
import sys
import zipfile

from os import listdir
from os.path import isfile, join
from pathlib import Path
from collections.abc import Mapping

try:
    from utils import args_handler
except ImportError:
    from .utils import args_handler


def normal_path(path):
    return Path(os.path.abspath(path))


def find_metafolder_path(starting_app_path, base_parent_dir_name):
    """
    given the running program name search the dir where it's running
    go up in directories till you find the application base folder
    return path
    if cannot find return False
    """
    current_path = normal_path(starting_app_path)
    while current_path != os.path.dirname(current_path):
        if os.path.basename(current_path) == base_parent_dir_name:
            return current_path
        current_path = os.path.dirname(current_path)

    return False


def search_in_folder(root_path, file_name):
    """
    search a file in a dir and its subdirs recursively
    returns:
    if found: file path
    else False
    """
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in [f for f in filenames if f == file_name]:
            return os.path.join(dirpath, filename)

    return False


def context_find(file_name):
    return search_in_folder(METAFOLDER_PATH, file_name)


def execs_context_find(file_name):
    return search_in_folder(EXECUTIONS_CONTAINER_PATH, file_name)


def retrieve(map, key):
    return map[key] if key in map else False


def retrieve_config(name):
    return retrieve(config_data, name)


def retrieve_cache(name):
    return retrieve(cache_data, name)


def apply_json_extension(name):
    return name if str(name).endswith(".json") else "{}.{}".format(name, "json")


def apply_txt_extension(name):
    return name if str(name).endswith(".txt") else "{}.{}".format(name, "txt")


def read_json(json_path):
    """
    :parameter json_path: json file path
    :return: json file content if has content
    """
    with open(json_path) as f:
        if f.readlines():
            f.seek(0)
            return json.load(f)


def write_json(data, json_path):
    with open(json_path, 'w') as f:
        if cache_prettyprint:
            json.dump(data, f, indent=3, sort_keys=True)
        else:
            json.dump(data, f)


def save_cache(cache_data_in=None, name=None):
    if not cache_data_in and not name:
        write_json(cache_data, context_find(config_data["cache_file_name"]))
    elif cache_data_in and name:
        write_json(cache_data_in, os.path.join(CACHE_CONTAINER_PATH, apply_json_extension(name)))
    elif cache_data_in:
        write_json(cache_data_in, context_find(config_data["cache_file_name"]))
    elif name:
        write_json(cache_data, os.path.join(CACHE_CONTAINER_PATH, apply_json_extension(name)))


def autosave_cache():
    if autosave:
        save_cache()


def load_cache(file_name=None):
    # here cache_data has to be global!
    global cache_data
    if file_name:
        cache_data = read_json(os.path.join(CACHE_CONTAINER_PATH, apply_json_extension(file_name)))
        autosave_cache()
    else:
        cache_data = read_json(context_find(config_data["cache_file_name"]))
        autosave_cache()


def print_configs():
    def configuration_settings():
        """
        returns list of simple configuration properties (not maps)
        :return:
        """
        ignore_list = ["print_configs_at_startup"]
        return [data for data in config_data if
                (not isinstance(config_data[data], Mapping) and data not in ignore_list)]

    for config in configuration_settings(): print(config, ":", config_data[config])


class MetafolderController:
    def get_metafolder_archive_subdir(self, other_dir):
        return os.path.join(self.METAFOLDER_PATH, "archive", other_dir)

    def context_find(self, file_name):
        return search_in_folder(self.METAFOLDER_PATH, file_name)

    def execs_context_find(self, file_name):
        return search_in_folder(self.EXECUTIONS_CONTAINER_PATH, file_name)

    def retrieve_config(self, name):
        return retrieve(self.config_data, name)

    def retrieve_cache(self, name):
        return retrieve(self.cache_data, name)

    def print_configs(self):
        def configuration_settings():
            """
            returns list of simple configuration properties (not maps)
            :return:
            """
            ignore_list = ["print_configs_at_startup"]
            return [data for data in self.config_data if
                    (not isinstance(self.config_data[data], Mapping) and data not in ignore_list)]

        for config in configuration_settings(): print(config, ":", self.config_data[config])

    def __init__(self):
        # args = self.args = sys.argv[1:]

        self.script_name = sys.argv[0]
        self.METAFOLDER_PATH = find_metafolder_path(self.script_name, "metafolder")

        self.FILE_CONTAINER_PATH = self.get_metafolder_archive_subdir("file_container")
        self.DIR_CONTAINER_PATH = self.get_metafolder_archive_subdir("dir_container")
        self.CACHE_CONTAINER_PATH = self.get_metafolder_archive_subdir("cache_container")
        self.EXECUTIONS_CONTAINER_PATH = self.get_metafolder_archive_subdir("exec_flows")
        self.ZIPS_TEMP_CONTAINER_PATH = self.get_metafolder_archive_subdir("zips_temp")

        self.config_data = read_json(self.context_find("config.json"))
        self.cache_data = read_json(self.context_find(self.config_data["cache_file_name"]))

        self.cache_prettyprint = self.retrieve_config("cache_prettyprint")
        self.autosave = self.retrieve_config("autosave")

        self.shorthands = [item for sublist in list(self.config_data["shortcuts"].values()) for item in sublist]
        if len(self.shorthands) != len(set(self.shorthands)):
            print("ATTENTION! One or more shorthand configurations may be duplicated or incorrect!")

        if self.retrieve_config("print_configs_at_startup"): print_configs()

        configure_metafolder_path(self)
        configure_archive_containers(self)
        configure_config_and_cache_data(self)
        configure_other_params(self)


def configure_metafolder_path(metafolder_controller):
    """
    Sets the variables needed for the main logic of elaborations
    Has to be run before running any of methods in this .py
    """
    global METAFOLDER_PATH
    METAFOLDER_PATH = metafolder_controller.METAFOLDER_PATH


def configure_archive_containers(metafolder_controller):
    global FILE_CONTAINER_PATH, DIR_CONTAINER_PATH
    global CACHE_CONTAINER_PATH
    global EXECUTIONS_CONTAINER_PATH
    global ZIPS_TEMP_CONTAINER_PATH

    FILE_CONTAINER_PATH = metafolder_controller.FILE_CONTAINER_PATH
    DIR_CONTAINER_PATH = metafolder_controller.DIR_CONTAINER_PATH
    CACHE_CONTAINER_PATH = metafolder_controller.CACHE_CONTAINER_PATH
    EXECUTIONS_CONTAINER_PATH = metafolder_controller.EXECUTIONS_CONTAINER_PATH
    ZIPS_TEMP_CONTAINER_PATH = metafolder_controller.ZIPS_TEMP_CONTAINER_PATH


def configure_config_and_cache_data(metafolder_controller):
    global config_data, cache_data
    config_data = metafolder_controller.config_data
    cache_data = metafolder_controller.cache_data


def configure_other_params(metafolder_controller):
    global cache_prettyprint, autosave
    cache_prettyprint = metafolder_controller.cache_prettyprint
    autosave = metafolder_controller.autosave


def get_metafolder_archive_subdir(other_dir):
    return os.path.join(METAFOLDER_PATH, "archive", other_dir)


def item_not_found(item_type, path):
    print("could not find", item_type, "[{}]".format(path))
    return None


def safe_copy_dir(src_dir_path, dst_dir_path):
    if not normal_path(src_dir_path).is_dir():
        return None
    if normal_path(dst_dir_path).is_dir():
        shutil.rmtree(dst_dir_path)
    return shutil.copytree(src_dir_path, dst_dir_path)


def remove_current_file():
    if cache_data["current_file_name"]:
        try:
            os.remove(os.path.join(FILE_CONTAINER_PATH, cache_data["current_file_name"]))
        except FileNotFoundError:
            print("could not delete current file")
        cache_data["current_file_name"] = ""
        autosave_cache()


def remove_current_dir():
    if cache_data["current_dir_name"]:
        try:
            shutil.rmtree(os.path.join(DIR_CONTAINER_PATH, cache_data["current_dir_name"]))
        except FileNotFoundError:
            print("could not delete current dir")
        cache_data["current_dir_name"] = ""
        autosave_cache()


def get_file(file_path):
    """Saves a file as the current file
        :returns: new file path"""

    file_path = normal_path(file_path)

    if os.path.isdir(file_path):
        remove_current_dir()
        cache_data["current_dir_name"] = normal_path(file_path).name
        current_dir_path = os.path.join(DIR_CONTAINER_PATH, cache_data["current_dir_name"])
        safe_copy_dir(file_path, current_dir_path)
        autosave_cache()
        return current_dir_path

    # if the extension is missing
    check = Path(str(file_path) + ".txt")
    if check.is_file():
        file_path = check

    if os.path.isfile(file_path):
        remove_current_file()
        cache_data["current_file_name"] = normal_path(file_path).name
        current_file_path = os.path.join(FILE_CONTAINER_PATH, cache_data["current_file_name"])
        shutil.copy(file_path, current_file_path)
        autosave_cache()
        return current_file_path

    return item_not_found("path", file_path)


def get_path_alias(path, alias):
    # todo: refactor with normal_path
    path = os.path.abspath(path)
    if os.path.isfile(path):
        return get_with_alias("file", "file_map", FILE_CONTAINER_PATH, path, alias)
    if os.path.isdir(path):
        return get_with_alias("dir", "dir_map", DIR_CONTAINER_PATH, path, alias)
    return item_not_found("path", path)


def get_with_alias(file_type, map_type, container_path, file_path, alias):
    cache_data[map_type][alias] = os.path.join(container_path, os.path.basename(file_path))
    if file_type == "file":
        shutil.copy(file_path, cache_data[map_type][alias])
    else:
        safe_copy_dir(file_path, cache_data[map_type][alias])
    # autosave_cache()
    save_cache()
    print("get {}:{} with alias:{}".format(file_type, file_path, alias))
    return cache_data[map_type][alias]


def put_file(destination_path):
    """Copies the current file to a specific destination fixme: (has to be a folder (?!))"""
    # get_current_file_path()
    destination_path = os.path.abspath(destination_path)
    if not os.path.isdir(destination_path): return item_not_found("dir", destination_path)
    file_path = os.path.join(FILE_CONTAINER_PATH, cache_data["current_file_name"])
    shutil.copy(file_path, destination_path)
    # print("put {}:{} with alias:{}".format(file_type.., file_path.., alias..))
    print("put file in {}".format(destination_path))


def put_file_alias(alias, alias_or_destination_path):
    """Copies the current file to a specific destination alias or folder path"""

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

            safe_copy_dir(source.path, os.path.join(DIR_CONTAINER_PATH, source.normalized_path.name))
        else:
            print("error in copy source to path")

    source = create_source(alias)
    destination = create_destination(alias_or_destination_path)
    copy(source, destination)


def safe_create_path(unzipped_dir_path, zip_relative_path):
    only_one_step = os.path.join(unzipped_dir_path, zip_relative_path)
    if not os.path.isdir(only_one_step):
        os.mkdir(only_one_step)


def copy_file_to_dir_relative(file_path, unzipped_dir_path, zip_relative_path):
    safe_create_path(unzipped_dir_path, zip_relative_path)
    shutil.copy(file_path, os.path.join(unzipped_dir_path, zip_relative_path))


def zip_file(destination_path_with_name, unzipped_dir_path):
    shutil.make_archive(destination_path_with_name, 'zip', unzipped_dir_path)
    return "%s.zip" % destination_path_with_name


def put_to_zip(file_path_or_alias, zip_path, zip_relative_path):
    file_path = file_path_or_alias  # convert_to_path(file_path_or_alias)
    unzipped_dir_path = unzip_file_to_temp(zip_path)
    zip_name = Path(zip_path).stem
    copy_file_to_dir_relative(file_path, unzipped_dir_path, zip_relative_path)
    destination_path_with_name = os.path.join(ZIPS_TEMP_CONTAINER_PATH, zip_name)
    new_zipped_file_path = zip_file(destination_path_with_name, unzipped_dir_path)
    original_zip_parent_path = os.path.dirname(file_path)
    shutil.copy(new_zipped_file_path, original_zip_parent_path)  # overwrite always?
    print("done!")


def unzip_file_to_temp(zip_path):
    zip_name = Path(zip_path).stem
    zip_temp_dir = os.path.join(ZIPS_TEMP_CONTAINER_PATH, zip_name)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(zip_temp_dir)
    return zip_temp_dir


def get_from_zip(zip_relative_path, zip_path, alias):
    temp_zip_dir = unzip_file_to_temp(zip_path)
    file_path = Path(os.path.join(ZIPS_TEMP_CONTAINER_PATH, temp_zip_dir, zip_relative_path))
    result_file_path = shutil.copy(file_path, FILE_CONTAINER_PATH)
    cache_data["file_map"][alias] = result_file_path
    autosave_cache()


def show_list_caches():
    files_list = [f for f in listdir(CACHE_CONTAINER_PATH) if isfile(join(CACHE_CONTAINER_PATH, f))]
    [print(join(CACHE_CONTAINER_PATH, f)) for f in files_list]


def show_list_files_dirs():
    print(" files:", list(cache_data["file_map"].keys()))
    print(" dirs:", list(cache_data["dir_map"].keys()))


def show_list_shorthands():
    print(config_data["shortcuts"])


def show_execution_content():
    with open(context_find("current_exec.txt")) as file:
        lines = [line.rstrip() for line in file]
    for line in lines:
        print(line)


def show_execution_content(exec_name):
    exec_name_ext = exec_name + ".txt"

    alias_value = safe_get_alias(cache_data, "executions", exec_name)
    exec_file_name = alias_value if alias_value else exec_name_ext

    if search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name):
        with open(execs_context_find(exec_file_name)) as file:
            lines = [line.rstrip() for line in file]

    try:
        lines
    except NameError:
        print("no executions found with that name")
        return

    for line in lines:
        print(line)


# reformat "execution" name/term
# prints the LOADED file! no live update
def show_list_executions():
    cache_data = read_json(context_find(config_data["cache_file_name"]))
    print(" executions:", list(cache_data["executions"].keys()))


def show_map_files_dirs():
    print(" files:")
    if not cache_data["file_map"] is None:
        [print("   {}: {}".format(k, v)) for k, v in cache_data["file_map"].items()]

    print(" dirs:")
    if not cache_data["dir_map"] is None:
        [print("   {}: {}".format(k, v)) for k, v in cache_data["dir_map"].items()]


def clean_directory(dir_name):
    """Cleans the contents of a directory"""
    for filename in os.listdir(dir_name):
        file_path = os.path.join(dir_name, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def clean_folders():
    clean_directory(FILE_CONTAINER_PATH)
    clean_directory(DIR_CONTAINER_PATH)


def clean_cache():
    # todo: parametrize for each "archive"
    cache_data["current_file_name"] = ""
    cache_data["current_dir_name"] = ""
    cache_data["file_map"] = {}
    cache_data["dir_map"] = {}

    save_cache()


def clean_cache_and_folders():
    clean_folders()
    clean_cache()


def remove_file_alias(alias):
    # fixme: extract method
    if alias in cache_data["file_map"]:
        del cache_data["file_map"][alias]


def remove_dir_alias(alias):
    if alias in cache_data["dir_map"]:
        del cache_data["dir_map"][alias]


def configure_args_handler(args_list):
    """
    sets the variables of args_handler module
    """
    global args_check, any
    args_handler.args = args_list
    args_check, any = args_handler.args_check, args_handler.any


def retrieve_options(command):
    if command in config_data["shortcuts"]:
        options = config_data["shortcuts"][command].copy()
        options.append(command)
        return options
    else:
        return [command]


def safe_get_from_array(array, index):
    """
    returns indexes value of an array
    only if present
    """
    try:
        return array[index]
    except IndexError:
        return None


# todo: check if works on dictionaries
def safe_get_alias(data, group, key):
    """
    returns value of an alias of a certain group
    only if present
    """
    try:
        return data[group][key]
    except KeyError:
        return None


def execute_args_check():
    """
    executes commands and checks the input arguments and relative shortcuts
    """
    args_check(print_help, retrieve_options("help"))

    args_check(show_map_files_dirs, retrieve_options("map"))
    args_check(show_list_files_dirs, retrieve_options("list"))
    args_check(show_list_caches, retrieve_options("list"), "caches")

    args_check(show_list_shorthands, retrieve_options("list"), retrieve_options("shortcuts"))

    args_check(clean_cache, retrieve_options("clean"), "cache")
    args_check(clean_folders, retrieve_options("clean"), "folders")
    args_check(clean_cache_and_folders, retrieve_options("clean"), "data")

    args_check(get_file, retrieve_options("get"), any)
    args_check(get_path_alias, retrieve_options("get"), any, "as", any)

    args_check(put_file, retrieve_options("put"), any)
    args_check(put_file_alias, retrieve_options("put"), any, "in", any)

    args_check(save_cache, "save", "cache", any)
    args_check(load_cache, "load", "cache", any)

    # todo: refactor!
    args_check(show_execution_content, "show", "exec")
    args_check(show_execution_content, "show", "exec", any)
    args_check(show_list_executions, "list", "execs")

    if not args_handler.retrive_activator(): print("couldn't find command", args_handler.args)


def print_help():
    commands_list = []

    commands_list.append("get FILE_NAME")
    commands_list.append("get FILE_NAME as ALIAS")

    commands_list.append("put DESTINATION_DIR_NAME")
    commands_list.append("put ALIAS in DESTINATION_DIR_NAME")

    commands_list.append("map")
    commands_list.append("list")
    commands_list.append("list caches")

    commands_list.append("clean cache")
    commands_list.append("clean folders")
    commands_list.append("clean data")

    commands_list.append("save cache NAME")
    commands_list.append("load cache NAME")

    commands_list.append("init ... [commands] ... end ... execute")
    # todo: refactor
    commands_list.append("show exec")
    commands_list.append("list execs")
    commands_list.append("exec mode")
    commands_list.append("exec mode for EXEC_NAME")

    [print("\t{}".format(el)) for el in commands_list]
