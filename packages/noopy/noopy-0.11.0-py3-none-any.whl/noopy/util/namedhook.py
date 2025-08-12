#!/home/twinkle/venv/bin/python

from noopy.util.globals import __globals__

#def __add__(self, other):
#    return type(self)([self[i] + other[i] for i in range(len(other))]) if isinstance(other, list) else type(self)([self[i] + other for i in range(len(self))])

class hookpy():
    def __init__(self, *args, **kwargs):
        super(hookpy, self).__init__(*args, **kwargs)
    def __add__(self, other):
        print("__add__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] + other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item + other for item in self])
        else:
            return NotImplemented
    def __radd__(self, other):
        print("__radd__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] + other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item + other for item in self])
        else:
            return NotImplemented
    def __iadd__(self, other):
        print("__iadd__")
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
        print("__sub__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] - other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item - other for item in self])
        else:
            return NotImplemented
    def __rsub__(self, other):
        print("__rsub__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] - other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item - other for item in self])
        else:
            return NotImplemented
    def __isub__(self, other):
        print("__isub__")
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
        print("__mul__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([self[i] * other for i in range(len(self))])
        else:
            return NotImplemented
    def __rmul__(self, other):
        print("__rmul__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item * other for item in self])
        else:
            return NotImplemented
    def __imul__(self, other):
        print("__imul__")
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
        print("__matmul__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            r = 0; r += ([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item * other for item in self])
        else:
            return NotImplemented
    def __rmatmul__(self, other):
        print("__rmatmul__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item * other for item in self])
        else:
            return NotImplemented
    def __imatmul__(self, other):
        print("__imatmul__")
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
        print("__truediv__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] / other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item / other for item in self])
        else:
            return NotImplemented
    def __rtruediv__(self, other):
        print("__rtruediv__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] / other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item / other for item in self])
        else:
            return NotImplemented
    def __itruediv__(self, other):
        print("__itruediv__")
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
        print("__floordiv__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] // other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item // other for item in self])
        else:
            return NotImplemented
    def __rfloordiv__(self, other):
        print("__rfloordiv__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] // other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item // other for item in self])
        else:
            return NotImplemented
    def __ifloordiv__(self, other):
        print("__ifloordiv__")
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
        print("__mod__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] % other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item % other for item in self])
        else:
            return NotImplemented
    def __rmod__(self, other):
        print("__rmod__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] % other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item % other for item in self])
        else:
            return NotImplemented
    def __imod__(self, other):
        print("__imod__")
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
        print("__divmod__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([(self[i] // other[i], self[i] % other[i]) for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([(item // other, item % other) for item in self])
        else:
            return NotImplemented
    def __rdivmod__(self, other):
        print("__rdivmod__")
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
        print("__pow__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ** other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ** other for item in self])
        else:
            return NotImplemented
    def __rpow__(self, other):
        print("__rpow__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ** other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ** other for item in self])
        else:
            return NotImplemented
    def __ipow__(self, other):
        print("__ipow__")
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
        print("__and__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] & other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item & other for item in self])
        else:
            return NotImplemented
    def __rand__(self, other):
        print("__rand__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] & other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item & other for item in self])
        else:
            return NotImplemented
    def __iand__(self, other):
        print("__iand__")
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
        print("__or__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] | other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item | other for item in self])
        else:
            return NotImplemented
    def __ror__(self, other):
        print("__ror__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] | other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item | other for item in self])
        else:
            return NotImplemented
    def __ior__(self, other):
        print("__ior__")
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
        print("__xor__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ^ other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ^ other for item in self])
        else:
            return NotImplemented
    def __rxor__(self, other):
        print("__rxor__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] ^ other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item ^ other for item in self])
        else:
            return NotImplemented
    def __ixor__(self, other):
        print("__ixor__")
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
        print("__lshift__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] << other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item << other for item in self])
        else:
            return NotImplemented
    def __rlshift__(self, other):
        print("__rlshift__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] << other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item << other for item in self])
        else:
            return NotImplemented
    def __ilshift__(self, other):
        print("__ilshift__")
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
        print("__rshift__")
        if isinstance(other, (list, tuple, str)):
            if len(self) != len(other):
                raise ValueError("list lengths must be the same for element-wise addition.")
            return type(self)([self[i] >> other[i] for i in range(len(self))])
        elif isinstance(other, (int, float, complex)):
            return type(self)([item >> other for item in self])
        else:
            return NotImplemented
    def __rrshift__(self, other):
        print("__rrshift__")
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
