import gevent

from ats_base.common import func
from ats_base.log.logger import logger
from ats_base.service import udm

from ats_case.case import base, asb
from ats_case.case.context import Context
from ats_case.common.enum import *


class Bench(object):
    def __init__(self):
        self._operation = None
        self._parameter = None
        self._is_meter_pos_operation = False  # 针对台体的单个表位, 不是针对整个台体的操作
        self._interval = None
        self._secs = 0
        self._result = None
        self._exec_times = 0
        self._func = None
        self._expect_result = None
        self._func_parameter = {}
        self._not_pass = None
        self._break_case = 0
        self._repeat_times = 0
        self._repeat_sleep = 0

    def operation(self, command: str):
        self._operation = command
        if self._operation.find('read') >= 0:
            self._is_meter_pos_operation = True
        return self

    def parameter(self, param=None):
        self._parameter = param
        if type(self._parameter) is dict:
            if self._parameter.get('meter_pos') is not None:
                self._is_meter_pos_operation = True
        return self

    def interval(self, times):
        self._interval = times
        return self

    def secs(self, s=0):
        self._secs = s
        return self

    def compare(self, data):
        self._func = data.get('code')
        self._expect_result = data.get('expect_result', None)
        self._func_parameter = data.get('parameter', {})
        self._not_pass = data.get('not_pass', None)

        if isinstance(self._not_pass, dict) and len(self._not_pass) > 0:
            self._break_case = self._not_pass.get('break_case', 0)
            self._repeat_times = self._not_pass.get('repeat_times', 0)
            self._repeat_sleep = self._not_pass.get('sleep', 0)

        return self

    def encode(self, context: Context):
        logger.info(
            '~ @BENCH-> manufacture:{} operation:{} parameter:{}'.format(context.bench.manufacture, self._operation,
                                                                         self._parameter))

        if type(self._parameter) is dict:
            self._parameter = base.transform(context, self._parameter)

    def decode(self, context: Context):
        logger.info('~ @BENCH<- manufacture:{} operation:{} result:{}'.format(context.bench.manufacture,
                                                                              self._operation, self._result))
        self._flush(context)

    def acv(self, context: Context):
        result = str(self._result)
        data = func.to_dict(result=self._result)
        if self._func is not None:
            data['parameter'] = base.transform(context, self._func_parameter)
            try:
                if self._expect_result is None:
                    data['expect_result'] = context.runtime.sos[context.runtime.step - 1]
                else:
                    data['expect_result'] = context.runtime.sos[int(self._expect_result)]
            except:
                pass

            logger.info('~ @ACD-> module:{} function:{} parameter:{}'.format('bench', self._func, data['parameter']))
            result = udm.handle(module='bench', function=self._func, data=data,
                                debug_url=context.debug_service_url.get('acd'))
            logger.info('~ @ACD<- module:{} function:{} result:{}'.format('bench', self._func, result))

            context.runtime.sas[context.runtime.step] = result

        return result

    def _flush(self, context: Context):
        context.runtime.sos.update({context.runtime.step: func.to_dict(obj='bench', op=self._operation
                                                                       , parameter=self._parameter,
                                                                       result=self._result)})

    def sleep(self, context: Context):
        self._secs = base.transform(context, self._secs)
        if isinstance(self._secs, int) and self._secs > 0:
            base.send(context, todo={'app:show': {'msg': base.BENCH_SLEEP_MESSAGE.format(self._secs)}})
            base.sleep(self._secs)

    def _times(self, context: Context):
        self._interval = base.transform(context, self._interval)
        if self._interval > 0:
            if context.runtime.loop_index == 0 or (context.runtime.loop_index + 1) % self._interval != 0:
                return False

            self._exec_times += 1
        return True

    def exec(self, context: Context):
        if context.meter.index == 0 or self._is_meter_pos_operation:
            if self._times(context):
                if not self._exec_main(context):
                    self._fail_repeat(context)

                if self._is_meter_pos_operation:
                    pass_quantity = asb.Application.get(context.test_sn, 'pass_quantity')
                    if pass_quantity == 'NULL':
                        pass_quantity = 0
                    pass_quantity = int(pass_quantity) + 1
                    asb.Application.set(context.test_sn, 'pass_quantity', pass_quantity)

                    if pass_quantity >= int(asb.Application.get(context.test_sn, "meter:quantity")):
                        asb.Application.set(context.test_sn, 'pass_quantity', 0)
                        self.sleep(context)
                else:
                    self.sleep(context)

    def _exec_main(self, context: Context):
        self.encode(context)
        try:
            self._result = base.send(context, todo={'bench:{}'.format(self._operation): self._parameter})
            self._result = self._result.get('result')
        except:
            self._result = ''
        self.decode(context)

        self._result = self.acv(context)
        base.send(context, todo={'app:show': {'msg': self._result}})

        return base.result_judge(self._result)

    def _fail_repeat(self, context: Context):
        if isinstance(self._repeat_times, int) and self._repeat_times > 0:
            is_finished = False     # 单只表比对结果是否合格
            asb.Application.set(context.test_sn, 'finished_quantity', 0)

            for r in range(self._repeat_times):
                if context.mode == WorkMode.FORMAL:  # 项目测试 - 协程切换
                    gevent.sleep(0.05)

                # 多表测试时, 多表比对结果合格数量
                finished_quantity = int(asb.Application.get(context.test_sn, 'finished_quantity'))
                # 多表测试时, 多表比对结果执行一轮不合格数量
                one_loop_finished_quantity = asb.Application.get(context.test_sn, 'one_loop_finished_quantity')
                if one_loop_finished_quantity == 'NULL':
                    one_loop_finished_quantity = 0
                else:
                    one_loop_finished_quantity = int(one_loop_finished_quantity)

                if not is_finished:
                    if self._exec_main(context):
                        is_finished = True
                        finished_quantity += 1
                        asb.Application.set(context.test_sn, 'finished_quantity', finished_quantity)
                    else:
                        one_loop_finished_quantity += 1
                        asb.Application.set(context.test_sn, 'one_loop_finished_quantity', one_loop_finished_quantity)

                # 多表测试时, 判断是否是最后一只表, 是否睡眠
                quantity = int(asb.Application.get(context.test_sn, "meter:quantity"))
                if one_loop_finished_quantity >= quantity - finished_quantity:
                    # 一轮循环最后一只表
                    asb.Application.set(context.test_sn, 'one_loop_finished_quantity', 0)
                    if finished_quantity < quantity:
                        # 最后一轮最后一只表不睡眠, 其他轮次最后一只表都睡眠
                        if isinstance(self._repeat_sleep, int) and self._repeat_sleep > 0:
                            base.sleep(self._repeat_sleep)
                        else:
                            base.sleep(context.runtime.bench_result_valid_fail_delay)

                if is_finished:
                    if finished_quantity >= quantity:
                        # 全部合格完成
                        break

            if self._break_case == 1 and not is_finished:
                raise AssertionError(str(self._result))
