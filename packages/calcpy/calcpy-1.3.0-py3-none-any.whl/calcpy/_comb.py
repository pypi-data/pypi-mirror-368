"""Combinatorics."""


def bellpartition(values):
    """ Get possible paritions of values.

    Parameters:
        values (list | tuple | set): Values to partition.

    Yields:
        list[list | tuple | set]: Parition of values

    See also:
        `<https://docs.sympy.org/latest/modules/functions/combinatorial.html#sympy.functions.combinatorial.numbers.bell>`_
        `<https://oeis.org/A000110>`_

    Examples:
        Partition a list.

        >>> for partition in bellpartition([0, 1, 2]):
        ...     print(partition)
        [[0, 1, 2]]
        [[0], [1, 2]]
        [[0, 1], [2]]
        [[0, 2], [1]]
        [[0], [1], [2]]

        Partition a tuple.

        >>> for partition in bellpartition(("a", "b", "c", "d")):
        ...     print(partition)
        [('a', 'b', 'c', 'd')]
        [('a',), ('b', 'c', 'd')]
        [('a', 'b'), ('c', 'd')]
        [('a', 'c', 'd'), ('b',)]
        [('a',), ('b',), ('c', 'd')]
        [('a', 'b', 'c'), ('d',)]
        [('a', 'd'), ('b', 'c')]
        [('a',), ('b', 'c'), ('d',)]
        [('a', 'b', 'd'), ('c',)]
        [('a', 'c'), ('b', 'd')]
        [('a',), ('b', 'd'), ('c',)]
        [('a', 'b'), ('c',), ('d',)]
        [('a', 'c'), ('b',), ('d',)]
        [('a', 'd'), ('b',), ('c',)]
        [('a',), ('b',), ('c',), ('d',)]

        Partition a set.

        >>> for partition in bellpartition({False, True}):
        ...     print(partition)
        [{False, True}]
        [{False}, {True}]
    """
    if not values:
        yield []
        return

    type_ = type(values)
    values = list(values)
    value0 = values[0]
    remaining_values = type_(values[1:])

    for subsets in bellpartition(remaining_values):
        for idx, subset in enumerate(subsets):
            yield [type_([value0] + list(subset))] + subsets[:idx] + subsets[idx+1:]
        yield [type_([value0])] + subsets
