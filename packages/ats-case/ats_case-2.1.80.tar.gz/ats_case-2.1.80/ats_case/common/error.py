class APIError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "APIError - API服务接口[{}], 连接失败.".format(repr(self.value))


class MeterNeedSecurityAuthentication(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "MeterNeedSecurityAuthentication - 电表需要安全认证, 表位:[{}].".format(repr(self.value))


class MeterSecurityAuthenticationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "MeterSecurityAuthenticationError - 电表安全认证失败, {}.".format(repr(self.value))


class MeterResponseFrameNoneError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "MeterResponseFrameNoneError - 电表无响应帧, {}.".format(repr(self.value))


class MeterResponseFrameParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "MeterResponseFrameParseError - 电表响应帧解析失败, {}.".format(repr(self.value))


class BenchReadNoneError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "BenchReadNoneError - 表台读取误差错误, {}.".format(repr(self.value))


class ClientError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "ClientReturnError - 客户端返回结果为空. {}".format(repr(self.value))


# MeterTimeoutError 电表连接超时
# 服务接口错误  电表错误  客户端错误 加密机错误
# 连接错误 代码错误 操作错误


