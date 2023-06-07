import os
import json
from typing import *

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))


if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)


def get_file_name(name: str) -> str:
    return os.path.join(DATA_DIR, f"{name}.json")


def load_data(name: str, default=None) -> Any:
    file = get_file_name(name)
    if os.path.exists(file):
        try:
            with open(file, "r") as fp:
                return json.load(fp)
        except:
            pass
    return default


def save_data(name: str, data: Any):
    with open(get_file_name(name), "w") as fp:
        json.dump(data, fp)
