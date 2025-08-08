import os
import threading

import gevent
import pytest

from datetime import datetime

from ats_base.common import func
from ats_base.common.enum import Payload
from ats_base.service import mm, db, msg

from ats_case.case import asb
from ats_case.common.enum import WorkMode


# 主进程
def run(**kwargs):
    try:
        mode = WorkMode(kwargs.get('mode'))
        if mode == WorkMode.FORMAL:
            pt = FormalMode(kwargs)
        else:
            pt = DebugMode(kwargs)
        pt.run()
    except:
        pass


# 装饰器
def message(fc):
    def wrapper(self):
        fc(self)

        # after
        try:
            self._end_time = datetime.now()
            msg.send('dingding', func.to_dict(payload=Payload.NORMAL.value, workmode=self._workmode.value,
                                              project=self._project, test_sn=self._sn,
                                              start_time=self._start_time.strftime('%Y.%m.%d %H:%M:%S'),
                                              end_time=self._end_time.strftime('%Y.%m.%d %H:%M:%S')))
        except Exception as e:
            print(str(e))

    return wrapper


class ExecMode(object):
    def __init__(self, data: dict):
        self._data = data
        self._workmode = WorkMode(data.get('mode', 'DEBUG'))
        self._project = self._data.get('project', '')
        self._username = self._data.get('tester', {}).get('username', '')
        self._sn = self._username.upper() + datetime.now().strftime('%y%m%d%H%M%S%f')
        self._start_time = datetime.now()
        self._end_time = None

        self._init()

    def _init(self):
        pass

    def run(self):
        pass

    def _build(self, work_mode: WorkMode, code: str = None):
        if code is None:
            code = 'case'

        user_dir = func.makeDir(func.project_dir(), 'testcase', work_mode.value.lower(), self._username)
        template_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'testcase_v1.tmp')
        script_file = os.path.join(user_dir, 'test_{}.py'.format(code))

        with open(template_file, 'r', encoding='UTF-8') as file:
            content = file.read()
            content = content.replace('{script}', code.upper())
        with open(script_file, 'w', encoding='UTF-8') as file:
            file.write(content)

        return script_file


class FormalMode(ExecMode):
    def _init(self):
        sn = self._data.get('test_sn')

        if sn is None or len(sn) == 0:
            self._save()
        else:  # 断点续测
            self._sn = sn
            self._data['renew'] = 1
            self._data = mm.Dict.get('test:log', self._sn)

        self._cases = self._data.get('usercases', [])
        self.meters = self._data.get('meters', [])

        asb.Application.set(self._sn, "meter:quantity", len(self.meters))

    def _save(self):
        try:
            db.save('test:log', sn=self._sn, start_time=self._start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    offbench=self._data.get('offbench', 0), tester=self._data.get('tester'),
                    usercases=self._data.get('usercases'), meters=self._data.get('meters'),
                    bench=self._data.get('bench'))  # , debug_service_url=self._data.get('debug_service_url')
        except Exception as e:
            print(str(e))

    @message
    def run(self):
        index = 0
        for id_v, data in self._cases.items():
            case = self._get_case(id_v, data)

            index += 1
            if index == len(self._cases):
                case['end'] = 1

            case_task = self.CaseTask(self, case)
            case_task.start()
            case_task.join()

    def _get_case(self, id_v, data):
        idv = id_v.split(':')
        case_id = idv[0]
        version = idv[1]

        c_v = db.query('view:case:version', id=case_id, version=version)
        if isinstance(data, dict):
            g = data.get('global')
            if isinstance(g, dict):
                if isinstance(c_v['control'], str):
                    c_v['control'] = c_v['control'].replace('null', 'None')
                    control = eval(c_v['control'])

                    control['global'] = g
                    c_v['control'] = str(control)

        return c_v

    class CaseTask(threading.Thread):
        def __init__(self, parent, case):
            super(FormalMode.CaseTask, self).__init__()
            self._parent = parent
            self._case = case

        def run(self):
            gs = []
            length = len(self._parent.meters)
            for i in range(length):
                # i = 0 执行操作表台 传入参数index
                self._parent.meters[i]['index'] = i
                # 全部用例和电表结束标签
                if self._case.get('end', 0) == 1 and i == (length - 1):
                    self._parent.meters[i]['end'] = 1
                gs.append(gevent.spawn(self._parent.exec, self._parent.handle(case=self._case,
                                                                              meter=self._parent.meters[i])))

            gevent.joinall(gs)

    def handle(self, case, meter):
        self._data['usercase'] = case
        self._data['meter'] = meter

        test_sn = '{}:{}'.format(self._sn, meter['pos'])
        mm.Dict.put('test:log', test_sn, self._data)

        return test_sn

    def exec(self, test_sn):
        pytest.main(["-sv", self._build(WorkMode.FORMAL), '--sn={}'.format(test_sn)])


class DebugMode(ExecMode):
    def _init(self):
        asb.Application.set(self._sn, "meter:quantity", 1)
        self._flush()

    def _flush(self):
        mm.Dict.put('test:log', self._sn, self._data)

    @message
    def run(self):
        pytest.main(["-sv", self._build(WorkMode.DEBUG), '--sn={}'.format(self._sn)])
