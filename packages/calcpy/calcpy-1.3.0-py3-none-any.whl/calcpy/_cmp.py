"""Comparison."""

from functools import cmp_to_key
import operator


def key_to_cmp(key):
    """Convert a key function to a comparison function.
    The comparison function will compare two objects based on the key function.

    Parameters:
        key (callable): A function that takes an object and returns a value that can be compared.

    Returns:
        callable: A comparison function that takes two objects and
            returns 1 if the first is greater than or equal to the second,
            -1 if the first is less than the second, and 0 if they are equal.

    Examples:
        >>> cmp = key_to_cmp(len)
        >>> cmp("Hello", "World")
        0
        >>> cmp("Hello", "Python")
        -1
    """
    def cmp(a, b):
        if key is not None:
            a = key(a)
            b = key(b)
        if a < b:
            result = -1
        elif a > b:
            result = 1
        else:
            result = 0
        return result
    return cmp


def eq_to_cmp(eq=operator.eq):
    """Convert an equality function to a comparison function.

    The comparison function will return 0 if the two objects are equal, and 1 otherwise.

    Parameters:
        eq (callable): A function that takes at least two arguments and
            returns True if the first two arguments are equal, False otherwise.

    Returns:
        callable: A comparison function that takes two objects and
            returns 1 if the first is greater than or equal to the second,
            -1 if the first is less than the second, and 0 if they are equal.

    Note:
        This function is experimental and may be changed in the future.

    Examples:
        >>> cmp = eq_to_cmp(operator.eq)
        >>> cmp(1, 2)
        1
        >>> cmp(1, 1)
        0
        >>> cmp(2, 1)
        1
    """
    def cmp(a, b):
        return int(not eq(a, b))
    return cmp


def ne_to_cmp(ne=operator.ne):
    """Convert a non-equality function to a comparison function.

    The comparison function will return 0 if the two objects are not equal, and 1 otherwise.

    Parameters:
        ne (callable): A function that takes two arguments and
            returns True if the first two arguments are not equal, False otherwise.

    Returns:
        callable: A comparison function that takes two objects and
            returns 1 if the first is greater than or equal to the second,
            -1 if the first is less than the second, and 0 if they are equal.

    Note:
        This function is experimental and may be changed in the future.

    Examples:
        >>> cmp = ne_to_cmp(operator.ne)
        >>> cmp(1, 2)
        1
        >>> cmp(1, 1)
        0
        >>> cmp(2, 1)
        1
    """
    def cmp(a, b):
        return int(ne(a, b))
    return cmp


def lt_to_cmp(lt=operator.le):
    """Convert a less-than function to a comparison function.

    Parameters:
        lt (callable): A function that takes at least two arguments and
            returns True if the first is less than the second, False otherwise.

    Returns:
        callable: A comparison function that takes two objects and
            returns 1 if the first is greater than or equal to the second,
            -1 if the first is less than the second, and 0 if they are equal.

    Examples:
        >>> cmp = lt_to_cmp(operator.lt)
        >>> cmp(1, 2)
        -1
        >>> cmp(1, 1)
        0
        >>> cmp(2, 1)
        1
    """
    def cmp(a, b):
        if lt(a, b):
            return -1
        elif lt(b, a):
            return 1
        else:
            return 0
    return cmp


def le_to_cmp(le=operator.le):
    """Convert a less-than-or-equal-to function to a comparison function.

    Parameters:
        le (callable): A function that takes at least two arguments and
            returns True if the first is less than or equal to the second, False otherwise.

    Returns:
        callable: A comparison function that takes two objects and
            returns 1 if the first is greater than or equal to the second,
            -1 if the first is less than the second, and 0 if they are equal.

    Examples:
        >>> cmp = le_to_cmp(operator.le)
        >>> cmp(1, 2)
        -1
        >>> cmp(1, 1)
        0
        >>> cmp(2, 1)
        1
    """
    def cmp(a, b):
        if not le(a, b):
            return 1
        elif not le(b, a):
            return -1
        else:
            return 0
    return cmp


def gt_to_cmp(gt=operator.ge):
    """Convert a greater-than function to a comparison function.

    Parameters:
        gt (callable): A function that takes at least two arguments and
            returns True if the first is greater than the second, False otherwise.

    Returns:
        callable: A comparison function that takes two objects and
            returns 1 if the first is greater than or equal to the second,
            -1 if the first is less than the second, and 0 if they are equal.

    Examples:
        >>> cmp = gt_to_cmp(operator.gt)
        >>> cmp(1, 2)
        -1
        >>> cmp(1, 1)
        0
        >>> cmp(2, 1)
        1
    """
    def cmp(a, b):
        if gt(a, b):
            return 1
        elif gt(b, a):
            return -1
        else:
            return 0
    return cmp


def ge_to_cmp(ge=operator.ge):
    """Convert a greater-than-or-equal-to function to a comparison function.

    Parameters:
        ge (callable): A function that takes at least two arguments and
            returns True if the first is greater than or equal to the second, False otherwise.

    Returns:
        callable: A comparison function that takes two objects and
            returns 1 if the first is greater than or equal to the second,
            -1 if the first is less than the second, and 0 if they are equal.

    Examples:
        >>> cmp = ge_to_cmp(operator.ge)
        >>> cmp(1, 2)
        -1
        >>> cmp(1, 1)
        0
        >>> cmp(2, 1)
        1
    """
    def cmp(a, b):
        if not ge(a, b):
            return -1
        elif not ge(b, a):
            return 1
        else:
            return 0
    return cmp


def eq_to_key(eq=operator.eq):
    """Convert an equality function to a key function.

    Parameters:
        eq (callable): A function that takes two at least arguments and
            returns True if the arguments are equal, False otherwise.

    Returns:
        callable:

    Note:
        This function is experimental and may change in the future.
    """
    cmp = eq_to_cmp(eq)
    key = cmp_to_key(cmp)
    return key


def ne_to_key(ne=operator.ne):
    """Convert an equality function to a key function.

    Parameters:
        eq (callable): A function that takes two arguments and
            returns True if the arguments are equal, False otherwise.

    Returns:
        callable:

    Note:
        This function is experimental and may change in the future.
    """
    cmp = ne_to_cmp(ne)
    key = cmp_to_key(cmp)
    return key


def lt_to_key(lt=operator.lt):
    """Convert a less-than function to a key function.

    Parameters:
        lt (callable): A function that takes two arguments and
            returns True if the first is less than the second, False otherwise.

    Returns:
        callable:

    Examples:
        >>> import operator
        >>> key = lt_to_key(operator.lt)
        >>> sorted([3, 1, 2], key=key)
        [1, 2, 3]
    """
    cmp = lt_to_cmp(lt)
    key = cmp_to_key(cmp)
    return key


def le_to_key(le=operator.le):
    """Convert a less-than-or-equal-to function to a key function.

    Parameters:
        le (callable): A function that takes two arguments and
            returns True if the first is less than or equal to the second, False otherwise.

    Returns:
        callable:

    Examples:
        >>> import operator
        >>> key = le_to_key(operator.le)
        >>> sorted([3, 1, 2], key=key)
        [1, 2, 3]
    """
    cmp = le_to_cmp(le)
    key = cmp_to_key(cmp)
    return key


def gt_to_key(gt=operator.gt):
    """Convert a greater-than function to a key function.

    Parameters:
        gt (callable): A function that takes two arguments and
            returns True if the first is greater than the second, False otherwise.

    Returns:
        callable:

    Examples:
        >>> import operator
        >>> key = gt_to_key(operator.gt)
        >>> sorted([3, 1, 2], key=key)
        [1, 2, 3]
    """
    cmp = gt_to_cmp(gt)
    key = cmp_to_key(cmp)
    return key


def ge_to_key(ge=operator.ge):
    """Convert a greater-than-or-equal-to function to a key function.

    Parameters:
        ge (callable): A function that takes two arguments and
            returns True if the first is greater than or equal to the second, False otherwise.

    Returns:
        callable:

    Examples:
        >>> import operator
        >>> key = ge_to_key(operator.ge)
        >>> sorted([3, 1, 2], key=key)
        [1, 2, 3]
    """
    cmp = ge_to_cmp(ge)
    key = cmp_to_key(cmp)
    return key


def _cmp_to_gleten(gleten_name):
    # gleten is short for the collections of ["le", "lt", "ge", "gt", "eq", "ne"].

    def from_cmp(cmp):
        def f(a, b):
            result = cmp(a, b)
            gleten = getattr(operator, gleten_name)
            return gleten(result, 0)
        return f
    from_cmp.__name__ = f"cmp_to_{gleten_name}"
    from_cmp.__doc__ = \
        f"""Convert a cmp= function to a {gleten_name}= function.

        Parameters:
            cmp (callable): A comparison function that takes two arguments and
                returns -1, 0, or 1 when the first is less than, equal to, or greater than the second.

        Returns:
            callable:

        Examples:
            >>> def cmp(a, b):
            ...     return (a > b) - (a < b)
            >>> {gleten_name} = cmp_to_{gleten_name}(cmp)
            >>> {gleten_name}(1, 2)
            {bool(getattr(operator, gleten_name)(1, 2))}
        """
    return from_cmp


cmp_to_eq = _cmp_to_gleten("eq")
cmp_to_ne = _cmp_to_gleten("ne")
cmp_to_lt = _cmp_to_gleten("lt")
cmp_to_le = _cmp_to_gleten("le")
cmp_to_gt = _cmp_to_gleten("gt")
cmp_to_ge = _cmp_to_gleten("ge")


def _key_to_gleten(gleten_name):
    # gleten is short for the collections of ["le", "lt", "ge", "gt", "eq", "ne"].

    def from_key(key=None):
        def f(a, b):
            if key is not None:
                a = key(a)
                b = key(b)
            gleten = getattr(operator, gleten_name)
            return gleten(a, b)
        return f
    from_key.__name__ = f"key_to_{gleten_name}"
    from_key.__doc__ = \
        f"""Convert a key= function to a {gleten_name} function.

        Parameters:
            key (callable):

        Returns:
            callable: A function that takes two arguments and returns True or False based on the comparison.

        Examples:
            >>> {gleten_name} = key_to_{gleten_name}(len)
            >>> {gleten_name}("Hello", "World")
            {bool(getattr(operator, gleten_name)(5, 5))}
        """
    return from_key


key_to_eq = _key_to_gleten("eq")
key_to_ne = _key_to_gleten("ne")
key_to_lt = _key_to_gleten("lt")
key_to_le = _key_to_gleten("le")
key_to_gt = _key_to_gleten("gt")
key_to_ge = _key_to_gleten("ge")
