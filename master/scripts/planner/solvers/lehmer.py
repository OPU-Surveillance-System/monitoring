"""
Permutations by Lehmer codes (http://en.wikipedia.org/wiki/Lehmer_code)
Inspired by http://stackoverflow.com/a/3241894/212278
Given input sequence
>>> seq = ["A", "B", "C", "D"]
>>> lehmer_code = [2, 1, 0, 0]
>>> int_from_code(lehmer_code)
6
>>> list(lehmer.iter_perm(['A', 'B', 'C']))
[['A', 'B', 'C'],
 ['B', 'A', 'C'],
 ['C', 'B', 'A'],
 ['A', 'C', 'B'],
 ['B', 'C', 'A'],
 ['C', 'A', 'B']]
Swap is the default method, switch to "pick and drop" by pick=True option.
>>> perm_from_int(seq, 6)
['C', 'A', 'B', 'D']
>>> perm_from_int(seq, 6, pick=True)
['C', 'B', 'A', 'D']
>>> int_from_perm(seq, ['C', 'A', 'B', 'D'])
6
>>> int_from_perm(seq, ['C', 'B', 'A', 'D'], pick=True)
6
Swap would:
- swap 0 and 2 elements ["A", "B", "C", "D"] -> ["C", "B", "A", "D"], then
- swap 1 and 2 elements ["C", "B", "A", "D"] -> ["C", "A", "B", "D"], then
- no swap (swap 2 and 2)
- no swap (swap 3 and 3)
- return ["C", "A", "B", "D"]
Same Lehmer code by "pick and drop" produces different permutation:
- pick 2 and drop it [], ["A", "B", "C", "D"] -> ["C"], ["A", "B", "D"], then
- pick 1 and drop it ["C"], ["A", "B", "D"] -> ["C", "B"], ["A", "D"], then
- pick 0 and drop it ["C", "B"], ["A", "D"] -> ["C", "B", "A"], ["D"], then
- pick 0 and drop it ["C", "B", "A"], ["D"] -> ["C", "B", "A", "D"], []
- return ["C", "B", "A", "D"]
Swap is the default one as it requires less operations and can be implemented
more efficiently (does not require any drop operations...).
Other implementation could be based on Steinhaus-Johnson-Trotter algorithm:
- http://en.wikipedia.org/wiki/Steinhaus-Johnson-Trotter_algorithm
- http://www.ics.uci.edu/~eppstein/PADS/Permutations.py
"""
import math

__all__ = ['perm_from_int', 'int_from_perm', 'int_from_code', 'code_from_int',
           'perm_from_code', 'code_from_perm', 'iter_perm']


def _perm_from_int_pick(base, num):
    """
    :type base: list
    :type num: int
    :rtype: list
    """
    pass

def _perm_from_code_pick(base, code):
    """
    :type base: list
    :type code: list
    :rtype: list
    """
    pass

def _code_from_perm_pick(base, perm):
    """
    :type base: list
    :type perm: list
    :rtype: list
    """
    pass

def _int_from_perm_pick(base, perm):
    """
    :type base: list
    :type perm: list
    :rtype: int
    """
    pass

def _int_from_code_pick(code):
    """
    :type code: list
    :rtype: int
    """
    pass

def iter_perm(base, *rargs, pick=None):
    """
    :type base: list
    :param rargs: range args [start,] stop[, step]
    :rtype: generator
    """
    if not rargs:
        rargs = [math.factorial(len(base))]
    for i in range(*rargs):
        yield perm_from_int(base, i, pick=pick)

def int_from_code(code):
    """
    :type code: list
    :rtype: int
    """
    num = 0
    for i, v in enumerate(reversed(code), 1):
        num *= i
        num += v

    return num

def code_from_int(size, num):
    """
    :type size: int
    :type num: int
    :rtype: list
    """
    code = []
    for i in range(size):
        num, j = divmod(num, size - i)
        code.append(j)

    return code


def perm_from_code(base, code, pick=None):
    """
    :type base: list
    :type code: list
    :rtype: list
    """
    if pick:
        return _perm_from_code_pick(base, code)

    perm = base.copy()
    for i in range(len(base) - 1):
        j = code[i]
        perm[i], perm[i+j] = perm[i+j], perm[i]

    return perm

def perm_from_int(base, num, pick=None):
    """
    :type base: list
    :type num: int
    :rtype: list
    """
    code = code_from_int(len(base), num)
    return perm_from_code(base, code, pick=pick)

def code_from_perm(base, perm, pick=None):
    """
    :type base: list
    :type perm: list
    :rtype: list
    """
    if pick:
        _code_from_perm_pick(base, perm)

    p = base.copy()
    n = len(base)
    pos_map = {v: i for i, v in enumerate(base)}

    w = []
    for i in range(n):
        d = pos_map[perm[i]] - i
        w.append(d)

        if not d:
            continue
        t = pos_map[perm[i]]
        pos_map[p[i]], pos_map[p[t]] = pos_map[p[t]], pos_map[p[i]]
        p[i], p[t] = p[t], p[i]

    return w

def int_from_perm(base, perm, pick=None):
    """
    :type base: list
    :type perm: list
    :rtype: int
    """
    code = code_from_perm(base, perm, pick=pick)
    return int_from_code(code)
