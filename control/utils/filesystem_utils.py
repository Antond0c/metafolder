import os
import shutil

from .normal import normal_path


def safe_copy_dir(src_dir_path, dst_dir_path):
    if not normal_path(src_dir_path).is_dir():
        return None
    # todo: check the behaviour
    joinpath = normal_path(dst_dir_path).joinpath(normal_path(src_dir_path).name)
    if joinpath.is_dir():
        shutil.rmtree(joinpath)
    # else:
    #     normal_path(dst_dir_path).mkdir(parents=True, exist_ok=True)
    return shutil.copytree(src_dir_path, joinpath)


def safe_create_path(unzipped_dir_path, zip_relative_path):
    only_one_step = os.path.join(unzipped_dir_path, zip_relative_path)
    if not os.path.isdir(only_one_step):
        os.mkdir(only_one_step)


def copy_file_to_dir_relative(file_path, unzipped_dir_path, zip_relative_path):
    safe_create_path(unzipped_dir_path, zip_relative_path)
    shutil.copy(file_path, os.path.join(unzipped_dir_path, zip_relative_path))
