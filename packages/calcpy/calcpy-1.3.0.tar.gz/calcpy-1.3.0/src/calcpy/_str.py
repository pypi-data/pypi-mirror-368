from keyword import iskeyword as _iskeyword
from math import inf, isinf
import operator
import re
import string
from textwrap import wrap, fill, shorten, dedent, indent  # noqa: F401

import pandas as pd

from ._nppd import broadcast_first
from ._op import methodcaller
from .typing import NDFrame, ListLike, StrLike, StrListLike


def _pdseries_apply(series, fun, *args, **kwargs):
    if isinstance(fun, StrLike):
        fun = methodcaller(fun)
    return fun(series, *args, **kwargs)


def _pdframe_apply(frame, fun, *args, **kwargs):
    if isinstance(frame, pd.Series):
        return _pdseries_apply(frame, fun, *args, **kwargs)
    if isinstance(frame, pd.DataFrame):
        return frame.apply(_pdseries_apply, fun, args=args, axis=1, **kwargs)
    raise TypeError()


def _elementwise_apply(arg, fun, *args, **kwargs):
    if isinstance(fun, str):
        fun = methodcaller(fun)
    f = broadcast_first(fun)
    return f(arg, *args, **kwargs)


def _apply_via_pd(arg, attrname, *args, **kwargs):
    if isinstance(arg, StrLike):
        frame = pd.Series([arg])
    elif isinstance(arg, ListLike):
        frame = pd.Series(arg)
    elif isinstance(arg, NDFrame):
        frame = arg
    else:
        raise NotImplementedError()

    results = _pdframe_apply(frame, attrname, *args, **kwargs)

    if isinstance(arg, StrLike):
        result = results.iloc[0]
        if hasattr(result, "item"):  # particularly, np.bool_
            return result.item()
        return result
    if isinstance(arg, ListLike):
        return type(arg)(results.tolist())
    return results


def _apply_via_str_or_pd(arg, attrname, *args, **kwargs):
    if isinstance(arg, StrListLike):
        c = operator.methodcaller(attrname, *args, **kwargs)
        if isinstance(arg, StrLike):
            return c(arg)
        else:
            return type(arg)(c(s) for s in arg)
    if isinstance(arg, NDFrame):
        return _pdframe_apply(arg, "str." + attrname, *args, **kwargs)
    raise NotImplementedError()


def capitalize(value, /):
    """Capitalize the first character of each word in the string.

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> capitalize("hello world")
        'Hello world'
        >>> capitalize(["hello", "world"])
        ['Hello', 'World']
        >>> import pandas as pd
        >>> capitalize(pd.Series(["hello", "world"]))
        0    Hello
        1    World
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.capitalize
    """
    return _apply_via_str_or_pd(value, "capitalize")


def capwords(value, /):
    """Capitalize the first character of each word in the string.

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> capwords("hello world")
        'Hello World'
        >>> capwords(["hello", "world"])
        ['Hello', 'World']
        >>> import pandas as pd
        >>> capwords(pd.Series(["hello", "world"]))
        0    Hello
        1    World
        dtype: object

    See also:
        https://docs.python.org/3/library/string.html#string.capwords
    """
    return _elementwise_apply(value, string.capwords)


def casefold(value, /):
    """casefold

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> casefold("Hello World")
        'hello world'
        >>> casefold(["Hello", "World"])
        ['hello', 'world']
        >>> import pandas as pd
        >>> casefold(pd.Series(["Hello", "World"]))
        0    hello
        1    world
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.casefold
    """
    return _apply_via_str_or_pd(value, "casefold")


def center(value, /, width, fillchar=' '):
    """center

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        width (int): width of the string
        fillchar (str): fill character

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> center("Hello World", 20)
        '  Hello World  '
        >>> center(["Hello", "World"], 20)
        ['  Hello  ', '  World  ']
        >>> import pandas as pd
        >>> center(pd.Series(["Hello", "World"]), 20)
        0      Hello
        1      World
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.center
    """
    return _apply_via_str_or_pd(value, "center", width, fillchar)


def contains(value, /, pat, case=True, flags=0, na=None, regex=True):
    """contains

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        pat (str): pattern to match
        case (bool): case sensitive
        flags (int): flags
        na (bool): na value
        regex (bool): regex

    Returns:
        bool | (list | tuple | pd.Series)[str]:

    Examples:
        >>> contains("Hello World", "World")
        True
        >>> contains(["Hello", "World"], "World")
        [False, True]
        >>> import pandas as pd
        >>> contains(pd.Series(["Hello", "World"]), "World")
        0    False
        1     True
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.contains
    """
    return _apply_via_pd(value, "str.contains", pat=pat, case=case, flags=flags, na=na, regex=regex)


def count(value, /, sub, start=0, end=None):
    """count

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        sub (str): substring to count
        start (int): start index
        end (int): end index

    Returns:
        int | (list | tuple | pd.Series):

    Examples:
        >>> count('Hello World', 'o')
        2
        >>> count(['Hello', 'World'], 'o')
        [1, 1]
        >>> import pandas as pd
        >>> count(pd.Series(['Hello', 'World']), 'o')
        0    1
        1    1
        dtype: int64

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.count
    """
    return _elementwise_apply(value, "count", sub, start, end)


def decode(value, /, encoding='utf-8', errors='strict'):
    """decode

    Parameters:
        value (bytes | bytearray | (list | tuple | pd.Series)[bytes | bytearray]):
        encoding (str): encoding
        errors (str): errors

    Returns:
        str | list | tuple | pd.Series:

    Examples:
        >>> decode(b'Hello World', 'utf-8', 'strict')
        'Hello World'
        >>> decode([b'Hello', b'World'], 'utf-8', 'strict')
        ['Hello', 'World']
        >>> import pandas as pd
        >>> decode(pd.Series([b'Hello', b'World']), 'utf-8', 'strict')
        0    Hello
        1    World
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#bytes.decode
    """
    return _apply_via_pd(value, "str.decode", encoding=encoding, errors=errors)


def encode(value, /, encoding='utf-8', errors='strict'):
    """encode

    Parameters:
        value (str | (list | tuple | pd.Series)[str]):
        encoding (str): encoding
        errors (str): errors

    Returns:
        bytes | list | tuple | pd.Series:

    Examples:
        >>> encode('Hello World', 'utf-8', 'strict')
        b'Hello World'
        >>> encode(['Hello', 'World'], 'utf-8', 'strict')
        [b'Hello', b'World']
        >>> import pandas as pd
        >>> encode(pd.Series(['Hello', 'World']), 'utf-8', 'strict')
        0    b'Hello'
        1    b'World'
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.encode
    """
    return _apply_via_str_or_pd(value, "encode", encoding, errors)


def endswith(value, /, suffix, start=0, end=None):
    """endswith

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        suffix (str): suffix to endswith
        start (int): start index
        end (int): end index

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> endswith('Hello World', 'World')
        True
        >>> endswith(['Hello', 'World'], 'World')
        [False, True]
        >>> import pandas as pd
        >>> endswith(pd.Series(['Hello', 'World']), 'World')
        0    False
        1     True
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.endswith
    """
    return _elementwise_apply(value, "endswith", suffix, start, end)


def expandtabs(value, /, tabsize=8):
    """expandtabs

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        tabsize (int): tabs

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> expandtabs('Hello\tWorld', 4)
        'Hello    World'
        >>> expandtabs(['Hello\tWorld', 'Hello\tWorld'], 4)
        ['Hello    World', 'Hello    World']
        >>> import pandas as pd
        >>> expandtabs(pd.Series(['Hello\tWorld', 'Hello\tWorld']), 4)
        0    Hello    World
        1    Hello    World
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.expandtabs
    """
    return _elementwise_apply(value, "expandtabs", tabsize)


def find(value, /, sub, start=0, end=None):
    """find

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        sub (str): substring to find
        start (int): start index
        end (int): end in

    Returns:
        int | list | tuple | pd.Series:

    Examples:
        >>> find('Hello World', 'World')
        6
        >>> find(['Hello', 'World'], 'World')
        [-1, 0]
        >>> import pandas as pd
        >>> find(pd.Series(['Hello', 'World']), 'World')
        0    -1
        1     0
        dtype: int64

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.find
    """
    return _apply_via_str_or_pd(value, "find", sub, start, end)


def format_(value, /, *args, **kwargs):
    """Perform a string formatting operation.

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        *args:
        **kwargs:

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> format_('Hello {0}', 'World')
        'Hello World'
        >>> format_(['Hello', 'World'], '{0}')
        ['Hello', 'World']
        >>> import pandas as pd
        >>> format_(pd.Series(['Hello', 'World']), '{0}')
        0    Hello
        1    World
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.format
    """
    return _elementwise_apply(value, "format", *args, **kwargs)


def format_map(value, /, mapping):
    """format_map

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        mapping (dict): mapping

    Returns:
        str | bytes | bytearray | (list | tuple | pd.Series)[str]:

    Examples:
        >>> format_map('Hello {w}', {'w': 'World'})
        'Hello World'
        >>> format_map(['Hello', '{w}'], {'w': 'World'})
        ['Hello', 'World']
        >>> import pandas as pd
        >>> format_map(pd.Series(['Hello', '{w}']), {'w': 'World'})
        0    Hello
        1    World
        dtype: object

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.format_map
    """
    return _elementwise_apply(value, "format_map", mapping)


def index(value, /, sub, start=0, end=None):
    """index

    Parameters:
        value (str | bytes | bytearray | (list | tuple | pd.Series)[str]):
        sub (str): substring to index
        start (int): start index
        end (int): end index

    Returns:
        int | list | tuple | pd.Series:

    Raises:
        ValueError: if ``sub`` is not found

    Examples:
        >>> index('Hello World', 'World')
        6
        >>> index(['Hello', 'World'], 'World')
        Traceback (most recent call last):
        ValueError: substring not found
        >>> import pandas as pd
        >>> index(pd.Series(['Hello', 'World']), 'World')
        Traceback (most recent call last):
        ValueError: substring not found

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.index
    """
    return _apply_via_str_or_pd(value, "index", sub, start, end)


def isalnum(value, /):
    """isalnum

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> isalnum('Hello World')
        False
        >>> isalnum(['Hello', 'World'])
        [True, True]
        >>> import pandas as pd
        >>> isalnum(pd.Series(['Hello', 'World']))
        0    True
        1    True
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isalnum
    """
    return _apply_via_str_or_pd(value, "isalnum")


def isalpha(value, /):
    """isalpha

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> isalpha('Hello World')
        False
        >>> isalpha(['Hello', 'World'])
        [True, True]
        >>> import pandas as pd
        >>> isalpha(pd.Series(['Hello', 'World']))
        0    True
        1    True
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isalpha
    """
    return _apply_via_str_or_pd(value, "isalpha")


def _isascii(s):
    return all(c in string.ascii_letters for c in s)


def isascii(value, /):
    """isascii

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> isascii('Hello World')
        True
        >>> isascii(['Hello', 'World'])
        [True, True]
        >>> import pandas as pd
        >>> isascii(pd.Series(['Hello', 'World']))
        0    True
        1    True
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isascii
    """
    try:
        return _elementwise_apply(value, "isascii")
    except AttributeError:
        return _elementwise_apply(value, _isascii)


def isdecimal(value, /):
    """isdecimal

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> isdecimal('Hello World')
        False
        >>> isdecimal(['Hello', 'World'])
        [False, False]
        >>> import pandas as pd
        >>> isdecimal(pd.Series(['Hello', 'World']))
        0    False
        1    False
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isdecimal
    """
    return _apply_via_str_or_pd(value, "isdecimal")


def isidentifier(value, /):
    """isidentifier

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> isidentifier('Hello World')
        False
        >>> isidentifier(['Hello', 'World'])
        [True, True]
        >>> import pandas as pd
        >>> isidentifier(pd.Series(['Hello', 'World']))
        0    True
        1    True
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isidentifier
    """
    return _elementwise_apply(value, "isidentifier")


def iskeyword(value, /):
    """iskeyword

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> iskeyword('Hello World')
        False
        >>> iskeyword(['Hello', 'World'])
        [False, False]
        >>> import pandas as pd
        >>> iskeyword(pd.Series(['Hello', 'World']))
        0    False
        1    False
        dtype: bool

    See also:
        https://docs.python.org/3/library/keyword.html#keyword.iskeyword
    """
    return _elementwise_apply(value, _iskeyword)


def islower(value, /):
    """islower

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> islower('Hello World')
        False
        >>> islower(['Hello', 'World'])
        [False, False]
        >>> import pandas as pd
        >>> islower(pd.Series(['Hello', 'World']))
        0    False
        1    False
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.islower
    """
    return _apply_via_str_or_pd(value, "islower")


def isnumeric(value, /):
    """isnumeric

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> isnumeric('Hello World')
        False
        >>> isnumeric(['Hello', 'World'])
        [False, False]
        >>> import pandas as pd
        >>> isnumeric(pd.Series(['Hello', 'World']))
        0    False
        1    False
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isnumeric
    """
    return _apply_via_str_or_pd(value, "isnumeric")


def isprintable(value, /):
    """isprintable

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    Examples:
        >>> isprintable('Hello World')
        True
        >>> isprintable(['Hello', 'World'])
        [True, True]
        >>> import pandas as pd
        >>> isprintable(pd.Series(['Hello', 'World']))
        0    True
        1    True
        dtype: bool

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isprintable
    """
    return _elementwise_apply(value, "isprintable")


def isspace(value, /):
    """isspace

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isspace
    """
    return _apply_via_str_or_pd(value, "isspace")


def istitle(value, /):
    """istitle

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.istitle
    """
    return _apply_via_str_or_pd(value, "istitle")


def isupper(value, /):
    """isupper

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        bool | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.isupper
    """
    return _apply_via_str_or_pd(value, "isupper")


def join(value, /, sep=""):
    """join

    Parameters:
        value (list[str] | tuple[str] | pd.Series[str]): string to join
        sep (str): separator

    Returns:
        str

    Examples:
        >>> join(['Hello', 'World'], ' ')
        'Hello World'
        >>> import pandas as pd
        >>> join(pd.Series(['Hello', 'World']), ' ')
        'Hello World'

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.join
    """
    return sep.join(value)


def ljust(value, /, width, fillchar=' '):
    """ljust

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):
        width (int):
        fillchar (str):

    Returns:
        str | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.ljust
    """
    return _apply_via_str_or_pd(value, "ljust", width, fillchar)


def lower(value, /):
    """lower

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):

    Returns:
        str | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.lower
    """
    return _apply_via_str_or_pd(value, "lower")


def lstrip(value, /, chars=None):
    """lstrip

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):
        chars (str):

    Returns:
        str | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.lstrip
    """
    return _apply_via_str_or_pd(value, "lstrip", chars)


def partition(value, /, sep, expand=True):
    """partition

    Parameters:
        value (str | bytes | bytearray | list | pd.Series[str]): string to partition
        sep (str): separator
        expand (bool): expand or not. Only used when input is an ``NDFrame``.
            Should be ``False`` when value is a ``pd.DataFrame``.

    Returns:
        tuple | list | pd.DataFrame:

    Examples:
        >>> partition('Hello World', ' ')
        ('Hello', ' ', 'World')
        >>> partition(['Hello', 'World'], ' ')
        [('Hello', '', ''), ('World', '', '')]
        >>> import pandas as pd
        >>> partition(pd.Series(['Hello', 'World']), 'l')
             0  1   2
        0   He  l  lo
        1  Wor  l   d

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.partition
    """
    attrname = "partition"
    if expand and isinstance(value, NDFrame):
        return _pdseries_split_expand(value, attrname=attrname, sep=sep)
    return _elementwise_apply(value, _str_split, sep, attrname=attrname)


def removeprefix(value, /, prefix):
    """removeprefix

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):
        prefix (str):

    Returns:
        str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.removeprefix
    """
    return _apply_via_str_or_pd(value, "removeprefix", prefix)


def removesuffix(value, /, suffix):
    """removesuffix

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):
        suffix (str):

    Returns:
        str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame:

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.removesuffix
    """
    return _apply_via_str_or_pd(value, "removsuffix", suffix)


def _replace(text, pattern, new=None, count=inf):
    if isinstance(pattern, dict):
        for pat, replacement in pattern.items():
            if callable(replacement):
                replaced = 0
                position = 0
                while (replaced < count) and (position := text.find(pat, position)) != -1:
                    new_text = replacement(pattern)
                    text = text[:position] + new_text + text[position + len(pattern):]
                    position += len(new_text)
                    replaced += 1
            else:
                text = text.replace(pat, replacement, count)
    else:
        if isinf(count):
            count = -1
        text = text.replace(pattern, new, count)
    return text


def replace(value, pattern, new=None, /, count=inf):
    """replace

    Parameters:
        value (str | list[str] | tuple[str] | pd.Series[str]): string to replace
        pattern (str | dict): old string, or a dict from old string to new string
        new (str | None): new string if ``pattern`` is the old string
        count (int | inf): maximum number of replacements.
            Default value (inf) means do not limit the number of replacements.
            0 means disabling replacements.

    Returns:
        string replaced.

    Notes:
        The parameters differ from either the built-in ``str.replace`` method or ``pd.Series.str.replace`` method.

    Examples:
        >>> replace('Hello World', 'World', 'Earth')
        'Hello Earth'
        >>> replace(['Hello', 'World'], 'World', 'Earth')
        ['Hello', 'Earth']
        >>> import pandas as pd
        >>> replace(pd.Series(['Hello', 'World']), 'World', 'Earth')
        0    Hello
        1    Earth
        dtype: object
        >>> replace('aaaa', {'a': 'b'}, count=0)
        'aaaa'
        >>> replace('aaaa', {'a': 'b'}, count=2)
        'bbaa'

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.replace
    """
    return _elementwise_apply(value, _replace, pattern, new, count)


def rfind(value, /, sub, start=0, end=None):
    """rfind

    Parameters:
        value (str | list[str] | tuple[str] | pd.Series[str]): string to find
        sub (str): substring to find
        start (int): start index
        end (int): end in

    Returns:
        Found indices.

    Examples:
        >>> rfind('Hello World', 'World')
        6
        >>> rfind(['Hello', 'World'], 'World')
        [-1, 0]
        >>> import pandas as pd
        >>> rfind(pd.Series(['Hello', 'World']), 'World')
        0    -1
        1     0
        dtype: int64

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.rfind
    """
    return _apply_via_str_or_pd(value, "rfind", sub, start, end)


def rindex(value, /, sub, start=0, end=None):
    """rindex

    Parameters:
        value (str | bytes | bytearray | list | tuple | pd.Series | pd.DataFrame):
        sub (str): substring to index
        start (int): start index
        end (int): end index

    Returns:
        indices

    Raises:
        ValueError: if ``sub`` is not found

    Examples:
        >>> rindex('Hello World', 'World')
        6
        >>> rindex(['Hello', 'World'], 'World')
        Traceback (most recent call last):
        ValueError: substring not found
        >>> import pandas as pd
        >>> rindex(pd.Series(['Hello', 'World']), 'World')
        Traceback (most recent call last):
        ValueError: substring not found

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.rindex
    """
    return _apply_via_str_or_pd(value, "rindex", sub, start, end)


def rjust(value, /, width, fillchar=' '):
    """rjust

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.rjust
    """
    return _apply_via_str_or_pd(value, "rjust", width, fillchar)


def rpartition(s, /, sep):
    """rpartition

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.rpartition
    """
    return s.rpartition(sep)


def _str_split(s, *args, attrname="split", minsplit=0, fillvalue=None):
    segs = getattr(s, attrname)(*args)  # args are sep, and optional maxsplit
    if len(segs) < minsplit:
        segs.extend([fillvalue] * (minsplit - len(segs)))
    return segs


def _pdseries_split_expand(s, attrname="split", sep=None, minsplit=0, fillvalue=None, **kwargs):
    df = getattr(s.str, attrname)(sep, expand=True, **kwargs)
    if fillvalue is not None:
        df.fillna(fillvalue, inplace=True)
    if len(df.columns) < minsplit:
        df = df.reindex(columns=range(minsplit), fill_value=fillvalue)
    return df


def rsplit(value, /, sep=None, maxsplit=-1, minsplit=0, fillvalue=None, expand=False):
    """Split string by separator.

    Parameters:
        s (str | pd.Series): string to split
        sep (str, optional): separator. By default split on whitespace
        maxsplit (int): maximum number of splits
        minsplit (int): minimum number of splits
        fillvalue (Optional): fill value if not enough splits
        expand (bool): expand result ``pd.Series`` to ``pd.DataFrame``.
            Can be ``True`` only when input is an ``pd.Series``

    Returns:
        Splitted strings

    Examples:
        >>> rsplit('abc def ghi')
        ['abc', 'def', 'ghi']
        >>> rsplit('abc def ghi', ' ', maxsplit=1)
        ['abc def', 'ghi']
        >>> rsplit('abc def ghi', ' ', minsplit=2)
        ['abc', 'def', 'ghi']
        >>> rsplit('abc def ghi', ' ', minsplit=4, fillvalue="")
        ['abc', 'def', 'ghi', '']
        >>> rsplit(pd.Series(['abc def', 'ABC']), ' ', minsplit=3, fillvalue="", expand=True)
             0    1 2
        0  abc  def
        1  ABC

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.rsplit
    """
    attrname = "rsplit"
    if expand and isinstance(value, NDFrame):
        return _pdseries_split_expand(value, attrname=attrname, sep=sep, n=maxsplit,
                                      minsplit=minsplit, fillvalue=fillvalue)
    return _elementwise_apply(value, _str_split, sep, maxsplit, attrname=attrname,
                              minsplit=minsplit, fillvalue=fillvalue)


def split(value, /, sep=None, maxsplit=-1, minsplit=0, fillvalue=None, expand=False):
    """Split string by separator.

    Parameters:
        value (str | pd.Series): string to split
        sep (str, optional): separator. By default split on whitespace
        maxsplit (int): maximum number of splits
        minsplit (int): minimum number of splits
        fillvalue (Optional): fill value if not enough splits
        expand (bool): expand result ``pd.Series`` to ``pd.DataFrame``.
            Can be ``True`` only when input is an ``pd.Series``

    Returns:
        Splitted strings

    Examples:
        >>> split('abc def ghi')
        ['abc', 'def', 'ghi']
        >>> split('abc def ghi', ' ', maxsplit=1)
        ['abc', 'def ghi']
        >>> split('abc def ghi', ' ', minsplit=2)
        ['abc', 'def', 'ghi']
        >>> split('abc def ghi', ' ', minsplit=4, fillvalue="")
        ['abc', 'def', 'ghi', '']
        >>> split(pd.Series(['abc def', 'ABC']), ' ', minsplit=3, fillvalue="", expand=True)
             0    1 2
        0  abc  def
        1  ABC

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.split
    """
    attrname = "split"
    if expand and isinstance(value, NDFrame):
        return _pdseries_split_expand(value, attrname=attrname, sep=sep, n=maxsplit,
                                      minsplit=minsplit, fillvalue=fillvalue)
    return _elementwise_apply(value, _str_split, sep, maxsplit, attrname=attrname,
                              minsplit=minsplit, fillvalue=fillvalue)


def splitlines(value, /, keepends=False):
    """splitlines

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.splitlines
    """
    return _apply_via_str_or_pd(value, "splitlines", keepends)


def startswith(value, /, prefix, start=0, end=None):
    """startswith

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.startswith
    """
    return _apply_via_str_or_pd(value, "startswith", prefix, start, end)


def strip(value, /, chars=None):
    """strip

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.strip
    """
    return _apply_via_str_or_pd(value, "strip", chars)


def swapcase(value, /):
    """swapcase

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.swapcase
    """
    return _apply_via_str_or_pd(value, "swapcase")


def _sub(value, pattern, new, count, flags):
    if count == 0:  # no change allowed
        count = -1
    elif isinf(count):  # no limits on change number
        count = 0
    if isinstance(pattern, dict):
        for pat, replacement in pattern.items():
            value = re.sub(pat, replacement, value, count=count, flags=flags)
    else:
        value = re.sub(pattern, new, value, count=count, flags=flags)
    return value


def sub(value, pattern, new=None, count=inf, flags=0):
    """Replace using regex.

    Parameters:
        value (str | list[str] | tuple[str] | pd.Series[str]): string to replace
        pattern (str | dict): old pattern, or a dict from old string to new string
        new (str | None): new string if ``pattern`` is the old string
        count (int | inf): maximum number of replacements.
            By default, there is no limit on the number of replacements.
            0 means disabling replacements.
        flags (re.RegexFlag):

    Returns:
        string replaced.

    Notes:
        The parameters differ from the built-in ``re.sub`` method.

    Examples:
        >>> sub('Hello World', 'World', 'Earth')
        'Hello Earth'
        >>> sub(['Hello', 'World'], 'World', 'Earth')
        ['Hello', 'Earth']
        >>> import pandas as pd
        >>> sub(pd.Series(['Hello', 'World']), 'World', 'Earth')
        0    Hello
        1    Earth
        dtype: object
        >>> sub('aaaa', {'a': 'b'}, count=0)
        'aaaa'
        >>> sub('aaaa', {'a': 'b'}, count=2)
        'bbaa'

    See also:
        https://docs.python.org/3/library/re.html#re.sub
    """
    return _elementwise_apply(value, _sub, pattern, new, count, flags)


def title(value, /):
    """title

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.title
    """
    return _apply_via_str_or_pd(value, "title")


def translate(value, /, table):
    """translate

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.translate
    """
    return _apply_via_str_or_pd(value, "translate", table)


def upper(value, /):
    """upper

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.upper
    """
    return _apply_via_str_or_pd(value, "upper")


def zfill(value, /, width):
    """zfill

    See also:
        https://docs.python.org/3/library/stdtypes.html#str.zfill
    """
    return _apply_via_str_or_pd(value, "zfill", width)
