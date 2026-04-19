import json
import os

def read_json(file_name: str) -> dict:
    if not os.path.exists(file_name):
        return {}
    with open(file_name, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def write_json(file_name: str, obj: dict):
    data = read_json(file_name)
    data |= obj
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=True)
        f.flush()