import os

from .json_utils import write_json, read_json
from .objects_utils import ControllerUser
from .retrieve_utils import search_in_folder


class CacheManager(ControllerUser):

    def save(self, name):
        save_cache(self.controller, name=name)

    def load(self, name):
        load_cache(self.controller, name)


def apply_json_extension(name):
    return name if str(name).endswith(".json") else "{}.{}".format(name, "json")


def apply_txt_extension(name):
    return name if str(name).endswith(".txt") else "{}.{}".format(name, "txt")


def save_cache(controller, cache_data_in=None, name=None):
    container = controller.container
    data = controller.data
    if not cache_data_in and not name:
        write_json(data.cache, search_in_folder(container.metafolder, data.config["cache_file_name"]), True)
    elif cache_data_in and name:
        write_json(cache_data_in, os.path.join(container.cache, apply_json_extension(name)), True)
    elif cache_data_in:
        write_json(cache_data_in, search_in_folder(container.metafolder, data.config["cache_file_name"]), True)
    elif name:
        write_json(data.cache, os.path.join(container.cache, apply_json_extension(name)), True)


def autosave_cache(controller, autosave):
    if autosave:
        save_cache(controller)


def load_cache(controller, file_name=None):
    container = controller.container
    data = controller.data
    if file_name:
        data.cache = read_json(os.path.join(container.cache, apply_json_extension(file_name)))
        autosave_cache(controller, True)
    else:
        data.cache = read_json(search_in_folder(container.metafolder, data.config["cache_file_name"]))
        autosave_cache(controller, True)
