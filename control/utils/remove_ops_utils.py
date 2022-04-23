import os
import shutil

from .cache_utils import autosave_cache


def remove_current_file(cache_data, FILE_CONTAINER_PATH):
    if cache_data["current_file_name"]:
        try:
            os.remove(os.path.join(FILE_CONTAINER_PATH, cache_data["current_file_name"]))
        except FileNotFoundError:
            print("could not delete current file")
        cache_data["current_file_name"] = ""
        autosave_cache()


def remove_current_dir(cache_data, DIR_CONTAINER_PATH=None):
    if cache_data["current_dir_name"]:
        try:
            shutil.rmtree(os.path.join(DIR_CONTAINER_PATH, cache_data["current_dir_name"]))
        except FileNotFoundError:
            print("could not delete current dir")
        cache_data["current_dir_name"] = ""
        autosave_cache()


def remove_file_alias(cache_data, alias):
    # fixme: extract method
    if alias in cache_data["file_map"]:
        del cache_data["file_map"][alias]


def remove_dir_alias(cache_data, alias):
    if alias in cache_data["dir_map"]:
        del cache_data["dir_map"][alias]
