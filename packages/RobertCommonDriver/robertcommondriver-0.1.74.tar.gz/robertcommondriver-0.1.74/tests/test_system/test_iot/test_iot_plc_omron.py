import random
import time
from robertcommondriver.system.iot.iot_plc_omron import OmronFinsClient, IOTPlcOmronFins


def logging_print(**kwargs):
    print(kwargs)


def test_read_write():
    omron = OmronFinsClient('192.168.1.12', 9600, 0x0B)
    omron.logging(call_logging=logging_print)
    while True:
        aa = omron.write(('D263', 18, 2.234))
        print(aa.contents[0].contents[8])
        time.sleep(4)


def test_iot_omron_read():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'timeout': 5}
    dict_point = {}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '192.168.1.12/9600/11', 'point_address': 'D263', 'point_type': 18, 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '192.168.1.12/9600/11', 'point_address': 'W320', 'point_type': 6, 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': '192.168.1.12/9600/11', 'point_address': 'W330.2', 'point_type': 0, 'point_scale': '1'}
    client = IOTPlcOmronFins(configs=dict_config, points=dict_point)
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


def test_iot_omron_simulate():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'timeout': 5}
    dict_point = {}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '0.0.0.0/9600/11', 'point_address': 'D263', 'point_type': 18, 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '0.0.0.0/9600/11', 'point_address': 'W320', 'point_type': 6, 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': '0.0.0.0/9600/11', 'point_address': 'W330.2', 'point_type': 0, 'point_scale': '1'}
    client = IOTPlcOmronFins(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            for name, point in dict_point.items():
                if name in ['plc12']:
                    point['point_value'] = random.randint(0, 1)
                else:
                    point['point_value'] = random.randint(0, 100)
                print(f"{point['point_address']}: {point['point_value']}")
            client.simulate(points=dict_point)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(400)


test_iot_omron_read()