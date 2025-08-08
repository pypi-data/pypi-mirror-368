import time
import random
from threading import Thread
from robertcommondriver.system.iot.iot_opcda import IOTOPCDA, PumpWaitingMessages


def logging_print(**kwargs):
    print(kwargs)


def test_read_write():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        'host': 'localhost',  # 'host': '192.168.1.36:8804', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'action': '',
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}
    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int', 'point_tag': '213Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['static_int1'] = {'point_writable': True, 'point_name': 'static_int1', 'point_tag': 'Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4', 'point_type': '', 'point_description': ''}
    dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': 'Random.String', 'point_type': '', 'point_description': ''}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            # print(client.ping())
            reuslts = client.read()
            print(reuslts)
            time.sleep(4)
            continue

            print(client.write(values={'static_int1': random.randint(1,10), 'static_int': random.randint(1,10)}))

            print(client.info())
        except Exception as e:
            client.close()
            print(e.__str__())
        time.sleep(4)


def test_read_write_service():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        'host': '192.168.1.40:8810',  # 'host': '192.168.1.36:8804', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'action': '',
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}
    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int', 'point_tag': '213Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['static_int1'] = {'point_writable': True, 'point_name': 'static_int1', 'point_tag': 'Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4', 'point_type': '', 'point_description': ''}
    dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': 'Random.String', 'point_type': '', 'point_description': ''}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            # print(client.ping())
            reuslts = client.read()
            print(reuslts)
            time.sleep(4)
            continue

            print(client.write(values={'static_int1': random.randint(1,10), 'static_int': random.randint(1,10)}))

            print(client.info())
        except Exception as e:
            client.close()
            print(e.__str__())
        time.sleep(4)


def test_read_write_service5():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        'host': '192.168.1.104:8810',  # 'host': '192.168.1.40:8810', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'action': '',
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}
    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int', 'point_tag': '213Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['static_int1'] = {'point_writable': True, 'point_name': 'static_int1', 'point_tag': 'Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4', 'point_type': '', 'point_description': ''}
    dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': 'Random.String', 'point_type': '', 'point_description': ''}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            # print(client.ping())
            reuslts = client.read()
            print(reuslts)
            time.sleep(4)
            continue

            print(client.write(values={'static_int1': random.randint(1,10), 'static_int': random.randint(1,10)}))

            print(client.info())
        except Exception as e:
            client.close()
            print(e.__str__())
        time.sleep(4)


def test_scan():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        'host': 'localhost',  # 'host': '192.168.1.36:8804', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    # print(f"ping: {client.ping()}")
    #print(f"discover: {client.discover()}")
    result = client.scan(path='*', include_property=True)
    print(f"scan: {result}")
    time.sleep(4)


def test_read_wincc():
    dict_config = {
        'server': 'test_read_wincc',
        'host': 'localhost',  # 'host': '192.168.1.40:8810', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'action': '',
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}
    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int', 'point_tag': 'test_read_wincc', 'point_type': 'real', 'point_description': ''}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            reuslts = client.read()
            print(reuslts)
        except Exception as e:
            client.close()
            print(e.__str__())
        time.sleep(4)


def pump_wait_msg():
    while True:
        try:
            if True:
                PumpWaitingMessages()
                continue
        except Exception as e:
            pass
        time.sleep(0.01)


def test_sub():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        'host': '192.168.1.12:8810',  # 'host': '192.168.1.36:8804', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'action': '',
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}
    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int', 'point_tag': 'Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['static_int2'] = {'point_writable': True, 'point_name': 'static_int2', 'point_tag': 'Bucket Brigade.Int2', 'point_type': '', 'point_description': ''}
    dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4', 'point_type': '', 'point_description': ''}
    dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': 'Random.String', 'point_type': '', 'point_description': ''}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    #Thread(target=pump_wait_msg, name="opcda pump", daemon=True).start()

    while True:
        try:
            reuslts = client.read()
            print(reuslts)
            while True:
                print(client.read())
                time.sleep(0.1)
            time.sleep(4)
        except Exception as e:
            client.close()
            print(e.__str__())
        time.sleep(4)


test_sub()
