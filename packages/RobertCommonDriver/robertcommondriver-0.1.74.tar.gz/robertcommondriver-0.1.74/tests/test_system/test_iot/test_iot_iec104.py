import time
from robertcommondriver.system.iot.iot_iec104 import IOTIEC104, unpack, IECData, IECPacket, IECFrame


def logging_print(**kwargs):
    print(kwargs)


def test_read():
    dict_config = {'host': '192.168.1.184', 'port': 2404, 'timeout': 4}
    dict_point = {}
    dict_point['iec1'] = {'point_writable': True, 'point_name': 'iec1', 'point_type': 1, 'point_address': 1, 'point_scale': '1'}
    dict_point['iec2'] = {'point_writable': True, 'point_name': 'iec2', 'point_type': 13, 'point_address': 16386, 'point_scale': '1'}

    client = IOTIEC104(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read(names=list(dict_point.keys()))
            print(result)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(1)


def test_parse():
    #r = IOTIEC104.APDU(bytes.fromhex('68 0E 06 00 08 00 64 01 06 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'))
    #r = IOTIEC104.APDU(bytes.fromhex('68 0E 02 00 02 00 01 82 14 00 01 00 01 00 00 01 68 0E 04 00 02 00 64 01 0A 00 01 00 00 00 00 14'))
    #datas = bytes.fromhex('68 8C 36 00 02 00 01 FF 14 00 01 00 F3 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
    datas = bytes.fromhex('68 0E 30 98 9E 02 64 01 47 00 01 00 00 00 00 14')
    r = IOTIEC104.APDU(datas)
    print(r.info())
    s = IOTIEC104.ASDU(datas[6:]).values()

    pkt = IOTIEC104.APDU()
    pkt /= IOTIEC104.APCI(ApduLen=14, Type=0x00, Tx=12, Rx=0)
    pkt /= IOTIEC104.ASDU(Type=100, SQ=0, Cause=6, Num=1, Test=0, OA=0, Addr=1, IOA=[IECData.IOAS[100](IOA=0, QOI=0x14)])
    print(IOTIEC104().format_bytes(pkt.build()))

    pkt = IOTIEC104.APDU()
    pkt /= IOTIEC104.APCI(ApduLen=4, Type=0x01, Rx=12)
    print(IOTIEC104().format_bytes(pkt.build()))


def test_parse1():
    #r = IOTIEC104.APDU(bytes.fromhex('68 0E 06 00 08 00 64 01 06 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'))
    #r = IOTIEC104.APDU(bytes.fromhex('68 0E 02 00 02 00 01 82 14 00 01 00 01 00 00 01 68 0E 04 00 02 00 64 01 0A 00 01 00 00 00 00 14'))
    datas = bytes.fromhex('68 0E 30 98 9E 02 64 01 47 00 01 00 00 00 00 14')
    datas = bytes.fromhex('68 0E 30 00 06 00 65 01 07 00 00 00 00 00 00 45')

    r = IOTIEC104.APDU(datas)
    print(r.info())

    frame = IECFrame.iec_104.parse(datas)   # 解析速度快
    print(frame)


def test_read1():
    dict_config = {'host': '127.0.0.1', 'port': 2404, 'timeout': 2, 'zongzhao_interval': 60, 'zongzhao_timeout': 30,  'dianneng_interval': 60, 'dianneng_timeout': 30, 'u_test_timeout': 10,  's_interval': 1}
    dict_point = {}
    dict_point['iec1'] = {'point_writable': True, 'point_name': 'iec1', 'point_type': 1, 'point_address': 1, 'point_scale': '1'}
    dict_point['iec2'] = {'point_writable': True, 'point_name': 'iec2', 'point_type': 13, 'point_address': 3, 'point_scale': '1'}

    client = IOTIEC104(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read(names=list(dict_point.keys()))
            print(result)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(5)


def test_frame():
    pkt = IOTIEC104.APDU()
    pkt /= IOTIEC104.APCI(ApduLen=14, Type=0x00, Tx=0, Rx=0)
    pkt /= IOTIEC104.ASDU(Type=100, SQ=0, Cause=6, Num=1, Test=0, OA=0, Addr=1, IOA=[IECData.IOAS[100](IOA=0, QOI=0x14)])
    print(IOTIEC104().format_bytes(pkt.build()))


    pkt = IOTIEC104.APDU()
    pkt /= IOTIEC104.APCI(ApduLen=14, Type=0x00, Tx=2, Rx=7)
    pkt /= IOTIEC104.ASDU(Type=101, SQ=0, Cause=6, Num=1, Test=0, OA=0, Addr=1, IOA=[IECData.IOAS[101](IOA=0, QCC=0x45)])
    print(IOTIEC104().format_bytes(pkt.build()))

    info = IOTIEC104.APDU(bytes.fromhex('68 1A 0E 00 00 00 0D 02 01 00 01 00 01 40 00 A4 70 92 42 00 06 40 00 88 1D 12 41 00')).info()
    print(info)


def test_dianneng():
    dict_config = {'host': '127.0.0.1', 'port': 2404, 'timeout': 5, 'zongzhao_interval': 0, 'zongzhao_timeout': 30, 'dianneng_interval': 20, 'dianneng_timeout': 10, 'u_test_timeout': 10,  's_interval': 4}
    dict_point = {}
    dict_point['iec1'] = {'point_writable': True, 'point_name': 'iec1', 'point_type': 13, 'point_address': 2, 'point_scale': '1'}
    dict_point['iec2'] = {'point_writable': True, 'point_name': 'iec2', 'point_type': 13, 'point_address': 16385, 'point_scale': '1'}
    dict_point['iec3'] = {'point_writable': True, 'point_name': 'iec3', 'point_type': 1, 'point_address': 1176, 'point_scale': '1'}   # 37515
    dict_point['iec4'] = {'point_writable': True, 'point_name': 'iec4', 'point_type': 1, 'point_address': 1, 'point_scale': '1'}   # 500315

    client = IOTIEC104(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read(names=list(dict_point.keys()))
            print(result)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(10)


test_dianneng()