from os import listdir
from os.path import isfile, join

from ..ControllerUser import ControllerUser
from ..path_normalizer import normal_path


class Printer(ControllerUser):

    def list(self):
        file_map = self.controller.retrieve_cache_property("file_map")
        dir_map = self.controller.retrieve_cache_property("dir_map")
        show_list_files_and_dirs(file_map, dir_map)

    def map(self):
        file_map = self.controller.retrieve_cache_property("file_map")
        dir_map = self.controller.retrieve_cache_property("dir_map")
        show_map_files_and_dirs(file_map, dir_map)

    def caches(self):
        cache_container_path = self.controller.container.cache
        enabled = self.controller.retrieve_config_property("print_caches_path")
        show_list_caches(cache_container_path, print_caches_path_enabled=enabled)

    def shorts(self):
        shortcuts_map = self.controller.retrieve_config_property("shortcuts")
        show_list_shortcuts(shortcuts_map)

    def print_currents(self):
        print("file", ":", self.controller.retrieve_cache_property("current_file_name"))
        print("dir", ":", self.controller.retrieve_cache_property("current_dir_name"))
        print()

    def echo(self, name):
        file_map = self.controller.data.cache["file_map"]
        dir_map = self.controller.data.cache["dir_map"]

        if name in file_map:
            # print("found '{}' as '{}' in file_map".format(file_map[name], name))
            print(file_map[name])
            return
        if name in dir_map:
            # print("found '{}' as '{}' in dir_map".format(dir_map[name], name))
            print(dir_map[name])
            return

        print("no '{}' in current cache".format(name))

    def resolve(self, text):
        print(normal_path(text))


def show_list_caches(cache_container_path, print_caches_path_enabled=False):
    # searches for all files in cache_container_path
    files_list = [f for f in listdir(cache_container_path) if isfile(join(cache_container_path, f))]

    if len(files_list) == 0:
        print("", "no caches to show")
    else:
        for f in files_list:
            print(normal_path(f).stem)
            if print_caches_path_enabled:
                print("\t", join(cache_container_path, f))


def show_list_shortcuts(shortcuts_map):
    print(shortcuts_map)


def show_list_files_and_dirs(files_map, dirs_map):
    print(" files:", list(files_map.keys()))
    print(" dirs:", list(dirs_map.keys()))
    print()


def show_map_files_and_dirs(files_map, dirs_map):
    print(" files:")
    if files_map:
        [print("  ", "{}: {}".format(k, v)) for k, v in files_map.items()]

    print(" dirs:")
    if dirs_map:
        [print("  ", "{}: {}".format(k, v)) for k, v in dirs_map.items()]
