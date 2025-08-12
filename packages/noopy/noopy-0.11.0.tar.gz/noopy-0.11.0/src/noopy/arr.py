#!/home/twinkle/venv/bin/python

from array import array, typecodes

from noopy.math import mathpy

# array.array
class arrpy(array, mathpy):
    def __pow__(self, v):
        if not isinstance(self, arrpy):
            raise NotImplementedError("arrpy: not implemented for non-arrpy.")
        f = []
        for i in self:
            f.append(i ** v)
        print("TYPE", type(f[0]))
        return arrpy('f', f)
    def atype(self):
        return self.typecode
    def size(self):
        return len(self)
    def blen(self):
        return self.itemsize
    ## XD Functions
    # Flatten
    def flatten(self):
        # Only 1D
        # Another, Not in Self ^^;
        return self;
        # Not Another, in Self ^^;
        #self = n_l; return self;
        raise NotImplementedError("arrpy: linspace is not implemented for 'u' and 'w'.")
    # Transpose
    def transpose(self, x:int=0, y:int=0):
        x_y = x * y
        idx = 0
        a_l = self.size()
        n_l = _ainit(self.typecode, a_l)
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
        a_l = self.size()
        n_l = _ainit(self.typecode, a_l)
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

# typecodes
def get_types():
    return typecodes
# initialize
def _ainit(t:str=None, n:int=0):
    if t not in typecodes:
        return arrpy('i', [int(0)] * n)
    elif t == 'f' or t == 'd': # float, double
        return arrpy(t, [0.0] * n)
    elif t == 'u' or t == 'w': # unicode(w_char), ucs
        return arrpy(t, ["\u002a"] * n)
    else:
        return arrpy(t, [0] * n)

## BASIC Functions
def zeros(n:int=0, t:str='i'):
    if t not in typecodes:
        return arrpy('i', [int(0)] * n)
    elif t == 'f' or t == 'd':
        return arrpy(t, [0.0] * n)
    elif t == 'u' or t == 'w': # unicode(w_char), ucs
        return arrpy(t, ["\u0030"] * n)
    return arrpy(t, [int(0)] * n)
def ones(n:int = 0, t:str='i'):
    if t not in typecodes:
        return arrpy('i', [int(1)] * n)
    elif t == 'f' or t == 'd':
        return arrpy(t, [1.0] * n)
    elif t == 'u' or t == 'w': # unicode(w_char), ucs
        return arrpy(t, ["\u0031"] * n)
    return arrpy(t, [int(1)] * n)
def nones(n:int = 0):
    raise NotImplementedError("arrpy: linspace is not implemented for 'u' and 'w'.")
def linspace(s:float=0.0, e:float=0.0, n:int=0, t:str='i'):
    if t not in typecodes or (t == 'u' or t == 'w'):
        raise NotImplementedError("arrpy: linspace is not implemented for 'u' and 'w'.")
    n_l = zeros(n, t)
    n_m = float((e - s) / (n-1))
    for i in range(n):
        if t == 'f' or t == 'd':
            n_l[i] = (s + (i * n_m))
        else:
            n_l[i] = int(s + (i * n_m))
    return n_l

## XD Functions
# _Flatten
def _flatten(arr:list=None):
    a_l = len(arr)
    n_l = []
    for i in range(a_l):
        if isinstance(arr[i], list):
            t_l = len(arr[i])
            for j in range(t_l):
                if isinstance(arr[i][j], list):
                    n_l.append(_flatten(arr[i][j]))
                else:
                    n_l.append(arr[i][j])
        else:
            t_l = len(arr[i])
            for j in range(t_l):
                n_l.append(arr[i][j])
    return n_l
# Flatten
def flatten(arr:list=None):
    a_l = len(arr)
    n_l = []
    for i in range(a_l):
        if isinstance(arr[i], list):
            t_l = len(arr[i])
            for j in range(t_l):
                if isinstance(arr[i][j], list):
                    n_l.append(_flatten(arr[i][j]))
                else:
                    n_l.append(arr[i][j])
        else:
            t_l = len(arr[i])
            for j in range(t_l):
                n_l.append(arr[i][j])
    # May be Instance
    if n_t == str:
       n_a = arrpy('u', n_t)
    elif n_t == float:
       n_a = arrpy('f', n_t)
    elif n_t == int:
       n_a = arrpy('q', n_t)
    else:
       n_a = arrpy('i', n_t)
    return n_a
# Transpose
def transpose(arr:array=None, x:int=0, y:int=0):
    x_y = x * y
    idx = 0
    a_l = arr.size()
    n_l = _ainit(arr.typecode, a_l)
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
def flip(arr:array=None, x:int=0, y:int=0, z:str='z'):
    x_y = x * y
    a_l = arr.size()
    n_l = _ainit(arr.typecode, a_l)
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

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["arrpy", "get_types", "zeros", "ones", "nones", "linspace", "flatten", "transpose", "flip"]

""" __DATA__

class arrpy(array):
    # ...
    def __truediv__(self, other):
        # otherがスカラー値の場合
        if isinstance(other, (int, float)):
            result = _ainit('f', self.size()) # 除算結果はfloatになる
            for i in range(self.size()):
                if other == 0:
                    # ゼロ除算の処理
                    result[i] = float('inf')
                else:
                    result[i] = self[i] / other
            return result
        # otherがarrpyオブジェクトの場合
        elif isinstance(other, arrpy):
            # arrpy同士の除算ロジック
            # ...
        else:
            raise TypeError("Unsupported operand type(s) for /")

class arrpy(array):
    # ...
    def __add__(self, other):
        # 他のオブジェクトもarrpyであることを前提とする
        if not isinstance(other, arrpy):
            raise TypeError("arrpyオブジェクト同士のみ加算可能です")

        if self.size() != other.size():
            raise ValueError("サイズが異なるarrpyオブジェクトは加算できません")

        result = _ainit(self.typecode, self.size())
        for i in range(self.size()):
            result[i] = self[i] + other[i]
        return result

__END__ """
