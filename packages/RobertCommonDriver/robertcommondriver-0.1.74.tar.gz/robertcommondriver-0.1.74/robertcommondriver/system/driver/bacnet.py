import time
import logging
from threading import Lock
from typing import Optional
from collections import deque
from datetime import datetime
from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut
from ipaddress import ip_network, ip_address
from psutil import net_if_addrs
from .base import BasePoint, BaseDriver, PointTableDict, BaseCommon

# bacnet
from bacpypes.app import BIPSimpleApplication
from bacpypes.apdu import AbortReason, RejectReason, ReadAccessSpecification, PropertyReference, ReadPropertyMultipleRequest, ReadPropertyMultipleACK, ReadPropertyRequest, ReadPropertyACK, WritePropertyRequest, SimpleAckPDU, WhoIsRequest, IAmRequest, AbortPDU, RejectPDU
from bacpypes.basetypes import ServicesSupported
from bacpypes.constructeddata import Array, Any
from bacpypes.core import run, stop, deferred, enable_sleeping
from bacpypes.debugging import bacpypes_debugging
from bacpypes.errors import DecodingError
from bacpypes.iocb import IOCB
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import get_datatype
from bacpypes.primitivedata import Null, Atomic, Integer, Unsigned, Real
from bacpypes.pdu import GlobalBroadcast, Address
from bacpypes.service.object import ReadWritePropertyMultipleServices

'''
 pip install bacpypes==0.18.5
'''

'''
20220406
    短连接模式
    
20220411
    优化反馈匹配
'''

# Tweeks to BACpypes to make it play nice with Gevent.
enable_sleeping()


# BacnetPoint
class BacnetPoint(BasePoint):

    # point_writable, point_name, point_device_address, point_type, point_property, point_address, point_description
    def __init__(self, point_writable: bool, point_name: str, point_device_address: str, point_type: str, point_property: str, point_address: int, point_description: str = ''):
        super().__init__('bacnet', point_writable, point_name, point_description)

        self.point_device_address = point_device_address
        self.point_type = point_type
        self.point_property = point_property
        self.point_address = point_address

    # get point_device_address
    @property
    def get_point_device_address(self):
        return self.point_device_address

    # get point_type
    @property
    def get_point_type(self):
        return self.point_type

    # get point_property
    @property
    def get_point_property(self):
        return self.point_property

    # get point_address
    @property
    def get_point_address(self):
        return self.point_address


# bacnet context
class ObjectListContext:

    # init
    def __init__(self, bacnet_device_id: tuple, bacnet_address: str, bacnet_property_list: list, bacnet_start_array_index: int = None, bacnet_end_array_index: int = None, bacnet_current: int = None):
        self.bacnet_device_id = bacnet_device_id  # bacnet device ID
        self.bacnet_address = bacnet_address  # bacnet address
        self.bacnet_object_list = []  # bacnet object list
        self.bacnet_array_index = 0  # property array index
        self.bacnet_object_name_list = []
        self.bacnet_list_queue = None
        self.bacnet_property_list = bacnet_property_list  # bacnet property
        self.bacnet_object_count = 0  # bacnet object count
        self.current_object = 0  # current bacnet object index
        self.bacnet_object_dict = {}  # {ObjectIndex : {value:dict}}
        self.bacnet_start_array_index = bacnet_start_array_index  # start array index
        self.bacnet_end_array_index = bacnet_end_array_index  # end array index
        self.bacnet_current = bacnet_current  # current index

        self.bacnet_property_reference_list = []
        for property_identifier in bacnet_property_list:
            prop_reference = PropertyReference(
                propertyIdentifier=property_identifier,
            )
            self.bacnet_property_reference_list.append(prop_reference)

    # read complete
    def completed(self):
        stop()

    # get point dict
    def get_bacnet_point_dict(self) -> dict:
        return self.bacnet_object_dict

    # get point count
    def get_bacnet_point_count(self):
        return self.bacnet_object_count


# Bacnet read/write class
class BacnetApplication(BIPSimpleApplication):

    #
    def __init__(self, local_device, local_address: str, parent: Any = None):
        try:
            self.bacnet_context = None
            self.bancet_create = False
            self.parent = parent
            self.bacnet_device_address_dict = {}
            self.date_response = datetime.now()
            self.lock_read_write_handler = Lock()  # read/write lock

            self.bacnet_cmd_interval = 0.3
            self.bacnet_multi_read = 20
            self.address_network_dict = {}

            self.bacnet_support_property = ['analogInput', 'analogOutput', 'analogValue', 'binaryInput', 'binaryOutput', 'binaryValue', 'multiStateInput', 'multiStateOutput', 'multiStateValue']

            #
            BIPSimpleApplication.__init__(self, local_device, local_address)

            self.bancet_create = True
        except Exception as e:
            raise Exception('init bacnet(%s) fail(%s)' % (local_address, e.__str__()))

    # end
    def __del__(self):
        self.exit()

    def __str__(self):
        return f"{self.localAddress}"

    def exit(self):
        stop()

    # bacnet request
    def request(self, apdu):
        try:
            # forward it along
            BIPSimpleApplication.request(self, apdu)
        except Exception as e:
            logging.error(f"bacnet({self}) request fail({e.__str__()})")

    # Bacnet config
    def confirmation(self, apdu):
        try:
            # forward it along
            BIPSimpleApplication.confirmation(self, apdu)
        except Exception as e:
            logging.error(f"bacnet({self}) confirmation fail({e.__str__()})")

    # Bacnet
    def indication(self, apdu):
        try:
            # forward it along
            BIPSimpleApplication.indication(self, apdu)
        except Exception as e:
            logging.error(f"bacnet({self}) indication fail({e.__str__()})")

    # end
    def end_discover(self):
        stop()

    # get if timeout
    def get_time_out(self, time_out: int = 5) -> bool:
        if (datetime.now() - self.date_response).total_seconds() >= time_out:
            return True
        return False

    # search Bacnet device
    def discover_bacnet_device(self):
        try:
            broad_address = GlobalBroadcast()
            BIPSimpleApplication.who_is(self, None, None, broad_address)
            self.date_response = datetime.now()
        except Exception as e:
            logging.error(f"bacnet({self}) discover device fail({e.__str__()})")

    # get Bacnet device list
    def get_bacnet_device_list(self) -> list:
        bacnet_device_list = []
        for read_key in self.bacnet_device_address_dict.keys():
            bacnet_device_list.append(read_key)
            bacnet_device_list.sort()
        return bacnet_device_list

    # whois
    def do_WhoIsRequest(self, apdu):
        try:
            """Respond to a Who-Is request."""

            # continue with the default implementation
            BIPSimpleApplication.do_WhoIsRequest(self, apdu)
        except Exception as e:
            logging.error(f"bacnet({self}) whois fail({e.__str__()})")

    # iam
    def do_IAmRequest(self, apdu):
        try:
            self.date_response = datetime.now()

            read_key = f"{str(apdu.pduSource)}/{int(apdu.iAmDeviceIdentifier[1])}"
            if apdu.pduSource.addrType == Address.remoteStationAddr:
                read_key = f"{read_key}/{self.nsap.router_info_cache.get_router_info(None, apdu.pduSource.addrNet).address}"

            if read_key not in self.bacnet_device_address_dict.keys():
                self.parent.set_call_result('debug_log', content=f"bacnet({self}) received device {len(self.bacnet_device_address_dict)}({read_key})")

            self.bacnet_device_address_dict[read_key] = apdu

            # continue with the default implementation
            BIPSimpleApplication.do_IAmRequest(self, apdu)
        except Exception as e:
            logging.error(f"bacnet({self}) iam fail({e.__str__()})")

    # whohas
    def do_WhoHasRequest(self, apdu):
        try:
            """Respond to a Who-Has request."""

            BIPSimpleApplication.do_WhoHasRequest(self, apdu)
        except Exception as e:
            logging.error(f"bacnet({self}) whohas fail({e.__str__()})")

    # IHave
    def do_IHaveRequest(self, apdu):
        try:
            """Respond to a I-Have request."""

            BIPSimpleApplication.do_IHaveRequest(self, apdu)
        except Exception as e:
            logging.error(f"bacnet({self}) ihave fail({e.__str__()})")

    #
    def read_bacnet_object_count(self, bacnet_device_id: tuple, bacnet_address: str, bacnet_property_list: list, bacnet_start_array_index: int, bacnet_end_array_index: int, bacnet_current: int):
        try:
            self.bacnet_context = ObjectListContext(bacnet_device_id, bacnet_address, bacnet_property_list, bacnet_start_array_index, bacnet_end_array_index, bacnet_current)

            # read
            bacnet_request = ReadPropertyRequest(
                destination=self.bacnet_context.bacnet_address,
                objectIdentifier=self.bacnet_context.bacnet_device_id,
                propertyIdentifier='objectList',
                propertyArrayIndex=0
            )
            bacnet_iocb = IOCB(bacnet_request)
            bacnet_iocb.context = self.bacnet_context
            bacnet_iocb.add_callback(self.bacnet_object_count_result)  # add callback
            self.request_io(bacnet_iocb)
        except Exception as e:
            logging.error(f"bacnet({self}) read object fail({e.__str__()})")

    # get bacnet object count
    def get_bacnet_object_count(self, bacnet_device_id: tuple, bacnet_address: str, bacnet_current: int):
        try:
            self.bacnet_context = ObjectListContext(bacnet_device_id, bacnet_address, [], None, None, bacnet_current)

            #
            bacnet_request = ReadPropertyRequest(
                destination=self.bacnetContext.bacnet_address,
                objectIdentifier=self.bacnetContext.bacnet_device_id,
                propertyIdentifier='objectList',
                propertyArrayIndex=0
            )
            bacnet_iocb = IOCB(bacnet_request)
            bacnet_iocb.context = self.bacnet_context
            bacnet_iocb.add_callback(self.get_bacnet_object_count_result)  # add callback
            self.request_io(bacnet_iocb)
        except Exception as e:
            logging.error(f"bacnet({self}) get object fail({e.__str__()})")

    def get_bacnet_object_count_result(self, bacnet_iocb):
        bacnet_context = None
        try:
            bacnet_context = bacnet_iocb.context
            if not bacnet_iocb.ioError:
                bacnet_apdu = bacnet_iocb.ioResponse
                if isinstance(bacnet_apdu, ReadPropertyACK):
                    bacnet_data_type = get_datatype(bacnet_apdu.objectIdentifier[0], bacnet_apdu.propertyIdentifier)
                    if issubclass(bacnet_data_type, Array) and (bacnet_apdu.propertyArrayIndex is not None):
                        if bacnet_apdu.propertyArrayIndex == 0:
                            bacnet_context.bacnet_object_count = bacnet_apdu.propertyValue.cast_out(Unsigned)
                        else:
                            bacnet_context.bacnet_object_count = bacnet_apdu.propertyValue.cast_out(bacnet_data_type.subtype)
                    else:
                        bacnet_context.bacnet_object_count = bacnet_apdu.propertyValue.cast_out(bacnet_data_type)
        except Exception as e:
            logging.error(f"bacnet({self}) read object result fail({e.__str__()})")
        if bacnet_context:
            bacnet_context.completed()

    def bacnet_object_count_result(self, bacnet_iocb):
        bacnet_context = None
        try:
            bacnet_context = bacnet_iocb.context
            if not bacnet_iocb.ioError:
                bacnet_apdu = bacnet_iocb.ioResponse
                if isinstance(bacnet_apdu, ReadPropertyACK):
                    bacnet_data_type = get_datatype(bacnet_apdu.objectIdentifier[0], bacnet_apdu.propertyIdentifier)
                    if issubclass(bacnet_data_type, Array) and (bacnet_apdu.propertyArrayIndex is not None):
                        if bacnet_apdu.propertyArrayIndex == 0:
                            bacnet_context.bacnet_object_count = bacnet_apdu.propertyValue.cast_out(Unsigned)
                        else:
                            bacnet_context.bacnet_object_count = bacnet_apdu.propertyValue.cast_out(bacnet_data_type.subtype)
                    else:
                        bacnet_context.bacnet_object_count = bacnet_apdu.propertyValue.cast_out(bacnet_data_type)
        except Exception as e:
            logging.error(f"bacnet({self}) get object result fail({e.__str__()})")
        finally:
            bacnet_context.current_object = bacnet_context.current_object + 1
            if bacnet_context.bacnet_start_array_index is not None:
                bacnet_context.current_object = bacnet_context.bacnet_start_array_index
            # read next object
            deferred(self.read_bacnet_object_list, bacnet_context)

    #
    def read_bacnet_object_list(self, bacnet_context):
        try:
            # if current_object less than bacnet_end_array_index continute
            if (bacnet_context.bacnet_end_array_index is not None and bacnet_context.current_object > bacnet_context.bacnet_end_array_index) or bacnet_context.current_object > bacnet_context.bacnet_object_count:
                # read property
                bacnet_context.bacnet_list_queue = deque(bacnet_context.bacnet_object_list)
                deferred(self.read_bacnet_property_list, bacnet_context)
            else:
                bacnet_request = ReadPropertyRequest(
                    destination=bacnet_context.bacnet_address,
                    objectIdentifier=bacnet_context.bacnet_device_id,
                    propertyIdentifier='objectList',
                    propertyArrayIndex=bacnet_context.current_object
                )
                if bacnet_context.bacnet_end_array_index is not None:
                    self.parent.set_call_result('debug_log', content=f"bacnet({self}) read object {bacnet_context.current_object}/{bacnet_context.bacnet_end_array_index}({str(bacnet_context.bacnet_current)}-{str(bacnet_context.bacnet_address)}/{str(bacnet_context.bacnet_device_id[1])})")
                else:
                    self.parent.set_call_result('debug_log', content=f"bacnet({self}) read object {bacnet_context.current_object}/{bacnet_context.bacnet_object_count}({str(bacnet_context.bacnet_current)}-{str(bacnet_context.bacnet_address)}/{str(bacnet_context.bacnet_device_id[1])})")

                bacnet_iocb = IOCB(bacnet_request)
                bacnet_iocb.context = bacnet_context
                bacnet_iocb.add_callback(self.bacnet_object_list_result)
                self.request_io(bacnet_iocb)
        except Exception as e:
            logging.error(f"bacnet({self}) read object list fail({e.__str__()})")

    def bacnet_object_list_result(self, bacnet_iocb):
        bacnet_context = None
        try:
            bacnet_context = bacnet_iocb.context
            if not bacnet_iocb.ioError:
                bacnet_apdu = bacnet_iocb.ioResponse
                if isinstance(bacnet_apdu, ReadPropertyACK):
                    bacnet_data_type = get_datatype(bacnet_apdu.objectIdentifier[0], bacnet_apdu.propertyIdentifier)
                    if issubclass(bacnet_data_type, Array) and (bacnet_apdu.propertyArrayIndex is not None):
                        if bacnet_apdu.propertyArrayIndex == 0:
                            bacnet_context.bacnet_object_list.append([bacnet_apdu.propertyArrayIndex, bacnet_apdu.propertyValue.cast_out(Unsigned)])
                        else:
                            bacnet_context.bacnet_object_list.append([bacnet_apdu.propertyArrayIndex, bacnet_apdu.propertyValue.cast_out(bacnet_data_type.subtype)])
                    else:
                        bacnet_context.bacnet_object_list.append([bacnet_apdu.propertyArrayIndex, bacnet_apdu.propertyValue.cast_out(bacnet_apdu)])
        except Exception as e:
            logging.error(f"bacnet({self}) read object list result fail({e.__str__()})")
        finally:
            bacnet_context.current_object = bacnet_context.current_object + 1
            # next
            deferred(self.read_bacnet_object_list, bacnet_context)

    def read_bacnet_property_list(self, bacnet_context):
        try:
            if not bacnet_context.bacnet_list_queue:
                bacnet_context.completed()
            else:
                bacnet_array_index, bacnet_object_id = bacnet_context.bacnet_list_queue.popleft()
                self.parent.set_call_result('debug_log', content=f"read bacnet property left {len(bacnet_context.bacnet_list_queue)}({str(bacnet_context.bacnet_current)}-{str(bacnet_context.bacnet_address)}/{str(bacnet_context.bacnet_device_id[1])})")

                bacnet_read_access_spec = ReadAccessSpecification(
                    objectIdentifier=bacnet_object_id,
                    listOfPropertyReferences=bacnet_context.bacnet_property_reference_list,
                )
                bacnet_read_access_spec_list = list()
                bacnet_read_access_spec_list.append(bacnet_read_access_spec)

                bacnet_request = ReadPropertyMultipleRequest(
                    listOfReadAccessSpecs=bacnet_read_access_spec_list,
                )
                bacnet_request.pduDestination = bacnet_context.bacnet_address
                bacnet_context.bacnet_array_index = bacnet_array_index

                # make an IOCB, reference the context
                bacnet_iocb = IOCB(bacnet_request)
                bacnet_iocb.context = bacnet_context
                bacnet_iocb.add_callback(self.read_bacnet_property_list_result)
                self.request_io(bacnet_iocb)
        except Exception as e:
            logging.error(f"bacnet({self}) read object property fail({e.__str__()})")

    def _format_name(self, device_address: str, device_id: str, type: str, address: str):
        return '%s_%s_%s_%s' % (device_address.replace('.', '_').replace(':', '_'), device_id, type, address)

    def read_bacnet_property_list_result(self, bacnet_iocb):
        bacnet_context = bacnet_iocb.context
        try:
            if not bacnet_iocb.ioError:
                bacnet_apdu = bacnet_iocb.ioResponse

                if isinstance(bacnet_apdu, ReadPropertyMultipleACK):
                    for result in bacnet_apdu.listOfReadAccessResults:
                        object_identifier = result.objectIdentifier
                        bacnet_point_name = self._format_name(str(bacnet_context.bacnet_address), str(bacnet_context.bacnet_device_id[1]), str(object_identifier[0]), str(object_identifier[1]))
                        property_dict = dict()
                        for element in result.listOfResults:
                            property_identifier = element.propertyIdentifier
                            property_array_index = element.propertyArrayIndex
                            read_result = element.readResult

                            if read_result.propertyAccessError is None:
                                property_name = str(property_identifier)
                                property_value = read_result.propertyValue

                                bacnet_data_type = get_datatype(object_identifier[0], property_identifier)
                                if bacnet_data_type:
                                    if issubclass(bacnet_data_type, Array) and (property_array_index is not None):
                                        if property_array_index == 0:
                                            property_dict[property_name] = str(property_value.cast_out(Unsigned))
                                        else:
                                            property_dict[property_name] = str(property_value.cast_out(bacnet_data_type.subtype))
                                    else:
                                        property_dict[property_name] = str(property_value.cast_out(bacnet_data_type))

                        if str(object_identifier[0]) in self.bacnet_support_property:
                            bacnet_point_property = {'point_name': bacnet_point_name, 'index': bacnet_context.bacnet_array_index, 'point_writable': 'True', 'point_device_address': '%s/%s' % (str(bacnet_context.bacnet_address), str(bacnet_context.bacnet_device_id[1])), 'point_type': str(object_identifier[0]), 'point_property': 'presentValue', 'point_address': str(object_identifier[1]), 'point_description': ''}
                            bacnet_point_property.update(property_dict)
                            bacnet_context.bacnet_object_dict[bacnet_point_name] = bacnet_point_property

        except Exception as e:
            logging.error(f"bacnet({self}) read object property reasult fail({e.__str__()})")
        finally:
            deferred(self.read_bacnet_property_list, bacnet_context)

    def get_bacnet_point_dict(self) -> dict:
        bacnet_point_dict = {}
        if self.bacnet_context:
            bacnet_point_dict = self.bacnet_context.get_bacnet_point_dict()
        return bacnet_point_dict

    def get_bacnet_point_count(self) -> int:
        bacnet_object_count = 0
        if self.bacnet_context:
            bacnet_object_count = self.bacnet_context.get_bacnet_point_count()
        return bacnet_object_count

    def _get_bacnet_max_read_count_by_apdu_length(self, max_apdu_length: int) -> int:
        max_read_count = int((max_apdu_length - 57) / 9)
        if max_apdu_length <= 0:
            max_read_count = 1
        return max_read_count

    def get_bacnet_max_read_count(self, address_key: str, bacnet_multi_read: int) -> int:
        max_read_count = bacnet_multi_read
        if len(address_key) > 0:
            if address_key in self.bacnet_device_address_dict.keys():
                return self._get_bacnet_max_read_count_by_apdu_length(self.bacnet_device_address_dict[address_key].maxAPDULengthAccepted)
        return max_read_count

    def get_bacnet_dest_address(self, address_key: str):
        if address_key in self.bacnet_device_address_dict.keys():
            return self.bacnet_device_address_dict[address_key].pduSource

        address = address_key.split('/')
        if len(address) == 3:
            self.add_route_by_device(str(address[2]), address_key)
            return Address(str(address[0]))

        return Address(str(address[0]))

    def _read_values(self, bacnet_point_dict: dict, bacnet_cmd_interval: float = 0.3, bacnet_multi_read: int = 20) -> dict:
        result_dict = {}
        self.bacnet_cmd_interval = bacnet_cmd_interval
        self.bacnet_multi_read = bacnet_multi_read

        current = 0
        for read_key, points in bacnet_point_dict.items():
            result_dict.update(self._rebuild_bacnet_point_list(read_key, points, current, len(bacnet_point_dict)))
            time.sleep(self.bacnet_cmd_interval)
            current = current + 1
        return result_dict

    def _chunk_list(self, values: list, number: int):
        for i in range(0, len(values), number):
            yield values[i:i + number]

    def rebuild_bacnet_group(self, bacnet_read_multi_list: list, group: int) -> list:
        if len(bacnet_read_multi_list) > 0:
            bacnet_read_multi_list_group = []
            list_access = self._chunk_list(bacnet_read_multi_list, group)

            for access in list_access:
                bacnet_read_multi_list_group.append(access)

            return bacnet_read_multi_list_group
        return bacnet_read_multi_list

    def _rebuild_bacnet_point_list(self, read_key: str, bacnet_point_list: list, current: int, total: int) -> dict:
        result_dict = {}
        try:
            max_read_count = self.get_bacnet_max_read_count(read_key, self.bacnet_multi_read)

            # If the maximum number of reads is less than the length, regrouping is required
            if max_read_count < len(bacnet_point_list):
                bacnet_read_multi_list_group = self.rebuild_bacnet_group(bacnet_point_list, max_read_count)
                for index, _bacnet_read_multi_list in enumerate(bacnet_read_multi_list_group):
                    process = f"{current+1}/{total}-{index+1}/{len(bacnet_read_multi_list_group)}"
                    # Here according to the specified length to re-categorize and adjust the number of reads
                    if len(_bacnet_read_multi_list) == 1 and max_read_count == 1:  # Single point reading
                        result_dict.update(self.read_single_value(read_key, _bacnet_read_multi_list, process))
                    else:  # Batch read
                        result_dict.update(self.read_multi_value(read_key, _bacnet_read_multi_list, process))
                    time.sleep(self.bacnet_cmd_interval)
            else:
                # Here to reclassify and adjust the number of reads according to the specified length
                process = f"{current+1}/{total}-1/1"
                if len(bacnet_point_list) == 1 and max_read_count == 1:  # Single point reading
                    result_dict.update(self.read_single_value(read_key, bacnet_point_list, process))
                else:  # Batch read
                    result_dict.update(self.read_multi_value(read_key, bacnet_point_list, process))
        except Exception as e:
            logging.error(f"bacnet({self}) rebulid object point fail({e.__str__()})")
        return result_dict

    # readKey:address_type
    def read_multi_value(self, read_key: str, bacnet_point_list: list, process: str) -> dict:
        result_dict = {}
        bacnet_tag_dict = {}
        with self.lock_read_write_handler:
            try:
                pdu_destination = self.get_bacnet_dest_address(read_key)
                if pdu_destination:  # Receive device target address
                    bacnet_read_multi_list = []
                    for point in bacnet_point_list:
                        point_type = point.get_point_type
                        point_address = point.get_point_address
                        point_property = point.get_point_property
                        point_name = point.get_point_name

                        bacnet_prop_list = list()
                        bacnet_prop_list.append(PropertyReference(propertyIdentifier=point_property, ))

                        # build a read access specification
                        bacnet_read_access = ReadAccessSpecification(
                            objectIdentifier=(point_type, point_address),
                            listOfPropertyReferences=bacnet_prop_list,
                        )
                        bacnet_read_multi_list.append(bacnet_read_access)
                        bacnet_tag_dict['%s_%s_%s' % (point_type, str(point_address), point_property)] = point_name

                    # Create bulk read requests
                    request = ReadPropertyMultipleRequest(
                        listOfReadAccessSpecs=bacnet_read_multi_list,
                    )
                    request.pduDestination = pdu_destination

                    # Generate a IOCB
                    iocb = IOCB(request)

                    self.request_io(iocb)

                    iocb.wait()

                    if iocb.ioResponse:
                        apdu = iocb.ioResponse

                        # The returned apdu type judgment must be an ack
                        if not isinstance(apdu, ReadPropertyMultipleACK):
                            return result_dict

                        for result in apdu.listOfReadAccessResults:

                            # ('analogInput', 17)
                            object_identifier = result.objectIdentifier

                            # Traverse the property value of each object
                            for element in result.listOfResults:
                                property_identifier = element.propertyIdentifier
                                property_array_index = element.propertyArrayIndex
                                read_result = element.readResult
                                point_tag = f'{str(object_identifier[0])}_{str(object_identifier[1])}_{property_identifier}'

                                # Determine whether the attribute value is wrong
                                if read_result.propertyAccessError is not None:
                                    logging.error(f"bacnet({self}) read fail({read_key}-[{point_tag}]-{str(read_result.propertyAccessError.errorCode)})")
                                else:
                                    property_value = read_result.propertyValue
                                    data_type = get_datatype(object_identifier[0], property_identifier)
                                    if not data_type:
                                        continue

                                    # special case for array parts, others are managed by cast_out
                                    if issubclass(data_type, Array) and (property_array_index is not None):
                                        if property_array_index == 0:
                                            value = property_value.cast_out(Unsigned)
                                        else:
                                            value = property_value.cast_out(data_type.subtype)
                                    else:
                                        value = property_value.cast_out(data_type)

                                    if point_tag in bacnet_tag_dict.keys():
                                        point_name = bacnet_tag_dict[point_tag]
                                        result_dict[point_name] = value
                    else:  # Device point does not respond
                        raise Exception(f"No Response({str(iocb.ioError) if iocb.ioError else ''}-{iocb.ioID % 256})")
            except Exception as e:
                logging.error(f"bacnet({self}) read fail({read_key} [{list(bacnet_tag_dict.values())}] {e.__str__()})")
        return result_dict

    def read_single_value(self, read_key: str, bacnet_point_list: list, process: str) -> dict:
        result_dict = {}
        with self.lock_read_write_handler:
            try:
                pdu_destination = self.get_bacnet_dest_address(read_key)
                if pdu_destination:
                    point = bacnet_point_list[0]
                    point_type = point.get_point_type
                    point_address = point.get_point_address
                    point_property = point.get_point_property
                    point_name = point.get_point_name

                    bacnet_prop_list = list()
                    bacnet_prop_list.append(PropertyReference(propertyIdentifier=point_property, ))

                    request = ReadPropertyRequest(
                        objectIdentifier=(point_type, point_address),
                        propertyIdentifier=point_property, )
                    request.pduDestination = pdu_destination

                    iocb = IOCB(request)
                    self.request_io(iocb)
                    iocb.wait()

                    if iocb.ioResponse:
                        apdu = iocb.ioResponse

                        if not isinstance(apdu, ReadPropertyACK):
                            return result_dict

                        property_identifier = apdu.propertyIdentifier
                        object_identifier = apdu.objectIdentifier
                        property_array_index = apdu.propertyArrayIndex

                        property_value = apdu.propertyValue

                        data_type = get_datatype(object_identifier[0], property_identifier)
                        if data_type:
                            # special case for array parts, others are managed by cast_out
                            if issubclass(data_type, Array) and (property_array_index is not None):
                                if property_array_index == 0:
                                    value = property_value.cast_out(Unsigned)
                                else:
                                    value = property_value.cast_out(data_type.subtype)
                            else:
                                value = property_value.cast_out(data_type)

                            result_dict[point_name] = value

                    else:
                        raise Exception(f"No Response({str(iocb.ioError) if iocb.ioError else ''}-{iocb.ioID % 256})")
            except Exception as e:
                logging.error(f"bacnet({self}) read fail({read_key} [{bacnet_point_list[0].get_point_name}] {e.__str__()})")
        return result_dict

    def _convert_bacnet_value(self, bacnet_type: str, bacnet_value):
        format_value = None
        try:
            # get the datatype
            data_type = get_datatype(bacnet_type, 'presentValue')
            if bacnet_value == 'null':
                format_value = Null()
            elif issubclass(data_type, Atomic):
                if data_type is Integer:
                    format_value = int(bacnet_value)
                elif data_type is Real:
                    format_value = float(bacnet_value)
                elif data_type is Unsigned:
                    format_value = int(bacnet_value)
                format_value = data_type(format_value)
        except Exception as e:
            logging.error(f"bacnet({self}) convert value fail({e.__str__()})")
        return format_value

    # write value
    def write_single_value(self, bacnet_point, bacnet_value):
        with self.lock_read_write_handler:
            try:
                point_type = bacnet_point.get_point_type
                point_address = bacnet_point.get_point_address
                point_property = bacnet_point.get_point_property
                read_key = bacnet_point.get_point_device_address
                bacnet_value = self._convert_bacnet_value(point_type, bacnet_value)
                if bacnet_value is not None:
                    pdu_destination = self.get_bacnet_dest_address(read_key)
                    if pdu_destination:
                        request = WritePropertyRequest(
                            objectIdentifier=(point_type, point_address),
                            propertyIdentifier=point_property,
                        )
                        request.pduDestination = pdu_destination
                        request.propertyValue = Any()
                        request.propertyValue.cast_in(bacnet_value)
                        iocb = IOCB(request)
                        self.request_io(iocb)

                        iocb.wait()

                        if iocb.ioResponse:
                            apdu = iocb.ioResponse
                            if isinstance(apdu, SimpleAckPDU):
                                return True
            except Exception as e:
                logging.error(f"bacnet({self}) write fail([{bacnet_point.get_point_name}] {e.__str__()})")
        return False

    def add_route_by_device(self, router_address: str, device_address: str):
        if len(router_address) > 0 and len(device_address) > 0:
            if device_address.find(':') > 0:
                self.add_router(router_address, int(str(device_address.split(':')[0])))

    # Add network routing for access across network segments(6:2)
    def add_router(self, bacnet_address: str, network: int):
        try:
            if bacnet_address not in self.address_network_dict.keys():
                self.address_network_dict[bacnet_address] = []

            if network not in self.address_network_dict[bacnet_address]:
                self.address_network_dict[bacnet_address].append(network)
                # rtn 192.168.1.184:47808 6
                self.nsap.update_router_references(None, Address(bacnet_address), self.address_network_dict[bacnet_address])
        except Exception as e:
            logging.error(f"bacnet({self}) add router fail({e.__str__()})")


bacpypes_debugging(BacnetApplication)


# Bacnet read/write class
class BacnetReadWriteApplication(BIPSimpleApplication):

    def __init__(self, local_device, local_address: str, parent: Any = None):
        self.bacnet_device_address_dict = {}
        self.lock_read_write_handler = Lock()  # read/write lock
        self.bacnet_init_status = False
        self.bacnet_exception = None
        self.bacnet_local_address = local_address
        self.bacnet_support_property = ['analogInput', 'analogOutput', 'analogValue', 'binaryInput', 'binaryOutput', 'binaryValue', 'multiStateInput', 'multiStateOutput', 'multiStateValue']

        self.bacnet_cmd_interval = 0.3
        self.bacnet_multi_read = 20
        self.bacnet_timeout = 5000
        self.address_network_dict = {}
        self.parent = parent
        self.next_invoke_id = 1

        #
        try:
            BIPSimpleApplication.__init__(self, local_device, local_address)
            self.bacnet_init_status = True
        except Exception as e:
            self.bacnet_exception = e

    def __del__(self):
        self.exit()

    def __str__(self):
        return f"{self.bacnet_local_address}"

    def exit(self):
        pass

    def get_next_invoke_id(self, addr):
        """Called to get an unused invoke ID."""
        self.next_invoke_id = (self.next_invoke_id + 1) % 256
        return self.next_invoke_id

    def find_reason(self, apdu) -> str:
        try:
            if apdu == TimeoutError:
                return "Timeout"
            elif apdu == RuntimeError:
                return f"RuntimeError({apdu})"
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

    def confirmation(self, apdu):
        self.parent.set_call_result('debug_log', content=f"bacnet({self}) confir invoke({apdu.apduInvokeID})")
        BIPSimpleApplication.confirmation(self, apdu)

    def _get_bacnet_max_read_count_by_apdu_length(self, max_apdu_length: int) -> int:
        max_read_count = int((max_apdu_length - 57) / 9)
        if max_apdu_length <= 0:
            max_read_count = 1
        return max_read_count

    def get_bacnet_max_read_count(self, address_key: str, bacnet_multi_read: int) -> int:
        max_read_count = bacnet_multi_read
        if len(address_key) > 0:
            if address_key in self.bacnet_device_address_dict.keys():
                return self._get_bacnet_max_read_count_by_apdu_length(self.bacnet_device_address_dict[address_key].maxAPDULengthAccepted)
        return max_read_count

    def get_bacnet_dest_address(self, address_key: str):
        if address_key in self.bacnet_device_address_dict.keys():
            return self.bacnet_device_address_dict[address_key].pduSource
        address = address_key.split('/')
        if len(address) == 3:
            self.add_route_by_device(str(address[2]), address_key)
            return Address(str(address[0]))

        return Address(str(address[0]))

    def _read_values(self, bacnet_point_dict: dict, bacnet_cmd_interval: float = 0.3, bacnet_multi_read: int = 20) -> dict:
        result_dict = {}
        self.bacnet_cmd_interval = bacnet_cmd_interval
        self.bacnet_multi_read = bacnet_multi_read

        current = 0
        for read_key, points in bacnet_point_dict.items():
            result_dict.update(self._rebuild_bacnet_point_list(read_key, points, current, len(bacnet_point_dict)))
            time.sleep(self.bacnet_cmd_interval)
            current = current + 1
        return result_dict

    def _chunk_list(self, values: list, number: int):
        for i in range(0, len(values), number):
            yield values[i:i + number]

    def rebuild_bacnet_group(self, bacnet_read_multi_list: list, group_size: int) -> list:
        if len(bacnet_read_multi_list) > 0:
            bacnet_read_multi_list_group = []
            list_access = self._chunk_list(bacnet_read_multi_list, group_size)

            for access in list_access:
                bacnet_read_multi_list_group.append(access)

            return bacnet_read_multi_list_group
        return bacnet_read_multi_list

    def _rebuild_bacnet_point_list(self, read_key: str, bacnet_point_list: list, current: int, total: int) -> dict:
        result_dict = {}
        try:
            max_read_count = self.get_bacnet_max_read_count(read_key, self.bacnet_multi_read)

            # If the maximum number of reads is less than the length, regrouping is required
            if max_read_count < len(bacnet_point_list):
                bacnet_read_multi_list_group = self.rebuild_bacnet_group(bacnet_point_list, max_read_count)
                for index, _bacnet_read_multi_list in enumerate(bacnet_read_multi_list_group):
                    process = f"{current+1}/{total}-{index+1}/{len(bacnet_read_multi_list_group)}"
                    # Here according to the specified length to re-categorize and adjust the number of reads
                    if len(_bacnet_read_multi_list) == 1 and max_read_count == 1:  # Single point reading
                        result_dict.update(self.read_single_value(read_key, _bacnet_read_multi_list, process))
                    else:  # Batch read
                        result_dict.update(self.read_multi_value(read_key, _bacnet_read_multi_list, process))
                    time.sleep(self.bacnet_cmd_interval)
            else:
                # Here to reclassify and adjust the number of reads according to the specified length
                process = f"{current+1}/{total}-1/1"
                if len(bacnet_point_list) == 1 and max_read_count == 1:  # Single point reading
                    result_dict.update(self.read_single_value(read_key, bacnet_point_list, process))
                else:  # Batch read
                    result_dict.update(self.read_multi_value(read_key, bacnet_point_list, process))
        except Exception as e:
            logging.error(f"bacnet({self}) rebuild point fail({e.__str__()})")
        return result_dict

    @func_set_timeout(10)
    def make_request_iocb(self, request, process: str = ''):
        start = datetime.now()
        bacnet_apdu_iocb = IOCB(request)
        bacnet_apdu_iocb.set_timeout(self.bacnet_timeout)
        request.apduInvokeID = self.get_next_invoke_id(request.pduDestination)
        process = f"({process})" if process != '' else ''
        self.parent.set_call_result('debug_log', content=f"bacnet({self}) invoke({request.apduInvokeID}) send{process} address({request.pduDestination})")

        deferred(self.request_io, bacnet_apdu_iocb)
        bacnet_apdu_iocb.wait()

        if bacnet_apdu_iocb.ioError:
            raise Exception(f"{request.pduDestination}-{request.apduInvokeID} ({self.find_reason(bacnet_apdu_iocb.ioError)})")
        else:
            self.parent.set_call_result('debug_log', content=f"bacnet({self}) invoke({request.apduInvokeID}) cost({(datetime.now() - start).total_seconds()}s) ack")
        return bacnet_apdu_iocb

    # readKey:address_type
    def read_multi_value(self, read_key: str, bacnet_point_list: list, process: str) -> dict:
        result_dict = {}
        with self.lock_read_write_handler:
            try:
                pdu_destination = self.get_bacnet_dest_address(read_key)
                if pdu_destination:  # Receive device target address
                    bacnet_read_multi_list = []
                    bacnet_tag_dict = {}  # type_address_property: name
                    for point in bacnet_point_list:
                        point_type = point.get_point_type
                        point_name = point.get_point_name
                        if point_type not in self.bacnet_support_property:
                            logging.error(f'bacnet({self}) read fail({read_key} [{point_name}] Invalid Point Type: {point_type})')
                            continue
                        point_address = point.get_point_address
                        point_property = point.get_point_property

                        bacnet_prop_list = list()
                        bacnet_prop_list.append(PropertyReference(propertyIdentifier=point_property, ))

                        # build a read access specification
                        bacnet_read_access = ReadAccessSpecification(
                            objectIdentifier=(point_type, point_address),
                            listOfPropertyReferences=bacnet_prop_list,
                        )
                        bacnet_read_multi_list.append(bacnet_read_access)
                        bacnet_tag_dict['%s_%s_%s' % (point_type, str(point_address), point_property)] = point_name

                    # Create bulk read requests
                    request = ReadPropertyMultipleRequest(
                        listOfReadAccessSpecs=bacnet_read_multi_list,
                    )
                    request.pduDestination = pdu_destination
                    try:
                        result = self.make_request_iocb(request, process).ioResponse
                        if not isinstance(result, ReadPropertyMultipleACK):
                            raise Exception(f"{read_key} Ack: {result}")

                        self.parent.set_call_result('debug_log', content=f"bacnet({self}) read ({read_key}) success points({len(bacnet_tag_dict)}/{len(result.listOfReadAccessResults)}))")

                        for result in result.listOfReadAccessResults:
                            # ('analogInput', 17)
                            object_identifier = result.objectIdentifier

                            # Traverse the property value of each object
                            for element in result.listOfResults:
                                property_identifier = element.propertyIdentifier
                                property_array_index = element.propertyArrayIndex
                                read_result = element.readResult

                                point_tag = f'{str(object_identifier[0])}_{str(object_identifier[1])}_{property_identifier}'
                                point_name = bacnet_tag_dict.get(point_tag, '')

                                # Determine whether the attribute value is wrong
                                if read_result.propertyAccessError is not None:
                                    logging.error(f"bacnet({self}) read fail({read_key} [{point_name}] {str(read_result.propertyAccessError.errorCode)})")
                                else:
                                    property_value = read_result.propertyValue
                                    data_type = get_datatype(object_identifier[0], property_identifier)
                                    if not data_type:
                                        continue

                                    # special case for array parts, others are managed by cast_out
                                    if issubclass(data_type, Array) and (property_array_index is not None):
                                        if property_array_index == 0:
                                            value = property_value.cast_out(Unsigned)
                                        else:
                                            value = property_value.cast_out(data_type.subtype)
                                    else:
                                        value = property_value.cast_out(data_type)

                                    if point_name != '':
                                        result_dict[point_name] = value
                    except FunctionTimedOut as e:
                        raise Exception(f"{read_key} {process} wait timeout")
                    except Exception as e:
                        raise Exception(f"{read_key} {process} {e.__str__()}")
            except Exception as e:
                logging.error(f'bacnet({self}) read fail({e.__str__()})')
        return result_dict

    def read_single_value(self, read_key: str, bacnet_point_list: list, process: str) -> dict:
        result_dict = {}
        with self.lock_read_write_handler:
            try:
                pdu_destination = self.get_bacnet_dest_address(read_key)
                if pdu_destination:
                    point = bacnet_point_list[0]
                    point_type = point.get_point_type
                    point_address = point.get_point_address
                    point_property = point.get_point_property
                    point_name = point.get_point_name

                    bacnet_prop_list = list()
                    bacnet_prop_list.append(PropertyReference(propertyIdentifier=point_property, ))

                    request = ReadPropertyRequest(
                        objectIdentifier=(point_type, point_address),
                        propertyIdentifier=point_property, )
                    request.pduDestination = pdu_destination

                    try:
                        result = self.make_request_iocb(request, process).ioResponse

                        if not isinstance(result, ReadPropertyACK):
                            raise Exception(f"{read_key} [{point_name}] Ack: {result}")

                        property_identifier = result.propertyIdentifier
                        object_identifier = result.objectIdentifier
                        property_array_index = result.propertyArrayIndex

                        property_value = result.propertyValue
                        self.parent.set_call_result('debug_log', content=f"bacnet({self}) read ({read_key}) success points: 1-[{point_name}] response: {property_value})")
                        data_type = get_datatype(object_identifier[0], property_identifier)
                        if data_type:
                            # special case for array parts, others are managed by cast_out
                            if issubclass(data_type, Array) and (property_array_index is not None):
                                if property_array_index == 0:
                                    value = property_value.cast_out(Unsigned)
                                else:
                                    value = property_value.cast_out(data_type.subtype)
                            else:
                                value = property_value.cast_out(data_type)

                            result_dict[point_name] = value
                    except Exception as e:
                        raise Exception(f"{read_key} {process} {e.__str__()}")
            except Exception as e:
                logging.error(f'bacnet({self}) read fail({e.__str__()})')
        return result_dict

    def _convert_bacnet_value(self, bacnet_type: str, bacnet_value):
        format_value = None
        try:
            # get the datatype
            data_type = get_datatype(bacnet_type, 'presentValue')
            if bacnet_value == 'null':
                format_value = Null()
            elif issubclass(data_type, Atomic):
                if data_type is Integer:
                    format_value = int(bacnet_value)
                elif data_type is Real:
                    format_value = float(bacnet_value)
                elif data_type is Unsigned:
                    format_value = int(bacnet_value)
                format_value = data_type(format_value)
        except Exception as e:
            logging.error(f"bacnet({self}) convert value fail({e.__str__()})")
        return format_value

    # write value
    def write_single_value(self, bacnet_point, bacnet_value):
        with self.lock_read_write_handler:
            try:
                point_type = bacnet_point.get_point_type
                point_address = bacnet_point.get_point_address
                point_property = bacnet_point.get_point_property
                read_key = bacnet_point.get_point_device_address
                point_name = bacnet_point.get_point_name
                if point_type not in self.bacnet_support_property:
                    raise Exception(f'({read_key} [{point_name}] Invalid Point Type: {point_type})')

                bacnet_value = self._convert_bacnet_value(point_type, bacnet_value)
                if bacnet_value is not None:
                    pdu_destination = self.get_bacnet_dest_address(read_key)
                    if pdu_destination:
                        request = WritePropertyRequest(
                            objectIdentifier=(point_type, point_address),
                            propertyIdentifier=point_property,
                        )
                        request.pduDestination = pdu_destination
                        request.propertyValue = Any()
                        request.propertyValue.cast_in(bacnet_value)
                        try:
                            result = self.make_request_iocb(request).ioResponse
                            if not isinstance(result, SimpleAckPDU):
                                raise Exception(f"{read_key} [{point_name}] Ack: {result}")
                            self.parent.set_call_result('debug_log', content=f"bacnet({self}) write ({read_key}) success points: [{point_name}] {bacnet_value})")
                            return True
                        except Exception as e:
                            raise Exception(f"{read_key} [{point_name}] {e.__str__()}")
            except Exception as e:
                logging.error(f'bacnet({self}) write fail({e.__str__()})')
        return False

    def add_route_by_device(self, router_address: str, device_address: str):
        if len(router_address) > 0 and len(device_address) > 0:
            if device_address.find(':') > 0:
                self.add_router(router_address, int(str(device_address.split(':')[0])))

    # Add network routing for access across network segments(6:2)
    def add_router(self, bacnet_address: str, network: int):
        try:
            if bacnet_address not in self.address_network_dict.keys():
                self.address_network_dict[bacnet_address] = []

            if network not in self.address_network_dict[bacnet_address]:
                self.address_network_dict[bacnet_address].append(network)
                # rtn 192.168.1.184:47808 6
                self.nsap.update_router_references(None, Address(bacnet_address), self.address_network_dict[bacnet_address])
        except Exception as e:
            logging.error(f"bacnet({self}) add router fail({e.__str__()})")


bacpypes_debugging(BacnetReadWriteApplication)


# scan point
class BacnetScanApplication(BIPSimpleApplication):

    def __init__(self, local_device, local_address: str, parent: Any = None):
        self.bacnet_init_status = False
        self.bacnet_exception = None
        self.parent = parent
        self.expect_confirmation = True
        self.bacnet_timeout = 5000
        self.bacnet_response = False

        self.bacnet_apdu_iocb = None
        try:
            BIPSimpleApplication.__init__(self, local_device, local_address)
            self.bacnet_init_status = True
        except Exception as e:
            self.bacnet_exception = e

    def __del__(self):
        stop()

    def __str__(self):
        return f"{self.localAddress}"

    def confirmation(self, apdu):
        BIPSimpleApplication.confirmation(self, apdu)
        if self.bacnet_apdu_iocb and self.bacnet_apdu_iocb.ioResponse == apdu:
            self.bacnet_response = True
            stop()

    def request_timeout(self):
        if self.bacnet_response is False:
            stop()

    def make_request_iocb(self, request, process: str = ''):
        self.bacnet_response = False
        self.bacnet_apdu_iocb = IOCB(request)
        self.timer.run(self.bacnet_timeout, self.request_timeout)
        deferred(self.request_io, self.bacnet_apdu_iocb)
        run(spin=0.1)
        self.timer.cancel()
        return self.bacnet_apdu_iocb


bacpypes_debugging(BacnetScanApplication)


# who is
class BacnetWhoIsIAmApplication(BIPSimpleApplication):

    def __init__(self, local_device, local_address: str, parent: Any = None):
        self.bacnet_init_status = False
        self.bacnet_exception = None
        # keep track of requests to line up responses
        self._request = None
        self.bacnet_device_address_dict = {}
        self.date_response = datetime.now()
        self.parent = parent

        try:
            BIPSimpleApplication.__init__(self, local_device, local_address)
            self.bacnet_init_status = True
        except Exception as e:
            self.bacnet_exception = e

    def __str__(self):
        return f"{self.localAddress}"

    def request(self, apdu):
        # save a copy of the request
        self._request = apdu

        # forward it along
        BIPSimpleApplication.request(self, apdu)

    def confirmation(self, apdu):
        # forward it along
        BIPSimpleApplication.confirmation(self, apdu)

    def indication(self, apdu):
        if (isinstance(self._request, WhoIsRequest)) and (isinstance(apdu, IAmRequest)):
            device_type, device_instance = apdu.iAmDeviceIdentifier
            if device_type != 'device':
                raise DecodingError("invalid object type")

            if (self._request.deviceInstanceRangeLowLimit is not None) and \
                    (device_instance < self._request.deviceInstanceRangeLowLimit):
                pass
            elif (self._request.deviceInstanceRangeHighLimit is not None) and \
                    (device_instance > self._request.deviceInstanceRangeHighLimit):
                pass
            else:
                self.date_response = datetime.now()

                read_key = '%s/%u' % (str(apdu.pduSource), int(apdu.iAmDeviceIdentifier[1]))
                if apdu.pduSource.addrType == Address.remoteStationAddr:
                    read_key = f"{read_key}/{self.nsap.router_info_cache.get_router_info(None, apdu.pduSource.addrNet).address}"

                if read_key not in self.bacnet_device_address_dict.keys():
                    self.parent.set_call_result('debug_log', content=f"bacnet({self}) receive device {len(self.bacnet_device_address_dict)}({read_key})")
                    
                self.bacnet_device_address_dict[read_key] = apdu

        # forward it along
        BIPSimpleApplication.indication(self, apdu)

    # get if timeout
    def get_time_out(self, time_out: int = 5) -> bool:
        if (datetime.now() - self.date_response).total_seconds() >= time_out:
            return True
        return False

    # search Bacnet device
    def discover_bacnet_device(self):
        broad_address = GlobalBroadcast()
        BIPSimpleApplication.who_is(self, None, None, broad_address)
        self.date_response = datetime.now()

    # get Bacnet device list
    def get_bacnet_device_list(self) -> list:
        bacnet_device_list = []
        for read_key in self.bacnet_device_address_dict.keys():
            bacnet_device_list.append(read_key)
            bacnet_device_list.sort()
        return bacnet_device_list


bacpypes_debugging(BacnetWhoIsIAmApplication)


# Bacnet Driver
class BacnetDriver(BaseDriver):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        super().__init__(dict_config, dict_point)

        ##########
        self.bacnet_application = None
        self.bacnet_application_runing = False
        self.bacnet_device = None
        self.bacnet_multi_read = 20  # bacnet Number of batches read
        self.bacnet_cmd_interval = 0.3  # bacnet cmd interval
        self.bacnet_time_out = 5  # timeout
        self.enable = True
        self.lock_read_write_handler = Lock()  # lock
        self.bacnet_busy = False
        self.bacnet_readwrite_application = None

        # server
        self.bacnet_server_ip = ''  # bacnet server ip(Bind network card)
        self.bacnet_server_identifier = '555'  # bacnet server identifier
        self.bacnet_server_name = 'BacnetDriver'  # bacnet server name
        self.bacnet_server_max_apdu = 1024  # bacnet server max apdu
        self.bacnet_server_segmentation = 'segmentedBoth'  # bacnet server segmentation
        self.bacnet_server_vendor_identifier = 15  # bacnet server vendor
        self.bacnet_server_apdu_timeout = 5000  # bacnet server timeout
        self.bacnet_server_apdu_retties = 0  # bacnet server apdu retries
        self.bacnet_support_property = ['analogInput', 'analogOutput', 'analogValue', 'binaryInput', 'binaryOutput', 'binaryValue', 'multiStateInput', 'multiStateOutput', 'multiStateValue']

        ##########

        self.bacnet_device_list = []
        self.dict_bacnet_point = {}

        self.configure()

    # exit
    def __del__(self):
        self.exit()

    def __str__(self):
        return f"{self.bacnet_server_ip}"

    def exit(self):
        self.close()

    # close
    def close(self):
        self.bacnet_application_runing = False
        stop()

        if self.bacnet_application:
            if hasattr(self.bacnet_application, 'mux'):
                self.set_call_result('debug_log', content=f"bacnet({self}) close app: {self.bacnet_application}")
                self.bacnet_application.close_socket()
            del self.bacnet_application

        if self.bacnet_device:
            del self.bacnet_device

        self.bacnet_application = None
        self.bacnet_device = None

        self.bacnet_readwrite_application = self._release_bacnet_application_v1(self.bacnet_readwrite_application)

    # get local bacnet ip (192.168.1.0/24)
    def _get_local_bacnet_ip(self, ip: str, net: str):
        ip_start = ip_address(str(ip_network(ip, False)).split('/')[0])
        ip_end = ip_network(ip, False).broadcast_address

        addrs = net_if_addrs().items()
        for k, v in addrs:
            for item in v:
                if item[0] == 2:
                    item_ip = item[1]
                    if ':' not in item_ip:
                        item_ip = ip_address(item_ip)
                        if ip_start <= item_ip < ip_end:
                            return '%s/%s' % (item_ip, net)
        raise Exception(f'bacnet bind ip fail({ip})')

    # change to local ip
    def _change_bacnet_local_ip(self, bacnet_ip):
        if len(bacnet_ip) > 0:
            address_list = bacnet_ip.split(':')
            if len(address_list) >= 2:  # IP:Port
                [ip, port] = address_list
                ip_list = ip.split('/')
                if len(ip_list) >= 2:
                    return '%s:%s' % (self._get_local_bacnet_ip(ip, ip_list[1]), port)
            else:  # IP no port
                ip = address_list[0]
                ip_list = ip.split('/')
                if len(ip_list) >= 2:
                    return '%s' % self._get_local_bacnet_ip(ip, ip_list[1])
        return bacnet_ip

    # Parse configuration
    def configure(self):
        # config
        self.bacnet_server_ip = self._change_bacnet_local_ip(str(self.dict_config.get("address", "")))  # bacnet server ip(Bind network card)
        self.bacnet_server_identifier = int(str(self.dict_config.get("identifier", "555")))  # bacnet server identifier
        self.bacnet_server_name = str(self.dict_config.get("name", 'BacnetDriver'))  # bacnet server name
        self.bacnet_server_max_apdu = int(str(self.dict_config.get("max_apdu", "1024")))  # bacnet server max apdu
        self.bacnet_server_segmentation = str(self.dict_config.get("segmentation", 'segmentedBoth'))  # bacnet server segmentation
        self.bacnet_server_vendor_identifier = int(str(self.dict_config.get("vendor_identifier", "15")))  # bacnet server vendor
        self.bacnet_multi_read = int(str(self.dict_config.get("multi_read", "20")))
        self.bacnet_cmd_interval = float(str(self.dict_config.get("cmd_interval", "0.3")))
        self.bacnet_time_out = int(str(self.dict_config.get("timeout", "5")))  # timeout
        self.bacnet_short_connect = str(self.dict_config.get("short_connect", "false")).lower() == 'true'  # short_connect
        self.enable = str(self.dict_config.get("enabled", "true")).lower() == 'true'  # enable

        # csv
        for point_name, point in self.dict_point.items():
            self.dict_bacnet_point[point_name] = BacnetPoint(bool(str(point['point_writable'])), str(point['point_name']), str(point['point_device_address']), str(point['point_type']), str(point['point_property']), int(str(point['point_address'])), str(point['point_description']))

    # ping server
    def ping_target(self):
        return True

    def get_points(self, dict_point: dict = {}) -> dict:
        result_dict = {}
        if self.bacnet_busy is True:
            return result_dict
        else:
            self.bacnet_busy = True
            try:
                if len(dict_point) == 0:
                    result_dict = self._scrap_points()
                else:
                    result_dict = self._get_points(dict_point)
            finally:
                self.bacnet_busy = False
        return result_dict

    def _get_points(self, dict_point: dict) -> dict:
        result_dict = {}
        bacnet_point_dict = {}
        for point_name in dict_point.keys():
            if point_name in self.dict_bacnet_point.keys():
                read_key = self.dict_bacnet_point[point_name].get_point_device_address
                if read_key not in bacnet_point_dict.keys():
                    bacnet_point_dict[read_key] = []
                bacnet_point_dict[read_key].append(self.dict_bacnet_point[point_name])
        result_dict.update(self._read_bacnet_values_v1(bacnet_point_dict))
        return result_dict

    # scrap
    def _scrap_points(self) -> dict:
        result_dict = {}
        bacnet_point_dict = {}
        for point_name, point in self.dict_bacnet_point.items():
            read_key = point.get_point_device_address
            if read_key not in bacnet_point_dict.keys():
                bacnet_point_dict[read_key] = []
            bacnet_point_dict[read_key].append(point)

        result_dict.update(self._read_bacnet_values_v1(bacnet_point_dict, self.bacnet_short_connect))
        return result_dict

    # set
    def set_points(self, dict_point: dict) -> dict:
        set_result_dict = {}
        if self.bacnet_busy is True:
            return set_result_dict
        else:
            self.bacnet_busy = True
            try:
                for point_name, point_value in dict_point.items():
                    set_result = False
                    if point_name in self.dict_bacnet_point.keys():
                        bacnet_point = self.dict_bacnet_point[point_name]
                        set_result = self._write_bacnet_value_v1(bacnet_point, point_value, False)
                    set_result_dict[point_name] = set_result
            finally:
                self.bacnet_busy = False
        return set_result_dict

    # reset config
    def reset_config(self, dict_config: dict):
        super().reset_config(dict_config)
        self.configure()

    # reset point
    def reset_point(self, dict_point: dict):
        super().reset_point(dict_point)
        self.configure()

    # search
    def search_points(self) -> dict:
        search_point = {}
        bacnet_device_list = self._search_bacnet_device_list_v1()

        bacnet_device_count = len(bacnet_device_list)
        for bacnet_index in range(0, bacnet_device_count):
            bacnet_device = bacnet_device_list[bacnet_index]
            if len(bacnet_device) > 0:
                list_bacnet_info = str(bacnet_device).split('/')
                if len(list_bacnet_info) >= 2:
                    search_point.update(self._search_bacnet_device_point_dict_v1(str(list_bacnet_info[0]), str(list_bacnet_info[1]), ['objectName', 'description', 'presentValue'], '%d/%d' % (bacnet_index+1, bacnet_device_count)))
                    time.sleep(2)
        return search_point

    # bacnet application
    def _get_bacnet_application(self):
        try:
            if self.bacnet_application is None:
                if self.bacnet_device is None:
                    # create Bacnet device
                    self.bacnet_device = LocalDeviceObject(
                        objectName=self.bacnet_server_name,
                        objectIdentifier=('device', self.bacnet_server_identifier),
                        numberOfApduRetries=self.bacnet_server_apdu_retties,
                        apduTimeout=self.bacnet_server_apdu_timeout,
                        maxApduLengthAccepted=self.bacnet_server_max_apdu,
                        segmentationSupported=self.bacnet_server_segmentation,
                        vendorIdentifier=self.bacnet_server_vendor_identifier,
                    )

                if self.bacnet_device:
                    self.bacnet_application = BacnetApplication(self.bacnet_device, self.bacnet_server_ip, self)

                    if self.bacnet_application.bancet_create is False:
                        del self.bacnet_application
                        self.bacnet_application = None
                    else:
                        # Add additional bulk read and write services
                        self.bacnet_application.add_capability(ReadWritePropertyMultipleServices)

                        # build a bit string that knows about the bit names.
                        pss = ServicesSupported()
                        pss['whoIs'] = 1
                        pss['iAm'] = 1
                        pss['readProperty'] = 1
                        pss['readPropertyMultiple'] = 1
                        # set the property value to be just the bits
                        self.bacnet_application.protocolServicesSupported = pss.value

        except Exception as e:
            raise e
        return self.bacnet_application

    def _running_bacnet(self):
        BaseCommon.function_thread(self._running_bacnet_thread, False, f"bacnet({self})").start()

        # Wait for 1s to read data before delay start
        time.sleep(self.bacnet_cmd_interval)

    def _running_bacnet_thread(self):
        if self.bacnet_application_runing is False:
            if self._get_bacnet_application():
                self.bacnet_application_runing = True
                enable_sleeping()
                run(spin=0.1)

    # Search Bacnet devices
    def _search_bacnet_device_list(self) -> list:
        bacnet_device_list = []
        # Create a thread here to execute 10s and judge the timeout to end

        BaseCommon.function_thread(fn=self._handle_search_bacnet_device, daemon=True, name=f"bacnet({self})").start()

        # Here to determine whether the thread has timed out and the timeout ends
        exit_thread = False
        while exit_thread is False:
            time.sleep(1)
            bacnet_device_list = self._end_search_bacnet_device()
            if bacnet_device_list is not None:
                exit_thread = True
        return bacnet_device_list

    def _search_bacnet_device_point_dict(self, bacnet_device_address: str, bacnet_device_id: str, bacnet_property_list: list, bacnet_start_array_index: Optional[int] = None, bacnet_end_array_index: Optional[int] = None, bacnet_current: Optional[str] = None) -> dict:
        bacnet_point_dict = {}
        if self._get_bacnet_application():
            bacnet_id = ('device', int(bacnet_device_id))

            bacnet_address = Address(bacnet_device_address)

            deferred(self.bacnet_application.read_bacnet_object_count, bacnet_id, bacnet_address, bacnet_property_list, bacnet_start_array_index, bacnet_end_array_index, bacnet_current)

            self.bacnet_application_runing = True
            enable_sleeping()
            run(spin=0.1)

            bacnet_point_dict = self.bacnet_application.get_bacnet_point_dict()

            self.close()
        return bacnet_point_dict

    def _handle_search_bacnet_device(self):
        if self._get_bacnet_application():
            deferred(self.bacnet_application.discover_bacnet_device)

            self.bacnet_application_runing = True
            enable_sleeping()
            run(spin=0.1)

    def _end_search_bacnet_device(self):
        bacnet_device_list = None
        if self._get_bacnet_application():
            if self.bacnet_application.get_time_out(self.bacnet_time_out) is True:
                bacnet_device_list = self.bacnet_application.get_bacnet_device_list()
                self.bacnet_application.end_discover()
                self.close()
        return bacnet_device_list

    def _read_bacnet_values(self, bacnet_point_dict: dict) -> dict:
        result_dict = {}
        if self.bacnet_application_runing is False:
            self._running_bacnet()

        if self.bacnet_application_runing is True:
            result_dict = self.bacnet_application._read_values(bacnet_point_dict, self.bacnet_cmd_interval, self.bacnet_multi_read)
        return result_dict

    def _write_bacnet_value(self, bacnet_point, bacnet_value) -> bool:
        if self.bacnet_application_runing is False:
            self._running_bacnet()

        if self.bacnet_application_runing is True:
            return self.bacnet_application.write_single_value(bacnet_point, bacnet_value)
        return False

    # v1
    def _end_search_bacnet_device_v1(self, **kwargs):
        bacnet_application = kwargs.get('bacnet_application')
        while bacnet_application:
            if bacnet_application.get_time_out(self.bacnet_time_out) is True:
                self.bacnet_device_list = bacnet_application.get_bacnet_device_list()
                stop()
                break
            time.sleep(1)

    def _get_bacnet_application_v1(self, bacnet_app_class):
        # create Bacnet device
        bacnet_device = LocalDeviceObject(
            objectName=self.bacnet_server_name,
            objectIdentifier=('device', self.bacnet_server_identifier),
            numberOfApduRetries=self.bacnet_server_apdu_retties,
            apduTimeout=self.bacnet_server_apdu_timeout,
            maxApduLengthAccepted=self.bacnet_server_max_apdu,
            segmentationSupported=self.bacnet_server_segmentation,
            vendorIdentifier=self.bacnet_server_vendor_identifier,
        )

        if bacnet_device:
            bacnet_application = bacnet_app_class(bacnet_device, self.bacnet_server_ip, self)
            self.set_call_result('debug_log', content=f"bacnet({self}) get app: {bacnet_application}")
            if bacnet_application is not None:
                if bacnet_application.bacnet_init_status is False:
                    logging.error(f'bacnet({self}) get application({self.bacnet_server_ip}) fail {bacnet_application.bacnet_exception}')
                    bacnet_application = self._release_bacnet_application_v1(bacnet_application)
                else:
                    BaseCommon.function_thread(self.control_status, False, f"bacnet({self})").start()
                    time.sleep(1)
                    return bacnet_application
        return None

    def _release_bacnet_application_v1(self, bacnet_application):
        try:
            if bacnet_application:
                self.control_status(False)
                time.sleep(1)
                if hasattr(bacnet_application, 'mux'):
                    self.set_call_result('debug_log', content=f"bacnet({self}) close app: {bacnet_application}")
                    bacnet_application.close_socket()
        except Exception as e:
            logging.error(f'bacnet({self}) release {self.bacnet_server_ip} fail {e}')
        finally:
            if bacnet_application:
                del bacnet_application
            bacnet_application = None
        return None

    def _search_bacnet_device_list_v1(self) -> list:
        self.bacnet_device_list = []
        bacnet_whois_application = None
        try:
            bacnet_whois_application = self._get_bacnet_application_v1(BacnetWhoIsIAmApplication)
            if bacnet_whois_application is not None:

                BaseCommon.function_thread(fn=self._end_search_bacnet_device_v1, daemon=True, bacnet_application=bacnet_whois_application, name=f"bacnet({self})").start()

                bacnet_whois_application.discover_bacnet_device()

                run(spin=0.1)
            return self.bacnet_device_list
        finally:
            bacnet_whois_application = self._release_bacnet_application_v1(bacnet_whois_application)

    def _read_bacnet_obj_v1(self, bacnet_scan_application, bacnet_address, bacnet_id, obj_type, obj_inst, prop_id, index=None):
        request = ReadPropertyRequest(objectIdentifier=(obj_type, obj_inst), propertyIdentifier=prop_id, propertyArrayIndex=index)
        request.pduDestination = bacnet_address

        result = bacnet_scan_application.make_request_iocb(request).ioResponse
        if isinstance(result, ReadPropertyACK):
            # find the datatype
            datatype = get_datatype(obj_type, prop_id)
            if issubclass(datatype, Array) and (result.propertyArrayIndex is not None):
                if result.propertyArrayIndex == 0:
                    value = result.propertyValue.cast_out(Unsigned)
                else:
                    value = result.propertyValue.cast_out(datatype.subtype)
            else:
                value = result.propertyValue.cast_out(datatype)
            return value
        return None

    def _read_bacnet_prop_v1(self, bacnet_scan_application, address, bacnet_id, obj_type, obj_inst, array_index, bacnet_property_reference_list):
        bacnet_point_dict = {}
        bacnet_read_access_spec = ReadAccessSpecification(
            objectIdentifier=(obj_type, obj_inst),
            listOfPropertyReferences=bacnet_property_reference_list,
        )
        bacnet_read_access_spec_list = list()
        bacnet_read_access_spec_list.append(bacnet_read_access_spec)

        bacnet_request = ReadPropertyMultipleRequest(
            listOfReadAccessSpecs=bacnet_read_access_spec_list,
        )
        bacnet_request.pduDestination = address

        bacnet_apdu = bacnet_scan_application.make_request_iocb(bacnet_request).ioResponse
        if isinstance(bacnet_apdu, ReadPropertyMultipleACK):
            for result in bacnet_apdu.listOfReadAccessResults:
                object_identifier = result.objectIdentifier
                bacnet_point_name = self._format_name_v1(str(address),
                                                         str(obj_inst),
                                                         str(object_identifier[0]), str(object_identifier[1]))
                property_dict = {}
                for element in result.listOfResults:
                    property_identifier = element.propertyIdentifier
                    property_array_index = element.propertyArrayIndex
                    read_result = element.readResult

                    if read_result.propertyAccessError is None:
                        property_name = str(property_identifier)
                        if property_name == 'description':
                            property_name = 'point_description'
                        property_value = read_result.propertyValue

                        bacnet_data_type = get_datatype(object_identifier[0], property_identifier)
                        if bacnet_data_type:
                            if issubclass(bacnet_data_type, Array) and (property_array_index is not None):
                                if property_array_index == 0:
                                    property_dict[property_name] = str(property_value.cast_out(Unsigned))
                                else:
                                    property_dict[property_name] = str(
                                        property_value.cast_out(bacnet_data_type.subtype))
                            else:
                                property_dict[property_name] = str(property_value.cast_out(bacnet_data_type))

                if str(object_identifier[0]) in self.bacnet_support_property:
                    bacnet_point_property = {'point_name': bacnet_point_name,
                                             'index': array_index, 'point_writable': 'True',
                                             'point_device_address': '%s/%s' % (str(address), str(bacnet_id)),
                                             'point_type': str(object_identifier[0]),
                                             'point_property': 'presentValue',
                                             'point_address': str(object_identifier[1]), 'point_description': ''}
                    bacnet_point_property.update(property_dict)
                    bacnet_point_dict[bacnet_point_name] = bacnet_point_property
        return bacnet_point_dict

    def _search_bacnet_device_point_dict_v1(self, bacnet_device_address: str, bacnet_device_id: str, bacnet_property_list: list, bacnet_current: Optional[str] = None) -> dict:
        bacnet_point_dict = {}
        bacnet_scan_application = None
        try:
            bacnet_scan_application = self._get_bacnet_application_v1(BacnetScanApplication)
            if bacnet_scan_application is not None:
                bacnet_id = int(bacnet_device_id)
                bacnet_address = Address(bacnet_device_address)

                # read count
                object_count = self._read_bacnet_obj_v1(bacnet_scan_application, bacnet_address, bacnet_id, "device", bacnet_id, "objectList", index=0)

                if object_count is not None:
                    bacnet_property_reference_list = []
                    for property_identifier in bacnet_property_list:
                        prop_reference = PropertyReference(
                            propertyIdentifier=property_identifier,
                        )
                        bacnet_property_reference_list.append(prop_reference)

                    for array_index in range(1, object_count + 1):

                        obj_result = self._read_bacnet_obj_v1(bacnet_scan_application, bacnet_address, bacnet_id, "device", bacnet_id, 'objectList', index=array_index)
                        if obj_result is not None:
                            obj_type, obj_index = obj_result
                            bacnet_point_dict.update(self._read_bacnet_prop_v1(bacnet_scan_application, bacnet_address, bacnet_id, obj_type, obj_index, array_index, bacnet_property_reference_list))
                            self.set_call_result('debug_log', content=f"bacnet({self}) read ({bacnet_current}) object: {array_index}/{object_count} address: {bacnet_device_address}/{bacnet_device_id}")
            return bacnet_point_dict
        finally:
            bacnet_scan_application = self._release_bacnet_application_v1(bacnet_scan_application)

    def _format_name_v1(self, device_address: str, device_id: str, type: str, address: str):
        return '%s_%s_%s_%s' % (device_address.replace('.', '_').replace(':', '_'), device_id, type, address)

    def _read_bacnet_values_v1(self, bacnet_point_dict: dict, auto_release=True) -> dict:
        result_dict = {}
        try:
            if self.bacnet_readwrite_application is None:
                self.bacnet_readwrite_application = self._get_bacnet_application_v1(BacnetReadWriteApplication)
            if self.bacnet_readwrite_application is not None:
                result_dict = self.bacnet_readwrite_application._read_values(bacnet_point_dict, self.bacnet_cmd_interval, self.bacnet_multi_read)
            return result_dict
        finally:
            if self.bacnet_readwrite_application is not None:
                if auto_release is True:
                    self.bacnet_readwrite_application = self._release_bacnet_application_v1(self.bacnet_readwrite_application)
                elif len(bacnet_point_dict) > 0 >= len(result_dict):
                    self.bacnet_readwrite_application = self._release_bacnet_application_v1(self.bacnet_readwrite_application)

    def _write_bacnet_value_v1(self, bacnet_point, bacnet_value, auto_release=True) -> bool:
        try:
            if self.bacnet_readwrite_application is None:
                self.bacnet_readwrite_application = self._get_bacnet_application_v1(BacnetReadWriteApplication)
            if self.bacnet_readwrite_application is not None:
                return self.bacnet_readwrite_application.write_single_value(bacnet_point, bacnet_value)
            return False
        finally:
            if auto_release is True:
                self.bacnet_readwrite_application = self._release_bacnet_application_v1(self.bacnet_readwrite_application)

    def control_status(self, status: bool = True):
        if status is True:
            enable_sleeping()
            run(spin=0.1)
        else:
            stop()
