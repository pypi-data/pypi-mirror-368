from ats_base.common import func
from ats_base.common.enum import ProClazz
from ats_base.log.logger import logger
from ats_base.service import em, udm

from ats_case.case import base, asb
from ats_case.case.context import Context


class Encryptor(object):
    def __init__(self, protocol):
        self._protocol = ProClazz(protocol)
        self._operation = None
        self._parameter = None
        self._result = None

    def operation(self, op: str):
        self._operation = op
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def handle(self, context: Context):
        try:
            if self._parameter is None:
                self._parameter = {}
            self._parameter = context.runtime.sos[context.runtime.step - 1]['result']
            self._parameter['session_key'] = context.test_sn
        except:
            pass

        logger.info(
            '~ @EM-> security:{} operation:{} parameter:{}'.format(self._protocol, self._operation, self._parameter))
        self._result = em.handle(self._protocol.name, self._operation, self._parameter)
        logger.info('~ @EM<- security:{} operation:{} result:{}'.format(self._protocol, self._operation, self._result))
        self._flush(context)

    def _flush(self, context: Context):
        context.runtime.sos.update({context.runtime.step: func.to_dict(obj='em', op=self._operation
                                                                       , parameter=self._parameter,
                                                                       result=self._result)})

    def acv(self, context: Context):
        data = func.to_dict(result=self._result)

        logger.info('~ @ACD-> module:{} function:{} parameter:{}'.format(
            self._protocol.name, self._operation, self._parameter))
        result = udm.handle(module='em.{}'.format(self._protocol.name), function=self._operation,
                            data=data, debug_url=context.debug_service_url.get('acd'))
        logger.info('~ @ACD<- module:{} function:{} result:{}'.format(self._protocol.name, self._operation, result))

        context.runtime.sas[context.runtime.step] = result

        return result

    def exec(self, context: Context):
        self.handle(context)
        base.send(context, todo={'app:show': {'msg': self.acv(context)}})
