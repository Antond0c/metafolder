import os


def split_command_line_arguments(line):
    """
    splits line in blocks respecting the ["] character,
    creates an array
    """
    result = []
    if "\"" in line:
        raw = line.split("\"")
        for i in range(0, len(raw)):
            if i % 2 != 0:
                result.append(raw[i].strip())
            else:
                [result.append(x) for x in raw[i].split(" ") if x]
    else:
        [result.append(x) for x in line.split(" ") if x]
    return result


def read_script_lines(exec_file_path):
    """
    reads script from file
    if contains something
    else returns None
    """
    with open(exec_file_path) as file:
        return [line.rstrip() for line in file]


def find_in_container(container, exec_name):
    """
    """
    return search_in_folder(container, exec_name)


def create_archives(container):
    create_dir_if_missing(container.file)
    create_dir_if_missing(container.dir)
    create_dir_if_missing(container.zip)
    create_dir_if_missing(container.cache)
    create_dir_if_missing(container.execution)


def create_dir_if_missing(file):
    if not os.path.exists(file):
        os.mkdir(file)


def item_not_found(item_type, path):
    print("could not find", item_type, "[{}]".format(path))
    return None


# FILE EXTENSIONS

def apply_extension(file_name, extension):
    """Safely add extension to file name"""
    return file_name if str(file_name).endswith("." + extension) else "{}.{}".format(file_name, extension)


def apply_json_extension(file_name):
    """Safely add json extension to file name"""
    return apply_extension(file_name, "json")


def apply_txt_extension(file_name):
    """Safely add txt extension to file name"""
    return apply_extension(file_name, "txt")


# SAFE RETRIEVAL

# find usages
def safe_get_from_array(array, index):
    """if present returns index value of an array else None"""
    try:
        return array[index]
    except IndexError:
        return None


def safe_get_from_dict(dict_data, key):
    """if present returns key value of a dict else None"""
    try:
        return dict_data[key]
    except KeyError:
        return None


def safe_get_alias(data, group, key):
    """if present returns value of an alias of a certain group else None"""
    try:
        return data[group][key]
    except KeyError:
        return None


# search all paths under path
def search_in_folder(root_path, file_name):
    """
    search a file in a dir and its subdirs recursively
    returns:
    if found: file path
    else False
    """
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in [f for f in filenames if f == file_name]:
            return os.path.join(dirpath, filename)

    return None
