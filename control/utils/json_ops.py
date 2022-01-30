import json


def read_json(json_path):
    """
    :parameter json_path: json file path
    :return: json file content if has content
    """
    with open(json_path) as f:
        if f.readlines():
            f.seek(0)

            # parse json data
            try:
                json_content = json.load(f)
            except Exception as e:
                print("could not write json file")
                print(e)
                # raise e

            return json_content


def write_json(data, json_path, pretty_print_enabled=True):
    try:
        with open(json_path, 'w') as f:
            if pretty_print_enabled:
                json.dump(data, f, indent=3, sort_keys=True)
            else:
                json.dump(data, f)
    except Exception as e:
        print("could not write json file")
        print(e)
