import numpy as np
import pandas as pd

from ._cmp import key_to_eq
from ._nppd import overall_equal
from .typing import ListTypes, DictTypes, StrLike, NDFrame


class Matcher(object):
    def __init__(self, eq=None, key=None):
        self.set_key(eq=eq, key=key)

    def set_key(self, eq=None, key=None):
        if key is not None:
            self._eq = key_to_eq(key)
        else:
            self._eq = eq or overall_equal

    def disassemble(self, values):
        return list(values)

    def eq(self, loper, roper):
        return self._eq(loper, roper)


class SimpleMatcher(Matcher):
    def __init__(self, eq=None, key=None, assemble=None):
        super().__init__(eq=eq, key=key)
        self.assemble = assemble


class DictMatcher(Matcher):
    def disassemble(self, values):
        return values.items()

    def eq(self, loper, roper):
        return self._eq(loper[0], roper[0])

    def assemble(self, args):
        return {key: value for key, value in args}


class NumpyArrayMatcher(SimpleMatcher):
    def __init__(self, eq=None, key=None):
        super().__init__(eq=eq, key=key)
        self.assemble = np.concatenate

    def disassemble(self, values):
        count = len(values)
        results = [values[i:i+1] for i in range(count)]
        return results


class PandasFrameMatcher(Matcher):
    """Auxiliary class for ``pd.Series`` and ``pd.DataFrame``.

    Parameters:
        method (str): can be ``"object"``, ``"series"``, ``"index"``.
            ``"object"`` means comparing the whole ``pd.NDFrame`` object.
            ``"series"`` means comparing the whole ``pd.Series``, which is equivalent
            to a row (when axis=1) or a column (when axis=0).
            ``"index"`` means comparing the index value (when axis=0) or
            column value (when axis=1) only.
            ``"value"`` means comparing the values of some columns (when axis=0) or
            rows (when axis=1).
        axis (int or str): can be 0 ("index") or 1 ("column")
        matcher (callable): a binary function
        **kwargs : keyword arguments as of ``pd.DataFrame.drop_duplicates()``.
            Only used when ``method="value"``.

    Examples:
        >>> from calcpy import unique
        >>> df0 = pd.DataFrame({"A": 1, "B": 2, "C": 3}, index=[0])
        >>> df1 = pd.DataFrame({"A": 1, "B": 2, "C": 3}, index=[0])
        >>> df2 = pd.DataFrame({"A": 1, "B": 2, "C": 3}, index=[0])
        >>> len(unique([df0, df1, df2]))
        1

        >>> from calcpy import intersection
        >>> df0 = pd.DataFrame({"A": [1, 2, 3], "B": [3, 2, 3]}, index=["X", "Y", "Z"])
        >>> df1 = pd.DataFrame({"C": [4, 5, 6], "D": [8, 5, 2]}, index=["U", "V", "X"])
        >>> intersection(df0, df1, key=PandasFrameMatcher(method="index"))
           A  B
        X  1  3

        >>> df0 = pd.DataFrame({"A": [1, 2, 3], "B": [3, 2, 3]}, index=["X", "Y", "Z"])
        >>> df1 = pd.DataFrame({"C": [4, 5, 6], "D": [8, 5, 2]}, index=["U", "V", "X"])
        >>> intersection(df0, df1, key=PandasFrameMatcher(method="value"))  # return None
    """
    def __init__(self, method="object", axis=0, eq=None, key=None, **kwargs):
        super().__init__(eq=eq, key=key)
        self.method = method
        self.kwargs = kwargs
        self.transpose = axis in [1, "columns"]

    def disassemble(self, values):
        if self.transpose:
            values = values.T
        count = len(values)
        results = [values.iloc[i:i+1] for i in range(count)]
        return results

    def eq(self, loper, roper):
        if self.method == "object":
            return self._eq(loper, roper)
        if self.method == "index":
            return self._eq(loper.index[0], roper.index[0])
        if self.method == "value":
            concated = pd.concat([loper, roper])
            uniqued = concated.drop_duplicates(**self.kwargs)
            return len(uniqued) < len(concated)
        if self.method == "series":
            return self._eq(loper, roper)

    def assemble(self, args):
        if len(args) == 0:
            return None
        results = pd.concat(args)
        if self.transpose:
            results = results.T
        return results


# Register the matcher type for each collection type
matcher_classes = {}
matcher_classes[ListTypes] = SimpleMatcher(assemble=list)
matcher_classes[tuple] = SimpleMatcher(assemble=tuple)
matcher_classes[set] = SimpleMatcher(assemble=set)
matcher_classes[DictTypes] = DictMatcher()
matcher_classes[StrLike] = SimpleMatcher(assemble="".join)
matcher_classes[np.ndarray] = NumpyArrayMatcher()
matcher_classes[NDFrame] = PandasFrameMatcher()


def _get_matcher(arg, eq=None, key=None, matcher=None):
    for obj in [matcher, key]:
        if isinstance(obj, Matcher):
            return obj
    for type_ in matcher_classes:
        if isinstance(arg, type_):
            matcher = matcher_classes[type_]
            matcher.set_key(eq=eq, key=key)
            return matcher
    raise NotImplementedError()
