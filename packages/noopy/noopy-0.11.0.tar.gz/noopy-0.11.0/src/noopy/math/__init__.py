#!/home/twinkle/venv/bin/python

import math

class mathpy:
    pi = 3.141592653589793
    pih = pi / 2
    def __init__(self, *args, **kwargs):
        self.loaded=True
    # sign
    def sign(self):
        return type(self)([(-1 if i < 0 else 1) for i in self])
    # sqrt
    def sqrt(self):
        return type(self)([i**0.5 for i in self])
    # sqrtpi
    def sqrtpi(self):
        return type(self)([(self.pi*i)**0.5 for i in self])
    # signed_sqrt
    def signed_sqrt(self):
        si = self.sign()
        return type(self)([(abs(self[i])**0.5)*si[i] for i in range(len(self))])
    # signed_sqrtpi
    def signed_sqrtpi(self):
        si = self.sign(); return type(self)([(abs(self.pi*self[i])**0.5)*si[i] for i in range(len(self))])

## Signed SQRT
def signed_sqrt_digits(self, x):
    si = -1.0 if x < 0 else 1.0
    return si * math.sqrt(abs(x))

## LOG
def decimal_placed(self, x):
    return abs(int(math.floor(math.log10(abs(x)))))
def decimal_placed_shift(self, x):
        return x/(10 ** math.floor(math.log10(abs(x))))
def decimal_scaler(self, x):
    while math.fmod(x, 10) != 0: x *= 10
    return math.ceil(x/10)
def decimal_placed_shift_all(self, x):
    return decimal_scaler(x/(10 ** math.floor(math.log10(abs(x)))))

## Float GCD
def fgcd(self, a, b):
    sc_a = decimal_placed(a)
    sc_b = decimal_placed(b)
    sc = sc_b if sc_b > sc_a else sc_a
    fac = pow(10, sc)
    a = int(round(a*fac))
    b = int(round(b*fac))
    while b:
        a, b = b, a % b
    return round(a / fac, sc)
## Float LCM
def flcm(self, a, b):
    return ((a * b) / self.fgcd(a, b))

## Decimal GCD
def igcd(self, a, b):
    while b:
        a, b = b, a % b
    return round(a / fac, sc)
## Decimal LCM
def ilcm(self, a, b):
    return ((a * b) / self.igcd(a, b))

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["mathpy",]

""" __DATA__

__END__ """
