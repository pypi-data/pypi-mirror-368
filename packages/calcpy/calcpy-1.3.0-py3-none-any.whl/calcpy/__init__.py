from importlib.metadata import version

from extepy import call  # noqa: F401
from extepy import fillerr, fillwhen  # noqa: F401
from extepy import argchecker, attrchecker, itemchecker  # noqa: F401
from extepy import groupby, partition  # noqa: F401

from . import _api
from ._arg import MISSING  # noqa: F401
from ._cls import *  # noqa: F401,F403
from ._collect import *  # noqa: F401,F403
from ._cmp import *  # noqa: F401,F403
from ._compo import getcomponent
from ._compo import *  # noqa: F401,F403
from ._fun import *  # noqa: F401,F403
from ._math import isnan  # noqa: F401
from ._nppd import *  # noqa: F401,F403
from ._op import arggetter, attrgetter, itemgetter, constantcreator, methodcaller  # noqa: F401
from ._pd import *  # noqa: F401,F403
from ._seq import cycleperm, swap  # noqa: F401

try:
    __version__ = version("calcpy")
except ModuleNotFoundError:
    __version__ = "unknown"


def __getattr__(name):
    return getcomponent(_api, name)


__doc__ = """
calcpy: Facility for Python Calculation
=======================================

Main features:
- Extend Python Built-in Functions, including extended `set` operation functions, extended `str` operation functions, extended math functions.
- Unify APIs supporting both Python built-in types and numpy&pandas datatypes.
- Return value decorations: If the function raises an error or returns invalid values such as `None` and `nan`, fill values with designated values.
- Function compositions: Combine multiple callable into one callable.
- Function decorators: Reorganize function parameters.
"""
