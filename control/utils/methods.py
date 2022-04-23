from .retrieve_utils import search_in_folder


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
    # if search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name):
    #     with open(search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name)) as file:
    #         return [line.rstrip() for line in file]
    with open(exec_file_path) as file:
        return [line.rstrip() for line in file]


def find_in_container(container, exec_name):
    """
    """
    return search_in_folder(container, exec_name)
