import time

from ats_base.common import func
from ats_base.log.logger import logger
from ats_base.service import app, db

from ats_case.case import asb, atm
from ats_case.case.context import Context
from ats_case.common.enum import *
from ats_case.common.error import *

METER_NO_RESPONSE_FRAME = '无响应帧'
METER_ERROR_DECODE = '响应帧解析错误'
METER_ERROR_OPERATION = '操作电表失败'


METER_SLEEP_MESSAGE = '系统休眠{}秒, 等待电表操作完毕...'
BENCH_SLEEP_MESSAGE = '系统休眠{}秒, 等待表台调整完毕...'
JUMP_MESSAGE = '####步骤跳转[第{}次/共{}次] - 跳转到此用例第{}步, 重新开始执行.'
JUMP_END = '####步骤跳转[第{}次/共{}次] - 跳转结束.'

CODE_ERROR = '服务内部代码发生异常'
FRAME_ERROR = '返回帧有问题, 重新执行此操作'

"""
    基础操作
"""


def send(context: Context, todo: dict, types=2, end=0, retry_times: int = 3):
    """
    发送操作命令 - 向测试端app
    :param context:         上下文
    :param todo:            任务
    :param types:
    :param end:
    :param retry_times:     失败重试次数（默认：3次）
    :return:
    """
    result = None

    try:
        data = {
            'type': types,
            'end': end,
            'exec_time': func.sys_current_time(),
            'test_sn': context.test_sn,
            'case_id': context.case.id,
            'meter_pos': context.meter.pos,
            'step_id': context.runtime.step,
            'todo': todo
        }

        logger.info('~ @TCC-SEND-> client:{} data:{}'.format(context.tester.api, data))
        result = app.send(context.tester.api, data)
        logger.info('~ @TCC-SEND<- result:{}'.format(result))
    # except requests.exceptions.MissingSchema as me:
    #     logger.error(str(me))
    #     raise AssertionError(str(me))
    except Exception as ae:
        logger.error(str(ae))

        retry_times -= 1
        if retry_times <= 0:
            raise APIError(context.tester.api)
        else:
            sleep(5)
            send(context, todo, types, retry_times=retry_times)

    return result


def sleep(seconds: float):
    """
    休眠
    :param seconds:     秒
    :return:
    """
    logger.info('~ @TCC-SLEEP-> {}secs'.format(seconds))
    time.sleep(seconds)


"""
    公共函数
"""


def offbench(context: Context, disabled=1):
    """
    脱表台
    :param context:
    :param disabled:     使能
    :return:
    """
    clazz = OperationClazz(context.case.steps[str(context.runtime.step)].get('type'))

    if disabled == 1:
        if clazz == OperationClazz.BENCH:
            return True

    return False


def transform(context: Context, data):
    """
    转换变量数据
    :param context:
    :param data:
    :return:
    """
    if data is None:
        return None
    if isinstance(data, int) or isinstance(data, float):
        return data
    if isinstance(data, str):
        if '#' not in data and '~' not in data:
            return data
        sd = data
    else:
        sd = str(data)
        if '#' not in sd and '~' not in sd:
            return data

    sd = asb.V_loop(context, sd)

    return eval(sd)


def result_judge(result):
    """
    结果判断
    :param result:
    :return:
    """
    if str(result).find('不合格') >= 0:
        if str(result).find('读取不到误差数据') >= 0:
            raise BenchReadNoneError(str(result))
        return False

    return True


# def re_do(context: Context, result, repeat_times, break_case):
#     """
#     结果判断不合格, 重新执行
#     :param context:
#     :param result:
#     :param repeat_times:
#     :param break_case:
#     :return:
#     """
#     send(context, todo={'app:show': {'msg': result}})
#
#     if not result_judge(result):
#         if repeat_times > 0:
#             repeat_times -= 1
#             if repeat_times >= 0:
#                 sleep(1)
#                 return False
#
#         if break_case == 1:
#             raise AssertionError(str(result))
#     else:
#         return True


def end_step(context: Context, types):
    """
    所有用例的最后步骤处理
    :param context:
    :param types:
    :return:
    """
    if types == 1:
        if context.mode == WorkMode.FORMAL:
            if context.case.end == 1 and context.meter.end == 1:
                asb.flush(context.test_sn)
                sn = context.test_sn.split(':')[0]
                db.update('test:log', condition=func.to_dict(sn=sn), end_time=func.sys_current_time())
                return 1
        else:  # Debug模式
            asb.flush(context.test_sn)
            return 1
    return 0


"""
    测试报告
"""


def build_in_result(operation, parameter, result, tag, err: str = None):
    """
    格式化内置函数结论
    :param operation:
    :param parameter:
    :param result:
    :param tag:
    :param err:
    :return:
    """
    msg = []

    if tag == 1:
        msg.append('结论: {}.'.format('合格'))
    else:
        msg.append('结论: {}.'.format(CODE_ERROR))

    msg.append('\r\n--------------------详细---------------------')

    if operation is not None:
        msg.append('\r\n内置方法: {}'.format(operation))
    if parameter is not None:
        msg.append('\r\n方法参数: {}'.format(parameter))
    if err is not None:
        msg.append('\r\n返回异常: {}'.format(err))
    else:
        if result is not None:
            msg.append('\r\n返回结果: {}'.format(result))

    return ''.join(msg) + '\r\n'


def jump_result(jump_times, times, step):
    """
    格式化跳转结论
    :param jump_times:
    :param times:
    :param step:
    :return:
    """
    msg = list()
    msg.append('结论: {}.'.format('合格'))
    msg.append('\r\n--------------------详细---------------------')
    if jump_times >= times:
        msg.append('\r\n' + JUMP_END.format(jump_times, times))
    else:
        msg.append('\r\n' + JUMP_MESSAGE.format(jump_times, times, step))

    return ''.join(msg) + '\r\n'


def test_report(context: Context):
    """
    格式化用例结论
    :param context:
    :return:
    """
    sc = fc = 0
    fs = []
    error = None
    for s, result in context.runtime.sas.items():
        if str(result).find(CODE_ERROR) >= 0:
            error = result
            break

        if str(result).find('不合格') >= 0:
            fc += 1
            fs.append(str(s))
        else:
            sc += 1

    pattern = "{0:<11}\t{1:<6}\r\n"
    if error is not None:
        msg = pattern.format('系统错误:', '用例执行第{}步时, {}'.format(context.runtime.step, error))
    else:
        msg = pattern.format('用例步骤:', '{}步'.format(len(context.case.steps)))
        msg += pattern.format('执行合格:', '{}步'.format(sc))
        msg += pattern.format('执行不合格:', '{}步 ~ {}'.format(fc, ','.join(fs)))

    return msg


"""
    协议帧
"""


def write(context: Context, frame):
    ch = context.case.steps[str(context.runtime.step)].get('channel')
    ch = transform(context, ch)

    if ch.get('changed') is None:
        ch['changed'] = 0

    result = send(context, todo={'meter:comm': {'channel': ch, 'frame': frame}})

    return result.get('result')


def report(context: Context):
    ch = context.case.steps[str(context.runtime.step)].get('channel')
    ch = transform(context, ch)

    if ch.get('changed') is None:
        ch['changed'] = 0

    result = send(context, todo={'meter:report': {'channel': ch}})

    return result.get('result')


