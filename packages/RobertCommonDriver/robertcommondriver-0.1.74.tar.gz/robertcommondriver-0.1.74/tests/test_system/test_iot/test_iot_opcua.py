import time
import random
from robertcommondriver.system.iot.iot_opcua import IOTOPCUA


def logging_print(**kwargs):
    print(kwargs)


def test_discover():

    client = IOTOPCUA(configs={}, points={})
    client.logging(call_logging=logging_print)
    result = client.discover(target='opc.tcp://localhost:4841')
    print(result)


def test_scan():
    dict_config = {
        'endpoint': 'opc.tcp://localhost:4841/freeopcua/server/', #'opc.tcp://192.168.1.182:9503/freeopcua/server/',          #url
        'timeout': 4,
        'security': '',                  #
        'auth': {},          #
        'subscript_add': 1000,
        'subscript_interval': 1000,
    }

    client = IOTOPCUA(configs=dict_config, points={})
    client.logging(call_logging=logging_print)
    result = client.scan()
    print(result)


def test_read():
    dict_config = {
        'endpoint': 'opc.tcp://localhost:4841/freeopcua/server/',
        'timeout': 4,
        'security': '',  #
        'auth': {},  #
        'subscript_add': 1000,
        'subscript_interval': 500,
    }

    dict_point = {}
    dict_point['opcua1'] = {'point_writable': True, 'point_name': 'opcua1', 'point_node_id': 'ns=2;i=2', 'point_scale': '1'}
    dict_point['opcua'] = {'point_writable': True, 'point_name': 'opcua2', 'point_node_id': 'ns=2;i=13', 'point_scale': '1'}
    dict_point['opcua3'] = {'point_writable': True, 'point_name': 'opcua3', 'point_node_id': 'i=2256', 'point_scale': '1'}

    client = IOTOPCUA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read()
            print(result)
        except Exception as e:
            print(e.__str__())
        time.sleep(5)


def test_write():
    dict_config = {
        'endpoint': 'opc.tcp://localhost:4841/freeopcua/server/',
        'timeout': 4,
        'security': '',  #
        'auth': {},  #
        'subscript_add': 1000,
        'subscript_interval': 500,
    }

    dict_point = {}
    dict_point['opcua1'] = {'point_writable': True, 'point_name': 'opcua1', 'point_node_id': 'ns=2;i=2', 'point_scale': '1'}
    dict_point['opcua'] = {'point_writable': True, 'point_name': 'opcua2', 'point_node_id': 'ns=2;i=13', 'point_scale': '1'}
    dict_point['opcua3'] = {'point_writable': True, 'point_name': 'opcua3', 'point_node_id': 'i=2256', 'point_scale': '1'}

    client = IOTOPCUA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.write(values={'opcua': 2.1})
            print(result)
        except Exception as e:
            print(e.__str__())
        time.sleep(1)


def test_simulate():
    dict_config = {
        'endpoint': 'opc.tcp://0.0.0.0:4841/freeopcua/server/',
        'name': 'Robert OPC UA Server',  #
        'root': 'Robert1'
    }

    dict_point = {}
    dict_point['opcua1'] = {'point_writable': True, 'point_name': 'opcua1', 'point_node_id': 'ns=2;s=ModbusOPC.OPC1.qeq', 'point_node_path': '', 'point_scale': '1'}
    dict_point['opcua'] = {'point_writable': True, 'point_name': 'opcua2', 'point_node_id': 'ns=2;s=通道1.qwq', 'point_node_path': 'group2/group3/point2', 'point_scale': '1'}

    client = IOTOPCUA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        for name, point in dict_point.items():
            point['point_value'] = f"{random.randint(1, 100)}"
        client.simulate(points=dict_point)
        time.sleep(1)


def test_read_list():
    dict_config = {
        'endpoint': 'opc.tcp://20.25.34.201:4840',
        'timeout': 4,
        'security': '',  #
        'auth': {},  #
        'subscript_add': 1000,
        'subscript_interval': 500,
    }

    dict_point = {}
    dict_point['opcua1'] = {'point_writable': True, 'point_name': 'opcua1', 'point_node_id': 'ns=6;s=Arp.Plc.Eclr/PCHP_S_Para.A_Flow_AddSP', 'point_scale': '_in(v,1)'}

    client = IOTOPCUA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read()
            print(result)
        except Exception as e:
            print(e.__str__())
        time.sleep(5)


def test_rw_list():
    dict_config = {
        'endpoint': 'opc.tcp://20.25.34.201:4840',
        'timeout': 4,
        'security': '',  #
        'auth': {},  #
        'subscript_add': 1000,
        'subscript_interval': 500,
    }

    dict_point = {}
    dict_point['opcua1'] = {'point_writable': True, 'point_name': 'opcua1', 'point_node_id': '20.25.34.201:4840', 'point_scale': '1'}

    client = IOTOPCUA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read()
            print(result)
        except Exception as e:
            print(e.__str__())
        time.sleep(5)


test_rw_list()
