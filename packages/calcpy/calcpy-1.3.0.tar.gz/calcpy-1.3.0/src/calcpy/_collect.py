"""Collections."""

from math import inf


def convert_nested_dict_to_nested_list(data, /, maxdepth=inf):
    """Convert a nested dictionary to a nested list.

    Parameters:
        data (dict): Nested dictionary to convert.
        maxdepth (int): Maximum depth to convert to a nested list.

    Returns:
        list: A nested list representation of the nested dictionary.

    Example:
        >>> data = {"A": {"B": 1, "C": 2}, "D": {"E": 3, "F": 4}}
        >>> convert_nested_dict_to_nested_list(data)
        [['A', 'B', 1], ['A', 'C', 2], ['D', 'E', 3], ['D', 'F', 4]]
    """
    if maxdepth == 0:
        return [[data]]
    results = []
    for k in data:
        v = data[k]
        if isinstance(v, dict):
            lst = convert_nested_dict_to_nested_list(v, maxdepth-1)
            for e in lst:
                results.append([k] + e)
        else:
            results.append([k, v])
    return results
