import acl
import os
from .日志 import 记录acl返回值错误日志并抛出异常
from typing import Union, List, MutableMapping
from .动态库加载器 import 加载cann_toolkit_lib64中的库
import ctypes
import numpy as np

libascendcl = 加载cann_toolkit_lib64中的库('libascendcl.so')

# aclError aclrtGetDeviceCount(uint32_t *count)
libascendcl.aclrtGetDeviceCount.argtypes = [
    ctypes.c_void_p
]
libascendcl.aclrtGetDeviceCount.restype = ctypes.c_int32


def 设备数量() -> int:
    ret = np.zeros([1], dtype=np.uint32)
    status = libascendcl.aclrtGetDeviceCount(ret.ctypes.data)
    记录acl返回值错误日志并抛出异常('libascendcl.aclrtGetDeviceCount', status)
    return int(ret[0])


# aclError aclrtDeviceCanAccessPeer(int32_t *canAccessPeer, int32_t deviceId, int32_t peerDeviceId)
libascendcl.aclrtDeviceCanAccessPeer.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int32,
    ctypes.c_int32
]
libascendcl.aclrtDeviceCanAccessPeer.restype = ctypes.c_int32


def 设备间支持直接复制内存(设备ID1: int, 设备ID2: int) -> bool:
    ret = np.ones([1], dtype=np.int32)
    status = libascendcl.aclrtDeviceCanAccessPeer(
        ret.ctypes.data, 设备ID1, 设备ID2)
    记录acl返回值错误日志并抛出异常('libascendcl.aclrtDeviceCanAccessPeer', status)
    return int(ret[0]) == 1


# aclError aclrtDeviceEnablePeerAccess(int32_t peerDeviceId, uint32_t flags)
libascendcl.aclrtDeviceEnablePeerAccess.argtypes = [
    ctypes.c_int32,
    ctypes.c_uint32
]
libascendcl.aclrtDeviceEnablePeerAccess.restype = ctypes.c_int32


def 开启当前设备与指定设备之间的内存复制(设备ID: int):
    status = libascendcl.aclrtDeviceEnablePeerAccess(设备ID, 0)
    记录acl返回值错误日志并抛出异常('libascendcl.aclrtDeviceEnablePeerAccess', status)


# aclError aclrtDeviceDisablePeerAccess(int32_t peerDeviceId)
libascendcl.aclrtDeviceDisablePeerAccess.argtypes = [
    ctypes.c_int32
]
libascendcl.aclrtDeviceDisablePeerAccess.restype = ctypes.c_int32


def 关闭当前设备与指定设备之间的内存复制(设备ID: int):
    status = libascendcl.aclrtDeviceDisablePeerAccess(设备ID, 0)
    记录acl返回值错误日志并抛出异常('libascendcl.aclrtDeviceDisablePeerAccess', status)


class 设备信息:
    AICore数量 = 0
    VectorCore数量 = 1
    L2Buffer大小 = 2


class 设备管理器:
    def __init__(self) -> None:
        self.初始化成功 = False
        self.设备内存共享组: MutableMapping[int, List[int]] = {}

    def __del__(self):
        self.结束()

    def __初始化上下文与执行流水线(self):
        for i in range(self.设备数量 - 1, -1, -1):
            self._设置当前设备(i)

    def 开始(self):
        设备ID字符串 = os.environ.get("ASCEND_VISIBLE_DEVICES")
        if 设备ID字符串 is None:
            self.设备IDS = range(设备数量())
        else:
            self.设备IDS = [int(ID) for ID in 设备ID字符串.strip().split(',')]
        self.__初始化上下文与执行流水线()
        self.初始化成功 = True

    def 结束(self):
        for 设备ID in self.设备IDS:
            ret = acl.rt.reset_device_force(设备ID)
            记录acl返回值错误日志并抛出异常(f'acl.rt.reset_device({设备ID}))', ret)
        self.设备IDS = []

    @property
    def 设备数量(self):
        return len(self.设备IDS)

    @property
    def 当前设备索引(self):
        当前设备ID, ret = acl.rt.get_device()
        记录acl返回值错误日志并抛出异常(f'acl.rt.get_device())', ret)
        return self.设备IDS.index(当前设备ID)

    def _设备信息(self, 设备索引: int, 信息类型: int):
        设备ID = self.设备IDS[设备索引]
        value, ret = acl.get_device_capability(设备ID, 信息类型)
        记录acl返回值错误日志并抛出异常(f'acl.get_device_capability(设备ID, {信息类型})', ret)
        return value

    def 设备AICore数量(self, 设备索引: int):
        return self._设备信息(设备索引, 设备信息.AICore数量)

    def 设备VectorCore数量(self, 设备索引: int):
        return self._设备信息(设备索引, 设备信息.VectorCore数量)

    def 设备L2Buffer大小(self, 设备索引: int):
        return self._设备信息(设备索引, 设备信息.L2Buffer大小)

    def _设置当前设备(self, 设备索引: int):
        设备ID = self.设备IDS[设备索引]
        ret = acl.rt.set_device(设备ID)
        记录acl返回值错误日志并抛出异常(f'acl.set_device({设备ID})', ret)

    def 切换设备到(self, 设备索引: int):
        if self.初始化成功:
            if self.当前设备索引 == 设备索引:
                return
            self.同步当前设备流水()
        self._设置当前设备(设备索引)

    def 初始化目标设备(self, 目标, 设备索引: Union[int, None] = None):
        if 设备索引 is not None and self.当前设备索引 != 设备索引:
            目标.设备索引 = 设备索引
            self.切换设备到(设备索引)
        else:
            目标.设备索引 = self.当前设备索引

    def 同步当前设备流水(self):
        ret = acl.rt.synchronize_stream(0)
        记录acl返回值错误日志并抛出异常(f"acl.rt.synchronize_stream({0})", ret)

    def 设备间能够复制内存(self, 设备索引1: int, 设备索引2: int):
        设备ID1 = self.设备IDS[设备索引1]
        设备ID2 = self.设备IDS[设备索引2]
        if 设备ID1 == 设备ID2:
            return True
        return 设备间支持直接复制内存(设备ID1, 设备ID2)

    def 尝试开启当前设备与指定设备之间的内存复制成功(self, 设备索引: int):
        if self.当前设备索引 == 设备索引:
            return True
        if not self.设备间能够复制内存(self.当前设备索引, 设备索引):
            return False
        开启当前设备与指定设备之间的内存复制(设备索引)
        return True

    def 关闭当前设备与指定设备之间的内存复制(self, 设备索引: int):
        if self.当前设备索引 == 设备索引:
            return True
        if not self.设备间能够复制内存(self.当前设备索引, 设备索引):
            return
        关闭当前设备与指定设备之间的内存复制(设备索引)
        return True

    def 设置内存共享组(self, 设备索引列表: List[int]):
        for 设备索引 in 设备索引列表:
            self.设备内存共享组[设备索引] = 设备索引列表

    def 设备间是否共享内存(self, 设备索引列表: List[int]):
        for 设备索引 in 设备索引列表:
            共享数据 = self.设备内存共享组.get(设备索引)
            if 共享数据 is None:
                return False
            for 设备索引2 in 设备索引列表:
                if 设备索引2 != 设备索引:
                    try:
                        共享数据.index(设备索引2)
                    except:
                        return False
            return True


设备 = 设备管理器()
