import time
from typing import List, Dict, Any
from pysnmp.hlapi import ObjectType, ObjectIdentity, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, setCmd, bulkCmd, getCmd
from .base import IOTBaseCommon, IOTDriver

'''
pip install pysnmp==4.4.12
'''


class IOTSNMP(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def reinit(self):
        self.exit_flag = False

    def exit(self):
        self.exit_flag = True

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                    {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '设备地址' if lan == 'ch' else 'Address', 'code': 'point_device_address', 'type': 'string', 'default': '192.168.1.200/161/v1/public/private', 'enum': [], 'tip': ''},
                    {'required': True, 'name': 'OID' if lan == 'ch' else 'oid'.upper(), 'code': 'point_oid', 'type': 'string', 'default': '1.3.6.1.2.1.1.1.0', 'enum': [], 'tip': ''},
                    {'required': False, 'name': '点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                    {'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
            ])
        elif type in ['config', 'scan']:
            templates.extend([
                    {'required': True, 'name': '超时(s)' if lan == 'ch' else 'Cmd Timeout(s)', 'code': 'cmd_timeout', 'type': 'int', 'default': 3, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '重试' if lan == 'ch' else 'Cmd Retries', 'code': 'cmd_retries', 'type': 'int', 'default': 3, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '批量读取个数' if lan == 'ch' else 'Multi Read', 'code': 'multi_read', 'type': 'int', 'default': 20, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '命令间隔(s)' if lan == 'ch' else 'Cmd Interval(s)', 'code': 'cmd_interval', 'type': 'float', 'default': 0.3, 'enum': [], 'tip': ''}
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
                oid = point.get('point_oid')
                device_host = point.get('point_device_address')    # 192.168.1.200/161/v1/public/private
                if oid is not None and device_host is not None:
                    if device_host not in read_items.keys():
                        read_items[device_host] = [[]]
                    if len(read_items[device_host][-1]) >= self.configs.get('multi_read'):
                        read_items[device_host].append([])
                    read_items[device_host][-1].append(ObjectType(ObjectIdentity(oid)))

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                oid = point.get('point_oid')
                device_host = point.get('point_device_address')  # 192.168.1.200/161/v1/public/private
                if oid is not None and device_host is not None:
                    value = self._get_value(name, device_host, oid)
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
                oid = point.get('point_oid')
                device_host = point.get('point_device_address')  # 192.168.1.200/161/v1/public/private
                if oid is not None and device_host is not None:
                    self._write(device_host, oid, value)
                    result = self.get_device_property(device_host, oid, [self.get_write_quality, self.get_write_result])
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
        return self._ping(kwargs.get('host'), port=kwargs.get('port', 161), comunity=kwargs.get('comunity', 'public'))

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        networks = IOTBaseCommon.get_networks(kwargs.get('address'))
        self.logging(content=f"discover({kwargs.get('address')})")
        jobs = IOTBaseCommon.SimpleThreadPool(kwargs.get('limit', 40), f"{self}")
        for ip in networks:
            jobs.submit_task(self._discover, host=ip)
        results = jobs.done(False)
        self.update_info(discover=len(results))
        return results

    def scan(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        address = kwargs.get('address')
        root = kwargs.get('root', '1.3')
        self.logging(content=f"scan({address}) {root}")
        try:
            auth, transport, context = self._get_connect_info(address)
            for (error, status, index, var_binds) in bulkCmd(SnmpEngine(), auth, transport, context, 0, 25, ObjectType(ObjectIdentity(root)), lookupMib=False, lexicographicMode=False, ignoreNonIncreasingOid=True):
                if error:
                    self.logging(content=f"scan({address}) fail({error})", level='ERROR')
                    continue
                if not status:
                    for var_bind in var_binds:
                        name = IOTBaseCommon.format_name(var_bind[0].prettyPrint())
                        value = var_bind[1].prettyPrint()
                        type = var_bind[1].__class__.__name__
                        results[name] = self.create_point(point_name=name, point_name_alias=name, point_device_address=address, point_oid=name, point_type=type, point_description=name, point_value=value)
                        self.logging(content=f"recv {len(results)} point({name})")
        except Exception as e:
            self.logging(content=f"scan ({address}) fail({e.__str__()})", level='ERROR')
        self.update_info(scan=len(results))
        return results

    def _discover(self, **kwargs):
        return kwargs.get('host') if self._ping(kwargs.get('host'), port=kwargs.get('port', 161), comunity=kwargs.get('comunity', 'public')) else None

    def _ping(self, host: str, port: int = 161, comunity: str = 'public', timeout: float = 1, retries: int = 0) -> bool:
        self.logging(content=f"ping {host}:{port} {comunity}")
        error, status, index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(comunity, mpModel=0),
                   UdpTransportTarget((host, port), timeout=timeout, retries=retries),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysContact', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysObjectID', 0)),
                   )
        )
        if not error and not status:
            return True
        return False

    def _read(self, read_items: dict):
        if len(read_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(read_items), f"{self}")
            for address, oids in read_items.items():
                jobs.submit_task(self._read_oids, address, oids)
            return jobs.done()
        return {}

    def _get_connect_info(self, address: str):
        infos = address.split('/')  # '192.168.1.200/161/v1/public/private'
        if len(infos) >= 5:
            transport = UdpTransportTarget((infos[0], int(infos[1])), timeout=self.configs.get('cmd_timeout', 3), retries=self.configs.get('cmd_retries', 3))
            context = ContextData()
            if infos[2] == 'v1':
                auth = CommunityData(infos[3], infos[4], mpModel=0)
            elif infos[2] == 'v2':
                auth = CommunityData(infos[3], infos[4], mpModel=1)
            else:
                raise Exception(f"unsupport protocol({infos[2]})")
            return auth, transport, context
        raise Exception(f"invalid address({address})")

    def _read_multi(self, auth, transport, context, address, oid: list, raise_unexist: bool = False):
        var_binds = tuple(oid)
        try:
            error, status, index, var_binds = next(getCmd(SnmpEngine(), auth, transport, context, *var_binds))
            if error:
                raise Exception(f"{error}")
            elif status:
                raise Exception(f"{status.prettyPrint()} at {index and var_binds[int(index) - 1][0] or '?'}")
            else:
                for var_bind in var_binds:
                    self.update_device(f"{address}", str(var_bind[0]), **self.gen_read_write_result(True, var_bind[1].prettyPrint()))
        except Exception as e:
            for id in oid:
                self.update_device(f"{address}", str(id[0]), **self.gen_read_write_result(False, e.__str__()))
            error_msg = e.__str__().lower()
            if raise_unexist is True and (error_msg.find('no such') > -1 or error_msg.find('nosuch') > -1): # no such object
                raise e

    def _read_oids(self, *args, **kwargs):
        (address, oids) = args
        results = {}
        auth, transport, context = self._get_connect_info(address)
        for oid in oids:
            start = time.time()
            try:
                self._read_multi(auth, transport, context, address, oid, True)
            except Exception as e:
                if len(oid) > 1:
                    for o in oid:
                        self._read_multi(auth, transport, context, address, [o], False)
            finally:
                self.logging(content=f"read({address}) oids({len(oid)}) cost: {'{:.2f}'.format(time.time() - start)}")
            self.delay(self.configs.get('cmd_interval', 1))
        return results

    def _write(self, address: str, oid: str, value):
        try:
            if len(oid) > 0:
                self.logging(content=f"write({address}) oid({oid})")
                var_binds = tuple([ObjectType(ObjectIdentity(oid), value)])
                auth, transport, context = self._get_connect_info(address)
                error, status, index, var_binds = next(setCmd(SnmpEngine(), auth, transport, context, *var_binds))
                if error:
                    raise Exception(f"{error}")
                elif status:
                    raise Exception(f"{status.prettyPrint()} at {index and var_binds[int(index) - 1][0] or '?'}")
                else:
                    self.update_device(f"{address}", oid, **self.gen_read_write_result(True, None, False))
            raise Exception('set fail')
        except Exception as e:  # other
            self.update_device(f"{address}", oid, **self.gen_read_write_result(False, e.__str__(), False))

    def _get_value(self, name: str, device_address: str, id: str):
        try:
            [result, value] = self.get_device_property(device_address, id, [self.get_read_quality, self.get_read_result])
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

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_snmp.py({pos})"
