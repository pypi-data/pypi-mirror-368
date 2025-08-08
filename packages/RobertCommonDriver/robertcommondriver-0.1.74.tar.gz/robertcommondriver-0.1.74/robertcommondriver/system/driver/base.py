from typing import Dict, Any, Callable, Optional
from abc import abstractmethod
from datetime import datetime
from threading import Timer, Thread
from ipaddress import ip_network, ip_address
from psutil import net_if_addrs
from re import compile as re_compile


class BaseCommon:

    class RepeatingTimer:

        def __init__(self, interval, function, args=None, kwargs=None):
            self.interval = interval
            self.function = function
            self.args = args if args is not None else []
            self.kwargs = kwargs if kwargs is not None else {}
            self._should_continue = False
            self.is_running = False
            self.thread = None

        def is_alive(self):
            return self._should_continue

        def _handle_function(self):
            self.is_running = True
            self.function(self.args, self.kwargs)
            self.is_running = False
            self._start_timer()

        def _start_timer(self):
            if self._should_continue:  # Code could have been running when cancel was called.
                self.thread = Timer(self.interval, self._handle_function)
                self.thread.start()

        def start(self):
            if not self._should_continue and not self.is_running:
                self._should_continue = True
                self._start_timer()

        def cancel(self):
            if self.thread is not None:
                self._should_continue = False  # Just in case thread is running and cancel fails.
                self.thread.cancel()

    class SimpleTimer:

        def __init__(self):
            self.timer = None

        def is_running(self):
            return self.timer and self.timer.is_alive()

        def run(self, interval: int, function: Callable, args=None, kwargs=None):
            if self.is_running():
                if kwargs.get('force', False) is False:
                    raise Exception(f"timer is running, please cancel")
                else:
                    self.cancel()
            self._run_timer(interval, function, args, kwargs)

        def _run_timer(self, interval: int, function: Callable, args=None, kwargs=None):
            self.timer = Timer(interval, function, args, kwargs)
            self.timer.start()

        def cancel(self):
            if self.is_running():
                self.timer.cancel()
            self.timer = None

    @staticmethod
    def function_thread(fn: Callable, daemon: bool, name: Optional[str] = None, *args, **kwargs):
        return Thread(target=fn, name=name, args=args, kwargs=kwargs, daemon=daemon)

    @staticmethod
    def chunk_list(values: list, num: int):
        for i in range(0, len(values), num):
            yield values[i: i + num]

    @staticmethod
    def get_datetime() -> datetime:
        return datetime.now()

    @staticmethod
    def get_datetime_str() -> str:
        return BaseCommon.get_datetime().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def change_local_ip(ip: str) -> str:
        m = re_compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
        if m:
            (_ip, net, port) = m.groups()
            if _ip is not None and net is not None:
                __ip = f"{_ip}/{net}"
                ip_start = ip_address(str(ip_network(__ip, False)).split('/')[0])
                ip_end = ip_network(__ip, False).broadcast_address
                for k, v in net_if_addrs().items():
                    for item in v:
                        if item[0] == 2:
                            item_ip = item[1]
                            if ':' not in item_ip:
                                item_ip = ip_address(item_ip)
                                if ip_start <= item_ip < ip_end:
                                    return ip.replace(_ip, str(item_ip))
        return ip


# Point base class
class BasePoint(object):

    def __init__(self, point_source: str, point_writable: bool, point_name: str, point_description: str = '', point_sample_value: Any = None):
        self.point_writable = point_writable
        self.point_source = point_source
        self.point_name = point_name
        self.point_description = point_description
        self.point_sample_value = point_sample_value
        self.point_value = None

    # get point_source
    @property
    def get_point_source(self):
        return self.point_source

    # get point_description
    @property
    def get_point_description(self):
        return self.point_description

    # get point_name
    @property
    def get_point_name(self):
        return self.point_name

    # get point_writable
    @property
    def get_point_writable(self):
        return self.point_writable


PointTableDict = Dict[str, Dict[str, Any]]


class BaseDriver(object):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        self.dict_config = dict_config
        self.dict_point = dict_point
        self.callbacks = {}

    def __del__(self):
        self.exit()

    def exit(self):
        pass

    @abstractmethod
    def get_points(self, dict_point: dict = {}) -> tuple:
        pass

    def set_points(self, dict_points: dict) -> dict:
        pass

    def reset_config(self, dict_config: dict):
        self.dict_config = dict_config

    def reset_point(self, dict_point: dict):
        self.dict_point = dict_point

    def ping_target(self):
        return True

    @abstractmethod
    def configure(self):
        pass

    def search_points(self) -> dict:
        return {}

    def enable_logging(self, callback: Callable = None):
        self.callbacks['debug_log'] = callback

    def set_call_result(self, call_method: str, **kwargs):
        if isinstance(self.callbacks, dict):
            call_method = self.callbacks.get(call_method)
            if isinstance(call_method, Callable):
                call_method(**kwargs)
