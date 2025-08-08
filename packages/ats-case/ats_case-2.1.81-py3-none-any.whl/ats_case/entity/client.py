from ats_base.log.logger import logger

from ats_case.case import base, asb
from ats_case.case.context import Context


class App(object):
    def __init__(self):
        self._name = 'app'
        self._operation = None
        self._message = None
        self._parameter = None

    def operation(self, command: str):
        self._operation = command
        return self

    def message(self, msg):
        self._message = {'msg': msg}
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def show(self, context: Context, types=2):
        logger.info('~ @APP-> operation:{} message:{}'.format('show', self._message))
        base.send(context, todo={'{}:{}'.format(self._name, 'show'): self._message},
                  types=types, end=base.end_step(context, types))

    def error(self, context: Context, types=2):
        logger.info('~ @APP-> operation:{} message:{}'.format('error', self._message))
        base.send(context, todo={'{}:{}'.format(self._name, 'error'): self._message},
                  types=types, end=base.end_step(context, types))

    def exec(self, context: Context):
        logger.info('~ @APP-> operation:{} message:{}'.format(self._operation, self._message))
        base.send(context, todo={'{}:{}'.format(self._name, self._operation): self._message})