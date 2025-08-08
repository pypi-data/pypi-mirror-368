from ats_base.log.logger import logger

from ats_base.service import build_in
from ats_case.case import base, asb
from ats_case.case.context import Context


class ATS(object):
    def __init__(self):
        self._name = 'ats'
        self._operation = None
        self._parameter = None
        self._glo = None
        self._stx = None
        self._ptx = None
        self._jp = None
        self._secs = 0
        self._result = None

    def operation(self, command: str):
        self._operation = command
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def glo(self, g=None):
        self._glo = g
        return self

    def stx(self, c=None):
        self._stx = c
        return self

    def ptx(self, c=None):
        self._ptx = c
        return self

    def jp(self, j=None):
        self._jp = j
        return self

    def secs(self, s=0):
        self._secs = s
        return self

    def build_in(self, context: Context):
        if isinstance(self._operation, str) and len(self._operation) > 0:
            self._parameter = base.transform(context, self._parameter)
            logger.info('~ @ATS:BUILD-IN-> operation:{} parameter:{}'.format(self._operation, self._parameter))
            try:
                self._result = build_in.handle(function=self._operation, data=self._parameter,
                                               debug_url=context.debug_service_url.get('build_in'))
                result = base.build_in_result(self._operation, self._parameter, self._result, 1)
                base.send(context, todo={'app:show': {'msg': result}})
            except Exception as e:
                result = base.build_in_result(self._operation, self._parameter, self._result, 2, str(e))
                base.send(context, todo={'app:show': {'msg': result}})

            context.runtime.sas[context.runtime.step] = result

    def flush(self, context: Context):
        if isinstance(self._glo, dict) and len(self._glo) > 0:
            logger.info('~ @ATS:GLOBAL-> global:{} result:{}'.format(self._glo, self._result))
            for result, name in self._glo.items():
                context.runtime.glo[name] = self._result[result]

    def set(self, context: Context):
        if isinstance(self._stx, dict) and len(self._stx) > 0:
            logger.info('~ @ATS:SET-> context:{} result:{}'.format(self._stx, self._result))
            for result, sx in self._stx.items():
                exec('{} = {}'.format(sx, self._result[result]))

    def put(self, context: Context):
        if isinstance(self._ptx, dict) and len(self._ptx) > 0:
            logger.info('~ @ATS:PUT-> context:{} result:{}'.format(self._ptx, self._result))
            for px, result in self._ptx.items():
                exec('{} = {}'.format(px, result))

    def jump(self, context: Context):
        if isinstance(self._jp, dict) and len(self._jp) > 0:
            step = self._jp.get('step')
            times = self._jp.get('times')

            times = base.transform(context, times)

            logger.info('~ @ATS:JUMP-> context:{} step:{} times:{}'.format(self._stx, step, times))

            context.runtime.jump_times += 1

            result = base.jump_result(context.runtime.jump_times, times, step)
            base.send(context, todo={'app:show': {'msg': result}})
            context.runtime.sas[context.runtime.step] = result

            if context.runtime.jump_times >= times:
                context.runtime.step_jump = False
                context.runtime.jump_times = 0
            else:
                context.runtime.step_jump = True
                context.runtime.step = step
                context.runtime.loop_sn = self._loop_sn(context, step)
                context.runtime.loop_index = 0

    def _loop_sn(self, context: Context, step: int):
        loops = context.case.control.get('loops')
        if loops is None or type(loops) is not list or len(loops) <= 0:
            return 0

        index = 0
        for loop in loops:
            ranges = loop.get('range')
            s = ranges.split(':')
            start_step = int(s[0])
            if step <= start_step:
                break
            index += 1

        return index

    def sleep(self, context: Context):
        self._secs = base.transform(context, self._secs)
        if isinstance(self._secs, int) and self._secs > 0:
            base.send(context, todo={'app:show': {'msg': base.ATS_SLEEP_MESSAGE.format(self._secs)}})
            base.sleep(self._secs)

    def exec(self, context: Context):
        self.build_in(context)
        self.flush(context)
        self.set(context)
        self.jump(context)
        self.sleep(context)
