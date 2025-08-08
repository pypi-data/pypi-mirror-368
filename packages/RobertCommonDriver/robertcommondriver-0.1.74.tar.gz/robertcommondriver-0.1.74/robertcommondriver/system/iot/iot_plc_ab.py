import time

from typing import List, Dict, Any, Union, Optional

from .base import IOTBaseCommon, IOTDriver

'''
https://blog.csdn.net/lishiming0308/article/details/85243041

Rockwell Allen-Bradley(AB)PLC
罗克韦尔CIP
AB PLC的数据通信类，使用CIP协议实现，适用1756，1769等型号，支持使用标签的形式进行读写操作，支持标量数据，一维数组，二维数组，三维数组等等。如果是局部变量，那么使用 Program:MainProgram.[变量名]

ABPLC的通讯采用小端模式。一般情况实现注册、请求、读写数据即可。不实现关闭请求、卸载注册在实际测试过程中也不会出现问题。在断开连接时不提交关闭请求和卸载注册指令。再重新连接plc执行注册、打开请求、读写数据还是一样可以成功的。
连接：
    客户端发送注册会话请求， PLC收到请求后，生成会话句柄并返回客户端
    客户端收到句柄后生成连接标识，通过开放数据连接(ForwardOpen)请求发送给PLC， OLC收到后发送O2T给客户端
    读取数据请求
    应答
'''


class AllenBradleyMessage(IOTBaseCommon.IOTNetMessage):
    """用于和 AllenBradley PLC 交互的消息协议类"""

    def get_head_length(self) -> int:
        """协议头数据长度，也即是第一次接收的数据长度"""
        return 24

    def get_content_length(self) -> int:
        """二次接收的数据长度"""
        if self.heads is not None:
            return IOTBaseCommon.DataTransform.unpack_bytes(self.heads[2:4], '<h')
        else:
            return 0

    def check_response(self) -> bool:
        """回复报文校验"""
        return True


# 初始化指令交互报文
class AllenBradleyConstant:
    CIP_READ_DATA = 0x4C    # CIP命令中的读取数据的服务
    CIP_WRITE_DATA = 0x4D   # CIP命令中的写数据的服务
    CIP_READ_WRITE_DATA = 0x4E
    CIP_READ_FRAGMENT = 0x52    # CIP命令中的读片段的数据服务
    CIP_WRITE_FRAGMENT = 0x53   # CIP命令中的写片段的数据服务
    CIP_READ_LIST = 0x55
    CIP_MULTIREAD_DATA = 0x1000  # CIP命令中的对数据读取服务
    CIP_TYPE_BOOL = 0xC1    # bool型数据，一个字节长度
    CIP_TYPE_BYTE = 0xC2    # byte型数据，一个字节长度
    CIP_TYPE_WORD = 0xC3    # 整型，两个字节长度
    CIP_TYPE_DWORD = 0xC4   # 长整型，四个字节长度
    CIP_TYPE_LINT = 0xC5
    CIP_TYPE_REAL = 0xCA    # 实数数据，四个字节长度
    CIP_TYPE_DOUBLE = 0xCB
    CIP_TYPE_STRUCT = 0xCC
    CIP_TYPE_STRING = 0xD0
    CIP_TYPE_BIT_ARRAY = 0xD3   # 二进制数据内容

    RegisteredCommand = bytearray([0x65, 0x00,                              # 注册请求
                                   0x04, 0x00,                              # 命令数据长度(单位字节)
                                   0x00, 0x00, 0x00, 0x00,                    # 会话句柄,初始值为0x00000000
                                   0x00, 0x00, 0x00, 0x00,                    # 状态，初始值为0x00000000（状态好）
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # 请求通信一方的说明
                                   0x00, 0x00, 0x00, 0x00,                    # 选项，默认为0x00000000
                                   0x01, 0x00,                              # 协议版本（0x0001）
                                   0x00, 0x00                               # 选项标记（0x0000
                                   ])


# 基础方法
class AllenBradleyTools:

    # 创建路径指令
    @staticmethod
    def parse_address(address: str, type: int):
        """
            0: address 1: path 2: type 3: type_code 8: value 9: result 10: msg
        """
        result = IOTBaseCommon.IOTNetResult()
        try:
            result.contents[0] = address
            result.contents[1] = address[0:1]
            result.contents[2] = type
            result.contents[3] = AllenBradleyTools.get_type_code(type)
            result.contents[4] = 1

            ms = bytearray(0)
            tag_names = address.split(".")

            for i, tag_name in enumerate(tag_names):
                index = ""
                index_first = tag_name.find("[")
                index_second = tag_name.find("]")
                if 0 < index_first < index_second:
                    index = tag_name[index_first + 1: index_second]
                    tag_name = tag_name[0: index_first]

                ms.append(0x91)  # 固定
                ms.append(len(tag_name))
                name = tag_name.encode(encoding='utf-8')
                ms.extend(name)
                if len(name) % 2 == 1:
                    ms.append(0x00)

                if index.strip() != "":
                    indexs = index.split(",")
                    for j in range(len(indexs)):
                        index = int(indexs[j])
                        if index < 256:
                            ms.append(0x28)
                            ms.append(index)
                        else:
                            ms.append(0x29)
                            ms.append(0x00)
                            ms.append(IOTBaseCommon.DataTransform.pack_value(index, '<i')[0])
                            ms.append(IOTBaseCommon.DataTransform.pack_value(index, '<i')[1])

            result.contents[1] = ms
            result.is_success = True
            return result
        except Exception as e:
            return IOTBaseCommon.IOTNetResult(msg=e.__str__())

    @staticmethod
    def get_type_code(type: int):
        type_code = AllenBradleyConstant.CIP_TYPE_WORD
        if type in [IOTBaseCommon.DataTransform.TypeFormat.BOOL.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_BOOL
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT8.value, IOTBaseCommon.DataTransform.TypeFormat.UINT8.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_BYTE
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.UINT16.value, IOTBaseCommon.DataTransform.TypeFormat.UINT16.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_WORD
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT32.value, IOTBaseCommon.DataTransform.TypeFormat.UINT32.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_DWORD
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT64.value, IOTBaseCommon.DataTransform.TypeFormat.UINT64.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_LINT
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.FLOAT.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_REAL
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.DOUBLE.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_DOUBLE
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.STRING.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_STRING
        elif type in [IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY.value]:
            type_code = AllenBradleyConstant.CIP_TYPE_BIT_ARRAY
        return type_code

    @staticmethod
    def build_request_path_command(address: str) -> bytearray:
        ms = bytearray(0)
        tag_names = address.split(".")

        for i, tag_name in enumerate(tag_names):
            index = ""
            index_first = tag_name.find("[")
            index_second = tag_name.find("]")
            if 0 < index_first < index_second:
                index = tag_name[index_first + 1: index_second]
                tag_name = tag_name[0: index_first]

            ms.append(0x91)  # 固定
            ms.append(len(tag_name))
            name = tag_name.encode(encoding='utf-8')
            ms.extend(name)
            if len(name) % 2 == 1:
                ms.append(0x00)

            if index.strip() != "":
                indexs = index.split(",")
                for j in range(len(indexs)):
                    index = int(indexs[j])
                    if index < 256:
                        ms.append(0x28)
                        ms.append(index)
                    else:
                        ms.append(0x29)
                        ms.append(0x00)
                        ms.append(IOTBaseCommon.DataTransform.pack_value(index, '<i')[0])
                        ms.append(IOTBaseCommon.DataTransform.pack_value(index, '<i')[1])
        return ms

    # 打包成可发送的数据指令
    @staticmethod
    def pack_request_header(command: int, session: int, command_specific_data: bytearray) -> bytes:
        """
        command_specific_data，打包成可发送的数据指令 -> bytes
        Prarameter
          command: ushort 实际的命令暗号
          session: uint 当前会话的id
          command_specific_data: byteArray CommandSpecificData命令
        """
        buffer = bytearray(len(command_specific_data) + 24)
        buffer[24: 24 + len(command_specific_data)] = command_specific_data
        buffer[0:2] = IOTBaseCommon.DataTransform.pack_value(command, '<H')  # 注册请求
        buffer[2:4] = IOTBaseCommon.DataTransform.pack_value(len(command_specific_data), '<H')  # 命令数据长度(单位字节)
        buffer[4:8] = IOTBaseCommon.DataTransform.pack_value(session, '<I')  # 会话句柄,初始值为0x00000000
        buffer[8: 12] = bytes.fromhex('00 00 00 00')    # 初始值为0x000000
        buffer[12: 20] = bytes.fromhex('00 00 00 00 00 00 00 00')  # 发送方描述
        buffer[20: 24] = bytes.fromhex('00 00 00 00')  # 选项
        return buffer

    # 打包生成一个请求读取数据的节点信息，CIP指令信息
    @staticmethod
    def pack_requset_read(request_path: bytearray, length: int) -> bytes:
        buffer = bytearray(4 + len(request_path))
        buffer[0] = AllenBradleyConstant.CIP_READ_DATA  # 读
        buffer[1] = len(request_path) // 2
        buffer[2: 2 + len(request_path)] = request_path
        buffer[2 + len(request_path)] = IOTBaseCommon.DataTransform.pack_value(length, '<i')[0]
        buffer[1 + 2 + len(request_path)] = IOTBaseCommon.DataTransform.pack_value(length, '<i')[1]
        return buffer

    # 打包生成一个请求读取数据片段的节点信息
    @staticmethod
    def pack_request_read_segment(address: str, start: int, length: int) -> bytes:
        buffer = bytearray(1024)
        offect = 0
        buffer[offect] = AllenBradleyConstant.CIP_READ_FRAGMENT
        offect += 1
        offect += 1

        request_path = AllenBradleyTools.build_request_path_command(address)
        buffer[offect:offect + len(request_path)] = request_path
        offect += len(request_path)

        buffer[1] = (offect - 2) // 2
        buffer[offect] = IOTBaseCommon.DataTransform.pack_value(length, '<i')[0]
        offect += 1
        buffer[offect] = IOTBaseCommon.DataTransform.pack_value(length, '<i')[1]
        offect += 1
        buffer[offect + 0] = IOTBaseCommon.DataTransform.pack_value(start, '<i')[0]
        buffer[offect + 1] = IOTBaseCommon.DataTransform.pack_value(start, '<i')[1]
        buffer[offect + 2] = IOTBaseCommon.DataTransform.pack_value(start, '<i')[2]
        buffer[offect + 3] = IOTBaseCommon.DataTransform.pack_value(start, '<i')[3]
        offect += 4

        return buffer[0:offect]

    # 据指定的数据和类型，生成对应的数据
    @staticmethod
    def pack_request_write(request_path: bytearray, type_code: int, value: bytes, length: int = 1) -> bytes:
        buffer = bytearray(6 + len(request_path) + len(value))
        buffer[0] = AllenBradleyConstant.CIP_WRITE_DATA  # 写
        buffer[1] = len(request_path) // 2
        buffer[2: 2 + len(request_path)] = request_path
        buffer[2 + len(request_path)] = IOTBaseCommon.DataTransform.pack_value(type_code, '<i')[0]
        buffer[3 + len(request_path)] = IOTBaseCommon.DataTransform.pack_value(type_code, '<i')[1]
        buffer[4 + len(request_path)] = IOTBaseCommon.DataTransform.pack_value(length, '<i')[0]
        buffer[5 + len(request_path)] = IOTBaseCommon.DataTransform.pack_value(length, '<i')[1]
        buffer[6 + len(request_path): 6 + len(request_path) + len(value)] = value
        return buffer

    # 将所有的cip指定进行打包操作
    @staticmethod
    def pack_command_service(slot: bytearray, cips: list) -> bytes:
        ms = bytearray(0)
        ms.append(0xB2)     # 连接的项数
        ms.append(0x00)
        ms.append(0x00)     # 后面数据包的长度，等全部生成后在赋值
        ms.append(0x00)

        ms.append(0x52)     # 服务
        ms.append(0x02)     # 请求路径大小
        ms.append(0x20)     # 请求路径
        ms.append(0x06)
        ms.append(0x24)
        ms.append(0x01)
        ms.append(0x0A)     # 超时时间
        ms.append(0xF0)
        ms.append(0x00)     # CIP指令长度
        ms.append(0x00)

        count = 0
        if len(cips) == 1:
            ms.extend(cips[0])
            count += len(cips[0])
        else:
            ms.append(0x0A)
            ms.append(0x02)
            ms.append(0x20)
            ms.append(0x02)
            ms.append(0x24)
            ms.append(0x01)
            count += 8

            ms.extend(IOTBaseCommon.DataTransform.pack_value(len(cips), '<H'))
            offect = 0x02 + 2 * len(cips)
            count += 2 * len(cips)

            for i in range(len(cips)):
                ms.extend(IOTBaseCommon.DataTransform.pack_value(offect, '<H'))
                offect = offect + len(cips[i])

            for i in range(len(cips)):
                ms.extend(cips[i])
                count += len(cips[i])

        ms.append((len(slot) + 1) // 2)
        ms.append(0x00)
        ms.extend(slot)
        if len(slot) % 2 == 1:
            ms.append(0x00)

        ms[12:14] = IOTBaseCommon.DataTransform.pack_value(count, '<H')
        ms[2:4] = IOTBaseCommon.DataTransform.pack_value(len(ms) - 4, '<H')
        return ms

    # 生成读取直接节点数据信息的内容
    @staticmethod
    def pack_command_specific_data(service: List[bytearray]) -> bytes:
        buffer = bytearray(0)
        buffer.append(0x00)
        buffer.append(0x00)
        buffer.append(0x00)
        buffer.append(0x00)
        buffer.append(0x01)  # 超时
        buffer.append(0x00)
        buffer.extend(IOTBaseCommon.DataTransform.pack_value(len(service), '<H'))
        for i in range(len(service)):
            buffer.extend(service[i])
        return buffer

    # 从PLC反馈的数据解析
    @staticmethod
    def extract_actual_data(response: bytearray, is_read: bool):
        data = bytearray()
        offset = 38
        has_more_data = False
        data_type = 0
        count = IOTBaseCommon.DataTransform.unpack_bytes(response[38:40], '<H')  # 剩余总字节长度，在剩余的字节里，有可能是一项数据，也有可能是多项
        if IOTBaseCommon.DataTransform.unpack_bytes(response[40:44], '<i') == 0x8A:  # 多项数据
            offset = 44
            data_count = IOTBaseCommon.DataTransform.unpack_bytes(response[offset:offset + 2], '<H')
            for i in range(data_count):
                offset_start = IOTBaseCommon.DataTransform.unpack_bytes(response[offset + 2 + i * 2: offset + 4 + i * 2], '<H')
                if i == data_count - 1:
                    offset_end = len(response)
                else:
                    offset_end = IOTBaseCommon.DataTransform.unpack_bytes(response[offset + 2 + i * 2: offset + 4 + i * 2], '<H')

                err = IOTBaseCommon.DataTransform.unpack_bytes(response[offset_start + 2: offset_start + 4], '<H')
                if err in [0x04, 0x05, 0x0A, 0x13, 0x1C, 0x1E, 0x26]:
                    return IOTBaseCommon.IOTNetResult(code=err, msg=AllenBradleyTools.get_status_description(err))
                elif err == 0x06:
                    if response[offset + 2] == 0xD2 or response[offset + 2] == 0xCC:
                        return IOTBaseCommon.IOTNetResult(code=err, msg=AllenBradleyTools.get_status_description(err))
                elif err == 0x00:
                    pass
                else:
                    return IOTBaseCommon.IOTNetResult(code=err, msg=AllenBradleyTools.get_status_description(err))

                if is_read is True:
                    for j in range(offset_start + 6, offset_end, 1):
                        data.append(response[j])
        else:   # 单项数据
            err = response[offset + 4]
            if err in [0x04, 0x05, 0x0A, 0x13, 0x1C, 0x1E, 0x26]:
                return IOTBaseCommon.IOTNetResult(code=err, msg=AllenBradleyTools.get_status_description(err))
            elif err == 0x06:
                has_more_data = True

            elif err == 0x00:
                if response[offset + 2] == 0xCD or response[offset + 2] == 0xD3:    # 写服务应答为0xD3
                    return IOTBaseCommon.IOTNetResult.create_success([data, data_type, has_more_data])
                if response[offset + 2] == 0xCC or response[offset + 2] == 0xD2:    # 0xD2为读取数据标签应答
                    for i in range(offset + 8, offset + 2 + count, 1):
                        data.append(response[i])
                    data_type = IOTBaseCommon.DataTransform.unpack_bytes(response[offset + 6:offset + 8], '<H')
                elif response[offset + 2] == 0xD5:
                    for i in range(offset + 6, offset + 2 + count, 1):
                        data.append(response[i])
            else:
                return IOTBaseCommon.IOTNetResult(code=err, msg=AllenBradleyTools.get_status_description(err))
        return IOTBaseCommon.IOTNetResult.create_success([data, data_type, has_more_data])

    @staticmethod
    def get_status_description(err):
        """获取错误信息的字符串描述文本"""
        if err == 0:
            return f"Communication is normal."
        elif err == 1:
            return f"The message header is not fins"
        elif err == 2:
            return f"Data length too long"
        elif err == 3:
            return f"This command does not support"
        elif err == 20:
            return f"Exceeding connection limit"
        elif err == 21:
            return f"The specified node is already in the connection"
        elif err == 22:
            return f"Attempt to connect to a protected network node that is not yet configured in the PLC"
        elif err == 23:
            return f"The current client's network node exceeds the normal range"
        elif err == 24:
            return f"The current client's network node is already in use"
        elif err == 25:
            return f"All network nodes are already in use"
        else:
            return f"Unknown Error"

    @staticmethod
    def get_session_status_description(status: int) -> str:
        """获取错误信息的字符串描述文本"""
        if status == 0x01:
            return f"The sender issued an invalid or unsupported encapsulation command."
        elif status == 0x02:
            return f"Insufficient memory resources in the receiver to handle the command. This is not an application error. Instead, it only results if the encapsulation layer cannot obtain memory resources that it need."
        elif status == 0x03:
            return f"Poorly formed or incorrect data in the data portion of the encapsulation message."
        elif status == 0x64:
            return f"An originator used an invalid session handle when sending an encapsulation message."
        elif status == 0x65:
            return f"The target received a message of invalid length."
        elif status == 0x69:
            return f"Unsupported encapsulation protocol revision."
        else:
            return f"Unknown"


class AllenBradleyClient(IOTBaseCommon.IOTNetworkDeviceClient):

    def __init__(self, host: str, port: int, slot: int = 0, timeout: int = 10):
        super().__init__(host, port, timeout)

        self.slot = slot  # 插槽
        self.cip_command = 0x6F  # 实际的命令暗号
        self.session_handle = 0  # 当前会话的id

    def get_net_msg(self):
        return AllenBradleyMessage()

    def pack_command_with_header(self, command: bytearray):
        return AllenBradleyTools.pack_request_header(self.cip_command, self.session_handle, command)

    def register_session_handle(self):
        """
            向PLC注册会话ID的报文(协议版本（0x0001) 选项标记（0x0000))
            65 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00
        """
        return AllenBradleyTools.pack_request_header(0x65, 0, bytearray([0x01, 0x00, 0x00, 0x00]))

    def unregister_session_handle(self):
        """
            获取卸载一个已注册的会话的报文
            66 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00
        """
        return AllenBradleyTools.pack_request_header(0x66, self.session_handle, bytearray(0))

    def check_response(self, response: bytes):
        try:
            status = IOTBaseCommon.DataTransform.convert_value(response[8:12], IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, IOTBaseCommon.DataTransform.TypeFormat.INT32, pos=0)
            if status == 0:
                return IOTBaseCommon.IOTNetResult.create_success()
            return IOTBaseCommon.IOTNetResult(msg=AllenBradleyTools.get_session_status_description(status))
        except Exception as ex:
            return IOTBaseCommon.IOTNetResult(msg=str(ex))

    def initialization_on_connect(self, socket):
        """在连接上PLC后，需要进行一步握手协议"""
        # 握手信号
        read = self.read_from_socket(socket, self.register_session_handle(), has_response=True, pack_unpack=False)
        if read.is_success is False:
            return read

        # 检查返回的状态
        check = self.check_response(read.contents[0])
        if check.is_success is False:
            return check

        self.session_handle = IOTBaseCommon.DataTransform.unpack_bytes(read.contents[0][4:8], '<I')

        # 返回成功的信号
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_disconnect(self, socket):
        read = self.read_from_socket(socket, self.unregister_session_handle(), has_response=True, pack_unpack=False)
        if read.is_success is False:
            return read

        return IOTBaseCommon.IOTNetResult.create_success()

    def read(self, address: Union[tuple, list]):
        """从PLC读取数据"""
        if isinstance(address, list):
            results = []
            for (adr, type) in address:
                tmp = AllenBradleyTools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                results.append(tmp)
            return self._read(results)
        elif isinstance(address, tuple):
            result = AllenBradleyTools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            return self._read([result])

    def write(self, address: Union[tuple, list]):
        """将数据写入到PLC数据，地址格式为I100，Q100，DB20.100，M100，以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type, value) in address:
                tmp = AllenBradleyTools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                tmp.contents[8] = IOTBaseCommon.DataTransform.convert_value(value, IOTBaseCommon.DataTransform.TypeFormat(type), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.ABCD)
                results.append(tmp)
            return self._write(results)
        elif isinstance(address, tuple):
            result = AllenBradleyTools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            result.contents[8] = IOTBaseCommon.DataTransform.convert_value(address[2], IOTBaseCommon.DataTransform.TypeFormat(address[1]), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.ABCD)
            return self._write([result])

    def ping(self):
        return self.get_socket().is_success

    def get_real_command(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        try:
            command_specific_data = AllenBradleyTools.pack_command_specific_data([bytearray(4), AllenBradleyTools.pack_command_service(self.slot if self.slot is None else bytearray([0x01, self.slot]), [AllenBradleyTools.pack_requset_read(address.contents[1], address.contents[4])])])
            return IOTBaseCommon.IOTNetResult.create_success([command_specific_data])
        except Exception as e:
            return IOTBaseCommon.IOTNetResult(code=10000, msg=f"{e.__str__()}")

    def get_write_command(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        try:
            cip = AllenBradleyTools.pack_request_write(address.contents[1], address.contents[3], address.contents[8])
            command_specific_data = AllenBradleyTools.pack_command_specific_data([bytearray(4), AllenBradleyTools.pack_command_service(self.slot if self.slot is None else bytearray([0x01, self.slot]), [cip])])
            return IOTBaseCommon.IOTNetResult.create_success([command_specific_data])
        except Exception as e:
            return IOTBaseCommon.IOTNetResult(code=10000, msg=f"{e.__str__()}")

    def get_command(self, address: Optional[IOTBaseCommon.IOTNetResult] = None, is_read: bool = True):
        """生成一个读取字数据指令头的通用方法"""
        return self.get_real_command(address) if is_read else self.get_write_command(address)

    def _read(self, addresss: list):
        """基础的读取方法，外界不应该调用本方法"""
        for address in addresss:
            command = self.get_command(address)
            if command.is_success is False:
                address.contents[9] = False
                address.contents[10] = command.msg
                continue

            # 核心数据交互
            read = self.read_server(command.contents[0])
            if read.is_success is False:
                address.contents[9] = False
                address.contents[10] = read.msg
                continue

            # 数据有效性分析
            valid = self.check_response(read.contents[0])
            if valid.is_success is False:
                address.contents[9] = False
                address.contents[10] = valid.msg
                continue

            # 提取数据 -> Extracting data
            extract = AllenBradleyTools.extract_actual_data(read.contents[0], True)
            if extract.is_success is True:
                length, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(IOTBaseCommon.DataTransform.TypeFormat(address.contents[2]))
                response_data = bytearray(length)
                response_data[0: length] = extract.contents[0][0: length]
                address.contents[9] = True
                address.contents[8] = IOTBaseCommon.DataTransform.convert_value(response_data, IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, IOTBaseCommon.DataTransform.TypeFormat(address.contents[2]), format=IOTBaseCommon.DataTransform.DataFormat.ABCD, pos=0)

        return IOTBaseCommon.IOTNetResult.create_success(addresss)

    def _write(self, addresss: list):
        """基础的写入数据的操作支持"""
        for address in addresss:
            command = self.get_command(address, False)
            if command.is_success is False:
                address.contents[9] = False
                address.contents[10] = command.msg
                continue

            # 核心数据交互
            read = self.read_server(command.contents[0])
            if read.is_success is False:
                address.contents[9] = False
                address.contents[10] = read.msg
                continue

            # 数据有效性分析
            valid = self.check_response(read.contents[0])
            if valid.is_success is False:
                address.contents[9] = False
                address.contents[10] = valid.msg
                continue

            # 提取数据 -> Extracting data
            extract = AllenBradleyTools.extract_actual_data(read.contents[0], False)
            if extract.is_success is True:
                address.contents[9] = True

        return IOTBaseCommon.IOTNetResult.create_success(addresss)


class IOTPlcAllenBradley(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.clients = {}

    def exit(self):
        self.exit_flag = True
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
                                {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''}
                                ])
            if mode == 0:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '192.168.1.184/44818/0', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '0.0.0.0/44818/0', 'enum': [], 'tip': ''})
            templates.extend([
                {'required': True, 'name': '点地址' if lan == 'ch' else 'address'.upper(), 'code': 'point_address', 'type': 'string', 'default': 'DB3,REAL4', 'enum': [], 'tip': ''},
                {'required': True, 'name': '点类型' if lan == 'ch' else 'address'.upper(), 'code': 'point_type', 'type': 'int', 'default': 1, 'enum': [], 'tip': ''},
                {'required': False, 'name': '点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''}
            ])
            if mode == 0:
                templates.extend([{'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''}])
            else:
                templates.append(
                    {'required': True, 'name': '点值' if lan == 'ch' else 'value'.upper(), 'code': 'point_value', 'type': 'int', 'default': 0, 'enum': [], 'tip': ''})
            templates.extend([
                {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
            ])

        elif type == 'config':
            if mode == 0:
                templates.extend([
                    {'required': True, 'name': '批量读取个数' if lan == 'ch' else 'Multi Read', 'code': 'multi_read', 'type': 'int', 'default': 100, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '命令间隔(s)' if lan == 'ch' else 'Cmd Interval(s)', 'code': 'cmd_interval', 'type': 'float', 'default': 0.3, 'enum': [], 'tip': ''},
                ])
            templates.append({'required': True, 'name': '超时(s)' if lan == 'ch' else 'Timeout(s)', 'code': 'timeout', 'type': 'int', 'default': 15, 'enum': [], 'tip': ''})
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
                type = point.get('point_type')
                if device_address is not None and address is not None and type is not None:
                    if device_address not in read_items.keys():
                        read_items[device_address] = []
                    if (address, type) not in read_items[device_address]:
                        read_items[device_address].append((address, type))

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                device_address = point.get('point_device_address')
                address = point.get('point_address')
                type = point.get('point_type')
                if device_address is not None and address is not None and type is not None:
                    value = self._get_value(name, device_address, address, type)
                    if value is not None:
                        self.update_results(name, True, value)
            else:
                self.update_results(name, False, 'UnExist')
        return self.get_results(**kwargs)

    def write(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        values = kwargs.get('values', {})
        write_items = {}
        for name, value in values.items():
            point = self.points.get(name)
            if point:
                device_address = point.get('point_device_address')
                address = point.get('point_address')
                type = point.get('point_type')
                if device_address is not None and address is not None and type is not None:
                    if device_address not in write_items.keys():
                        write_items[device_address] = []
                    if (address, type, value) not in write_items[device_address]:
                        write_items[device_address].append((address, type, value))

        self._write(write_items)

        for name, value in values.items():
            point = self.points.get(name)
            if point:
                device_address = point.get('point_device_address')
                address = point.get('point_address')
                type = point.get('point_type')
                if device_address is not None and address is not None and type is not None:
                    result = self.get_device_property(device_address, f"{address}_{type}", [self.get_write_quality, self.get_write_result])
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
        if kwargs.get('address') is not None:
            if self._get_client(kwargs.get('address')) is not None:
                return self._get_client(kwargs.get('address')).ping()
            return False
        return True

    def _get_address_info(self, device_address: str) -> dict:
        # ip/port/slot
        info_list = device_address.split('/')
        return {'host': info_list[0] if len(info_list) > 1 else '', 'port': int(float(info_list[1])) if len(info_list) > 2 else 44818, 'slot': int(float(info_list[2])) if len(info_list) > 3 else 0}

    def _release_client(self, address: str):
        client = self.clients.get(address)
        try:
            if client:
                client.exit()
        except Exception as e:
            pass
        finally:
            if address in self.clients.keys():
                del self.clients[address]

    def _get_client(self, address: str):
        client = self.clients.get(address)
        if client is not None and client.get_connected() is False:
            self._release_client(address)
            client = None

        if client is None:
            info = self._get_address_info(address)
            if len(info) > 0:
                client = AllenBradleyClient(info['host'], info['port'], info['slot'], self.configs.get('timeout'))
                client.logging(call_logging=self.logging)
                result = client.connect()
                if result.is_success is True and client.get_connected() is True:
                    self.clients[address] = client
                else:
                    raise Exception(f"{result.msg}")
        return self.clients.get(address)

    def _send_read_cmd(self, address: str, ab_item_list: list):
        try:
            if self._get_client(address) is not None and len(ab_item_list) > 0:
                result = self._get_client(address).read(ab_item_list)
                if isinstance(result, IOTBaseCommon.IOTNetResult):
                    if result.is_success is True:
                        for item in result.contents:
                            if isinstance(item, IOTBaseCommon.IOTNetResult):
                                if item.is_success:
                                    if item.contents[9] is True:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[2]}", **self.gen_read_write_result(True, item.contents[8]))
                                    else:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[2]}", **self.gen_read_write_result(False, item.contents[10]))
                                else:
                                    self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[2]}", **self.gen_read_write_result(False, item.msg))
                    else:
                        raise Exception(f"{result.msg}")
        except Exception as e:
            for (ad, type) in ab_item_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__()))

    def _read_address(self, *args, **kwargs) -> dict:
        start = time.time()
        (address, ab_items) = args
        results = {}
        units = IOTBaseCommon.chunk_list(ab_items, self.configs.get('multi_read'))
        for unit in units:
            self._send_read_cmd(address, unit)
            self.delay(self.configs.get('cmd_interval', 0.3))
        self.logging(content=f"plc({address}) read: {len(ab_items)} response: {results} group: {len(units)} cost: {'{:.2f}'.format(time.time() - start)}", pos=self.stack_pos)
        return results

    def _read(self, read_items: dict):
        if len(read_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(read_items), f"{self}")
            for address, ab_items in read_items.items():
                jobs.submit_task(self._read_address, address, ab_items)
            return jobs.done()
        return {}

    def _get_value(self, name: str, device_address: str, address: str, type: int):
        try:
            [result, value] = self.get_device_property(device_address, f"{address}_{type}", [self.get_read_quality, self.get_read_result])
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

    def _send_write_cmd(self, address: str, ab_item_list: list):
        try:
            if self._get_client(address) is not None and len(ab_item_list) > 0:
                result = self._get_client(address).write(ab_item_list)
                if isinstance(result, IOTBaseCommon.IOTNetResult):
                    if result.is_success is True:
                        for item in result.contents:
                            if isinstance(item, IOTBaseCommon.IOTNetResult):
                                if item.is_success:
                                    if item.contents[9] is True:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[2]}",  **self.gen_read_write_result(True, item.contents[9], False))
                                    else:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[2]}",  **self.gen_read_write_result(False, item.contents[10], False))
                                else:
                                    self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[2]}",  **self.gen_read_write_result(False, item.msg, False))
                    else:
                        raise Exception(f"{result.msg}")
        except Exception as e:
            for (ad, type, value) in ab_item_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__(), False))

    def _write_address(self, *args, **kwargs) -> dict:
        (address, ab_items) = args
        results = {}
        units = IOTBaseCommon.chunk_list(ab_items, self.configs.get('multi_read'))
        for unit in units:
            self._send_write_cmd(address, unit)
            self.delay(self.configs.get('cmd_interval', 0.3))
        return results

    def _write(self, write_items: dict):
        if len(write_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(write_items), f"{self}")
            for address, ab_items in write_items.items():
                jobs.submit_task(self._write_address, address, ab_items)
            return jobs.done()
        return {}

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_plc_ab.py({pos})"
