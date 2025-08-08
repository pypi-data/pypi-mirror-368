import time
from threading import Lock, Event, currentThread
from typing import Optional, List, Dict, Callable, Tuple
from queue import Queue
from inspect import stack
from concurrent.futures import ThreadPoolExecutor

from .base import IOTBaseCommon, IOTDriver, IOTSimulateObject, FunctionTimedOut, func_timeout

# bacnet
from bacpypes.apdu import APDU, AbortReason, RejectReason, ReadAccessSpecification, ConfirmedRequestSequence, ConfirmedCOVNotificationRequest, PropertyReference, ReadPropertyMultipleRequest, ReadPropertyMultipleACK, ReadPropertyRequest, ReadPropertyACK, WritePropertyRequest, SimpleAckPDU, WhoIsRequest, IAmRequest, AbortPDU, RejectPDU, SubscribeCOVRequest
from bacpypes.app import BIPSimpleApplication
from bacpypes.basetypes import ServicesSupported, StatusFlags
from bacpypes.constructeddata import Array, Any, Choice
from bacpypes.core import run, stop, deferred, enable_sleeping
from bacpypes.iocb import IOCB
from bacpypes.local.device import LocalDeviceObject
from bacpypes.npdu import WhoIsRouterToNetwork, WhatIsNetworkNumber
from bacpypes.object import get_datatype, AnalogInputObject, AnalogOutputObject, AnalogValueObject, MultiStateInputObject, MultiStateOutputObject, MultiStateValueObject, OctetStringValueObject, BinaryInputObject, BinaryOutputObject, BinaryValueObject, BitStringValueObject, CharacterStringValueObject
from bacpypes.pdu import GlobalBroadcast, Address, LocalBroadcast
from bacpypes.primitivedata import Null, Atomic, Integer, Unsigned, Real, Enumerated, CharacterString
from bacpypes.service.object import ReadWritePropertyMultipleServices
from bacpypes.task import RecurringTask


class SubscriptionContext(object):

    def __init__(self, target_address: str, object_type: str, instance_number: int, sub_process_id: int, lifetime: Optional[int] = None, confirmed: bool = True):
        self.target_address = target_address
        self.sub_process_id = sub_process_id
        self.object_type = object_type
        self.instance_number = instance_number
        self.lifetime = lifetime
        self.confirmed = confirmed


class IOCBContext:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def update(self, **kwargs):
        self.kwargs.update(kwargs)


class IOCBHelper:

    def __init__(self, iocb: IOCB, request_io: Callable[[IOCB], Any]):
        self.iocb = iocb
        self.request_io = request_io

    def __enter__(self):
        deferred(self.request_io, self.iocb)
        self.iocb.wait()

    def __exit__(self, exc_type, exc_val, exc_tb):
        deferred(stop)


class BacnetClientSample(BIPSimpleApplication):

    def __init__(self, local_address: Address):
        super(BacnetClientSample, self).__init__(LocalDeviceObject(
            objectName="BACpypes Client",
            objectIdentifier=("device", 1),
            maxApduLengthAccepted=1024,
            segmentationSupported="segmentedBoth",
            vendorIdentifier=15,
        ), local_address)

    def _init_iocb(self, iocb: IOCB, successful_callback: Callable[[APDU], Any]) -> Any:
        with IOCBHelper(iocb, self.request_io):
            if iocb.ioError:
                raise Exception(f"something error({iocb.ioError})")
            elif iocb.ioResponse:
                return successful_callback(iocb.ioResponse)
            else:
                raise Exception(f"something wrong")
            return None

    def _do_read_property(self, read_property_request: ReadPropertyRequest, property_identifier: str):

        def callback(apdu: APDU) -> Any:
            datatype = get_datatype(apdu.objectIdentifier[0], property_identifier)
            if not datatype:
                raise TypeError("unknown datatype")
            # special case for array parts, others are managed by cast_out
            value = apdu.propertyValue.cast_out(datatype)
            return value

        return self._init_iocb(IOCB(read_property_request), callback)

    def _do_read_property_multiple(self, read_property_multiple_request: ReadPropertyMultipleRequest):
        def callback(apdu: APDU) -> Any:
            return None

        return self._init_iocb(IOCB(read_property_multiple_request), callback)

    def make_request_read_property(self, device_address: Address, object_identifier: Tuple[str, int],
                                   property_identifier: str):
        # Create a BACnet ReadPropertyRequest
        request = ReadPropertyRequest(
            objectIdentifier=object_identifier,
            propertyIdentifier=property_identifier,
        )
        request.pduDestination = device_address

        with ThreadPoolExecutor() as executor:
            future = executor.submit(self._do_read_property, request, property_identifier)
            run()
            return future.result()

    def make_request_read_property_multiple(self, device_address: Address):
        # Create a BACnet ReadPropertyMultipleRequest
        request = ReadPropertyMultipleRequest()
        request.pduDestination = device_address

        with ThreadPoolExecutor() as executor:
            future = executor.submit(self._do_read_property, request)
            run()
            return future.result()


class BacnetSimulateObject:

    class BacnetObject:
        presentValue = None

        def set_value(self, name, value):
            pass  # print(f"set value ({name}:{value})")

    class BacnetAnalogInputObject(BacnetObject, AnalogInputObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetAnalogOutputObject(BacnetObject, AnalogOutputObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetAnalogValueObject(BacnetObject, AnalogValueObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetMultiStateInputObject(BacnetObject, MultiStateInputObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetMultiStateOutputObject(BacnetObject, MultiStateOutputObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetMultiStateValueObject(BacnetObject, MultiStateValueObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetBinaryInputObject(BacnetObject, BinaryInputObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetBinaryOutputObject(BacnetObject, BinaryOutputObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetBinaryValueObject(BacnetObject, BinaryValueObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetOctetStringValueObject(BacnetObject, OctetStringValueObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetBitStringValueObject(BacnetObject, BitStringValueObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)

    class BacnetCharacterStringValueObject(BacnetObject, CharacterStringValueObject):

        def WriteProperty(self, propid, value, arrayIndex=None, priority=None, direct=False):
            self.presentValue = value
            super().set_value(self.objectName, value)


class BacnetApplication(BIPSimpleApplication, RecurringTask):

    def __init__(self, local_device, local_address: str, **kwargs):
        self.kwargs = kwargs
        BIPSimpleApplication.__init__(self, local_device, local_address)
        RecurringTask.__init__(self, self.kwargs.get('request_check_interval', 100))

        self.local_address = local_address
        self.exit_flag: bool = False  # 退出事件
        self.next_invoke_id: int = 0  # invoke id
        self.current_invoke_id: int = 0  # invoke id
        self.process = ''
        self.request_queue = Queue()
        self.iocbs: dict = {}  # 现有iocb
        self.callbacks: dict = self.kwargs.get('callbacks', {})  # 回调函数
        self.sub_cov_contexts = {}  # COV 订阅
        self.cov_sub_process_id = 1  # COV 请求ID
        self.address_network_dict = {}  # 网络地址
        self.read_write_lock = Lock()
        self.timeout_flag = 0   # 连续五次超时 重新连接

        # self.install_task()

    def __del__(self):
        self.exit()

    def __str__(self):
        return f"{self.local_address}"

    def exit(self):
        self.exit_flag = True

    def _get_value_from_request(self, apdu):
        value = None
        datatype = get_datatype(apdu.objectIdentifier[0], apdu.propertyIdentifier)
        if datatype:
            # special case for array parts, others are managed by cast_out
            if issubclass(datatype, Array) and apdu.propertyArrayIndex is not None:
                if apdu.propertyArrayIndex == 0:
                    value = apdu.propertyValue.cast_out(Unsigned)
                else:
                    value = apdu.propertyValue.cast_out(datatype.subtype)
            else:
                value = apdu.propertyValue.cast_out(datatype)
                if issubclass(datatype, Enumerated):
                    value = datatype(value).get_long()
        return value

    def indication(self, apdu):
        if isinstance(apdu, IAmRequest):
            device_type, device_instance = apdu.iAmDeviceIdentifier
            if device_type != 'device':
                return

            i_am = self.callbacks.get('i_am')
            if i_am is not None:
                address = str(apdu.pduSource)
                if address.find(':') > 0:
                    address = self.nsap.router_info_cache.path_info.get((None, int(address.split(':')[0])), None)
                    if address is not None:
                        address = str(address.address)
                i_am(str(apdu.pduSource), address, device_instance, apdu.maxAPDULengthAccepted, str(apdu.segmentationSupported), apdu.vendorID)

        elif isinstance(apdu, ConfirmedCOVNotificationRequest):
            # Handling for ConfirmedCOVNotificationRequests. These requests are sent by the device when a point with a COV subscription updates past the covIncrement threshold(See COV_Detection class in
            # Bacpypes: https://bacpypes.readthedocs.io/en/latest/modules/service/cov.html)

            result_dict = {}
            for element in apdu.listOfValues:
                property_id = element.propertyIdentifier
                if not property_id == "statusFlags":
                    values = []
                    for tag in element.value.tagList:
                        values.append(tag.app_to_object().value)
                    if len(values) == 1:
                        result_dict[property_id] = values[0]
                    else:
                        result_dict[property_id] = values
        elif isinstance(apdu, WritePropertyRequest):
            write = self.callbacks.get('write')
            if write is not None:
                value = self._get_value_from_request(apdu)
                if value is not None:
                    write(str(apdu.pduSource), apdu.objectIdentifier[0], apdu.objectIdentifier[1], apdu.propertyIdentifier, value)

        # forward it along
        BIPSimpleApplication.indication(self, apdu)

    def confirmation(self, apdu):
        content = ''
        BIPSimpleApplication.confirmation(self, apdu)
        if apdu is not None:
            apduInvokeID = None
            if hasattr(apdu, 'apduInvokeID'):
                apduInvokeID = apdu.apduInvokeID
            content = f"recv({self.process}) {apduInvokeID} {apdu.__class__.__name__} {self.current_invoke_id}"

        if len(content) > 0:
            logging = self.callbacks.get('logging')
            if logging is not None:
                logging(content=content)

    def process_task(self):
        while self.exit_flag is False:
            if not self.request_queue.empty():
                self.handle_request(self.request_queue.get())

    def get_next_invoke_id(self, addr) -> int:
        """Called to get an unused invoke ID."""

        initial_id = self.next_invoke_id
        while 1:
            self.current_invoke_id = self.next_invoke_id
            self.next_invoke_id = (self.next_invoke_id + 1) % 256

            # see if we've checked for them all
            if initial_id == self.next_invoke_id:
                raise RuntimeError("no available invoke ID")

            # see if this one is used
            if (addr, self.current_invoke_id) not in self.iocbs:
                break

        return self.current_invoke_id

    def handle_request(self, iocb):
        apdu = iocb.ioRequest

        if isinstance(apdu, ConfirmedRequestSequence):
            # assign an invoke identifier
            apdu.apduInvokeID = self.get_next_invoke_id(apdu.pduDestination)

            # build a key to reference the IOCB when the response comes back
            invoke_key = (apdu.pduDestination, apdu.apduInvokeID)

            # keep track of the request
            self.iocbs[invoke_key] = iocb

        try:
            self.request(apdu)
        except Exception as e:
            iocb.set_exception(e)

    @IOTBaseCommon.set_timeout_wrapper(10)
    def send_iocb(self, iocb: IOCB, wait: bool = True):
        deferred(self.request_io, iocb)
        if wait is True:
            iocb.wait()
        return iocb

    def send_iocb_with_timeout(self, iocb: IOCB, wait: bool = True):
        try:
            response = func_timeout(int(self.kwargs.get('timeout', 3000))/1000+0.5, self.send_iocb1, kwargs={'iocb': iocb, 'wait': wait})
            self.timeout_flag = 0
            return response
        except (FunctionTimedOut, TimeoutError):
            self.timeout_flag = self.timeout_flag + 1
            raise Exception(f'send time out({iocb.ioState})')
        except Exception as e:
            raise e

    def send_iocb1(self, iocb: IOCB, wait: bool = True):
        currentThread().setName(f"Bacnet({self}) iocb")
        deferred(self.request_io, iocb)
        if wait is True:
            iocb.wait()
        return iocb

    def send_request(self, request, wait: bool = True, context: Optional[IOCBContext] = None, process: Optional[str] = ''):
        with self.read_write_lock:
            self.process = process
            iocb = IOCB(request)
            iocb.set_timeout(self.kwargs.get('timeout', 3000) * (self.kwargs.get('retry', 0) + 1) * 1.2, err=TimeoutError)
            if request.apduInvokeID is None:
                request.apduInvokeID = self.get_next_invoke_id(request.pduDestination)
            if context is None:
                context = IOCBContext(invoke_id=request.apduInvokeID)
            else:
                context.update(invoke_id=request.apduInvokeID)
            iocb.context = context

            try:
                iocb = self.send_iocb_with_timeout(iocb, wait)
            except Exception as e:
                if e.__str__().find('time out') >= 0:
                    iocb.ioError = TimeoutError(e.__str__())
            return iocb

    # Add network routing for access across network segments(6:2)
    def add_router(self, target_address: str, network: int):
        networks = self.address_network_dict.get(target_address, [])
        if network not in networks:
            networks.append(network)
            self.nsap.update_router_references(None, Address(target_address), networks)
            self.address_network_dict[target_address] = networks
            return True
        return False

    def do_ConfirmedCOVNotificationRequest(self, apdu):
        cov = self.callbacks.get('cov')
        if cov is not None:
            cov(str(apdu.pduSource), apdu.monitoredObjectIdentifier[0], apdu.monitoredObjectIdentifier[1],
                apdu.timeRemaining,
                [(str(element.propertyIdentifier), str(element.value.tagList[0].app_to_object().value)) for element in apdu.listOfValues], True)

        # success
        response = SimpleAckPDU(context=apdu)

        # return the result
        self.response(response)

    def do_UnconfirmedCOVNotificationRequest(self, apdu):
        cov = self.callbacks.get('cov')
        if cov is not None:
            cov(str(apdu.pduSource), apdu.monitoredObjectIdentifier[0], apdu.monitoredObjectIdentifier[1],
                apdu.timeRemaining,
                [(str(element.propertyIdentifier), str(element.value.tagList[0].app_to_object().value)) for element in
                 apdu.listOfValues], False)


class BacnetClient:

    def __init__(self, is_client: bool = True, parent=None, **kwargs):
        self.kwargs = kwargs

        self.bacnet_server_ip = IOTBaseCommon.change_local_ip(kwargs.get('address'))
        self.cov_update_buffer = kwargs.get('cov_update_buffer', 3)
        self.bacnet_cmd_interval = kwargs.get('cmd_interval', 0.3)
        self.bacnet_max_per_request = kwargs.get('multi_read', 25)
        self.bacnet_timeout_flag = kwargs.get('timeout_flag', 5)
        self.parent = parent
        self.is_client = is_client

        self.reset()

        self._get_application()

    def __str__(self):
        return f"BacnetClient({self.bacnet_server_ip})"

    def __del__(self):
        self.exit()

    def reset(self):
        self.bacnet_application = None
        self.control_thread = None
        self.bacnet_devices = {}
        self.bacnet_cov_subs = {}  # 订阅请求
        self.bacnet_cov_sub_process_id = 1
        self.bacnet_objects = {}
        self.process = ''

    def exit(self):
        self._release_application()
        self.reset()

    def device(self, **kwargs):
        bacnet_device = LocalDeviceObject(
            objectName=kwargs.get('name', 'Robert BACnet driver'),
            objectIdentifier=('device', kwargs.get('identifier', 599)),
            numberOfApduRetries=kwargs.get('retry', 0),
            apduTimeout=kwargs.get('timeout', 3000),
            maxApduLengthAccepted=kwargs.get('max_apdu', 1024),
            segmentationSupported=kwargs.get('segmentation', 'segmentedBoth'),
            vendorIdentifier=kwargs.get('vendor_identifier', 15),
        )

        # build a bit string that knows about the bit names.
        pss = ServicesSupported()
        pss['whoIs'] = 1
        pss['iAm'] = 1
        pss['readProperty'] = 1
        pss['readPropertyMultiple'] = 1

        # set the property value to be just the bits
        try:
            bacnet_device.protocolServicesSupported = pss.value
        except:
            pass
        return bacnet_device

    def control(self, status: bool = True):
        self.logging(content=f"control({status})", pos=self.stack_pos)
        if status is True:
            enable_sleeping()
            run(spin=0.05, sigterm=stop, sigusr1=None)
        else:
            stop()

    def discover(self, low_device_id: Optional[int] = None, high_device_id: Optional[int] = None, target_address: Optional[str] = None) -> bool:
        request = WhoIsRequest()
        if low_device_id is not None:
            request.deviceInstanceRangeLowLimit = low_device_id
        if high_device_id is not None:
            request.deviceInstanceRangeHighLimit = high_device_id
        if target_address is not None:
            request.pduDestination = self._create_address(target_address)
        else:
            request.pduDestination = GlobalBroadcast()
        self.logging(content=f"discover({request.pduDestination} {low_device_id}-{high_device_id})", pos=self.stack_pos)
        event = Event()
        self._update_device(target_address, **{'event_whois': event})
        iocb = self._send_request(request, False)
        return event.wait(5)

    def whois_router_to_network(self, network: Optional[int] = None, target_address: Optional[str] = None):
        request = WhoIsRouterToNetwork()
        if network is not None:
            request.wirtnNetwork = network
        if target_address is not None:
            request.pduDestination = self._create_address(target_address)
        else:
            request.pduDestination = LocalBroadcast()
        iocb = self._send_request(request, True)

    def what_is_network_number(self, target_address: Optional[str] = None):
        request = WhatIsNetworkNumber()
        if target_address is not None:
            request.pduDestination = self._create_address(target_address)
        else:
            request.pduDestination = LocalBroadcast()
        iocb = self._send_request(request, True)

    def ping(self, target_address: str, device_id: Optional[int] = None, device_address: Optional[str] = None) -> dict:
        self.logging(content=f"ping({target_address}-{device_id}-{device_address})", pos=self.stack_pos)
        if self.discover(device_id, device_id, target_address) is True:
            return self.bacnet_devices.get(target_address, {})
        return {}

    def ping_target(self, target_address: str) -> bool:
        target_address, device_id, bind_ip = self._parse_adderss(target_address)
        bacnet_device = self.ping(target_address, device_id, bind_ip)  # 测试设备
        if len(bacnet_device) == 0:
            return False
        return True

    def read_property(self, target_address: str, object_type: str, instance_number: int, property_name: str, property_index: Optional[int] = None):
        self.logging(content=f"read property({target_address}-{object_type}-{instance_number}-{property_name}-{property_index})", pos=self.stack_pos)
        value = ['Good', '']
        try:
            request = ReadPropertyRequest(objectIdentifier=(object_type, instance_number), propertyIdentifier=property_name, propertyArrayIndex=property_index)
            request.pduDestination = self._create_address(target_address)
            iocb = self._send_request(request, True)
            value[1] = self._parse_response(request, iocb)
        except Exception as e:
            value = ['Bad', e.__str__()]
        return value

    def read_properties(self, target_address: str, object_type: str, instance_number: int, properties: Optional[list] = None, use_read_multiple: bool = True):
        self.logging(content=f"read properties({target_address}-{object_type}-{instance_number}-{properties}-{use_read_multiple})", pos=self.stack_pos)
        if properties is None:
            properties = ['objectName', 'description', 'presentValue']

        if use_read_multiple is True:
            property_reference_list = []
            for property_identifier in properties:
                prop_reference = PropertyReference(propertyIdentifier=property_identifier, )
                property_reference_list.append(prop_reference)

            read_access_spec = ReadAccessSpecification(objectIdentifier=(object_type, instance_number), listOfPropertyReferences=property_reference_list, )
            request = ReadPropertyMultipleRequest(listOfReadAccessSpecs=[read_access_spec])
            request.pduDestination = self._create_address(target_address)
            iocb = self._send_request(request)
            self._parse_response(request, iocb)
        else:
            for property_identifier in properties:
                quality, value = self.read_property(target_address, object_type, instance_number, property_identifier)
                self._update_device(target_address, **{'object_type': object_type, 'instance_number': instance_number, property_identifier: value if quality == 'Good' else None, 'quality': quality, 'error': value if quality == 'Bad' else None})

    def read(self, target_address: str, objct_propertys: list, max_per_request: Optional[int] = None, use_read_multiple: bool = True, ping_check: bool = False):
        self.logging(content=f"read({target_address}-{len(objct_propertys)}-{max_per_request}-{use_read_multiple})", pos=self.stack_pos)
        target_address, device_id, bind_ip = self._parse_adderss(target_address)
        if ping_check is True:
            bacnet_device = self.ping(target_address, device_id, bind_ip)  # 测试设备
            if len(bacnet_device) == 0:
                for object_type, instance_number, property_identifier in objct_propertys:
                    self._update_device(target_address, **{'object_type': object_type, 'instance_number': instance_number, property_identifier: None, 'quality': 'Bad', 'error': f"device({target_address}) not find"})
                return
        if use_read_multiple is True:
            read_access_specs = []
            for object_type, instance_number, property_identifier in objct_propertys:
                read_access_specs.append(ReadAccessSpecification(objectIdentifier=(object_type, instance_number), listOfPropertyReferences=[PropertyReference(propertyIdentifier=property_identifier)]))
                self._update_device(target_address, **{'object_type': object_type, 'instance_number': instance_number, property_identifier: None, 'quality': 'Bad', 'error': 'ReInit'})

            read_access_specs = list(IOTBaseCommon.chunk_list(read_access_specs, max_per_request if max_per_request is not None else self.bacnet_max_per_request))
            for index, read_access_spec in enumerate(read_access_specs):
                self.process = f"{index + 1}/{len(read_access_specs)}"
                request = ReadPropertyMultipleRequest(listOfReadAccessSpecs=read_access_spec)
                request.pduDestination = Address(target_address)
                iocb = self._send_request(request)
                self._parse_response(request, iocb)
                self.parent.delay(self.bacnet_cmd_interval)
        else:
            for index, (object_type, instance_number, property_identifier) in enumerate(objct_propertys):
                self.process = f"{index + 1}/{len(objct_propertys)}"
                quality, value = self.read_property(target_address, object_type, instance_number, property_identifier)
                self._update_device(target_address, **{'object_type': object_type, 'instance_number': instance_number, property_identifier: value if quality == 'Good' else None, 'quality': quality, 'error': value if quality == 'Bad' else None})
                self.parent.delay(self.bacnet_cmd_interval)

    def write(self, target_address: str, object_type: str, instance_number: int, property_name: str, value, priority: Optional[int] = None, index: Optional[int] = None):
        self.logging(content=f"write({target_address}-{object_type}-{instance_number}-{property_name}-{value}-{priority}-{index})", pos=self.stack_pos)
        target_address, device_id, bind_ip = self._parse_adderss(target_address)
        request = WritePropertyRequest(objectIdentifier=(object_type, instance_number), propertyIdentifier=property_name)
        bac_value = self._convert_value_to_set(value, get_datatype(object_type, property_name), index)
        request.propertyValue = Any()
        request.propertyValue.cast_in(bac_value)
        request.pduDestination = self._create_address(target_address)
        if index is not None:
            request.propertyArrayIndex = index
        if priority is not None:
            request.priority = priority
        iocb = self._send_request(request)
        return self._parse_response(request, iocb)

    def cov(self, target_address: str, object_type: str, instance_number: int, lifetime: int = 180, renew: bool = False):
        try:
            self.logging(content=f"cov({target_address}-{object_type}-{instance_number}-{lifetime}-{renew})", pos=self.stack_pos)
            self._create_cov_subscription(target_address, object_type, instance_number, lifetime)
        except Exception as e:
            pass
        if renew and lifetime > self.cov_update_buffer:
            # 定时触发
            IOTBaseCommon.SimpleTimer().run(lifetime - self.cov_update_buffer, self.cov, kwargs={'target_address': target_address, 'object_type': object_type, 'instance_number': instance_number, 'lifetime': lifetime, 'renew': renew})

    def route(self, target_address: str, network: int):
        if self._get_application():
            if self._get_application().add_router(target_address, network) is True:
                self.logging(content=f"route({target_address}-{network})", pos=self.stack_pos)

    # 6:2
    def scan(self, target_address: str, use_read_multiple: bool = True, ping_check: bool = False):
        self.logging(content=f"scan({target_address}-{use_read_multiple}-{ping_check})", pos=self.stack_pos)
        target_address, device_id, bind_ip = self._parse_adderss(target_address)

        bacnet_device = self.devices(target_address)
        if ping_check is True:
            bacnet_device = self.ping(target_address, device_id, bind_ip)  # 测试设备
            if len(bacnet_device) == 0:
                raise Exception(f"device({target_address}) not find")
        else:
            self._update_device(target_address, **{'address': bind_ip, 'device_id': device_id})

        if device_id is not None:
            # 读取数量
            quality, object_count = self.read_property(target_address, 'device', device_id, 'objectList', 0)
            if quality == 'Good':
                for array_index in range(1, object_count + 1):
                    try:
                        quality, object_instance = self.read_property(target_address, 'device', device_id, 'objectList', array_index)
                        if quality == 'Good':
                            self._update_device(target_address, object_type=object_instance[0], instance_number=object_instance[1], property_index=array_index)
                            self.read_properties(target_address, object_instance[0], object_instance[1], None, use_read_multiple)
                    except Exception as e:
                        print(e.__str__())
                    self.parent.delay(self.bacnet_cmd_interval)
        return self.devices(target_address)

    def devices(self, target_address: Optional[str] = None):
        if target_address is not None:
            target_address, device_id, bind_ip = self._parse_adderss(target_address)
            if target_address is not None:
                return self.bacnet_devices.get(target_address)
        return self.bacnet_devices

    def simluate(self, objects: List[IOTSimulateObject], callbacks: Optional[dict] = None):
        for object in objects:
            self._create_object(object)
        self.refresh_objects(objects)

    def value(self, target_address: str, object_type: str, instance_number: int, property_name: str):
        target_address, device_id, bind_ip = self._parse_adderss(target_address)
        bacnet_device = self.bacnet_devices.get(target_address)
        if bacnet_device is not None and len(bacnet_device) > 0:
            quality = bacnet_device.get('objects', {}).get(f"{object_type}_{instance_number}", {}).get('quality', 'Bad')
            if quality == 'Good':
                return quality, bacnet_device.get('objects', {}).get(f"{object_type}_{instance_number}", {}).get(property_name)
            else:
                return quality, bacnet_device.get('objects', {}).get(f"{object_type}_{instance_number}", {}).get('error')
        return 'Bad', 'UnFind'

    def _get_application(self, bacnet_app_class=BacnetApplication, bacnet_device=None):
        if self.bacnet_application is None:
            if bacnet_device is None:
                bacnet_device = self.device(**self.kwargs)

            bacnet_application = bacnet_app_class(bacnet_device, self.bacnet_server_ip, callbacks={'logging': self.logging, 'i_am': self._call_back_i_am, 'cov': self._call_back_cov, 'write': None if self.is_client else self._call_back_write}, **self.kwargs)
            if bacnet_application is not None:
                bacnet_application.add_capability(ReadWritePropertyMultipleServices)
                self.control_thread = IOTBaseCommon.function_thread(self.control, False, str(self))
                self.control_thread.start()
                self.parent.delay(1)
                self.bacnet_application = bacnet_application
        return self.bacnet_application

    def _release_application(self):
        try:
            if self.bacnet_application:
                self.control(False)
                self.parent.delay(1)
                if hasattr(self.bacnet_application, 'mux'):
                    self.bacnet_application.close_socket()
                try:
                    if self.control_thread is not None:
                        IOTBaseCommon.stop_thread(self.control_thread)
                except:
                    pass
                del self.bacnet_application
        except Exception as e:
            self.logging(content=f"release {self.bacnet_server_ip} fail {e.__str__()}", level='ERROR', pos=self.stack_pos)
        finally:
            self.bacnet_application = None

    def _send_request(self, request, wait_result: bool = True, context: Optional[IOCBContext] = None):
        if self._get_application():
            request.apduInvokeID = self._get_application().get_next_invoke_id(request.pduDestination)
            self.logging(content=f"send({self.process}) {request.apduInvokeID} {request.__class__.__name__}", pos=self.stack_pos)
            try:
                return self._get_application().send_request(request, wait_result, context, self.process)
            finally:
                if self._get_application().timeout_flag >= self.bacnet_timeout_flag:
                    self._release_application()
        return None

    def _find_reason(self, apdu) -> str:
        try:
            if isinstance(apdu, TimeoutError) is True:
                return "Timeout"
            elif isinstance(apdu, RuntimeError) is True:
                return f"RuntimeError{apdu}"
            elif apdu.pduType == RejectPDU.pduType:
                reasons = RejectReason.enumerations
            elif apdu.pduType == AbortPDU.pduType:
                reasons = AbortReason.enumerations
            else:
                if apdu.errorCode and apdu.errorClass:
                    return f"{apdu.errorCode}"
                else:
                    raise ValueError(f"Cannot find reason({apdu.errorCode})...")
            code = apdu.apduAbortRejectReason
            try:
                return [k for k, v in reasons.items() if v == code][0]
            except IndexError:
                return code
        except Exception as err:
            return f"Unknown error: {err.__str__()}"

    def _gen_key(self, target_address: str, object_type: str, instance_number: int, property_name: Optional[str] = None, property_index: Optional[int] = None) -> str:
        values = f"{target_address}_{object_type}_{instance_number}"
        if property_name is not None:
            values = f"{values}_{property_name}"
        if property_index is not None:
            values = f"{values}_{property_index}"
        return values

    def _get_value_from_read_property_request(self, apdu):
        datatype = get_datatype(apdu.objectIdentifier[0], apdu.propertyIdentifier)
        if not datatype:
            raise Exception("unknown datatype")
        # special case for array parts, others are managed by cast_out
        if issubclass(datatype, Array) and apdu.propertyArrayIndex is not None:
            if apdu.propertyArrayIndex == 0:
                value = apdu.propertyValue.cast_out(Unsigned)
            else:
                value = apdu.propertyValue.cast_out(datatype.subtype)
        else:
            value = apdu.propertyValue.cast_out(datatype)
            if issubclass(datatype, Enumerated):
                value = datatype(value).get_long()
        return value

    def _get_value_from_property_value(self, property_value, datatype):
        value = property_value.cast_out(datatype)
        if issubclass(datatype, Enumerated):
            value = datatype(value).get_long()
        try:
            if issubclass(datatype, Array) and issubclass(datatype.subtype, Choice):
                new_value = []
                for item in value.value[1:]:
                    result = list(item.dict_contents().values())
                    if result[0] != ():
                        new_value.append(result[0])
                    else:
                        new_value.append(None)
                value = new_value
        except Exception as e:
            raise e
        return value

    def _parse_response(self, request, iocb):
        if iocb is not None:
            ioError = iocb.ioError
            ioResponse = iocb.ioResponse
            (apduInvokeID, results) = (request.apduInvokeID, ioError) if ioError else (request.apduInvokeID, ioResponse)
            self.logging(content=f"recv({self.process}) {apduInvokeID} {results.__class__.__name__}", pos=self.stack_pos)
            if isinstance(request, ReadPropertyRequest):
                if ioError:
                    raise Exception(f"{request.apduInvokeID}({self._find_reason(ioError)})")
                else:
                    if isinstance(results, ReadPropertyACK):
                        return self._get_value_from_read_property_request(results)
            elif isinstance(request, ReadPropertyMultipleRequest):
                if ioError:
                    for read in request.listOfReadAccessSpecs:
                        object_identifier = read.objectIdentifier
                        for property in read.listOfPropertyReferences:
                            property_identifier = property.propertyIdentifier
                            self._update_device(str(request.pduDestination), **{'object_type': object_identifier[0], 'instance_number': object_identifier[1], property_identifier: None, 'quality': 'Bad', 'error': f"{request.apduInvokeID}({self._find_reason(ioError)})"})
                else:
                    if isinstance(results, ReadPropertyMultipleACK):
                        for result in results.listOfReadAccessResults:
                            object_identifier = result.objectIdentifier
                            for element in result.listOfResults:
                                property_identifier = element.propertyIdentifier
                                property_array_index = element.propertyArrayIndex
                                read_result = element.readResult
                                quality, value = 'Good', ''
                                if read_result.propertyAccessError is not None:
                                    quality, value = 'Bad', f"{request.apduInvokeID}({read_result.propertyAccessError.errorCode})"
                                else:
                                    property_value = read_result.propertyValue
                                    datatype = get_datatype(object_identifier[0], property_identifier)
                                    if datatype:
                                        if issubclass(datatype, Array) and property_array_index is not None:
                                            if property_array_index == 0:
                                                value = property_value.cast_out(Unsigned)
                                            else:
                                                value = property_value.cast_out(datatype.subtype)
                                        else:
                                            value = self._get_value_from_property_value(property_value, datatype)
                                self._update_device(str(request.pduDestination), **{'object_type': object_identifier[0], 'instance_number': object_identifier[1], property_identifier: value if quality == 'Good' else None, 'quality': quality, 'error': value if quality == 'Bad' else None})
            elif isinstance(request, WritePropertyRequest):
                if ioError:
                    return False, f"{request.apduInvokeID}({self._find_reason(ioError)})"
                else:
                    if isinstance(results, SimpleAckPDU):
                        return True, ''
            elif isinstance(request, SubscribeCOVRequest):
                pass
            else:
                raise Exception('Unsupported Request Type')

    # callback#################
    def _call_back_i_am(self, target_address: str, bind_address: str, device_id: int, max_apdu_len: int, seg_supported: str, vendor_id: int):
        if self.bacnet_devices.get(target_address, {}).get('device_id') is None:
            self.logging(content=f"i-am({target_address}({bind_address})-{device_id}-{max_apdu_len}-{seg_supported}-{vendor_id})", pos=self.stack_pos)
        event_whois = self.bacnet_devices.get(target_address, {}).get('event_whois')
        if event_whois:
            event_whois.set()
        self._update_device(target_address, **{'address': bind_address, 'device_id': device_id, 'max_apdu_len': max_apdu_len, 'seg_supported': seg_supported, 'vendor_id': vendor_id})

    def _call_back_cov(self, target_address: str, object_type: str, instance_number: int, time_remaining: str, elements: list, confirm: bool = True):
        if target_address in self.bacnet_devices.keys():
            kwargs = {'object_type': object_type, 'instance_number': instance_number, 'time_remaining': time_remaining}
            for property, value in elements:
                kwargs[property] = value
                self.logging(content=f"cov_({target_address}-{object_type}-{instance_number}-{time_remaining}-{property}-{value})", pos=self.stack_pos)
            self._update_device(target_address, **kwargs)

    def _call_back_write(self, target_address: str, object_type: str, instance_number: int, property_identifier: str, value):
        self.logging(content=f"{target_address} set ({object_type}, {instance_number}) {property_identifier} {value}", pos=self.stack_pos)

    def _create_address(self, target_address: str):
        return Address(target_address.split('/')[0])

    def _parse_adderss(self, target_address: Optional[str]):
        address = None
        id = None
        ip = None
        if isinstance(target_address, str) and len(target_address) > 0:
            if target_address.find(':') > 0:    # 6:2/502/192.168.1.184
                infos = target_address.split('/')
                if len(infos) == 1:
                    address = infos[0]
                elif len(infos) == 2:
                    address = infos[0]
                    id = int(str(infos[1]))
                elif len(infos) >= 3:
                    address = infos[0]
                    id = int(str(infos[1]))
                    ip = infos[2]
                    self.route(ip, int(address.split(':')[0]))
            else:
                infos = target_address.split('/')
                if len(infos) == 1:
                    address = infos[0]
                elif len(infos) == 2:
                    address = infos[0]
                    id = int(str(infos[1]))
                elif len(infos) >= 3:
                    address = infos[0]
                    id = int(str(infos[1]))
                    ip = infos[2]
        return address, id, ip

    def _init_results(self, target_address: str, object_type: str, instance_number: int, properties: Optional[list] = None) -> dict:
        results = {}
        for property_identifier in properties:
            results[self._gen_key(target_address, object_type, instance_number, property_identifier)] = ['Bad', 'UnKnown']
        return results

    def _cast_value(self, value, datatype):
        if datatype is Integer:
            value = int(value)
        elif datatype is Real:
            value = float(value)
        elif datatype is Unsigned:
            value = int(value)
        return datatype(value)

    def _convert_value_to_set(self, value, datatype, index):
        bac_value = None
        if value is None:
            pass
        elif value == 'null':
            bac_value = Null()
        elif issubclass(datatype, Atomic):
            bac_value = self._cast_value(value, datatype)
        elif issubclass(datatype, Array) and (index is not None):
            if index == 0:
                bac_value = Integer(value)
            elif issubclass(datatype.subtype, Atomic):
                bac_value = datatype.subtype(value)
            elif not isinstance(value, datatype.subtype):
                raise TypeError(f"invalid result datatype, expecting {datatype.subtype.__name__}")
        elif not isinstance(value, datatype):
            raise TypeError(f"invalid result datatype, expecting {datatype.__name__}")
        return bac_value

    def _create_cov_subscription(self, target_address: str, object_type: str, instance_number: int, lifetime: Optional[int] = None, confirmed: bool = True):
        if self._get_application():
            subscription = None
            for sub in self._get_application().sub_cov_contexts.values():
                if sub.target_address == target_address and sub.object_type == object_type and sub.instance_number == instance_number:
                    subscription = sub
                    break
            if subscription is None:
                subscription = SubscriptionContext(target_address, object_type, instance_number,
                                                   self._get_application().cov_sub_process_id, lifetime, confirmed)
                self._get_application().sub_cov_contexts[self._get_application().cov_sub_process_id] = subscription
                self._get_application().cov_sub_process_id += 1
            if subscription:
                self._send_cov_subscription(subscription.target_address, subscription.sub_process_id,
                                            subscription.object_type, subscription.instance_number, lifetime, confirmed)

    def _send_cov_subscription(self, target_address: str, sub_process_id: int, object_type: str, instance_number: int, lifetime: Optional[int] = None, confirmed: bool = True):
        request = SubscribeCOVRequest(subscriberProcessIdentifier=sub_process_id,
                                      monitoredObjectIdentifier=(object_type, instance_number),
                                      issueConfirmedNotifications=confirmed, lifetime=lifetime)
        request.pduDestination = self._create_address(target_address)
        iocb = self._send_request(request)
        return self._parse_response(request, iocb)

    def _update_device(self, target_address: Optional[str], **kwargs):
        if target_address is not None:
            if target_address not in self.bacnet_devices.keys():
                self.bacnet_devices[target_address] = {'objects': {}}

            if 'object_type' in kwargs.keys() and 'instance_number' in kwargs.keys():
                key = f"{kwargs.get('object_type')}_{kwargs.get('instance_number')}"
                if key not in self.bacnet_devices[target_address]['objects']:
                    self.bacnet_devices[target_address]['objects'][key] = {}
                if 'presentValue' in kwargs.keys():
                    kwargs['update'] = IOTBaseCommon.get_datetime_str()
                self.bacnet_devices[target_address]['objects'][key].update(kwargs)
            else:
                self.bacnet_devices[target_address].update(kwargs)

    def _make_mutable(self, object, identifier="presentValue", mutable=True):
        for prop in object.properties:
            if prop.identifier == identifier:
                prop.mutable = mutable
        return object

    def _create_object(self, object: IOTSimulateObject):
        try:
            if self._get_application() is not None:
                object_type = object.get('point_type')
                instance_number = object.get('point_address')
                if object_type is not None and instance_number is not None:
                    key = f"{object_type}_{instance_number}"
                    if key not in self.bacnet_objects.keys():
                        object_classs = {
                            'analogInput': BacnetSimulateObject.BacnetAnalogInputObject,
                            'analogOutput': BacnetSimulateObject.BacnetAnalogOutputObject,
                            'analogValue': BacnetSimulateObject.BacnetAnalogValueObject,
                            'binaryInput': BacnetSimulateObject.BacnetBinaryInputObject,
                            'binaryOutput': BacnetSimulateObject.BacnetBinaryOutputObject,
                            'binaryValue': BacnetSimulateObject.BacnetBinaryValueObject,
                            'multiStateInput': BacnetSimulateObject.BacnetMultiStateInputObject,
                            'multiStateOutput': BacnetSimulateObject.BacnetMultiStateOutputObject,
                            'multiStateValue': BacnetSimulateObject.BacnetMultiStateValueObject,
                            'bitstringValue': BacnetSimulateObject.BacnetBitStringValueObject,
                            'characterstringValue': BacnetSimulateObject.BacnetCharacterStringValueObject,
                            'octetstringValue': BacnetSimulateObject.BacnetOctetStringValueObject,
                        }
                        object_class = object_classs.get(object_type)
                        if object_class is not None:
                            new_object = object_class(
                                objectIdentifier=(object_type, instance_number),
                                objectName=object.get('point_name', key),
                                presentValue=self._convert_value_to_set(IOTBaseCommon.format_value(object.get('point_value')), get_datatype(object_type, 'presentValue'), None),
                                description=CharacterString(object.get('point_description', '')),
                                statusFlags=StatusFlags(),
                            )
                            new_object = self._make_mutable(new_object, mutable=object.get('mutable', False))
                            self._get_application().add_object(new_object)
                            self.bacnet_objects[key] = [new_object, object]
        except Exception as e:
            self.logging(content=f"create object({object.get('point_type')} {object.get('point_address')}) fail({e.__str__()})", level='ERROR', pos=self.stack_pos)

    def update_object(self, object_type: str, instance_number: int, value=None, flags=[0, 0, 0, 0]):
        self.logging(content=f"update object({object_type}-{instance_number}-{value})")
        key = f"{object_type}_{instance_number}"
        if key in self.bacnet_objects.keys():
            self.bacnet_objects[key][0].presentValue = value
            self.bacnet_objects[key][0].statusFlags = flags

    def refresh_objects(self, objects: List[IOTSimulateObject]):
        for object in objects:
            object_type = object.get('point_type')
            instance_number = object.get('point_address')
            value = IOTBaseCommon.format_value(object.get('point_value'))
            try:
                if object_type is not None and instance_number is not None and value not in [None, '']:
                    key = f"{object_type}_{instance_number}"
                    if key in self.bacnet_objects.keys():
                        self.bacnet_objects[key][0].presentValue = self._convert_value_to_set(value, get_datatype(object_type, 'presentValue'), None)
            except Exception as e:
                self.logging(content=f"refresh object({object.get('point_type')} {object.get('point_address')}) fail({e.__str__()})", level='ERROR', pos=self.stack_pos)

    def logging(self, **kwargs):
        if self.parent:
            if hasattr(self.parent, 'logging'):
                self.parent.logging(**kwargs)

    @property
    def stack_pos(self):
        return f"{IOTBaseCommon.get_file_name(stack()[1][1])}({stack()[1][2]})"


class IOTBacnet(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.client = None
        self.server = None

    def exit(self):
        self.exit_flag = True

        self._release_client()

        self._release_server()

        self.reinit()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.append({'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''})
            templates.append({'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''})
            if mode == 0:
                templates.append({'code': 'point_device_address', 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'required': True, 'type': 'string', 'default': '192.168.1.1/2', 'enum': [], 'tip': ''})
            templates.append({'code': 'point_type', 'name': '点类型' if lan == 'ch' else 'type'.upper(), 'required': True, 'type': 'string', 'default': 'analogInput', 'enum': ['analogInput', 'analogOutput', 'analogValue', 'binaryInput', 'binaryOutput', 'binaryValue', 'multiStateInput', 'multiStateOutput', 'multiStateValue'], 'tip': ''})
            if mode == 0:
                templates.append({'code': 'point_property', 'name': '点属性' if lan == 'ch' else 'property'.upper(), 'required': True, 'type': 'string', 'default': 'presentValue', 'enum': ['presentValue', 'objectName', 'eventState', 'description'], 'tip': ''})
            templates.append({'code': 'point_address', 'name': '点地址' if lan == 'ch' else 'address'.upper().upper(), 'required': True, 'type': 'int', 'default': '1', 'enum': [], 'tip': ''})
            templates.append({'code': 'point_description', 'name': '点描述' if lan == 'ch' else 'description', 'required': False, 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''})
            if mode == 0:
                templates.append({'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': '点值' if lan == 'ch' else 'value'.upper(), 'code': 'point_value', 'type': 'int', 'default': 0, 'enum': [], 'tip': ''})
            templates.append({'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''})
            templates.append({'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''})
        elif type in ['config', 'scan']:
            templates.append({'name': '绑定网卡' if lan == 'ch' else 'Address', 'required': True, 'code': 'address', 'type': 'string', 'default': '192.168.1.42/24:47808', 'enum': [], 'tip': ''})
            templates.append({'name': '设备ID' if lan == 'ch' else 'Bacnet Sever ID', 'required': True, 'code': 'identifier', 'type': 'int', 'default': 5555, 'enum': [], 'tip': ''})
            templates.append({'name': '设备名称' if lan == 'ch' else 'Bacnet Sever Name', 'required': True, 'code': 'name', 'type': 'string', 'default': 'BacnetDriver', 'enum': [], 'tip': ''})
            templates.append({'name': '设备APDU' if lan == 'ch' else 'Bacnet Sever APDU', 'required': True, 'code': 'max_apdu', 'type': 'int', 'default': 1024, 'enum': [], 'tip': ''})
            templates.append({'name': '设备segmentation' if lan == 'ch' else 'Bacnet Sever segmentation', 'required': True, 'code': 'segmentation', 'type': 'string', 'default': 'segmentedBoth', 'enum': [], 'tip': ''})
            templates.append({'name': '设备vendor' if lan == 'ch' else 'Bacnet Sever vendor', 'required': True, 'code': 'vendor_identifier', 'type': 'int', 'default': 15, 'enum': [], 'tip': ''})

            if mode == 0:
                templates.append({'name': '批量读取个数' if lan == 'ch' else 'Multi Read', 'required': True, 'code': 'multi_read', 'type': 'int', 'default': 20, 'enum': [], 'tip': ''})
                templates.append({'name': '命令间隔(s)' if lan == 'ch' else 'Cmd Interval(s)', 'required': True, 'code': 'cmd_interval', 'type': 'float', 'default': 0.3, 'enum': [], 'tip': ''})
                templates.append({'name': '失败重试' if lan == 'ch' else 'Multi Retry', 'required': True, 'code': 'retry', 'type': 'int', 'default': 0, 'enum': [], 'tip': ''})
                templates.append({'name': '连续超时失败重连' if lan == 'ch' else 'Timeout Retries', 'required': False, 'code': 'timeout_flag', 'type': 'int', 'default': 5, 'enum': [], 'tip': ''})
            templates.append({'name': '超时(ms)' if lan == 'ch' else 'Timeout(ms)', 'required': True, 'code': 'timeout', 'type': 'int', 'default': 5000, 'enum': [], 'tip': ''})

            if type == 'scan':
                templates.append({'name': '目标设备' if lan == 'ch' else 'Target'.title(), 'required': True, 'code': 'target', 'type': 'string', 'default': '', 'enum': [], 'tip': ''})
                templates.append({'name': '是否连读' if lan == 'ch' else 'use read multiple'.title(), 'required': True, 'code': 'use_read_multiple', 'type': 'bool', 'default': True, 'enum': [], 'tip': ''})
                templates.append({'name': '是否检查连接' if lan == 'ch' else 'ping check'.title(), 'required': True, 'code': 'ping_check', 'type': 'bool', 'default': True, 'enum': [], 'tip': ''})
        return templates

    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        names = kwargs.get('names', list(self.points.keys()))
        self.update_results(names, True, None)

        read_items = {}
        for name in names:
            point = self.points.get(name)
            if point:
                target_address = point.get('point_device_address')
                object_type = point.get('point_type')
                instance_number = point.get('point_address')
                point_property = point.get('point_property', 'presentValue')
                if target_address is not None and object_type is not None and instance_number is not None:
                    if target_address not in read_items.keys():
                        read_items[target_address] = []
                    read = (object_type, instance_number, point_property)
                    if read not in read_items[target_address]:
                        read_items[target_address].append(read)

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                target_address = point.get('point_device_address')
                object_type = point.get('point_type')
                instance_number = point.get('point_address')
                point_property = point.get('point_property', 'presentValue')
                value = self._get_value(name, target_address, object_type, instance_number, point_property)
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
                target_address = point.get('point_device_address')
                object_type = point.get('point_type')
                instance_number = point.get('point_address')
                point_property = point.get('point_property', 'presentValue')
                if target_address is not None and object_type is not None and instance_number is not None:
                    results[name] = self._write(name, target_address, object_type, instance_number, point_property, value)
            else:
                results[name] = [False, 'UnExist']
        return results

    def scan(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        self.logging(content=f"scan({kwargs.get('address')})", pos=self.stack_pos)

        devices = {}
        if self._get_client():
            address = kwargs.get('address')
            if address:
                devices = {address: self.client.scan(target_address=address, use_read_multiple=kwargs.get('use_read_multiple', True), ping_check=kwargs.get('ping_check', True))}
            else:
                devices = self.discover(retries=2, **kwargs)
                for address, device in devices.items():
                    self.client.scan(target_address=f"{address}/{device.get('device_id')}/{device.get('address')}", use_read_multiple=kwargs.get('use_read_multiple', True), ping_check=kwargs.get('ping_check', False))

        for address, device in devices.items():
            objects = device.get('objects', {})
            for name, object in objects.items():
                point_name = IOTBaseCommon.format_name(f"{device.get('address')}_{device.get('device_id')}_{name}")
                results[point_name] = self.create_point(point_name=point_name, point_name_alias=point_name, point_property_index=object.get('property_index'), point_type=object.get('object_type'), point_device_address=address, point_property='presentValue', point_address=object.get('instance_number'), point_description=object.get('description') if object.get('description') is not None else object.get('objectName'), point_value=object.get('presentValue'))

        return results

    def ping(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        if self._get_client():
            target_address = kwargs.get('address')
            if target_address:
                return self.client.ping_target(target_address)
        return False

    def simulate(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        points = kwargs.get('points', {})
        callbacks = kwargs.get('callbacks', {})
        self.logging(content=f"simulate({len(points)})", pos=self.stack_pos)
        objects = []
        for name, point in points.items():
            objects.append(IOTSimulateObject(**point))

        if self._get_server():
            self.server.simluate(objects, callbacks)

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        self.logging(content=f"discover({kwargs.get('address')}) {kwargs.get('retries', 1)}", pos=self.stack_pos)
        if self._get_client():
            retries = kwargs.get('retries', 1)
            while retries > 0:
                self.client.discover(kwargs.get('low_device_id'), kwargs.get('high_device_id'), kwargs.get('address'))
                retries = retries - 1
        devices = self.client.devices()
        self.update_info(discover=len(devices))
        return devices

    def _get_client(self):
        if self.client is None:
            self.client = BacnetClient(True, self, **self.configs)
        return self.client

    def _release_client(self):
        try:
            if self.client is not None:
                self.client.exit()
        except:
            pass
        finally:
            self.client = None

    def _get_server(self):
        if self.server is None:
            self.server = BacnetClient(False, self, **self.configs)
        return self.server

    def _release_server(self):
        try:
            if self.server is not None:
                self.server.exit()
        except:
            pass
        finally:
            self.server = None

    def _read(self, read_items: dict):
        if len(read_items) > 0:
            if self._get_client():
                for target_address, objct_propertys in read_items.items():
                    start = time.time()
                    self.client.read(target_address=target_address, objct_propertys=objct_propertys, max_per_request=self.configs.get('multi_read'), use_read_multiple=self.configs.get('multi_read') > 1, ping_check=False)
                    self.logging(content=f"bacnet({target_address}) read: {len(objct_propertys)} cost: {'{:.2f}'.format(time.time() - start)}", pos=self.stack_pos)

    def _get_value(self, name: str, target_address: str, object_type: str, instance_number: int, point_property: str):
        if self._get_client():
            quality, value = self.client.value(target_address, object_type, instance_number, point_property)
            if quality == 'Good':
                return value
            else:
                self.update_results(name, False, value)
        return None

    def _write(self, name: str, target_address: str, object_type: str, instance_number: int, property_name: str, value):
        try:
            if self._get_client():
                return self.client.write(target_address=target_address, object_type=object_type, instance_number=instance_number, property_name=property_name, value=value)
        except Exception as e:
            self.logging(content=f"write point({name}) fail({e.__str__()})", level='ERROR', source=name, pos=self.stack_pos)
        return False

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_bacnet.py({pos})"
