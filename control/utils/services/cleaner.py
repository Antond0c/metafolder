import os
import shutil

from .cache_manager import save_cache
from ..ControllerUser import ControllerUser


class Cleaner(ControllerUser):
    """cleans folders and file contents"""

    def folders(self):
        clean_archive_folders(self.controller)

    def cache(self):
        clean_cache_content(self.controller.data.cache)

    def archives_and_cache(self):
        clean_archives_and_cache(self.controller)

    def archive(self, name):
        clean_archive(self.controller, name)


def clean_directory_content(dir_name):
    """Cleans the contents of a directory"""
    for file_name in os.listdir(dir_name):
        file_path = os.path.join(dir_name, file_name)
        purge_file_or_dir(file_path)


def purge_file_or_dir(file_path):
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))


def clean_archive_folders(controller):
    """Cleans services' folders"""
    archives_to_purge = ["dir", "file", "cache", "execution", "zip"]
    for archive in archives_to_purge:
        archive_path = controller.container.get_metafolder_archive_subdir(archive)
        clean_directory_content(archive_path)


def clean_archive(controller, name):
    """Cleans specified archive"""
    archives_to_purge = ["dir", "file", "cache", "execution", "zip"]
    if name in archives_to_purge:
        archive_path = controller.container.get_metafolder_archive_subdir(name)
        clean_directory_content(archive_path)


def clean_cache_content(controller):
    """Cleans current cache properties"""
    current_cache = controller.data.cache

    current_cache["current_file_name"] = ""
    current_cache["current_dir_name"] = ""
    current_cache["file_map"] = {}
    current_cache["dir_map"] = {}
    current_cache["executions"] = {}

    # cache_manager.save()
    save_cache(controller)


def clean_archives_and_cache(controller):
    clean_archive_folders(controller)
    clean_cache_content(controller)
