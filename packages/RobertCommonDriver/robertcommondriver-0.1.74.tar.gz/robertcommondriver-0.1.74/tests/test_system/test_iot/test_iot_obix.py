import time

from robertcommondriver.system.iot.iot_obix import IOTObix
from robertcommonbasic.basic.data.csv import values_to_csv


def logging_print(content):
    print(content)


def test_ping():
    client = IOTObix(configs={'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8082', 'timeout': 10}, points={})
    print(client.ping())
    print()


def test_get():
    point_dict = {}
    point_dict['test1'] = {'point_name': 'test1', 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_2/points/CHW_ENT','point_type': 'real', 'point_writable': False,  'point_description': ''}
    point_dict['test2'] = {'point_name': 'test2', 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_2/points/CHW_SPT1','point_type': 'real', 'point_writable': False,  'point_description': ''}
    driver = IOTObix(configs={'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'timeout': 10}, points=point_dict)
    while True:
        if driver.ping() == True:
            result = driver.read()  # 读取点
            print(result)
        time.sleep(10)


def test_read():
    points = {'Services_AlarmService_Add': {'point_name': 'Services_AlarmService_Add', 'point_writable': True,
                                            'point_url': '/obix/config/Services/AlarmService/Add/',
                                            'point_type': 'real',
                                            'point_description': '500.0 {ok}', 'point_value': '500.0'},
              'Services_AlarmService_TotalAlarm': {'point_name': 'Services_AlarmService_TotalAlarm',
                                                   'point_writable': True,
                                                   'point_url': '/obix/config/Services/AlarmService/TotalAlarm1/',
                                                   'point_type': 'real', 'point_description': '500.0 {ok} @ 10',
                                                   'point_value': '500.0'},
              'Services_AlarmService_test': {'point_name': 'Services_AlarmService_test', 'point_writable': True,
                                             'point_url': '/obix/config/Services/AlarmService/test/',
                                             'point_type': 'bool',
                                             'point_description': 'false {overridden,unackedAlarm} @ 8',
                                             'point_value': 'false'}}
    driver = IOTObix(configs={'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'reltime': 'PT30M', 'filiter': ['obix:Point'], 'timeout': 10}, points=points)
    driver.logging(call_logging=logging_print)
    while True:
        if driver.ping() == True:
            result = driver.read()  # 读取点
            print(result)
        time.sleep(10)


def test_read_queen():
    points = {'Bacnet_3205Q_T1_L02_AHUT1_2d02_2d02_i_OA_Temp': {'point_name': 'Bacnet_3205Q_T1_L02_AHUT1_2d02_2d02_i_OA_Temp', 'point_writable': True,
                                            'point_url': '/obix/config/Drivers/BacnetAwsNetwork/$3205Q_T1/L02/AHUT1$2d02$2d02/points/i_OA_Temp/',
                                            'point_type': 'real',
                                            'point_description': '500.0 {ok}', 'point_value': '500.0'},
              'Bacnet_3205Q_T1_L02_AHUT1_2d02_2d02_i_OA_Temp1': {
                  'point_name': 'Bacnet_3205Q_T1_L02_AHUT1_2d02_2d02_i_OA_Temp1', 'point_writable': True,
                  'point_url': '/obix/config/Drivers/BacnetAwsNetwork/$3205Q_T1/L02/AHUT1$2d02$2d02/points/i_OA_Temp12/',
                  'point_type': 'real',
                  'point_description': '500.0 {ok}', 'point_value': '500.0'},
              }
    driver = IOTObix(configs={'username': 'obix_queen', 'password': 'C0ll1ers!2023', 'url': 'https://58.28.208.154:52443', 'reltime': 'PT30M', 'filiter': ['obix:Point'], 'timeout': 10}, points=points)
    driver.logging(call_logging=logging_print)
    while True:
        try:
            if driver.ping() is True:
                result = driver.read()  # 读取点
                print(result)
        except Exception as e:
            print(e.__str__())
        time.sleep(35)


def test_scan():
    driver = IOTObix(configs={'username': 'IndustryTech', 'password': 'IndustryTech25!', 'url': 'http://144.6.60.143/obix/config/Drivers/NiagaraNetwork/MetCentre_Retail_2/points/Level_09/VAV_05/', 'filiter': ['obix:Point'], 'timeout': 20}, points={})
    driver.logging(call_logging=logging_print)
    if driver.ping() is True:
        result = driver.scan(limit=20)  # 读取点
        values_to_csv(result, 'queen1.csv', False, True)


test_scan()
