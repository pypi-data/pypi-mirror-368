from .动态库加载器 import 加载cann_toolkit_lib64中的库
from .数据类型 import 将numpy类型转换为acl类型
from .日志 import 记录acl返回值错误日志并抛出异常, 记录acl空指针日志并抛出异常
from typing import Union, List
import numpy as np
import ctypes


libnnopbase = 加载cann_toolkit_lib64中的库('libnnopbase.so')
# aclScalar *aclCreateScalar(void *value, aclDataType dataType)
libnnopbase.aclCreateScalar.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateScalar.restype = ctypes.c_void_p
# aclnnStatus aclDestroyScalar(const aclScalar *scalar)
libnnopbase.aclDestroyScalar.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyScalar.restype = ctypes.c_int

# aclScalarList *aclCreateScalarList(const aclScalar *const *value, uint64_t size)
libnnopbase.aclCreateScalarList.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateScalarList.restype = ctypes.c_void_p
# aclnnStatus aclDestroyScalarList(const aclScalarList *array)
libnnopbase.aclDestroyScalarList.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyScalarList.restype = ctypes.c_int


class 标量:
    def __init__(self, 数值: Union[np.ndarray, int, float, bool]) -> None:
        if not isinstance(数值, np.ndarray):
            数值 = np.array(数值)
        self.数值 = 数值
        self.类型 = 将numpy类型转换为acl类型(数值.dtype)
        self.标量指针 = libnnopbase.aclCreateScalar(self.数值.ctypes.data, self.类型)
        记录acl空指针日志并抛出异常(self.标量指针, '标量 libnnopbase.aclCreateScalar错误')

    def __del__(self):
        if self.标量指针 == 0:
            return
        self.标量指针 = 0
        ret = libnnopbase.aclDestroyScalar(self.标量指针)
        记录acl返回值错误日志并抛出异常('libnnopbase.aclDestroyScalar(self.标量指针)', ret)

    @property
    def 指针(self):
        return self.标量指针


class 标量数组:
    def __init__(self, 数值列表: List[Union[int, float, bool]]) -> None:
        self.标量指针列表 = np.zeros(len(数值列表), dtype=np.uint64)
        # 创输入数据指针
        self.数值列表: List[np.ndarray] = []
        for 数值 in 数值列表:
            self.数值列表.append(np.array(数值))
        # 创建标量
        for i in range(0, self.标量指针列表.size):
            数值 = self.数值列表[i]
            新标量指针 = libnnopbase.aclCreateScalar(
                数值.ctypes.data, 将numpy类型转换为acl类型(数值.dtype))
            记录acl空指针日志并抛出异常(新标量指针, '标量数组 libnnopbase.aclCreateScalar错误')
            self.标量指针列表[i] = 新标量指针

        # 创建标量列表
        self.标量列表指针 = libnnopbase.aclCreateScalarList(
            self.标量指针列表.ctypes.data, self.标量指针列表.size)
        记录acl空指针日志并抛出异常(self.标量列表指针, '标量数组  libnnopbase.aclCreateScalarList错误')

    def __del__(self):
        if self.标量列表指针 == 0:
            return
        self.标量列表指针 = 0
        ret = libnnopbase.aclDestroyScalarList(self.标量列表指针)
        记录acl返回值错误日志并抛出异常('libnnopbase.aclDestroyScalarList(self.标量列表指针)', ret)

    @property
    def 指针(self):
        return self.标量列表指针
