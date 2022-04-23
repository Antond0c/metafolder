import os


class Container:
    """
    contains the path to different folders
    sub-folders under the archive folder
    metafolder, files, dirs, zips, caches, executions
    """

    def get_metafolder_archive_subdir(self, other_dir):
        return os.path.join(self.metafolder, "archive", other_dir)

    def __init__(self, metafolder_path):
        self.metafolder = metafolder_path

        self.file = self.get_metafolder_archive_subdir("file_container")
        self.dir = self.get_metafolder_archive_subdir("dir_container")
        self.zip = self.get_metafolder_archive_subdir("zips_temp")
        self.cache = self.get_metafolder_archive_subdir("cache_container")
        self.execution = self.get_metafolder_archive_subdir("exec_flows")


class Data:
    """config_data and cache_data"""
    def __init__(self, config, cache):
        self.config = config
        self.cache = cache


class InData():
    """contains the data from input line"""
    def __init__(self):
        self.line = input().strip()
        self.args = self.line.split(" ")
        self.size = len(self.args)
        self.has_multi = self.size > 1
        self.first = self.command = self.args[0] if self.size > 0 else None
        self.second = self.args[1] if self.size > 1 else None
        self.third = self.args[2] if self.size > 2 else None
        self.params = None

    def init_params(self):
        if not self.params and self.size > 1:
            self.params = self.args[1:]


class Activator():
    """contains the state for handling commands execution"""
    def __init__(self):
        self.state = False

    def apply(self, val):
        if val: self.state = True

    def up(self):
        self.apply(True)

    def down(self):
        self.apply(False)


class CheckUnit():
    """represents one command"""
    def __init__(self, function, options, description, print_description):
        self.function = function
        self.options = options
        self.description = description
        self.print_description = print_description

    def execute(self, activator, args):
        actual_args = args
        actual_args_len = len(actual_args)
        expected_args = self.options
        expected_args_len = len(expected_args)

        if actual_args_len != expected_args_len:
            activator.down()
            return False

        function_params = []
        for i in range(0, expected_args_len):
            is_argument_list = isinstance(expected_args[i], list)
            is_not_option = (actual_args[i] not in expected_args[i])
            no_matches_argument = actual_args[i] != expected_args[i]
            no_match = is_not_option if is_argument_list else no_matches_argument
            if no_match:
                if expected_args[i] == "ANY":
                    function_params.append(actual_args[i])
                else:
                    activator.down()
                    return False
        # matches the function case
        activator.up()
        self.function() if not function_params else self.function(*function_params)
        return True

class ControllerUser():
    def __init__(self, controller):
        self.controller = controller