#!/home/twinkle/venv/bin/python

# list
class strpy(str):
    ## XD Functions
    # Transpose
    def transpose(self, x:int=0, y:int=0):
        n_l = strpy("")
        s_l = len(self)
        x_y = x * y
        if s_l % x_y != 0:
            raise ValueError(f"splist: could not be transposing str {x_y} on {s_l}.")
        tmp = []
        for p in range(0, s_l, x_y):
            tmp.append(self[p:p+x_y])
        t_l = len(tmp)
        for i in range(t_l):
            t_x = []
            for q in range(0, x_y, x):
                t_x.append(tmp[i][q:q+x])
            l_x = len(t_x)
            z_x = list(zip(*t_x))
            z_l = len(z_x)
            for j in range(z_l):
                for k in range(x):
                    n_l += z_x[j][k]
        # Another, Not in Self ^^;
        return n_l
    # Flip
    def flip(self, x:int=0, y:int=0, z:str='z'):
        n_l = strpy("")
        s_l = len(self)
        x_y = x * y
        if s_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping str {x_y} on {s_l}.")
        tmp = []
        for p in range(0, s_l, x_y):
            tmp.append(self[p:p+x_y])
        t_l = len(tmp)
        for i in range(t_l):
            t_x = []
            for q in range(0, x_y, x):
                t_x.append(tmp[i][q:q+x])
            l_x = len(t_x)
            for j in range(l_x):
                a_y = (l_x - 1) - j
                for k in range(x):
                    a_x = (x - 1) - k
                    if z == 'x':
                        n_l += t_x[j][a_x]
                    elif z == 'y':
                        n_l += t_x[a_y][k]
                    else:
                        n_l += t_x[a_y][a_x]
        # Another, Not in Self ^^;
        return n_l

## BASIC Functions
def zeros(n:int=0):
    return strpy("0" * n)
def ones(n:int = 0):
    return strpy("1" * n)
def nones():
    return strpy("\0" * n)
    raise NotImplementedError("strpy: nones is not implemented.")
def linspace(s:float=0.0,e:float=0.0, n:int=0, t:str='i'):
    n_l = strpy("")
    n_m = float((e - s) / n)
    for i in range(n):
        n_v = s + (i * n_m)
        if t == 'f' or t == 'd':
            n_l += str(round(n_v, 2)) + ","
        else:
            n_l += str(int(n_v)) + ", "
    return n_l

## XD Functions
# Flatten
def flatten(arr:list=None):
    n_l = strpy()
    a_l = len(arr)
    for i in range(a_l):
        if isinstance(arr[i], list):
            t_l = len(arr[i])
            for j in range(t_l):
                if isinstance(arr[i][j], list):
                    n_l += str(flatten(arr[i][j]))
                else:
                    n_l += str(arr[i][j])
        else:
            n_l += str(arr[i])
    return n_l
# Transpose
def transpose(arr:str=None, x:int=0, y:int=0):
    n_l = strpy("")
    s_l = len(arr)
    x_y = x * y
    if s_l % x_y != 0:
        raise ValueError(f"splist: could not be transposing str {x_y} on {s_l}.")
    tmp = []
    for p in range(0, s_l, x_y):
        tmp.append(arr[p:p+x_y])
    t_l = len(tmp)
    for i in range(t_l):
        t_x = []
        for q in range(0, x_y, x):
            t_x.append(tmp[i][q:q+x])
        l_x = len(t_x)
        z_x = list(zip(*t_x))
        z_l = len(z_x)
        for j in range(z_l):
            for k in range(x):
                n_l += z_x[j][k]
    # Another, Not in Self ^^;
    return n_l
# Flip
def flip(arr:str=None, x:int=0, y:int=0, z:str='z'):
    n_l = strpy("")
    s_l = len(arr)
    x_y = x * y
    if s_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping str {x_y} on {s_l}.")
    tmp = []
    for p in range(0, s_l, x_y):
        tmp.append(arr[p:p+x_y])
    t_l = len(tmp)
    for i in range(t_l):
        t_x = []
        for q in range(0, x_y, x):
            t_x.append(tmp[i][q:q+x])
        l_x = len(t_x)
        for j in range(l_x):
            a_y = (l_x - 1) - j
            for k in range(x):
                a_x = (x - 1) - k
                if z == 'x':
                    n_l += t_x[j][a_x]
                elif z == 'y':
                    n_l += t_x[a_y][k]
                else:
                    n_l += t_x[a_y][a_x]
    # Another, Not in Self ^^;
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
