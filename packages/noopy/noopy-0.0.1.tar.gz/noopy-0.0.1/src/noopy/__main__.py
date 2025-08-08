#!/home/twinkle/venv/bin/python

######################################################################
# LIBS

import noopy as nop
from noopy import lispy, arrpy

######################################################################
# MAIN

block = lispy([
    "0", "1", "2", "3", "4", "5",
    "6", "7", "8", "9", "a", "b",
    "c", "d", "e", "f", "g", "h",
    "i", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t",
    "u", "v", "w", "x", "y", "z",
])

######################################################################
# DEFS
def lispri(arr:list=None, n:int=3):
    a_l = len(arr)
    for i in range(a_l):
        if i % n == 0: print("")
        print(arr[i], end=", ")
    print("\n")

######################################################################
# MAIN

print("By the first, this is original array.")
lispri(block, 6)

print("Available split positions.")
lispri(nop.splpos(block))

print("Available split to 9(9x4)?")
print("")
print(nop.is_spl(block, 9))
print("")

print("Split to 9(9x4).")
lispri(nop.splist(block, 9))

print("[ Transpose ]")
lispri(nop.transpose(block, 6, 6), 6)

print("[ Flip LR ]")
lispri(nop.flip(block, 6, 6, 'x'), 6)

print("[ Flip UD ]")
lispri(nop.flip(block, 6, 6, 'y'), 6)

print("[ Flip XX ]")
lispri(nop.flip(block, 6, 6, 'z'), 6)

print("These are 2D Array Simulation from on there.")
print("")

print("Split to 9(9x4).")
lispri(block.splist(9))

print("[ Transpose ]")
lispri(block.transpose(3, 3), 3)

print("[ Flip LR ]")
lispri(block.flip(3, 3, 'x'), 3)

print("[ Flip UD ]")
lispri(block.flip(3, 3, 'y'), 3)

print("[ Flip XX ]")
lispri(block.flip(3, 3, 'z'), 3)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = []

""" __DATA__

__END__ """
