import random
import time
from robertcommondriver.system.iot.iot_plc_ab import AllenBradleyClient, IOTPlcAllenBradley


def logging_print(**kwargs):
    print(kwargs)


def test_read_write():
    omron = AllenBradleyClient('192.168.1.12', 44818, 0)
    omron.logging(call_logging=logging_print)
    while True:
        a1 = omron.write(('A11', 10, 12345))

        aa = omron.read([('A11', 10)])
        print(aa)
        time.sleep(4)


def test_iot_ab_read():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'timeout': 5}
    dict_point = {}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '192.168.1.12/44818/0', 'point_address': 'A11', 'point_type': 10, 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '192.168.1.12/44818/0', 'point_address': 'A1', 'point_type': 10, 'point_scale': '1'}
    client = IOTPlcAllenBradley(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            aa = client.write(values={'plc10': random.randint(1, 100)})
            print(aa)

            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


test_iot_ab_read()
