import acl
from .日志 import 记录acl返回值错误日志并抛出异常
from typing import Union
from .设备 import 设备
import numpy as np


class 内存分配方案:
    """
    0：ACL_MEM_MALLOC_HUGE_FIRST，当申请的内存小于等于1M时，即使使用该内存分配规则，也是申请普通页的内存。当申请的内存大于1M时，优先申请大页内存，如果大页内存不够，则使用普通页的内存。
    1：ACL_MEM_MALLOC_HUGE_ONLY，仅申请大页，如果大页内存不够，则返回错误。
    2：ACL_MEM_MALLOC_NORMAL_ONLY，仅申请普通页。
    3：ACL_MEM_MALLOC_HUGE_FIRST_P2P，仅Device之间内存复制场景下申请内存时使用该选项，表示优先申请大页内存，如果大页内存不够，则使用普通页的内存。预留选项。
    4：ACL_MEM_MALLOC_HUGE_ONLY_P2P，仅Device之间内存复制场景下申请内存时使用该选项，仅申请大页内存，如果大页内存不够，则返回错误。预留选项。
    5：ACL_MEM_MALLOC_NORMAL_ONLY_P2P，仅Device之间内存复制场景下申请内存时使用该选项，仅申请普通页的内存。预留选项。
    """
    大页优先_小于1M普通页_大于1M优先使用大页 = 0
    仅分配大页_大页不够_返回错误 = 1
    仅分配普通页 = 2
    设备之间复制时使用的大页优先策略 = 3
    设备之间复制时使用的仅申请大页 = 4
    设备之间复制时使用的仅申请普通页 = 5
    ACL_MEM_TYPE_LOW_BAND_WIDTH = 0x0100
    ACL_MEM_TYPE_HIGH_BAND_WIDTH = 0x1000

# typedef enum aclrtMemcpyKind {
#     ACL_MEMCPY_HOST_TO_HOST,     // Host内的内存复制
#     ACL_MEMCPY_HOST_TO_DEVICE,   // Host到Device的内存复制
#     ACL_MEMCPY_DEVICE_TO_HOST,   // Device到Host的内存复制
#     ACL_MEMCPY_DEVICE_TO_DEVICE, // Device内或两个Device间的内存复制
#     ACL_MEMCPY_DEFAULT，         // 由系统根据源、目的内存地址自行判断拷贝方向
#     ACL_MEMCPY_HOST_TO_BUF_TO_DEVICE,   // Host到Device的内存复制，但Host内存会暂存在Runtime管理的缓存中，内存复制接口调用成功后，就可以释放Host内存
#     ACL_MEMCPY_INNER_DEVICE_TO_DEVICE,  // Device内的内存复制
#     ACL_MEMCPY_INTER_DEVICE_TO_DEVICE,  // 两个Device之间的内存复制
# } aclrtMemcpyKind;


class 内存复制类型:
    主机到主机 = 0
    主机到设备 = 1
    设备到主机 = 2
    设备内或两个设备间的内存复制 = 3
    自行判断拷贝方向 = 4
    带缓存的主机到设备 = 5
    设备内部复制 = 6
    两个设备之间 = 7


class 设备内存:
    def __init__(self, 内存大小: int, 策略: Union[int, None] = None):
        self.设备索引 = 设备.当前设备索引
        self.内存大小 = 内存大小
        self.设备内存指针, ret = acl.rt.malloc(
            内存大小, 策略 or 内存分配方案.大页优先_小于1M普通页_大于1M优先使用大页)
        记录acl返回值错误日志并抛出异常("分配内存失败", ret)

    def __del__(self):
        if self.设备内存指针 is None:
            return
        acl.rt.free(self.设备内存指针)

    @property
    def 指针(self):
        return self.设备内存指针

    def 从主机复制数据(self, 主机内存指针: int, 要复制的数据大小: int):
        要复制的数据大小 = int(min(要复制的数据大小, self.内存大小))
        ret = acl.rt.memcpy(
            self.设备内存指针,
            要复制的数据大小,
            主机内存指针,
            要复制的数据大小,
            内存复制类型.主机到设备,
        )
        记录acl返回值错误日志并抛出异常("从主机复制数据", ret)

    def 将数据复制到主机(self, 主机内存指针: int, 要复制的数据大小: int):
        要复制的数据大小 = int(min(要复制的数据大小, self.内存大小))
        ret = acl.rt.memcpy(
            主机内存指针,
            要复制的数据大小,
            self.设备内存指针,
            要复制的数据大小,
            内存复制类型.设备到主机,
        )
        记录acl返回值错误日志并抛出异常("将数据复制到主机", ret)

    def 从其他设备复制数据(self, 其他设备内存):
        _内存: 设备内存 = 其他设备内存
        要复制的数据大小 = int(min(_内存.内存大小, self.内存大小))
        if 设备.尝试开启当前设备与指定设备之间的内存复制成功(_内存.设备索引):
            ret = acl.rt.memcpy(
                self.设备内存指针,
                要复制的数据大小,
                _内存.指针,
                要复制的数据大小,
                内存复制类型.设备内或两个设备间的内存复制,
            )
            记录acl返回值错误日志并抛出异常("从其他设备复制数据", ret)
            return
        主机内存 = np.zeros([要复制的数据大小], np.uint8)
        _内存.将数据复制到主机(主机内存.ctypes.data, 要复制的数据大小)
        self.从主机复制数据(主机内存.ctypes.data, 要复制的数据大小)