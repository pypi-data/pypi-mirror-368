"""Function composition."""

from contextlib import contextmanager
from copy import deepcopy
from functools import partial

_modes = dict(args=False, kwargs=False, force_callable=False)


def set_composition_mode(args=None, kwargs=None, force_callable=None):
    """Set composition mode.

    Parameters:
        args (bool, optional): whether to enable composition for positional arguments.
            The default is ``None``, meaning that the current status will be kept.
        kwargs (bool, optional): whether to enable composition for keyword arguments
            The default is ``None``, meaning that the current status will be kept.
        force_callable (bool, optional): whether to force return results to be callable
            The default is ``None``, meaning that the current status will be kept.

    Examples:
        >>> set_composition_mode(args=False, kwargs=False, force_callable=False)
    """
    if args is not None:
        assert isinstance(args, bool)
        _modes["args"] = args
    if kwargs is not None:
        assert isinstance(kwargs, bool)
        _modes["kwargs"] = kwargs
    if force_callable is not None:
        assert isinstance(force_callable, bool)
        _modes["force_callable"] = force_callable


def disable_composition():
    """Disable ``args`` composition and ``kwargs`` composition.

    Alias of ``set_composition_mode(args=False, kwargs=False)``
    """
    set_composition_mode(args=False, kwargs=False)


def enable_composition():
    """Enable args composition and kwargs composition.

    Alias of ``set_composition_mode(args=True, kwargs=True)``
    """
    set_composition_mode(args=True, kwargs=True)


def disable_args_composition():
    """Disable ``args`` composition.

    Alias of ``set_composition_mode(args=False)``
    """
    set_composition_mode(args=False)


def enable_args_composition():
    """Enable ``args`` composition.

    Alias of ``set_composition_mode(args=True)``
    """
    set_composition_mode(args=True)


def disable_kwargs_composition():
    """Disable ``kwargs`` composition.

    Alias of ``set_composition_mode(kwargs=False)``
    """
    set_composition_mode(kwargs=False)


def enable_kwargs_composition():
    """Enable ``kwargs`` composition.

    Alias of ``set_composition_mode(kwargs=True)``
    """
    set_composition_mode(kwargs=True)


def disable_force_callable():
    """Disable force callable.

    Alias of ``set_composition_mode(force_callable=False)``
    """
    set_composition_mode(force_callable=False)


def enable_force_callable():
    """Enable force callable.

    Alias of ``set_composition_mode(force_callable=True)``
    """
    set_composition_mode(force_callable=True)


def args_composition_enabled():
    """Return ``True`` when ``args`` composition is enabled.

    Returns:
        bool:
    """
    return _modes["args"]


def kwargs_composition_enabled():
    """Return ``True`` when ``kwargs`` composition is enabled.

    Returns:
        bool:
    """
    return _modes["kwargs"]


def force_callable_enabled():
    """Return ``True`` when force callable is enabled.

    Returns:
        bool:
    """
    return _modes["force_callable"]


def composition_enabled():
    """Return ``True`` when ``args`` composition or ``kwargs`` composition or force callable is enabled.

    Returns:
        bool:
    """
    return _modes["args"] or _modes["kwargs"] or _modes["force_callable"]


@contextmanager
def composition_mode_context(args=None, kwargs=None, force_callable=None):
    """Context manager to temporarily set composite mode in a ``with`` statement.

    Parameters:
        args (bool): whether to enable composition for positional arguments
        kwargs (bool): whether to enable composition for keyword arguments
        force_callable (bool): whether to force return results to be callable

    Examples:
        >>> force_callable_enabled()
        False
        >>> with composition_mode_context(args=False, kwargs=False, force_callable=True):
        ...     force_callable_enabled()
        True
        >>> force_callable_enabled()
        False
    """
    saved_modes = deepcopy(_modes)
    try:
        if args is not None:
            _modes["args"] = args
        if kwargs is not None:
            _modes["kwargs"] = kwargs
        if force_callable is not None:
            _modes["force_callable"] = force_callable
        yield
    finally:
        for key in ["args", "kwargs", "force_callable"]:
            _modes[key] = saved_modes[key]


def callable_arguments(*args, **kwargs):
    """Check whether the argument will lead to a callable result.

    Parameters:
        *args: values or callable objects.
        **kwargs: keyword arguments, either values or callable objects.

    Returns:
        bool

    Examples:
        >>> callable_arguments(1, 2, 3)
        False
        >>> enable_composition()
        >>> callable_arguments(sum)
        True
        >>> disable_composition()
    """
    if force_callable_enabled():
        return True
    if args_composition_enabled():
        if any(callable(arg) for arg in args):
            return True
    if kwargs_composition_enabled():
        for key in kwargs:
            kwarg = kwargs[key]
            if callable(kwarg):
                return True
    return False


def composite_callable(how, /, *args, **kwargs):
    """Combine multiple callables into a single callable, using a combining function.

    Parameters:
        how : Callable object that combines multiple results.
        *args : Callable objects or values.
        **kwargs : Keyword arguments to pass to the callables.

    Returns:
        A callable object.

    Examples:
        >>> from calcpy import itemgetter
        >>> enable_composition()
        >>> composite_callable(max, itemgetter(1), 7, itemgetter(2, default=3))([3, 4, 5])
        7
        >>> composite_callable(min, itemgetter(1), 7, itemgetter(2, default=3))([3, 4, 5])
        4
        >>> composite_callable(max, 3, 4, 5)()
        5
        >>> disable_composition()
    """
    def f(*args_, **kwargs_):
        _args = []
        for arg in args:
            if args_composition_enabled() and callable(arg):
                _arg = arg(*args_, **kwargs_)
            else:
                _arg = arg
            _args.append(_arg)
        _kwargs = {}
        for key in kwargs:
            kwarg = kwargs[key]
            if kwargs_composition_enabled() and callable(kwarg):
                _kwarg = kwarg(*args_, **kwargs_)
            else:
                _kwarg = kwarg
            _kwargs[key] = _kwarg
        result = how(*_args, **_kwargs)
        return result
    return f


def composite(how, /, *args, **kwargs):
    """Combine multiple callables into a single callable, using a combining function.

    Parameters:
        how : Callable object that combines multiple results.
        *args : Callable objects or values.
        **kwargs : Keyword arguments to pass to the callables.

    Returns:
        callable:

    Examples:
        >>> from calcpy import itemgetter
        >>> enable_composition()
        >>> composite(max, itemgetter(1), 7, itemgetter(2, default=3))([3, 4, 5])
        7
        >>> composite(min, itemgetter(1), 7, itemgetter(2, default=3))([3, 4, 5])
        4
        >>> composite(max, 3, 4, 5)
        5
        >>> disable_composition()
    """
    if callable_arguments(*args, **kwargs):
        return composite_callable(how, *args, **kwargs)
    return how(*args, **kwargs)


def componentize(how, /):
    """Decorate a callable function so that it becomes a building block of function composition.

    Need to enable composition mode before using this function.

    Parameters:
        how : Callable object that combines multiple results.

    Returns:
        callable:

    Examples:
        >>> from calcpy import itemgetter
        >>> enable_composition()
        >>> max_ = componentize(max)
        >>> max_(itemgetter(1), 7, itemgetter(2, default=3))([3, 4, 5])
        7
        >>> min_ = componentize(min)
        >>> min_(itemgetter(1), 7, itemgetter(2, default=3))([3, 4, 5])
        4
        >>> min_(3, 4, 5)
        3
        >>> disable_composition()
    """
    if not composition_enabled():
        return how  # avoid mess up function signature and docstring
    return partial(composite, how)


def getcomponent(module, name):
    f = getattr(module, name)
    component = componentize(f)
    return component
