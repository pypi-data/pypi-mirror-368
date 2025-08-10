#!/home/twinkle/venv/bin/python

from noopy.lst import lispy
from noopy.arr import arrpy
from noopy.str import strpy

## Dump Xh
def dumpxh(arr:list=None, n:int=3):
    a_l = len(arr)
    for i in range(a_l):
        if i % n == 0 and i != 0: print("")
        print(arr[i], end=", ")
    if i % n != 0: print("")

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

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["lispy", "arrpy", "strpy", "dumpxh", "splpos", "splmax", "splmin", "is_spl"]

""" __DATA__

__END__ """
