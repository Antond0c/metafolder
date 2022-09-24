import os
import sys
from collections.abc import Mapping

from utils.json_ops import read_json
from utils.methods import create_archives
from utils.path_normalizer import normal_path


def retrieve(map, key):
    return map[key] if key in map else None


def find_metafolder_path(script_path):
    return normal_path(script_path).parent.parent


def print_configs(config_data):
    def configuration_settings():
        """returns list of simple configuration properties (not maps)"""
        ignore_list = ["print_configs_at_startup"]
        return [data for data in config_data if
                (not isinstance(config_data[data], Mapping) and data not in ignore_list)]

    for config in configuration_settings(): print(config, ":", config_data[config])


class MetafolderController:
    config_sample = "{\"clean_cache_at_startup\":false,\"cache_file_name\":\"cache.json\",\"cache_prettyprint\":true,\"startup_script\":\"\",\"autosave\":false,\"print_configs_at_startup\":false,\"print_caches_path\":true,\"shortcuts\":{\"help\":[\"h\"],\"map\":[\"m\"],\"list\":[\"l\"],\"clean\":[\"c\"],\"shortcuts\":[\"shorts\",\"shorthands\"]}}"
    cache_sample = "{\"current_dir_name\":\"\",\"current_file_name\":\"\",\"dir_map\":{\"prova\":\"\"},\"executions\":{\"ciao\":\"\"},\"file_map\":{\"zipfile\":\"\"}}"

    def __init__(self, script_name):
        self.checker = None

        # create or check folder structure
        self.container = Container(find_metafolder_path(script_name))
        create_archives(self.container)

        # load configuration and cache data
        self.config_data = read_json(self.retrieve_config_file("config.json"))
        self.cache_data = read_json(self.retrieve_config_file(self.config_data["cache_file_name"]))
        self.data = Data(self.config_data, self.cache_data)

        # load properties values
        self.cache_prettyprint = self.retrieve_config_property("cache_prettyprint")
        self.autosave = self.retrieve_config_property("autosave")

        # extract shortcuts values from the dictionary
        self.shorthands = [item for sublist in list(self.config_data["shortcuts"].values()) for item in sublist]
        if len(self.shorthands) != len(set(self.shorthands)):
            print("ATTENTION! One or more shorthand settings may be duplicated or incorrect!")

        # show all user configurations if required
        if self.retrieve_config_property("print_configs_at_startup"): print_configs(self.config_data)

        if self.retrieve_config_file("check_paths_status"):
            pass

    def retrieve_config_property(self, name):
        return retrieve(self.data.config, name)

    def retrieve_cache_property(self, name):
        return retrieve(self.data.cache, name)

    def retrieve_current_cache_file_path(self):
        return self.retrieve_config_file(self.config_data["cache_file_name"])

    def retrieve_config_file(self, file_name):
        return normal_path(self.container.get_metafolder_configuration_dir()).joinpath(file_name)

    def set_checker(self, checker):
        self.checker = checker


class Container:
    """
    contains the path to different folders\n
    sub-folders under the archive folder\n
    metafolder, files, dirs, zips, caches, executions\n
    (contains **paths**)
    """

    def get_metafolder_archive_subdir(self, other_dir):
        return os.path.join(self.metafolder, "archive", other_dir)

    def get_metafolder_configuration_dir(self):
        return os.path.join(self.metafolder, "configuration")

    def __init__(self, metafolder_path):
        self.metafolder = metafolder_path

        self.file = self.get_metafolder_archive_subdir("file_container")
        self.dir = self.get_metafolder_archive_subdir("dir_container")
        self.zip = self.get_metafolder_archive_subdir("zip")
        self.cache = self.get_metafolder_archive_subdir("cache_container")
        self.execution = self.get_metafolder_archive_subdir("exec_flows")


class Data:
    """config_data and cache_data\n
    (contains **configurations**)"""

    def __init__(self, config, cache):
        self.config = config
        self.cache = cache
