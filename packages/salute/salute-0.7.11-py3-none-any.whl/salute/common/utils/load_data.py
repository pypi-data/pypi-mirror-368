import json
from pathlib import Path


def load_data(filename: Path) -> dict:
    data = {}
    with open(filename) as f:
        data = json.load(f)
    return data
