import re

from ats_base.service import mm, build_in
from ats_case.case.context import Context

NAME = 'session'

"""
    运行时变量替换
"""

V_A = {
    'global': '~global::(.+?)\']',
    'session': '~session::(.+?)\']'
}

V_F = {  # 查找要替换的格式
    'method': '~method::(.+?)\'',
    'result': '~result::(.+?)\'',
    'global': '~global::(.+?)\'',
    'session': '~session::(.+?)\''
}

V_I = {  # 转换为对应的系统调用函数
    'method': 'atm.{}',
    'result': 'context.runtime.sos[{}]["result"]',
    'global': 'context.runtime.glo.get("{}")',
    'session': 'asb.Session.get(context, "{}")',
    'build_in': 'asb.build_in_handle(context, "{}")'
}


def V_loop(context: Context, sd):
    sd = _replace_build_in(context, sd)
    sd = _replace_context(context, sd)
    sd = _replace_array(context, sd)
    sd = _replace_common(context, sd)

    return sd


def _replace_array(context: Context, sd: str):
    for w, s_format in V_A.items():
        re_l = re.findall(r"{}".format(s_format), sd)

        for k in re_l:
            try:
                ss = eval(V_I[w].format(k))
                a_r = ss.split(';')
                if len(a_r) <= 1:
                    a_r = ss.split(',')
                r_r = []
                for av in a_r:
                    r_r.append('"{}"'.format(av))

                sd = sd.replace('\'~{}::{}\''.format(w, k), ','.join(r_r))
            except:
                pass

    return sd


def _replace_common(context: Context, sd: str):
    for word, search_format in V_F.items():
        re_list = re.findall(r"{}".format(search_format), sd)
        if len(re_list) <= 0:
            re_list = re.findall(r"{}$".format(search_format[:-1]), sd)

        for key in re_list:
            var = sd.replace('\'~{}::{}\''.format(word, key), V_I[word].format(key))
            if var == sd:
                var = sd.replace('~{}::{}'.format(word, key), V_I[word].format(key))
            sd = var

    return sd


def _replace_context(context: Context, sd: str):
    re_list = re.findall(r"#(.+?)\'", sd)
    if len(re_list) <= 0:
        re_list = re.findall(r"#(.+?)$", sd)

    for c in re_list:
        var = sd.replace('\'#{}\''.format(c), c)
        if var == sd:
            var = sd.replace('#{}'.format(c), c)
        sd = var

    return sd


def _replace_build_in(context: Context, sd: str):
    re_list = re.findall(r"~build_in@@(.+?)<<(.+?)(>>(.+?))?\'", sd)
    if len(re_list) <= 0:
        re_list = re.findall(r"~build_in@@(.+?)<<(.+?)(>>(.+?))?$", sd)

    if len(re_list) > 0:
        pd = {}
        for f in re_list:
            op = f[0]
            param = f[1]
            flag = f[2]
            rs = f[3]

            pa_list = re.findall(r"(\w*)=([~#.:(%‰)\w]*)", param)
            for p in pa_list:
                v = _replace_common(context, _replace_context(context, p[1]))
                try:
                    if v.find('asb.Session') >= 0:
                        v = v.replace('asb.Session', 'Session')
                    pd[p[0]] = eval(v)
                except:
                    pd[p[0]] = v

            result = build_in.handle(function=op, data=pd, debug_url=context.debug_service_url.get("build_in"))

            of = '~build_in@@{}<<{}'.format(op, param)
            if len(flag) > 0:
                rs_list = re.findall(r"(\w*)=(#\w*)", rs)
                for r in rs_list:
                    if r[1] == '#RSD':
                        context.runtime.glo[r[0]] = result
                    else:
                        context.runtime.glo[r[0]] = result[r[1]]

                of = '~build_in@@{}<<{}>>{}'.format(op, param, rs)

            if isinstance(result, str):
                sd = sd.replace('{}'.format(of), str(result))
            else:
                sd = sd.replace('\'{}\''.format(of), str(result))

    return sd


"""
    Redis缓存
"""


class Application(object):
    @staticmethod
    def get(test_sn: str, key: str):
        sn = test_sn.split(':')[0]
        value = mm.Dict.get(sn, key)

        return value

    @staticmethod
    def set(test_sn: str, key, data):
        sn = test_sn.split(':')[0]
        mm.Dict.put(sn, key, data)


class Session(object):
    NAME = 'session'

    @staticmethod
    def get(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, Session.NAME)
        if isinstance(session, dict):
            return session.get(key)

        return None

    @staticmethod
    def set(context: Context, key: str, data):
        session = mm.Dict.get(context.test_sn, Session.NAME)

        kv = {key: data}
        if isinstance(session, dict):
            session.update(kv)
            mm.Dict.put(context.test_sn, Session.NAME, session)
        else:
            mm.Dict.put(context.test_sn, Session.NAME, kv)

    @staticmethod
    def set_callback(test_sn: str, key: str, data):
        session = mm.Dict.get(test_sn, Session.NAME)

        kv = {key: data}
        if isinstance(session, dict):
            session.update(kv)
            mm.Dict.put(test_sn, Session.NAME, session)
        else:
            mm.Dict.put(test_sn, Session.NAME, kv)

    @staticmethod
    def delete(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, Session.NAME)

        if isinstance(session, dict):
            try:
                session.pop(key)
                mm.Dict.put(context.test_sn, Session.NAME, session)
            except:
                pass


class BreakPoint(object):
    NAME = 'breakpoint'

    @staticmethod
    def get(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, BreakPoint.NAME)
        if isinstance(session, dict):
            return session.get(key)

        return None

    @staticmethod
    def set(context: Context, key: str, data):
        session = mm.Dict.get(context.test_sn, BreakPoint.NAME)

        kv = {key: data}
        if isinstance(session, dict):
            session.update(kv)
            mm.Dict.put(context.test_sn, BreakPoint.NAME, session)
        else:
            mm.Dict.put(context.test_sn, BreakPoint.NAME, kv)

    @staticmethod
    def delete(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, BreakPoint.NAME)

        if isinstance(session, dict):
            try:
                session.pop(key)
                mm.Dict.put(context.test_sn, BreakPoint.NAME, session)
            except:
                pass


def test_log(test_sn):
    return mm.Dict.get("test:log", test_sn)


def flush(test_sn):
    mm.delete(test_sn)



