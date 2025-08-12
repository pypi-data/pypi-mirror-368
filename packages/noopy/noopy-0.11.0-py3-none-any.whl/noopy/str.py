#!/home/twinkle/venv/bin/python

from noopy.math import mathpy

# list
class strpy(str):
    ## XD Functions
    # Flatten
    def flatten(self):
        # Only 1D
        # Another, Not in Self ^^;
        return self;
        # Not Another, in Self ^^;
        #self = n_l; return self;
    # Transpose
    def transpose(self, x:int=0, y:int=0):
        x_y = x * y
        idx = 0
        a_l = len(self)
        n_l = strpy("")
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
        for p in range(0, a_l, x_y):       # Dimensioning
            for q in range(0, x):          # Y
                for r in range(0, x_y, y): # X
                    tsp = p + q + r
                    n_l += self[tsp]
                    idx += 1
        # Another, Not in Self ^^;
        return n_l
        # Not Another, in Self ^^;
        #self = n_l; return self;
    # Flip
    def flip(self, x:int=0, y:int=0, z:str='z'):
        x_y = x * y
        a_l = len(self)
        n_l = strpy("")
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
        for p in range(0, a_l, x_y):   # Dimensioning
            for q in range(0, x_y, y): # Y
                for r in range(0, x):  # X
                    idx = p + q + r
                    if z == 'x':
                        n_l += self[(p + q + x - r - 1)]
                    elif z == 'y':
                        n_l += self[(p + x_y - q + r - x)]
                    else: # == 'z':
                        n_l += self[(p + x_y - q - r - 1)]
        # Another, Not in Self ^^;
        return n_l
        # Not Another, in Self ^^;
        #self = n_l; return self;

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

## BASIC Functions
def zeros(n:int=0):
    return strpy("0" * n)
def ones(n:int=0):
    return strpy("1" * n)
def nones():
    raise NotImplementedError("strpy: nones is not implemented.")
    return strpy("\0" * n)
# ^^;
def linspace(s:float=0.0, e:float=0.0, n:int=0, t:str='i'):
    n_l = strpy("")
    n_m = float((e - s) / (n-1))
    for i in range(n):
        n_v = s + (i * n_m)
        if t == 'f' or t == 'd':
            n_l += str(round(n_v, 2)) + ","
        else:
            n_l += str(int(n_v)) + ", "
    return n_l

## XD Functions
# Flatten
def flatten(arr=None):
    if isinstance(arr, list):
        n_l = strpy("".join(arr))
    elif isinstance(arr, dict):
        n_l = strpy("".join(arr.items()))
    else:
        n_l = strpy(str(arr))
    return n_l
# Transpose
def transpose(arr:str=None, x:int=0, y:int=0):
    x_y = x * y
    idx = 0
    a_l = len(arr)
    n_l = strpy("")
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    for p in range(0, a_l, x_y):       # Dimensioning
        for q in range(0, x):          # Y
            for r in range(0, x_y, y): # X
                tsp = p + q + r
                n_l += arr[tsp]
                idx += 1
    return n_l
# Flip
def flip(arr:str=None, x:int=0, y:int=0, z:str='z'):
    x_y = x * y
    a_l = len(arr)
    n_l = strpy("")
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    for p in range(0, a_l, x_y):   # Dimensioning
        for q in range(0, x_y, y): # Y
            for r in range(0, x):  # X
                idx = p + q + r
                if z == 'x':
                    n_l += arr[(p + q + x - r - 1)]
                elif z == 'y':
                    n_l += arr[(p + x_y - q + r - x)]
                else: # == 'z':
                    n_l += arr[(p + x_y - q - r - 1)]
    return n_l
# mm
def mm(arr:str=None, brr:list=None, x:int=0, y:int=0):
    x_y = x * y
    idx = 0
    a_l = len(arr)
    b_l = len(brr)
    n_l = strpy("")
    if a_l != b_l:
        raise ValueError("list lengths must be the same for element-wise addition.")
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    for p in range(0, a_l, x_y):       # Dimensioning
        for q in range(0, x):          # Y
            for r in range(0, x_y, y): # X
                tsp = p + q + r
                n_l += chr(
                    int( ((ord(arr[idx]) * ord(brr[tsp]) / 255)) )
                )
                idx += 1
    return n_l

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["strpy", "zeros", "ones", "nones", "linspace", "flatten", "transpose", "flip"]

""" __DATA__

__END__ """
