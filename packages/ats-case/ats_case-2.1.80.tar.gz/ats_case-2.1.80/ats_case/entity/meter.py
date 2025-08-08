import re
import gevent

from ats_base.common import func
from ats_base.common.enum import ProClazz
from ats_base.log.logger import logger
from ats_base.service import pro, udm

from ats_case.case import base, asb
from ats_case.case.context import Context
from ats_case.common.enum import *
from ats_case.common.error import *
from ats_case.security import link


class Meter(object):
    def __init__(self, protocol):
        self._protocol = ProClazz(protocol)
        self._comm_addr = None
        self._operation = None
        self._element = None
        self._parameter = None
        self._addition = None
        self._security = None
        self._report = None
        self._is_report = False
        self._report_sleep = 0
        self._secs = 0
        self._chip_id = None
        self._frame = None
        self._parse = None
        self._func_module = None
        self._func = None
        self._expect_result = None
        self._func_parameter = {}
        self._not_pass = None
        self._break_case = 0
        self._repeat_times = 0
        self._repeat_sleep = 0

        self._customframe = None

    def comm_addr(self, addr: str):
        self._comm_addr = addr
        return self

    def operation(self, op: str):
        self._operation = op
        return self

    def element(self, di):
        self._element = di
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def addition(self, addi=None):
        self._addition = addi
        return self

    def security(self, se=None):
        self._security = se
        return self

    def report(self, rp=None):
        self._report = rp
        if isinstance(self._report, dict) and len(self._report) > 0:
            self._is_report = True
            try:
                self._report_sleep = int(self._report.get('sleep', 0))
            except:
                pass
        return self

    def secs(self, s=0):
        self._secs = s
        return self

    def chip_id(self, ci):
        self._chip_id = ci
        return self

    def compare(self, data):
        self._func_module = data.get('module')
        self._func = data.get('code')
        self._expect_result = data.get('expect_result', None)
        self._func_parameter = data.get('parameter', {})
        self._not_pass = data.get('not_pass', None)

        if isinstance(self._not_pass, dict) and len(self._not_pass) > 0:
            self._break_case = self._not_pass.get('break_case', 0)
            self._repeat_times = self._not_pass.get('repeat_times', 0)
            self._repeat_sleep = self._not_pass.get('sleep', 0)

        return self

    def frame(self, hexStr: str):
        self._frame = hexStr
        return self

    def customframe(self, hexStr: str):
        self._customframe = hexStr
        return self

    def encode(self, context: Context):
        if self._customframe is not None and len(self._customframe) > 0:
            logger.info('~ @PRO-USER_DEFINED_FRAME<- security:{} customframe:{}'.format(self._protocol, self._customframe))
            self._frame = base.transform(context, self._customframe)
        else:
            logger.info(
                '~ @PRO-ENCODE-> security:{} comm_addr:{} operation:{} element:{}'.format(self._protocol,
                                                                                          self._comm_addr,
                                                                                          self._operation,
                                                                                          self._element))

            self._element = base.transform(context, self._element)
            self._parameter = base.transform(context, self._parameter)
            self._addition = base.transform(context, self._addition)

            parse = pro.encode(func.to_dict(protocol=self._protocol.name, comm_addr=self._comm_addr,
                                            operation=self._operation, element=self._element,
                                            chip_id=self._chip_id, parameter=self._parameter,
                                            addition=self._addition, security=self._security,
                                            session_key=context.test_sn))
            # 1. 是否需要安全认证
            if parse.get('need_sa') == 1:
                raise MeterNeedSecurityAuthentication(context.meter.pos)

            logger.info('~ @PRO-ENCODE<- security:{} frame:{}'.format(self._protocol, parse.get('frame')))

            self._frame = parse.get('frame')
        return self._frame

    def decode(self, context: Context, index=0):
        # 1. 异常判断 - 无响应帧
        if self._frame is None or len(self._frame) <= 0:
            self._parse = base.METER_NO_RESPONSE_FRAME
            self._flush(context)
            raise MeterResponseFrameNoneError('表位:{}'.format(context.meter.pos))
            # return self._parse

        logger.info('~ @PRO-DECODE-> security:{} frame:{}'.format(self._protocol, self._frame))
        try:
            data = pro.decode(
                func.to_dict(protocol=self._protocol.name, frame=self._frame, session_key=context.test_sn))
        except:
            # 2. 异常判断 - 响应帧解析错误
            self._parse = base.METER_ERROR_DECODE
            self._flush(context)
            raise MeterResponseFrameParseError('表位:{}'.format(context.meter.pos))
            # return self._parse
        logger.info('~ @PRO-DECODE<- security:{} parse:{}'.format(self._protocol, data))

        # 3. 是否需要安全认证
        if data.get('need_sa') == 1:
            raise MeterNeedSecurityAuthentication(context.meter.pos)

        # 4. 异常判断 - 操作电表失败
        if data.get('error') == 1:
            self._parse = data.get('result', base.METER_ERROR_OPERATION)
            self._flush(context)
            return self._parse
            # raise MeterOperationError(data.get('result'))

        # 5. 分帧处理开始
        next_frame = data.get('next_frame', None)
        if next_frame is not None:
            self._frame = base.write(context, next_frame)
            self.decode(context, index + 1)
        else:
            context.runtime.final_result = data.get('result')
        # 5. 分帧处理结束

        if index == 0:
            self._parse = context.runtime.final_result
            self._flush(context)
            return self._parse

    def _flush(self, context: Context):
        context.runtime.sos.update({context.runtime.step: func.to_dict(obj='meter', op=self._operation
                                                                       , element=self._element
                                                                       , parameter=self._parameter,
                                                                       result=self._parse)})

    def sleep(self, context: Context):
        self._secs = base.transform(context, self._secs)
        if isinstance(self._secs, int) and self._secs > 0:
            base.send(context, todo={'app:show': {'msg': base.METER_SLEEP_MESSAGE.format(self._secs)}})
            base.sleep(self._secs)

    def acv(self, context: Context):
        result = str(self._parse)
        if self._func is not None:
            if type(self._func_parameter) is dict:
                self._func_parameter['mode'] = context.mode.name
                self._func_parameter = base.transform(context, self._func_parameter)
            else:
                self._func_parameter = {}

            self._expect_result_handle(context)

            self._func_parameter['protocol'] = self._protocol.name
            data = func.to_dict(result=self._parse, expect_result=self._expect_result,
                                parameter=self._func_parameter)

            logger.info('~ @ACD-> module:{} function:{} parameter:{}'.format(
                self._func_module, self._func, self._func_parameter))
            result = udm.handle(module='device.{}'.format(self._func_module), function=self._func, data=data,
                                debug_url=context.debug_service_url.get('acd'))
            logger.info('~ @ACD<- module:{} function:{} result:{}'.format(self._func_module, self._func, result))

            context.runtime.sas[context.runtime.step] = result

        return result

    def _expect_result_handle(self, context: Context):
        try:
            if self._expect_result is None or len(str(self._expect_result).strip()) <= 0:
                self._expect_result = context.runtime.sos[context.runtime.step - 1]
            if isinstance(self._expect_result, int):
                self._expect_result = context.runtime.sos[self._expect_result]
            if isinstance(self._expect_result, str):
                rs = re.findall(r"(\d+)", self._expect_result)
                if len(rs) == 1:
                    self._expect_result = context.runtime.sos[int(rs[0])]
                else:
                    self._expect_result = []
                    for r in rs:
                        self._expect_result.append(context.runtime.sos[int(r)])
        except:
            pass

    def exec(self, context: Context):
        if self._is_report:
            self._exec_report(context)
        else:
            try:
                self._exec_main(context)
            except MeterNeedSecurityAuthentication as ms:
                try:
                    link.establish(context, self._protocol.name.lower())
                except MeterSecurityAuthenticationError as ma:
                    raise ma

                self._exec_main(context)

        self._fail_repeat(context)
        self.sleep(context)

    def _exec_report(self, context: Context):
        base.sleep(self._report_sleep)
        try:
            self._frame = base.report(context)
        except:
            self._frame = None

        self.decode(context)
        self._result = self.acv(context)
        base.send(context, todo={'app:show': {'msg': self._result}})

    def _exec_main(self, context: Context, retry_times=3):
        self.encode(context)
        try:
            self._frame = base.write(context, self._frame)
        except:
            self._frame = None

        try:
            self.decode(context)

            self._result = self.acv(context)
            base.send(context, todo={'app:show': {'msg': self._result}})
        except MeterResponseFrameNoneError as ne:
            self._redo(context, ne, retry_times)
        except MeterResponseFrameParseError as pe:
            self._redo(context, pe, retry_times)

    def _redo(self, context: Context, e, retry_times):
        retry_times -= 1
        if retry_times <= 0:
            self._result = self.acv(context)
            base.send(context, todo={'app:show': {'msg': self._result}})
        else:
            base.send(context, todo={'app:show': {'msg': str(e)}})
            base.sleep(2)
            self._exec_main(context, retry_times)

    def _fail_repeat(self, context: Context):
        if not base.result_judge(self._result):
            if isinstance(self._repeat_times, int) and self._repeat_times > 0:
                is_finished = False  # 单只表比对结果是否合格
                for r in range(self._repeat_times):
                    if context.mode == WorkMode.FORMAL:  # 项目测试 - 协程切换
                        gevent.sleep(0.05)

                    if self._is_report:
                        self._exec_report(context)
                    else:
                        self._exec_main(context)

                    if base.result_judge(self._result):
                        is_finished = True
                        break

                    if isinstance(self._repeat_sleep, int) and self._repeat_sleep > 0:
                        base.sleep(self._repeat_sleep)
                    else:
                        base.sleep(context.runtime.meter_result_valid_fail_delay)

                if self._break_case == 1 and not is_finished:
                    raise AssertionError(str(self._result))
