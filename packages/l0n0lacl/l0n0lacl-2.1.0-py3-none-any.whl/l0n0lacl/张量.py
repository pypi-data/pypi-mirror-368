from .设备内存 import 设备内存
from .动态库加载器 import 加载cann_toolkit_lib64中的库
from .数据类型 import 将numpy类型转换为acl类型, 将acl类型转换为numpy类型
from .日志 import 记录acl返回值错误日志并抛出异常, 记录acl空指针日志并抛出异常
from .设备 import 设备
from typing import Union, List
import numpy as np
import ctypes
import math

libnnopbase = 加载cann_toolkit_lib64中的库('libnnopbase.so')
# ACL_FUNC_VISIBILITY aclTensor * aclCreateTensor(
#     const int64_t * viewDims,
#     uint64_t viewDimsNum,
#     aclDataType dataType,
#     const int64_t * stride,
#     int64_t offset,
#     aclFormat format,
#     const int64_t * storageDims,
#     uint64_t storageDimsNum,
#     void * tensorData)
libnnopbase.aclCreateTensor.argtypes = [
    ctypes.c_void_p,  # viewDims
    ctypes.c_uint64,  # viewDimsNum
    ctypes.c_int,    # dataType
    ctypes.c_void_p,  # stride
    ctypes.c_int64,  # offset
    ctypes.c_int,    # format
    ctypes.c_void_p,  # storageDims
    ctypes.c_uint64,  # storageDimsNum
    ctypes.c_void_p,  # tensorData
]
libnnopbase.aclCreateTensor.restype = ctypes.c_void_p
libnnopbase.aclDestroyTensor.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyTensor.restype = ctypes.c_int


# aclTensorList *aclCreateTensorList(const aclTensor *const *value, uint64_t size)
libnnopbase.aclCreateTensorList.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateTensorList.restype = ctypes.c_void_p
# aclnnStatus aclDestroyTensorList(const aclTensorList *array)
libnnopbase.aclDestroyTensorList.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyTensorList.restype = ctypes.c_int


# aclnnStatus aclInitTensor(
# aclTensor *tensor,
# const int64_t *viewDims,
# uint64_t viewDimsNum,
# aclDataType dataType,
# const int64_t *stride,
# int64_t offset,
# aclFormat format,
# const int64_t *storageDims,
# uint64_t storageDimsNum,
# void *tensorDataAddr)
libnnopbase.aclInitTensor.argtypes = [
    ctypes.c_void_p,  # tensor
    ctypes.c_void_p,  # viewDims
    ctypes.c_uint64,  # viewDimsNum
    ctypes.c_int,    # dataType
    ctypes.c_void_p,  # stride
    ctypes.c_int64,  # offset
    ctypes.c_int,    # format
    ctypes.c_void_p,  # storageDims
    ctypes.c_uint64,  # storageDimsNum
    ctypes.c_void_p,  # tensorData
]
libnnopbase.aclInitTensor.restype = ctypes.c_int


class 张量格式:
    '''
    * UNDEFINED：未知格式，默认值。
    * NCHW：4维数据格式。
    * NHWC：4维数据格式。
    * ND：表示支持任意格式，仅有Square、Tanh等这些单输入对自身处理的算子外，其它需要慎用。
    * NC1HWC0：5维数据格式。其中，C0与微架构强相关，该值等于cube单元的size，例如16；C1是将C维度按照C0切分：C1=C/C0， 若结果不整除，最后一份数据需要padding到C0。
    * FRACTAL_Z：卷积的权重的格式。
    * NC1HWC0_C04：5维数据格式。其中，C0固定为4，C1是将C维度按照C0切分：C1=C/C0， 若结果不整除，最后一份数据需要padding到C0。当前版本不支持。
    * HWCN：4维数据格式。
    * NDHWC：NDHWC格式。对于3维图像就需要使用带D（Depth）维度的格式。
    * FRACTAL_NZ：内部分形格式，用户目前无需使用。
    * NCDHW：NCDHW格式。对于3维图像就需要使用带D（Depth）维度的格式。
    * NDC1HWC0：6维数据格式。相比于NC1HWC0，仅多了D（Depth）维度。
    * FRACTAL_Z_3D：3D卷积权重格式，例如Conv3D/MaxPool3D/AvgPool3D这些算子都需要这种格式来表达。
    * NC：2维数据格式。
    * NCL：3维数据格式。

    说明
    各维度的含义如下：N（Batch）表示批量大小、H（Height）表示特征图高度、W（Width）表示特征图宽度、C（Channels）表示特征图通道、D（Depth）表示特征图深度、L是特征图长度。
    '''
    UNDEFINED = -1
    NCHW = 0
    NHWC = 1
    ND = 2
    NC1HWC0 = 3
    FRACTAL_Z = 4
    NC1HWC0_C04 = 12
    HWCN = 16
    NDHWC = 27
    FRACTAL_NZ = 29
    NCDHW = 30
    NDC1HWC0 = 32
    FRACTAL_Z_3D = 33
    NC = 35
    NCL = 47


class 张量:
    def __init__(self,
                 数据,
                 数据类型: Union[int, None] = None,
                 设备索引: Union[int, None] = None,
                 格式: Union[int, None] = None):
        self.格式 = 格式 or 张量格式.ND
        self.设备索引 = 0
        设备.初始化目标设备(self, 设备索引)
        self.需要执行aclDestroyTensor = True
        if isinstance(数据, np.ndarray):
            self.__从numpy初始化(数据, 数据类型)
        if isinstance(数据, 张量):
            self.__从张量初始化(数据)
        self.__创建()

    def __创建(self):
        # 创建Tensor
        self.张量指针 = libnnopbase.aclCreateTensor(
            self.形状.ctypes.data,
            self.形状.size,
            self.数据类型,
            0,
            0,
            self.格式,
            self.形状.ctypes.data,
            self.形状.size,
            self.内存.设备内存指针
        )
        记录acl空指针日志并抛出异常(self.张量指针, "张量数组 libnnopbase.aclCreateTensor 错误")

    def __从numpy初始化(self,
                    numpy数组: np.ndarray,
                    数据类型: Union[int, None] = None):
        # 类型转换
        self.数据类型 = 将numpy类型转换为acl类型(numpy数组.dtype)
        if 数据类型 is not None and self.数据类型 != 数据类型:
            self.数据类型 = 数据类型
            numpy数组 = numpy数组.astype(将acl类型转换为numpy类型(数据类型))
        # 收集数据
        self.形状 = np.array(numpy数组.shape, dtype=np.int64)
        self.数据个数 = numpy数组.size
        self.单数据大小 = numpy数组.itemsize
        self.数据总byte数 = self.数据个数 * self.单数据大小
        # 256对其
        self.数据需要的设备内存 = int(math.ceil(self.数据总byte数 / 256) * 256) + 256
        # 分配设备内存
        self.内存 = 设备内存(self.数据需要的设备内存)
        # 复制数据
        self.内存.从主机复制数据(numpy数组.ctypes.data, self.数据总byte数)

    def __从张量初始化(self, 数据):
        _数据: 张量 = 数据
        # 类型转换
        self.数据类型 = _数据.数据类型
        self.形状 = _数据.形状
        self.数据个数 = _数据.数据个数
        self.单数据大小 = _数据.单数据大小
        self.数据总byte数 = _数据.数据总byte数
        self.数据需要的设备内存 = _数据.数据需要的设备内存
        self.内存 = 设备内存(self.数据需要的设备内存)
        self.内存.从其他设备复制数据(_数据.内存)

    def __str__(self) -> str:
        return str(self.numpy())

    def __del__(self):
        self._销毁()

    def _销毁(self):
        if not self.需要执行aclDestroyTensor or self.张量指针 is None or self.张量指针 == 0:
            self.张量指针 = 0
            return
        ret = libnnopbase.aclDestroyTensor(self.张量指针)
        self.张量指针 = 0
        记录acl返回值错误日志并抛出异常("aclDestroyTensor", ret)

    def numpy(self) -> np.ndarray:
        设备.切换设备到(self.设备索引)
        设备.同步当前设备流水()
        cpu数据 = np.zeros(self.形状, dtype=将acl类型转换为numpy类型(self.数据类型))
        self.内存.将数据复制到主机(cpu数据.ctypes.data, self.数据总byte数)
        return cpu数据

    @property
    def 指针(self):
        return self.张量指针

    def 变更格式(self, 格式: int):
        self.格式 = 格式
        ret = libnnopbase.aclInitTensor(
            self.指针,
            self.形状.ctypes.data,
            self.形状.size,
            self.数据类型,
            0,
            0,
            self.格式,
            self.形状.ctypes.data,
            self.形状.size,
            self.内存.设备内存指针
        )
        记录acl返回值错误日志并抛出异常('libnnopbase.aclInitTensor错误', ret)
        return self

    def 切换到设备(self, 设备索引: int):
        if 设备索引 == self.设备索引:
            return self
        self._销毁()
        设备.初始化目标设备(self, 设备索引)
        _内存 = self.内存
        self.内存 = 设备内存(self.数据需要的设备内存)
        self.内存.从其他设备复制数据(_内存)
        self.__创建()
        return self


class 张量列表:
    def __init__(self, 数据列表: List[Union[张量, np.ndarray]],
                 设备索引: Union[int, None] = None):
        self.数据列表 = 数据列表
        self.张量指针数组 = np.zeros(len(数据列表), dtype=np.uint64)
        self.张量数组指针 = None
        self._重新创建(设备索引)

    def _重新创建(self, 设备索引: Union[int, None]):
        self._销毁()
        self.设备索引 = 0
        设备.初始化目标设备(self, 设备索引)
        self.张量缓存 = []
        i = 0
        for 数据 in self.数据列表:
            if isinstance(数据, np.ndarray):
                新张量 = 张量(数据, 设备索引=self.设备索引)
                self.张量缓存.append(新张量)
                指针 = 新张量.指针
                新张量.需要执行aclDestroyTensor = False
            else:
                self.张量缓存.append(数据.切换到设备(self.设备索引))
                指针 = 数据.指针
                数据.需要执行aclDestroyTensor = False
            self.张量指针数组[i] = 指针
            i += 1
        self.张量数组指针 = libnnopbase.aclCreateTensorList(
            self.张量指针数组.ctypes.data, self.张量指针数组.size)
        记录acl空指针日志并抛出异常(self.张量数组指针, "张量数组 libnnopbase.aclCreateTensorList")

    def __del__(self):
        self._销毁()

    def _销毁(self):
        if self.张量数组指针 is None or self.张量数组指针 == 0:
            return
        ret = libnnopbase.aclDestroyTensorList(self.张量数组指针)
        self.张量数组指针 = 0
        记录acl返回值错误日志并抛出异常("aclDestroyTensor", ret)

    @property
    def 指针(self):
        return self.张量数组指针

    def 切换到设备(self, 设备索引: int):
        self._重新创建(设备索引)
        return self
