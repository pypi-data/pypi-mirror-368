#!/home/twinkle/venv/bin/python

from array import array, typecodes

# array.array
class arrpy(array):
    def type(self):
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
                    id = q * q
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
    n_m = (e - s) / n
    for i in range(n):
        if t == 'f' or t == 'd':
            n_l[i] = (s + (i * n_m))
        else:
            n_l[i] = int(s + (i * n_m))
    return n_l

## XD Functions
# Flatten
def flatten(arr:list=None):
    # Only 1D
    raise NotImplementedError("arrpy: linspace is not implemented for 'u' and 'w'.")
# Transpose
def translistpose(arr:list=None, x:int=0, y:int=0):
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
# Transpose
def transpose(arr:array=None, x:int=0, y:int=0):
    idx = 0
    x_y = x * y
    a_l = arr.size()
    n_l = _ainit(arr.typecode, a_l)
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    for p in range(0, a_l, x_y):       # Dimensioning
        for q in range(0, x):          # Y
            for r in range(0, x_y, y): # X
                id = q * q
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

__END__ """
