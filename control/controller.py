import sys
from collections import Mapping

from utils.ArgsChecker import ArgsChecker
from utils.retrieve_utils import search_in_folder, find_metafolder_path, find_metafolder_path_simpler
from utils.json_utils import read_json
from utils.objects_utils import Container, Data


def retrieve(map, key):
    return map[key] if key in map else None


def print_configs(config_data):
    def configuration_settings():
        """returns list of simple configuration properties (not maps)"""
        ignore_list = ["print_configs_at_startup"]
        return [data for data in config_data if
                (not isinstance(config_data[data], Mapping) and data not in ignore_list)]

    for config in configuration_settings(): print(config, ":", config_data[config])


class MetafolderController:

    def retrieve_config(self, name):
        return retrieve(self.config_data, name)

    def handle_command_line(self, argument_list):
        """executes argument check"""
        self.checker.execute_check(argument_list)

    def __init__(self):
        script_name = sys.argv[0]
        self.container = Container(find_metafolder_path_simpler(script_name))
        # self.container = Container(find_metafolder_path(script_name, "metafolder"))
        # todo: create archives structure

        self.config_data = read_json(search_in_folder(self.container.metafolder, "config.json"))
        self.cache_data = read_json(search_in_folder(self.container.metafolder, self.config_data["cache_file_name"]))
        self.data = Data(self.config_data, self.cache_data)

        self.cache_prettyprint = self.retrieve_config("cache_prettyprint")
        self.autosave = self.retrieve_config("autosave")

        # extract shortcuts values from the dictionary
        self.shorthands = [item for sublist in list(self.config_data["shortcuts"].values()) for item in sublist]
        if len(self.shorthands) != len(set(self.shorthands)):
            print("ATTENTION! One or more shorthand settings may be duplicated or incorrect!")

        if self.retrieve_config("print_configs_at_startup"): print_configs(self.config_data)

        self.checker = ArgsChecker(self)
