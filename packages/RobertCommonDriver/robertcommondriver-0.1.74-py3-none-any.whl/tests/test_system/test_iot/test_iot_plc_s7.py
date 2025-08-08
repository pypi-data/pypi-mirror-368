import random
import time
from robertcommondriver.system.iot.iot_plc_s7 import IOTPlcS7


def logging_print(**kwargs):
    print(kwargs)


def test_simulate():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500}
    dict_point = {}
    dict_point['plc111'] = {'point_writable': True, 'point_name': 'plc111', 'point_device_address': 102, 'point_address': 'DB3,REAL4', 'point_scale': '1'}
    dict_point['plc211'] = {'point_writable': True, 'point_name': 'plc211', 'point_device_address': 102, 'point_address': 'DB3,REAL8', 'point_scale': '1'}
    dict_point['plc1'] = {'point_writable': True, 'point_name': 'plc1', 'point_device_address': 102, 'point_address': 'DB15,INT0', 'point_scale': '1'}
    dict_point['plc2'] = {'point_writable': True, 'point_name': 'plc2', 'point_device_address': 102, 'point_address': 'DB15,INT1', 'point_scale': '1'}
    dict_point['plc3'] = {'point_writable': True, 'point_name': 'plc3', 'point_device_address': 102, 'point_address': 'DB3,BOOL4.0', 'point_scale': '1'}
    dict_point['plc4'] = {'point_writable': True, 'point_name': 'plc4', 'point_device_address': 102, 'point_address': 'DB15,WORD5', 'point_scale': '1'}
    dict_point['plc5'] = {'point_writable': True, 'point_name': 'plc5', 'point_device_address': 102, 'point_address': 'DB15,DWORD22', 'point_scale': '1'}
    dict_point['plc6'] = {'point_writable': True, 'point_name': 'plc6', 'point_device_address': 102, 'point_address': 'DB3,INT28', 'point_scale': '1'}
    dict_point['plc7'] = {'point_writable': True, 'point_name': 'plc7', 'point_device_address': 102, 'point_address': 'DB15,REAL38', 'point_scale': '1'}
    dict_point['plc8'] = {'point_writable': True, 'point_name': 'plc8', 'point_device_address': 102, 'point_address': 'DB15,INT42', 'point_scale': '1'}
    dict_point['plc9'] = {'point_writable': True, 'point_name': 'plc9', 'point_device_address': 102, 'point_address': 'DB3,WORD44', 'point_scale': '1'}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': 102, 'point_address': 'I0.0', 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': 102, 'point_address': 'Q0.0', 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': 102, 'point_address': 'MW300', 'point_scale': '1'}
    dict_point['plc13'] = {'point_writable': True, 'point_name': 'plc13', 'point_device_address': 102, 'point_address': 'M5.7', 'point_scale': '1'}

    client = IOTPlcS7(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            for name, point in dict_point.items():
                point['point_value'] = f"{random.randint(1, 100)}"
            client.simulate(points=dict_point)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_read():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500}
    dict_point = {}
    dict_point['plc1'] = {'point_writable': True, 'point_name': 'plc1', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT0', 'point_scale': '1'}
    dict_point['plc2'] = {'point_writable': True, 'point_name': 'plc2', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT1', 'point_scale': '1'}
    dict_point['plc3'] = {'point_writable': True, 'point_name': 'plc3', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB3,BOOL4.0', 'point_scale': '1'}
    dict_point['plc4'] = {'point_writable': True, 'point_name': 'plc4', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,WORD5', 'point_scale': '1'}
    dict_point['plc5'] = {'point_writable': True, 'point_name': 'plc5', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,DWORD22', 'point_scale': '1'}
    dict_point['plc6'] = {'point_writable': True, 'point_name': 'plc6', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB3,INT28', 'point_scale': '1'}
    dict_point['plc7'] = {'point_writable': True, 'point_name': 'plc7', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,REAL38', 'point_scale': '1'}
    dict_point['plc8'] = {'point_writable': True, 'point_name': 'plc8', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT42', 'point_scale': '1'}
    dict_point['plc9'] = {'point_writable': True, 'point_name': 'plc9', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB3,WORD44', 'point_scale': '1'}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'I0.0', 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'Q0.0', 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'MW300', 'point_scale': '1'}
    dict_point['plc13'] = {'point_writable': True, 'point_name': 'plc13', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'M5.7', 'point_scale': '1'}
    dict_point['plc14'] = {'point_writable': True, 'point_name': 'plc14', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT10', 'point_scale': '1'}
    dict_point['plc15'] = {'point_writable': True, 'point_name': 'plc15', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT11', 'point_scale': '1'}
    dict_point['plc16'] = {'point_writable': True, 'point_name': 'plc16', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT12', 'point_scale': '1'}
    dict_point['plc17'] = {'point_writable': True, 'point_name': 'plc17', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT13', 'point_scale': '1'}
    dict_point['plc18'] = {'point_writable': True, 'point_name': 'plc18', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT14', 'point_scale': '1'}
    dict_point['plc19'] = {'point_writable': True, 'point_name': 'plc19', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT15', 'point_scale': '1'}
    dict_point['plc20'] = {'point_writable': True, 'point_name': 'plc20', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT16', 'point_scale': '1'}
    dict_point['plc21'] = {'point_writable': True, 'point_name': 'plc121', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB15,INT17', 'point_scale': '1'}

    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_read_200():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500}
    dict_point = {}
    dict_point['PMPower_DHU_B1_4F_13'] = {'point_writable': True, 'point_name': 'PMPower_DHU_B1_4F_13', 'point_device_address': '192.168.1.184/102/0/1/5', 'point_address': 'DB1,REAL3000', 'point_scale': '1'}
    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_read1():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500}
    dict_point = {}
    dict_point['plc1'] = {'point_writable': True, 'point_name': 'plc1', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB1,INT1', 'point_scale': '1'}

    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_read2():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500, 'library': r'D:\UM\code\core\snap7.dll'}
    dict_point = {}
    dict_point['plc1'] = {'point_writable': True, 'point_name': 'plc1', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB1,BYTE24', 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB1,BYTE25', 'point_scale': '1'}
    dict_point['plc2'] = {'point_writable': True, 'point_name': 'plc2', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB1,INT24', 'point_scale': '1'}
    dict_point['plc31'] = {'point_writable': True, 'point_name': 'plc31', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB1,X24.1', 'point_scale': '1'}
    dict_point['plc3'] = {'point_writable': True, 'point_name': 'plc3', 'point_device_address': '127.0.0.1/102/0/1', 'point_address': 'DB1,X24.2', 'point_scale': '1'}

    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
            client.write(values={'plc3': 1})
            print(client.read())
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_read_200s():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 1000}
    dict_point = {}
    dict_point['M1'] = {'point_writable': True, 'point_name': 'M1', 'point_device_address': '192.168.2.113/102/0/0/2/3', 'point_address': 'MW1', 'point_scale': '1'}
    dict_point['DB1'] = {'point_writable': True, 'point_name': 'DB1', 'point_device_address': '192.168.2.113/102/0/0/2/3', 'point_address': 'DB1,WORD1', 'point_scale': '1'}
    dict_point['M1.0'] = {'point_writable': True, 'point_name': 'M1.0', 'point_device_address': '192.168.2.113/102/0/0/2/3', 'point_address': 'M1.0', 'point_scale': '1'}
    dict_point['DB1.0'] = {'point_writable': True, 'point_name': 'DB1.0', 'point_device_address': '192.168.2.113/102/0/0/2/3', 'point_address': 'DB1,BOOL1.0', 'point_scale': '1'}

    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_connect_plc():

    client = IOTPlcS7(configs={'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 1500, 'library': r'D:\UM\code\core\snap7.dll'}, points={})
    client.logging(call_logging=logging_print)
    print(client.discover(version=[2], ip='192.168.2.113', port=102))


def test_rw_200s():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 1000}
    dict_point = {}
    dict_point['M1'] = {'point_writable': True, 'point_name': 'M1', 'point_device_address': '20.25.34.47/102/0/1/2/3', 'point_address': 'DB1,BOOL3000.1', 'point_scale': '1'}

    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
            client.write(values={'M1': 0})
            print(client.read())
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_rw_smart200():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 1000}
    dict_point = {}
    dict_point['V0'] = {'point_writable': True, 'point_name': 'V0', 'point_device_address': '192.168.0.11/102/0/0/2/2', 'point_address': 'DB1,REAL116', 'point_scale': '1'}

    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


test_rw_smart200()