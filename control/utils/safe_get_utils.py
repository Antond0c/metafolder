def safe_get_from_array(array, index):
    """
    returns indexes value of an array
    only if present
    """
    try:
        return array[index]
    except IndexError:
        return None


# todo: check if works on dictionaries
def safe_get_alias(data, group, key):
    """
    returns value of an alias of a certain group
    only if present
    """
    try:
        return data[group][key]
    except KeyError:
        return None