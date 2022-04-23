import json


def read_json(json_path):
    """
    :parameter json_path: json file path
    :return: json file content if has content
    """
    with open(json_path) as f:
        if f.readlines():
            f.seek(0)
            return json.load(f)


def write_json(data, json_path, is_prettyprint):
    with open(json_path, 'w') as f:
        if is_prettyprint:
            json.dump(data, f, indent=3, sort_keys=True)
        else:
            json.dump(data, f)