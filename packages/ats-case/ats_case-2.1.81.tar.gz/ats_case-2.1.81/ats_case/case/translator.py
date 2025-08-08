import os

from pathlib import Path

from ats_base.common import func
from ats_case.case.context import Context
from ats_case.common.enum import OperationClazz


def translate(context: Context):
    return Translator(context).write()


class Translator(object):
    def __init__(self, context: Context):
        self.KEYWORD = ["if", "for", "while"]
        self.TAB = "   "
        self.LINE = "\n"
        self._context = context

    def write(self):
        steps = []

        with open(self._script(), "w", encoding='utf-8') as f:
            f.write(self._gen_import())
            f.write(self._gen_line(2))

            for step, operations in self._context.case.steps.items():
                steps.append(int(step))
                f.write(self._gen_step(int(step), operations))

                tab_count = 1
                # for op in operations:
                f.write(self._gen_tab(tab_count) + self._gen_operation(operations) + self._gen_line(1))
                # if self._contain_keyword(step):
                #     tab_count += 1
                f.write(self._gen_line(2))

            return steps

    def _script(self):
        user_dir = func.makeDir(func.project_dir(), 'script', 'auto', self._context.tester.username)
        script_file = os.path.join(user_dir, 'tsm_{}.py'.format(self._context.meter.pos))

        if not os.path.exists(user_dir):
            Path(user_dir).mkdir(parents=True, exist_ok=True)

        return script_file

    def _gen_import(self):
        return 'from ats_case.case import command' + self.LINE + 'from ats_case.case.context import Context' + self.LINE

    def _gen_step(self, step: int, op: dict):
        return '@command.step_annotation(desc="{}"){}'.format(op.get('desc', ''), self.LINE) + \
               'def step_{}(context: Context):{}'.format(step, self.LINE)

    def _gen_tab(self, count: int):
        ts = ''
        for i in range(count):
            ts += self.TAB

        return ts

    def _gen_line(self, count: int):
        ls = ''
        for i in range(count):
            ls += self.LINE

        return ls

    def _contain_keyword(self, step: str):
        for k in self.KEYWORD:
            if k in step:
                return True

        return False

    def _gen_operation(self, op: dict):
        opt = OperationClazz(op.get('type').upper())

        code = eval('{}(self._context).translate(op)'.format(opt.name))

        return code + self.LINE


class Operation(object):
    def __init__(self, context: Context):
        self._context = context

    def translate(self, op: dict):
        pass


class METER(Operation):
    def translate(self, op: dict):
        clazz = op.get('clazz')
        module = op.get('module')
        opt = op.get('operation')
        elem = op.get('element')
        param = op.get('parameter')
        addi = op.get('addition')
        se = op.get('security')
        rp = op.get('report')
        acd = op.get('acd')
        secs = op.get('sleep')
        ci = op.get('data_clazz_id')
        customframe = op.get('customframe')

        addr = self._context.meter.addr
        if isinstance(module, int):
            addr = '{}:{}'.format(module, self._context.meter.addr)

        code = "command.meter('{}').comm_addr('{}').operation('{}')".format(clazz, addr, opt)

        code += _transfer('element', elem)
        code += _transfer('parameter', param)
        code += _transfer('addition', addi)
        code += _transfer('security', se)
        code += _transfer('report', rp)
        code += _transfer('compare', acd)
        code += _transfer('secs', secs)
        code += _transfer('chip_id', ci)
        code += _transfer('customframe', customframe)

        code += ".exec(context)"

        return code


class EM(Operation):
    def translate(self, op: dict):
        clazz = op.get('clazz')
        opt = op.get('operation')
        param = op.get('parameter')

        code = "command.encrypt('{}').operation('{}').parameter({}).exec(context)".format(clazz, opt, param)

        return code


class BENCH(Operation):
    def translate(self, op: dict):
        opt = op.get('operation')
        param = op.get('parameter')
        interval = op.get('interval')
        acd = op.get('acd')
        secs = op.get('sleep')

        code = "command.bench().operation('{}')".format(opt)

        code += _transfer('parameter', param)
        code += _transfer('interval', interval)
        code += _transfer('compare', acd)
        code += _transfer('secs', secs)

        code += ".exec(context)"

        return code


class APP(Operation):
    def translate(self, op: dict):
        clazz = op.get('clazz')
        opt = op.get('operation')
        msg = op.get('message')
        param = op.get('parameter')

        code = "command.app('{}').operation('{}')".format(clazz, opt)

        if msg is not None:
            if param is not None:
                msg = msg.format(param)
            code += ".message('{}')".format(msg)

        code += ".exec(context)"

        return code


class ATS(Operation):
    def translate(self, op: dict):
        opt = op.get('operation')
        param = op.get('parameter')
        glo = op.get('cache')
        stx = op.get('set')
        ptx = op.get('put')
        jp = op.get('jump')
        secs = op.get('sleep')

        code = "command.ats().operation('{}')".format(opt)

        code += _transfer('parameter', param)
        code += _transfer('glo', glo)
        code += _transfer('stx', stx)
        code += _transfer('ptx', ptx)
        code += _transfer('jp', jp)
        code += _transfer('secs', secs)

        code += ".exec(context)"

        return code


def _transfer(attribute, value):
    if value is not None:
        if isinstance(value, str):
            code = ".{}('{}')".format(attribute, value)
        else:
            code = ".{}({})".format(attribute, value)

        return code

    return ''
