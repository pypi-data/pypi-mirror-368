import pickle
import sys
from datetime import datetime

import gevent
from importlib import import_module, reload

from ats_base.common import func
from ats_base.common.enum import Payload
from ats_base.log.logger import logger
from ats_base.service import msg

from ats_case.case import asb, base, translator, command
from ats_case.case.context import Context
from ats_case.common.enum import *
from ats_case.common.error import *
from ats_case.statement import logic


def execute(context: Context):
    if context.mode == WorkMode.FORMAL:
        FormalExecutor(context).exec()
    else:
        DebugExecutor(context).exec()


class Executor(object):
    def __init__(self, context: Context):
        self._context = context
        self._model = None
        self._steps = []

    def handle(self):
        """
        抽象方法 - 子类实现脚本脚本
        :return:
        """
        pass

    def exec(self):
        """
        执行用例所有步骤
        :return:
        """
        self.handle()

        index = self._load()  # 加载所需关键变量
        while index < len(self._steps):
            index = self.step_exec(index)

    def _load(self):
        """
        加载索引或断点索引
        :return:
        """
        # 断点信息
        if self._context.renew == 1:
            try:
                rt = pickle.loads(asb.BreakPoint.get(self._context, 'runtime'))
                if isinstance(rt, self._context.Runtime):
                    self._incr_loop_sn = rt.incr_loop_sn
                    self._context.runtime.step = rt.step

                    self._context.runtime.loop_sn = rt.loop_sn
                    self._context.runtime.loop_count = rt.loop_count
                    self._context.runtime.loop_index = rt.loop_index

                    self._context.runtime.currentLoop = rt.currentLoop
                    self._context.runtime.glo = rt.glo

                    self._context.runtime.sos = rt.sos
                    self._context.runtime.sas = rt.sas

                    self._context.runtime.meter_result_valid_fail_delay = rt.meter_result_valid_fail_delay
                    self._context.runtime.bench_result_valid_fail_delay = rt.bench_result_valid_fail_delay

                    self._context.runtime.final_result = rt.final_result

                    try:
                        return self._steps.index(self._context.runtime.step)
                    except:
                        pass
            except:
                pass

        return 0

    def _flush(self):
        """
        缓存断点数据
        :return:
        """
        try:
            asb.BreakPoint.set(self._context, 'runtime', pickle.dumps(self._context.runtime))
        except:
            pass

    @logic.monitoring_control
    def step_exec(self, index: int):
        """
        执行单个步骤
        :return:
        """
        if self._context.mode == WorkMode.FORMAL:  # 项目测试 - 协程切换
            gevent.sleep(0.05)

        logger.info('~ @TCC-STEP-> steps[#{}] execute'.format(self._context.runtime.step))

        self._flush()  # 缓存在断点续测时所需关键变量
        if self.is_exec():
            try:
                getattr(self._model, 'step_{}'.format(self._context.runtime.step))(self._context)
            except APIError as ae:
                logger.info(str(ae))
                self._err_msg_notify(str(ae))

                raise AssertionError(str(ae))
            except Exception as e:
                self._context.runtime.sas[self._context.runtime.step] = '{} - {} '.format(base.CODE_ERROR, str(e))
                if isinstance(e, BenchReadNoneError):
                    asb.Application.set(self._context.test_sn, "meter:quantity",
                                        int(asb.Application.get(self._context.test_sn, "meter:quantity")) - 1)
                command.client().message(str(e)).error(self._context)
                logger.error(str(e))
                self._err_msg_notify(str(e))

                raise AssertionError(str(e))

    def is_exec(self):
        """
        判断步骤是否执行
        :return:
        """
        if base.offbench(self._context, self._context.offbench):
            return False

        return True

    def _err_msg_notify(self, err: str):
        """
        异常消息通知
        :param err:
        :return:
        """
        msg.send('dingding', func.to_dict(payload=Payload.ERROR.value, workmode=self._context.mode.value,
                                          project=self._context.project, case_name=self._context.case.name,
                                          meter_pos=self._context.meter.pos, step=self._context.runtime.step,
                                          test_sn=self._context.test_sn,
                                          start_time=self._context.start_time.strftime('%Y.%m.%d %H:%M:%S'),
                                          end_time=datetime.now().strftime('%Y.%m.%d %H:%M:%S'),
                                          msg=err))


def extract_steps(content: list):
    n_s = []
    for s in content:
        if s.upper().find('STEP_') >= 0:
            num = func.extract_digit(s)
            n_s.append(int(num))

    return sorted(n_s)


def import_script(clazz: ScriptClazz, context: Context, manual_dir: str = 'debug'):
    # 分为两种情况: 0. 手动编写的脚本 1.自动转化的脚本
    if clazz == ScriptClazz.AUTO:
        steps = translator.translate(context)
        a_name = 'script.auto.{}.tsm_{}'.format(context.tester.username.lower(), context.meter.pos)
        try:
            model = sys.modules[a_name]
            model = reload(model)
        except:
            model = import_module(a_name)
    else:
        m_name = 'script.manual.{}.{}'.format(manual_dir, context.case.steps)
        try:
            model = sys.modules[m_name]
            model = reload(model)
        except:
            model = import_module(m_name)

        steps = extract_steps(dir(model))

    return model, steps


class FormalExecutor(Executor):
    def handle(self):
        self._model, self._steps = import_script(self._context.case.script, self._context, 'formal')


class DebugExecutor(Executor):
    def handle(self):
        self._model, self._steps = import_script(self._context.case.script, self._context)
