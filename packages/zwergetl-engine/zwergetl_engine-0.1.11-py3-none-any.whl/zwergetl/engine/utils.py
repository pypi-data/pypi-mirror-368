# various utility functions


def get_field_index(field_name, meta_data):
    """Returns field index in metadata, -1 if not found"""
    res = -1
    cnt = 0
    for fld in meta_data:
        cur_name = fld['name']
        if cur_name == field_name:
            res = cnt
            break
        cnt += 1
    return res

def get_index(name, list_of_names):
    """Returns index of a given string in a list of names, or -1 if not found
    """
    res = -1
    for item in list_of_names:
        if item == name:
            res = list_of_names.index(item)
            break
    return res


def convert_to_list_if_its_not(list_of_values):
    """Converts a string of comma-delimited values to list.
    If list_of_values is not a str, returns it as it is.
    If list_of_values is None, returns None
    """
    res = list_of_values

    if isinstance(list_of_values, str):
        res = list_of_values.split(',')

    return res


def any2str(value, data_type, format_mask=None):
    """
    Converts any zwerg data type to string
    """
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    if data_type is None:
        raise Exception("data_type must not be None")

    if value is None:
        ret_val = ""
    else:
        ret_val = value
    
    if data_type == 'integer':
        if value != "":
            ret_val = str(value)
    elif data_type == 'decimal':
        if value != "":
            ret_val = str(value)
    elif data_type == 'date':
        if value != "":
            fmt = format_mask
            if fmt is None:
                fmt = DEFAULT_DATE_FORMAT
                ret_val = value.strftime(fmt)

    return ret_val
