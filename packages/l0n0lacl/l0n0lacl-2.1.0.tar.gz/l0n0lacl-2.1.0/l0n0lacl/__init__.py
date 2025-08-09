from .utils import *
from .算子运行器 import 算子运行器
from .动态库加载器 import 加载cann_toolkit_lib64中的库, 加载库
from .设备 import 设备
from .环境 import 开始, 结束
from .张量 import 张量, 张量格式, 张量列表
from .数组 import 数组
from .标量 import 标量, 标量数组
from .日志 import *
import atexit

开始()


@atexit.register
def __退出():
    结束()
