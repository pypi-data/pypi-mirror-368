from collections import defaultdict, deque
from sys import maxsize


def A276128(n=maxsize):
    """Generate OEIS sequence A276128.

    Parameters:
        n (int): Length of sequence

    Yields:
        int: Value of the sequence

    See also:
        `OEIS A276128 <https://oeis.org/A276128>`_

    Explanations:
        (Adapted from https://oeis.org/A276128)
        Definition of sequence:
        For a positive integer n, let the single-player game G[n] be as follows:
        x is a number in {0, 1, 2, ..., n}, but unknown to the player.
        The player can guess as many times as he wants to determine the value of x.
        For each guess, the player can propose a possible value c in {0, 1, 2, ..., n},
        but such guess will cost the player c dollars.
        After each guess, the player will get response to show whether c<x, c=x, or c>x.
        A guess strategy will consist a series of guesses to determine x.
        The cost of multiple guesses is defined to be the sum of the cost of each guess.
        The cost of guess strategy is defined to be the worse case of the cost of the guess series.
        The optimal guess strategy for the game G[n] is the guess strategy that has the minimum cost.
        a[n] is the cost of the optimal guess strategy.
        It is indifference whether the set {0, 1, ..., n} contains the element 0
        since identifing this element takes no costs.

        Algorithms: Dynamic programming

    Complexity:
        Generate :math:`a[n]` when :math:`(a[0],...,a[n-1])` are available:
            Time complexity: :math:`O(n)`.
            Space complexity: :math:`O(n)`.
        Generate :math:`a[0],...,a[n-1]` entries (:math:`n` entries in total):
            Time complexity: :math:`O(n^2)`.
            Space complexity: :math:`O(n^2)`.

    Examples:
        >>> list(A276128(14))
        [0, 0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 21, 24]
    """
    a = defaultdict(int)  # tuple[int, int] -> int
    for end in range(n):
        h = end - 1
        fs = deque()  # deque[tuple[int, int]], store possible values of f
        for start in range(end - 1, 0, -1):
            # search h
            while a[(start, h - 1)] > a[(h + 1, end)]:
                if (len(fs) > 0) and (fs[0][1] == h):
                    fs.popleft()  # out of range, remove
                h -= 1
            v = start + a[(start + 1, end)]  # new entry into the range
            while (len(fs) > 0) and (v < fs[-1][0]):
                fs.pop()
            fs.append((v, start))

            # update a
            f = fs[0][0]
            g = a[(start, h)] + h + 1
            a[(start, end)] = min(f, g)
        yield a[(1, end)]
