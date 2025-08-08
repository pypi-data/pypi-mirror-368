from ats_base.common import func

from ats_base.service import pro, em, mm
from ats_case.case import base, asb
from ats_case.case.context import Context
from ats_case.common.error import MeterSecurityAuthenticationError


def establish(context: Context, protocol: str):
    exec('_{}(context, protocol)'.format(protocol))


def _gw698(context: Context, protocol: str, retry_times=3):
    for i in range(retry_times):
        if i > 0:
            base.sleep(5)

        try:
            # 1. 读取esam参数
            result = pro.encode(
                func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                             operation='get:request:normal_list',
                             element=['F1000200', 'F1000300', 'F1000400', 'F1000500', 'F1000600', 'F1000700'],
                             session_key=context.test_sn))
            frame = base.write(context, result.get('frame'))
            data = pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
            # 2. 协商密钥
            e_r = data.get('result')
            e_r['session_key'] = context.test_sn
            em.handle(protocol, 'negotiate', e_r)
            # 3. 连接
            result = pro.encode(
                func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                             operation='connect:request:symmetry',
                             element='',
                             parameter={
                                 '期望的应用层协议版本号': 21,
                                 '期望的协议一致性块': 'FFFFFFFFC0000000',
                                 '期望的功能一致性块': 'FFFEC400000000000000000000000000',
                                 '客户机发送帧最大尺寸(字节)': 512,
                                 '客户机接收帧最大尺寸(字节)': 512,
                                 '客户机接收帧最大窗口尺寸(个)': 1,
                                 '客户机最大可处理APDU尺寸': 2000,
                                 '期望的应用连接超时时间(秒)': 7200,
                                 '认证请求对象': {
                                     '对称加密': {
                                         '密文1': asb.Session.get(context, 'em_data'),
                                         '客户机签名1': asb.Session.get(context, 'em_mac')
                                     }
                                 }
                             },
                             session_key=context.test_sn))
            frame = base.write(context, result.get('frame'))
            data = pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
            # 4. 加密
            e_r = data.get('result')
            e_r['session_key'] = context.test_sn
            em.handle(protocol, 'secret', e_r)
            # base.sleep(1)

            break
        except Exception as e:
            if i >= (retry_times - 1):
                raise MeterSecurityAuthenticationError('[表位:{}]{}'.format(context.meter.pos, str(e)))
            continue


def _dlms(context: Context, protocol: str, retry_times=3):
    for i in range(retry_times):
        if i > 0:
            base.sleep(5)

        try:
            step = context.case.steps[str(context.runtime.step)]
            if context.runtime.pro_sa_method is None:
                if not _dlms_hls(context, protocol, step):
                    if not _dlms_lls(context, protocol, step):
                        raise Exception('建立连接错误')
            elif context.runtime.pro_sa_method == "dlms_hls":
                if not _dlms_hls(context, protocol, step):
                    raise Exception('建立连接错误')
            elif context.runtime.pro_sa_method == "dlms_lls":
                if not _dlms_lls(context, protocol, step):
                    raise Exception('建立连接错误')

            break
        except Exception as e:
            if i >= (retry_times - 1):
                raise MeterSecurityAuthenticationError('[表位:{}]{}'.format(context.meter.pos, str(e)))
            continue


def _dlms_hls(context: Context, protocol: str, s):
    try:
        # 0. mac
        s['channel']['changed'] = 1
        s['channel']['baudrate'] = 300
        s['channel']['data_bits'] = 7
        s['channel']['parity'] = 'Even'
        mac = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='mac:request:baudrate',
                         element='',
                         session_key=context.test_sn))
        frame = base.write(context, mac.get('frame'))
        r = pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
        br = r['result']['result'].get('baudrate', 9600)

        s['channel']['changed'] = 2
        s['channel']['baudrate'] = br
        s['channel']['data_bits'] = 7
        s['channel']['parity'] = 'Even'
        ack = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='mac:request:ack',
                         element='',
                         parameter={
                             '波特率': br
                         },
                         session_key=context.test_sn))
        base.write(context, ack.get('frame'))
        pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
    except:
        return False

    try:
        # 1. snrm
        s['channel']['changed'] = 1
        s['channel']['baudrate'] = br
        s['channel']['data_bits'] = 8
        s['channel']['parity'] = 'None'
        srnm = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='snrm',
                         element='',
                         session_key=context.test_sn))
        frame = base.write(context, srnm.get('frame'))
        pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))

        # 2. aarq - AES-GMAC
        result = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='aarq',
                         element='',
                         parameter={
                             '应用上下文名': 'LN_Referencing_With_Ciphering',
                             '加密机制': 'HIGH_GMAC',
                             '用户信息': {
                                 '安全控制': 'SC_AE',
                                 '计数器': 0,
                                 '初始化': {
                                     '一致性提议': {'引用类型': 'LN_REFERENCING_PROPOSED'}
                                 }
                             }
                         },
                         session_key=context.test_sn))
        frame = base.write(context, result.get('frame'))
        result = pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
        if result.get('need_sa') == 1:
            _dlms_disc(context, protocol)
            return False
        else:
            # 3. rlrq
            result = pro.encode(
                func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                             operation='action:request:normal',
                             element={"000F0000280000FF01": "XXXXXXXX"},
                             session_key=context.test_sn))
            frame = base.write(context, result.get('frame'))
            pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))

            context.runtime.pro_sa_method = "dlms_hls"
    except:
        _dlms_disc(context, protocol)
        return False
    return True


def _dlms_disc(context: Context, protocol: str):
    try:
        # 4. disc
        disc = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='disc',
                         element='',
                         session_key=context.test_sn))
        frame = base.write(context, disc.get('frame'))
        pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
    finally:
        mm.Dict.delete(context.test_sn, 'session')
        mm.Dict.delete(context.test_sn, 'control')


def _dlms_lls(context: Context, protocol: str, s):
    # 重新开始 - 使用LLS连接
    try:
        # 0. mac
        s['channel']['changed'] = 1
        s['channel']['baudrate'] = 300
        s['channel']['data_bits'] = 7
        s['channel']['parity'] = 'Even'
        mac = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='mac:request:baudrate',
                         element='',
                         session_key=context.test_sn))
        frame = base.write(context, mac.get('frame'))
        r = pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
        br = r['result']['result'].get('baudrate', 9600)

        s['channel']['changed'] = 2
        s['channel']['baudrate'] = br
        s['channel']['data_bits'] = 7
        s['channel']['parity'] = 'Even'
        ack = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='mac:request:ack',
                         element='',
                         parameter={
                             '波特率': br
                         },
                         session_key=context.test_sn))
        base.write(context, ack.get('frame'))
        pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))
    except:
        return False

    try:
        # 1. snrm
        s['channel']['changed'] = 1
        s['channel']['baudrate'] = br
        s['channel']['data_bits'] = 8
        s['channel']['parity'] = 'None'
        srnm = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='snrm',
                         element='',
                         session_key=context.test_sn))
        frame = base.write(context, srnm.get('frame'))
        pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))

        # 2. aarq - LOW
        result = pro.encode(
            func.to_dict(protocol=protocol, comm_addr=context.meter.addr,
                         operation='aarq',
                         element='',
                         parameter={
                             '应用上下文名': 'LN_Referencing_No_Ciphering',
                             '加密机制': 'LOW',
                             '用户信息': {
                                 '初始化': {
                                     '一致性提议': {'引用类型': 'LN_REFERENCING_PROPOSED'}
                                 }
                             }
                         },
                         session_key=context.test_sn))
        frame = base.write(context, result.get('frame'))
        pro.decode(func.to_dict(protocol=protocol, frame=frame, session_key=context.test_sn))

        context.runtime.pro_sa_method = "dlms_lls"
    except:
        _dlms_disc(context, protocol)
        return False

    return True


def _dlt645(context: Context, retry_times=3):
    pass


def _cjt188(context: Context, retry_times=3):
    pass
