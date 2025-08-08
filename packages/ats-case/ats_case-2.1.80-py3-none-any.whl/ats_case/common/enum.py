from enum import Enum


class WorkMode(Enum):
    FORMAL = 'FORMAL'
    DEBUG = 'DEBUG'


class StepClazz(Enum):
    START = 0
    END = 1
    PROCESS = 2


class ScriptClazz(Enum):
    AUTO = 1
    MANUAL = 0


class OperationClazz(Enum):
    METER = 'METER'
    BENCH = 'BENCH'
    APP = 'APP'
    ATS = 'ATS'
    EM = 'EM'


