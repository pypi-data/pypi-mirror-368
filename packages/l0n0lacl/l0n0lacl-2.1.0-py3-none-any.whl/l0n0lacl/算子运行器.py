from .张量 import 张量, 张量列表
from .数组 import 数组
from .标量 import 标量, 标量数组
from .设备内存 import 设备内存
from .设备 import 设备
from .动态库加载器 import 加载库
from .日志 import 记录错误日志并抛出异常, 记录acl返回值错误日志并抛出异常, 记录错误日志
from .utils import 驼峰转下划线
from typing import Dict, Tuple, List
import numpy as np
import os
import ctypes
import re


ascend_home_path = os.environ["ASCEND_HOME_PATH"]
ascend_opp_path = os.environ['ASCEND_OPP_PATH']
不使用自定义算子 = os.environ.get('NO_VENDORS_OPP') == '1'

_自定义算子缓存 = {}
_自定义算子include缓存 = {}
_官方算子缓存 = {}


def _缓存算子(库内容: str, 库目录: str, 自定义: bool):
    算子名称迭代器 = re.finditer(r'aclnn(.+)GetWorkspaceSize', 库内容)
    for 算子名称匹配结果 in 算子名称迭代器:
        算子名称 = 算子名称匹配结果.group(1)
        if 自定义:
            _自定义算子缓存[算子名称] = 加载库(库目录)
            include目录 = '/'.join(库目录.split('/')[:-2]) + f'/include'
            for 文件名 in os.listdir(include目录):
                if not 文件名.endswith('.h'):
                    continue
                地址 = include目录 + '/' + 文件名
                with open(地址) as fp:
                    内容 = fp.read()
                if 内容.find(f'aclnn{算子名称}GetWorkspaceSize') != -1:
                    include目录 = 地址
                    break
            _自定义算子include缓存[算子名称] = include目录
        else:
            _官方算子缓存[算子名称] = 加载库(库目录)


def 缓存所有算子库():
    # 自定义库
    前缀目录 = f'{ascend_opp_path}/vendors'
    for 算子前缀 in os.listdir(前缀目录):
        算子前缀目录 = f'{前缀目录}/{算子前缀}'
        if not os.path.isdir(算子前缀目录):
            continue
        库目录 = f'{算子前缀目录}/op_api/lib/libcust_opapi.so'
        结果 = os.popen(
            f'nm -D {库目录} | grep -e "GetWorkspaceSize"').read().strip()
        if len(结果) < 0:
            continue
        _缓存算子(结果, 库目录, True)

    nn算子目录 = f"{ascend_home_path}/lib64/libopapi.so"
    结果 = os.popen(
        f'nm -D {nn算子目录} | grep -e "GetWorkspaceSize"').read().strip()
    _缓存算子(结果, nn算子目录, False)


缓存所有算子库()
_找到的自定义算子缓存: Dict[str, Tuple] = {}
_找到的官方算子缓存: Dict[str, Tuple] = {}


def 寻找算子Api(算子名称: str):
    if 不使用自定义算子:
        缓存 = _找到的官方算子缓存.get(算子名称)
    else:
        缓存 = _找到的自定义算子缓存.get(算子名称) or _找到的官方算子缓存.get(算子名称)
    if 缓存 is not None:
        return 缓存

    自定义算子中找到的 = False
    if 不使用自定义算子:
        库 = _官方算子缓存.get(算子名称)
    else:
        库 = _自定义算子缓存.get(算子名称)
        if 库 is not None:
            自定义算子中找到的 = True
        库 = _官方算子缓存.get(算子名称)
    if 库 is None:
        记录错误日志并抛出异常(f"算子[{算子名称}]没找到对应的库")
    GetWorkspace: ctypes._FuncPointer = getattr(
        库, f"aclnn{算子名称}GetWorkspaceSize")
    算子运行Api: ctypes._FuncPointer = getattr(库, f"aclnn{算子名称}")
    if GetWorkspace is None:
        raise Exception(f"aclnn{算子名称}GetWorkspaceSize 没找到")
    if 算子运行Api is None:
        raise Exception(f"aclnn{算子名称} 没找到")
    GetWorkspace.restype = ctypes.c_int
    算子运行Api.argtypes = [
        ctypes.c_void_p,  # workspace指针
        ctypes.c_uint64,  # workspace大小
        ctypes.c_void_p,  # 运行器(executor)
        ctypes.c_void_p,  # 流水线(stream)
    ]
    算子运行Api.restype = ctypes.c_int

    if 自定义算子中找到的:
        _找到的自定义算子缓存[算子名称] = (GetWorkspace, 算子运行Api)
    else:
        _找到的官方算子缓存[算子名称] = (GetWorkspace, 算子运行Api)

    return GetWorkspace, 算子运行Api


def 根据算子名称获取include文件(算子名称: str, 跳过自定义算子: bool = False):
    include文件位置 = None
    if not 跳过自定义算子:
        include文件位置 = _自定义算子include缓存.get(算子名称)
    if include文件位置 is None:
        下划线名称 = 驼峰转下划线(算子名称)
        if 下划线名称.startswith('inplace_'):
            下划线名称 = 下划线名称[len('inplace_'):]
        include文件位置 = f'{ascend_home_path}/include/aclnnop/aclnn_{下划线名称}.h'
    try:
        with open(include文件位置) as fp:
            文件内容 = fp.read()
    except:
        记录错误日志(include文件位置, '不存在')
        return
    return 文件内容


def 根据include声明参数类型转换为python类型(参数类型: str):
    if 参数类型 == 'aclTensor*':
        参数类型 = 'Union[np.ndarray, 张量]'
    if 参数类型 == 'aclTensorList*':
        参数类型 = 'List[Union[张量, np.ndarray]]'
    elif 参数类型 == 'aclScalar*':
        参数类型 = 'Union[int,float,bool,标量]'
    elif 参数类型 == 'aclScalarList*':
        参数类型 = 'Union[List[Union[int, float, bool]],标量数组]'
    elif 参数类型 == 'aclBoolArray*':
        参数类型 = 'Union[List[bool], 数组]'
    elif 参数类型 == 'aclIntArray*':
        参数类型 = 'Union[List[int], 数组]'
    elif 参数类型 == 'aclFloatArray*':
        参数类型 = 'Union[List[float], 数组]'
    elif (参数类型 == 'int8_t'
            or 参数类型 == 'int16_t'
            or 参数类型 == 'int32_t'
            or 参数类型 == 'int'
            or 参数类型 == 'int64_t'
            or 参数类型 == 'uint8_t'
            or 参数类型 == 'uint16_t'
            or 参数类型 == 'uint32_t'
            or 参数类型 == 'usigned int'
            or 参数类型 == 'uint64_t'
            or 参数类型 == 'aclDataType'):
        参数类型 = 'int'
    elif (参数类型 == 'float'
            or 参数类型 == 'double'):
        参数类型 = 'float'
    elif 参数类型 == 'bool':
        参数类型 = 'bool'
    elif 参数类型 == 'char*':
        参数类型 = 'bytes'
    return 参数类型


def 根据include声明参数转换为python参数(参数类型: str, 参数名: str):
    if 参数类型 == 'aclTensor*':
        return f'''
    if isinstance({参数名}, np.ndarray):
        {参数名} = 张量({参数名}, 设备索引 = 设备索引)
    if not isinstance({参数名}, 张量):
        raise TypeError('{参数名} 应该是numpy.ndarray或者是[张量]类型')
'''
    if 参数类型 == 'aclTensorList*':
        return f'''
    {参数名} = 张量列表({参数名}, 设备索引 = 设备索引)
'''
    elif 参数类型 == 'aclScalar*':
        return f'''
    if not isinstance({参数名}, 标量):
        {参数名} = 标量({参数名})
'''
    elif 参数类型 == 'aclScalarList*':
        return f'''
    if not isinstance({参数名}, 标量数组):
        {参数名} = 标量数组({参数名})
'''
    elif 参数类型 == 'aclBoolArray*':
        return f'''
    if not isinstance({参数名}, 数组):
        {参数名} = 数组({参数名})
'''
    elif 参数类型 == 'aclIntArray*':
        return f'''
    if not isinstance({参数名}, 数组):
        {参数名} = 数组({参数名})
'''
    elif 参数类型 == 'aclFloatArray*':
        return f'''
    if not isinstance({参数名}, 数组):
        {参数名} = 数组({参数名})
'''
    return ''


def 根据include声明参数类型转换为ctypes类型(参数类型: str):
    if (参数类型 == 'aclTensor*'
        or 参数类型 == 'aclTensorList*'
        or 参数类型 == 'aclScalar*'
        or 参数类型 == 'aclScalarList*'
        or 参数类型 == 'aclBoolArray*'
        or 参数类型 == 'aclIntArray*'
            or 参数类型 == 'aclFloatArray*'):
        return 'ctypes.c_void_p'
    elif 参数类型 == 'aclDataType':
        return 'ctypes.c_int'
    elif 参数类型 == 'int8_t':
        return 'ctypes.c_byte'
    elif 参数类型 == 'int16_t':
        return 'ctypes.c_short'
    elif 参数类型 == 'int32_t':
        return 'ctypes.c_int'
    elif 参数类型 == 'int':
        return 'ctypes.c_int'    
    elif 参数类型 == 'int64_t':
        return 'ctypes.c_longlong'
    elif 参数类型 == 'uint8_t':
        return 'ctypes.c_ubyte'
    elif 参数类型 == 'uint16_t':
        return 'ctypes.c_ushort'
    elif 参数类型 == 'uint32_t':
        return 'ctypes.c_uint'
    elif 参数类型 == 'unsigned int':
        return 'ctypes.c_uint'    
    elif 参数类型 == 'uint64_t':
        return 'ctypes.c_ulonglong'
    elif 参数类型 == 'float':
        return 'ctypes.c_float'
    elif 参数类型 == 'double':
        return 'ctypes.c_double'
    elif 参数类型 == 'char*':
        return 'ctypes.c_char_p'
    elif 参数类型 == 'bool':
        return 'ctypes.c_bool'
    return ''


def 创建算子函数(include文件内容: str, 目标目录: str, init列表: List[str]):
    for 结果 in re.finditer(fr'aclnn(\w+?)GetWorkspaceSize\(([\s\S]+?)\)', include文件内容):
        算子名称 = 结果.group(1).strip()
            
        # 匹配出GetWorkspaceSize
        结果 = 结果.group(2).strip()
        # 替换调无用的信息
        结果 = re.sub(r'//.*', '', 结果)
        结果 = re.sub(r'/\*[\s\S]*?\*/', '', 结果)
        结果 = re.sub(r'\*\s*\*', '**', 结果)
        结果 = re.sub(r'\s+\*\*', '** ', 结果)
        结果 = re.sub(r'\s+\*', '* ', 结果)
        结果 = re.sub(r'const', '', 结果).strip()
        结果 = [参数.strip() for 参数 in 结果.split(',')]
        结果 = 结果[:-2]

        # 解析参数
        参数声明列表 = []
        参数名列表 = []
        GetWorkspaceSize参数声明列表 = []
        参数初始化代码列表 = []
        for 参数字符串 in 结果:
            参数名: str = ''
            参数类型: str = ''
            ret = re.search(r'([\w\*]+?)\s+?(\w+)', 参数字符串)
            if ret is None:
                记录错误日志并抛出异常(f'{参数字符串} 匹配错误')
                return
            参数类型 = ret.group(1).strip().replace(' ', '')
            参数名 = ret.group(2).strip() + '_'
            if len(参数名) == 0:
                记录错误日志并抛出异常(f'{参数字符串} 参数名为空')
                return
            ctypes类型 = 根据include声明参数类型转换为ctypes类型(参数类型)
            GetWorkspaceSize参数声明列表.append(f'{ctypes类型}, # {参数类型} {参数名}')
            参数初始化代码 = 根据include声明参数转换为python参数(参数类型, 参数名)
            参数类型 = 根据include声明参数类型转换为python类型(参数类型)
            参数初始化代码列表.append(参数初始化代码)
            参数声明列表.append(f'{参数名}: {参数类型}')
            参数名列表.append(参数名)
        GetWorkspaceSize参数声明列表.append('ctypes.c_void_p, # uint64_t*  workspaceSize')
        GetWorkspaceSize参数声明列表.append('ctypes.c_void_p  # aclOpExecutor** executor')
        GetWorkspaceSize参数声明列表字符串 = '\n    '.join(GetWorkspaceSize参数声明列表)
        参数声明字符串 = ',\n    '.join(参数声明列表)
        参数名列表字符串 = ', '.join(参数名列表)
        # 生成代码
        代码 = f'''
from l0n0lacl import *
from typing import Union, List
import numpy as np
import ctypes
算子 = 算子运行器('{算子名称}')
算子.获取workspace大小函数.argtypes = [
    {GetWorkspaceSize参数声明列表字符串}
]

def {算子名称}({参数声明字符串}):
    设备索引 = 算子.检测将要运行的设备索引({参数名列表字符串})
    {''.join(参数初始化代码列表)}
    return 算子.为生成代码提供的调用函数({参数名列表字符串})
'''
        with open(f'{目标目录}/{算子名称}.py', 'w') as fp:
            fp.write(代码)

        init列表.append(f'from .{算子名称} import {算子名称}')


def 为所有算子创建函数(目标目录: str, 跳过自定义算子: bool = False):
    if not os.path.exists(目标目录):
        os.mkdir(目标目录)
    include文件位置 = f'{ascend_home_path}/include/aclnnop'
    init列表 = []
    for 文件名 in os.listdir(include文件位置):
        if not 文件名.endswith('.h') or not 文件名.startswith('aclnn'):
            continue
        with open(f'{include文件位置}/{文件名}') as fp:
            文件内容 = fp.read()
        创建算子函数(文件内容, 目标目录, init列表)

    if not 跳过自定义算子:
        # 自定义库
        前缀目录 = f'{ascend_opp_path}/vendors'
        for 算子前缀 in os.listdir(前缀目录):
            算子前缀目录 = f'{前缀目录}/{算子前缀}'
            if not os.path.isdir(算子前缀目录):
                continue
            include目录 = f'{算子前缀目录}/op_api/include/'
            for 文件名 in os.listdir(include目录):
                if not 文件名.endswith('.h'):
                    continue
                with open(f'{include目录}/{文件名}') as fp:
                    文件内容 = fp.read()
                创建算子函数(文件内容, 目标目录, init列表)

    with open(f'{目标目录}/__init__.py', 'w') as fp:
        fp.write('\n'.join(init列表))


class 算子运行器:
    def __init__(self, 算子名称: str) -> None:
        self.获取workspace大小函数, self.算子执行函数 = 寻找算子Api(算子名称)
        self.executor = np.array([0], dtype=np.uint64)
        self.参数保持不被销毁缓存: list
        self.workspace内存 = None

    def 检测将要运行的设备索引(self, *args):
        用到的设备 = set()
        用到的设备.add(设备.当前设备索引)
        for arg in args:
            if not isinstance(arg, 张量) and not isinstance(arg, 张量列表):
                continue
            用到的设备.add(arg.设备索引)
        用到的设备 = list(用到的设备)
        if len(用到的设备) == 0:
            return
        if len(用到的设备) == 1:
            return 用到的设备.pop()
        if 设备.设备间是否共享内存(用到的设备):
            return None
        raise Exception(f'用到了很多设备但不共享内存{用到的设备}')

    def 根据输入将ndarray创建为张量并缓存参数(self, *args):
        设备索引 = self.检测将要运行的设备索引(*args)
        self.参数保持不被销毁缓存 = []
        for arg in args:
            if isinstance(arg, np.ndarray):
                self.参数保持不被销毁缓存.append(张量(arg, 设备索引=设备索引))
            elif isinstance(arg, list):
                if isinstance(arg[0], np.ndarray) or isinstance(arg[0], 张量):
                    self.参数保持不被销毁缓存.append(张量列表(arg, 设备索引=设备索引))
                else:
                    self.参数保持不被销毁缓存.append(数组(arg))
            elif isinstance(arg, int) or isinstance(arg, float) or isinstance(arg, bool):
                self.参数保持不被销毁缓存.append(标量(arg))
            else:
                self.参数保持不被销毁缓存.append(arg)

    def GetWorkspaceSize函数的参数(self):
        调用算子时传入的参数 = []
        for arg in self.参数保持不被销毁缓存:
            if (isinstance(arg, 张量)
                or isinstance(arg, 张量列表)
                or isinstance(arg, 标量)
                or isinstance(arg, 标量数组)
                    or isinstance(arg, 数组)):
                调用算子时传入的参数.append(arg.指针)
            elif (isinstance(arg, ctypes.c_int8)
                  or isinstance(arg, ctypes.c_int16)
                  or isinstance(arg, ctypes.c_int32)
                  or isinstance(arg, ctypes.c_int64)
                  or isinstance(arg, ctypes.c_float)
                  or isinstance(arg, ctypes.c_double)
                  or isinstance(arg, ctypes.c_uint8)
                  or isinstance(arg, ctypes.c_uint16)
                  or isinstance(arg, ctypes.c_uint32)
                  or isinstance(arg, ctypes.c_uint64)
                  or isinstance(arg, ctypes.c_bool)):
                调用算子时传入的参数.append(arg.value)
            else:
                调用算子时传入的参数.append(arg)
        workspace = np.zeros([1], dtype=np.uint64)
        调用算子时传入的参数.append(workspace.ctypes.data)
        调用算子时传入的参数.append(self.executor.ctypes.data)
        return 调用算子时传入的参数, workspace

    def 根据输入构建GetWorkspaceSize参数类型(self):
        获取workspace函数的参数类型 = []
        for arg in self.参数保持不被销毁缓存:
            if (isinstance(arg, 张量)
                    or isinstance(arg, 张量列表)
                    or isinstance(arg, 标量)
                    or isinstance(arg, 标量数组)
                    or isinstance(arg, 数组)):
                获取workspace函数的参数类型.append(ctypes.c_void_p)
            elif isinstance(arg, bytes):
                获取workspace函数的参数类型.append(ctypes.c_char_p)
            elif isinstance(arg, ctypes.c_int8):
                获取workspace函数的参数类型.append(ctypes.c_int8)
            elif isinstance(arg, ctypes.c_int16):
                获取workspace函数的参数类型.append(ctypes.c_int16)
            elif isinstance(arg, ctypes.c_int32):
                获取workspace函数的参数类型.append(ctypes.c_int32)
            elif isinstance(arg, ctypes.c_int64):
                获取workspace函数的参数类型.append(ctypes.c_int64)
            elif isinstance(arg, ctypes.c_uint8):
                获取workspace函数的参数类型.append(ctypes.c_uint8)
            elif isinstance(arg, ctypes.c_uint16):
                获取workspace函数的参数类型.append(ctypes.c_uint16)
            elif isinstance(arg, ctypes.c_uint32):
                获取workspace函数的参数类型.append(ctypes.c_uint32)
            elif isinstance(arg, ctypes.c_uint64):
                获取workspace函数的参数类型.append(ctypes.c_uint64)
            elif isinstance(arg, ctypes.c_float):
                获取workspace函数的参数类型.append(ctypes.c_float)
            elif isinstance(arg, ctypes.c_double):
                获取workspace函数的参数类型.append(ctypes.c_double)
            elif isinstance(arg, ctypes.c_bool):
                获取workspace函数的参数类型.append(ctypes.c_bool)
        获取workspace函数的参数类型.append(ctypes.c_void_p)
        获取workspace函数的参数类型.append(ctypes.c_void_p)
        self.获取workspace大小函数.argtypes = 获取workspace函数的参数类型

    def 设置GetWorkspaceSize参数类型(self, 类型列表: list):
        self.获取workspace大小函数.argtypes = 类型列表

    def __call__(self, *args, 自动推导GetWorkspaceSize函数参数类型=True):
        self.根据输入将ndarray创建为张量并缓存参数(*args)
        调用算子时传入的参数, workspace = self.GetWorkspaceSize函数的参数()
        if 自动推导GetWorkspaceSize函数参数类型:
            self.根据输入构建GetWorkspaceSize参数类型()
        ret = self.获取workspace大小函数(*调用算子时传入的参数)
        记录acl返回值错误日志并抛出异常('获取workspace大小函数', ret)
        workspace指针 = 0
        workspace容量 = int(workspace[0])
        if workspace容量 > 0:
            self.workspace内存 = 设备内存(workspace容量)
            workspace指针 = self.workspace内存.指针
        self.算子执行函数(workspace指针, workspace容量, int(self.executor[0]), 0)
        记录acl返回值错误日志并抛出异常('算子执行函数', ret)
        return self.参数保持不被销毁缓存

    def 为生成代码提供的调用函数(self, *args):
        self.参数保持不被销毁缓存 = list(args)
        调用算子时传入的参数, workspace = self.GetWorkspaceSize函数的参数()
        ret = self.获取workspace大小函数(*调用算子时传入的参数)
        记录acl返回值错误日志并抛出异常('获取workspace大小函数', ret)
        workspace指针 = 0
        workspace容量 = int(workspace[0])
        if workspace容量 > 0:
            self.workspace内存 = 设备内存(workspace容量)
            workspace指针 = self.workspace内存.指针
        self.算子执行函数(workspace指针, workspace容量, int(self.executor[0]), 0)
        记录acl返回值错误日志并抛出异常('算子执行函数', ret)
        return self.参数保持不被销毁缓存
