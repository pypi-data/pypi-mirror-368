import acl
import colorama
import time


class 日志等级:
    调试 = 0
    提示 = 1
    警告 = 2
    错误 = 3


终端显示的日志等级 = 日志等级.调试


def 设置终端日志等级(等级: int):
    global 终端显示的日志等级
    终端显示的日志等级 = 等级


def _拼接消息(*args):
    message = ''
    for arg in args:
        message += str(arg) + ' '
    return message


def 记录调试日志(*args):
    msg = _拼接消息(*args)
    acl.app_log(日志等级.调试, msg)
    if 终端显示的日志等级 > 日志等级.调试:
        return
    msg = f'{colorama.Fore.BLUE}[{time.ctime()}][调试]{msg}{colorama.Style.RESET_ALL}'
    print(msg, flush=True)


def 记录提示信息日志(*args):
    msg = _拼接消息(*args)
    acl.app_log(日志等级.提示, msg)
    if 终端显示的日志等级 > 日志等级.提示:
        return
    print(f'[{time.ctime()}][提示]{msg}', flush=True)


def 记录警告日志(*args):
    msg = _拼接消息(*args)
    acl.app_log(日志等级.警告, msg)
    if 终端显示的日志等级 > 日志等级.警告:
        return
    msg = f'{colorama.Fore.CYAN}[{time.ctime()}][警告]{msg}{colorama.Style.RESET_ALL}'
    print(msg, flush=True)


def 记录错误日志(*args):
    msg = _拼接消息(*args)
    acl.app_log(日志等级.错误, msg)
    if 终端显示的日志等级 > 日志等级.错误:
        return
    msg = f'{colorama.Fore.LIGHTRED_EX}[{time.ctime()}][错误]{msg}{colorama.Style.RESET_ALL}'
    print(msg, flush=True)


def 记录错误日志并抛出异常(*args):
    msg = _拼接消息(*args)
    acl.app_log(日志等级.错误, msg)
    if 终端显示的日志等级 > 日志等级.错误:
        return
    msg = f'{colorama.Fore.LIGHTRED_EX}[{time.ctime()}][错误]{msg}{colorama.Style.RESET_ALL}'
    raise Exception(msg)


def 记录acl返回值错误日志(msg, ret):
    if ret == 0:
        return
    err_msg = acl.get_recent_err_msg()
    记录错误日志(msg, err_msg, ret)


def 记录acl返回值错误日志并抛出异常(msg, ret):
    记录acl返回值错误日志(msg, ret)
    if ret != 0:
        raise Exception(msg)


def 记录acl错误日志(msg):
    err_msg = acl.get_recent_err_msg()
    记录错误日志(msg, err_msg)


def 记录acl错误日志并抛出异常(msg):
    err_msg = acl.get_recent_err_msg()
    记录错误日志并抛出异常(msg, err_msg)


def 记录acl空指针日志并抛出异常(指针, 信息):
    if 指针 != 0:
        return
    记录acl错误日志并抛出异常(信息)


if __name__ == '__main__':
    acl.init()
    记录调试日志("测试debug")
    记录提示信息日志("测试info")
    记录警告日志("测试warning")
    记录错误日志("测试error")
    acl.finalize()
