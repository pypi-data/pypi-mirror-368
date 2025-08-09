from .动态库加载器 import 加载cann_toolkit_lib64中的库
from .数据类型 import 将numpy类型转换为acl类型
from .设备 import 设备
from typing import Union, List
import numpy as np
import ctypes


libnnopbase = 加载cann_toolkit_lib64中的库('libnnopbase.so')
# aclIntArray *aclCreateIntArray(const int64_t *value, uint64_t size)
libnnopbase.aclCreateIntArray.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateIntArray.restype = ctypes.c_void_p
# aclnnStatus aclDestroyIntArray(const aclIntArray *array)
libnnopbase.aclDestroyIntArray.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyIntArray.restype = ctypes.c_int

# aclFloatArray *aclCreateFloatArray(const float *value, uint64_t size)
libnnopbase.aclCreateFloatArray.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateFloatArray.restype = ctypes.c_void_p
# aclnnStatus aclDestroyFloatArray(const aclFloatArray *array)
libnnopbase.aclDestroyFloatArray.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyFloatArray.restype = ctypes.c_int

# aclBoolArray *aclCreateBoolArray(const bool *value, uint64_t size)
libnnopbase.aclCreateBoolArray.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateBoolArray.restype = ctypes.c_void_p
# aclnnStatus aclDestroyBoolArray(const aclBoolArray *array)
libnnopbase.aclDestroyBoolArray.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyBoolArray.restype = ctypes.c_int


class 数组:
    def __init__(self,
                 data: Union[np.ndarray, List[Union[int, float, bool]]]):
        data_array: np.ndarray
        # 创建ndarray
        if isinstance(data, list):
            data_array = np.array(data)
        else:
            data_array = data

        # 矫正类型
        self.np_array = data_array
        if data_array.dtype == np.int32:
            data_array = data_array.astype(np.int64)
        elif data_array.dtype == np.float64:
            data_array = data_array.astype(np.float32)

        # 创建Array
        if data_array.dtype == np.int64:
            self.ptr = libnnopbase.aclCreateIntArray(
                data_array.ctypes.data, data_array.size)
        elif data_array.dtype == np.float32:
            self.ptr = libnnopbase.aclCreateFloatArray(
                data_array.ctypes.data, data_array.size)
        elif data_array.dtype == np.bool_:
            self.ptr = libnnopbase.aclCreateBoolArray(
                data_array.ctypes.data, data_array.size)
        else:
            raise Exception(
                "np_array的类型必须是[numpy.int64, numpy.float32, numpy.bool] 的一种, 提供的类型为:" + str(data_array.dtype))
        # 缓存dtype
        self.dtype: int = 将numpy类型转换为acl类型(data_array.dtype)

    def __del__(self):
        ret: int = 0
        if self.np_array.dtype == np.int64:
            ret = libnnopbase.aclDestroyIntArray(self.ptr)
        elif self.np_array.dtype == np.float32:
            ret = libnnopbase.aclDestroyFloatArray(self.ptr)
        elif self.np_array.dtype == np.bool_:
            ret = libnnopbase.aclDestroyBoolArray(self.ptr)
        assert (ret == 0)

    @property
    def 指针(self):
        return self.ptr
