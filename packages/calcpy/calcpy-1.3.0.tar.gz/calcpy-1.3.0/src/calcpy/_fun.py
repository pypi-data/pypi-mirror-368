from functools import wraps
from inspect import signature, Parameter


def curry(*args, **kwargs):
    """Fill arguments of a callable.

    If you want to fill positional arguments in the middle without filling argumetns in the begining,
    you can use ``prioritize()`` to move those positional parameter to the beginning,
    and then fill them using this ``curry()``.

    Parameters:
        args (tuple): Positional arguments to fill.
        kwargs (dict): Keyword arguments to fill.

    Returns:
        Callable[callable, callable]:

    Examples:
        Use as a decorator:

        >>> @curry(2, 3)
        ... def muladd(a, b, c):
        ...     return a * b + c
        >>> muladd(4)
        10

        Use as a decorator, together with ``prioritize()``:

        >>> from calcpy.fun import prioritize
        >>> @curry(2, 3)
        ... @prioritize(-2, -1)
        ... def muladd(a, b, c):
        ...     return a * b + c
        >>> muladd(4)
        14
    """
    def wrapper(f):
        @wraps(f)
        def fun(*arguments, **keywordarguments):
            return f(*args, *arguments, **kwargs, **keywordarguments)
        return fun
    return wrapper


def extargs(mode=None):
    """Enhance a function so that it can accept unused parameters.

    Parameters:
        mode (optional): Method to resolve when both positional argument and
            keyword argument tries to write to the same parameter.
            The default value ``None`` means to raise when there are conflicts.
            ``inspect.Parameter.POSITIONAL_ONLY`` means to use the values in positional arguments.
            ``inspect.Parameter.KEYWORD_ONLY`` means to use the values in keyword arguments.

    Returns:
        callable: Decorator that enhances the target function with parameter filtering.

    Examples:

        Enrich a function so that it can accept additional parameters, overwriting default values.

        >>> def print_fixed(a, /, b, c="c", *, d, e="e"):  # fixed parameters
        ...     print(f"a={a}, b={b}, c={c}, d={d}, e={e}")
        >>> eprint_fixed = extargs()(print_fixed)
        >>> eprint_fixed(0, 1, 2, 3, d="D", e="E", f="F")
        a=0, b=1, c=2, d=D, e=E

        Use default values.

        >>> eprint_fixed(0, 1, d="D")
        a=0, b=1, c=c, d=D, e=e

        Raise due to missing obligatory positional arguments.

        >>> eprint_fixed(c="C", d="D", e="E", f="F")
        Traceback (most recent call last):
        ...
        TypeError: missing a required argument: 'a'

        Raise due to missing obligatory keyword arguments.

        >>> eprint_fixed(0, 1)
        Traceback (most recent call last):
        ...
        TypeError: missing a required argument: 'd'

        Raise due to the conflict between positional arguments and keyword arguments.

        >>> eprint_fixed(0, 1, 2, 3, c="C", d="D", e="E", f="F")
        Traceback (most recent call last):
        ...
        TypeError: multiple values for argument 'c'

        Use positional argument values when conflicting.

        >>> import inspect
        >>> pprint_fixed = extargs(inspect.Parameter.POSITIONAL_ONLY)(print_fixed)
        >>> pprint_fixed(0, 1, 2, 3, c="C", d="D", e="E", f="F")
        a=0, b=1, c=2, d=D, e=E

        Use keyword argument values when conflicting.

        >>> kprint_fixed = extargs(inspect.Parameter.KEYWORD_ONLY)(print_fixed)
        >>> kprint_fixed(0, 1, 2, 3, c="C", d="D", e="E", f="F")
        a=0, b=1, c=C, d=D, e=E

        Deal with varied arguments.

        >>> def print_var(a, /, b, c="c", *args, d, e="e", **kwargs):  # var parameters
        ...     print(f"a={a}, b={b}, c={c}, args={args}, d={d}, e={e}, kwargs={kwargs}")
        >>> eprint_var = extargs()(print_var)
        >>> eprint_var(0, 1, 2, 3, c="C", d="D", e="E", f="F")
        Traceback (most recent call last):
        ...
        TypeError: multiple values for argument 'c'
        >>> pprint_var = extargs(inspect.Parameter.POSITIONAL_ONLY)(print_var)
        >>> pprint_var(0, 1, 2, 3, c="C", d="D", e="E", f="F")
        a=0, b=1, c=2, args=(3,), d=D, e=E, kwargs={'f': 'F'}
        >>> kprint_var = extargs(inspect.Parameter.KEYWORD_ONLY)(print_var)
        >>> kprint_var(0, 1, 2, 3, c="C", d="D", e="E", f="F")
        a=0, b=1, c=C, args=(3,), d=D, e=E, kwargs={'f': 'F'}

        Raise due to missing obligatory keyword arguments, when the original function has varied arguments.

        >>> eprint_var(d="D")
        Traceback (most recent call last):
        ...
        TypeError: missing a required argument: 'a'
    """
    def decorator(f):
        sig = signature(f)
        params = sig.parameters

        # Identify parameter characteristics
        has_var_args = any(param.kind == param.VAR_POSITIONAL for param in params.values())
        has_var_kwargs = any(param.kind == param.VAR_KEYWORD for param in params.values())
        max_positional = sum(
            1 for param in params.values()
            if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
        )

        @wraps(f)
        def wrapper(*args, **kwargs):
            # Process positional arguments
            if not has_var_args:
                args = args[:max_positional]

            # Filter keyword arguments
            if not has_var_kwargs:
                kwargs = {
                    k: v for k, v in kwargs.items()
                    if k in params and params[k].kind in (Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
                }

            # Conflict resolution
            if mode == Parameter.KEYWORD_ONLY:
                # Update positional argument values
                new_args = []
                for i, param in enumerate(params.values()):
                    if i < len(args):
                        if param.name in kwargs:
                            new_args.append(kwargs[param.name])
                        else:
                            new_args.append(args[i])
                args = tuple(new_args)

            if mode is not None:  # inspect.Parameter.POSITIONAL_ONLY or KEYWORD_ONLY
                # Remove conflicting keys
                position_assigned = set()
                for i, param in enumerate(params.values()):
                    if i < len(args) and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                        position_assigned.add(param.name)
                kwargs = {
                    k: v for k, v in kwargs.items()
                    if k not in position_assigned
                }

            # Bind and execute
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            fun = f(*bound_args.args, **bound_args.kwargs)
            return fun

        return wrapper
    return decorator
