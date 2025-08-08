#!/home/twinkle/venv/bin/python

import array

# list
class lispy(list):
    ## SPLIT
    # Get Split Positions
    def splpos(self):
        spl = []
        a_l = int(len(self) / 2)
        for i in range(2, a_l+1):
           if a_l % i == 0: spl.append(i)
        return spl
    # Search n < max
    def splmax(self, n:int=0):
        spl = splpos(self)
        spm = max(spl) + 1
        if n < 2:
            raise ValueError(f"splmax: could not be search {n} least up to 3-.")
        elif n > spm:
            raise ValueError(f"splmax: could not be search {n} on {spm} over ranges.")
        for i in range(n, spm):
           if i in spl: return i
        return 0
    # Search n > min
    def splmin(self, n:int=0):
        spl = splpos(self)
        spm = max(spl) + 1
        if n < 2:
            raise ValueError(f"splmax: could not be search {n} least up to 3-.")
        elif n > spm:
            raise ValueError(f"splmax: could not be search {n} on {spm} over ranges.")
        for i in reversed(range(2, n+1)):
           if i in spl: return i
        return 0
    # Check Split Compatibility Array
    def is_spl(self, n:int=0):
        a_l = len(self)
        if a_l % n == 0: return True
        return False
    # Split List
    def splist(self, n:int=0, r:bool=False):
        spl = []
        a_l = len(self)
        if a_l % n != 0:
            raise ValueError(f"splist: could not be split array {n} on {a_l}.")
        for i in range(0, len(self), n):
            spl.append(self[i:i+n])
        return spl[::-1] if r is True else spl
    # Transpose
    def transpose(self, x:int=0, y:int=0):
        n_l = []
        a_l = len(self)
        x_y = x * y
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be transposing array {x_y} on {a_l}.")
        tmp = []
        for p in range(0, a_l, x_y):
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
                    n_l.append(z_x[j][k])
        return n_l
    # Flip
    def flip(self, x:int=0, y:int=0, z:str='z'):
        n_l = []
        a_l = len(self)
        x_y = x * y
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
        tmp = []
        for p in range(0, a_l, x_y):
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
                        n_l.append(t_x[j][a_x])
                    elif z == 'y':
                        n_l.append(t_x[a_y][k])
                    else:
                        n_l.append(t_x[a_y][a_x])
        return n_l

# array.array
class arrpy(array.array):
    ## SPLIT
    # Get Positions
    def splpos(self):
        spl = []
        a_l = int(len(self) / 2)
        for i in range(2, a_l+1):
           if a_l % i == 0: spl.append(i)
        return spl
    # Search n < max
    def splmax(self, n:int=0):
        spl = splpos(self)
        spm = max(spl) + 1
        if n < 2:
            raise ValueError(f"splmax: could not be search {n} least up to 3-.")
        elif n > spm:
            raise ValueError(f"splmax: could not be search {n} on {spm} over ranges.")
        for i in range(n, spm):
           if i in spl: return i
        return 0
    # Search n > min
    def splmin(self, n:int=0):
        spl = splpos(self)
        spm = max(spl) + 1
        if n < 2:
            raise ValueError(f"splmax: could not be search {n} least up to 3-.")
        elif n > spm:
            raise ValueError(f"splmax: could not be search {n} on {spm} over ranges.")
        for i in reversed(range(2, n+1)):
           if i in spl: return i
        return 0
    # Check Split Compatibility Array
    def is_spl(self, n:int=0):
        a_l = len(self)
        if a_l % n == 0: return True
        return False
    # Split List
    def splist(self, n:int=0, r:bool=False):
        spl = []
        a_l = len(self)
        if a_l % n != 0:
            raise ValueError(f"splist: could not be split array {n} on {a_l}.")
        for i in range(0, len(self), n):
            spl.append(self[i:i+n])
        return spl[::-1] if r is True else spl
    # Transpose
    def transpose(self, x:int=0, y:int=0):
        n_l = []
        a_l = len(self)
        x_y = x * y
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be transposing array {x_y} on {a_l}.")
        tmp = []
        for p in range(0, a_l, x_y):
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
                    n_l.append(z_x[j][k])
        return n_l
    # Flip
    def flip(self, x:int=0, y:int=0, z:str='z'):
        n_l = []
        a_l = len(self)
        x_y = x * y
        if a_l % x_y != 0:
            raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
        tmp = []
        for p in range(0, a_l, x_y):
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
                        n_l.append(t_x[j][a_x])
                    elif z == 'y':
                        n_l.append(t_x[a_y][k])
                    else:
                        n_l.append(t_x[a_y][a_x])
        return n_l

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
    spl = []
    a_l = len(arr)
    if a_l % n != 0:
        raise ValueError(f"splist: could not be split array {n} on {A_l}.")
    for i in range(0, len(arr), n):
        spl.append(arr[i:i+n])
    return spl[::-1] if r is True else spl
# Transpose
def transpose(arr:list=None, x:int=0, y:int=0):
    n_l = []
    a_l = len(arr)
    x_y = x * y
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be transposing array {x_y} on {a_l}.")
    #print("x * y:", x_y, f"({x}, {y})")
    tmp = []
    for p in range(0, a_l, x_y):
        tmp.append(arr[p:p+x_y])
    t_l = len(tmp)
    #print("split:", t_l)
    for i in range(t_l):
        t_x = []
        for q in range(0, x_y, x):
            t_x.append(tmp[i][q:q+x])
        l_x = len(t_x)
        #print("split:", l_x)
        z_x = list(zip(*t_x))
        z_l = len(z_x)
        #print("ziped:", z_l)
        for j in range(z_l):
            for k in range(x):
                n_l.append(z_x[j][k])
    return n_l
# Flip
def flip(arr:list=None, x:int=0, y:int=0, z:str='z'):
    n_l = []
    a_l = len(arr)
    x_y = x * y
    if a_l % x_y != 0:
        raise ValueError(f"splist: could not be flipping array {x_y} on {a_l}.")
    #print("x * y:", x_y, f"({x}, {y})")
    tmp = []
    for p in range(0, a_l, x_y):
        tmp.append(arr[p:p+x_y])
    t_l = len(tmp)
    #print("split:", t_l)
    for i in range(t_l):
        t_x = []
        for q in range(0, x_y, x):
            t_x.append(tmp[i][q:q+x])
        l_x = len(t_x)
        #print("split:", l_x)
        for j in range(l_x):
            a_y = (l_x - 1) - j
            for k in range(x):
                a_x = (x - 1) - k
                #print(a_x, a_y)
                if z == 'x':
                    n_l.append(t_x[j][a_x])
                elif z == 'y':
                    n_l.append(t_x[a_y][k])
                else:
                    n_l.append(t_x[a_y][a_x])
    return n_l

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["lispy", "arrpy"]

""" __DATA__

__END__ """
