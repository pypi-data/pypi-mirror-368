
import logging
import time
import sys
import Pyro5.core

from datetime import datetime
from enum import IntEnum
from os import getenv as os_getenv, path as os_path, getpid, system as os_system
from psutil import Process
from platform import system as platform_system
from Pyro5.client import Proxy
from Pyro5.server import Daemon
from Pyro5.api import expose as pyro5_expose, current_context
from re import compile as re_compile, IGNORECASE
from socket import gethostname, gethostbyname
from subprocess import Popen
from typing import Optional, Union, List, Dict, Any
from threading import Event, Thread, Lock

from .base import IOTBaseCommon, IOTDriver


if platform_system().lower() == 'windows':
    import winreg
    import pywintypes
    import win32com.client

    from pythoncom import (CoInitialize, CoInitializeEx, CoUninitialize,  COINIT_APARTMENTTHREADED, COINIT_MULTITHREADED, PumpWaitingMessages, com_error, GetScodeString, Missing)

    sys.coinit_flags = 0  # pythoncom.COINIT_MULTITHREADED == 0
    pywintypes.datetime = pywintypes.TimeType
    win32com.client.gencache.is_readonly = False    # Allow gencache to create the cached wrapper objects
    win32com.client.gencache.Rebuild(verbose=0)  # Under p2exe the call in gencache to __init__() does not happen so we use Rebuild() to force the creation of the gen_py folder


class OPCDA:

    class OPCCommon:

        @staticmethod
        def get_datetime() -> datetime:
            return datetime.now()

        @staticmethod
        def get_datetime_str() -> str:
            return OPCDA.OPCCommon.get_datetime().strftime('%Y-%m-%d %H:%M:%S')

        @staticmethod
        def get_timestamp() -> int:
            return int(time.time())

        @staticmethod
        def convert_time(timestamp: float):
            try:
                return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
            except:
                pass
            return timestamp

        @staticmethod
        def get_env(name: str, default: Optional[Any] = None):
            if platform_system().lower() == 'windows':
                try:

                    value, valuetype = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\Session Manager\Environment', 0, winreg.KEY_READ), name)
                    return value
                except:
                    return default
            return os_getenv(name, default)

        @staticmethod
        def get_host_ip() -> str:
            try:
                ip = gethostbyname(gethostname())
            except:
                ip = '0.0.0.0'
            return ip

        @staticmethod
        def get_executable_folder() -> str:
            """获取当前运行目录"""
            return os_path.dirname(sys.executable)

        @staticmethod
        def type_check(tags: Union[list, tuple, str, None]):
            single = type(tags) not in (list, tuple)
            tags = tags if tags else []
            tags = [tags] if single else tags
            valid = len([t for t in tags if type(t) not in (str, bytes)]) == 0
            return tags, single, valid

        @staticmethod
        def wild2regex(content: str):
            """将Unix通配符glob转换为正则表达式"""
            return content.replace('.', r'\.').replace('*', '.*').replace('?', '.').replace('!', '^')

        @staticmethod
        def tags2trace(tags: list):
            """将列表标记转换为适合跟踪回调日志的格式化字符串"""
            arg_str = ''
            for i, t in enumerate(tags[1:]):
                if i > 0:
                    arg_str += ','
                arg_str += '%s' % t
            return arg_str

        @staticmethod
        def exceptional(func, alt_return=None, alt_exceptions=(Exception,), final=None, catch=None):
            """将异常转换为替代返回值"""
            def _exceptional(*args, **kwargs):
                try:
                    try:
                        return func(*args, **kwargs)
                    except alt_exceptions:
                        return alt_return
                    except:
                        if catch:
                            return catch(sys.exc_info(), lambda: func(*args, **kwargs))
                        raise
                finally:
                    if final:
                        final()
            return _exceptional

        @staticmethod
        def get_quality_string(quality_bits):
            """Convert OPC quality bits to a descriptive string"""
            quality = (quality_bits >> 6) & 3
            return OPCDA.OPCDefine.QUALITY[quality]

        @staticmethod
        def split_to_list(values, size: int):
            if isinstance(values, dict):
                results = [{}]
                for k, v in values.items():
                    if len(results[-1]) >= size:
                        results.append({k: v})
                    else:
                        results[-1][k] = v
                return results
            elif isinstance(values, list):
                return [values[i:i + size] for i in range(0, len(values), size)]
            return values

        @staticmethod
        def get_current_pids() -> str:
            pids = []
            pid = getpid()
            pids.append(str(pid))
            pids.extend([str(p.pid) for p in Process(pid).children()])
            return ','.join(pids)

        @staticmethod
        def get_current_process() -> dict:
            """获取当前进程信息"""
            info = {}
            p = Process(getpid())
            if p:
                with p.oneshot():
                    info['pid'] = p.pid
                    info['memory'] = p.memory_info().rss / 1024 / 1024
                    info['threads'] = p.num_threads()
                    info['status'] = p.status()
                    info['cpu'] = p.cpu_percent()
                    info['create'] = OPCDA.OPCCommon.convert_time(p.create_time())
            return info

        @staticmethod
        def restart_service(servic_name: str):
            """重启服务"""
            bat_path = f"restart.bat"
            with open(bat_path, 'w') as f:
                content = f"@echo off\n"  # 关闭bat脚本的输出
                content = f"{content}echo {OPCDA.OPCCommon.get_datetime_str()}"
                content = f"{content}choice /t 3 /d y /n >nul\n"  # 延时3秒执行
                content = f"{content}net stop {servic_name}\n"
                content = f"{content}net start {servic_name}\n"
                f.write(content)
            Popen(bat_path)
            return True

        @staticmethod
        def register_dll(dll_path: str):
            dll_path = dll_path.replace('\\', '/')
            os_system(f"regsvr32 {dll_path}")

        @staticmethod
        def convert_socket_address(address) -> str:
            if isinstance(address, tuple) and len(address) > 1:
                return f"{address[0]}:{address[1]}"
            return str(address)

    class OPCConfig:

        def __init__(self, service_name: str = 'RobertOPCDAService', service_display: str = 'Robert OPC DA Service', service_desc: str = 'OPC DA Service 20230627 edit by robert'):
            self.OPC_DA_SERVICE_NAME = service_name
            self.OPC_DA_SERVICE_DISPLAY_NAME = service_display
            self.OPC_DA_SERVICE_DESCRIPTION = service_desc

            self.OPC_DA_START = OPCDA.OPCCommon.get_datetime_str()
            self.OPC_DA_CLASS = OPCDA.OPCCommon.get_env('OPC_DA_CLASS', 'Matrikon.OPC.Automation;Graybox.OPC.DAWrapper;HSCOPC.Automation;RSI.OPCAutomation;OPC.Automation')
            self.OPC_DA_GATE_HOST = OPCDA.OPCCommon.get_env('OPC_DA_GATE_HOST',  OPCDA.OPCCommon.get_host_ip())
            self.OPC_DA_GATE_PORT = int(str(OPCDA.OPCCommon.get_env('OPC_DA_GATE_PORT', '8810')))
            self.OPC_DA_GATE_MODE = OPCDA.OPCCommon.get_env('OPC_DA_GATE_MODE', 'service')
            self.OPC_DA_GATE_TOKEN_APP = OPCDA.OPCCommon.get_env('OPC_DA_GATE_TOKEN_APP', 'explorer.exe')
            self.OPC_DA_GATE_TIMEOUT = int(str(OPCDA.OPCCommon.get_env('OPC_DA_GATE_TIMEOUT', '600')))
            self.OPC_DA_GATE_CONNECT_INTERVAL = int(str(OPCDA.OPCCommon.get_env('OPC_DA_GATE_CONNECT_INTERVAL', '5')))
            self.OPC_DA_GATE_LIMIT_SIZE = int(str(OPCDA.OPCCommon.get_env('OPC_DA_GATE_LIMIT_SIZE', '25')))
            self.OPC_DA_GATE_MEMORY_LIMIT = int(str(OPCDA.OPCCommon.get_env('OPC_DA_GATE_MEMORY_LIMIT', '1000')))
            self.OPC_DA_CLIENT_NAME = OPCDA.OPCCommon.get_env('OPC_DA_CLIENT',  'RobertOPCDA')  # client name
            self.OPC_DA_GATE_LOG = f"{OPCDA.OPCCommon.get_executable_folder()}/log/service.log".replace('\\', '/')

        def to_json(self):
            return self.__dict__

    class OPCDefine:

        SOURCE = {'cache': 1, 'device': 2}

        STATUS = (0, 'Running', 'Failed', 'NoConfig', 'Suspended', 'Test')

        BROWSER_TYPE = (0, 'Hierarchical', 'Flat')

        ACCESS_RIGHT = (0, 'Read', 'Write', 'Read/Write')

        QUALITY = ('Bad', 'Uncertain', 'Unknown', 'Good')

    class GroupEvents:
        """组事件"""

        def __init__(self):
            self.client = None

        def set_client(self, client):
            self.client = client

        def OnDataChange(self, TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps):
            if self.client and hasattr(self.client, 'callback_data_change_value'):
                self.client.callback_data_change_value('OnDataChange', TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps)

        def OnAsyncReadComplete(self, TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps, Errors):
            if self.client and hasattr(self.client, 'callback_data_change_value'):
                self.client.callback_data_change_value('OnAsyncReadComplete', TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps, Errors)

        def OnAsyncWriteComplete(self, TransactionID, NumItems, ClientHandles, Errors):
            if self.client and hasattr(self.client, 'callback_data_change_value'):
                self.client.callback_data_change_value('OnAsyncWriteComplete', TransactionID, NumItems, ClientHandles, None, None, None, Errors)

        def OnAsyncCancelComplete(self, CancelID):
            # Not working, not in VB either
            pass

    class ServerEvents:
        """服务器事件"""

        def __init__(self):
            self.client = None

        def set_client(self, client):
            self.client = client

        def OnServerShutDown(self, Reason):
            if self.client and hasattr(self.client, 'callback_shut_down'):
                self.client.callback_shut_down(Reason)

    class VtType(IntEnum):
        VT_EMPTY = 0
        VT_NULL = 1
        VT_I2 = 2
        VT_I4 = 3
        VT_R4 = 4
        VT_R8 = 5
        VT_CY = 6
        VT_DATE = 7
        VT_BSTR = 8
        VT_DISPATCH = 9
        VT_ERROR = 10
        VT_BOOL = 11
        VT_VARIANT = 12
        VT_UNKNOWN = 13
        VT_DECIMAL = 14
        VT_I1 = 16
        VT_UI1 = 17
        VT_UI2 = 18
        VT_UI4 = 19
        VT_I8 = 20
        VT_UI8 = 21
        VT_INT = 22
        VT_UINT = 23
        VT_VOID = 24
        VT_HRESULT = 25
        VT_PTR = 26
        VT_SAFEARRAY = 27
        VT_CARRAY = 28
        VT_USERDEFINED = 29
        VT_LPSTR = 30
        VT_LPWSTR = 31
        VT_RECORD = 36
        VT_FILETIME = 64
        VT_BLOB = 65
        VT_STREAM = 66
        VT_STORAGE = 67
        VT_STREAMED_OBJECT = 68
        VT_STORED_OBJECT = 69
        VT_BLOB_OBJECT = 70
        VT_CF = 71
        VT_CLSID = 72
        VT_TYPEMASK = 4095
        VT_VECTOR = 4096
        VT_ARRAY = 8192
        VT_BYREF = 16384
        VT_ILLEGAL = 65535
        VT_RESERVED = 32768

        @classmethod
        def _missing_(cls, value):
            return cls.VT_BSTR

    class OPCGroup:

        def __init__(self, name: str, opc_client, update_rate: int, is_subscribed: int = 1, is_active: int = 1, dead_band: int = 0, opc_timeout: float = 5.0):
            self.name = name
            self.update_rate = update_rate
            self.is_subscribed = is_subscribed
            self.is_active = is_active
            self.dead_band = dead_band
            self.opc_client = opc_client
            self.opc_timeout = opc_timeout

            self.exit_flag = False
            self.group = None
            self.group_event = None

            self.tags = {}  # tag: client_handle
            self.server_handles = {}    # tag: server_handle
            self.client_handle_values = {}   # client_handle: value
            self.client_handle = 0
            self.transaction_id = 0
            self.transaction_events = {}    # transaction_id: event

            self.group_use = OPCDA.OPCCommon.get_timestamp()
            self.group_data_change = OPCDA.OPCCommon.get_timestamp()

            self.create_group()

            Thread(target=self.pump_wait_msg, name="opcda pump", daemon=False).start()

        def __del__(self):
            self.exit()

        def exit(self):
            self.exit_flag = True
            if self.group_event:
                self.group_event.close()
            try:
                if self.opc_client and self.opc_client.is_connected() is True:
                    self.opc_client.OPCGroups.Remove(self.name)
            except:
                pass

            self.client_handle = 0
            self.transaction_id = 0
            self.tags = {}
            self.server_handles = {}
            self.client_handle_values = {}
            self.transaction_events = {}

        def info(self) -> dict:
            """组详情"""
            return {'name': self.name, 'update_rate': self.update_rate, 'size': len(self.tags), 'use': self.group_use, 'data_change': self.group_data_change}

        def create_group(self):
            """创建组"""
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            try:
                self.group = self.opc_client.OPCGroups.Add(self.name)
                self.group.IsSubscribed = self.is_subscribed
                self.group.IsActive = self.is_active
                self.group.DeadBand = self.dead_band
                self.group.UpdateRate = self.update_rate
                self.group_event = win32com.client.WithEvents(self.group, OPCDA.GroupEvents)
                self.group_event.set_client(self)
            except com_error as e:
                raise Exception(f"create group fail({self.get_error(e)})")

        def valid_items(self, tags: list):
            """检查tag是否有效"""
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            try:
                tags.insert(0, 0)
                return self.group.OPCItems.Validate(len(tags) - 1, tags)
            except com_error as e:
                raise Exception(f"valid item fail({self.get_error(e)})")

        def add_items(self, client_handles: list, valid_tags: list):
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            try:
                client_handles.insert(0, 0)
                valid_tags.insert(0, 0)
                return self.group.OPCItems.AddItems(len(client_handles) - 1, valid_tags, client_handles)
            except com_error as e:
                raise Exception(f"add items fail({self.get_error(e)})")

        def remove_items(self, server_handles: list):
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            try:
                server_handles.insert(0, 0)
                return self.group.OPCItems.Remove(len(server_handles) - 1, server_handles)
            except com_error as e:
                raise Exception(f"remove items fail({self.get_error(e)})")

        def sync_read(self, data_source: int, server_handles: dict):
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            try:
                item_tags = list(server_handles.keys())
                server_handles_ = list(server_handles.values())
                server_handles_.insert(0, 0)
                values, errors, qualities, timestamps = self.group.SyncRead(data_source, len(server_handles_) - 1, server_handles_)
                _errors = []
                for error in errors:
                    if error == 0:
                        _errors.append((True, ''))
                    else:
                        _errors.append((False, self.get_error_string(error)))
                self.parse_value(item_tags, values, _errors, qualities, timestamps)
            except com_error as e:
                raise Exception(f"sync read fail{self.get_error(e)}")

        def async_read(self, server_handles: dict):
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            try:
                opc_transaction_id = self.add_transaction()
                server_handles_ = list(server_handles.values())
                server_handles_.insert(0, 0)
                self.group.AsyncRead(len(server_handles_) - 1, server_handles_, Missing, opc_transaction_id)
                self.wait_transaction(opc_transaction_id, self.opc_timeout)
            except com_error as e:
                raise Exception(f"async read fail{self.get_error(e)}")

        def async_refresh(self, data_source: int):
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            try:
                opc_transaction_id = self.add_transaction()
                self.group.AsyncRefresh(data_source, opc_transaction_id)
                self.wait_transaction(opc_transaction_id, self.opc_timeout)
            except com_error as e:
                raise Exception(f"async refresh fail {self.get_error(e)}")

        def sync_write(self, server_handles: list, item_values: list, item_tags: list) -> dict:
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            results = {}
            try:
                server_handles.insert(0, 0)
                item_values.insert(0, 0)
                errors = self.group.SyncWrite(len(server_handles) - 1, server_handles, item_values)
                for i, item_tag in enumerate(item_tags):
                    if errors[i] == 0:
                        results[item_tag] = [True, '']
                    else:
                        results[item_tag] = [False, self.get_error_string(errors[i])]
            except com_error as e:
                raise Exception(f"sync write fail{self.get_error(e)}")
            return results

        def async_write(self, server_handles: list, item_values: list, item_tags: list):
            self.group_use = OPCDA.OPCCommon.get_timestamp()
            results = {}
            try:
                server_handles.insert(0, 0)
                item_values.insert(0, 0)
                opc_transaction_id = self.add_transaction()
                self.group.AsyncWrite(len(server_handles) - 1, server_handles, item_values, Missing, opc_transaction_id)
                result = [True, '']
                if self.wait_transaction(opc_transaction_id, self.opc_timeout):
                    result = [False, 'timeout']
                for item_tag in item_tags:
                    results[item_tag] = result
            except com_error as e:
                raise Exception(f"async write fail{self.get_error(e)}")
            return results

        def get_error_string(self, error_id: int):
            return self.opc_client.GetErrorString(error_id)

        def get_error(self, err) -> str:
            if not isinstance(err, com_error):
                return str(err)

            hr, msg, exc, arg = err.args

            if exc is None:
                error_str = str(msg)
            else:
                scode = exc[5]
                try:
                    opc_err_str = str(self.opc_client.GetErrorString(scode)).strip('\r\n')
                except:
                    opc_err_str = None

                try:
                    com_err_str = str(GetScodeString(scode)).strip('\r\n')
                except:
                    com_err_str = None

                if opc_err_str is None and com_err_str is None:
                    error_str = str(scode)
                elif opc_err_str == com_err_str:
                    error_str = opc_err_str
                elif opc_err_str is None:
                    error_str = com_err_str
                elif com_err_str is None:
                    error_str = opc_err_str
                else:
                    error_str = f'{opc_err_str} ({com_err_str})'
            return error_str

        def check_tag_exist(self, tag: str) -> bool:
            return tag in self.tags.keys()

        def add_tag(self, tag: str):
            self.client_handle = self.client_handle + 1
            self.tags[tag] = self.client_handle
            return self.client_handle

        def add_tag_server_handle(self, tag: str, server_handle):
            self.server_handles[tag] = server_handle

        def get_tag_server_handle(self, tag: str):
            return self.server_handles.get(tag)

        def get_tag_value(self, tag: str, property: Union[str, list] = 'value'):
            """获取标签属性"""
            if isinstance(property, str):
                 return self.client_handle_values.get(self.tags.get(tag), {}).get(property)
            elif isinstance(property, list):
                value = self.client_handle_values.get(self.tags.get(tag))
                if isinstance(value, dict):
                    return [value.get(p) for p in property]
            return None

        def add_transaction(self):
            if self.transaction_id >= 0xFFFF:
                self.transaction_id = 0
            self.transaction_id = self.transaction_id + 1
            self.transaction_events[self.transaction_id] = Event()
            return self.transaction_id

        def wait_transaction(self, transaction_id: int, timeout: Union[int, float]):
            event = self.transaction_events.pop(transaction_id, None)
            if event:
                event.wait(timeout)

        def set_transaction(self, transaction_id: int):
            event = self.transaction_events.pop(transaction_id, None)
            if event:
                event.set()

        def get_server_handles(self, tags: list) -> list:
            return [self.server_handles.get(tag) for tag in tags if tag in self.server_handles.keys()]

        def remove_tags(self, tags: list):
            for tag in tags:
                self.tags.pop(tag, None)
                self.server_handles.pop(tag, None)

        def parse_value(self, item_tags: list, values: list, errors: list, qualities: list, timestamps: list) -> int:
            success = 0
            now_str = OPCDA.OPCCommon.get_datetime_str()
            for i, item_tag in enumerate(item_tags):
                client_handle = self.tags.get(item_tag)
                if client_handle is not None:
                    if errors[i][0] is True:
                        success = success + 1
                    self.update_values(client_handle, value=str(values[i]), quality=OPCDA.OPCCommon.get_quality_string(qualities[i]), time=str(timestamps[i]), error=errors[i][1], update=now_str, transaction_id=-1)
            return success

        def update_values(self, client_handle: int, **kwargs):
            if client_handle not in self.client_handle_values.keys():
                self.client_handle_values[client_handle] = {}
            self.client_handle_values[client_handle].update(**kwargs)

        def callback_data_change_value(self, action: str, transaction_id: int, item_num: int, client_handles: list, values: list, qualities: list, timestamps: list, errors: Optional[list] = None):
            if transaction_id == 0:
                self.group_data_change = OPCDA.OPCCommon.get_timestamp()

            if action in ['OnDataChange', 'OnAsyncReadComplete']:
                now_str = OPCDA.OPCCommon.get_datetime_str()
                for i in range(item_num):
                    error = ''
                    if errors is not None and i < len(errors) and errors[i] != 0:
                        error = self.get_error_string(errors[i])    # TODO
                    self.update_values(client_handles[i], value=str(values[i]), quality=OPCDA.OPCCommon.get_quality_string(qualities[i]), time=str(timestamps[i]), error=error, update=now_str, transaction_id=transaction_id)
            self.set_transaction(transaction_id)    # 激活事件

        def pump_wait_msg(self):
            while self.exit_flag is False:
                try:
                    if self.opc_client and self.opc_client.is_connected() is True and len(self.tags) > 0:
                        PumpWaitingMessages()
                        continue
                except:
                    pass
                time.sleep(0.01)

    class OPCPyro:
        """OPC Pyro 实例"""

        def __init__(self, client_id: str, client_socket, client):
            self.pyro_client_id = client_id
            self.pyro_client_socket = client_socket
            self.pyro_client = client
            self.pyro_create_time = OPCDA.OPCCommon.get_timestamp()   # 创建时间
            logging.info(f"process({OPCDA.OPCCommon.get_current_pids()}): create session({client_id})")

        def __del__(self):
            self.exit('delete')

        def exit(self, reason: str = ''):
            if self.pyro_client:
                try:
                    self.pyro_client.close(True)
                except:
                    pass
                logging.info(f"process({OPCDA.OPCCommon.get_current_pids()}): close session ({self.pyro_client_id})({reason})")
            self.pyro_client = None

        def get_info(self) -> list:
            return [self.pyro_client_id, self.pyro_create_time, self.pyro_client.use() if self.pyro_client else self.pyro_create_time, self.get_client_socket()]

        def get_client_socket(self):
            return OPCDA.OPCCommon.convert_socket_address(self.pyro_client_socket.client_sock_addr)

    @pyro5_expose
    class OPCCom:

        def __init__(self, opc_class: str):
            self.opc_class = opc_class
            self.opc_client = None
            self.server_event = None
            self.opc_connected = False
            self.opc_error = None

            self.server: Optional[str] = None
            self.host: str = 'localhost'
            self.opc_prev_serv_time = None
            self.opc_ping_time = None
            self.initialize_client(opc_class)

        def __del__(self):
            self.exit()

        def exit(self):
            CoUninitialize()
            if self.server_event is not None:
                self.server_event.close()
            self.disconnect()

        def initialize_client(self, opc_class):
            try:
                CoInitializeEx(COINIT_MULTITHREADED)    # CoInitialize() 单线程
                self.opc_client = win32com.client.gencache.EnsureDispatch(opc_class, 0)
                self.server_event = win32com.client.WithEvents(self.opc_client, OPCDA.ServerEvents)
                self.server_event.set_client(self)
            except (Exception, com_error) as err:
                self.opc_error = Exception(err.__str__())
                raise self.opc_error

        def connect(self, server: Optional[str] = None, host: Optional[str] = 'localhost'):
            self.host = host if host is not None else 'localhost'
            self.server = server

            if self.opc_client is None:
                raise self.opc_error

            if self.opc_connected is False:
                try:
                    self.opc_client.Connect(self.server, self.host)
                except (Exception, com_error) as e:
                    raise Exception(f"connect fail({self.get_error(e)})")
                self.opc_connected = True
            return self.opc_connected

        def disconnect(self):
            if self.is_connected() is True:
                try:
                    self.opc_client.Disconnect()
                except:
                    pass
            self.opc_connected = False
            self.opc_client = None

        def add_group(self, group_name: str, update_rate: int, timeout: float, is_subscribed: int = 1, is_active: int = 1, dead_band: int = 0):
            return OPCDA.OPCGroup(group_name, self.opc_client, update_rate, is_subscribed, is_active, dead_band, timeout)

        def create_browser(self):
            return self.opc_client.CreateBrowser()

        def server_name(self):
            return self.opc_client.ServerName

        def get_opc_servers(self, opc_host):
            return self.opc_client.GetOPCServers(opc_host)

        def get_available_properties(self, tag):
            try:
                return list(self.opc_client.QueryAvailableProperties(tag))
            except com_error as err:
                raise Exception(f"properties fail({err.__str__()})")

        def get_tag_properties(self, tags: list, id: Optional[Union[str, list]] = None):
            """此方法返回标记的Properties。如果您想从服务器读取许多标记，建议只读取所需的属性ID。测试表明，这种方法非常缓慢，并导致一些服务器崩溃。"""
            try:
                tags, single_tag, valid = OPCDA.OPCCommon.type_check(tags)
                descriptions = []
                property_id = []

                if not valid:
                    raise Exception(f"tags must be a string or a list of strings")

                try:
                    id.remove(0)
                    include_name = True
                except:
                    include_name = False

                if id is not None:
                    if isinstance(id, list) or isinstance(id, tuple):
                        property_id = list(id)
                        single_property = False
                    else:
                        property_id = [id]
                        single_property = True

                    for i in property_id:
                        descriptions.append('Property id %d' % i)
                else:
                    single_property = False

                for tag in tags:
                    if id is None:
                        count, property_id, descriptions, datatypes = self.get_available_properties(tag)
                        tag_properties = list(map(lambda x, y: (x, y), property_id, descriptions))
                        property_id = [p for p, d in tag_properties if p > 0]
                        descriptions = [d for p, d in tag_properties if p > 0]

                    property_id.insert(0, 0)
                    values, errors = self.opc_client.GetItemProperties(tag, len(property_id) - 1, property_id)

                    property_id.pop(0)
                    values = [str(v) if type(v) == pywintypes.TimeType else v for v in values]

                    # Replace variant id with type strings
                    try:
                        i = property_id.index(1)
                        values[i] = OPCDA.OPCClient.VtType(values[i]).name
                    except:
                        pass

                    # Replace quality bits with quality strings
                    try:
                        i = property_id.index(3)
                        values[i] = OPCDA.OPCCommon.get_quality_string(values[i])
                    except:
                        pass

                    # Replace access rights bits with strings
                    try:
                        i = property_id.index(5)
                        values[i] = OPCDA.OPCDefine.ACCESS_RIGHT[values[i]]
                    except:
                        pass

                    if id is not None:
                        if single_property:
                            if single_tag:
                                tag_properties = values
                            else:
                                tag_properties = [values]
                        else:
                            tag_properties = list(map(lambda x, y: (x, y), property_id, values))
                    else:
                        tag_properties = list(map(lambda x, y, z: (x, y, z), property_id, descriptions, values))
                        tag_properties.insert(0, (0, 'Item ID (virtual property)', tag))

                    if include_name:
                        tag_properties.insert(0, (0, tag))
                    if not single_tag:
                        tag_properties = [tuple([tag] + list(p)) for p in tag_properties]

                    for p in tag_properties:
                        yield p
            except com_error as err:
                raise Exception(f"properties fail({self.get_error(err)})")

        def list_items(self, paths: str = '*', recursive: bool = False, flat: bool = False, include_type: bool = False):
            try:
                try:
                    browser = self.opc_client.CreateBrowser()
                except com_error as e:
                    raise Exception(f"no browser")

                paths, single, valid = OPCDA.OPCCommon.type_check(paths)
                if not valid:
                    raise Exception("paths must be a string or a list of strings")

                if len(paths) == 0:
                    paths = ['*']

                nodes = {}
                node_type = 'Leaf'
                for path in paths:
                    if flat:
                        browser.MoveToRoot()
                        browser.Filter = ''
                        browser.ShowLeafs(True)
                        pattern = re_compile('^%s$' % OPCDA.OPCCommon.wild2regex(path), IGNORECASE)
                        matches = filter(pattern.search, browser)
                        if include_type:
                            matches = [(x, node_type) for x in matches]
                        for node in matches:
                            yield node
                        continue

                    queue = [path]

                    while len(queue) > 0:
                        tag = queue.pop(0)

                        browser.MoveToRoot()
                        browser.Filter = ''
                        pattern = None

                        path_str = '/'
                        path_list = tag.replace('.', '/').split('/')
                        path_list = [p for p in path_list if len(p) > 0]
                        found_filter = False
                        path_postfix = '/'

                        for i, p in enumerate(path_list):
                            if found_filter:
                                path_postfix += p + '/'
                            elif p.find('*') >= 0:
                                pattern = re_compile('^%s$' % OPCDA.OPCCommon.wild2regex(p), IGNORECASE)
                                found_filter = True
                            elif len(p) != 0:
                                pattern = re_compile('^.*$')
                                browser.ShowBranches()

                                # Branch node, so move down
                                if len(browser) > 0:
                                    try:
                                        browser.MoveDown(p)
                                        path_str += p + '/'
                                    except:
                                        if i < len(path_list) - 1:
                                            return
                                        pattern = re_compile('^%s$' % OPCDA.OPCCommon.wild2regex(p), IGNORECASE)

                                else:
                                    p = '.'.join(path_list[i:])
                                    pattern = re_compile('^%s$' % OPCDA.OPCCommon.wild2regex(p), IGNORECASE)
                                    break

                        browser.ShowBranches()

                        if len(browser) == 0:
                            browser.ShowLeafs(False)
                            lowest_level = True
                            node_type = 'Leaf'
                        else:
                            lowest_level = False
                            node_type = 'Branch'

                        matches = filter(pattern.search, browser)

                        if not lowest_level and recursive:
                            queue += [path_str + x + path_postfix for x in matches]
                        else:
                            if lowest_level:
                                matches = [OPCDA.OPCCommon.exceptional(browser.GetItemID, x)(x) for x in matches]
                            if include_type:
                                matches = [(x, node_type) for x in matches]
                            for node in matches:
                                if node not in nodes:
                                    yield node
                                nodes[node] = True
            except com_error as err:
                raise Exception(f"list item fail({self.get_error(err)})")

        def servers(self, opc_host='localhost'):
            try:
                servers = self.opc_client.GetOPCServers(opc_host)
                return [s for s in servers if s is not None]
            except com_error as err:
                raise Exception(f"servers: {self.get_error(err)}")

        def info(self):
            try:
                info_list = []
                info_list.append(('Client Name', self.opc_client.ClientName))
                info_list.append(('OPC Server', self.opc_client.ServerName))
                info_list.append(('State', self.opc_status[self.opc_client.ServerState]))
                info_list.append(('Version', f"{self.opc_client.MajorVersion}.{self.opc_client.MinorVersion} (Build {self.opc_client.BuildNumber})"))

                try:
                    browser = self.opc_client.CreateBrowser()
                    browser_type = self.browser_types[browser.Organization]
                except:
                    browser_type = 'Not Supported'
                info_list.append(('Browser', browser_type))
                info_list.append(('Start Time', str(self.opc_client.StartTime)))
                info_list.append(('Current Time', str(self.opc_client.CurrentTime)))
                info_list.append(('Vendor', self.opc_client.VendorInfo))
                return info_list
            except com_error as err:
                raise Exception(f"info: {self._get_error(err)}")

        def ping(self, timeout: int = 5):
            try:
                if self.is_connected() is True:
                    opc_serv_time = self.opc_client.CurrentTime
                    opc_ping_time = datetime.now()   # 超时5秒
                    if opc_serv_time == self.opc_prev_serv_time and (self.opc_ping_time is not None and (opc_ping_time - self.opc_ping_time).total_seconds() >= timeout):    # 同一秒调用错误
                        return False
                    else:
                        self.opc_prev_serv_time = opc_serv_time
                        self.opc_ping_time = opc_ping_time
                        return True
            except com_error:
                pass
            return False

        def get_error_string(self, error_id: int):
            return self.opc_client.GetErrorString(error_id)

        def get_error(self, err) -> str:
            if not isinstance(err, com_error):
                return str(err)

            hr, msg, exc, arg = err.args

            if exc is None:
                error_str = str(msg)
            else:
                scode = exc[5]
                try:
                    opc_err_str = str(self.opc_client.GetErrorString(scode)).strip('\r\n')
                except:
                    opc_err_str = None

                try:
                    com_err_str = str(GetScodeString(scode)).strip('\r\n')
                except:
                    com_err_str = None

                if opc_err_str is None and com_err_str is None:
                    error_str = str(scode)
                elif opc_err_str == com_err_str:
                    error_str = opc_err_str
                elif opc_err_str is None:
                    error_str = com_err_str
                elif com_err_str is None:
                    error_str = opc_err_str
                else:
                    error_str = f'{opc_err_str} ({com_err_str})'
            return error_str

        @staticmethod
        def get_vt_type(datatype_number: int):
            return OPCDA.VtType(datatype_number).name

        def is_connected(self):
            return self.opc_connected

        def callback_shut_down(self, reason):
            self.opc_connected = False

    @pyro5_expose
    class OPCClient:

        def __init__(self, opc_class: Optional[str] = None, client_name: Optional[str] = None, **kwargs):
            self.kwargs = kwargs
            self.opc_client = None
            self.opc_name = ''
            self.opc_timeout = kwargs.get('timeout', 10)

            self.opc_class = opc_class if opc_class is not None else OPCDA.OPCCommon.get_env('OPC_DA_CLASS', 'OPC.Automation')
            self.opc_client_name = client_name if client_name is not None else OPCDA.OPCCommon.get_env('OPC_DA_CLIENT', 'RobertOPCDA')

            ############
            self.opc_groups = {}  # 组
            self.opc_infos = {}

            # service
            self.opc_svc = None
            self.opc_svc_client = None
            self.opc_prev_serv_time = None
            self.opc_svc_host = None
            self.opc_svc_port = None
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp())

        def __del__(self):
            self.exit()

        def exit(self):
            self.close(True)

        def track_resource(self):
            """服务监视对象"""
            current_context.track_resource(self)

        def set_svc_info(self, host: str, port: int, client_id, service: Optional[Any] = None):
            self.opc_svc_host = host
            self.opc_svc_port = port
            self.opc_svc = service
            self.update_infos(guid=client_id)

        # ####interface###########
        def update_infos(self, **kwargs):
            self.opc_infos.update(**kwargs)

        def get_info(self) -> dict:
            self.opc_infos.update(connected=self.is_connected(), groups=[group.info() for group in self.opc_groups.values()])
            return self.opc_infos

        def connect(self, name: Optional[str] = None, host: str = 'localhost') -> bool:
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp(), name=name, host=host)
            try:
                return self._get_client().connect(name, host)
            finally:
                if self.opc_svc:
                    logging.info(f"process({OPCDA.OPCCommon.get_current_pids()}): connect({self.get_info()})")

        def is_connected(self) -> bool:
            return self.opc_client and self.opc_client.is_connected()

        def guid(self):
            return self.get_info().get('guid')

        def use(self):
            """使用时间"""
            return self.get_info().get('used')

        def disconnect(self):
            if self.opc_client is not None:
                self.opc_client.disconnect()
            self.opc_client = None

        def close(self, del_object: bool = True):
            try:
                if self.opc_svc and self.opc_client:
                    logging.info(f"process({OPCDA.OPCCommon.get_current_pids()}): close({self.get_info()})")
                group_names = self.groups()
                for group_name in group_names:
                    self.remove_group(group_name)
                self.disconnect()
            except (com_error, Exception) as e:
                pass
            finally:
                # Remove this object from the open gateway service
                if self.opc_svc and del_object:
                    self.opc_svc.release_client(self.opc_svc_client)
                    self.opc_svc_client = None

        def groups(self) -> list:
            return sorted(list(self.opc_groups.keys()))

        def add_group(self, group_name: str, update_rate: int = 1000) -> bool:
            if group_name not in self.opc_groups.keys():
                try:
                    self.opc_groups[group_name] = self.opc_client.add_group(group_name, update_rate, self.opc_timeout)
                except (com_error, Exception) as err:
                    raise Exception(f"add group({group_name}) fail({self.get_error(err)})")
            return True

        def remove_group(self, group_name: str):
            group: OPCDA.OPCGroup = self.opc_groups.pop(group_name, None)
            if group is not None:
                group.exit()
            return True

        def add_items(self, group, item_tags: list):
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp())
            if group is not None:
                tags, single, valid = OPCDA.OPCCommon.type_check(item_tags)
                if valid is False:
                    raise Exception(f"tags must be a string or a list of strings")

                new_tags = []
                for item_tag in item_tags:
                    if group.check_tag_exist(item_tag) is False:
                        new_tags.append(item_tag)

                valid_tags = []
                client_handles = []
                error_msgs = {}

                if len(new_tags) > 0:
                    errors = group.valid_items(new_tags.copy())

                    for i, item_tag in enumerate(new_tags):
                        if errors[i] == 0:
                            valid_tags.append(item_tag)
                            opc_client_handle = group.add_tag(item_tag)
                            client_handles.append(opc_client_handle)
                        else:
                            error_msgs[item_tag] = group.get_error_string(errors[i])

                    if len(valid_tags) > 0:
                        server_handles, errors = group.add_items(client_handles.copy(), valid_tags.copy())
                        if len(server_handles) > 0:
                            valid_tags_tmp = []
                            for i, tag in enumerate(valid_tags):
                                if errors[i] == 0:
                                    valid_tags_tmp.append(tag)
                                    group.add_tag_server_handle(tag, server_handles[i])
                                else:
                                    error_msgs[tag] = group.get_error_string(errors[i])
                            return True if len(valid_tags_tmp) > 0 else False, valid_tags_tmp, error_msgs  # 只要有一个点添加成功即为正确
                        return False, [], dict.fromkeys(item_tags, 'add item fail')  # 添加点失败
                    return False, [], error_msgs  # 点都不正确
                return True, [], {}  # 无需额外添加点
            return False, [], dict.fromkeys(item_tags, 'group not exist')  # 组不存在

        def remove_items(self, group_name: str, item_tags: list):
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp())
            opc_group: OPCDA.OPCGroup = self.opc_groups.get(group_name)
            if opc_group is not None:
                tags, single, valid = OPCDA.OPCCommon.type_check(item_tags)
                if not valid:
                    raise Exception(f"tags must be a string or a list of strings")

                new_tags = []
                for item_tag in item_tags:
                    if opc_group.check_tag_exist(item_tag) is True:
                        new_tags.append(item_tag)

                if len(new_tags) > 0:
                    server_handles = opc_group.get_server_handles(new_tags)

                    if len(server_handles) > 0:
                        opc_group.remove_items(server_handles)

                    opc_group.remove_tags(new_tags)

        def read(self, group_name: str, item_tags: Optional[list] = None, action: str = '', source: str = 'cache', size: int = 100, interval: float = 0.1) -> dict:
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp())
            results = {}
            if self.is_connected() is True:
                opc_group: OPCDA.OPCGroup = self.opc_groups.get(group_name)
                if opc_group is not None:
                    item_tags = [] if item_tags is None else item_tags
                    if len(item_tags) > 0:
                        result, success, errors = self.add_items(opc_group, item_tags)
                        if len(errors) > 0:
                            results.update(errors)
                        if len(success) > 0:
                            action = 'sync'

                    valid_item_tags = []
                    if len(item_tags) > 0:
                        for item_tag in item_tags:
                            if opc_group.check_tag_exist(item_tag) is True:
                                valid_item_tags.append(item_tag)
                    else:
                        valid_item_tags = list(set(list(opc_group.tags.keys())))

                    #
                    if action == 'refresh':  # async异步刷新
                        results.update(self._read(group_name, valid_item_tags, action, source))
                    else:
                        item_tags_groups = OPCDA.OPCCommon.split_to_list(valid_item_tags, size)
                        for item_tags in item_tags_groups:
                            results.update(self._read(group_name, item_tags, action, source))
                            time.sleep(interval)
                else:
                    raise Exception(f"no group({group_name})")
            else:
                raise Exception(f"not connected")
            return results

        def write(self, group_name: str, items_values: dict, action: str = 'sync', size: int = 100, interval: float = 0.1) -> dict:
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp())
            results = {}
            if self.is_connected() is True:
                opc_group: OPCDA.OPCGroup = self.opc_groups.get(group_name)
                if opc_group is not None:
                    if len(items_values) > 0:
                        result, success, errors = self.add_items(opc_group, list(items_values.keys()))
                        if len(errors) > 0:
                            for k, v in errors.items():
                                results[k] = [False, v]
                        if len(success) > 0:
                            action = 'sync'

                    valid_item_values = {}
                    if len(items_values) > 0:
                        for item_tag in items_values.keys():
                            if opc_group.check_tag_exist(item_tag) is True:
                                valid_item_values[item_tag] = items_values[item_tag]

                    #
                    item_tags_values = OPCDA.OPCCommon.split_to_list(valid_item_values, size)
                    for item_tags_value in item_tags_values:
                        results.update(self._write(group_name, item_tags_value, action))
                        time.sleep(interval)
            else:
                raise Exception(f"not connected")
            return results

        def properties(self, tags: list, ids=None):
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp())
            if self.is_connected() is True:
                return list(self.opc_client.get_tag_properties(tags, ids))
            else:
                raise Exception(f"not connected")

        def list_items(self, paths: str = '*', recursive: bool = False, flat: bool = False, include_type: bool = False):
            self.update_infos(used=OPCDA.OPCCommon.get_timestamp())
            if self.is_connected() is True:
                return list(self.opc_client.list_items(paths, recursive, flat, include_type))
            else:
                raise Exception(f"not connected")

        def servers(self, opc_host='localhost'):
            return self._get_client().servers(opc_host)

        def info(self):
            info_list = []
            mode = 'OpenOPC' if self.opc_svc else 'DCOM'
            info_list.append(('Protocol', mode))
            if mode == 'OpenOPC':
                info_list.append(('',))
                info_list.append(('Gateway Host', f"{self.opc_svc_host}:{self.opc_svc_port}"))
                info_list.append(('Gateway Version', '1.4.0'))
            info_list.append(('Class', self.opc_class))
            info_list.append(('OPC Host', self.opc_svc_host))
            if self._get_client():
                info_list.extend(self.opc_client.info())
            return info_list

        def ping(self):
            if self.is_connected() is True:
                return self.opc_client.ping()
            else:
                return False

        ##########################
        def _get_client(self):
            if self.opc_client is None:
                opc_classs = self.opc_class.split(';')
                for i, opc_class in enumerate(opc_classs):
                    try:
                        opc_client = OPCDA.OPCCom(opc_class)
                        self.opc_client = opc_client
                        break
                    except (com_error, Exception) as err:
                        if i == len(opc_classs) - 1:
                            raise Exception(f"get client fail(EnsureDispatch '{opc_class}' fail: {self.get_error(err)})")
            return self.opc_client

        def get_error(self, err) -> str:
            if not isinstance(err, com_error):
                return str(err)

            hr, msg, exc, arg = err.args

            if exc is None:
                error_str = str(msg)
            else:
                scode = exc[5]
                try:
                    opc_err_str = str(self.opc_client.GetErrorString(scode)).strip('\r\n')
                except:
                    opc_err_str = None

                try:
                    com_err_str = str(GetScodeString(scode)).strip('\r\n')
                except:
                    com_err_str = None

                if opc_err_str is None and com_err_str is None:
                    error_str = str(scode)
                elif opc_err_str == com_err_str:
                    error_str = opc_err_str
                elif opc_err_str is None:
                    error_str = com_err_str
                elif com_err_str is None:
                    error_str = opc_err_str
                else:
                    error_str = f'{opc_err_str} ({com_err_str})'
            return error_str

        def _read(self, group_name: str, item_tags: Optional[list] = None, action: str = '', source: str = 'cache') -> dict:
            results = {}
            if self.is_connected() is True:
                opc_group: OPCDA.OPCGroup = self.opc_groups.get(group_name)
                if opc_group is not None:
                    item_tags = [] if item_tags is None else item_tags
                    if action == '':  # 订阅变化数据
                        pass
                    elif action in ['sync', 'async']:  # sync同步读取
                        data_source = OPCDA.OPCDefine.SOURCE.get(source, 1)
                        server_handles = {}
                        for item_tag in item_tags:
                            server_handle = opc_group.get_tag_server_handle(item_tag)
                            if server_handle is not None:
                                server_handles[item_tag] = server_handle

                        if len(server_handles) > 0:
                            if action == 'sync':
                                opc_group.sync_read(data_source, server_handles)
                            elif action == 'async':
                                opc_group.async_read(server_handles)
                    elif action == 'refresh':  # async异步读取
                        data_source = OPCDA.OPCDefine.SOURCE.get(source, 1)
                        opc_group.async_refresh(data_source)

                    # 返回值
                    for item_tag in item_tags:
                        value = opc_group.get_tag_value(item_tag, ['value', 'quality', 'time', 'error', 'update'])    # v, status, time, error, update
                        if value is not None:
                            results[item_tag] = value
            return results

        def _write(self, group_name: str, items_values: dict, action: str = 'sync'):
            results = {}
            if self.is_connected() is True:
                opc_group: OPCDA.OPCGroup = self.opc_groups.get(group_name)
                if opc_group is not None:
                    if action in ['sync', 'async']:  # sync同步读取
                        server_handles = []
                        item_tags = []
                        values = []
                        for item_tag in items_values.keys():
                            server_handle = opc_group.get_tag_server_handle(item_tag)
                            if server_handle is not None:
                                item_tags.append(item_tag)
                                server_handles.append(server_handle)
                                values.append(items_values[item_tag])

                        if len(server_handles) > 0:
                            if action == 'sync':
                                results.update(opc_group.sync_write(server_handles.copy(), values.copy(), item_tags.copy()))
                            elif action == 'async':
                                results.update(opc_group.async_write(server_handles.copy(), values.copy(), item_tags.copy()))
            return results

    @pyro5_expose
    class OPCServer:

        def __init__(self, opc_config: Optional[Any] = None):
            self.opc_config: OPCDA.OPCConfig = opc_config   # 配置信息
            self.clients: dict = {}     # id: OPCPyro
            self.connections = {}       # 连接： ID
            self.lock = Lock()

        def client_disconnected(self, connection):
            """
                客户端关闭事件
                注意实际调用时候是另起一个连接，实际上就是两次连接
            """
            for guid in [r.guid() for r in connection.tracked_resources]:
                self.force_close(guid, 'disconnected')

        def get_clients(self) -> list:
            return [client.get_info() for client_id, client in self.clients.items()]

        def close_all_sessions(self, reason: str = ''):
            for guid in list(self.clients.keys()):
                self.force_close(guid, reason)

        def force_close(self, guid: Union[str, list], reason: str = ''):
            """强制关闭连接"""
            if isinstance(guid, str):
                guid = [guid]

            for g in guid:
                with self.lock:
                    obj: OPCDA.OPCPyro = self.clients.pop(g, None)
                    if obj is not None:
                        obj.exit(reason)

        def close_by_reason(self, reason: str = ''):
            """根据原因事件分别关闭"""
            try:
                all_clients = self.get_clients()
                if reason == 'limit':
                    if len(all_clients) >= self.opc_config.OPC_DA_GATE_LIMIT_SIZE:
                        reason = 'limit'
                        stale_clients = sorted(all_clients, key=lambda s: s[2])[:-self.opc_config.OPC_DA_GATE_LIMIT_SIZE]
                        self.force_close([client[0] for client in stale_clients], reason)
                elif reason == 'timeout':
                    stale_clients = [s for s in all_clients if (OPCDA.OPCCommon.get_timestamp() - s[2]) > self.opc_config.OPC_DA_GATE_TIMEOUT]
                    self.force_close([client[0] for client in stale_clients], reason)
                elif reason == 'exit':
                    self.close_all_sessions(reason)
            except Exception as e:
                pass

        def cleanup_clients(self, reasons: list):
            for reason in reasons:
                self.close_by_reason(reason)

        def create_client(self):
            """在Pyro服务器中创建新实例"""
            if len(self.clients) > self.opc_config.OPC_DA_GATE_LIMIT_SIZE:
                raise Exception(f"Connection reached maximum limit({self.opc_config.OPC_DA_GATE_LIMIT_SIZE})")

            opc_da_client = OPCDA.OPCClient(self.opc_config.OPC_DA_CLASS, self.opc_config.OPC_DA_CLIENT_NAME)
            uri = self._pyroDaemon.register(opc_da_client)
            opc_client_id = uri.object
            opc_da_client.set_svc_info(self.opc_config.OPC_DA_GATE_HOST, self.opc_config.OPC_DA_GATE_PORT, opc_client_id, self)
            self.clients[opc_client_id] = OPCDA.OPCPyro(opc_client_id, Pyro5.client.current_context, opc_da_client)
            return opc_da_client

        def release_client(self, obj):
            """在Pyro服务器中释放实例"""
            if obj is not None:
                self._pyroDaemon.unregister(obj)
                with self.lock:
                    self.clients.pop(obj.guid(), None)
                del obj

        def get_info(self) -> dict:
            """获取进程信息"""
            info: dict = dict()
            info['config'] = self.opc_config.to_json()
            info.update(OPCDA.OPCCommon.get_current_process())
            return info

        def restart(self):
            """重启"""
            return OPCDA.OPCCommon.restart_service(self.opc_config.OPC_DA_SERVICE_NAME)

    class OPCPyroServer:

        def __init__(self, opc_config):
            self.opc_config = opc_config
            self.pyro_daemon = None
            self.pyro_event = Event()
            self.pyro_thread = None
            self.pyro_exit = False

        def __del__(self):
            self.exit()

        def exit(self):
            self.pyro_event.set()
            if self.pyro_thread:
                self.pyro_thread.join()
            self.pyro_exit = True
            if self.pyro_daemon:
                self.pyro_daemon.shutdown()

        def create_clean_thread(self):
            self.pyro_thread = Thread(target=self.inactive_cleanup)
            self.pyro_thread.start()

        def delay(self, second: int):
            while self.pyro_exit is False and second > 0:
                self.pyro_event.wait(1)
                second = second - 1

        def inactive_cleanup(self):
            """退出清除"""
            pyro_server = None
            while self.pyro_exit is False:
                try:
                    if pyro_server is None:
                        pyro_server = OPCDA(self.opc_config.OPC_DA_GATE_HOST, self.opc_config.OPC_DA_GATE_PORT)
                    self.delay(10)
                    if self.pyro_event.is_set():
                        pyro_server.cleanup_sessions(['exit'])
                        self.pyro_event.clear()
                        return
                    else:
                        pyro_server.cleanup_sessions(['timeout', 'limit'])
                except Exception as e:
                    logging.error(f"process({OPCDA.OPCCommon.get_current_pids()}): inactive_cleanup fail({e.__str__()})")
                    pyro_server = None
                    self.delay(30)

        def run_loop(self):
            self.pyro_daemon = Daemon(host=self.opc_config.OPC_DA_GATE_HOST, port=self.opc_config.OPC_DA_GATE_PORT)
            self.pyro_daemon.register(OPCDA.OPCServer(self.opc_config), objectId="opc")
            self.create_clean_thread()
            self.pyro_daemon.requestLoop()

        def run_foreground(self):
            self.pyro_daemon = Daemon(host=self.opc_config.OPC_DA_GATE_HOST, port=self.opc_config.OPC_DA_GATE_PORT)
            server = OPCDA.OPCServer(self.opc_config)
            self.pyro_daemon.register(server, objectId="opc")
            self.pyro_daemon.clientDisconnect = server.client_disconnected
            self.create_clean_thread()
            self.pyro_daemon.requestLoop()

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host = 'localhost' if host is None else host
        self.port = 8810 if host is None else port
        self.proxy = None

    def __del__(self):
        self.exit()

    def exit(self):
        if self.proxy is not None:
            del self.proxy
        self.proxy = None

    def get_uri(self, prefix: str = 'PYRO:opc'):
        return f"{prefix}@{self.host}:{self.port}"

    def get_proxy(self, proxy_id: str = ''):
        if self.proxy is None:
            with Proxy(self.get_uri()) as proxy:
                if len(proxy_id) > 0:
                    proxy._pyroHandshake = proxy_id
                    proxy._pyroBind()
                self.proxy = proxy
        return self.proxy

    def call_method(self, func_name, *args, **kwargs):
        proxy = self.get_proxy()
        if hasattr(proxy, func_name):
            return getattr(proxy, func_name)(*args, **kwargs)
        raise Exception(f"call method({func_name}) fail")

    def get_sessions(self):
        return self.get_proxy().get_clients()

    def close_session(self, guid):
        return self.get_proxy().force_close(guid)

    def close_all_sessions(self):
        return self.get_proxy().close_all_sessions()

    def cleanup_sessions(self, reasons: list):
        return self.get_proxy().cleanup_clients(reasons)

    def open_client(self):
        client = self.get_proxy().create_client()
        client.track_resource()
        return client

    def get_info(self):
        return self.get_proxy().get_info()

    def restart(self):
        return self.get_proxy().restart()


class IOTOPCDA(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.client = None

    def exit(self):
        self.exit_flag = True
        self.close()
        self.reinit()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': True, 'name': 'OPC标签' if lan == 'ch' else 'tag'.upper(), 'code': 'point_tag', 'type': 'string', 'default': 'Bucket Brigade.Int2', 'enum': [], 'tip': ''},
                {'required': False, 'name': 'OPC标签类型' if lan == 'ch' else 'type'.upper(), 'code': 'point_type', 'type': 'string', 'default': 'VT_R4', 'enum': [], 'tip': ''},
                {'required': False, 'name': 'OPC标签描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
                ])

        elif type in ['config', 'scan']:
            templates.extend([
                {'required': True, 'name': 'OPC服务名称' if lan == 'ch' else 'Server Name', 'code': 'server', 'type': 'string', 'default': 'Matrikon.OPC.Simulation.1', 'enum': [], 'tip': ''},
                {'required': True, 'name': 'OPC服务地址' if lan == 'ch' else 'Host', 'code': 'host', 'type': 'string', 'default': 'localhost:7766', 'enum': [], 'tip': ''},
                {'required': False, 'name': '读取方式' if lan == 'ch' else 'Action', 'code': 'action', 'type': 'string', 'default': 'sync', 'enum': ['', 'sync', 'async'], 'tip': ''},
                {'required': True, 'name': 'OPC组名' if lan == 'ch' else 'Group', 'code': 'group', 'type': 'string', 'default': 'opc1', 'enum': [], 'tip': ''},
                {'required': True, 'name': 'OPC最大点位限制' if lan == 'ch' else 'Limit', 'code': 'limit', 'type': 'int', 'default': 10000, 'enum': [], 'tip': ''},
                {'required': True, 'name': '单次读取限制' if lan == 'ch' else 'Read Limit', 'code': 'read_limit', 'type': 'int', 'default': 1000, 'enum': [], 'tip': ''},
                {'required': True, 'name': '更新速率(ms)' if lan == 'ch' else 'Update Rate(ms)', 'code': 'update_rate', 'type': 'int', 'default': 500, 'enum': [], 'tip': ''}
            ])

            if type == 'scan':
                templates.extend([
                    {'required': True, 'name': '目录' if lan == 'ch' else 'Path'.title(), 'code': 'path', 'type': 'string', 'default': '*', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '是否读取属性' if lan == 'ch' else 'include property'.title(), 'code': 'include_property', 'type': 'bool', 'default': True, 'enum': [], 'tip': ''}
                ])
        return templates
    
    # ##API#############
    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        names = kwargs.get('names', list(self.points.keys()))
        self.update_results(names, True, None)

        read_items = []
        for name in names:
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                if tag is not None and tag not in read_items:
                    read_items.append(tag)

        self._read(sorted(read_items))

        for name in names:
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                value = self._get_value(name, tag)
                if value is not None:
                    self.update_results(name, True, value)
            else:
                self.update_results(name, False, 'UnExist')
        return self.get_results(**kwargs)

    def write(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        write_items = {}
        values = kwargs.get('values', {})
        for name, value in values.items():
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                if tag is not None:
                    write_items[tag] = value

        self._write(write_items)

        for name, value in values.items():
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                result = self.get_device_property(self.configs.get('server'), tag, [self.get_write_quality, self.get_write_result])
            else:
                result = [False, 'Point UnExist']

            results[name] = result
            if result[0] is not True:
                self.logging(content=f"write value({name}) fail({result[1]})", level='ERROR', source=name)
        return results

    def ping(self, **kwargs) -> bool:
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        return self._get_client() and self.client.ping()

    def scan(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        if self._get_client():
            path = kwargs.get('path', '*')
            include_property = kwargs.get('include_property', False)
            self.logging(content=f"scan opc({path})")
            points = self._get_client().list_items(paths=path, flat=True)  # flat=True
            self.logging(content=f"scan opc flags({len(points)})")
            for point in points:
                params = {'point_name': point, 'point_name_alias': point, 'point_writable': True, 'point_tag': point, 'point_type': '', 'point_description': '', 'point_value': ''}
                if include_property is True:
                    properties = self._get_client().properties(tags=[point])
                    self.logging(content=f"scan opc item({point}) property({len(properties)})")
                    for property in properties:
                        if len(property) >= 3:
                            if property[2] == 'Item Canonical DataType':
                                params['point_type'] = OPCDA.VtType(property[3]).name
                            elif property[2] == 'Item Value':
                                params['point_value'] = str(property[3])
                            elif property[2] == 'Item Description':
                                params['point_description'] = property[3]
                results[point] = self.create_point(**params)
        self.update_info(scan=len(results))
        return results

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = []
        if self._get_client(False):
            results = self._get_client(False).servers(opc_host=self.configs.get('host', 'localhost'))
        self.update_info(discover=len(results))
        return results

    ###################

    def _get_host_info(self) -> Optional[dict]:
        host = self.configs.get('host')
        if len(host) > 0:
            host_info = host.split(':')
            if len(host_info) == 1:
                return {'com': True, 'ip': host_info[0], 'port': None, 'server': self.configs.get('server'), 'group': self.configs.get('group')}
            elif len(host_info) == 2:
                return {'com': False, 'ip': host_info[0], 'port': int(float(host_info[1])), 'server': self.configs.get('server'), 'group': self.configs.get('group')}
        return None

    def _release_client(self):
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            logging.error(f'release client fail({e.__str__()})')
        finally:
            self.client = None

    def _get_client(self, auto_connect: bool = True):
        try:
            if self.client:
                if self.client.ping() is True:
                    return self.client
                self._release_client()
        except Exception as e:
            self.client = None

        if self.client is None:
            info = self._get_host_info()
            if isinstance(info, dict):
                try:
                    if info.get('com') is True:
                        self.client = OPCDA.OPCClient()
                    else:
                        self.client = OPCDA(info.get('ip'), info.get('port')).open_client()

                    if auto_connect is True:
                        self.client.connect(info.get('server'), info.get('host'))
                        self.logging(content=f"connect opc({info.get('host')}-{info.get('server')})")

                        self.client.add_group(self.configs.get('group'), self.configs.get('update_rate'))
                        self.logging(content=f"add opc group({self.configs.get('group')})")
                except Exception as e:
                    self._release_client()
                    raise Exception(f"connect fail({e.__str__()})")
        return self.client

    def _read(self, tags: list):
        try:
            if len(tags) > 0 and self._get_client():
                chunk_tags = IOTBaseCommon.chunk_list(tags, self.configs.get('read_limit', 100))
                for chunk_tag in chunk_tags:
                    self.delay(0.0001)
                    values = self.client.read(self.configs.get('group'), chunk_tag, self.configs.get('action'))
                    for tag, value in values.items():
                        if isinstance(value, list):
                            if len(value) >= 4:
                                (v, status, time, error, update) = value
                                if status == 'Good':
                                    self.update_device(self.configs.get('server'), tag, **self.gen_read_write_result(True, v))
                                else:
                                    self.update_device(self.configs.get('server'), tag, **self.gen_read_write_result(False, f"[{status}] {error}"))
                        else:
                            self.update_device(self.configs.get('server'), tag, **self.gen_read_write_result(False, f"{value}"))
        except Exception as e:
            for tag in tags:
                self.update_device(self.configs.get('server'), tag, **self.gen_read_write_result(False, e.__str__()))

    def _get_value(self, name: str, tag: str):
        try:
            [result, value] = self.get_device_property(self.configs.get('server'), tag, [self.get_read_quality, self.get_read_result])
            if result is True:
                if value is not None:
                    return value
                else:
                    raise Exception(f"value is none")
            else:
                raise Exception(str(value))
        except Exception as e:
            self.update_results(name, False, e.__str__())
        return None

    def _write(self, set_values: dict):
        try:
            if len(set_values) > 0 and self._get_client():
                values = self.client.write(self.configs.get('group'), set_values)
                for tag, [status, result] in values.items():
                    self.update_device(self.configs.get('server'), tag, **self.gen_read_write_result(status, result, False))
        except Exception as e:
            for tag in set_values.keys():
                self.update_device(self.configs.get('server'), tag, **self.gen_read_write_result(False, e.__str__(), False))

    def close(self):
        self._release_client()

    def info(self, **kwargs):
        if self._get_client():
            return self.client.get_info()

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_opcda.py({pos})"

    def copy_new_self(self):
        """复制自身"""
        return self
        return IOTOPCDA(**self.kwargs)
