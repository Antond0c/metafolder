def safe_get_from_array(array, index):
    """if present returns indexes value of an array else None"""
    try:
        return array[index]
    except IndexError:
        return None


def safe_get_alias(data, group, key):
    """if present value of an alias of a certain group"""
    try:
        return data[group][key]
    except KeyError:
        return None