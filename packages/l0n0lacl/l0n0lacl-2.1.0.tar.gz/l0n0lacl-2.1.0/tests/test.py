from l0n0lacl import *
import numpy as np
import ctypes
import time
设备.设置内存共享组([0, 1])
a = np.random.uniform(-2, -1, (1024))
a_out = np.zeros_like(a)
a = 张量(a)
a_out = 张量(a_out)
a.切换到设备(1)
# a_out.切换到设备(1)
fn = 算子运行器('Abs')
out = fn(a, a_out)
print(out[1])

fn = 算子运行器('InplaceAcos')
a = np.random.uniform(-1, 1, (2000,2000)).astype(np.float16)
print(a)
out = fn(a)
print(out[0])

fn = 算子运行器('AdaptiveAvgPool2d')
a = np.random.uniform(0, 100, (2, 100, 100)).astype(np.float32)
out = np.zeros((2, 3, 3), dtype=a.dtype)
a = 张量(a, 格式=张量格式.NCL)
out = 张量(out).变更格式(张量格式.NCL)
output = fn(a, [3, 3], out)
print(output[2])


fn = 算子运行器('Addmv')
s = np.ones(3, dtype=np.float32)
mat = np.random.uniform(-1, 1, (3, 40000)).astype(np.float32)
vec = np.random.uniform(-1, 1, 40000).astype(np.float32)
alpha = 1.2
beta = 标量(1.1)
out = np.zeros(3, dtype=np.float32)
output = fn(s, mat, vec, alpha, beta, out, ctypes.c_int8(1))
print(output[-2])

fn = 算子运行器('Any')
s = np.random.uniform(-1, -0.5, (3, 4))
out = np.zeros(3, dtype=np.bool_)
output = fn(s, [1], ctypes.c_bool(False), out)
print(output[-1])
