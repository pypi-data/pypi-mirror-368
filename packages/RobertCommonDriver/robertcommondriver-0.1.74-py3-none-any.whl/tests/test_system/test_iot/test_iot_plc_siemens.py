import random
import time
from robertcommondriver.system.iot.iot_plc_siemens import SiemensS7Client, SiemensS7Version, SiemensS7Server, IOTPlcSiemensS7


def logging_print(**kwargs):
    print(kwargs)


def test_siemens():
    s7 = SiemensS7Client(SiemensS7Version.S7_200, '192.168.1.184', 102, 0, 1)
    aa = s7.read(('V2634', 8))
    print(aa)


def test_siemens_server():
    s7 = SiemensS7Server(SiemensS7Version.S7_1500, '0.0.0.0', 102, 0, 1)
    s7.start_server()
    while True:
        time.sleep(1)


def test_iot_siemens_read():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'timeout': 5}
    dict_point = {}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '6/192.168.1.12/102/0/1', 'point_address': 'I0.0', 'point_type': 0, 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '6/192.168.1.11/102/0/1', 'point_address': 'DB1,0.3', 'point_type': 0, 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': '6/192.168.1.12/102/0/1', 'point_address': 'MW300', 'point_type': 10, 'point_scale': '1'}
    client = IOTPlcSiemensS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_iot_siemens_write():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'timeout': 5}
    dict_point = {}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '6/192.168.1.12/102/0/1', 'point_address': 'I0.0', 'point_type': 0, 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '6/192.168.1.12/102/0/1', 'point_address': 'DB1,0.3', 'point_type': 0, 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': '6/192.168.1.12/102/0/1', 'point_address': 'MW300', 'point_type': 10, 'point_scale': '1'}
    client = IOTPlcSiemensS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            #print(client.write(values={'plc10': 1, 'plc11': 0, 'plc12': 22}))
            print(client.write(values={'plc10': random.randint(0,1), 'plc11': random.randint(0,1), 'plc12': random.randint(0,100)}))
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_iot_siemens_server():

    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'timeout': 5}
    dict_point = {}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '6/0.0.0.0/102/0/1', 'point_address': 'I0.3', 'point_type': 0, 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '6/0.0.0.0/102/0/1', 'point_address': 'DB1,0.3', 'point_type': 0, 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': '6/0.0.0.0/102/0/1', 'point_address': 'MW300', 'point_type': 10, 'point_scale': '1'}
    client = IOTPlcSiemensS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            #print(client.write(values={'plc10': 1, 'plc11': 0, 'plc12': 22}))
            for name, point in dict_point.items():
                if name in ['plc10', 'plc11']:
                    point['point_value'] = random.randint(0, 1)
                else:
                    point['point_value'] = random.randint(0, 100)
                print(f"{point['point_address']}: {point['point_value']}")
            client.simulate(points=dict_point)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


test_siemens()