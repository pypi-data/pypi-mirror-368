"""Iterators."""

try:
    from itertools import pairwise  # >=Python3.10  # noqa: F401
except Exception:
    from itertools import tee

    def pairwise(iterable):
        """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
