import logging
import time
from ctypes import create_string_buffer as ctypes_create_string_buffer, c_int32 as ctypes_c_int32, pointer as ctypes_pointer, cast as ctypes_cast, POINTER, c_uint8 as ctypes_c_uint8, c_uint16 as ctypes_c_uint16, string_at as ctypes_string_at
from enum import Enum
from snap7.common import error_text, load_library, check_error
from snap7.types import S7DataItem, S7WLByte, SendTimeout, RecvTimeout, RemotePort, wordlen_to_ctypes, Areas
from snap7 import util as snap7_util, client as snap7_client, server as snap7_server

from typing import List, Dict, Any, Optional
from threading import Lock

from .base import IOTBaseCommon, IOTDriver, IOTSimulateObject

'''
pip install python-snap7==0.10

Note：
    snap7_server需要使用64位环境
    最大连读个数20
    指定dll位置
    大端模式
        网络传输一般采用大端序，也被称之为网络字节序，或网络序。IP协议中定义大端序为网络字节序。
        高字节放在内存的地地址
        
    windows:
        snap7.dll is added to the python installation directory or any directory in the system environment

    linux install dll 
        下载压缩包:
            https://sourceforge.net/projects/snap7/files/下载snap7-full-1.4.2.7z
        
        解压
            apt-get install p7zip-full
            7z x snap7-full-1.4.2.7z
        
        编译
            cd snap7-full-1.4.2/build/unix
            make -f X86_64_linux.mk all
            
        拷贝
            sudo cp ../bin/arm_v7-linux/libsnap7.so /usr/lib/libsnap7.so
            sudo cp ../bin/arm_v7-linux/libsnap7.so /usr/local/lib/libsnap7.so

        sudo ldconfig

        可选
        sudo apt-get install python-pip3

        安装python snap7库
        sudo pip3 install python-snap7
       
地址
    #define daveP 0x80    		/* direct peripheral access */
    #define daveInputs 0x81     S7AreaPE  
    #define daveOutputs 0x82    S7AreaPA
    #define daveFlags 0x83      S7AreaMK
    #define daveDB 0x84	       S7AreaDB /* data blocks */

DB Address：
    V   daveDB      1
    I/E daveInputs  0
    Q   daveOutputs 0
    M/F daveFlags   0
    T   daveTimer200    0
    C/Z daveCounter200  0
    S   daveSysFlags    0
    A   daveAnaOut/daveAnaIn    0
    P   daveP       0
    
rack是机架号，slot卡槽号
    s7-200 0, 1
    s7-300 0, 2
    s7-400 具体看硬件组态
    s7-1200/1500 0, 0/1
    
    
    配置
        S7_200Smart	
            IP/Port/0/0/2
                STSAP	RTSAP
                0100    0300
        S7_200	
            IP/Port/19799/19799/1
                STSAP	RTSAP
                4D57    4D57
    
connection_type:
    PG=1
    OP=2
    S7-Basic=3/10
    
dbnumber:
    地址编号（int），只适用于DB区和200samart的V区，其它区全默认0，V区只能填1

read_multi_vars：
    这是可以一次读取<=19个不同地址类型的变量，由于pdu大小限制一次性读取不能超过19个变量

数据类型
    TypeSize = {
    'int': 2,  # 有符号（-32768～32767）
    'bool': 1,  # bool值
    'dint': 4,  # 有符号 （-2147483648～2147483647）
    'word': 2,  # 无符号（0～65536）
    'real': 4,  # 有符号 float类型（这范围记不住了）
    'dword': 4,  # 无符号（0～4294967295）
    'char': 1,  # CHAR，ASCII字符集，占用1个字节内存，主要针对欧美国家（字符比较少）
    'string': 255,  # STRING，占用256个字节内存，ASCII字符串，由ASCII字符组成
    's5time': 2,
    'wchar': 2,  # WCHAR，Unicode字符集，占用2个字节内存，主要针对亚洲国家（字符比较多）
    'wstring': 512,  # WSTRING，默认占用512个字节内存（可变），Unicode字符串，由Unicode字符构成
    'dt': 4,  # DateTime 日期
    'usint': 1,  # 0～255
    'sint': 1,  # -128～127
    'uint': 2,  # 0～4294967295
    'udint': 4,  # 0～4294967295
    'lreal': 8,
    'time': 4,
    'd': 2,
    'tod': 4,  # TOD (TIME_OF_DAY)数据作为无符号双整数值存储，被解释为自指定日期的凌晨算起的毫秒数(凌晨 = 0ms)。必须指定小时(24 小时/天)、分钟和秒。可以选择指定小数秒格式。
    'dtl': 12,  # DTL(日期和时间长型)数据类型使用 12 个字节的结构保存日期和时间信息。可以在块的临时存储器或者 DB 中定义 DTL 数据。
    'date': 2,  # Date(16位日期值)、
    'ltod': 8
}

Point：
    DB2,REAL10,VT_R4,192.168.0.2,1,3
    I0.6

'''


'''
    pip install python-snap7==1.3
'''


class IOTPlcS7(IOTDriver):

    # 西门子PLC的类型对象
    class S7Version(Enum):
        S7_200 = 1  # 西门子S7-200 需要配置网络模块
        S7_200Smart = 2
        S7_300 = 3
        S7_400 = 4
        S7_1200 = 5
        S7_1500 = 6

    class S7BlockUnit:

        def __init__(self, area, db: int, size: int):
            self.area = area
            self.db = db
            self.size = size
            self.buffers = None

        def __str__(self):
            return f"{self.area}_{self.db}"

        @property
        def get_area(self):
            areas = {0x81: 0, 0x82: 1, 0x83: 2, 0x1C: 3, 0x1D: 4, 0x84: 5}
            return areas.get(self.area, 5)

        @property
        def get_db(self):
            return self.db

        @property
        def get_size(self):
            return self.size

        def set_size(self, size):
            self.size = size

        @property
        def get_buffers(self):
            return self.buffers

        def buffer(self):
            self.buffers = ctypes_create_string_buffer(self.size)

        def update(self, server, start: int, addr: int, type, value):
            index = start
            if server and 0 <= index < self.size:
                if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL:
                    server.lock_area(self.get_area, self.db)
                    snap7_util.set_bool(self.buffers, index, addr, int(float(value)))
                    server.unlock_area(self.get_area, self.db)
                elif type == IOTBaseCommon.DataTransform.TypeFormat.INT16:
                    server.lock_area(self.get_area, self.db)
                    snap7_util.set_int(self.buffers, index, int(float(value)))
                    server.unlock_area(self.get_area, self.db)
                elif type == IOTBaseCommon.DataTransform.TypeFormat.INT32:
                    server.lock_area(self.get_area, self.db)
                    snap7_util.set_dword(self.buffers, index, int(float(value)))
                    server.unlock_area(self.get_area, self.db)
                elif type == IOTBaseCommon.DataTransform.TypeFormat.FLOAT:
                    server.lock_area(self.get_area, self.db)
                    snap7_util.set_real(self.buffers, index, float(value))
                    server.unlock_area(self.get_area, self.db)

    class S7ReadUnit:

        def __init__(self, address: str, area, db: int, start: int, length: int, type):
            self.address = address
            self.area = area
            self.db = db
            self.start = start
            self.length = length
            self.type = type

        def __str__(self):
            return f"{self.address}_{self.area}_{self.db}_{self.start}_{self.length}"

        @property
        def get_area(self):
            return self.area

        @property
        def get_db(self):
            return self.db

        @property
        def get_start(self):
            return self.start

        @property
        def get_amount(self):
            return self.length

        def get_item(self):
            item = S7DataItem()
            item.Area = ctypes_c_int32(self.area)
            item.WordLen = ctypes_c_int32(S7WLByte)
            item.Result = ctypes_c_int32(0)
            item.DBNumber = ctypes_c_int32(self.db)
            item.Start = ctypes_c_int32(self.start)
            item.Amount = ctypes_c_int32(self.length)  # reading a REAL, 4 bytes
            buffer = ctypes_create_string_buffer(item.Amount)
            item.pData = ctypes_cast(ctypes_pointer(buffer), POINTER(ctypes_c_uint8))
            return item

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.clients = {}
        self.rw_locks = {}  # 读写锁
        self.client_connect_fails = {}  # 连接连续失败次数
        self.servers = {}
        self.plc_objects = {}

        log_common = logging.getLogger('snap7.common')
        if log_common:
            log_common.setLevel(logging.ERROR)
            log_common.disabled = True

    def exit(self):
        self.exit_flag = True
        for port, server in self.servers.items():
            self._release_server(port)

        address = list(self.clients.keys())
        for address in address:
            if address in self.clients.keys():
                self._release_client(address)

        self.reinit()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''}])
            if mode == 0:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '192.168.1.184/102/0/1', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '102', 'enum': [], 'tip': ''})
            templates.extend([
                {'required': True, 'name': '点地址' if lan == 'ch' else 'address'.upper(), 'code': 'point_address', 'type': 'string', 'default': 'DB3,REAL4', 'enum': [], 'tip': ''},
                {'required': False, 'name': '点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''}
                ])
            if mode == 0:
                templates.extend([{'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''}])
            else:
                templates.append({'required': True, 'name': '点值' if lan == 'ch' else 'value'.upper(), 'code': 'point_value', 'type': 'int', 'default': 0, 'enum': [], 'tip': ''})
            templates.extend([
                {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
            ])

        elif type == 'config':
            templates.append({'required': False, 'name': '依赖库路径' if lan == 'ch' else 'Library', 'code': 'library', 'type': 'string', 'default': '', 'enum': [], 'tip': ''})
            if mode == 0:
                templates.extend([
                    {'required': False, 'name': '尝试读取次数' if lan == 'ch' else 'Read Retries', 'code': 'read_retries', 'type': 'int', 'default': 2, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '批量读取个数' if lan == 'ch' else 'Multi Read', 'code': 'multi_read', 'type': 'int', 'default': 19, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '命令间隔(s)' if lan == 'ch' else 'Cmd Interval(s)', 'code': 'cmd_interval', 'type': 'float', 'default': 0.1, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '发送超时(ms)' if lan == 'ch' else 'Send Timeout(ms)', 'code': 'send_timeout', 'type': 'int', 'default': 15, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '接收超时(ms)' if lan == 'ch' else 'Recv Timeout(ms)', 'code': 'rec_timeout', 'type': 'int', 'default': 3500, 'enum': [], 'tip': ''},
                    {'required': False, 'name': '读写分离' if lan == 'ch' else 'Write Alone', 'code': 'write_alone', 'type': 'bool', 'default': False, 'enum': [], 'tip': ''},
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
                address = point.get('point_address')
                if device_address is not None and address is not None:
                    if device_address not in read_items.keys():
                        read_items[device_address] = []
                    if address not in read_items[device_address]:
                        read_items[device_address].append(address)

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                device_address = point.get('point_device_address')
                address = point.get('point_address')
                if device_address is not None and address is not None:
                    value = self.get_value(name, device_address, address)
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
            if point:
                device_address = point.get('point_device_address')
                address = point.get('point_address')
                if device_address is not None and address is not None:
                    area, db, start, length, addr, type = self._get_s7_item(address)
                    s7_key = self._gen_key(area, db, start, length)
                    self._write(device_address, address, s7_key, value)
                    result = self.get_device_property(device_address, s7_key, [self.get_write_quality, self.get_write_result])
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
        points = kwargs.get('points', {})
        self.logging(content=f"simulate({len(points)})", pos=self.stack_pos)
        server_objects = {}
        for name, point in points.items():
            point = points.get(name)
            if point:
                device_address = point.get('point_device_address')
                address = point.get('point_address')
                if device_address is not None and address is not None:
                    if device_address not in server_objects.keys():
                        server_objects[device_address] = []
                    server_objects[device_address].append(IOTSimulateObject(**point))

        if len(server_objects) > 0:
            for port, objects in server_objects.items():
                if self._get_server(port) is not None:

                    self._create_objects(port, objects)

                    self._refresh_objects(port, objects)

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        # ip/port/rack/slot/version/connection_type
        versions = kwargs.get('version', [1, 2, 3])
        ip = kwargs.get('ip', '')
        port = kwargs.get('port', 102)
        racks = kwargs.get('rack', [0, 1, 2, 3])
        slots = kwargs.get('slot', [0, 1, 2, 3])
        for version in versions:
            for rack in racks:
                for slot in slots:
                    if version == IOTPlcS7.S7Version.S7_200Smart.value:
                        for connection_type in [1, 2, 3]:
                            address = f"{ip}/{port}/{rack}/{slot}/{version}/{connection_type}"
                            try:
                                if self._get_client(address):
                                    self.logging(content=f"success({address})", pos=self.stack_pos)
                                    if kwargs.get('once', False) is True:
                                        return True
                            except Exception as e:
                                self.logging(content=f"error: {address} {e.__str__()}", pos=self.stack_pos)
                            finally:
                                self._release_client(address)
                    else:
                        address = f"{ip}/{port}/{rack}/{slot}/{version}"
                        try:
                            if self._get_client(address):
                                self.logging(content=f"success({address})", pos=self.stack_pos)
                                if kwargs.get('once', False) is True:
                                    return True
                        except Exception as e:
                            self.logging(content=f"error: {address} {e.__str__()}", pos=self.stack_pos)
                        finally:
                            self._release_client(address)
        return False

    def _gen_key(self, area, db: int, start: int, length: int) -> str:
        return f"{area}_{db}_{start}_{length}"

    def _cread_read_units(self, address, s7_items: list) -> dict:
        read_units = {}
        for s7_item in s7_items:
            if isinstance(s7_item, str) and len(s7_item) > 0:
                area, db, start, length, addr, type = self._get_s7_item(s7_item)
                unit = self.S7ReadUnit(address, area, db, start, length, type)
                if unit.__str__() not in read_units.keys():
                    read_units[unit.__str__()] = unit.get_item()
        return read_units

    def _get_address_info(self, device_address: str) -> dict:
        # ip/port/rack/slot/version/connection_type
        info_list = device_address.split('/')
        return {'host': info_list[0] if len(info_list) > 0 else '', 'port': int(float(info_list[1])) if len(info_list) > 1 else 102, 'rack': int(float(info_list[2])) if len(info_list) > 2 else 0, 'slot': int(float(info_list[3])) if len(info_list) > 3 else 1, 'type': IOTPlcS7.S7Version.S7_200Smart if len(info_list) <= 2 else IOTPlcS7.S7Version.S7_1200 if 2 < len(info_list) <= 4 else IOTPlcS7.S7Version(int(info_list[4])), 'connection_type': int(str(info_list[-1])) if len(info_list) > 5 else 3}

    def _release_client(self, address: str):
        client = self.clients.get(address)
        try:
            if client:
                client.disconnect()
                client.destroy()
        except Exception as e:
            pass
        finally:
            if address in self.clients.keys():
                del self.clients[address]

    def _load_library(self):
        if IOTBaseCommon.is_windows():
            library = self.configs.get('library')
            if isinstance(library, str) and len(library) > 0 and IOTBaseCommon.check_file_exist(library):
                load_library(library)

    def set_connect_status(self, address: str, is_success: bool = False):
        if is_success is True:
            self.client_connect_fails[address] = 0
        else:
            self.client_connect_fails[address] = self.client_connect_fails[address] + 1

    def _get_client(self, address: str, write_alone: bool = False):
        _address = address if write_alone is False else f"{address}_write"
        client = self.clients.get(_address)
        if client is not None:
            try:
                if client.get_connected() is False:  # 连接成功
                    raise Exception(f"connected is false")
            except Exception as e:
                self._release_client(_address)
                client = None

        if client is None:
            try:
                if self.client_connect_fails.get(address, 0) >= self.configs.get('max_retries', 5):  # 连续连接失败达到5次 本次轮询不在尝试
                    raise Exception(f"connection failure count exceeded({self.configs.get('max_retries', 5)})")

                info = self._get_address_info(address)
                if 'type' in info.keys():
                    self._load_library()
                    client = snap7_client.Client()
                    if client:
                        if self.configs.get('send_timeout', 15) > 0:
                            client.set_param(SendTimeout, self.configs.get('send_timeout'))
                        if self.configs.get('rec_timeout', 3500) > 0:
                            client.set_param(RecvTimeout, self.configs.get('rec_timeout'))

                    if info['type'] == IOTPlcS7.S7Version.S7_200:
                        client.set_param(RemotePort, info['port'])
                        client._library.Cli_SetConnectionParams(client._pointer, info['host'].encode(), ctypes_c_uint16(info['rack']), ctypes_c_uint16(info['slot']))
                        result = client._library.Cli_Connect(client._pointer)
                        check_error(result, context="client")
                    elif info['type'] == IOTPlcS7.S7Version.S7_200Smart:
                        client.set_connection_type(info.get('connection_type', 3))   # 设置连接资源类型，即客户端,连接到PLC   默认情况下，客户端连接为PG（编程控制台），使用此功能可以将连接资源类型更改为OP（西门子HMI面板）或S7 Basic（通用数据传输连接）
                        client.connect(info['host'], info['rack'], info['slot'], info['port'])
                    else:
                        client.connect(info['host'], info['rack'], info['slot'], info['port'])
                    if client.get_connected() is True:
                        self.set_connect_status(address, True)
                        self.clients[_address] = client
                        if _address not in self.rw_locks.keys():
                            self.rw_locks[_address] = Lock()
            except Exception as e:
                self.set_connect_status(address, False)
                raise IOTBaseCommon.IOTConnectException(e.__str__())
        return self.clients.get(_address)

    def _parse_result(self, address: str, s7_key: str, s7_item):
        self.update_device(address, s7_key, **self.gen_read_write_result(True, ctypes_string_at(s7_item.pData, s7_item.Amount)))

    def _send_read_cmd(self, address: str, s7_item_list: list, process: Optional[str] = None, read_retries: int = 2):
        for i in range(read_retries):
            if address not in self.rw_locks.keys():
                self.rw_locks[address] = Lock()
            lock = self.rw_locks.get(address)
            with lock:
                start = time.time()
                try:
                    if self._get_client(address) is not None and len(s7_item_list) > 0:
                        s7_item_byref = (S7DataItem * len(s7_item_list))()
                        for index in range(0, len(s7_item_list)):
                            s7_item_byref[index] = s7_item_list[index]

                        result, s7_data_items = self._get_client(address).read_multi_vars(s7_item_byref)
                        for s7_item in s7_data_items:
                            s7_key = self._gen_key(s7_item.Area, s7_item.DBNumber, s7_item.Start, s7_item.Amount)
                            try:
                                if s7_item.Result:
                                    raise Exception(error_text(s7_item.Result))
                                else:
                                    self._parse_result(address, s7_key, s7_item)
                            except Exception as e:
                                self.update_device(address, s7_key, **self.gen_read_write_result(False, f"read error: {e.__str__()}"))
                    break
                except (Exception, IOTBaseCommon.IOTConnectException) as e:
                    self._release_client(address)
                    if i == read_retries - 1:
                        for s7_item in s7_item_list:
                            self.update_device(address, self._gen_key(s7_item.Area, s7_item.DBNumber, s7_item.Start, s7_item.Amount), **self.gen_read_write_result(False, f"connect error: read({e.__str__()})" if isinstance(e, IOTBaseCommon.IOTConnectException) else f"read error: {e.__str__()}"))
                finally:
                    self.logging(content=f"plc({address}) read{'' if process is None else f'({process})'} {len(s7_item_list)} {i + 1}/{read_retries} cost: {'{:.2f}'.format(time.time() - start)}", pos=self.stack_pos)

    def _read_address(self, *args, **kwargs) -> dict:
        start = time.time()
        (address, s7_items) = args
        results = {}
        self.client_connect_fails[address] = 0
        read_units = self._cread_read_units(address, sorted(s7_items))

        units = list(IOTBaseCommon.chunk_list(list(read_units.values()), self.configs.get('multi_read', 19)))
        for i, unit in enumerate(units):
            self._send_read_cmd(address, unit, f"{i}/{len(units)}", self.configs.get('read_retries', 2))
            self.delay(self.configs.get('cmd_interval', 0.3))
        self.logging(content=f"plc({address}) read: {len(s7_items)} response: {results} group: {len(units)} cost: {'{:.2f}'.format(time.time() - start)}", pos=self.stack_pos)
        return results

    def _read(self, read_items: dict):
        if len(read_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(read_items), f"{self}")
            for address, s7_items in read_items.items():
                jobs.submit_task(self._read_address, address, s7_items)
            return jobs.done()
        return {}

    def _get_s7_item(self, address: str):
        # DB2,REAL10,VT_R4 I0.6
        # define daveP 0x80    		/* direct peripheral access */
        # define daveInputs 0x81     S7AreaPE
        # define daveOutputs 0x82    S7AreaPA
        # define daveFlags 0x83      S7AreaMK
        # define daveDB 0x84	       S7AreaDB /* data blocks */

        areas = {'I': 0x81, 'E': 0x81, 'Q': 0x82, 'M': 0x83, 'F': 0x83, 'V': 0x84, 'T': 31, 'C': 30}
        area = areas.get(address[0], 0x84)

        db = 0
        start = 0
        length = 1
        type = IOTBaseCommon.DataTransform.TypeFormat.INT8
        addr = 0

        # DB2,REAL10
        if address.startswith('DB') is True:
            infos = address.split(',')
            if len(infos) == 2:
                db = int(infos[0][2:])
                if infos[1].startswith('INT'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.INT16
                    length = 2
                    start = int(float(infos[1][3:]))
                elif infos[1].startswith('WORD'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.UINT16
                    length = 2
                    start = int(float(infos[1][4:]))
                elif infos[1].startswith('BYTE'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.INT8
                    length = 1
                    start = int(float(infos[1][4:]))
                elif infos[1].startswith('DINT'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.INT32
                    length = 4
                    start = int(float(infos[1][4:]))
                elif infos[1].startswith('DWORD'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.UINT32
                    length = 4
                    start = int(float(infos[1][5:]))
                elif infos[1].startswith('REAL'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.FLOAT
                    length = 4
                    start = int(float(infos[1][4:]))
                elif infos[1].startswith('BOOL'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.BOOL
                    length = 1
                    pos = infos[1].find('.')
                    if pos >= 4:
                        start = int(float(infos[1][4:pos]))
                        addr = int(float(infos[1][pos + 1:]))
                elif infos[1].startswith('X'):
                    type = IOTBaseCommon.DataTransform.TypeFormat.BOOL
                    length = 1
                    pos = infos[1].find('.')
                    if pos >= 1:
                        start = int(float(infos[1][1:pos]))
                        addr = int(float(infos[1][pos + 1:]))
        else:   # I2.0 VD200
            db = 1 if address[0] == 'V' else 0
            if address[1] == 'B':   # BYTE
                type = IOTBaseCommon.DataTransform.TypeFormat.INT8
                length = 1
            elif address[1] == 'W':
                type = IOTBaseCommon.DataTransform.TypeFormat.INT16
                length = 2
            elif address[1] == 'D':
                type = IOTBaseCommon.DataTransform.TypeFormat.INT32
                length = 4
            elif address[1] == 'R':     # 额外新增
                type = IOTBaseCommon.DataTransform.TypeFormat.FLOAT
                length = 4
            else:
                type = IOTBaseCommon.DataTransform.TypeFormat.BOOL
                length = 1

            info = address[2:] if address[1] in ['D', 'B', 'W', 'R'] else address[1:]
            pos = info.find('.')
            if pos > 0:
                start = int(float(info[:pos]))
                addr = int(float(info[pos+1:]))
            else:
                start = int(float(info))

        return area, db, start, length, addr, type

    def get_value(self, name: str, device_address: str, address: str):
        try:
            area, db, start, length, addr, type = self._get_s7_item(address)
            s7_key = self._gen_key(area, db, start, length)
            [result, value] = self.get_device_property(device_address, s7_key, [self.get_read_quality, self.get_read_result])
            if result is True:
                if value is not None:
                    value = IOTBaseCommon.DataTransform.convert_bytes_to_values(value, type, 0, little_endian=False)
                    if isinstance(value, list):
                        if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL:
                            return value[addr]
                        return value[0]
                    else:
                        return value
                else:
                    raise Exception(f"value is none")
            else:
                raise Exception(str(value))
        except Exception as e:
            self.update_results(name, False, e.__str__())
        return None

    def _conver_set_data_value(self, reading, value, type, addr):
        if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL:
            snap7_util.set_bool(reading, 0, addr, bool(int(str(value))))
        else:
            reading = bytearray(IOTBaseCommon.DataTransform.convert_values_to_bytes(value, type, little_endian=False))
        return reading

    def _write(self, device_address: str, address: str, s7_key: str, value, read_retries: int = 2):
        result = [False, '']
        write_alone = str(self.configs.get('write_alone', 'false')).lower() == 'true'  # 写通道独立
        _device_address = device_address if write_alone is False else f"{device_address}_write"
        for i in range(read_retries):
            if _device_address not in self.rw_locks.keys():
                self.rw_locks[_device_address] = Lock()
            lock = self.rw_locks.get(_device_address)
            with lock:
                try:
                    area, db, start, length, addr, type = self._get_s7_item(address)
                    if self._get_client(device_address, write_alone) is not None:
                        reading = bytearray(1)
                        if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL:
                            reading = self._get_client(device_address, write_alone).read_area(Areas(area), db, start, length)
                        reading = self._conver_set_data_value(reading, value, type, addr)
                        result[0] = self._get_client(device_address, write_alone).write_area(Areas(area), db, start, reading)
                        return self.update_device(device_address, s7_key, **self.gen_read_write_result(True, None, False))
                    raise Exception(f"Unknown")
                except (Exception, IOTBaseCommon.IOTConnectException) as e:
                    self._release_client(_device_address)
                    if i == read_retries - 1:
                        self.update_device(device_address, s7_key, **self.gen_read_write_result(False, f"connect error: write({e.__str__()})" if isinstance(e, IOTBaseCommon.IOTConnectException) else f"write error: {e.__str__()}", False))

    def _get_server(self, port: int = 102):
        server = self.servers.get(port, {}).get('server')
        if server is None:
            self._load_library()
            server = snap7_server.Server()
            server.start(tcpport=port)
            self.servers[port] = {'server': server, 'blocks': {}}
        return server

    def _release_server(self, port: int):
        try:
            server = self.servers.get(port, {}).get('server')
            if server is not None:
                server.stop()
                server.destroy()
            server = None
        except:
            pass
        finally:
            if 'server' in self.servers.get(port, {}).keys():
                del self.servers[port]['server']

    # 合并生成地址块单元
    def _combine_unit(self, block_unit, block_units: dict):
        units = block_units.get(block_unit.__str__())
        if units is not None:
            if block_unit.get_size > units.get_size:
                units.set_size(block_unit.get_size)
        else:
            block_units[block_unit.__str__()] = block_unit

    def _create_objects(self, port: int, objects: List[IOTSimulateObject]):
        server_cache = self.servers.get(port, {})
        server = server_cache.get('server')
        blocks = server_cache.get('blocks', {})
        if server is not None:
            new_blocks = {}
            for object in objects:
                area, db, start, length, addr, type = self._get_s7_item(object.get('point_address'))
                key = f"{area}_{db}"
                if key not in new_blocks.keys():
                    new_blocks[key] = {'area': area, 'db': db, 'size': start + length, 'buffer': None}
                else:
                    if start + length > new_blocks[key].get('size'):
                        new_blocks[key].update({'size': start + length})

            try:
                areas = {0x81: 0, 0x82: 1, 0x83: 2, 0x1C: 3, 0x1D: 4, 0x84: 5}
                for key, block in new_blocks.items():
                    register = False
                    if key in blocks.keys():
                        if blocks[key].get('size') != block.get('size'):
                            server.unregister_area(areas.get(block.get('area')), block.get('db'))
                            register = True
                    else:
                        register = True

                    if register:
                        self.logging(content=f"register {block.get('area')} {block.get('db')} {block.get('size')}", pos=self.stack_pos)
                        buffer = (wordlen_to_ctypes[S7WLByte] * block.get('size'))()
                        server.register_area(areas.get(block.get('area')), block.get('db'), buffer)
                        block['buffer'] = buffer
                        blocks[key] = block
            except Exception as e:
                self.logging(content=f"create object({port}) fail({e.__str__()})", level='ERROR', pos=self.stack_pos)

    def _update_value(self, server, block, area, db, start: int, addr: int, type, value):
        if server is not None and isinstance(block, dict):
            index = start
            if server and 0 <= index < block.get('size'):
                if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL:
                    server.lock_area(area, db)
                    snap7_util.set_bool(block.get('buffer'), index, addr, bool(int(float(value))))
                    server.unlock_area(area, db)
                elif type == IOTBaseCommon.DataTransform.TypeFormat.INT16:
                    server.lock_area(area, db)
                    snap7_util.set_int(block.get('buffer'), index, int(float(value)))
                    server.unlock_area(area, db)
                elif type == IOTBaseCommon.DataTransform.TypeFormat.INT32:
                    server.lock_area(area, db)
                    snap7_util.set_dword(block.get('buffer'), index, int(float(value)))
                    server.unlock_area(area, db)
                elif type == IOTBaseCommon.DataTransform.TypeFormat.FLOAT:
                    server.lock_area(area, db)
                    snap7_util.set_real(block.get('buffer'), index, float(value))
                    server.unlock_area(area, db)

    def _refresh_objects(self, port: int, objects: List[IOTSimulateObject]):
        server_cache = self.servers.get(port, {})
        server = server_cache.get('server')
        blocks = server_cache.get('blocks', {})
        if server is not None and len(blocks) > 0:
            areas = {0x81: 0, 0x82: 1, 0x83: 2, 0x1C: 3, 0x1D: 4, 0x84: 5}
            for object in objects:
                point_address = object.get('point_address')
                value = IOTBaseCommon.format_value(object.get('point_value'))
                if point_address is not None and value not in [None, '']:
                    try:
                        area, db, start, length, addr, type = self._get_s7_item(point_address)
                        block = blocks.get(f"{area}_{db}")
                        self._update_value(server, block, areas.get(area), db, start, addr, type, value)
                    except Exception as e:
                        self.logging(content=f"refresh object({point_address}) fail({e.__str__()})", level='ERROR', pos=self.stack_pos)

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_plc_s7.py({pos})"
