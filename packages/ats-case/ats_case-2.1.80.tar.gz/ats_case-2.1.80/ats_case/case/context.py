from datetime import datetime

from ats_base.common import func
from ats_base.service import mm
from ats_case.common.enum import WorkMode, ScriptClazz


class Context(object):
    """
    测试用例上下文
    """

    def __init__(self, sn):
        self._test_sn = sn
        self._parse()

    def _parse(self):
        tl = mm.Dict.get("test:log", self._test_sn)

        self._mode = WorkMode(tl.get('mode'))
        self._project = tl.get('project')
        self._renew = tl.get('renew', 0)  # 1: 断点续测
        self._offbench = tl.get('offbench', 0)  # 1: 脱机
        self._start_time = datetime.now()
        self._tester = self.Tester(tl.get('tester'))
        self._case = self.Case(tl.get('usercase'))
        self._meter = self.Meter(self, tl.get('meter'))
        self._bench = self.Bench(tl.get('bench'))
        # 运行时
        self._runtime = self.Runtime(self)
        # Debug模式 - 测试开发人员本机调试数据比对服务使用
        self._debug_service_url = tl.get('debug_service_url', {})
        # 项目全局变量集合 - 目前包含计量参数 和 dlms协议的数据项
        self._overall = self.Overall(tl.get('overall', {}))

    @property
    def mode(self):
        return self._mode

    @property
    def project(self):
        return self._project

    @property
    def renew(self):
        return self._renew

    @property
    def offbench(self):
        return self._offbench

    @property
    def start_time(self):
        return self._start_time

    @property
    def test_sn(self):
        return self._test_sn

    @property
    def tester(self):
        return self._tester

    @property
    def bench(self):
        return self._bench

    @property
    def case(self):
        return self._case

    @property
    def meter(self):
        return self._meter

    @property
    def runtime(self):
        return self._runtime

    @property
    def debug_service_url(self):
        return self._debug_service_url

    @property
    def overall(self):
        return self._overall

    class Overall(object):
        def __init__(self, data: dict):
            self._dlms = data.get('dlms', {})
            self._measure = data.get('measure', {})
            self._variable = data.get('variable', {})

        @property
        def dlms(self):
            return self._dlms

        @property
        def measure(self):
            return self._measure

        @property
        def variable(self):
            return self._variable

    class Tester(object):
        def __init__(self, data: dict):
            self._ip = data.get('ip')
            self._port = data.get('port')
            self._username = data.get('username')
            self._hostname = data.get('hostname')

        @property
        def ip(self):
            return self._ip

        @property
        def port(self):
            return self._port

        @property
        def username(self):
            return self._username

        @property
        def hostname(self):
            return self._hostname

        @property
        def api(self):
            return "http://{}:{}/accept".format(self.ip, self.port)

    class Bench(object):
        def __init__(self, data: dict):
            if data is not None and len(data) > 0:
                self._manufacture = data.get('manufacture', '')
                self._model = data.get('model', '')
                self._port = data.get('port', 0)
                self._error_threshold = data.get('error_threshold', 0)

        #         self._iabc = data.get('iabc', 'H')
        #
        @property
        def manufacture(self):
            return self._manufacture

        @property
        def model(self):
            return self._model

        @property
        def port(self):
            return self._port

        @property
        def error_threshold(self):
            return self._error_threshold

    class Case(object):
        def __init__(self, data: dict):
            self._id = data.get('id', -1)
            self._name = data.get('name', 'test')
            self._code = data.get('code')
            self._version = data.get('version')
            self._script = ScriptClazz(data.get('script', 1))
            self._control = data.get('control', {})
            self._steps = data.get('steps', {})
            self._end = data.get('end', 0)

            if self._code is not None:
                self._name = '{}_{}'.format(self._name, self._code)
            if self._version is not None:
                self._name = '{}_{}'.format(self._name, self._version)
            if isinstance(self._control, str):
                self._control = self._control.replace('null', 'None')
                self._control = eval(self._control)
            if isinstance(self._steps, str):
                self._steps = self._steps.replace('null', 'None')
                self._steps = eval(self._steps)

        @property
        def id(self):
            return self._id

        @property
        def name(self):
            return self._name

        @property
        def script(self):
            return self._script

        @property
        def control(self):
            return self._control

        @property
        def steps(self):
            return self._steps

        @property
        def code(self):
            return self._code

        @property
        def version(self):
            return self._version

        @property
        def end(self):
            return self._end

    class Meter(object):
        def __init__(self, parent, data: dict):
            self._parent = parent
            self._index = data.get('index', 0)
            self._pos = data.get('pos')
            self._addr = data.get('addr')
            self._no = data.get('no')
            self._protocol = data.get('protocol')
            self._model = data.get('model')
            self._connect = data.get('connect')
            self._rated_voltage = data.get('rated_voltage')
            self._rated_current = data.get('rated_current')
            self._max_current = data.get('max_current')
            self._min_current = data.get('min_current')
            self._transfer_current = data.get('transfer_current')  # 转折电流
            self._starting_current = data.get('starting_current')
            self._frequency = data.get('frequency')
            self._mconst = data.get('mconst')  # 脉冲常数
            self._mpluse = data.get('mpluse')  # 圈数
            self._iabc = data.get('iabc')
            self._end = data.get('end', 0)
            self._operator = data.get('opcode', '00000000')
            self._pwd = data.get('password', '000000')
            self._category_code = data.get('category_code', 0)
            self._activemsm = data.get('activemsm', None)
            self._reactivemsm = data.get('reactivemsm', None)
            self._msthreshold = data.get('msthreshold', 0)

            session = dict()
            if self._operator is not None:
                session['operator'] = self._operator
            if self._pwd is not None:
                session['pwd'] = self._pwd

            mm.Dict.put(self._parent.test_sn, 'session', session)

        #         self._channel = {'RS485': data.get('baudrate_485'), 'IR': data.get('baudrate_ir'),
        #                          'PLC': data.get('baudrate_plc')}
        #
        #     def get_channel(self, c: CHANNEL):
        #         return func.to_dict(type=c.value, baudrate=self._channel.get(c.value))

        @property
        def index(self):
            return self._index

        @property
        def pos(self):
            return self._pos

        @property
        def addr(self):
            return self._addr

        @property
        def no(self):
            return self._no

        @property
        def protocol(self):
            return self._protocol

        @property
        def model(self):
            return self._model

        @property
        def connect(self):
            return self._connect

        @property
        def rated_voltage(self):
            return self._rated_voltage

        @property
        def rated_current(self):
            return self._rated_current

        @property
        def max_current(self):
            return self._max_current

        @property
        def min_current(self):
            return self._min_current

        @property
        def transfer_current(self):
            return self._transfer_current

        @property
        def starting_current(self):
            return self._starting_current

        @property
        def frequency(self):
            return self._frequency

        @property
        def mconst(self):
            return self._mconst

        @property
        def mpluse(self):
            return self._mpluse

        @property
        def iabc(self):
            return self._iabc

        @property
        def end(self):
            return self._end

        @property
        def category_code(self):
            return self._category_code

        @property
        def activemsm(self):
            return self._activemsm

        @property
        def reactivemsm(self):
            return self._reactivemsm

        @property
        def msthreshold(self):
            return self._msthreshold

    class Runtime(object):
        """
        运行时
        """

        def __init__(self, parent):
            self._parent = parent
            # 仅供2.0.0之前版本使用
            self._loop_sn = 0
            self._loop_count = 0
            self._loop_index = 0
            # 当前步骤
            self._incr_loop_sn = 0
            self._step = -1
            # 控制语句数据
            self._start_conditions = set()
            self._end_conditions = set()
            self._logicBody = {}
            # 当前循环
            self._currentLoop = None
            # 结果验证失败, 重复操作延时
            self._meter_result_valid_fail_delay = 2
            self._bench_result_valid_fail_delay = 2
            # 步骤协议解析返回结果集
            self._sos = {}
            # 步骤对比返回结果集 - 用例结束时统计执行结果
            self._sas = {}
            # 全局变量 - 用户自定义
            self._glo = {}
            # 多帧时使用
            self._final_result = None

            # 加载逻辑控制数据
            self._logic_control()

            # 协议安全认证连接方式
            self._pro_sa_method = None

            # 加载全局变量
            g = self._parent.case.control.get('global')
            if isinstance(g, dict) and len(g) > 0:
                for key, value in g.items():
                    try:
                        if str(value).find('[') >= 0 or str(value).find('{') >= 0 or str(value).find('(') >= 0:
                            self._glo[key] = eval(value)
                        else:
                            self._glo[key] = value
                    except:
                        self._glo[key] = value
                # self._glo = g

        def _logic_control(self):
            # if集合
            ifs = self._parent.case.control.get('ifs')
            if isinstance(ifs, dict):
                try:
                    ifs.pop('offbench')
                except:
                    pass

                if len(ifs) > 0:
                    for ranges, condition in ifs.items():
                        step_start = int(ranges.split(':')[0])
                        step_end = int(ranges.split(':')[1])
                        self._start_conditions.add(step_start)
                        self._end_conditions.add(step_end)

                        self._logicBody["IF_S_{}".format(step_start)] = func.to_dict(start=step_start, end=step_end,
                                                                                     condition=condition)
                        self._logicBody["IF_E_{}".format(step_end)] = func.to_dict(start=step_start, end=step_end,
                                                                                   condition=condition)

            # loop集合
            loops = self._parent.case.control.get('loops')
            if isinstance(loops, list):
                for loop in loops:
                    ranges = loop.get('range')
                    count = loop.get('count')

                    step_start = int(ranges.split(':')[0])
                    step_end = int(ranges.split(':')[1])
                    self._start_conditions.add(step_start)
                    self._end_conditions.add(step_end)

                    self._logicBody["LOOP_S_{}".format(step_start)] = func.to_dict(start=step_start, end=step_end,
                                                                                   count=count)
                    self._logicBody["LOOP_E_{}".format(step_end)] = func.to_dict(start=step_start, end=step_end,
                                                                                 count=count)

        @property
        def loop_sn(self):
            return self._loop_sn

        @loop_sn.setter
        def loop_sn(self, value):
            self._loop_sn = value

        @property
        def loop_count(self):
            return self._loop_count

        @loop_count.setter
        def loop_count(self, value):
            self._loop_count = value

        @property
        def loop_index(self):
            return self._loop_index

        @loop_index.setter
        def loop_index(self, value):
            self._loop_index = value

        @property
        def incr_loop_sn(self):
            return self._incr_loop_sn

        @incr_loop_sn.setter
        def incr_loop_sn(self, value):
            self._incr_loop_sn = value

        @property
        def step(self):
            return self._step

        @step.setter
        def step(self, value):
            self._step = value

        @property
        def start_conditions(self):
            return self._start_conditions

        @property
        def end_conditions(self):
            return self._end_conditions

        @property
        def logicBody(self):
            return self._logicBody

        @property
        def currentLoop(self):
            return self._currentLoop

        @currentLoop.setter
        def currentLoop(self, value):
            self._currentLoop = value

        @property
        def meter_result_valid_fail_delay(self):
            return self._meter_result_valid_fail_delay

        @meter_result_valid_fail_delay.setter
        def meter_result_valid_fail_delay(self, value):
            self._meter_result_valid_fail_delay = value

        @property
        def bench_result_valid_fail_delay(self):
            return self._bench_result_valid_fail_delay

        @bench_result_valid_fail_delay.setter
        def bench_result_valid_fail_delay(self, value):
            self._bench_result_valid_fail_delay = value

        @property
        def sos(self):
            return self._sos

        @sos.setter
        def sos(self, value):
            self._sos = value

        @property
        def sas(self):
            return self._sas

        @sas.setter
        def sas(self, value):
            self._sas = value

        @property
        def glo(self):
            return self._glo

        @glo.setter
        def glo(self, value):
            self._glo = value

        @property
        def final_result(self):
            return self._final_result

        @final_result.setter
        def final_result(self, value):
            self._final_result = value

        @property
        def pro_sa_method(self):
            return self._pro_sa_method

        @pro_sa_method.setter
        def pro_sa_method(self, value):
            self._pro_sa_method = value
