from os import listdir
from os.path import isfile, join

from .objects_utils import ControllerUser


class Printer(ControllerUser):

    def list(self):
        show_list_files_dirs(self.controller.data.cache)

    def map(self):
        show_map_files_dirs(self.controller.data.cache)

    def caches(self):
        show_list_caches(self.controller.container.cache)

    def shorts(self):
        show_list_shorthands(self.controller.data.config)


def show_list_caches(cache_container_path):
    files_list = [f for f in listdir(cache_container_path) if isfile(join(cache_container_path, f))]
    [print(join(cache_container_path, f)) for f in files_list]


def show_list_files_dirs(cache_data):
    print(" files:", list(cache_data["file_map"].keys()))
    print(" dirs:", list(cache_data["dir_map"].keys()))


def show_list_shorthands(config_data):
    print(config_data["shortcuts"])


def show_map_files_dirs(cache_data):
    print(" files:")
    if not cache_data["file_map"] is None:
        [print("   {}: {}".format(k, v)) for k, v in cache_data["file_map"].items()]

    print(" dirs:")
    if not cache_data["dir_map"] is None:
        [print("   {}: {}".format(k, v)) for k, v in cache_data["dir_map"].items()]
