#!/home/twinkle/venv/bin/python

from array import array

from noopy.lst import lispy
from noopy.arr import arrpy
from noopy.str import strpy

## Dump Xh
def dumpxh(arr:list=None, n:int=3):
    for i in range(len(arr)):
        if i % n == 0 and i != 0: print("")
        print(arr[i], end=", ")
    if i is not None and i % n != 0: print("", end="\n")

## SPLIT, TRANSPOSE, FLIP
# Get Split Positions
def splpos(arr:list=None):
    spl = []
    a_l = int(len(arr) / 2)
    for i in range(2, a_l+1):
       if a_l % i == 0: spl.append(i)
    return spl
# Search n < max
def splmax(arr:list=None, n:int=0):
    spl = splpos(arr)
    spm = max(spl) + 1
    if n < 2:
        raise ValueError(f"splmax: could not be search {n} least up to 3-.")
    elif n > spm:
        raise ValueError(f"splmax: could not be search {n} on {spm} over ranges.")
    for i in range(n, spm):
       if i in spl: return i
    return 0
# Search n > min
def splmin(arr:list=None, n:int=0):
    spl = splpos(arr)
    spm = max(spl) + 1
    if n < 2:
        raise ValueError(f"splmax: could not be search {n} least up to 3-.")
    elif n > spm:
        raise ValueError(f"splmax: could not be search {n} on {spm} over ranges.")
    for i in reversed(range(2, n+1)):
       if i in spl: return i
    return 0
# Check Split Compatibility Array
def is_spl(arr:list=None, n:int=0):
    a_l = int(len(arr))
    if a_l % n == 0: return True
    return False
# Split List
def splist(arr:list=None, n:int=0, r:bool=False):
    spl = lispy([])
    a_l = len(arr)
    if a_l % n != 0:
        raise ValueError(f"splist: could not be split array {n} on {A_l}.")
    for i in range(0, len(arr), n):
        spl.append(arr[i:i+n])
    return spl[::-1] if r is True else spl

## XD Functions
# Flatten
def flatten(arr:list=None):
    a_l = len(arr)
    n_l = lispy([])
    for i in range(a_l):
        if isinstance(arr[i], list):
            t_l = len(arr[i])
            for j in range(t_l):
                if isinstance(arr[i][j], list):
                    n_l.append(flatten(arr[i][j]))
                else:
                    n_l.append(arr[i][j])
        else:
            t_l = len(arr[i])
            for j in range(t_l):
                n_l.append(arr[i][j])
    return n_l
# Transpose
def transpose(arr:list=None, x:int=0, y:int=0):
    n_l = lispy([])
    a_l = len(arr)
    x_y = x * y
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be transposing array {x_y} on {a_l}.")
    tmp = lispy([])
    for p in range(0, a_l, x_y):
        tmp.append(arr[p:p+x_y])
    t_l = len(tmp)
    for i in range(t_l):
        t_x = lispy([])
        for q in range(0, x_y, x):
            t_x.append(tmp[i][q:q+x])
        l_x = len(t_x)
        z_x = list(zip(*t_x))
        z_l = len(z_x)
        for j in range(z_l):
            for k in range(x):
                n_l.append(z_x[j][k])
    return n_l
# Flip
def flip(arr:list=None, x:int=0, y:int=0, z:str='z'):
    a_l = len(arr)
    n_l = lispy([])
    x_y = x * y
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    tmp = lispy([])
    for p in range(0, a_l, x_y):
        tmp.append(arr[p:p+x_y])
    t_l = len(tmp)
    for i in range(t_l):
        t_x = lispy([])
        for q in range(0, x_y, x):
            t_x.append(tmp[i][q:q+x])
        l_x = len(t_x)
        for j in range(l_x):
            a_y = (l_x - 1) - j
            for k in range(x):
                a_x = (x - 1) - k
                if z == 'x': n_l.append(t_x[j][a_x])
                elif z == 'y': n_l.append(t_x[a_y][k])
                else: n_l.append(t_x[a_y][a_x])
    return n_l

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["lispy", "arrpy", "strpy", "dumpxh", "splpos", "splmax", "splmin", "is_spl", "flatten", "transpose", "flip"]

""" __DATA__

__END__ """
