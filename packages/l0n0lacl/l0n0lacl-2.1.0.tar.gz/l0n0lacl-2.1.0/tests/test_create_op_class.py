from l0n0lacl import *
import numpy as np
import opp
a = 张量(np.ones((2, 3)) * 2)
other =  张量(np.ones((2, 3)) * 3)
out = 张量(np.zeros([2, 3]))
opp.Add(a, other, 1.2, out)
print(out)

a = np.arange(12).reshape(3, 4).astype(np.float32)
b = np.arange(12, 24).reshape(3, 4).astype(np.float32)
out = 张量(np.zeros((6, 4)).astype(np.float32))
opp.Cat([a, b], 0, out)
print(out)

a = 张量(np.arange(3).astype(np.float32))
b = 张量(np.arange(3, 6).astype(np.float32))
out = 张量(np.zeros((3)).astype(np.float32))
opp.MaxN([a, b], out)
print(out)