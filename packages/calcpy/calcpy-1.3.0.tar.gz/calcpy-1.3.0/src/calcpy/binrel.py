"""Binary relationship."""
from functools import wraps


def sym_part(r, /):
    """Get the symmetric part of a binary relationship.

    Returns r(a, b) and r(b, a) for relationship r(a, b).

    Parameters:
        r (Callable[[Any, Any], bool]): binary relationship,
            a callable that accepts two positional arguments and returns a bool.

    Returns:
        Callable[[Any, Any], bool]:

    Examples:
        >>> def fracle(a, b):  # <= on fractional part
        ...     return (a % 1) <= (b % 1)
        >>> fraceq = sym_part(fracle)   # == on fractional part
        >>> fraceq(0.5, 1.5)
        True
        >>> fraceq(0.1, 2.3)
        False
    """
    @wraps(r)
    def fun(a, b):
        return r(a, b) and r(b, a)
    return fun


def asym_part(r, /):
    """Get the asymmetric part of a binary relationship.

    Returns r(a, b) and not r(b, a) for relationship r(a, b).

    Parameters:
        r (Callable[[Any, Any], bool]): binary relationship,
            a callable that accepts two positional arguments and returns a bool.

    Returns:
        Callable[[Any, Any], bool]:

    Examples:
        >>> def fracle(a, b):  # <= on fractional part
        ...     return (a % 1) <= (b % 1)
        >>> fraclt = asym_part(fracle)   # == on fractional part
        >>> fraclt(0.5, 1.5)
        False
        >>> fraclt(0.1, 2.3)
        True
    """
    @wraps(r)
    def fun(a, b):
        return r(a, b) and not r(b, a)
    return fun
