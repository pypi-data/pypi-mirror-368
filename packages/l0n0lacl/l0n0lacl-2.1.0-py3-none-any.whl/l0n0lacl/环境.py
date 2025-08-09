import acl
import os
from typing import Union
from .日志 import 记录acl返回值错误日志并抛出异常,记录调试日志
from .设备 import 设备


class 环境管理器:
    def __init__(self, 配置文件目录: Union[str, None] = None) -> None:
        self.__初始化配置文件(配置文件目录)
        self.__初始化版本信息()

    def __初始化配置文件(self, 配置文件目录: Union[str, None]):
        if 配置文件目录 is None:
            # 检查环境变量
            配置文件目录 = os.environ.get("ACL_CONFIG_FILE")
        if 配置文件目录 is None:
            当前目录配置文件 = f'{os.path.curdir}/acl_config.json'
            if os.path.exists(当前目录配置文件):
                配置文件目录 = 当前目录配置文件
        self.配置文件目录 = 配置文件目录

    def __初始化版本信息(self):
        大版本号, 小版本号, 补丁版本号, ret = acl.get_version()
        if ret == 0:
            self.大版本号 = 大版本号
            self.小版本号 = 小版本号
            self.补丁版本号 = 补丁版本号
        else:
            记录acl返回值错误日志并抛出异常('acl.get_version()', ret)


环境 = 环境管理器()


def 开始():
    if 环境.配置文件目录 is None:
        ret: int = acl.init()
    else:
        ret: int = acl.init(环境.配置文件目录)
    记录acl返回值错误日志并抛出异常(f"acl.init({环境.配置文件目录})", ret)
    设备.开始()


def 结束():
    设备.结束()
    ret = acl.finalize()
    记录acl返回值错误日志并抛出异常(f"acl.finalize()", ret)
