"""Extensions to pandas."""
from math import inf

import pandas as pd

from ._nppd import mapi
from ._op import arggetter


def _extend_index(old_index, new_index, mode="extend"):
    from ._set import union

    if mode == "extend":
        return union(list(old_index), list(new_index))
    if mode == "prioritize":
        return union(list(new_index), list(old_index))
    raise ValueError("mode must be 'extend' or 'prioritize'")


def _extend(frame, labels=None, index=None, columns=None, axis=None, mode="extend", **kwargs):
    if labels is not None:
        if axis in [0, "index"]:
            index = labels
        elif axis in [1, "columns"]:
            columns = labels
        else:
            raise ValueError("axis must be 0 or 1")
    if index is not None:
        kwargs["index"] = _extend_index(frame.index, index, mode=mode)
    if columns is not None:
        kwargs["columns"] = _extend_index(frame.columns, columns, mode=mode)
    result = frame.reindex(**kwargs)
    return result


def extend(frame, /, labels=None, *, index=None, columns=None, axis=None, **kwargs):
    """Add index values if the index values are not present.

    This API is simliar to ``pd.DataFrame.reindex()``.

    Parameters:
        frame (pd.Series | pd.DataFrame): Input data.
        labels (list | tuple, optional): New labels / index to conform the axis specified by.
        index (list | tuple, optional): index names.
        columns (list | tuple, optional): column names.
            only work for DataFrame.
        axis (int | str, optional): axis to extend.
            0: index, 1: columns.
            only work for DataFrame.
        kwargs: keyword arguments to be passed to ``pd.DataFrame.reindex()``,
            including ``copy``, ``level``, ``fill_value``, ``limit``, and ``tolerance``.

    Returns:
        pd.Series | pd.DataFrame:

    Example:
        >>> import pandas as pd
        >>> s = pd.Series(1, index=[0, 1])
        >>> extend(s, index=[1, 2])
        0    1.0
        1    1.0
        2    NaN
        dtype: float64
        >>> df = pd.DataFrame({"A": 1, "B": 2}, index=[0, 1])
        >>> extend(df, index=[1, 2], columns=["A", "C"])
              A    B    C
        0   1.0  2.0  NaN
        1   1.0  2.0  NaN
        2   NaN  NaN  NaN
    """
    result = _extend(frame, labels=labels, index=index, columns=columns, axis=axis, mode="extend", **kwargs)
    return result


def prioritize(frame, /, labels=None, *, index=None, columns=None, axis=None, **kwargs):
    """Put some index values at the begining of the index.

    If the index is already in the index, the index will be moved to the begining.
    If the index is not in the index, the index will be added to the index.

    This API is simliar to ``pd.Series.reindex()`` and ``pd.DataFrame.reindex()``.

    Parameters:
        frame (pd.Series | pd.DataFrame): Input data.
        labels (list | tuple, optional): New labels / index to conform the axis specified by
        index (list | tuple, optional): index names
        columns (list | tuple, optional): column names.
            only work for DataFrame.
        axis (int | str, optional): axis to extend.
            0: index, 1: columns.
            only work for DataFrame.
        kwargs: keyword arguments to be passed to ``pd.DataFrame.reindex()``,
            including ``copy``, ``level``, ``fill_value``, ``limit``, and ``tolerance``.

    Returns:
        pd.Series | pd.DataFrame:

    Example:
        >>> import pandas as pd
        >>> s = pd.Series(1, index=[0, 1])
        >>> prioritize(s, index=[1, 2])
        1    1.0
        2    NaN
        0    1.0
        dtype: float64
        >>> df = pd.DataFrame({"A": 1, "B": 2}, index=[0, 1])
        >>> prioritize(df, index=[1, 2], columns=["A", "C"])
             A   C    B
        1  1.0 NaN  2.0
        2  NaN NaN  NaN
        0  1.0 NaN  2.0
    """
    result = _extend(frame, labels=labels, index=index, columns=columns, axis=axis, mode="prioritize", **kwargs)
    return result


def stack(frame, /, **kwargs):
    """Stack a ``pd.Series`` or ``pd.DataFrame`` with ``future_stack`` behavior.

    Stack and silence the ``FutureWarning`` "The prevoius implementation of stack is deprecated".

    Parameters:
        frame (pd.DataFrame):
        **kwargs: Keyword arguments to be passed to ``pd.DataFrame.stack()``.

    Returns:
        pd.Series | pd.DataFrame:

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"A": 1, "B": 2}, index=[0])
        >>> stack(df)
        0 A  1
          B  2
        dtype: int64
    """
    dropna = kwargs.pop("dropna", False)
    try:
        result = frame.stack(future_stack=True, **kwargs)
    except Exception:
        result = frame.stack(dropna=False, **kwargs)
    if dropna:
        result = result.dropna()
    return result


def mdd(inputs):
    """Maximum drawdown.

    Parameters:
        inputs (pd.Series | pd.DataFrame): Input time series (not difference).

    Returns:
        float | pd.Series:

    Examples:

        Calculate maximum drawdown for a DataFrame.

        >>> from math import nan
        >>> import pandas as pd
        >>> data = {"___": [nan, nan, nan],
        ...         "1__": [1.0, nan, nan],
        ...         "_1_": [nan, 1.0, nan],
        ...         "__1": [nan, nan, 1.0],
        ...         "12_": [1.0, 2.0, nan],
        ...         "21_": [2.0, 1.0, nan],
        ...         "1_2": [1.0, nan, 2.0],
        ...         "2_1": [2.0, nan, 1.0],
        ...         "_12": [nan, 1.0, 2.0],
        ...         "_21": [nan, 2.0, 1.0],
        ...         "123": [1.0, 2.0, 3.0],
        ...         "132": [1.0, 3.0, 2.0],
        ...         "213": [2.0, 1.0, 3.0],
        ...         "231": [2.0, 3.0, 1.0],
        ...         "312": [3.0, 1.0, 2.0],
        ...         "321": [3.0, 2.0, 1.0]}
        >>> df = pd.DataFrame(data, index=pd.date_range("2000-01-01", "2000-01-03"))
        >>> mdd(df)
        ___    NaN
        1__    0.0
        _1_    0.0
        __1    0.0
        12_    0.0
        21_    1.0
        1_2    0.0
        2_1    1.0
        _12    0.0
        _21    1.0
        123    0.0
        132    1.0
        213    1.0
        231    2.0
        312    2.0
        321    2.0
        dtype: float64

        Calculate MDD for a Series.

        >>> mdd(pd.Series([4, 2, 3, 1, 4]))  # doctest: +SKIP
        np.int64(3)

        Empty inputs.

        >>> df = pd.DataFrame(columns=["A"])
        >>> mdd(df)
        A    NaN
        dtype: object
    """
    cummaxs = inputs.cummax()
    drawdowns = cummaxs - inputs
    maxdrawdowns = drawdowns.max()
    return maxdrawdowns


def mdd_recover(inputs, fillinf=None):
    """Recovery duration for maximum drawdown.

    Parameters:
        inputs (pd.Series | pd.DataFrame): Input time series (not difference).
        fillinf (optional): Value for duration that the drawdown is not recovered.

    Returns:
        pd.Series | pd.DataFrame: Recovery durations are shown in the places where the maximum drawdown begins.
            Show NaN in other places.
            Results can be furthered processed with operations such as ``mean`` and ``max`` to
            get the average duration and the max duration.

    Examples:

        >>> from math import nan
        >>> import pandas as pd
        >>> data = {"___": [nan, nan, nan],
        ...         "1__": [1.0, nan, nan],
        ...         "_1_": [nan, 1.0, nan],
        ...         "__1": [nan, nan, 1.0],
        ...         "12_": [1.0, 2.0, nan],
        ...         "21_": [2.0, 1.0, nan],
        ...         "1_2": [1.0, nan, 2.0],
        ...         "2_1": [2.0, nan, 1.0],
        ...         "_12": [nan, 1.0, 2.0],
        ...         "_21": [nan, 2.0, 1.0],
        ...         "123": [1.0, 2.0, 3.0],
        ...         "132": [1.0, 3.0, 2.0],
        ...         "213": [2.0, 1.0, 3.0],
        ...         "231": [2.0, 3.0, 1.0],
        ...         "312": [3.0, 1.0, 2.0],
        ...         "321": [3.0, 2.0, 1.0]}
        >>> df = pd.DataFrame(data, index=pd.date_range("2000-01-01", "2000-01-03"))
        >>> with pd.option_context("display.max_rows", None, "display.max_columns", None):
        ...     mdd_recover(df)
                   ___ 1__ _1_ __1 12_                            21_ 1_2  \\
        2000-01-01 NaT NaT NaT NaT NaT 106751 days 23:47:16.854775807 NaT
        2000-01-02 NaT NaT NaT NaT NaT                            NaT NaT
        2000-01-03 NaT NaT NaT NaT NaT                            NaT NaT
        <BLANKLINE>
                                              2_1 _12                            _21  \\
        2000-01-01 106751 days 23:47:16.854775807 NaT                            NaT
        2000-01-02                            NaT NaT 106751 days 23:47:16.854775807
        2000-01-03                            NaT NaT                            NaT
        <BLANKLINE>
                   123                            132    213  \\
        2000-01-01 NaT                            NaT 2 days
        2000-01-02 NaT 106751 days 23:47:16.854775807    NaT
        2000-01-03 NaT                            NaT    NaT
        <BLANKLINE>
                                              231                            312  \\
        2000-01-01                            NaT 106751 days 23:47:16.854775807
        2000-01-02 106751 days 23:47:16.854775807                            NaT
        2000-01-03                            NaT                            NaT
        <BLANKLINE>
                                              321
        2000-01-01 106751 days 23:47:16.854775807
        2000-01-02                            NaT
        2000-01-03                            NaT
    """
    cummaxs = inputs.cummax()
    drawdowns = cummaxs - inputs
    maxdrawdowns = drawdowns.max()
    valley_locs = (maxdrawdowns == drawdowns) & (drawdowns > 0)
    peak_locs = cummaxs.where(valley_locs).bfill() == inputs
    recovers = inputs - cummaxs.shift(1).ffill()
    recovered_locs = recovers >= 0
    times = mapi(inputs, arggetter(1))
    assert inputs.index.nlevels == 1, "Only support one level index"
    if fillinf is None:
        if isinstance(inputs.index, pd.DatetimeIndex):
            fillinf = pd.Timedelta.max
        else:
            fillinf = inf
    durations = (times.where(recovered_locs).bfill().shift(-1) - times).fillna(fillinf).where(peak_locs)
    return durations
