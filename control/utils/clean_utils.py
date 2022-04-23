import os
import shutil

from .cache_utils import save_cache
from .objects_utils import ControllerUser


class Cleaner(ControllerUser):

    def directory(self, name):
        clean_directory(self.controller, name)

    def folders(self):
        clean_folders(self.controller)

    def cache(self):
        clean_cache(self.controller)

    def all(self):
        clean_cache_and_folders(self.controller)


def clean_directory(controller, dir_name):
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


def clean_folders(controller):
    for key,value in controller.container.__dict__.items():
        if key != "metafolder":
            clean_directory(controller, value)


def clean_cache(controller):
    controller.data.cache["current_file_name"] = ""
    controller.data.cache["current_dir_name"] = ""
    controller.data.cache["file_map"] = {}
    controller.data.cache["dir_map"] = {}
    controller.data.cache["executions"] = {}

    save_cache(controller)


def clean_cache_and_folders(controller):
    clean_folders(controller)
    clean_cache(controller)
