import os

from ..ControllerUser import ControllerUser
from ..json_ops import write_json, read_json
from ..methods import apply_json_extension


class CacheManager(ControllerUser):

    def save(self, new_name=None):
        save_cache(self.controller, new_name)

    def load(self, cache_name):
        load_cache(self.controller, cache_name)
        save_cache(self.controller)


def save_cache(controller, custom_cache_data=None, new_name=None):
    """If only contoller provided saves the current cache to file"""
    current_cache_data = controller.data.cache
    current_cache_path = controller.retrieve_current_cache_file_path()

    # custom cache data currently not used
    cache_content = custom_cache_data or current_cache_data
    cache_file_path = get_cache_file_path(controller.container.cache, new_name) if new_name else current_cache_path

    write_json(cache_content, cache_file_path)


def load_cache(controller, cache_file_name=None):
    current_cache_path = controller.retrieve_current_cache_file_path()

    cache_file_path = get_cache_file_path(controller.container.cache, cache_file_name) if cache_file_name \
        else current_cache_path

    controller.data.cache = read_json(cache_file_path)


def autosave_cache(controller, autosave_enabled):
    """If autosave is enabled saves current cache"""
    if autosave_enabled:
        save_cache(controller)


def get_cache_file_path(cache_container, file_name):
    """:returns a file path of a cache file with a specific name in the cache container"""
    return os.path.join(cache_container, apply_json_extension(file_name))
