import os
from settings import DATA_PATH


def make_path(dest):
    cur_dir = os.getcwd()
    cur_dir += DATA_PATH
    cur_dir += '\\' + dest
    return cur_dir
