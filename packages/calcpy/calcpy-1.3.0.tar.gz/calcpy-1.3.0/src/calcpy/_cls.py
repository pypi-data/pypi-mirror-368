"""Class."""

from .binrel import asym_part
from .fun import dispatch, swap
from ._it import pairwise


def _pairwise_call(binop):
    def fun(*args):  # remove keyword arguments from function signature
        return dispatch(pairwise, agg=all)(binop)(*args)
    return fun


_issuperclass = swap()(issubclass)
_ispropersubclass = asym_part(issubclass)
_ispropersuperclass = swap()(_ispropersubclass)


issubclass_ = _pairwise_call(issubclass)
issubclass_.__name__ = "issubclass_"
issubclass_.__doc__ = \
    """Returns True if a argument is a subclass of the follow-up argument.

    Parameters:
        *args (type | tuple[type] | UnionType): Classes to check

    Returns:
        bool: True if all arguments are subclasses of the follow-up arguments

    Examples:
        >>> class A: pass
        >>> class B(A): pass
        >>> class C(B): pass
        >>> class D(A): pass
        >>> issubclass_()
        True
        >>> issubclass_(object)
        True
        >>> issubclass_(A, object)
        True
        >>> issubclass_(C, B, A, object)
        True
        >>> issubclass_(D, C)
        False
        >>> issubclass_(A, A)
        True

    See also:
        https://docs.python.org/3/library/functions.html#issubclass
    """

issuperclass = _pairwise_call(_issuperclass)
issuperclass.__name__ = "issuperclass"
issuperclass.__doc__ = \
    """Returns True if a argument is a superclasses of the follow-up argument.

    Parameters:
        *args (type | tuple[type] | UnionType): Classes to check

    Returns:
        bool: True if all arguments are superclasses of the follow-up arguments

    Examples:
        >>> class A: pass
        >>> class B(A): pass
        >>> class C(B): pass
        >>> class D(A): pass
        >>> issuperclass()
        True
        >>> issuperclass(A)
        True
        >>> issuperclass(A, B)
        True
        >>> issuperclass(object, A, B, C)
        True
        >>> issuperclass(D, C)
        False
        >>> issuperclass(A, A)
        True
    """


ispropersubclass = _pairwise_call(_ispropersubclass)
ispropersubclass.__name__ = "ispropersubclass"
ispropersubclass.__doc__ = \
    """Returns True if a argument is a proper subclass of the follow-up argument.

    Parameters:
        *args (type | tuple[type] | UnionType): Classes to check

    Returns:
        bool: True if all arguments are proper subclasses of the follow-up arguments

    Examples:
        >>> class A: pass
        >>> class B(A): pass
        >>> class C(B): pass
        >>> class D(A): pass
        >>> ispropersubclass()
        True
        >>> ispropersubclass(object)
        True
        >>> ispropersubclass(A, object)
        True
        >>> ispropersubclass(C, B, A, object)
        True
        >>> ispropersubclass(D, C)
        False
        >>> ispropersubclass(A, A)
        False
    """


ispropersuperclass = _pairwise_call(_ispropersuperclass)
ispropersuperclass.__name__ = "ispropersubclass"
ispropersuperclass.__doc__ = \
    """Returns True if a argument is a proper superclasses of the follow-up argument.

    Parameters:
        *args (type | tuple[type] | UnionType): Classes to check

    Returns:
        bool: True if all arguments are proper superclasses of the follow-up arguments

    Examples:
        >>> class A: pass
        >>> class B(A): pass
        >>> class C(B): pass
        >>> class D(A): pass
        >>> ispropersuperclass()
        True
        >>> ispropersuperclass(A)
        True
        >>> ispropersuperclass(object, A)
        True
        >>> ispropersuperclass(object, A, B, C)
        True
        >>> ispropersuperclass(D, C)
        False
        >>> ispropersuperclass(A, A)
        False
    """
