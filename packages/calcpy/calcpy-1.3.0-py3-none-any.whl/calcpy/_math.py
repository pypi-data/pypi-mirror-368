import functools
import itertools
import numbers
import operator

from extepy import fillerr
import numpy as np


def isnan(value):
    """Check if a value is NaN.

    Support all types.

    Parameters:
        value: Any value.

    Returns:
        True if the value is NaN, False otherwise.

    Example:
        >>> isnan(None)
        False
        >>> isnan(float('nan'))
        True
        >>> isnan(1)
        False
        >>> isnan("a")
        False
    """
    checker = fillerr(False)(np.isnan)
    result = bool(checker(value))
    return result


def add(*args, default=0):
    """Add all arguments together.

    Parameters:
        *args: Any number of arguments.
        default: Default value to return if no arguments are provided.

    Returns:
        Sum of all arguments.

    Example:
        >>> add()
        0
        >>> add(1)
        1
        >>> add(1, 2, 3)
        6

    See also:
        https://docs.python.org/3/library/operator.html#operator.add
    """
    return sum(args, start=default)


def mul(*args, default=1):
    """Multiply all arguments together.

    Parameters:
        *args: Any number of arguments.
        default: Default value to return if no arguments are provided.

    Returns:
        Product of all arguments.

    Example:
        >>> mul()
        1
        >>> mul(2)
        2
        >>> mul(1, 2, 3)
        6

    See also:
        https://docs.python.org/3/library/operator.html#operator.mul
    """
    return functools.reduce(operator.mul, args, default)


def matmul(*args, default=1):
    """Matrix multiplication of all arguments.

    Parameters:
        *args: Any number of arguments.
        default: Default value to return if no arguments are provided.

    Returns:
        Matrix product of all arguments.

    Example:
        >>> import numpy as np
        >>> matmul(np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]]))
        array([[19, 22],
               [43, 50]])

    See also:
        https://docs.python.org/3/library/operator.html#operator.matmul
    """
    if len(args) == 0:
        return default

    try:
        from operator import matmul as _matmul
    except ImportError:
        from numpy import matmul as _matmul
    result = default * functools.reduce(_matmul, args)
    return result


try:
    from math import sumprod
except ImportError:
    def sumprod(*args):
        """Calculate the sum of products of all elements in an iterable.

        Parameters:
            iterable : An iterable object.
            start : Starting value.

        Returns:
            Sum of products of all elements in the iterable.

        Example:
            >>> sumprod([1, 2, 3])
            6
            >>> sumprod([1, 2, 3], [1, 2, 3])
            14
            >>> sumprod([1, 2, 3], [1, 2, 3], [1, 2, 3])
            36
        """
        return sum(itertools.starmap(mul, zip(*args)))


def matprod(values, start=1):
    """Matrix product of all arguments.

    Parameters:
        *args: Any number of arguments.
        start: Starting value.

    Returns:
        Matrix product of all arguments.

    Example:
        >>> import numpy as np
        >>> matprod([np.array([[1, 2], [3, 4]])])
        array([[1, 2],
            [3, 4]])
        >>> matprod([np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]])])
        array([[19, 22],
            [43, 50]])
    """
    if not isinstance(start, numbers.Number):
        raise NotImplementedError("We only support number as start value.")
    if len(values) == 0:
        return start
    return start * functools.reduce(matmul, values)


try:
    from math import gcd as _gcd2  # in Python < 3.9, it supports only 2 arguments.
except ImportError:
    def _gcd2(a, b):
        while b:
            a, b = b, a % b
        return a


def gcd(*args, empty=0):
    """Calculate the greatest common divisor of all arguments.

    Parameters:
        *args: Any number of arguments.
        empty: Value to return if no arguments are provided.

    Returns:
        Greatest common divisor of all arguments.

    Example:
        >>> gcd()
        0
        >>> gcd(12)
        12
        >>> gcd(12, 15)
        3
        >>> gcd(12, 15, 21)
        3
    """
    if len(args) == 0:
        return empty

    return functools.reduce(_gcd2, args)


try:
    from math import lcm
except ImportError:
    def lcm(*args, empty=1):
        """Calculate the least common multiple of all arguments.

        Parameters:
            *args: Any number of arguments.
            empty: Value to return if no arguments are provided.

        Returns:
            Least common multiple of all arguments.

        Example:
            >>> lcm()
            1
            >>> lcm(12, 15)
            60
            >>> lcm(12, 15, 21)
            420
        """
        if len(args) == 0:
            return empty

        def _lcm(a, b):
            return a * b // _gcd2(a, b)
        return functools.reduce(_lcm, args)


try:
    from math import fma
except ImportError:
    def fma(x, y, z):
        """Calculate the fused multiply-add of three numbers.

        Parameters:
            x: First number.
            y: Second number.
            z: Third number.

        Returns:
            Result of x * y + z.

        Examples:
            >>> fma(2, 3, 4)
            10
            >>> fma(2.5, 3.5, 4.5)
            13.25
        """
        return x * y + z


try:
    from math import cbrt
except ImportError:
    def cbrt(x):
        """Calculate the cube root of a number.

        Parameters:
            x: Number.

        Returns:
            Cube root of x.

        Example:
            >>> cbrt(8)
            2.0
            >>> cbrt(27)
            3.0

        See also:
            https://docs.python.org/3/library/math.html#math.cbrt
        """
        return x ** (1/3)

try:
    from math import exp2
except ImportError:
    def exp2(x):
        """Calculate the base-2 exponential of a number.

        Parameters:
            x: Number

        Returns:
            The base-2 exponential of x.

        Examples:
            >>> exp2(1)
            2
            >>> exp2(2.0)
            4.0

        See also:
            https://docs.python.org/3/library/math.html#math.exp2
        """
        return 2 ** x


def minmax(*args, **kwargs):
    """Get both min and max.

    Examples:
        >>> minmax([1, 3, 4])
        (1, 4)
        >>> minmax(1, 3, 4)
        (1, 4)
    """
    return min(*args, **kwargs), max(*args, **kwargs)
