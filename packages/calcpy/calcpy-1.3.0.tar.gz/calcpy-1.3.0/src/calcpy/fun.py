from functools import wraps

from extepy import cycleperm as _cycleperm, swap as _swap, prioritize as _prioritize
from extepy import pack, unpack, skewer, repeat  # noqa: F401


def cycleperm(cycle=()):
    """Callable that swaps position parameters according to cyclc notation.

    Parameters:
        cycle (list | tuple): List of indices to swap.

    Returns:
        Callable[callable, callable]: a callable that swaps a callable so that
            its arguments are swapped according to cycle notation.

    Examples:

        Permutate a function.

        >>> permed = cycleperm(cycle=[0, 1])(range)
        >>> permed(3, 2, 6)
        range(2, 3, 6)

        >>> permed = cycleperm(cycle=[1, 2])(range)
        >>> permed(3, 2, 6)
        range(3, 6, 2)

        Use as a decorator.

        >>> @cycleperm(cycle=[0, 1])
        ... def g(a, b):
        ...    return (a + b) * (a - b)
        >>> g(2, 3)
        5
    """
    def wrapper(f):

        @wraps(f)
        def fun(*args, **kwargs):
            args = _cycleperm(list(args), cycle=cycle)
            result = f(*args, **kwargs)
            return result
        return fun

    return wrapper


def swap(i=0, j=1):
    """Callable that swaps positional arguments in a pair.

    Parameters:
        i (int): Index of the argument to swap.
        j (int): Index of another argument to swap.

    Returns:
        Callable[callable, callable]: a callable that swaps a callable so that two designated arguments are swapped.

    Examples:

        Swap arguments of a callable:

        >>> swapped = swap()(range)
        >>> swapped(3, 2, 6)
        range(2, 3, 6)

        >>> swapped = swap(i=1, j=2)(range)
        >>> swapped(3, 2, 6)
        range(3, 6, 2)

        Use as a decorator.

        >>> @swap()
        ... def g(a, b):
        ...     return (a + b) * (a - b)
        >>> g(2, 3)
        5
    """
    def wrapper(f):
        @wraps(f)
        def fun(*args, **kwargs):
            args = _swap(list(args), i=i, j=j)
            result = f(*args, **kwargs)
            return result
        return fun
    return wrapper


def prioritize(*index, dup="unique"):
    """Move some position parameters to the beginning.

    Parameters:
        index (int | list[int]): Index of the elements to move to the beginning.
            The index can be negative.
        dup (``{"unique", "raise"}``): Specify how to deal with the case that
            the same positional argument is prioritized mutliple times.
            ``"unique"``: The same element will appear only once.
            ``"raise"``: Raise an error.

    Returns:
        Callable[callable, callable]:

    Examples:

        Use as a decorator. Move a single positional parameter to the front.

        >>> @prioritize(1)
        ... def fun(a, b, c):
        ...     return [a, b, c]
        >>> fun(1, 2, 3)
        [2, 1, 3]

        Use as a decorator. Move multiple positional parameters to the front.

        >>> @prioritize(1, -1)  # has duplicated for this particular function
        ... def fun(a, b, c):
        ...     return [a, b, c]
        >>> fun(1, 2, 3)
        [2, 3, 1]

        Use as a decorator. Drop duplicates.

        >>> @prioritize(1, -2)
        ... def fun(a, b, c):
        ...     return [a, b, c]
        >>> fun(1, 2, 3)
        [2, 1, 3]
    """
    assert dup in ["unique", "raise"]

    def wrapper(f):
        @wraps(f)
        def fun(*args, **kwargs):
            args = _prioritize(args, index=index, dup=dup)
            result = f(*args, **kwargs)
            return result
        return fun
    return wrapper


def dispatch(dispatcher=None, /, *, agg=None, fix_begin=0):
    """Return callable that calculates using the first and each of the rest parameters with optional aggregation.

    Parameters:
        dispatcher (Callable[iterable, list[iterable]]): Callable that accepts
            an iterable and returns a list of iterables.
            By default, the dispatcher is ``itertools.batched(*, n=1)``.
        agg (callable, optional): Aggretion.
        fix_begin (int): Number of parameters to fix.

    Returns:
        Callable[callable, callable]: a callable that swaps a callable so that it is called repeated n times.

    Examples:

        Apply an operator for each of positional parameter

        >>> foreach = dispatch()
        >>> dispatched = foreach(abs)
        >>> list(dispatched(-2, 3, -4, 5))
        [2, 3, 4, 5]

        Apply an operator for each of positional parameter, and then multiple results all together

        >>> from math import prod
        >>> productionize = dispatch(agg=prod)
        >>> dispatched = productionize(abs)
        >>> dispatched(-2, 3, -4, 5)  # 2 * 3 * 4 * 5
        120

        Apply an operator for every two adjacent positional parameters, and then sum up

        >>> from calcpy import pairwise  # from itertools import pairwise
        >>> pairwise_sum = dispatch(pairwise, agg=sum)
        >>> import operator
        >>> dispatched = pairwise_sum(operator.mul)
        >>> dispatched(-2, 3, -4, 5)  # -2 * 3 + 3 * -4 + -4 * 5
        -38

        Apply the first parameter to each of other positional parameter, and then sum up

        >>> everyother_sum =  dispatch(agg=sum, fix_begin=1)
        >>> dispatched = everyother_sum(operator.mul)
        >>> dispatched(-2, 3, -4, 5)  # -2 * 3 + -2 * -4 + -2 * 5
        -8

        Extend an binary boolean operator to a multiple operator,
        return True only when all adjacent positional parameters return True.

        >>> pairwise_all = dispatch(pairwise, agg=all)
        >>> dispatched = pairwise_all(operator.lt)
        >>> dispatched(-2, 3, -4, 5)
        False

        Use as a decorator.

        >>> @dispatch(pairwise, agg=all)
        ... def fraceq(loper, roper):  # check whether the fractional parts are equal.
        ...     return (loper % 1) == (roper % 1)
        >>> fraceq()   # no inputs, return True
        True
        >>> fraceq(0)   # one input only, return True
        True
        >>> fraceq(0.5, 1.5, 2.5)
        True
        >>> fraceq(0.1, 2.3)
        False
    """
    def wrapper(f):
        @wraps(f)
        def fun(*args, **kwargs):
            fixed_args = args[:fix_begin]
            iter_args = args[fix_begin:]
            if dispatcher is None:
                iter_arguments = ((iter_arg,) for iter_arg in iter_args)
            else:
                iter_arguments = dispatcher(iter_args)
            results = (f(*fixed_args, *arguments, **kwargs) for arguments in iter_arguments)
            if agg is not None:
                results = agg(results)
            return results
        return fun
    return wrapper
