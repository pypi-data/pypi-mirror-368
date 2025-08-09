from extepy import fillwhen


def fillnan(value=0):
    """Decorator that returns a default value if the result is nan.

    Parameters:
        value : Value to return if the result is nan.

    Returns:
        callable:

    Examples:
        >>> @fillnan(-1)
        ... def f(x):
        ...     return x
        >>> f(None)  # return None, print nothing.
        >>> from math import nan
        >>> f(nan)
        -1
        >>> f(False)
        False
        >>> f(0)
        0
    """
    from ._math import isnan

    def decorator(f):
        return fillwhen(isnan, value)(f)
    return decorator
