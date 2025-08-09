from copy import copy
import functools

from .matcher import _get_matcher
from .typing import DictTypes
from ._it import pairwise
from ._seq import _unique_sequence
from ._op import _concat, concat


def union(*args, key=None):
    """Union of multiple parameters.

    This function can merge multiple ``dict``'s into one ``dict``. If two
    ``dict``'s ``d1`` and ``d2`` have the same key ``k``, ``union(d1, d2)``
    will use the value of ``d1[k]`` rather than ``d2[k]``, which differs from
    ``d1 | d2`` who takes ``d2[k]``.

    Parameters:
        *args
        key (callable)

    Examples:
        >>> union([1, 2, 3], [3, 2], [2, 4], [])
        [1, 2, 3, 4]
        >>> union((1, 2, 3), (3, 2), (2, 4), ())
        (1, 2, 3, 4)

        The following example considers a list and moves some of its elements to the front.

        >>> a = [1, 2, 3, 4, 5]  # the list
        >>> f = [3, 4]  # some elements that need to appear first
        >>> union(f, a)
        [3, 4, 1, 2, 5]

        Union of multiple ``dict``'s:

        >>> union({'a': 1, 'b': 2}, {'c': 13, 'a': 11}, {})
        {'a': 1, 'b': 2, 'c': 13}

        Use key:

        >>> union(["alpha", "beta"], ["gamma", "delta"], ["pi", "omega"], key=len)
        ['alpha', 'beta', 'pi']

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.union
    """
    matcher = _get_matcher(args[0], key=key)
    concated = _concat(*args, matcher=matcher, assemble=False)
    return _unique_sequence(concated, matcher=matcher, dissemble=False)


def isdisjoint(*args, key=None):
    """Check if the parameters are disjoint.

    Parameters:
        *args
        key (callable)

    Returns:
        bool:

    Examples:
        >>> isdisjoint([1, 2, 3], [2, 3, 4], [3, 4])
        False
        >>> isdisjoint([1, 2, 3], [4, 5, 6], [7, 8, 9])
        True

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.isdisjoint
    """
    concated = concat(*args, key=key)
    unioned = union(*args, key=key)
    return len(concated) == len(unioned)


def _wrapper2(fun, matcher):
    def f(loper, roper):
        loper = matcher.disassemble(loper)
        roper = matcher.disassemble(roper)
        results = fun(loper, roper, matcher)
        return matcher.assemble(results)
    return f


def _wrapper(fun):
    """Extend binary function to multi-ary function."""
    def f(*args, key=None):
        if len(args) == 0:
            return args
        matcher = _get_matcher(args[0], key=key)
        return functools.reduce(_wrapper2(fun, matcher=matcher), args)
    return f


def _wrapper_1dict(fun):
    """Support the case when the first parameter is a dict."""
    def f(*args, key=None):
        op = _wrapper(fun)
        if len(args) >= 1 and isinstance(args[0], DictTypes):
            arg = args[0]
            arglist = list(arg)
            params = list(args)
            params[0] = arglist
            keys = op(*params, key=key)
            results = copy(arg)
            for key in arglist:
                if key not in keys:
                    results.pop(key)
            return results
        return op(*args, key=key)
    return f


def _contains(seq, obj, matcher):
    for element in seq:
        if matcher.eq(obj, element):
            return True
    else:
        return False


def _intersection2(loper, roper, key=None, matcher=None):
    matcher = _get_matcher(loper, key=key, matcher=matcher)
    results = []
    for l in loper:  # noqa: E741
        if _contains(roper, l, matcher=matcher):
            results.append(l)
    return results


def _difference2(loper, roper, key=None, matcher=None):
    matcher = _get_matcher(loper, key=key, matcher=matcher)
    results = []
    for l in loper:  # noqa: E741
        if not _contains(roper, l, matcher=matcher):
            results.append(l)
    return results


def _symmetric_difference2(loper, roper, matcher):
    return concat(_difference2(loper, roper, matcher=matcher), _difference2(roper, loper, matcher=matcher))


def _issubset2(loper, roper, matcher):
    for l in loper:  # noqa: E741
        if not _contains(roper, l, matcher=matcher):
            return False
    return True


def _issuperset2(loper, roper, matcher):
    for r in roper:
        if not _contains(loper, r, matcher=matcher):
            return False
    return True


def _ispropersubset2(loper, roper, matcher):
    return _issubset2(loper, roper, matcher) and not _issuperset2(loper, roper, matcher)


def _ispropersuperset2(loper, roper, matcher):
    return _issuperset2(loper, roper, matcher) and not _issubset2(loper, roper, matcher)


def contains(values, /, *args, key=None):
    """Check if the first parameter contains the follow-up parameters.

    Parameters:
        values (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        *args
        key (callable, optional)

    Returns:
        bool:

    Examples:
        >>> contains([1, 2])   # return True when no elements to check
        True
        >>> contains([1, 2], 1)
        True
        >>> contains([1, 2], 3)
        False
        >>> contains([1, 2], 1, 2)
        True
        >>> contains([1, 2], 1, 2, 2)
        True
        >>> contains({'a': 1, 'b': 2}, 'a', 'b')
        True
        >>> contains({'a': 1, 'b': 2}, 'a', 'c')
        False
    """
    matcher = _get_matcher(values, key=key)
    for arg in args:
        if not _contains(values, arg, matcher=matcher):
            return False
    return True


intersection = _wrapper_1dict(_intersection2)
intersection.__doc__ = \
    """Intersect of multiple parameters.

    The first argument can be a ``dict``, while the following positions can not
    be a ``dict``. If the first argument is a ``dict``, it means to limit the keys
    of the first arugment within the list specified by the intersection of
    follow-up position arguments (if any).

    Parameters:
        *args
        key (callable)

    Examples:
        >>> intersection('abcd', 'edc')
        'cd'

        The case when the first argument is a ``dict``.

        >>> intersection({'a': 1, 'b': 2, 'c': 3})
        {'a': 1, 'b': 2, 'c': 3}
        >>> intersection({'a': 1, 'b': 2, 'c': 3}, ['a', 'c'])
        {'a': 1, 'c': 3}

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.intersection
    """

difference = _wrapper_1dict(_difference2)
difference.__doc__ = \
    """Exclude follow-up parameters from the first one.

    The first argument can be a ``dict``, while the following positions can not
    be a ``dict``. If the first argument is a ``dict``, it means to exclude all
    elements in the follow-up arguments out of the key of the first position
    argument.

    Parameters:
        *args
        key (callable)

    Examples:
        >>> difference('abcd', 'cat', 'bed')
        ''

        The case when the first argument is a ``dict``.

        >>> difference({'a': 1, 'b': 2, 'c': 3})
        {'a': 1, 'b': 2, 'c': 3}
        >>> difference({'a': 1, 'b': 2, 'c': 3}, ['b'])
        {'a': 1, 'c': 3}

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.difference
    """

symmetric_difference = _wrapper(_symmetric_difference2)
symmetric_difference.__doc__ = \
    """Pick elements that appear in odd number of parameters.

    Parameters:
        *args
        key (callable)

    Examples:
        >>> symmetric_difference([1, 2, 3], [2, 3, 4], [3, 4])
        [1, 3]
        >>> symmetric_difference('hello', 'he', 'okay')
        'llkay'

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.symmetric_difference
    """


def _allpairwise_wrapper(fun):
    """Wrapper for better function signatures."""
    def f(*args, key=None):
        if len(args) <= 1:
            return True
        matcher = _get_matcher(args[0], key=key)
        return all(fun(*p, matcher=matcher) for p in pairwise(args))
    return f


issubset = _allpairwise_wrapper(_issubset2)
issubset.__doc__ = \
    """Check if the parameter is a subset of the follow-up parameter.

    Parameters:
        *args
        key (callable)

    Returns:
        bool:

    Examples:
        >>> issubset([1, 2, 3], [1, 2, 3, 4, 5])
        True
        >>> issubset([], [1, 2, 3], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
        True
        >>> issubset([1, 2, 3], [1, 5, 6])
        False

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.issubset
    """

issuperset = _allpairwise_wrapper(_issuperset2)
issuperset.__doc__ = \
    """Check if the parameter is a superset of the follow-up parameter.

    Parameters:
        *args
        key (callable)

    Returns:
        bool:

    Examples:
        >>> issuperset([1, 2, 3, 4, 5], [1, 2, 3])
        True
        >>> issuperset([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3], [])
        True
        >>> issuperset([1, 2, 3], [4, 5, 6])
        False

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.issuperset
    """

ispropersubset = _allpairwise_wrapper(_ispropersubset2)
ispropersubset.__doc__ = \
    """Check if the parameter is a proper subset of the follow-up parameter.

    Parameters:
        *args
        key (callable)

    Returns:
        bool:

    Examples:
        >>> ispropersubset([1, 2, 3], [1, 2, 3, 4, 5])
        True
        >>> ispropersubset([], [1, 2, 3], [1, 2, 3, 4], [1, 2, 3, 4, 5])
        True
        >>> ispropersubset([1, 2, 3], [1, 5, 6])
        False
        >>> ispropersubset([1, 2, 3], [1, 2, 3])
        False
    """

ispropersuperset = _allpairwise_wrapper(_ispropersuperset2)
ispropersuperset.__doc__ = \
    """Check if the parameter is a proper superset of the follow-up parameter.

    Parameters:
        *args
        key (callable)

    Returns:
        bool:

    Examples:
        >>> ispropersuperset([1, 2, 3, 4, 5], [1, 2, 3])
        True
        >>> ispropersuperset([1, 2, 3, 4, 5], [1, 2, 3, 4], [1, 2, 3], [])
        True
        >>> ispropersuperset([1, 2, 3], [4, 5, 6])
        False
        >>> ispropersuperset([1, 2, 3], [1, 2, 3])
        False
    """
