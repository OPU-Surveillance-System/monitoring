# cython: profile=True

from libcpp.vector cimport vector

cdef extern from "<algorithm>" namespace "std":
    iter std_find "std::find" [iter, T](iter first, iter end, const T& value)

def tremove(list a, int idx):
    cdef vector[vector[int]] v = a
    vv = v[idx]
    vv.erase(std_find[vector[int].iterator, int](vv.begin(), vv.end(), 6))

    return vv

def cremove(vector[int] a):
    a.erase(std_find[vector[int].iterator, int](a.begin(), a.end(), 6))

    return a

def main():
    cdef vector[vector[int]] a = [[1,2,3,4],[6, 2, 6],[8,9]]
    cdef vector[vector[int]] b = [[1,2,3,4],[5,6,7],[8,9]]
    idx = 1
    print(a)
    a[idx] = cremove(a[idx])
    print(a)
