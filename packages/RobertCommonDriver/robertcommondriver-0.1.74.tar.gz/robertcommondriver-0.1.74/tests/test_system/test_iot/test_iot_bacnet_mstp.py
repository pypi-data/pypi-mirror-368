import time
from robertcommondriver.system.iot.iot_bacnet_mstp import IOTBacnetMSTP


def logging_print(**kwargs):
    print(kwargs)


def test_read():

    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 65,  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'timeout': 5  # 超时时间
    }

    dict_point = {
                  '6_4_2_analogValue_2': {'point_name': '6_4_2_analogValue_2', 'index': 3, 'point_writable': 'True',
                                          'point_device_address': '192.168.1.172:47808/160', 'point_type': 1,
                                          'point_property': 'presentValue', 'point_address': 3,
                                          'point_description': '', 'objectName': 'Random-604-2', 'presentValue': '2.0'},
                  }

    dict_point1 = {'192_168_1_184_47808_6_2_602_2_1': {'point_name': '192_168_1_184_47808_6_2_602_2_1', 'index': 0,
                                                      'point_writable': 'True',
                                                      'point_device_address': '6:2/602/192.168.1.184:47808',
                                                      'point_type': 2, 'point_property': 'presentValue',
                                                      'point_address': 1, 'description': 'None', 'point_value': '1.0',
                                                      'object_name': 'Random-602-1'}
                  }

    points = {'6_4_1_analogValue_1': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.171', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_12': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_13': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 2, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_14': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 3, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_15': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_16': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 5, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_17': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 6, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_18': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 7, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_19': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 8, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_110': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 9, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_111': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 10, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_112': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 11, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_113': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 12, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_114': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 13, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_115': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 14, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_116': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 15, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_117': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 16, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_118': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 17, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_119': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 18, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_120': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 0, 'point_property': 'presentValue', 'point_address': 19, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_121': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 1, 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_122': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 1, 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_123': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 1, 'point_property': 'presentValue', 'point_address': 2, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_124': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 1, 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_125': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 1, 'point_property': 'presentValue', 'point_address': 6, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_126': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 1, 'point_property': 'presentValue', 'point_address': 17, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_127': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 3, 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_128': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 3, 'point_property': 'presentValue', 'point_address': 2, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_129': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 3, 'point_property': 'presentValue', 'point_address': 3, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_130': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 3, 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_131': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 3, 'point_property': 'presentValue', 'point_address': 5, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_132': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 3, 'point_property': 'presentValue', 'point_address': 7, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_133': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_134': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 3, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_135': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_136': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 5, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_137': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 7, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_138': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 11, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_139': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 13, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_140': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 4, 'point_property': 'presentValue', 'point_address': 14, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_141': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 13, 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_142': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 14, 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              }

    client = IOTBacnetMSTP(configs = dict_config, points= points)
    client.logging(call_logging=logging_print)
    while True:
        try:

            results = client.read()
            print(results)


        except Exception as e:
            print(e.__str__())
        time.sleep(4)


def test_discover():
    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 65,  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'timeout': 5  # 超时时间
    }

    client = IOTBacnetMSTP(configs=dict_config, points={})
    client.logging(call_logging=logging_print)
    while True:
        try:

            results = client.discover()
            print(results)


        except Exception as e:
            print(e.__str__())
        time.sleep(4)


def test_scan():
    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 65,  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'timeout': 5  # 超时时间
    }

    client = IOTBacnetMSTP(configs = dict_config, points={})
    client.logging(call_logging=logging_print)
    while True:
        try:
            results = client.scan(address='6:4/604/192.168.1.184')
            # print(client.scan())
            print(results)
        except Exception as e:
            print(e.__str__())
        time.sleep(4)


def test_read_write():

    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 65,  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'timeout': 5  # 超时时间
    }

    dict_point = {
                  '6_4_2_analogValue_2': {'point_name': '6_4_2_analogValue_2', 'index': 3, 'point_writable': 'True',
                                          'point_device_address': '192.168.1.172:47808/160', 'point_type': 1,
                                          'point_property': 'presentValue', 'point_address': 1,
                                          'point_description': '', 'objectName': 'Random-604-2', 'presentValue': '2.0'},
                  }

    dict_point1 = {'192_168_1_184_47808_6_2_602_2_1': {'point_name': '192_168_1_184_47808_6_2_602_2_1', 'index': 0,
                                                      'point_writable': 'True',
                                                      'point_device_address': '192.168.1.184/2603/192.168.1.184:47808',
                                                      'point_type': 2, 'point_property': 'presentValue',
                                                      'point_address': 3, 'description': 'None', 'point_value': '1.0',
                                                      'object_name': 'Random-602-1'}
                  }


    client = IOTBacnetMSTP(configs = dict_config, points= dict_point1)
    client.logging(call_logging=logging_print)
    while True:
        try:

            results = client.read()
            print(results)

            #print(client.write(values={'192_168_1_184_47808_6_2_602_2_1': 2}))

        except Exception as e:
            print(e.__str__())
        time.sleep(4)


def test_read_write_mstp():
    dict_config = {
        'address': 'COM2/38400',  # bacnet server ip(绑定网卡)
        'identifier': 3,  # bacnet server identifier
        'vendor_identifier': 15,  # bacnet server vendor
        'timeout': 5,  # 超时时间
        'retry': 2,
        'whois': False,
        'multi_read': 20,  # bacnet 批量读取个数
        'segmentation': 65,  # bacnet server segmentation
    }

    dict_point1 = {'AV_1': {'point_name': 'AV_1',  'point_writable': 'True', 'point_device_address': '107', 'point_type': 2, 'point_property': 'presentValue', 'point_address': 1},
                   'AV_2': {'point_name': 'AV_2',  'point_writable': 'True', 'point_device_address': '107', 'point_type': 2, 'point_property': 'presentValue', 'point_address': 2}}

    client = IOTBacnetMSTP(configs=dict_config, points=dict_point1)
    client.logging(call_logging=logging_print)
    while True:
        try:

            results = client.read()
            print(results)


        except Exception as e:
            print(e.__str__())
        time.sleep(4)


test_read_write()