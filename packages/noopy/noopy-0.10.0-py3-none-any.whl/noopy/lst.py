#!/home/twinkle/venv/bin/python

# list
class lispy(list):
    ## XD Functions
    # Flatten
    def flatten(self):
        n_l = lispy(n_l)
        a_l = len(self)
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
        n_l = lispy([])
        a_l = len(self)
        x_y = x * y
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be transposing array {x_y} on {a_l}.")
        tmp = lispy([])
        for p in range(0, a_l, x_y):
            tmp.append(self[p:p+x_y])
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
        # Another, Not in Self ^^;
        return n_l;
        # Not Another, in Self ^^;
        #self = n_l; return self;
    # Flip
    def flip(self, x:int=0, y:int=0, z:str='z'):
        n_l = lispy([])
        a_l = len(self)
        x_y = x * y
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
        tmp = lispy([])
        for p in range(0, a_l, x_y):
            tmp.append(self[p:p+x_y])
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
                    if z == 'x':
                        n_l.append(t_x[j][a_x])
                    elif z == 'y':
                        n_l.append(t_x[a_y][k])
                    else:
                        n_l.append(t_x[a_y][a_x])
        # Another, Not in Self ^^;
        return n_l;
        # Not Another, in Self ^^;
        #self = n_l; return self;

## BASIC Functions
def zeros(n:int=0, t:str='i'):
    if t == 's':
        return lispy(["0"] * n)
    elif t == 'f' or t == 'd':
        return lispy([float(0)] * n)
    elif t == 'b':
        return lispy([b"0"] * n)
    else:
        return lispy([int(0)] * n)
def ones(n:int = 0, t:str='i'):
    if t == 's':
        return lispy(["1"] * n)
    elif t == 'f' or t == 'd':
        return lispy([float(1)] * n)
    elif t == 'b':
        return lispy([b"1"] * n)
    else:
        return lispy([int(1)] * n)
def nones(n:int = 0):
    return lispy([None] * n)
def linspace(s:float=0.0, e:float=0.0, n:int=0, t:str='i'):
    n_l = lispy([None] * n)
    n_m = float((e - s) / n)
    for i in range(n):
        n_v = s + (i * n_m)
        if t == 's':
            n_l[i] = str(round(n_v, 2))
        elif t == 'f' or t == 'd':
            n_l[i] = float(n_v)
        else:
            n_l[i] = int(n_v)
    return n_l

## XD Functions
# Flatten
def flatten(arr:list=None):
    n_l = lispy([])
    a_l = len(arr)
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
    n_l = lispy([])
    a_l = len(arr)
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
__all__ = ["lispy", "zeros", "ones", "nones", "linspace", "flatten", "transpose", "flip"]

""" __DATA__

__END__ """
