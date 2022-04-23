import os
from pathlib import Path


def normal_path(path):
    """
    Normalizes the path
    """
    # if os.path.exists(path):
    return Path(os.path.abspath(path))
    # else:
    #     return None


def item_not_found(item_type, path):
    print("could not find", item_type, "[{}]".format(path))
    return None

