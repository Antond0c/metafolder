import os
from pathlib import Path


def normal_path(path):
    """
    Normalizes the path
    """
    return Path(os.path.abspath(path))
