
import acl
import numpy as np
import colorama
import re


def 驼峰转下划线(驼峰命名: str):
    return re.sub(r'(?!^)([A-Z]+)', r'_\1', 驼峰命名).lower()


def 下划线转驼峰(下划线命名: str):
    return ''.join([部分字符串.capitalize() for 部分字符串 in 下划线命名.split('_')])


def get_loss_by_type(dtype):
    loss = 0
    if dtype == np.float16:
        loss = 1 / 1000
    elif dtype == np.float32:
        loss = 1 / 10000
    return loss


def _compare(v1: np.ndarray, v2: np.ndarray):
    loss = get_loss_by_type(v1.dtype)
    return np.abs(v1 - v2) <= loss


def compare(v1: np.ndarray, v2: np.ndarray):
    return _compare(v1, v2).all()


def right_rate(v1: np.ndarray, v2: np.ndarray):
    ret = _compare(v1, v2)
    return ret.astype(np.int32).sum() / v1.size

# 参考自：https://gitee.com/ascend/samples/blob/master/operator/AddCustomSample/KernelLaunch/AddKernelInvocationNeo/scripts/verify_result.py


def verify_result(real_result, golden):
    loss = get_loss_by_type(real_result.dtype)
    minimum = 10e-10
    result = np.abs(real_result - golden)  # 计算运算结果和预期结果偏差
    deno = np.maximum(np.abs(real_result), np.abs(golden))  # 获取最大值并组成新数组
    result_atol = np.less_equal(result, loss)  # 计算绝对误差
    result_rtol = np.less_equal(result / np.add(deno, minimum), loss)  # 计算相对误差
    if not result_rtol.all() and not result_atol.all():
        if (
            np.sum(result_rtol == False) > real_result.size * loss
            and np.sum(result_atol == False) > real_result.size * loss
        ):  # 误差超出预期时返回打印错误，返回对比失败
            print(
                colorama.Fore.RED, real_result.dtype, "[ERROR] result error", flush=True
            )
            print(colorama.Style.RESET_ALL, flush=True)
            return False
    print(colorama.Fore.GREEN, real_result.dtype, "test pass", flush=True)
    print(colorama.Style.RESET_ALL, flush=True)
    return True


class AclRunMode:
    ACL_DEVICE = 0
    ACL_HOST = 1
