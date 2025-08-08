import time
import struct
import logging
from typing import Optional
from threading import Lock
from serial import Serial
from socket import timeout as socket_timeout
from modbus_tk import defines as modbus_tk_defines
from modbus_tk.modbus_tcp import TcpMaster, TcpServer
from modbus_tk.modbus_rtu import RtuMaster, RtuServer
from modbus_tk.hooks import install_hook


from typing import List, Dict, Any
from .base import IOTBaseCommon, IOTDriver, IOTSimulateObject

'''
    pip install modbus-tk==1.1.2
'''

'''
    地址不偏移
    
    type
        NONE = -1
        BOOL = 0
        BOOL_ARRAY = 1
        INT8 = 2
        INT8_ARRAY = 3
        UINT8 = 4
        UINT8_ARRAY = 5
        INT16 = 6
        INT16_ARRAY = 7
        UINT16 = 8
        UINT16_ARRAY = 9
        INT32 = 10
        INT32_ARRAY = 11
        UINT32 = 12
        UINT32_ARRAY = 13
        INT64 = 14
        INT64_ARRAY = 15
        UINT64 = 16
        UINT64_ARRAY = 17
        FLOAT = 18
        FLOAT_ARRAY = 19
        DOUBLE = 20
        DOUBLE_ARRAY = 21
        STRING = 22
        HEX_STRING = 23
        BYTE_ARRAY = 24
        
    order
        ABCD = 0        # 按照顺序排序   Modbus 十进制数字123456789或十六进制07 5B CD 15 07 5B CD 15
        BADC = 1        # 按照单字反转
        CDAB = 2        # 按照双字反转 (大部分PLC默认排序方法)
        DCBA = 3        # 按照倒序排序
'''


class IOTModbus(IOTDriver):

    # modbus read/write unit
    class ModbusReadUnit:

        def __init__(self, address: str, slave_id: int, fun_code: int, start: int, end: int, multi_read: int):
            self.address = address
            self.slave_id = slave_id
            self.start = start
            self.end = end
            self.fun_code = fun_code
            self.multi_read = multi_read

            self.full_flag = False
            self.modbus_point_list = []

        def __str__(self):
            return f"{self.address}_{self.slave_id}_{self.fun_code}"

        @property
        def get_tag(self) -> str:
            return f"{self.address}_{self.slave_id}_{self.fun_code}_{self.start}"

        def set_full_flag(self):
            self.full_flag = True

        @property
        def get_full_flag(self):
            return self.full_flag

        @property
        def get_modbus_id(self):
            return self.slave_id

        @property
        def get_modbus_address(self):
            return self.address

        @property
        def get_modbus_start(self):
            return self.start

        @property
        def get_modbus_end(self):
            return self.end

        @property
        def get_modbus_fun(self):
            return self.fun_code

        @property
        def get_modbus_multi_read(self):
            return self.multi_read

        def set_modbus_end(self, end):
            self.end = end

    class ModbusBlockUnit:

        def __init__(self, name: str, id: int, fun_code: int, start: int, end: int):
            self.name = name
            self.id = id
            self.fun_code = fun_code
            self.start = start
            self.end = end

        def __str__(self):
            return f"{self.name}"

        @property
        def get_id(self):
            return self.id

        @property
        def get_address(self):
            return self.start

        @property
        def get_start(self):
            return self.start

        @property
        def get_end(self):
            return self.end

        @property
        def get_fun(self):
            return self.fun_code

        @property
        def get_size(self):
            return self.end - self.start + 1

    class ModbusClientLock:
        """连接锁"""
        def __init__(self, client):
            self.client = client
            self.lock = Lock()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.clients = {}
        self.servers = {}
        self.lock_read_write_handler = Lock()  # 默认运行更新 如果有修改值等修改完再更新
        self.handle_write_callback = None   # 设值回调

        log_modbus = logging.getLogger('modbus_tk')
        if log_modbus:
            log_modbus.setLevel(logging.ERROR)
            log_modbus.disabled = True

    def exit(self):
        self.exit_flag = True

        address = list(self.clients.keys())
        for address in address:
            if address in self.clients.keys():
                self._release_client(address)

        for address, server in self.servers.items():
            self._release_server(address)
        self.reinit()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''}])
            if mode == 0:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '192.168.1.184/502', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '0.0.0.0/502', 'enum': [], 'tip': ''})
            templates.extend([
                {'required': True, 'name': '子站号' if lan == 'ch' else 'slave id'.upper(), 'code': 'point_slave_id', 'type': 'int', 'default': '1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '功能码' if lan == 'ch' else 'fun code'.upper(), 'code': 'point_fun_code', 'type': 'int', 'default': '1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '点地址' if lan == 'ch' else 'address'.upper(), 'code': 'point_address', 'type': 'int', 'default': '1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '点类型' if lan == 'ch' else 'type'.upper(), 'code': 'point_data_type', 'type': 'int', 'default': '1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '点长度' if lan == 'ch' else 'length'.upper(), 'code': 'point_data_length', 'type': 'int', 'default': '1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '字节顺序' if lan == 'ch' else 'order'.upper(), 'code': 'point_data_order', 'type': 'int', 'default': '0', 'enum': [0, 1, 2, 3], 'tip': '0-abcd; 1-badc; 2-cdab; 3-dcba'},
                {'required': False, 'name': '点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''}])
            if mode == 0:
                templates.append({'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': '点值' if lan == 'ch' else 'value'.upper(), 'code': 'point_value', 'type': 'int', 'default': 0, 'enum': [], 'tip': ''})
            templates.extend([
                {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}

            ])
        elif type == 'config':
            if mode == 0:
                templates.extend([
                    {'required': True, 'name': '批量读取个数' if lan == 'ch' else 'Multi Read', 'code': 'multi_read', 'type': 'int', 'default': 100, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '命令间隔(s)' if lan == 'ch' else 'Cmd Interval(s)', 'code': 'cmd_interval', 'type': 'float', 'default': 0.3, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '超时(s)' if lan == 'ch' else 'Timeout(s)', 'code': 'timeout', 'type': 'int', 'default': 5, 'enum': [], 'tip': ''},
                ])

        return templates

    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        names = kwargs.get('names', list(self.points.keys()))
        self.update_results(names, True, None)
        read_items = {}
        for name in names:
            point = self.points.get(name)
            if point:
                device_address = point.get('point_device_address')
                slave_id = point.get('point_slave_id')
                fun_code = point.get('point_fun_code')
                address = point.get('point_address')
                data_type = point.get('point_data_type')
                data_length = point.get('point_data_length', 0)
                data_order = point.get('point_data_order', 0)
                if device_address is not None and slave_id is not None and fun_code is not None and address is not None and data_type is not None and data_length is not None:
                    target_address = device_address
                    if target_address not in read_items.keys():
                        read_items[target_address] = {}
                    if slave_id not in read_items[target_address].keys():
                        read_items[target_address][slave_id] = {}
                    if fun_code not in read_items[target_address][slave_id].keys():
                        read_items[target_address][slave_id][fun_code] = []
                    size = IOTBaseCommon.DataTransform.get_type_word_size(data_type, data_length)
                    for i in range(size):
                        p_address = address+i
                        if p_address not in read_items[target_address][slave_id][fun_code]:
                            read_items[target_address][slave_id][fun_code].append(p_address)

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                device_address = point.get('point_device_address')
                slave_id = point.get('point_slave_id')
                fun_code = point.get('point_fun_code')
                address = point.get('point_address')
                data_type = point.get('point_data_type')
                data_length = point.get('point_data_length', 0)
                data_order = point.get('point_data_order', 0)
                if device_address is not None and slave_id is not None and fun_code is not None and address is not None and data_type is not None and data_length is not None:
                    value = self.get_value(name, device_address, slave_id, fun_code, address, data_length, data_type, data_order)
                    if value is not None:
                        self.update_results(name, True, value)
            else:
                self.update_results(name, False, 'UnExist')
        return self.get_results(**kwargs)

    def write(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        values = kwargs.get('values', {})
        for name, value in values.items():
            point = self.points.get(name)
            result = [False, 'Unknown']
            if point:
                device_address = point.get('point_device_address')
                slave_id = point.get('point_slave_id')
                fun_code = point.get('point_fun_code')
                address = point.get('point_address')
                data_type = point.get('point_data_type')
                data_length = point.get('point_data_length')
                data_order = point.get('point_data_order', 0)
                if device_address is not None and slave_id is not None and fun_code is not None and address is not None and data_type is not None and data_length is not None:
                    self._write(device_address, slave_id, fun_code, address, data_type, data_length, data_order, value)
                    result = self.get_device_property(device_address, IOTModbus.gen_key(slave_id, fun_code, address), [self.get_write_quality, self.get_write_result])
                else:
                    result = [False, 'Invalid Params']
            else:
                result = [False, 'Point UnExist']
            results[name] = result
            if result[0] is not True:
                self.logging(content=f"write value({name}) fail({result[1]})", level='ERROR', source=name, pos=self.stack_pos)
        return results

    def ping(self, **kwargs) -> bool:
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        return True

    def simulate(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        self.points = kwargs.get('points', {})
        self.handle_write_callback = kwargs.get('handle_write_callback', None)
        self.logging(content=f"simulate({len(self.points)})", pos=self.stack_pos)
        server_objects = {}
        write_points = {}
        for name, point in self.points.items():
            if point:
                device_address = point.get('point_device_address')
                slave_id = point.get('point_slave_id')
                fun_code = point.get('point_fun_code')
                address = point.get('point_address')
                data_type = point.get('point_data_type')
                data_length = point.get('point_data_length')
                if device_address is not None and slave_id is not None and fun_code is not None and address is not None and data_type is not None and data_length is not None:
                    target_address = device_address
                    if target_address not in server_objects.keys():
                        server_objects[target_address] = {}
                    if slave_id not in server_objects[target_address].keys():
                        server_objects[target_address][slave_id] = {}
                    if fun_code not in server_objects[target_address][slave_id].keys():
                        server_objects[target_address][slave_id][fun_code] = []
                    server_objects[target_address][slave_id][fun_code].append(IOTSimulateObject(**point))

        if len(server_objects) > 0:
            for address, slaves in server_objects.items():
                for id, codes in slaves.items():
                    for code, objects in codes.items():
                        if self._get_server(address) is not None:
                            self._create_objects(address, id, code, objects)

                            self._refresh_objects(address, id, code, objects)

            # 更新设定值
            if len(self.devices) > 0:
                for name, point in self.points.items():
                    device_address = point.get('point_device_address')
                    slave_id = point.get('point_slave_id')
                    fun_code = point.get('point_fun_code')
                    address = point.get('point_address')
                    data_type = point.get('point_data_type')
                    data_length = point.get('point_data_length', 0)
                    data_order = point.get('point_data_order', 0)
                    point_scale = point.get('point_scale')
                    if device_address is not None and slave_id is not None and fun_code is not None and address is not None and data_type is not None and data_length is not None:
                        point_value = self.get_value(name, device_address, slave_id, fun_code, address, data_length, data_type, data_order)
                        if point_value is not None:
                            if point_scale is None:
                                point_value = IOTBaseCommon.convert_value(point_value, 'set')
                            else:
                                point_scale = str(point_scale)
                                if point_scale in ['0', '1', '', 'None']:
                                    point_value = IOTBaseCommon.convert_value(point_value, 'set')
                                elif point_scale.startswith('bit('):
                                    point_value = point_value
                                else:
                                    point_value = IOTBaseCommon.convert_value(str(IOTBaseCommon.DataTools.format_value(point_value, point_scale, 3, True)), 'set')
                            write_points[name] = point_value

                if self.handle_write_callback and len(write_points) > 0:
                    with self.lock_read_write_handler:
                        self.handle_write_callback(write_points)
                self.devices = {}
        return write_points

    @staticmethod
    def gen_key(slave_id: int, fun_code: int, address: int) -> str:
        return f"{slave_id}_{fun_code}_{address}"

    def _combine_read_unit(self, modbus_unit, modbus_read_units: dict):
        read_units = modbus_read_units.get(modbus_unit.__str__())
        if read_units is not None:
            if modbus_unit.get_modbus_start == (read_units[-1].get_modbus_end + 1):
                if read_units[-1].get_modbus_end - read_units[-1].get_modbus_start + 1 >= self.configs.get('multi_read', 100):  # 超过连读上限
                    read_units[-1].set_full_flag()
                    modbus_read_units[modbus_unit.__str__()].append(modbus_unit)
                else:
                    read_units[-1].set_modbus_end(modbus_unit.get_modbus_end)
            elif modbus_unit.get_modbus_start == read_units[-1].get_modbus_end:
                read_units[-1].set_modbus_end(modbus_unit.get_modbus_end)
            else:
                modbus_read_units[modbus_unit.__str__()].append(modbus_unit)
        else:
            modbus_read_units[modbus_unit.__str__()] = [modbus_unit]

    def cread_read_units(self, address, slave_items: dict) -> dict:
        modbus_read_units = {}
        for slave_id, fun_codes in slave_items.items():
            for fun_code, p_address in fun_codes.items():
                p_address.sort()
                for addr in p_address:
                    self._combine_read_unit(self.ModbusReadUnit(address, slave_id, fun_code, addr, addr, self.configs.get('multi_read', 100)), modbus_read_units)
        return modbus_read_units

    def _get_address_info(self, device_address: str) -> dict:
        modbus_info = {}
        if len(device_address) > 0:
            if device_address.find('/dev/tty') == 0:  # linux
                info_list = device_address.split('|')
                if len(info_list) == 1:  # port
                    modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': 9600, 'parity': 'N', 'bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
                elif len(info_list) == 2:  # port/baudrate
                    modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': int(str(info_list[1])), 'parity': 'N', 'bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
                elif len(info_list) == 3:  # port/baudrate/parity
                    modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': int(str(info_list[1])), 'parity': str(info_list[2]), 'bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
            else:
                info_list = device_address.split('/')
                if len(info_list) == 1:  # IP or port
                    if IOTBaseCommon.check_ip(info_list[0]) is True:
                        modbus_info = {'type': 'tcp', 'host': str(info_list[0]), 'port': 502}
                    else:
                        modbus_info = {'type': 'tcp', 'port': int(str(info_list[0]))}
                elif len(info_list) == 2:  # IP/port   port/baudrate
                    if IOTBaseCommon.check_ip(info_list[0]) is True:
                        modbus_info = {'type': 'tcp', 'host': str(info_list[0]), 'port': int(str(info_list[1]))}
                    else:
                        modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': int(str(info_list[1])), 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': 0}
                elif len(info_list) == 3:  # port/baudrate/parity
                    modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': int(str(info_list[1])), 'parity': str(info_list[2]), 'bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
        return modbus_info

    def _get_client(self, address: str):
        client = self.clients.get(address)
        if client is None:
            modbus_info = self._get_address_info(address)
            if 'type' in modbus_info.keys():
                modbus_type = modbus_info['type']
                if modbus_type == 'tcp':
                    client = TcpMaster(host=modbus_info['host'], port=modbus_info['port'])
                    client.set_timeout(self.configs.get('timeout', 5))
                    self.clients[address] = self.ModbusClientLock(client)
                else:
                    modbus_com = modbus_info['port']  # com5 或/dev/tty0
                    if modbus_com.find('/dev/tty') == 0:
                        client = RtuMaster(Serial(port=modbus_com, baudrate=modbus_info['baudrate'], bytesize=modbus_info['bytesize'], parity=modbus_info['parity'], stopbits=modbus_info['stopbits'], xonxoff=modbus_info['xonxoff']))
                        client.set_timeout(self.configs.get('timeout', 5))
                    else:
                        if modbus_com.startswith('com') is False:
                            modbus_com = f"com{modbus_com}"
                        client = RtuMaster(Serial(port=modbus_com, baudrate=modbus_info['baudrate'], bytesize=modbus_info['bytesize'], parity=modbus_info['parity'], stopbits=modbus_info['stopbits'], xonxoff=modbus_info['xonxoff']))

                    client.set_timeout(self.configs.get('timeout', 5))
                    client.set_verbose(True)
                    self.clients[address] = self.ModbusClientLock(client)
        return self.clients.get(address)

    def _release_client(self, address: str):
        client = self.clients.get(address)
        try:
            if client:
                client.client.close()
        except Exception as e:
            pass
        finally:
            if address in self.clients.keys():
                del self.clients[address]

    def _change_fun_code(self, fun_code: int, **kwargs):
        if kwargs.get('mode', 0) == 0:  # read
            if fun_code == modbus_tk_defines.READ_HOLDING_REGISTERS or fun_code == modbus_tk_defines.WRITE_MULTIPLE_REGISTERS or fun_code == modbus_tk_defines.READ_WRITE_MULTIPLE_REGISTERS:
                fun_code = modbus_tk_defines.READ_HOLDING_REGISTERS
            elif fun_code == modbus_tk_defines.READ_COILS or fun_code == modbus_tk_defines.WRITE_SINGLE_COIL or fun_code == modbus_tk_defines.WRITE_MULTIPLE_COILS:
                fun_code = modbus_tk_defines.READ_COILS
        else:   # mode
            if fun_code == modbus_tk_defines.READ_HOLDING_REGISTERS or fun_code == modbus_tk_defines.WRITE_MULTIPLE_REGISTERS or fun_code == modbus_tk_defines.READ_WRITE_MULTIPLE_REGISTERS:
                if kwargs.get('length', 1) <= 1:
                    fun_code = modbus_tk_defines.WRITE_SINGLE_REGISTER
                else:
                    fun_code = modbus_tk_defines.WRITE_MULTIPLE_REGISTERS
            elif fun_code == modbus_tk_defines.READ_COILS or fun_code == modbus_tk_defines.WRITE_SINGLE_COIL or fun_code == modbus_tk_defines.WRITE_MULTIPLE_COILS:
                if kwargs.get('length', 1) <= 1:
                    fun_code = modbus_tk_defines.WRITE_SINGLE_COIL
                else:
                    fun_code = modbus_tk_defines.WRITE_MULTIPLE_COILS
        return fun_code

    def _send_read_cmd(self, address: str, slave_id: int, add_start: int, add_end: int, fun_code: int, process: Optional[str] = ''):
        err_msg = None
        start = time.time()
        try:
            fun_code = self._change_fun_code(fun_code)
            client = self._get_client(address)
            if client is not None:
                """
                    20240808
                        threadsafe_function: 保障线程安全（有的设备可能不支持同时对其进行读写操作）
                            lock 已经被当成了一个全局变量，后续无论是创建多少个 TcpMaster 的实例对象，lock 变量所指向的锁都是同一个。
                            Master.execute() 方法中会去建立 socket 链接，一旦有 1 个 device 链接时间过长，也将会导致其他的 device 通信或链接阻塞。
                            一般来说在使用时我们会在 Master.execute() 方法中显式的传递 threadsafe=False 的关键字参数，自己实现 lock 来解决同一 device 不能同时读写的问题。
                """
                with client.lock:
                    value_list = client.client.execute(slave_id, fun_code, add_start, add_end - add_start + 1, threadsafe=False)
                    for index in range(0, len(value_list)):
                        self.update_device(address, IOTModbus.gen_key(slave_id, fun_code, add_start + index), **self.gen_read_write_result(True, value_list[index]))
        except (socket_timeout, ConnectionRefusedError, ConnectionResetError) as e:  # connect
            err_msg = f"connect fail: {e.__str__()}"
            self._release_client(address)
        except Exception as e:  # other
            err_msg = f"read fail: {e.__str__()}"
        finally:
            self.logging(content=f"iot_modbus({address}) read{f'({process})' if process is not None else ''} ({slave_id}-{fun_code}-[{add_start}-{add_end}]) cost: {'{:.3f}'.format(time.time() - start)} {'success' if err_msg is None else f'fail({err_msg})'}", pos=self.stack_pos)
            if err_msg is not None:
                for i in range(add_start, add_end + 1):
                    self.update_device(address, IOTModbus.gen_key(slave_id, fun_code, i), **self.gen_read_write_result(False, err_msg))

    def _read_address(self, *args, **kwargs) -> dict:
        start = time.time()
        (address, slave_items) = args
        results = {}
        read_units = self.cread_read_units(address, slave_items)
        for k, modbus_units in read_units.items():
            for index, modbus_unit in enumerate(modbus_units):
                if modbus_unit.get_modbus_id >= 0 and 0 <= modbus_unit.get_modbus_start <= modbus_unit.get_modbus_end and 0 < modbus_unit.get_modbus_fun < 17:
                    self._send_read_cmd(modbus_unit.get_modbus_address, modbus_unit.get_modbus_id, modbus_unit.get_modbus_start, modbus_unit.get_modbus_end, modbus_unit.get_modbus_fun, f"{index + 1}/{len(modbus_units)}")
            self.delay(self.configs.get('cmd_interval', 0.3))
        self.logging(content=f"iot_modbus({address}) read: {len(slave_items)} group: {len(read_units)} cost: {'{:.2f}'.format(time.time() - start)}", pos=self.stack_pos)
        return results

    def _read(self, read_items: dict) -> dict:
        if len(read_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(read_items), f"{self}")
            for address, slaves in read_items.items():
                jobs.submit_task(self._read_address, address, slaves)
            return jobs.done()
        return {}
    
    @staticmethod
    def convert_value(length: int, type: int, order: int, values: list = []):
        pos = 0
        if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY.value:
            pos = length
        length = IOTBaseCommon.DataTransform.get_type_word_size(type, length)
        if len(values) == length:
            return IOTBaseCommon.DataTransform.convert_value(values, IOTBaseCommon.DataTransform.TypeFormat.UINT16, IOTBaseCommon.DataTransform.TypeFormat(type), pos=pos, format=IOTBaseCommon.DataTransform.DataFormat(order))
        return None
    
    @staticmethod
    def get_type_size(type: int, length: int = 0):
        return IOTBaseCommon.DataTransform.get_type_word_size(type, length)

    def get_value(self, name: str, address: str, slave_id: int, fun_code: int, start: int, length: int, type: int, order: int):
        try:
            values = []
            for i in range(IOTModbus.get_type_size(type, length)):
                key = IOTModbus.gen_key(slave_id, fun_code, start+i)
                [result, value] = self.get_device_property(address, key, [self.get_read_quality, self.get_read_result])
                if result is True:
                    if value is not None:
                        values.append(value)
                    else:
                        raise Exception(f"({key}) is none")
                else:
                    raise Exception(str(value))
            return IOTModbus.convert_value(length, type, order, values)
        except Exception as e:
            self.update_results(name, False, e.__str__())
        return None

    def _convert_value_to_vector(self, src_type: int, src_order: int, dst_type: int, value):
        if src_type == IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY.value:
            return value
        return IOTBaseCommon.DataTransform.convert_value(value, IOTBaseCommon.DataTransform.TypeFormat(src_type), IOTBaseCommon.DataTransform.TypeFormat(dst_type), format=IOTBaseCommon.DataTransform.DataFormat(src_order))

    def _write(self, address: str, slave_id: int, fun_code: int, start: int, type: int, length: int, order: int, value):
        err_msg = None
        try:
            client = self._get_client(address)
            if client is not None:
                with client.lock:
                    if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY.value:
                        v = client.client.execute(slave_id, self._change_fun_code(fun_code), start, 1, threadsafe=False)
                        bs = IOTBaseCommon.DataTransform.convert_value(v[0], IOTBaseCommon.DataTransform.TypeFormat.UINT16, IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat(order))
                        bs[length] = value
                        value = IOTBaseCommon.DataTransform.convert_value(bs, IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY, IOTBaseCommon.DataTransform.TypeFormat.UINT16, pos=0, format=IOTBaseCommon.DataTransform.DataFormat(order))

                    set_values = self._convert_value_to_vector(type, order, 8, value)
                    if set_values is not None:
                        if isinstance(set_values, list):
                            if len(set_values) <= 0:
                                raise Exception(f"invalid type({type})")
                            set_size = len(set_values)
                            set_values = set_values[0] if set_size == 1 else set_values
                        else:
                            set_size = 1

                        fun_write_code = self._change_fun_code(fun_code, mode=1, length=set_size)
                        self.logging(content=f"iot_modbus({address}) write ({slave_id}-{fun_write_code}-[{start}-{start + set_size}])-({value}/{set_values})", pos=self.stack_pos)
                        value_list = client.client.execute(slave_id, fun_write_code, start, output_value=set_values, threadsafe=False)
                        if len(value_list) == 2 and value_list[0] == start:
                            return self.update_device(address, IOTModbus.gen_key(slave_id, fun_code, start), **self.gen_read_write_result(True, None, False))
                    err_msg = 'Unknown'
        except (socket_timeout, ConnectionRefusedError, ConnectionResetError) as e:  # connect
            err_msg = f"connect fail: {e.__str__()}"
            self._release_client(address)
        except Exception as e:  # other
            err_msg = e.__str__()
        finally:
            if err_msg is not None:
                self.update_device(address, IOTModbus.gen_key(slave_id, fun_code, start), **self.gen_read_write_result(False, err_msg, False))

    def on_handle_set_write(self, device_address: str, slave_id: int, fun_code: int, start_address: int, values: list):
        """设值"""
        for i, value in enumerate(values):
            self.update_device(device_address, IOTModbus.gen_key(slave_id, self._change_fun_code(fun_code), start_address + i), **self.gen_read_write_result(True, value))

    def _get_server(self, address: str):
        server = self.servers.get(address, {}).get('server')
        if server is None:
            modbus_info = self._get_address_info(address)
            if 'type' in modbus_info.keys():
                modbus_type = modbus_info['type']
                if modbus_type == 'tcp':
                    server = TcpServer(address='0.0.0.0', port=modbus_info['port'])

                    def on_handle_write_multiple_coils_request(args, **kwargs):
                        (slave, request) = args
                        self.logging(content=f"on_handle_write_multiple_coils_request {IOTBaseCommon.DataTransform.format_bytes(request)}")
                        try:
                            # 解析请求数据
                            (_address, _quantity, _byte_count) = struct.unpack(">HHB", request[1:6])
                            values = []
                            for i in range(_byte_count):
                                byte_value = request[6 + i]
                                for bit in range(8):
                                    if (i * 8 + bit) < _quantity:
                                        values.append((byte_value >> bit) & 0x01)
                            self.on_handle_set_write(address, slave.get_id(), modbus_tk_defines.WRITE_MULTIPLE_COILS, _address, values)
                        except Exception as e:
                            self.logging(content=f"Handle write multiple coils error: {str(e)}", level='ERROR', pos=self.stack_pos)

                    def on_handle_write_multiple_registers_request(args, **kwargs):
                        (slave, request) = args
                        self.logging(content=f"on_handle_write_multiple_registers_request {IOTBaseCommon.DataTransform.format_bytes(request)}")
                        try:
                            # 解析请求数据
                            (_address, _quantity, _byte_count) = struct.unpack(">HHB", request[1:6])
                            values = [int.from_bytes(request[6 + i:8 + i], byteorder='big') for i in range(0, _byte_count, 2)]
                            self.on_handle_set_write(address, slave._id, modbus_tk_defines.WRITE_MULTIPLE_REGISTERS, _address, values)
                        except Exception as e:
                            self.logging(content=f"Handle write multiple registers error: {str(e)}", level='ERROR', pos=self.stack_pos)

                    def on_handle_write_single_register_request(args, **kwargs):
                        (slave, request) = args
                        self.logging(content=f"on_handle_write_single_register_request {request}")
                        try:
                            # 解析请求数据
                            (_address, value) = struct.unpack(">HH", request[1:5])
                            self.on_handle_set_write(address, slave.get_id(), modbus_tk_defines.WRITE_SINGLE_REGISTER, _address, [value])
                        except Exception as e:
                            self.logging(content=f"Handle write single register error: {str(e)}", level='ERROR', pos=self.stack_pos)

                    def on_handle_write_single_coil_request(args, **kwargs):
                        (slave, request) = args
                        self.logging(content=f"on_handle_write_single_coil_request {request}")
                        try:
                            # 解析请求数据
                            (_address, value) = struct.unpack(">HH", request[1:5])
                            self.on_handle_set_write(address, slave.get_id(), modbus_tk_defines.WRITE_SINGLE_COIL, _address, [1 if value == 0xFF00 else 0])
                        except Exception as e:
                            self.logging(content=f"Handle write single coil error: {str(e)}", level='ERROR', pos=self.stack_pos)

                    install_hook('modbus.Slave.handle_write_multiple_coils_request', on_handle_write_multiple_coils_request)
                    install_hook('modbus.Slave.handle_write_multiple_registers_request', on_handle_write_multiple_registers_request)
                    install_hook('modbus.Slave.handle_write_single_register_request', on_handle_write_single_register_request)
                    install_hook('modbus.Slave.handle_write_single_coil_request', on_handle_write_single_coil_request)
                else:
                    modbus_com = modbus_info['port']  # com5 或/dev/tty0
                    if modbus_com.find('/dev/tty') == 0:
                        server = RtuServer(Serial(port=modbus_com, baudrate=modbus_info['baudrate'], bytesize=modbus_info['bytesize'], parity=modbus_info['parity'], stopbits=modbus_info['stopbits'], xonxoff=modbus_info['xonxoff']))
                    else:
                        if modbus_com.startswith('com') is False:
                            modbus_com = f"com{modbus_com}"
                        server = RtuServer(Serial(port=modbus_com, baudrate=modbus_info['baudrate'], bytesize=modbus_info['bytesize'], parity=modbus_info['parity'], stopbits=modbus_info['stopbits'], xonxoff=modbus_info['xonxoff']))
                if server is not None:
                    server.start()
                    self.servers[address] = {'server': server, 'nodes': {}, 'slaves': {}}
        return server

    def _release_server(self, address: str):
        try:
            server = self.servers.get(address, {}).get('server')
            if server is not None:
                server.stop()
        except:
            pass
        finally:
            if 'server' in self.servers.get(address, {}).keys():
                del self.servers[address]['server']

    def _get_slave(self, server, cache: dict, id: int):
        slave = cache.get('slaves', {}).get(id, {}).get('slave')
        if slave is None:
            slave = server.add_slave(id)
            cache['slaves'][id] = {'slave': slave, 'blocks': {}}
        return slave

    def _create_objects(self, address: str, id: int, code: int, objects: list):
        server_cache = self.servers.get(address, {})
        server = server_cache.get('server')
        if server is not None:
            slave = self._get_slave(server, server_cache, id)
            if slave is not None:
                addrs = []
                for object in objects:
                    addr = object.get('point_address')
                    type = object.get('point_data_type')
                    length = object.get('point_data_length')
                    size = IOTBaseCommon.DataTransform.get_type_word_size(type, length)
                    for i in range(size):
                        addrs.append(addr + i)

                if len(addrs) > 0:
                    blocks = server_cache.get('slaves', {}).get(id, {}).get('blocks', {})
                    key = str(code)
                    block = self.ModbusBlockUnit(key, id, code, min(addrs), max(addrs))

                    if key not in blocks.keys():
                        slave.add_block(key, block.get_fun, block.get_start, block.get_size)
                        slave.set_values(key, block.get_start, 0)
                        blocks[key] = block
                    else:
                        if blocks[key].get_start != block.get_start or blocks[key].get_end != block.get_end:
                            slave.remove_block(key)
                            slave.add_block(key, block.get_fun, block.get_start, block.get_size)
                            slave.set_values(key, block.get_start, 0)
                            blocks[key] = block

    def _refresh_objects(self, address: str, id: int, code: int, objects: List[IOTSimulateObject]):
        server_cache = self.servers.get(address, {})
        server = server_cache.get('server')
        if server is not None:
            slave = server_cache.get('slaves', {}).get(id, {}).get('slave')
            if slave is not None:
                blocks = server_cache.get('slaves', {}).get(id, {}).get('blocks', {})
                for object in objects:
                    addr = object.get('point_address')
                    type = object.get('point_data_type')
                    length = object.get('point_data_length')
                    value = IOTBaseCommon.format_value(object.get('point_value'))
                    order = object.get('point_data_order', 0)

                    try:
                        key = f"{code}"
                        if key in blocks.keys() and value not in [None, '']:
                            if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY.value:
                                v = slave.get_values(key, addr, 1)
                                bs = IOTBaseCommon.DataTransform.convert_value(v[0], IOTBaseCommon.DataTransform.TypeFormat.UINT16, IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat(order))
                                bs[length] = value
                                value = IOTBaseCommon.DataTransform.convert_value(bs, IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY, IOTBaseCommon.DataTransform.TypeFormat.UINT16, pos=0, format=IOTBaseCommon.DataTransform.DataFormat(order))
                            with self.lock_read_write_handler:  # 等待更新
                                slave.set_values(key, addr, self._convert_value_to_vector(type, order, 8, value))
                    except Exception as e:
                        self.logging(content=f"refresh object({id} {code} {addr}) fail({e.__str__()})", level='ERROR', pos=self.stack_pos)

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_modbus.py({pos})"
