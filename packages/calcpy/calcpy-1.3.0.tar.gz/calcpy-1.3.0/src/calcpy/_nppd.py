"""Extensions to numpy and pandas."""
import datetime
from math import inf
from numbers import Number
import sys

import numpy as np
import pandas as pd

from .typing import ListLike, NDFrame


def overall_equal(loper, roper):
    """Check whether two operands are exactly equal as a whole.

    It behaves like ``np.array_equal`` for ``np.ndarray``, and
    ``loper.equals(roper)`` for ``pd.Series`` and ``pd.DataFrame``.

    Parameters:
        loper (number | list | tuple | np.ndarray | pd.Series | pd.DataFrame):
        roper (number | list | tuple | np.ndarray | pd.Series | pd.DataFrame):

    Returns:
        bool:

    Examples:

        Compare lists.

        >>> overall_equal([1, 2, 3], [1, 2, 3])
        True

        Compare ``pd.DataFrame``.

        >>> import pandas as pd
        >>> df = pd.DataFrame({"A": 1, "B": 2}, index=[0])
        >>> overall_equal(df, df+0)
        True
        >>> overall_equal(df, df+1)
        False
        >>> overall_equal(df, df.iloc[:, 0])
        False
        >>> overall_equal(df["A"], df["B"]-1)
        True
    """
    if not isinstance(loper, type(roper)):
        return False
    if isinstance(loper, NDFrame):
        return loper.equals(roper)
    if isinstance(loper, np.ndarray):
        return np.array_equal(loper, roper)
    return loper == roper


def shape(arg):
    """Get the shape of an argument.

    Parameters:
        arg

    Returns:
        tuple:

    Examples:
        >>> shape(1)
        ()
        >>> shape([1, 2, 3])
        (3,)
        >>> shape(np.array([1, 2, 3]))
        (3,)
        >>> shape(pd.Series([1, 2, 3]))
        (3,)
        >>> shape(pd.DataFrame({"A": 1, "B": 2}, index=[0]))
        (1, 2)
    """
    if hasattr(arg, "shape"):
        return arg.shape
    if hasattr(arg, "__len__"):
        return (len(arg),)
    return ()


def ndim(arg):
    """Get the number of dimensions of an argument.

    Parameters:
        arg

    Returns:
        int:

    Examples:
        >>> ndim(1)
        0
        >>> ndim([1, 2, 3])
        1
        >>> ndim(np.array([1, 2, 3]))
        1
        >>> ndim(pd.Series([1, 2, 3]))
        1
        >>> ndim(pd.DataFrame({"A": 1, "B": 2}, index=[0]))
        2
    """
    if hasattr(arg, "ndim"):
        return arg.ndim
    if hasattr(arg, "__len__"):
        return 1
    return 0


def size(arg):
    """Get the size of an argument.

    Parameters:
        arg

    Returns:
        int:

    Examples:
        >>> size(1)
        1
        >>> size([1, 2, 3])
        3
        >>> size(np.array([1, 2, 3]))
        3
        >>> size(pd.Series([1, 2, 3]))
        3
        >>> size(pd.DataFrame({"A": 1, "B": 2}, index=[0]))
        2
    """
    if hasattr(arg, "size"):
        return arg.size
    if hasattr(arg, "__len__"):
        return len(arg)
    return 1


def empty(arg):
    """Check whether it is empty.

    Parameters:
        arg:

    Returns:
        bool:

    Examples:
        >>> empty(1)
        False
        >>> empty([])
        True
        >>> empty([1, 2, 3])
        False
        >>> empty(np.array([1, 2, 3]))
        False
        >>> empty(pd.Series([1, 2, 3]))
        False
        >>> empty(pd.DataFrame({"A": 1, "B": 2}, index=[0]))
        False
    """
    return size(arg) == 0


def full_like(template, fill_value, **kwargs):
    """Create a np.array or pd.Series or pd.DataFrame with the same shape as template.

    Parameters:
        template (list | tuple | np.ndarray | pd.Series | pd.DataFrame):
        fill_value : Value to populate.
        **kwargs: Keyword arguments for ``np.full_alike()``, ``pd.Series()``, or ``pd.DataFrame()``.

    Returns:
        list | tuple | np.ndarray | pd.Series | pd.DataFrame:

    Raises:
        TypeError:

    Examples:

        Create list and tuple.

        >>> full_like([1, 2, 3], 0)
        [0, 0, 0]
        >>> full_like((1, 2, 3), 0)
        (0, 0, 0)

        Create ``np.array``.

        >>> full_like(np.array([1, 2, 3]), 0)
        array([0, 0, 0])

        Create ``pd.Series`` and ``pd.DataFrame``.

        >>> full_like(pd.Series([1, 2, 3]), 0)
        0    0
        1    0
        2    0
        dtype: int64
        >>> full_like(pd.DataFrame({"A": 1, "B": 2}, index=[0]), 0)
              A  B
        0     0  0
    """
    if isinstance(template, (list, tuple)):
        if size(fill_value) == 1:
            values = [fill_value] * size(template)
        else:
            values = fill_value
        return type(template)(values)
    if isinstance(template, np.ndarray):
        return np.full_like(template, fill_value, **kwargs)
    if isinstance(template, pd.Series):
        return pd.Series(fill_value, index=template.index, name=template.name, **kwargs)
    if isinstance(template, pd.DataFrame):
        return pd.DataFrame(fill_value, index=template.index, columns=template.columns, **kwargs)
    raise ValueError(f"Unknown template types {type(template)}.")


def broadcast_first(fun):
    """Decorator for supporting ``np.ndarray``, ``pd.Series``, and ``pd.DataFrame``.

    Parameters:
        fun (callable): Callable that applies to a single element in its first argument.

    Returns:
        callable: Callable that applies to a single element or a ``list``, ``tuple``, ``np.ndarray``,
            ``pd.Series``, or ``pd.DataFrame``.

    Examples:
        >>> @broadcast_first
        ... def add(x, y):
        ...     return x + y
        >>> add(1, 2)
        3
        >>> add([1, 2, 3], 2)
        [3, 4, 5]
        >>> add(np.array([1, 2, 3]), 2)
        array([3, 4, 5])
        >>> add(pd.Series([1, 2, 3]), 2)
        0    3
        1    4
        2    5
        dtype: int64
        >>> add(pd.DataFrame({"A": 1, "B": 2}, index=[0]), 2)
              A  B
        0     3  4
    """

    def f(value, *args, **kwargs):
        def f0(arg):
            return fun(arg, *args, **kwargs)
        if isinstance(value, ListLike):
            return type(value)(f0(e) for e in value)
        if isinstance(value, np.ndarray):
            return np.vectorize(f0)(value)
        if isinstance(value, pd.Series):
            return value.apply(f0)
        if isinstance(value, pd.DataFrame):
            if hasattr(value, "map"):
                return value.map(f0)  # pandas>=2.1.0
            else:
                return value.applymap(f0)  # pandas<2.1.0
        return f0(value)
    return f


def _fetch_indices(index):
    """Auxiliary function for map"""
    if isinstance(index, pd.DatetimeIndex):
        results = list(index)  # avoid conversion to int
    else:
        results = index.values
    return results


def mapi(inputs, f):
    """Apply a function on every input element and its index.

    Parameters:
        inputs (list | tuple | np.ndarray | pd.Series | pd.DataFrame): Input data to transform
        f (callable): Transformation function with some positional arguments:
            - For list and tuple: f(value, index) -> new_value
            - For ndarray: f(value, index_0, index_1, ..., index_(ndim-1))
            - For DataFrame: f(value, index, column) -> new_value
            - For Series: f(value, index, name) -> new_value

    Returns:
        list | tuple | np.ndarray | pd.Series | pd.DataFrame: Transformed data with same shape/index/columns

    Examples:

        Transform a list.

        >>> def printall(*args):
        ...    return ":".join(str(arg) for arg in args)
        >>> mapi([1, 2, 3], printall)
        ['1:0', '2:1', '3:2']

        Transform a ndarray.

        >>> from calcpy import add
        >>> a = np.ones(shape=(2, 3, 4))
        >>> mapi(a, add)
        array([[[1., 2., 3., 4.],
                [2., 3., 4., 5.],
                [3., 4., 5., 6.]],
            [[2., 3., 4., 5.],
                [3., 4., 5., 6.],
                [4., 5., 6., 7.]]])

        Transform a Series.

        >>> s = pd.Series("value", index=range(3))
        >>> mapi(s, printall)
        0    value:0:None
        1    value:1:None
        2    value:2:None
        dtype: object

        Transform a Series with datetime index and Series name.

        >>> tindex = pd.date_range("2000-01-01", "2000-01-03")
        >>> s = pd.Series("value", index=tindex, name="name")
        >>> mapi(s, printall)
        2000-01-01    value:2000-01-01 00:00:00:name
        2000-01-02    value:2000-01-02 00:00:00:name
        2000-01-03    value:2000-01-03 00:00:00:name
        Freq: D, Name: name, dtype: object

        Transform a Series with multi-level index.

        >>> mindex = pd.DataFrame({"app": "X", "date": tindex}).set_index(["app", "date"]).index
        >>> s = pd.Series("value", index=mindex)
        >>> mapi(s, printall)
        app  date
        X    2000-01-01    value:('X', Timestamp('2000-01-01 00:00:00')):...
             2000-01-02    value:('X', Timestamp('2000-01-02 00:00:00')):...
             2000-01-03    value:('X', Timestamp('2000-01-03 00:00:00')):...
        dtype: object

        Transform a Series to another datatype

        >>> def sumlen(*args):
        ...     return sum(len(arg) for arg in args)
        >>> s = pd.Series("value", index=["a", "b"], name="name")
        >>> mapi(s, sumlen)  # doctest: +ELLIPSIS
        a    10
        b    10
        Name: name, dtype: int...

        Transform a DataFrame.

        >>> df = pd.DataFrame('hello', index=range(4), columns=range(3))
        >>> mapi(df, printall)
                   0          1          2
        0  hello:0:0  hello:0:1  hello:0:2
        1  hello:1:0  hello:1:1  hello:1:2
        2  hello:2:0  hello:2:1  hello:2:2
        3  hello:3:0  hello:3:1  hello:3:2

        Transform a DataFrame with multi-level index.

        >>> df = pd.DataFrame("value", index=mindex, columns=["a"])
        >>> print(mapi(df, printall))
                                                                      a
        app date
        X   2000-01-01  value:('X', Timestamp('2000-01-01 00:00:00')):a
            2000-01-02  value:('X', Timestamp('2000-01-02 00:00:00')):a
            2000-01-03  value:('X', Timestamp('2000-01-03 00:00:00')):a

        Handle empty input.

        >>> s = pd.Series(dtype=object, name='empty')
        >>> mapi(s, printall)
        Series([], Name: empty, dtype: object)

        Create a DataFrame whose elements are all the same as index.

        >>> from calcpy import arggetter
        >>> index = pd.date_range("2000-01-01", "2000-01-03")
        >>> df = pd.DataFrame(index=index, columns=["A", "B"])
        >>> mapi(df, arggetter(1))
                            A          B
        2000-01-01 2000-01-01 2000-01-01
        2000-01-02 2000-01-02 2000-01-02
        2000-01-03 2000-01-03 2000-01-03
    """
    if empty(inputs):
        return full_like(inputs, None)

    if isinstance(inputs, (list, tuple)):
        results = type(inputs)([f(inp, idx) for idx, inp in enumerate(inputs)])
    elif isinstance(inputs, (np.ndarray,) + NDFrame):
        vf = np.vectorize(f)
        if isinstance(inputs, np.ndarray):
            indices = np.meshgrid(*[range(s) for s in inputs.shape], indexing='ij')
            results = vf(inputs, *indices)
        elif isinstance(inputs, NDFrame):
            if isinstance(inputs, pd.Series):
                indices = _fetch_indices(inputs.index)
                result_data = vf(inputs.values, indices, inputs.name)
            elif isinstance(inputs, pd.DataFrame):
                idxs = _fetch_indices(inputs.index)
                cols = _fetch_indices(inputs.columns)
                indices, columns = np.meshgrid(idxs, cols, indexing='ij')
                result_data = vf(inputs.values, indices, columns)
            results = full_like(inputs, result_data)
    else:
        results = f(inputs)
    return results


def _minmaxvalue(dtype, *ignored_args):
    """Auxiliary function to return the min and max values for a given dtype."""
    if dtype is int:
        return -sys.maxsize-1, sys.maxsize
    if dtype is float:
        return -inf, inf
    if dtype is bool:
        return False, True
    for supertype in [np.datetime64, np.timedelta64]:  # need to be checked before np.integer
        if np.issubdtype(dtype, supertype):
            unit = np.datetime_data(dtype)[0]   # fetch time unit such as 'ns','us','s', or 'generic'
            if unit == "generic":
                unit = "ns"
            iinfo = np.iinfo(np.int64)
            return supertype(iinfo.min+1, unit), supertype(iinfo.max, unit)
    if np.issubdtype(dtype, np.integer):
        iinfo = np.iinfo(dtype)
        return iinfo.min, iinfo.max
    if np.issubdtype(dtype, np.floating):
        finfo = np.finfo(dtype)
        return finfo.min, finfo.max
    if hasattr(dtype, "max"):  # such as datetime.datetime, datetime.date, datetime.time, pd.Timestamp, pd.Timedelta
        return dtype.min, dtype.max
    raise TypeError(f"Unsupported type: {dtype}")


def maxvalue(dtype):
    """Get the max value of a type.

    Parameters:
        dtype (type): Type to get max value

    Returns:
        Max value of the type

    Examples:
        >>> maxvalue(int)
        9223372036854775807
        >>> maxvalue(float)
        inf
        >>> maxvalue(bool)
        True
        >>> import datetime
        >>> maxvalue(datetime.datetime)
        datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
        >>> maxvalue(datetime.date)
        datetime.date(9999, 12, 31)
        >>> maxvalue(datetime.time)
        datetime.time(23, 59, 59, 999999)
        >>> maxvalue(datetime.timedelta)
        datetime.timedelta(days=999999999, seconds=86399, microseconds=999999)
        >>> maxvalue(np.int64)
        9223372036854775807
        >>> maxvalue(np.float64)  # doctest: +SKIP
        1.7976931348623157e+308
        >>> maxvalue(np.datetime64)  # doctest: +SKIP
        numpy.datetime64('2262-04-11T23:47:16.854775807')
        >>> maxvalue(np.timedelta64)  # doctest: +SKIP
        numpy.timedelta64(9223372036854775807,'ns')
        >>> maxvalue(pd.Timestamp)
        Timestamp('2262-04-11 23:47:16.854775807')
        >>> maxvalue(pd.Timedelta)
        Timedelta('106751 days 23:47:16.854775807')
    """
    _, mx = _minmaxvalue(dtype)
    return mx


def minvalue(dtype):
    """Get the min value of a type.

    Parameters:
        dtype (type): Type to get min value

    Returns:
        Min value of the type

    Examples:
        >>> minvalue(int)
        -9223372036854775808
        >>> minvalue(float)
        -inf
        >>> minvalue(bool)
        False
        >>> minvalue(datetime.datetime)
        datetime.datetime(1, 1, 1, 0, 0)
        >>> minvalue(datetime.date)
        datetime.date(1, 1, 1)
        >>> minvalue(datetime.time)
        datetime.time(0, 0)
        >>> minvalue(datetime.timedelta)
        datetime.timedelta(days=-999999999)
        >>> minvalue(np.int64)
        -9223372036854775808
        >>> minvalue(np.float64)  # doctest: +SKIP
        -1.7976931348623157e+308
        >>> minvalue(np.datetime64)  # doctest: +SKIP
        numpy.datetime64('1677-09-21T00:12:43.145224193')
        >>> minvalue(np.timedelta64)  # doctest: +SKIP
        numpy.timedelta64(-9223372036854775807,'ns')
        >>> minvalue(pd.Timestamp)
        Timestamp('1677-09-21 00:12:43.145224193')
        >>> minvalue(pd.Timedelta)
        Timedelta('-106752 days +00:12:43.145224193')
    """
    mn, _ = _minmaxvalue(dtype)
    return mn


def difftype(dtype):
    """Determine the result type of subtracting two values of the given data type.

    This function handles Python built-in types, NumPy types, and Pandas-compatible types.
    For datetime types, returns the corresponding timedelta type. For numeric and timedelta
    types, returns the input type itself.

    Psarameters:
        dtype: A type object (e.g., datetime.datetime, np.int64, np.dtype('datetime64[ns]'))

    Returns:
        type: The resulting type of the subtraction operation

    Raises:
        NotImplementedError: If the input type doesn't support subtraction

    Examples:

        Python built-in types

        >>> difftype(int)
        <class 'int'>
        >>> difftype(float)
        <class 'float'>
        >>> import datetime
        >>> difftype(datetime.datetime)
        <class 'datetime.timedelta'>
        >>> difftype(datetime.timedelta)
        <class 'datetime.timedelta'>

        NumPy scalar types

        >>> import numpy as np
        >>> difftype(np.int32)
        <class 'numpy.int32'>
        >>> difftype(np.float64)
        <class 'numpy.float64'>
        >>> difftype(np.datetime64)
        <class 'numpy.timedelta64'>
        >>> difftype(np.timedelta64)
        <class 'numpy.timedelta64'>

        NumPy dtype objects

        >>> difftype(np.dtype('datetime64[ns]'))
        dtype('<m8[ns]')
        >>> difftype(np.dtype('timedelta64[ns]'))
        dtype('<m8[ns]')

        Unsupported types

        >>> difftype(str)
        Traceback (most recent call last):
        ...
        NotImplementedError: dtype <class 'str'> is not supported for difference operation
    """
    if dtype is datetime.datetime:
        return datetime.timedelta
    if dtype is np.datetime64:
        return np.timedelta64
    if isinstance(dtype, np.dtype) and dtype.kind == 'M':  # Handle NumPy datetime dtype objects with units
        # Extract time unit from dtype name (e.g., 'ns' from 'datetime64[ns]')
        name = dtype.name
        if '[' in name:
            unit = name.split('[')[1].split(']')[0]
            return np.dtype(f'timedelta64[{unit}]')
        return np.timedelta64

    if (isinstance(dtype, type) and issubclass(dtype, Number)) or \
            dtype in (datetime.timedelta, np.timedelta64) or \
            (isinstance(dtype, np.dtype) and dtype.kind in 'iufcm'):
        return dtype

    raise NotImplementedError(f"dtype {dtype} is not supported for difference operation")
