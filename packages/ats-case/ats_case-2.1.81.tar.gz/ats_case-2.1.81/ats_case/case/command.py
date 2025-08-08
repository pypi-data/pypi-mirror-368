from ats_case.case import base

from ats_case.entity.ats import ATS
from ats_case.entity.bench import Bench
from ats_case.entity.client import App
from ats_case.entity.encrypt import Encryptor
from ats_case.entity.meter import Meter

"""
    注释篇
"""


def step_annotation(**param):
    """
    测试步骤方法注释 - 装饰器
    :param param: desc-测试步骤描述
    :return:
    """
    desc = param.get('desc')

    def decorate(callback):
        def fn(*args, **kwargs):
            base.send(args[0], todo={'app:show': {'msg': desc}})
            r = callback(*args, **kwargs)
            return r

        return fn

    return decorate


"""
    通讯协议篇
"""


def meter(protocol: str):
    return Meter(protocol)


"""
    加密机篇
"""


def encrypt(protocol: str):
    return Encryptor(protocol)


"""
    表台篇
"""


def bench():
    return Bench()


"""
    测试终端篇
"""


def client():
    return App()


"""
    平台篇
"""


def ats():
    return ATS()
