from . import _str
from ._compo import getcomponent


def __getattr__(name):
    return getcomponent(_str, name)
