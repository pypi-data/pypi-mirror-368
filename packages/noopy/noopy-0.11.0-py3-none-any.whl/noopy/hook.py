#!/home/twinkle/venv/bin/python

from noopy.util.globals import __globals__

#def __add__(self, other):
#    return type(self)([self[i] + other[i] for i in range(len(other))]) if isinstance(other, list) else type(self)([self[i] + other for i in range(len(self))])

class hookpy():
    def __init__(self, *args, **kwargs):
        super(hookpy, self).__init__(*args, **kwargs)
    def __add__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] + other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item + other for item in self])
        else:
            return NotImplemented
    def __radd__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] + other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item + other for item in self])
        else:
            return NotImplemented
    def __iadd__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] + other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] + other
            return self
        else:
            return NotImplemented
    def __sub__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] - other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item - other for item in self])
        else:
            return NotImplemented
    def __rsub__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] - other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item - other for item in self])
        else:
            return NotImplemented
    def __isub__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] - other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] - other
            return self
        else:
            return NotImplemented
    def __mul__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([self[i] * other for i in range(len(self))])
        else:
            return NotImplemented
    def __rmul__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item * other for item in self])
        else:
            return NotImplemented
    def __imul__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] * other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] * other
            return self
        else:
            return NotImplemented
    def __matmul__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            r = 0; r += ([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item * other for item in self])
        else:
            return NotImplemented
    def __rmatmul__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item * other for item in self])
        else:
            return NotImplemented
    def __imatmul__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] * other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] * other
            return self
        else:
            return NotImplemented
    def __truediv__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] / other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item / other for item in self])
        else:
            return NotImplemented
    def __rtruediv__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] / other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item / other for item in self])
        else:
            return NotImplemented
    def __itruediv__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] / other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] / other
            return self
        else:
            return NotImplemented
    def __floordiv__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] // other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item // other for item in self])
        else:
            return NotImplemented
    def __rfloordiv__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] // other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item // other for item in self])
        else:
            return NotImplemented
    def __ifloordiv__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] // other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] // other
            return self
        else:
            return NotImplemented
    def __mod__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] % other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item % other for item in self])
        else:
            return NotImplemented
    def __rmod__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] % other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item % other for item in self])
        else:
            return NotImplemented
    def __imod__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] % other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] % other
            return self
        else:
            return NotImplemented
    def __divmod__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([(self[i] // other[i], self[i] % other[i]) for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([(item // other, item % other) for item in self])
        else:
            return NotImplemented
    def __rdivmod__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([(self[i] // other[i], self[i] % other[i]) for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([(item // other, item % other) for item in self])
        else:
            return NotImplemented
    def __idivmod__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = (self[i] // other[i], self[i] % other[i])
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = (self[i] // other, self[i] % other)
            return self
        else:
            return NotImplemented
    def __pow__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ** other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ** other for item in self])
        else:
            return NotImplemented
    def __rpow__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ** other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ** other for item in self])
        else:
            return NotImplemented
    def __ipow__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] ** other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] ** other
            return self
        else:
            return NotImplemented
    def __and__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] & other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item & other for item in self])
        else:
            return NotImplemented
    def __rand__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] & other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item & other for item in self])
        else:
            return NotImplemented
    def __iand__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] & other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] & other
            return self
        else:
            return NotImplemented
    __rand__ = __and__
    def __or__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] | other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item | other for item in self])
        else:
            return NotImplemented
    def __ror__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] | other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item | other for item in self])
        else:
            return NotImplemented
    def __ior__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] | other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] | other
            return self
        else:
            return NotImplemented
    def __xor__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ^ other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ^ other for item in self])
        else:
            return NotImplemented
    def __rxor__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ^ other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ^ other for item in self])
        else:
            return NotImplemented
    def __ixor__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] ^ other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] ^ other
            return self
        else:
            return NotImplemented
    def __lshift__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] << other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item << other for item in self])
        else:
            return NotImplemented
    def __rlshift__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] << other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item << other for item in self])
        else:
            return NotImplemented
    def __ilshift__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] << other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] << other
            return self
        else:
            return NotImplemented
    def __rshift__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] >> other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item >> other for item in self])
        else:
            return NotImplemented
    def __rrshift__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] >> other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item >> other for item in self])
        else:
            return NotImplemented
    def __irshift__(self, other):
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            for i in range(len(self)):
                self[i] = self[i] >> other[i]
            return self
        elif isinstance(other, (int, float, complex)):
            for i in range(len(self)):
                self[i] = self[i] >> other
            return self
        else:
            return NotImplemented
    def __str__(self):
        return str([str(i) for i in self])

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["hookpy",]

""" __DATA__

__END__ """
