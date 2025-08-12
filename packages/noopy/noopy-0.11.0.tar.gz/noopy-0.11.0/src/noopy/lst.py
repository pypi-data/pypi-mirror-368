#!/home/twinkle/venv/bin/python

from noopy.math import mathpy
from noopy.hook import hookpy

# list
class lispy(hookpy, list, mathpy):
    # Original
    def concat(self, arr:list=None):
        return lispy(list(self) + list(arr))
    ## XD Functions
    # Flatten
    def flatten(self):
        a_l = len(self)
        n_l = lispy(n_l)
        for i in range(a_l):
            if isinstance(self[i], list):
                t_l = len(self[i])
                for j in range(t_l):
                    if isinstance(self[i][j], list):
                        n_l.append(flatten(self[i][j]))
                    else:
                        n_l.append(self[i][j])
            else:
                t_l = len(self[i])
                for j in range(t_l):
                    n_l.append(self[i][j])
        # Another, Not in Self ^^;
        return n_l;
        # Not Another, in Self ^^;
        #self = n_l; return self;
    # Transpose
    def transpose(self, x:int=0, y:int=0):
        x_y = x * y
        idx = 0
        a_l = len(self)
        n_l = lispy([None] * a_l)
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
        for p in range(0, a_l, x_y):       # Dimensioning
            for q in range(0, x):          # Y
                for r in range(0, x_y, y): # X
                    tsp = p + q + r
                    n_l[idx] = self[tsp]
                    idx += 1
        # Another, Not in Self ^^;
        return n_l;
        # Not Another, in Self ^^;
        #self = n_l; return self;
    # Flip
    def flip(self, x:int=0, y:int=0, z:str='z'):
        x_y = x * y
        a_l = len(self)
        n_l = lispy([None] * a_l)
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
        for p in range(0, a_l, x_y):   # Dimensioning
            for q in range(0, x_y, y): # Y
                for r in range(0, x):  # X
                    idx = p + q + r
                    if z == 'x':
                        n_l[idx] = self[(p + q + x - r - 1)]
                    elif z == 'y':
                        n_l[idx] = self[(p + x_y - q + r - x)]
                    else: # == 'z':
                        n_l[idx] = self[(p + x_y - q - r - 1)]
        # Another, Not in Self ^^;
        return n_l;
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
def zeros(n:int=0, t:str='i'):
    if t == 's':
        return lispy(["0"] * n)
    elif t == 'f' or t == 'd':
        return lispy([float(0)] * n)
    elif t == 'b':
        return lispy([b"0"] * n)
    elif t == 'u':
        return lispy([u"0"] * n)
    else:
        return lispy([int(0)] * n)
def ones(n:int = 0, t:str='i'):
    if t == 's':
        return lispy(["1"] * n)
    elif t == 'f' or t == 'd':
        return lispy([float(1)] * n)
    elif t == 'b':
        return lispy([b"1"] * n)
    elif t == 'u':
        return lispy([u"1"] * n)
    else:
        return lispy([int(1)] * n)
def nones(n:int = 0):
    return lispy([None] * n)
def linspace(s:float=0.0, e:float=0.0, n:int=0, t:str='i'):
    n_l = lispy([None] * n)
    n_m = float((e - s) / (n-1))
    for i in range(0, n):
        n_v = float(s + (i * n_m))
        if t == 's':
            n_l[i] = str(round(n_v, 2))
        elif t == 'f' or t == 'd':
            n_l[i] = float(n_v)
        else:
            n_l[i] = int(n_v)
    return n_l

## Original
def concat(a:list=None, b:list=None):
    return lispy(list(a) + list(b))

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
    x_y = x * y
    idx = 0
    a_l = len(arr)
    n_l = lispy([None] * a_l)
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    for p in range(0, a_l, x_y):       # Dimensioning
        for q in range(0, x):          # Y
            for r in range(0, x_y, y): # X
                tsp = p + q + r
                n_l[idx] = arr[tsp]
                idx += 1
    return n_l
# Flip
def flip(arr:list=None, x:int=0, y:int=0, z:str='z'):
    x_y = x * y
    a_l = len(arr)
    n_l = lispy([None] * a_l)
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    for p in range(0, a_l, x_y):   # Dimensioning
        for q in range(0, x_y, y): # Y
            for r in range(0, x):  # X
                idx = p + q + r
                if z == 'x':
                    n_l[idx] = arr[(p + q + x - r - 1)]
                elif z == 'y':
                    n_l[idx] = arr[(p + x_y - q + r - x)]
                else: # == 'z':
                    n_l[idx] = arr[(p + x_y - q - r - 1)]
    return n_l
# mm
def mm(arr:list=None, brr:list=None, x:int=0, y:int=0):
    x_y = x * y
    idx = 0
    a_l = len(arr)
    b_l = len(brr)
    n_l = lispy([None] * a_l)
    if a_l % x_y != 0 or b_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    if a_l != b_l:
        raise ValueError("list lengths must be the same for element-wise addition.")
    for p in range(0, a_l, x_y):       # Dimensioning
        for q in range(0, x):          # Y
            for r in range(0, x_y, y): # X
                tsp = p + q + r
                #print(f"nth[{idx}] = A[{q}][{r}] * B[{r}][{q}]") # X, Y POS
                #print(f"nth[{idx}] = A[{tsp}] * B[{idx}]")
                n_l[idx] = brr[tsp] * arr[idx]
                idx += 1
    return n_l

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["lispy", "zeros", "ones", "nones", "linspace", "flatten", "transpose", "flip", "mm"]

""" __DATA__

def matmul(A, B):
    # 行数と列数のチェック
    if A.cols() != B.rows():
        raise ValueError("Matrix dimensions are not compatible for multiplication.")

    C = _ainit(...) # 結果を格納する新しい行列
    for i in range(A.rows()):
        for j in range(B.cols()):
            sum_val = 0
            for k in range(A.cols()):
                sum_val += A[i, k] * B[k, j]
            C[i, j] = sum_val
    return C

def __add__(self, other):
    # otherがリストのようなシーケンスの場合
    if isinstance(other, (list, tuple, str, arrpy, lispy)):
        if len(self) != len(other):
            raise ValueError("list lengths must be the same for element-wise addition.")
        return type(self)([self[i] + other[i] for i in range(len(self))])
    # otherがスカラー値（数値）の場合
    elif isinstance(other, (int, float, complex)):
        return type(self)([item + other for item in self])
    # それ以外の型の場合
    else:
        return NotImplemented

__END__ """
