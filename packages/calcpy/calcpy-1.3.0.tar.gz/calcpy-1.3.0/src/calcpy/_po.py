"""Partial order."""


def minimal(values, *, lt):
    """Returns the minimal elements of a poset.

    Parameters:
        values (iterable): Values to find the minimal elements.
        lt (Callable[[Any, Any], bool]): Less-than checker.

    Returns:
        list: Minimal elements.

    Examples:
        >>> def isproperfactor(a, b):
        ...     return (b % a == 0) and (a != b)
        >>> minimal([2, 3, 4, 5, 6, 7, 8, 9], lt=isproperfactor)
        [2, 3, 5, 7]
    """
    results = []
    for result in values:
        for value in values:
            if lt(value, result):
                break
        else:
            results.append(result)
    return results


def maximal(values, *, lt):
    """Returns the maximal elements of a poset.

    Parameters:
        values (iterable): Values to find the maximal elements.
        lt (Callable[[Any, Any], bool]): Less-than checker.

    Returns:
        list: Maximal elements.

    Examples:
        >>> def isproperfactor(a, b):
        ...     return (b % a == 0) and (a != b)
        >>> maximal([2, 3, 4, 5, 6, 7, 8, 9], lt=isproperfactor)
        [5, 6, 7, 8, 9]
    """
    results = []
    for result in values:
        for value in values:
            if lt(result, value):
                break
        else:
            results.append(result)
    return results
