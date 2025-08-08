from typing import Dict, List, Any
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
from xml.dom.minidom import parseString
from .base import IOTBaseCommon, IOTDriver


class IOTObix(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.is_base_url, self.origin_url, self.base_url = self.get_url()
        self.watch = {}
        self.converters = {
            'int': int,
            'bool': lambda x: x.lower() == "true",
            'real': float,
            'enum': self._enum_value_handler,
        }

    def exit(self):
        self.exit_flag = True
        self._del_watch()
        self.reinit()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                    {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                    {'required': True, 'name': 'Url' if lan == 'ch' else 'url'.upper(), 'code': 'point_url', 'type': 'string', 'default': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CHW_ENT/', 'enum': [], 'tip': ''},
                    {'required': False, 'name': '类型' if lan == 'ch' else 'type'.upper(), 'code': 'point_type', 'type': 'string', 'default': 'real', 'enum': [], 'tip': ''},
                    {'required': False, 'name': '描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                    {'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
            ])
        elif type in ['config', 'scan']:
            templates.extend([
                {'required': True, 'name': '服务地址' if lan == 'ch' else 'Url', 'code': 'url', 'type': 'string', 'default': 'http://XX.XX.XX.XX', 'enum': [], 'tip': ''},
                {'required': True, 'name': '用户名' if lan == 'ch' else 'Username', 'code': 'username', 'type': 'string', 'default': 'Monitor', 'enum': [], 'tip': ''},
                {'required': True, 'name': '密码' if lan == 'ch' else 'Password', 'code': 'password', 'type': 'string', 'default': 'Monitor123', 'enum': [], 'tip': ''},
                {'required': True, 'name': '过期时间' if lan == 'ch' else 'Reltime', 'code': 'reltime', 'type': 'string', 'default': 'PT30M', 'enum': [], 'tip': ''},
                {'required': True, 'name': '最大点位限制' if lan == 'ch' else 'Limit', 'code': 'limit', 'type': 'int', 'default': 10000, 'enum': [], 'tip': ''},
                {'required': True, 'name': '读取超时(s)' if lan == 'ch' else 'Timeout(s)', 'code': 'timeout', 'type': 'int', 'default': 30, 'enum': [], 'tip': ''}])
        return templates

    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        names = kwargs.get('names', list(self.points.keys()))
        self.update_results(names, True, None)

        read_items = []
        for name in names:
            point = self.points.get(name)
            if point:
                point_url = point.get('point_url')
                if point_url is not None:
                    if not point_url.endswith('/'):
                        point_url = f'{point_url}/'
                    if not point_url.endswith('/out/'):
                        point_url = f"{point_url}out/"

                    point.set('point_url', point_url)
                    if point_url not in read_items:
                        read_items.append(point_url)

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                point_url = point.get('point_url')
                point_type = point.get('point_type')
                value = self.get_value(name, point_url, point_type)
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
                point_url = point.get('point_url')
                point_type = point.get('point_url')
                if point_url is not None and point_url is not None:
                    results[name] = self._write(point_url, point_type, value)
            else:
                results[name] = [False, 'UnExist']
        return results

    def get_url(self):
        url = self.configs.get('url')
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        is_base_url = base_url == url
        origin_url = url if is_base_url is False else f'{url}/obix/config/'
        return is_base_url, origin_url, base_url

    def scan(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        job = IOTBaseCommon.RepeatThreadPool(kwargs.get('limit', 1), self._fetch, self._fetch_back)
        job.submit_task(self._fetch, self._fetch_back, (self.origin_url, results), job=job)
        job.done()
        self.update_info(scan=len(results))
        return results

    def ping(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        return IOTBaseCommon.send_request(url=f"{self.base_url}/obix", method='GET', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5)).success

    def _enum_value_handler(self, v):
        try:
            return int(v)
        except Exception:
            return str(v)

    def _set_reltime(self):
        reltime = self.configs.get('reltime', '')
        if len(reltime) > 0:
            url = f"{self.base_url}/obix/watchService/defaultLeaseTime/"
            self.logging(content=f"set reltime({url})", pos=self.stack_pos)
            response = IOTBaseCommon.send_request(url=url, method='GET', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
            if response.success is True:
                document = parseString(response.data)
                elements = document.getElementsByTagName("reltime")
                for element in elements:
                    if element.getAttribute("val") == reltime:
                        return True
                response = IOTBaseCommon.send_request(url=url, method='PUT', data=f'<reltime val="{reltime}"/>', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
                if response.success is True:
                    document = parseString(response.data)
                    elements = document.getElementsByTagName("reltime")
                    for element in elements:
                        if element.getAttribute("val") == reltime:
                            return True
        return False

    def _add_watch(self):
        if 'url' not in self.watch.keys():
            self.logging(content=f"add watch({self.base_url}/obix/watchService/make/)", pos=self.stack_pos)
            response = IOTBaseCommon.send_request(url=f"{self.base_url}/obix/watchService/make/", method='POST', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
            if response.success is True:
                document = parseString(response.data)
                elements = document.getElementsByTagName("obj")
                for element in elements:
                    self.watch['url'] = element.getAttribute("href")
                    return True
                raise Exception(f'add watch fail({response.data})')
            else:
                raise Exception(f'add watch fail({response.msg})')
        return False

    def _add_points(self, new_items: list):
        if 'url' in self.watch.keys():
            items = self.watch.get('items', {})
            add_items = []
            _add_items = []
            for new_item in new_items:
                if new_item not in items.keys():
                    add_items.append(f'<uri val="{new_item}" />')
                    _add_items.append(new_item)

            if len(add_items) > 0:
                data = f'<obj is="obix:WatchIn"><list names="hrefs">{"".join(add_items)}</list></obj>'.encode('utf-8')  # .encode("utf-8").decode("latin1")
                self.logging(content=f"add point({self.watch.get('url')}add/)", pos=self.stack_pos)
                response = IOTBaseCommon.send_request(url=f"{self.watch.get('url')}add/", headers={'Content-Type': 'application/xml'}, data=data, method='POST', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
                if response.success is True:
                    document = parseString(response.data)
                    elements = document.getElementsByTagName("obj")
                    for element in elements:
                        if element.getAttribute('is') == 'obix:WatchOut':
                            list_nodes = element.getElementsByTagName("list")
                            count = 0
                            for list_node in list_nodes:
                                for node in list_node.childNodes:
                                    if node.nodeType == node.ELEMENT_NODE:
                                        if node.tagName == 'err':
                                            self.update_device(self.base_url, node.getAttribute('href'), **self.gen_read_write_result(False, f"add point fail({node.getAttribute('is')})"))
                                        else:
                                            if 'items' not in self.watch.keys():
                                                self.watch['items'] = {}
                                            self.watch['items'][node.getAttribute('href').replace(self.base_url, '')] = None
                                            count = count + 1
                            self.logging(content=f"add point success({count})", pos=self.stack_pos)
                            return True
                else:
                    for item in _add_items:
                        self.update_device(self.base_url, item, **self.gen_read_write_result(False, f'add point fail({response.msg})'))
        return False

    def _del_watch(self):
        try:
            if 'url' in self.watch.keys():
                self.logging(content=f"delete watch({self.watch.get('url')}delete/)", pos=self.stack_pos)
                response = IOTBaseCommon.send_request(url=f"{self.watch.get('url')}delete/", data='', method='POST', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
        finally:
            self.watch = {}

    def _format_value(self, url: str, value):
        if 'value' not in self.watch.keys():
            self.watch['value'] = {}
        self.watch['value'][url] = value

    def _pool_refresh(self):
        if 'url' in self.watch.keys():
            self.logging(content=f"pool refresh({self.watch.get('url')}pollRefresh/)", pos=self.stack_pos)
            response = IOTBaseCommon.send_request(url=f"{self.watch.get('url')}pollRefresh/", data='', method='POST', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
            if response.success:
                document = parseString(response.data)
                err_elements = document.getElementsByTagName("err")
                if len(err_elements) > 0:
                    raise Exception(f"pool refresh Fail({err_elements[0].getAttribute('is')})")
                elements = document.getElementsByTagName("obj")
                for element in elements:
                    if element.getAttribute('is') == 'obix:WatchOut':
                        list_nodes = element.getElementsByTagName("list")
                        count = 0
                        for list_node in list_nodes:
                            if list_node.getAttribute('name') == 'values':
                                for _n in list_node.childNodes:
                                    if _n.nodeType == _n.ELEMENT_NODE:
                                        self.update_device(self.base_url, _n.getAttribute('href'), **self.gen_read_write_result(True, _n.getAttribute('val')))
                                        count = count + 1
                        self.logging(content=f"pool refresh success({count})", pos=self.stack_pos)
                    elif element.getAttribute('is') == 'obix:BadUriErr':
                        raise Exception(f"pool refresh Fail({element.getAttribute('is')})")
            else:
                raise Exception(f'pool refresh Fail({response.msg})')
        else:
            raise Exception(f'pool refresh Fail(no watch)')

    def _read(self, items: list):
        try:
            if len(items) > 0:

                if self._add_watch() is True:

                    self._set_reltime()

                self._add_points(items)

            self._pool_refresh()
        except Exception as e:
            self._del_watch()
            for item in items:
                self.update_device(self.base_url, item, **self.gen_read_write_result(False, e.__str__()))

    def get_value(self, name: str, url: str, type: str):
        try:
            [result, value] = self.get_device_property(self.base_url, url, [self.get_read_quality, self.get_read_result])
            if result is True:
                if value is not None:
                    converter = self.converters.get(type, str)
                    return str(value) if type != 'bool' else str(int(converter(value)))
                else:
                    raise Exception(f"({name}) is none")
            else:
                raise Exception(str(value))
        except Exception as e:
            self.update_results(name, False, e.__str__())
        return None

    def _write(self, url: str, type: str, value):
        return IOTBaseCommon.send_request(url=f"{self.watch.get('url')}{url.replace('/out/', '/')}", data=f'<{type} val="{str(value).lower()}" />', method='POST', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5)).success

    def _gen_name(self, point_url, folder_name) -> str:
        try:
            if point_url.startswith(folder_name) is True:
                point_url = point_url.replace(folder_name, '', 1)
            if point_url[-1] == '/':
                point_url = point_url[:-1]
            return IOTBaseCommon.format_name(point_url.replace('/points/', '_'))
        except Exception:
            pass
        return ''

    def _get_property(self, url: str, results):
        self.logging(content=f"fetching {url}out/", pos=self.stack_pos)
        response = IOTBaseCommon.send_request(url=f"{url}out/", method='GET', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
        if response.success is True:
            point_name = self._gen_name(url, f"{self.base_url}/obix/config/")
            obix_doc = parseString(response.data)
            obix_element = obix_doc.documentElement
            results[point_name] = self.create_point(point_name=point_name, point_name_alias=point_name, point_url=url.replace(self.base_url, ''), point_type=obix_element.tagName, point_description=obix_element.getAttribute("display"), point_value=obix_element.getAttribute("val"))

    def _filters(self, is_param: str) -> bool:
        if isinstance(is_param, str):
            filters = self.configs.get('filiter', ['obix:Point', '/obix/def/schedule'])
            for filter in filters:
                if is_param.find(filter) > 0:
                    return True
        return False

    def _get_urls_from_url(self, url: str, results: dict):
        urls = []
        response = IOTBaseCommon.send_request(url=url, method='GET', auth=HTTPBasicAuth(self.configs.get('username'), self.configs.get('password')), timeout=self.configs.get('timeout', 5))
        if response.success is True:
            document = parseString(response.data)
            elements = document.getElementsByTagName("ref")
            for element in elements:
                href = element.getAttribute("href")
                if self._filters(element.getAttribute("is")) is True:
                    self._get_property(f"{url}{href}", results)
                else:
                    new_url = f"{url}{href}"
                    urls.append(new_url)
        return urls, results

    def _fetch(self, url_params: tuple):
        url, results = url_params
        self.logging(content=f"fetching {url}", pos=self.stack_pos)
        return self._get_urls_from_url(url, results)

    def _fetch_back(self, task: dict):
        if isinstance(task, dict) and 'result' in task.keys():
            (urls, results) = task.get('result')
            job = task.get('kwargs', {}).get('job')
            if job:
                for new_url in urls:
                    index = job.submit_task(self._fetch, self._fetch_back, (new_url, results), job=job)
                job.reactive_task(task.get('future'))

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_obix.py({pos})"
