import ctypes
import os

加载缓存 = {}


def 加载库(path: str):
    cache = 加载缓存.get(path)
    if cache is not None:
        return cache
    lib = ctypes.CDLL(path)
    加载缓存[path] = lib
    return lib


def 加载cann_toolkit_lib64中的库(libname):
    ascend_home_path = os.environ["ASCEND_HOME_PATH"]
    lib_path = f"{ascend_home_path}/lib64/{libname}"
    return 加载库(lib_path)
