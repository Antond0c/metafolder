import os

from .normal import normal_path


def find_metafolder_path(starting_app_path, base_parent_dir_name):
    """
    given the running program name search the dir where it's running
    go up in directories till you find the application base folder
    return path
    if cannot find raises FileNotFoundError
    """
    current_path = normal_path(starting_app_path)
    while current_path != os.path.dirname(current_path):
        if os.path.basename(current_path) == base_parent_dir_name:
            return current_path
        current_path = os.path.dirname(current_path)

    raise FileNotFoundError("Could not find", base_parent_dir_name)

def find_metafolder_path_simpler(script_path):
    return normal_path(script_path).parent.parent


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

    return None


def retrieve_cmd_options(config_data, command):
    """returns all command's names"""
    if command in config_data["shortcuts"]:
        options = config_data["shortcuts"][command].copy()
        options.append(command)
        return options
    else:
        return [command]
