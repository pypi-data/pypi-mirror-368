import time
from enum import Enum

from typing import List, Dict, Any, Union, Optional

from .base import IOTBaseCommon, IOTDriver

"""
大端模式
        网络传输一般采用大端序，也被称之为网络字节序，或网络序。IP协议中定义大端序为网络字节序。
        高字节放在内存的地地址
        
点地址
    6/192.168.1.172/102/0/1

rack是机架号，slot卡槽号
    s7-200 0, 1
    s7-300 0, 2
    s7-400 具体看硬件组态
    s7-1200/1500 0, 0/1

dbnumber:
    地址编号（int），只适用于DB区和200samart的V区，其它区全默认0，V区只能填1

read_multi_vars：
    这是可以一次读取<=19个不同地址类型的变量，由于pdu大小限制一次性读取不能超过19个变量

Address:
    bool
        I0.1
        Q2.3
        M0.0
        DB1.DBX0.0
    Byte:
        IB2
        MB0
        QB0
        VB0
        DB1.DBB2
    WORD:
        MW10
        IW
        QW
        VW
        DB1.DBW2
    DWORD:
        MD10
        QD
        ID
        VD
        DB1.DBD2
"""


class SiemensS7Message(IOTBaseCommon.IOTNetMessage):

    """西门子s7协议的消息接收规则"""

    def get_head_length(self) -> int:
        """协议头数据长度，也即是第一次接收的数据长度"""
        return 4

    def get_content_length(self) -> int:
        """二次接收的数据长度"""
        if self.heads is not None:
            return self.heads[2] * 256 + self.heads[3] - 4
        else:
            return 0

    def check_response(self) -> bool:
        """回复报文校验"""
        if self.heads is not None:
            if self.heads[0] == 0x03 and self.heads[1] == 0x00:
                return True
            else:
                return False
        else:
            return False


# 西门子PLC的类型对象
class SiemensS7Version(Enum):
    S7_200 = 1  # 西门子S7-200 需要配置网络模块
    S7_200Smart = 2
    S7_300 = 3
    S7_400 = 4
    S7_1200 = 5
    S7_1500 = 6


# 初始化指令交互报文
class SiemensS7Constant:
    Head1 = bytearray([0x03, 0x00, 0x00, 0x16, 0x11, 0xE0, 0x00, 0x00, 0x00, 0x01, 0x00, 0xC0, 0x01, 0x0A, 0xC1, 0x02, 0x01, 0x02, 0xC2, 0x02, 0x01, 0x00])
    Head2 = bytearray([0x03, 0x00, 0x00, 0x19, 0x02, 0xF0, 0x80, 0x32, 0x01, 0x00, 0x00, 0x04, 0x00, 0x00, 0x08, 0x00, 0x00, 0xF0, 0x00, 0x00, 0x01, 0x00, 0x01, 0x01, 0xE0])
    Head1_200Smart = bytearray([0x03, 0x00, 0x00, 0x16, 0x11, 0xE0, 0x00, 0x00, 0x00, 0x01, 0x00, 0xC1, 0x02, 0x10, 0x00, 0xC2, 0x02, 0x03, 0x00, 0xC0, 0x01, 0x0A])
    Head2_200Smart = bytearray([0x03, 0x00, 0x00, 0x19, 0x02, 0xF0, 0x80, 0x32, 0x01, 0x00, 0x00, 0xCC, 0xC1, 0x00, 0x08, 0x00, 0x00, 0xF0, 0x00, 0x00, 0x01, 0x00, 0x01, 0x03, 0xC0])
    Head1_200 = bytearray([0x03, 0x00, 0x00, 0x16, 0x11, 0xE0, 0x00, 0x00, 0x00, 0x01, 0x00, 0xC1, 0x02, 0x4D, 0x57, 0xC2, 0x02, 0x4D, 0x57, 0xC0, 0x01, 0x09])
    Head2_200 = bytearray([0x03, 0x00, 0x00, 0x19, 0x02, 0xF0, 0x80, 0x32, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0xF0, 0x00, 0x00, 0x01, 0x00, 0x01, 0x03, 0xC0])


# 基础方法
class SiemensS7Tools:

    @staticmethod
    def get_begin_address(address: str):
        address = IOTBaseCommon.format_name(address, r'[^0-9.]+', '')  # 去除地址中的多余字符
        if address.find('.') >= 0:
            temp = address.split(".")
            return int(temp[0]) * 8 + int(temp[1])
        else:
            return int(address) * 8

    @staticmethod
    def get_db(address: str) -> int:
        return int(IOTBaseCommon.format_name(address, r'[^0-9]+', ''))

    @staticmethod
    def get_is_bit(address: str) -> bool:
        return IOTBaseCommon.format_name(address, r'[^0-9.]+', '').find('.') >= 0

    @staticmethod
    def parse_address(address: str, type: int):
        """解析数据地址，解析出地址类型，起始地址，DB块的地址"""
        result = IOTBaseCommon.IOTNetResult()
        try:
            # 1: area 2: start 3: db 4: is_bit 5: length 6: type 7: fmt 8: value
            type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(IOTBaseCommon.DataTransform.TypeFormat(type))
            result.contents[0] = address
            result.contents[3] = 0
            result.contents[5] = type_size
            result.contents[6] = type
            result.contents[7] = type_fmt

            if address[0] == 'I':
                result.contents[1] = 0x81
            elif address[0] == 'Q':
                result.contents[1] = 0x82
            elif address[0] == 'M':
                result.contents[1] = 0x83
            elif address[0] == 'D' or address[0:2] == "DB":
                result.contents[1] = 0x84
                pos = address.find(',')
                if pos > 0:
                    result.contents[3] = SiemensS7Tools.get_db(address[0:pos])
                else:
                    pos = address.find('.')
                    result.contents[3] = SiemensS7Tools.get_db(address[0:pos])
            elif address[0] == 'T':
                result.contents[1] = 0x1D
            elif address[0] == 'C':
                result.contents[1] = 0x1C
            elif address[0] == 'V':
                result.contents[1] = 0x84
                result.contents[3] = 1
            else:
                result.msg = f"Unsupported DataType"
                result.is_success = False
                return result

            if address[0] == 'D' and address[1] == 'B':
                pos = address.find(',') + 1
                if pos > 0:
                    result.contents[2] = SiemensS7Tools.get_begin_address(address[pos:])
                    result.contents[4] = SiemensS7Tools.get_is_bit(address[pos:])
                else:
                    pos = address.find('.') + 1
                    if pos > 0:
                        result.contents[2] = SiemensS7Tools.get_begin_address(address[pos:])
                        result.contents[4] = SiemensS7Tools.get_is_bit(address[pos:])

            else:
                # I0.0、V1004的情况（非PLC地址）
                result.contents[2] = SiemensS7Tools.get_begin_address(address)
                result.contents[4] = SiemensS7Tools.get_is_bit(address)

            result.is_success = True
            return result

        except Exception as e:
            result.msg = e.__str__()
            return result

    @staticmethod
    def get_real_command(address: Optional[list] = None):
        """生成一个读取字数据指令头的通用方法"""
        if address is None:
            raise Exception(f"address is empty")

        if len(address) > 19:
            raise Exception("size must be less than 19")

        read_count = len(address)
        command = bytearray(19 + read_count * 12)
        # ======================================================================================
        command[0] = 0x03  # 固定报文头
        command[1] = 0x00  # 固定报文头
        command[2] = len(command) // 256  # 长度 向下取整
        command[3] = len(command) % 256  # 整个读取请求长度为0x1F = 31
        command[4] = 0x02  # 固定
        command[5] = 0xF0
        command[6] = 0x80  # COTP
        command[7] = 0x32  # 协议标识 协议ID
        command[8] = 0x01  # 1 客户端发送命令 3 服务器回复命令
        command[9] = 0x00  # 冗余标识 (reserved): 0x0000;
        command[10] = 0x00  # 协议数据单元参考； 它由请求事件增加；
        command[11] = 0x00
        command[12] = 0x01  # [11][12] 两个字节，标识序列号，回复报文相同位置和这个完全一样；范围是0~65535
        command[13] = (len(command) - 17) // 256
        command[14] = (len(command) - 17) % 256  # parameter length（减17是因为从[17] 到最后属于parameter）
        command[15] = 0x00  # 读取内部数据时为00，读取CPU型号为Data数据长度
        command[16] = 0x00
        # =====================================================================================
        command[17] = 0x04  # 读写指令，04读，05写
        command[18] = read_count  # 读取数据块个数

        for i, adr in enumerate(address):
            # ===========================================================================================
            # 指定有效值类型
            command[19 + i * 12] = 0x12
            # 接下来本次地址访问长度
            command[20 + i * 12] = 0x0A
            # 语法标记，ANY
            command[21 + i * 12] = 0x10
            # 按字为单位
            command[22 + i * 12] = 0x01 if adr.contents[4] else 0x02
            # 访问数据的个数
            command[23 + i * 12] = adr.contents[5] // 256
            command[24 + i * 12] = adr.contents[5] % 256
            # DB块编号，如果访问的是DB块的话
            command[25 + i * 12] = adr.contents[3] // 256
            command[26 + i * 12] = adr.contents[3] % 256
            # 访问数据类型
            command[27 + i * 12] = adr.contents[1]
            # 偏移位置
            command[28 + i * 12] = adr.contents[2] // 256 // 256 % 256
            command[29 + i * 12] = adr.contents[2] // 256 % 256
            command[30 + i * 12] = adr.contents[2] % 256

        return IOTBaseCommon.IOTNetResult.create_success([command])

    @staticmethod
    def get_write_command(address: Optional[list] = None):
        write_length = 0
        for i, add in enumerate(address):
            write_length = write_length + (2 if len(add.contents[8]) == 1 else len(add.contents[8]))
            if i == len(address) - 1 and len(add.contents[8]) == 1:
                write_length = write_length - 1

        # 前19个固定的、16为Item长度、writes.Length为Imte的个数
        command = bytearray(19 + len(address) * 16 + write_length)
        command[0] = 0x03
        command[1] = 0x00  # [0][1] 固定报文头
        command[2] = len(command) // 256
        command[3] = len(command) % 256  # [2][3] 整个读取请求长度为0x1F = 31
        command[4] = 0x02
        command[5] = 0xF0
        command[6] = 0x80  # COTP
        command[7] = 0x32  # 协议ID
        command[8] = 0x01  # 1 客户端发送命令 3 服务器回复命令
        command[9] = 0x00
        command[10] = 0x00  # [4] - [10] 固定6个字节
        command[11] = 0x00
        command[12] = 0x01  # [11][12] 两个字节，标识序列号，回复报文相同位置和这个完全一样；范围是0~65535
        command[13] = (12 * len(address) + 2) // 256
        command[14] = (12 * len(address) + 2) % 256  # parameter length（减17是因为从[17] 到最后属于parameter）
        command[15] = (write_length + 4 * len(address)) // 256
        command[16] = (write_length + 4 * len(address)) % 256  # data length
        command[17] = 0x05  # 04读 05写
        command[18] = len(address)  # 读取数据块个数
        for i, data in enumerate(address):
            command[19 + i * 12] = 0x12
            command[20 + i * 12] = 0x0A
            command[21 + i * 12] = 0x10
            command[22 + i * 12] = 0x01 if data.contents[4] else 0x02
            command[23 + i * 12] = len(data.contents[8]) // 256
            command[24 + i * 12] = len(data.contents[8]) % 256  # 写入数据个数
            command[25 + i * 12] = data.contents[3] // 256
            command[26 + i * 12] = data.contents[3] % 256  # [25][26] DB块的编号
            command[27 + i * 12] = data.contents[1]  # 访问数据块的类型
            command[28 + i * 12] = data.contents[2] // 256 // 256 % 256
            command[29 + i * 12] = data.contents[2] // 256 % 256
            command[30 + i * 12] = data.contents[2] % 256  # [28][29][30] 访问DB块的偏移量

        index = 18 + len(address) * 12
        for i, data in enumerate(address):
            coefficient = 1 if data.contents[4] else 8
            command[1 + index] = 0x00
            command[2 + index] = 0x03 if data.contents[4] else 0x04
            command[3 + index] = len(data.contents[8]) * coefficient // 256
            command[4 + index] = len(data.contents[8]) * coefficient % 256  # 按位计算出的长度

            if len(data.contents[8]) == 1:
                if data.contents[4]:
                    command[5 + index] = 0x01 if data.contents[8][0] == 0x01 else 0x00
                else:
                    command[5 + index] = data.contents[8][0]
                if i >= len(address) - 1:
                    index = index + (4 + 1)
                else:
                    index = index + (4 + 2)  # fill byte  （如果不是最后一个bit，则需要填充一个空数据）
            else:
                command[5 + index: 5 + index + len(data.contents[8])] = data.contents[8]
                index = index + 4 + len(data.contents[8])
        return IOTBaseCommon.IOTNetResult.create_success([command])


class SiemensS7Client(IOTBaseCommon.IOTNetworkDeviceClient):
 
    def __init__(self, version: SiemensS7Version, host: str, port: int, slot: int = 0, rack: int = 0, timeout: int = 10, conn_retries: int = 1):
        super().__init__(host, port, timeout, conn_retries)
        self.version = version
        self.word_length = 2
        self.slot = slot
        self.rack = rack

    def get_net_msg(self):
        return SiemensS7Message()
    
    def initialization_on_connect(self, socket):
        """连接上服务器后需要进行的二次握手操作"""
        head1, head2 = self.init_head()
        
        # 第一次握手
        read_first = self.read_from_socket(socket, head1)
        if read_first.is_success is False: 
            return read_first

        # 第二次握手
        read_second = self.read_from_socket(socket, head2)
        if read_second.is_success is False: 
            return read_second

        # 返回成功的信号
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_disconnect(self, socket):
        return IOTBaseCommon.IOTNetResult.create_success()

    def init_head(self):
        head1 = SiemensS7Constant.Head1
        head2 = SiemensS7Constant.Head2
        if self.version == SiemensS7Version.S7_200:  # 0, 1
            head1 = SiemensS7Constant.Head1_200
            head2 = SiemensS7Constant.Head2_200
        elif self.version == SiemensS7Version.S7_200Smart:  #
            head1 = SiemensS7Constant.Head1_200Smart
            head2 = SiemensS7Constant.Head2_200Smart
        elif self.version == SiemensS7Version.S7_300:   # 0, 2
            head1[21] = self.rack * 0x20 + self.slot
        elif self.version == SiemensS7Version.S7_400:  # 具体看硬件组态
            head1[21] = self.rack * 0x20 + self.slot
            head1[17] = 0
        elif self.version == SiemensS7Version.S7_1200:   # 0, 0/1
            head1[21] = self.rack * 0x20 + self.slot
        elif self.version == SiemensS7Version.S7_1500:   # 0, 0/1
            head1[21] = self.rack * 0x20 + self.slot
        else:
            head1[18] = 0

        return head1, head2

    def read(self, address: Union[tuple, list]):
        """从PLC读取数据，地址格式为I100，Q100，DB20.100，M100，T100，C100以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type) in address:
                tmp = SiemensS7Tools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                results.append(tmp)
            return self._read(results)
        elif isinstance(address, tuple):
            result = SiemensS7Tools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            return self._read([result])

    def write(self, address: Union[tuple, list]):
        """将数据写入到PLC数据，地址格式为I100，Q100，DB20.100，M100，以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type, value) in address:
                tmp = SiemensS7Tools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                tmp.contents[8] = IOTBaseCommon.DataTransform.convert_value(value, IOTBaseCommon.DataTransform.TypeFormat(type), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.DCBA)
                results.append(tmp)
            return self._write(results)
        elif isinstance(address, tuple):
            result = SiemensS7Tools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            result.contents[8] = IOTBaseCommon.DataTransform.convert_value(address[2], IOTBaseCommon.DataTransform.TypeFormat(address[1]), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.DCBA)
            return self._write([result])

    def ping(self):
        return self.get_socket().is_success

    def _read(self, address: list):
        """基础的读取方法，外界不应该调用本方法"""
        command = SiemensS7Tools.get_real_command(address)
        if command.is_success is False:
            return command

        read = self.read_server(command.contents[0])
        if read.is_success is False:
            return read

        length = len(read.contents[0]) - 21
        response_data = bytearray(length)
        response_data[0: length] = read.contents[0][21: 21 + length]
        cursor = 0

        for i, adr in enumerate(address):
            adr.contents[9] = True
            if (response_data[cursor] == 0x0A and response_data[cursor+1] == 0x00) or (response_data[cursor] == 0x05 and response_data[cursor+1] == 0x00):
                adr.contents[9] = False
                adr.contents[10] = f"读取{adr.contents[0]}失败，请确认是否存在该地址"
            elif response_data[cursor] != 0xFF:
                adr.contents[9] = False
                adr.contents[10] = f"读取{adr.contents[0]}失败，异常代码: {response_data[cursor]}"

            cursor += 4
            if adr.contents[9] is False:
                continue

            read_result = response_data[cursor: cursor + adr.contents[5]]
            cursor += 2 if adr.contents[5] == 1 else adr.contents[5]
            adr.contents[8] = IOTBaseCommon.DataTransform.convert_value(read_result, None, IOTBaseCommon.DataTransform.TypeFormat(adr.contents[6]), format=IOTBaseCommon.DataTransform.DataFormat.DCBA)[0]

        return IOTBaseCommon.IOTNetResult.create_success(address)

    def _write(self, address: list):
        """基础的写入数据的操作支持"""
        command = SiemensS7Tools.get_write_command(address)
        if command.is_success is False:
            return command

        write = self.read_server(command.contents[0])
        if write.is_success is False:
            return write

        response_data = write.contents[0]
        for i, adr in enumerate(address):
            offset = 21 + i
            adr.contents[9] = False
            adr.contents[10] = f"UnResponse"
            if offset <= len(response_data) - 1:
                if response_data[offset] == 0x0A or response_data[offset] == 0x05:
                    adr.contents[9] = False
                    adr.contents[10] = f"读取{adr.contents[0]}失败，请确认是否存在该地址"
                elif response_data[offset] != 0xFF:
                    adr.contents[9] = False
                    adr.contents[10] = f"读取{adr.contents[0]}失败，异常代码: {response_data[offset]}"
                else:
                    adr.contents[9] = True
        return IOTBaseCommon.IOTNetResult.create_success(address)


class SiemensS7Server(IOTBaseCommon.IOTNetworkDeviceServer):

    def __init__(self, version: SiemensS7Version, host: str, port: int, slot: int = 0, rack: int = 0, timeout: int = 10):
        super().__init__(host, port, timeout)
        self.version = version
        self.word_length = 2
        self.slot = slot
        self.rack = rack

    def get_net_msg(self):
        return SiemensS7Message()

    def initialization_on_connect(self, socket):
        # 返回成功的信号
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_disconnect(self, socket):
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_receive(self, socket, datas: bytes):
        if datas[3] == len(SiemensS7Constant.Head1_200Smart) or datas[3] == len(SiemensS7Constant.Head2_200Smart):
            self.send(socket, datas)
        else:
            self._analyze_data(datas, socket)

    def simulate(self, address: Union[tuple, list]):
        """将数据写入到PLC数据，地址格式为I100，Q100，DB20.100，M100，以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type, value) in address:
                tmp = SiemensS7Tools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                tmp.contents[8] = IOTBaseCommon.DataTransform.convert_value(value, IOTBaseCommon.DataTransform.TypeFormat(type), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.DCBA)
                results.append(tmp)
            return self._simulate(results)
        elif isinstance(address, tuple):
            result = SiemensS7Tools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            result.contents[8] = IOTBaseCommon.DataTransform.convert_value(address[2], IOTBaseCommon.DataTransform.TypeFormat(address[1]), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.DCBA)
            return self._simulate([result])

    def _simulate(self, address: list):
        """基础的写入数据的操作支持"""
        command = SiemensS7Tools.get_write_command(address)
        if command.is_success is True:
            self._analyze_data(command.contents[0])
    
    def _analyze_data(self, datas: bytes, socket=None):
        if len(datas) > 21:
            if datas[17] == 4:  # 读
                db_size = datas[18]  # 数据块个数
                read_length = 0  # 读取数据总长度
                for i in range(db_size):
                    byte_length = datas[23 + i * 12] * 256 + datas[24 + i * 12]  # 访问数据的个数，以byte为单位
                    if byte_length == 1 and i < db_size - 1:  # 非最后一个bit/byte，需要补全
                        byte_length += 1
                    read_length += byte_length
    
                data_content = bytearray(4 * db_size + read_length)  # 数据报文总长度
                cursor = 0
                for i in range(db_size):
                    begin_address = datas[28 + i * 12] * 256 * 256 + datas[29 + i * 12] * 256 + datas[30 + i * 12]  # DB块的偏移量
                    byte_length = datas[23 + i * 12] * 256 + datas[24 + i * 12]  # 访问数据的个数
                    if byte_length == 1 and i < db_size - 1:  # 非最后一个bit/byte，需要补全
                        byte_length += 1
                    is_bit = datas[22 + i * 12] == 0x01  # 是否是bit类型
                    db_type = datas[27 + i * 12]
                    data_key = f"s200-{db_type}"
                    if data_key not in self.values.keys():
                        self.values[data_key] = bytearray(65536)
                    db_byte_array = self.values.get(data_key)
                    data_content[0 + cursor] = 0xFF
                    data_content[1 + cursor] = 0x03 if is_bit else 0x04  # 04 byte(字节) 03 bit（位）
                    data_content[2 + cursor] = byte_length // 256  # 后半截数据数的Length
                    data_content[3 + cursor] = byte_length % 256  # 后半截数据数的Length
                    pos = begin_address // 8
                    if is_bit:  # 按bit
                        data_content[4 + cursor] = IOTBaseCommon.DataTransform.get_bool(db_byte_array[pos], begin_address % 8)
                    else:
                        data_content[4 + cursor: 4 + cursor + byte_length] = db_byte_array[pos: pos + byte_length]
                    cursor += 4 + byte_length
    
                if socket:
                    response = bytearray(21 + len(data_content))
                    response[0:21] = bytes.fromhex("03 00 00 1A 02 F0 80 32 03 00 00 00 01 00 02 00 00 00 00 04 01")
                    response[8] = 0x03  # 1 客户端发送命令 3 服务器回复命令
                    response[2] = len(response) // 256  # 返回数据长度
                    response[3] = len(response) % 256
                    response[15] = len(response) // 256  # 读取数据长度
                    response[16] = len(response) % 256
                    response[20] = datas[18]  # 读取数据块个数
                    response[21:] = data_content[:]
                    self.send(socket, response)
            elif datas[17] == 5:  # 写
                writes_length = datas[18]  # 写如数据的个数
                cursor = 0
                for i in range(writes_length):
                    begin_address = datas[28 + i * 12] * 256 * 256 + datas[29 + i * 12] * 256 + datas[30 + i * 12]  # DB块的偏移量
                    db_type = datas[27 + i * 12]
                    data_key = f"s200-{db_type}"
                    if data_key not in self.values.keys():
                        self.values[data_key] = bytearray(65536)
                    data_before_index = 18 + writes_length * 12  # Data之前的下标
                    is_bit = datas[data_before_index + 4 * (i + 1) - 2 + cursor] == 0x03  # [2 + index]是否是bit类型
                    coefficient = 1 if is_bit else 8
                    write_value = bytearray(datas[data_before_index + 4 * (i + 1) + cursor] // coefficient)  # 初始化要写入的字节数组长度
                    requet_begin_location = data_before_index + 4 * (i + 1) + cursor + 1  # 开始写入的地址（报文中的数据的位置）
    
                    if len(write_value) == 1 and i < writes_length - 1:
                        cursor = cursor + 1
                    cursor += len(write_value)
    
                    write_value[:len(write_value)] = datas[requet_begin_location: requet_begin_location + len(write_value)]
                    db_byte_array = self.values.get(data_key)
    
                    pos = begin_address // 8
                    if is_bit:  # 按bit
                        db_byte_array[pos] = IOTBaseCommon.DataTransform.set_bool(db_byte_array[pos], begin_address % 8, write_value[0])
                    else:
                        db_byte_array[pos: pos + len(write_value)] = write_value
    
                    self.values[data_key] = db_byte_array
                
                if socket:
                    response = bytearray(21)
                    response[0:22] = bytes.fromhex("03 00 00 16 02 F0 80 32 03 00 00 00 01 00 02 00 01 00 00 05 01")
                    response[21: 21 + writes_length] = bytes([0xFF] * writes_length)
                    self.send(socket, response)


class IOTPlcSiemensS7(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.clients = {}
        self.servers = {}
        self.plc_objects = {}

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
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '0.0.0.0/102/0/1', 'enum': [], 'tip': ''})
            templates.extend([
                {'required': True, 'name': '点地址' if lan == 'ch' else 'address'.upper(), 'code': 'point_address', 'type': 'string', 'default': 'DB3,REAL4', 'enum': [], 'tip': ''},
                {'required': True, 'name': '点类型' if lan == 'ch' else 'address'.upper(), 'code': 'point_type', 'type': 'int', 'default': 1, 'enum': [], 'tip': ''},
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
            if mode == 0:
                templates.extend([
                    {'required': False, 'name': '连接重试' if lan == 'ch' else 'Conn Retries', 'code': 'conn_retries', 'type': 'int', 'default': 1, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '批量读取个数' if lan == 'ch' else 'Multi Read', 'code': 'multi_read', 'type': 'int', 'default': 19, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '命令间隔(s)' if lan == 'ch' else 'Cmd Interval(s)', 'code': 'cmd_interval', 'type': 'float', 'default': 0.1, 'enum': [], 'tip': ''},
                ])
            templates.append({'required': True, 'name': '超时(s)' if lan == 'ch' else 'Timeout(s)', 'code': 'timeout', 'type': 'int', 'default': 15, 'enum': [], 'tip': ''})
        return templates

    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
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

    def simulate(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        points = kwargs.get('points', {})
        self.logging(content=f"simulate({len(points)})")
        server_objects = {}
        for name, point in points.items():
            point = points.get(name)
            if point:
                device_address = point.get('point_device_address')
                address = point.get('point_address')
                type = point.get('point_type')
                value = point.get('point_value')
                if device_address is not None and address is not None and type is not None:
                    if device_address not in server_objects.keys():
                        server_objects[device_address] = []
                    if (address, type, value) not in server_objects[device_address]:
                        server_objects[device_address].append((address, type, value))

        if len(server_objects) > 0:
            for address, objects in server_objects.items():
                if self._get_server(address) is not None:
                    self._refresh_objects(address, objects)

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        # version/ip/port/rack/slot
        versions = kwargs.get('version', [1, 2, 3])
        ip = kwargs.get('ip', '')
        port = kwargs.get('port', 102)
        racks = kwargs.get('rack', [0, 1, 2, 3])
        slots = kwargs.get('slot', [0, 1, 2, 3])
        for version in versions:
            for rack in racks:
                for slot in slots:
                    address = f"{version}/{ip}/{port}/{rack}/{slot}"
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

    def _get_address_info(self, device_address: str) -> dict:
        # version/ip/port/rack/slot
        info_list = device_address.split('/')
        return {'host': info_list[1] if len(info_list) > 1 else '', 'port': int(float(info_list[2])) if len(info_list) > 2 else 102, 'rack': int(float(info_list[3])) if len(info_list) > 3 else 0, 'slot': int(float(info_list[4])) if len(info_list) > 4 else 1, 'type': int(float(info_list[0])) if len(info_list) > 1 else 1}

    def _release_client(self, address: str):
        try:
            client = self.clients.get(address)
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
            if 'type' in info.keys():
                client = SiemensS7Client(SiemensS7Version(info['type']), info['host'], info['port'], info['rack'], info['slot'], self.configs.get('timeout'), self.configs.get('conn_retries', 1))
                client.logging(call_logging=self.logging)
                result = client.connect()
                if result.is_success is True and client.get_connected() is True:
                    self.clients[address] = client
                else:
                    raise Exception(f"{result.msg}")
        return self.clients.get(address)

    def _send_read_cmd(self, address: str, s7_item_list: list):
        try:
            if self._get_client(address) is not None and len(s7_item_list) > 0:
                result = self._get_client(address).read(s7_item_list)
                if isinstance(result, IOTBaseCommon.IOTNetResult):
                    if result.is_success is True:
                        for item in result.contents:
                            if isinstance(item, IOTBaseCommon.IOTNetResult):
                                if item.is_success:
                                    if item.contents[9] is True:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[6]}", **self.gen_read_write_result(True, item.contents[8]))
                                    else:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[6]}", **self.gen_read_write_result(False, item.contents[10]))
                                else:
                                    self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[6]}", **self.gen_read_write_result(False, item.msg))
                    else:
                        raise Exception(f"{result.msg}")
        except Exception as e:
            for (ad, type) in s7_item_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__()))

    def _read_address(self, *args, **kwargs) -> dict:
        start = time.time()
        (address, s7_items) = args
        results = {}
        units = IOTBaseCommon.chunk_list(s7_items, self.configs.get('multi_read'))
        for unit in units:
            self._send_read_cmd(address, unit)
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

    def _send_write_cmd(self, address: str, s7_item_list: list):
        try:
            if self._get_client(address) is not None and len(s7_item_list) > 0:
                result = self._get_client(address).write(s7_item_list)
                if isinstance(result, IOTBaseCommon.IOTNetResult):
                    if result.is_success is True:
                        for item in result.contents:
                            if isinstance(item, IOTBaseCommon.IOTNetResult):
                                if item.is_success:
                                    if item.contents[9] is True:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[6]}",  **self.gen_read_write_result(True, item.contents[9], False))
                                    else:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[6]}",  **self.gen_read_write_result(False, item.contents[10], False))
                                else:
                                    self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[6]}",  **self.gen_read_write_result(False, item.msg, False))
                    else:
                        raise Exception(f"{result.msg}")
        except Exception as e:
            for (ad, type, value) in s7_item_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__(), False))

    def _write_address(self, *args, **kwargs) -> dict:
        (address, s7_items) = args
        results = {}
        units = IOTBaseCommon.chunk_list(s7_items, self.configs.get('multi_read'))
        for unit in units:
            self._send_write_cmd(address, unit)
            self.delay(self.configs.get('cmd_interval', 0.3))
        return results

    def _write(self, write_items: dict):
        if len(write_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(write_items), f"{self}")
            for address, s7_items in write_items.items():
                jobs.submit_task(self._write_address, address, s7_items)
            return jobs.done()
        return {}

    def _get_server(self, address: str):
        server = self.servers.get(address, {}).get('server')
        if server is None:
            info = self._get_address_info(address)
            if 'type' in info.keys():
                server = SiemensS7Server(SiemensS7Version(info['type']), info['host'], info['port'], info['rack'], info['slot'])
                server.logging(call_logging=self.logging)
                server.start_server()
                self.servers[address] = {'server': server, 'blocks': {}}
        return server

    def _release_server(self, address: str):
        try:
            server = self.servers.get(address, {}).get('server')
            if server is not None:
                server.stop_server()
            server = None
        except:
            pass
        finally:
            if 'server' in self.servers.get(address, {}).keys():
                del self.servers[address]['server']

    def _refresh_objects(self, address: str, objects: list):
        server_cache = self.servers.get(address, {})
        server = server_cache.get('server')
        if server is not None and len(objects) > 0:
            units = IOTBaseCommon.chunk_list(objects, self.configs.get('multi_read'))
            for unit in units:
                server.simulate(unit)

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_plc_siemens.py({pos})"
