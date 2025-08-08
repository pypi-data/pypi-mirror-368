import random
import time
from robertcommondriver.system.iot.iot_plc_mitsubishi import MitsubishiClient, MitsubishiVersion, IOTPlcMitsubishi


def logging_print(**kwargs):
    print(kwargs)


def test_read_write():
    omron = MitsubishiClient(MitsubishiVersion.Qna_3E, '192.168.1.12', 6000)
    omron.logging(call_logging=logging_print)
    while True:
        aa = omron.read(('D263', 18))
        print(aa)
        #aa = omron.write(('D263', 18, 2.234))
        #print(aa.contents[0].contents[8])
        time.sleep(4)


def test_read_write1():
    omron = MitsubishiClient(MitsubishiVersion.A_1E, '192.168.1.12', 6001)
    omron.logging(call_logging=logging_print)
    while True:
        value = random.randint(1, 100) / 10
        #value = 5.6
        print(f"value: {value}")
        a1 = omron.write(('D263', 18, value))
        aa = omron.read(('D263', 18))
        print(aa.contents[0].contents[8])
        #aa = omron.write(('D263', 18, 2.234))
        #print(aa.contents[0].contents[8])
        time.sleep(4)


def test_read_write2():
    omron = MitsubishiClient(MitsubishiVersion.Qna_3E, '192.168.1.12', 6000)
    omron.logging(call_logging=logging_print)
    while True:
        value = random.randint(1, 100) / 10
        #value = 5.6
        print(f"value: {value}")
        a1 = omron.write(('D263', 18, value))
        aa = omron.read(('D263', 18))
        print(aa.contents[0].contents[8])
        #aa = omron.write(('D263', 18, 2.234))
        #print(aa.contents[0].contents[8])
        time.sleep(4)


def test_iot_mistubishi_read():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'timeout': 5}
    dict_point = {}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '2/192.168.1.12/6000', 'point_address': 'D263', 'point_type': 18, 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '2/192.168.1.12/6000', 'point_address': 'D260', 'point_type': 18, 'point_scale': '1'}
    client = IOTPlcMitsubishi(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            aa = client.write(values={'plc10': random.randint(1, 100) / 10})
            print(aa)

            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


test_iot_mistubishi_read()
