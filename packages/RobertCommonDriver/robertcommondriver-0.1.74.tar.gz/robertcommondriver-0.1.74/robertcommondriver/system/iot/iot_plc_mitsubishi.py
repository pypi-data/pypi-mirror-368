import time

from enum import Enum

from typing import List, Dict, Any, Union, Optional

from .base import IOTBaseCommon, IOTDriver

"""
https://www.cnblogs.com/dathlin/p/7469679.html
FX5U配置：
    参数-FX5UCPU-模块参数-以太网端口
        SLMP连接设备-TCP

小端方式

地址：
    第一种，使用系统的类来标识，比如M200，写成(MelsecDataType.M, 200)的表示形式，这样也可以去MelsecDataType里面找到所有支持的数据类型。
    第二种，使用字符串表示，这个组件里所有的读写操作提供字符串表示的重载方法，所有的支持访问的类型对应如下，字符串的表示方式存在十进制和十六进制的区别：  
        输入继电器："X100","X1A0"            // 字符串为十六进制机制
        输出继电器："Y100" ,"Y1A0"           // 字符串为十六进制机制
        内部继电器："M100","M200"           // 字符串为十进制
        锁存继电器："L100"  ,"L200"           // 字符串为十进制
        报警器：       "F100", "F200"            // 字符串为十进制
        边沿继电器："V100" , "V200"          // 字符串为十进制
        链接继电器："B100" , "B1A0"          // 字符串为十六进制
        步进继电器："S100" , "S200"          // 字符串为十进制
        数据寄存器："D100", "D200"           // 字符串为十进制
        链接寄存器："W100" ,"W1A0"         // 字符串为十六进制
        文件寄存器："R100","R200"            // 字符串为十进制
        
A兼容1E帧协议
    FX3U(C) PLC
Qna兼容3E帧协议
    Q06UDV PLC
    fx5u PLC
    Q02CPU PLC
    L02CPU PLC

Address:
    0: address 1: type_char 2: start 3: type_code 4 bit_type 5: length 6: is_bit 7:type  8:value 9: result 10: msg 11 format
    
"""


class MitsubishiA1EBinaryMessage(IOTBaseCommon.IOTNetMessage):

    """三菱的A兼容1E帧协议解析规则"""

    def get_head_length(self) -> int:
        """协议头数据长度，也即是第一次接收的数据长度"""
        return 2    # 副标题 + 结束代码（结束代码用于判断后续需要接收的数据长度）

    def get_content_length(self) -> int:
        """二次接收的数据长度"""
        if self.heads is not None:
            if self.heads[1] == 0x5B:
                return 2    # /结束代码 + 0x00
            else:
                length = self.sends[10] if self.sends[10] % 2 == 0 else self.sends[10] + 1
                if self.heads[0] == 0x80:   # 位单位成批读出后，回复副标题
                    return int(length / 2)
                elif self.heads[0] == 0x81:  # 字单位成批读出后，回复副标题
                    return self.sends[10] * 2
                elif self.heads[0] == 0x82:  # 位单位成批写入后，回复副标题
                    return 0
                elif self.heads[0] == 0x83:  # 字单位成批写入后，回复副标题
                    return 0    # 在A兼容1E协议中，写入值后，若不发生异常，只返回副标题 + 结束代码(0x00) 这已经在协议头部读取过了，后面要读取的长度为0（contentLength=0）
        return 0

    def check_response(self) -> bool:
        """回复报文校验"""
        if self.heads is not None:
            if self.heads[0] - self.sends[0] == 0x80:
                return True
            else:
                return False
        else:
            return False


class MitsubishiQnA3EBinaryMessage(IOTBaseCommon.IOTNetMessage):

    """三菱的Qna兼容3E帧协议解析规则"""

    def get_head_length(self) -> int:
        """协议头数据长度，也即是第一次接收的数据长度"""
        return 9

    def get_content_length(self) -> int:
        """二次接收的数据长度"""
        if self.heads is not None:
            return self.heads[8] * 256 + self.heads[7]
        return 0

    def check_response(self) -> bool:
        """回复报文校验"""
        if self.heads is not None:
            if self.heads[0] == 0xD0 and self.heads[1] == 0x00:
                return True
            else:
                return False
        else:
            return False


class MitsubishiQnA3EAsciiMessage(IOTBaseCommon.IOTNetMessage):

    """三菱的Qna兼容3E帧的ASCII协议解析规则"""

    def get_head_length(self) -> int:
        """协议头数据长度，也即是第一次接收的数据长度"""
        return 18

    def get_content_length(self) -> int:
        """二次接收的数据长度"""
        if self.heads is not None:
            return int(self.heads[14:18].decode('ascii'), 16)
        return 0

    def check_response(self) -> bool:
        """回复报文校验"""
        if self.heads is not None:
            if self.heads[0] == ord('D') and self.heads[1] == ord('0') and self.heads[2] == ord('0') and self.heads[3] == ord('0'):
                return True
            else:
                return False
        else:
            return False


# 三菱PLC的类型对象
class MitsubishiVersion(Enum):
    NONE = 0
    A_1E = 1  # 三菱MC_A-1E帧
    Qna_3E = 2  # 三菱MC_Qna-3E帧 必须为二进制通讯
    Qna_3E_ASCII = 3  # 三菱MC_Qna-3E帧 必须为ASCII通讯格式


# 基础方法
class MitsubishiTools:

    @staticmethod
    def parse_address(version: MitsubishiVersion, address: str, type: int):
        if version == MitsubishiVersion.A_1E:
            return MitsubishiTools.parse_address_a_1e(address, type)
        elif version == MitsubishiVersion.Qna_3E:
            return MitsubishiTools.parse_address_qna_3e(address, type)
        elif version == MitsubishiVersion.Qna_3E_ASCII:
            return MitsubishiTools.parse_address_qna_3e(address, type)

    @staticmethod
    def parse_address_a_1e(address: str, type: int):
        """
            解析数据地址，解析出地址类型，起始地址，DB块的地址
            0: address 1: type_char 2: start 3: type_code 4 bit_type 5: length 6: is_bit 6:type  8:value 9: result 10:
        """
        result = IOTBaseCommon.IOTNetResult()
        try:
            # 0: address 1: type_char 2: start 3: type_code 4 bit_type 5: length 6: is_bit 6:type  8:value 9: result 10: msg 11: format
            result.contents[0] = address
            result.contents[1] = address[0:1].upper()
            type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(IOTBaseCommon.DataTransform.TypeFormat(type))
            result.contents[5] = type_size
            result.contents[6] = True if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL else False
            result.contents[7] = type
            if address[0].upper() == 'X':   # X输入寄存器
                result.contents[3] = bytearray([0x58, 0x20])
                result.contents[4] = 0x01
                result.contents[11] = 8
                result.contents[2] = int(address[1:], 8)
            elif address[0].upper() == 'Y':   # Y输出寄存器
                result.contents[3] = bytearray([0x59, 0x20])
                result.contents[4] = 0x01
                result.contents[11] = 8
                result.contents[2] = int(address[1:], 8)
            elif address[0].upper() == 'M':   # M中间寄存器
                result.contents[3] = bytearray([0x4D, 0x20])
                result.contents[4] = 0x01
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'S':   # S状态寄存器
                result.contents[3] = bytearray([0x53, 0x20])
                result.contents[4] = 0x01
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'D':   # D数据寄存器
                result.contents[3] = bytearray([0x44, 0x20])
                result.contents[4] = 0x00
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'R':   # R文件寄存器
                result.contents[3] = bytearray([0x52, 0x20])
                result.contents[4] = 0x00
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            else:
                result.is_success = False
                result.msg = f"Unsupported DataType"
                return result
            result.is_success = True
            return result

        except Exception as e:
            result.msg = e.__str__()
            return result

    @staticmethod
    def parse_address_qna_3e(address: str, type: int):
        """
            解析数据地址，解析出地址类型，起始地址，DB块的地址
            0: address 1: type_char 2: start 3: type_code 4 bit_type 5: length 6: is_bit 6:type  8:value 9: result 10:
        """
        result = IOTBaseCommon.IOTNetResult()
        try:
            # 0: address 1: type_char 2: start 3: type_code 4 bit_type 5: length 6: is_bit 6:type  8:value 9: result 10:
            result.contents[0] = address
            result.contents[1] = address[0:1].upper()
            type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(IOTBaseCommon.DataTransform.TypeFormat(type))
            result.contents[5] = type_size
            result.contents[6] = True if type == IOTBaseCommon.DataTransform.TypeFormat.BOOL else False
            result.contents[7] = type

            if address[0].upper() == 'M':  # M中间继电器
                result.contents[3] = bytearray([0x90])
                result.contents[4] = 0x01
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'X':  # X输入继电器
                result.contents[3] = bytearray([0x9C])
                result.contents[4] = 0x01
                result.contents[11] = 16
                result.contents[2] = int(address[1:], 16)
            elif address[0].upper() == 'Y':  # Y输出继电器
                result.contents[3] = bytearray([0x9D])
                result.contents[4] = 0x01
                result.contents[11] = 16
                result.contents[2] = int(address[1:], 16)
            elif address[0].upper() == 'D':  # D数据寄存器
                result.contents[3] = bytearray([0xA8])
                result.contents[4] = 0x00
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'W':  # W链接寄存器
                result.contents[3] = bytearray([0xB4])
                result.contents[4] = 0x00
                result.contents[11] = 16
                result.contents[2] = int(address[1:], 16)
            elif address[0].upper() == 'L':  # L锁存继电器
                result.contents[3] = bytearray([0x92])
                result.contents[4] = 0x01
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'F':  # F报警器
                result.contents[3] = bytearray([0x93])
                result.contents[4] = 0x01
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'V':  # V边沿继电器
                result.contents[3] = bytearray([0x94])
                result.contents[4] = 0x01
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'B':  # B链接继电器
                result.contents[3] = bytearray([0xA0])
                result.contents[4] = 0x01
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 16)
            elif address[0].upper() == 'R':  # R文件寄存器
                result.contents[3] = bytearray([0xAF])
                result.contents[4] = 0x00
                result.contents[11] = 10
                result.contents[2] = int(address[1:], 10)
            elif address[0].upper() == 'S':
                if address[1].upper() == 'C':   # 累计定时器的线圈
                    result.contents[3] = bytearray([0xC6])
                    result.contents[4] = 0x01
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
                elif address[1].upper() == 'S':   # 累计定时器的触点
                    result.contents[3] = bytearray([0xC7])
                    result.contents[4] = 0x01
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
                elif address[1].upper() == 'N':   # 累计定时器的当前值
                    result.contents[3] = bytearray([0xC8])
                    result.contents[4] = 0x00
                    result.contents[11] = 100
                    result.contents[2] = int(address[2:], 100)
                    result.contents[1] = address[0:2].upper()
                else:   # S步进继电器
                    result.contents[3] = bytearray([0x98])
                    result.contents[4] = 0x01
                    result.contents[11] = 10
                    result.contents[2] = int(address[1:], 10)
                    result.contents[1] = address[0:1].upper()
            elif address[0].upper() == 'Z':
                if address[1].upper() == 'R':   # 文件寄存器ZR区
                    result.contents[3] = bytearray([0xB0])
                    result.contents[4] = 0x00
                    result.contents[11] = 16
                    result.contents[2] = int(address[2:], 16)
                    result.contents[1] = address[0:2].upper()
                else:   # 变址寄存器
                    result.contents[3] = bytearray([0xCC])
                    result.contents[4] = 0x00
                    result.contents[11] = 10
                    result.contents[2] = int(address[1:], 10)
                    result.contents[1] = address[0:1].upper()
            elif address[0].upper() == 'T':
                if address[1].upper() == 'N':   # 定时器的当前值
                    result.contents[3] = bytearray([0xC2])
                    result.contents[4] = 0x00
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
                elif address[1].upper() == 'S':   # 定时器的触点
                    result.contents[3] = bytearray([0xC1])
                    result.contents[4] = 0x01
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
                elif address[1].upper() == 'C':   # 定时器的线圈
                    result.contents[3] = bytearray([0xC0])
                    result.contents[4] = 0x01
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
            elif address[0].upper() == 'C':
                if address[1].upper() == 'N':   # 计数器的当前值
                    result.contents[3] = bytearray([0xC5])
                    result.contents[4] = 0x00
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
                elif address[1].upper() == 'S':   # 计数器的触点
                    result.contents[3] = bytearray([0xC4])
                    result.contents[4] = 0x01
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
                elif address[1].upper() == 'C':   # 计数器的线圈
                    result.contents[3] = bytearray([0xC3])
                    result.contents[4] = 0x01
                    result.contents[11] = 10
                    result.contents[2] = int(address[2:], 10)
                    result.contents[1] = address[0:2].upper()
            result.is_success = True
            return result

        except Exception as e:
            result.msg = e.__str__()
            return result

    @staticmethod
    def build_bytes_from_data(value, length=None):
        """从数据构建一个ASCII格式地址字节"""
        if length is None:
            return ('{:02X}'.format(value)).encode('ascii')
        else:
            return (('{:0' + str(length) + 'X}').format(value)).encode('ascii')

    @staticmethod
    def build_bytes_from_address(address, base):
        """从三菱的地址中构建MC协议的6字节的ASCII格式的地址"""
        if base == 10:
            return ('{:06d}'.format(address)).encode('ascii')
        else:
            return ('{:06X}'.format(address)).encode('ascii')


class MitsubishiClient(IOTBaseCommon.IOTNetworkDeviceClient):

    def __init__(self, version: MitsubishiVersion, host: str, port: int, timeout: int = 10):
        super().__init__(host, port, timeout)
        self.version = version
        self.word_length = 1
        self.network = 0    # 网络号 依据PLC的配置而配置，如果PLC配置了1，那么此处也填0，如果PLC配置了2，此处就填2，测试不通的话，继续测试0
        self.network_station = 0  # 目标模块站号 依据PLC的配置而配置，如果PLC配置了1，那么此处也填0，如果PLC配置了2，此处就填2
        self.plc_number = 0xFF

    def get_net_msg(self):
        if self.version == MitsubishiVersion.A_1E:
            return MitsubishiA1EBinaryMessage()
        elif self.version == MitsubishiVersion.Qna_3E_ASCII:
            return MitsubishiQnA3EAsciiMessage()
        else:
            return MitsubishiQnA3EBinaryMessage()

    def initialization_on_connect(self, socket):
        # 返回成功的信号
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_disconnect(self, socket):
        return IOTBaseCommon.IOTNetResult.create_success()

    def read(self, address: Union[tuple, list]):
        """从PLC读取数据，地址格式为I100，Q100，DB20.100，M100，T100，C100以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type) in address:
                tmp = MitsubishiTools.parse_address(self.version, adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                results.append(tmp)
            return self._read(results)
        elif isinstance(address, tuple):
            result = MitsubishiTools.parse_address(self.version, address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            return self._read([result])

    def write(self, address: Union[tuple, list]):
        """将数据写入到PLC数据，地址格式为I100，Q100，DB20.100，M100，以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type, value) in address:
                tmp = MitsubishiTools.parse_address(self.version, adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                tmp.contents[8] = IOTBaseCommon.DataTransform.convert_value(value, IOTBaseCommon.DataTransform.TypeFormat(type), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.ABCD)
                results.append(tmp)
            return self._write(results)
        elif isinstance(address, tuple):
            result = MitsubishiTools.parse_address(self.version, address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            result.contents[8] = IOTBaseCommon.DataTransform.convert_value(address[2], IOTBaseCommon.DataTransform.TypeFormat(address[1]), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.ABCD)
            return self._write([result])

    def ping(self):
        return self.get_socket().is_success

    def get_real_command(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        """生成一个读取字数据指令头的通用方法"""
        if self.version == MitsubishiVersion.A_1E:
            return self._get_real_command_a_1e(address)
        elif self.version == MitsubishiVersion.Qna_3E_ASCII:
            return self._get_real_command_qna_3e_ascii(address)
        else:
            return self._get_real_command_qna_3e(address)

    def get_write_command(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        """生成一个读取字数据指令头的通用方法"""
        if self.version == MitsubishiVersion.A_1E:
            return self._get_write_command_a_1e(address)
        elif self.version == MitsubishiVersion.Qna_3E_ASCII:
            return self._get_write_command_qna_3e_ascii(address)
        else:
            return self._get_write_command_qna_3e(address)

    def analyse_response(self, address: Optional[IOTBaseCommon.IOTNetResult], response: bytes, is_read: bool = True):
        if self.version == MitsubishiVersion.A_1E:
            if len(response) < 2:
                address.contents[9] = False
                address.contents[10] = f"Receive length is too short"
            else:
                if response[1] == 0x5b:
                    address.contents[9] = False
                    address.contents[10] = f"error: {response[2]}"
                elif response[1] == 0x00:
                    if is_read is True:
                        self._response_a_1e(address, response)
                    else:
                        address.contents[9] = True
                else:
                    address.contents[9] = False
                    address.contents[10] = f"error: {response[1]}"

        elif self.version == MitsubishiVersion.Qna_3E_ASCII:
            error = int(response[18:22].decode('ascii'), 16)
            if error != 0:
                address.contents[9] = False
                address.contents[10] = f"error: {error}"
            else:
                if is_read is True:
                    self._response_qna_3e_asicc(address, response)
                else:
                    address.contents[9] = True
        else:
            error = response[9] * 256 + response[10]
            if error != 0:
                address.contents[9] = False
                address.contents[10] = f"error: {error}"
            else:
                if is_read is True:
                    self._response_qna_3e(address, response)
                else:
                    address.contents[9] = True

    def _read(self, addresss: list):
        """基础的读取方法，外界不应该调用本方法"""
        for address in addresss:
            command = self.get_real_command(address)
            if command.is_success is False:
                return command

            read = self.read_server(command.contents[0])
            if read.is_success is False:
                return read

            self.analyse_response(address, read.contents[0])
        return IOTBaseCommon.IOTNetResult.create_success(addresss)

    def _write(self, addresss: list):
        """基础的写入数据的操作支持"""
        for address in addresss:
            command = self.get_write_command(address)
            if command.is_success is False:
                return command

            read = self.read_server(command.contents[0])
            if read.is_success is False:
                return read

            self.analyse_response(address, read.contents[0], False)
        return IOTBaseCommon.IOTNetResult.create_success(addresss)

    def _get_real_command_qna_3e(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        length = address.contents[5]
        if address.contents[6] is False:
            length = length // 2
        command = bytearray(21)
        command[0] = 0x50   # 副标题
        command[1] = 0x00  # 副头部
        command[2] = self.network  # 网络编号
        command[3] = 0xFF  # PLC编号
        command[4] = 0xFF   # 目标模块IO编号
        command[5] = 0x03  # IO编号
        command[6] = self.network_station  # 模块站号
        command[7] = (len(command) - 9) % 256   # 请求数据长度
        command[8] = (len(command) - 9) // 256  # 请求数据长度
        command[9] = 0x0A   # CPU监视定时器
        command[10] = 0x00  # 时钟
        command[11] = 0x01  # 批量读取数据命令
        command[12] = 0x04  # 指令（0x01 0x04读 0x01 0x14写）
        command[13] = 0x01 if address.contents[6] is True else 0x00  # 以点为单位还是字为单位成批读取（位 或 字节为单位）
        command[14] = 0x00
        command[15] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[0]  # 起始地址的地位
        command[16] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[1]
        command[17] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[2]
        command[18] = address.contents[3][0]  # 数据类型
        command[19] = length % 256
        command[20] = length // 256  # 长度
        return IOTBaseCommon.IOTNetResult.create_success([command])

    def _get_real_command_qna_3e_ascii(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        length = address.contents[5]
        if address.contents[6] is False:
            length = length // 2

        # 默认信息----注意：高低字节交错
        command = bytearray(42)
        command[0] = 0x35  # 副标题
        command[1] = 0x30
        command[2] = 0x30
        command[3] = 0x30
        command[4] = MitsubishiTools.build_bytes_from_data(self.network)[0]  # 网络号
        command[5] = MitsubishiTools.build_bytes_from_data(self.network)[1]
        command[6] = 0x46  # PLC编号
        command[7] = 0x46
        command[8] = 0x30  # 目标模块IO编号
        command[9] = 0x33
        command[10] = 0x46
        command[11] = 0x46
        command[12] = MitsubishiTools.build_bytes_from_data(self.network_station)[0]  # 目标模块站号
        command[13] = MitsubishiTools.build_bytes_from_data(self.network_station)[1]
        command[14] = 0x30  # 请求数据长度
        command[15] = 0x30
        command[16] = 0x31
        command[17] = 0x38
        command[18] = 0x30  # CPU监视定时器
        command[19] = 0x30
        command[20] = 0x31
        command[21] = 0x30
        command[22] = 0x30  # 批量读取数据命令
        command[23] = 0x34
        command[24] = 0x30
        command[25] = 0x31
        command[26] = 0x30  # 以点为单位还是字为单位成批读取
        command[27] = 0x30
        command[28] = 0x30
        command[29] = 0x31 if address.contents[6] else 0x30
        command[30] = address.contents[1].encode('ascii')[0]  # 软元件类型
        command[31] = address.contents[1].encode('ascii')[1]
        command[32:38] = MitsubishiTools.build_bytes_from_address(address.contents[2], address.contents[11])  # 起始地址的地位
        command[38:42] = MitsubishiTools.build_bytes_from_data(length, 4)  # 软元件点数
        return IOTBaseCommon.IOTNetResult.create_success([command])

    def _get_real_command_a_1e(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        length = address.contents[5]
        if address.contents[6] is False:
            length = length // 2
        command = bytearray(12)
        command[0] = 0x00 if address.contents[6] is True else 0x01   # 副头部
        command[1] = self.plc_number  # PLC编号
        command[2] = 0x0A   # CPU监视定时器（L）这里设置为0x00,0x0A，等待CPU返回的时间为10*250ms=2.5秒
        command[3] = 0x00  # CPU监视定时器（H）
        command[4] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[0]  # 起始地址的地位
        command[5] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[1]
        command[6] = 0x00
        command[7] = 0x00
        command[8] = address.contents[3][1]  # 软元件代码（L）
        command[9] = address.contents[3][0]  # 软元件代码（H）
        command[10] = length % 256
        command[11] = length // 256  # 长度
        return IOTBaseCommon.IOTNetResult.create_success([command])

    def _response_qna_3e(self, address: Optional[IOTBaseCommon.IOTNetResult], response: bytes):
        if address.contents[6] is True:
            # 位读取
            content = bytearray((len(response) - 11) * 2)
            i = 11
            while i < len(response):
                if (response[i] & 0x10) == 0x10:
                    content[(i - 11) * 2 + 0] = 0x01
                if (response[i] & 0x01) == 0x01:
                    content[(i - 11) * 2 + 1] = 0x01
                i = i + 1
            address.contents[8] = content
            address.contents[9] = True
        else:
            # 字读取
            content = bytearray(len(response) - 11)
            content[0:] = response[11:]
            address.contents[8] = IOTBaseCommon.DataTransform.convert_value(content, None, IOTBaseCommon.DataTransform.TypeFormat(address.contents[7]))[0]
            address.contents[9] = True

    def _response_qna_3e_asicc(self, address: Optional[IOTBaseCommon.IOTNetResult], response: bytes):
        if address.contents[6] is True:
            # 位读取
            content = bytearray(len(response) - 22)
            for i in range(22, len(response)):
                content[i - 22] = 0x00 if response[i] == 0x30 else 0x01
            address.contents[8] = content
            address.contents[9] = True
        else:
            # 字读取
            content = bytearray((len(response) - 22) // 2)
            for i in range(len(content) // 2):
                tmp = int(response[i * 4 + 22:i * 4 + 26].decode('ascii'), 16)
                content[i * 2:i * 2 + 2] = IOTBaseCommon.DataTransform.pack_value(tmp, '<H')
            address.contents[8] = IOTBaseCommon.DataTransform.convert_value(content, None, IOTBaseCommon.DataTransform.TypeFormat(address.contents[7]))[0]
            address.contents[9] = True

    def _response_a_1e(self, address: Optional[IOTBaseCommon.IOTNetResult], response: bytes):
        if address.contents[6] is True:
            # 位读取
            content = bytearray((len(response) - 2) * 2)
            i = 2
            while i < len(response):
                if (response[i] & 0x10) == 0x10:
                    content[(i - 2) * 2 + 0] = 0x01
                if (response[i] & 0x01) == 0x01:
                    content[(i - 2) * 2 + 1] = 0x01
                i = i + 1
            address.contents[8] = content
            address.contents[9] = True
        else:
            # 字读取
            content = response[2:]
            address.contents[8] = IOTBaseCommon.DataTransform.convert_value(content, None, IOTBaseCommon.DataTransform.TypeFormat(address.contents[7]))[0]
            address.contents[9] = True

    def _get_write_command_qna_3e(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        length = len(address.contents[8]) // 2
        if address.contents[6] is True:
            length = 1
        command = bytearray(21 + len(address.contents[8]))
        command[0] = 0x50  # 副标题
        command[1] = 0x00  # 副头部
        command[2] = self.network  # 网络编号
        command[3] = 0xFF  # PLC编号
        command[4] = 0xFF  # 目标模块IO编号
        command[5] = 0x03  # IO编号
        command[6] = self.network_station  # 模块站号
        command[7] = (len(command) - 9) % 256  # 请求数据长度
        command[8] = (len(command) - 9) // 256  # 请求数据长度
        command[9] = 0x0A  # CPU监视定时器
        command[10] = 0x00  # 时钟
        command[11] = 0x01  # 批量读取数据命令
        command[12] = 0x14  # 指令（0x01 0x04读 0x01 0x14写）
        command[13] = 0x01 if address.contents[6] is True else 0x00  # 子指令（位 或 字节为单位）
        command[14] = 0x00
        command[15] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[0]  # 起始地址的地位
        command[16] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[1]
        command[17] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[2]
        command[18] = address.contents[3][0]  # 数据类型
        command[19] = length % 256
        command[20] = length // 256  # 长度
        command[21: 21 + len(address.contents[8])] = address.contents[8]
        return IOTBaseCommon.IOTNetResult.create_success([command])

    def _get_write_command_a_1e(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        length = len(address.contents[8]) // 2
        if address.contents[6] is True:
            length = len(address.contents[8])

        command = bytearray(12 + len(address.contents[8]))
        command[0] = 0x02 if address.contents[6] is True else 0x03   # 副头部
        command[1] = self.plc_number  # PLC编号
        command[2] = 0x0A   # CPU监视定时器（L）这里设置为0x00,0x0A，等待CPU返回的时间为10*250ms=2.5秒
        command[3] = 0x00  # CPU监视定时器（H）
        command[4] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[0]  # 起始地址的地位
        command[5] = IOTBaseCommon.DataTransform.pack_value(address.contents[2], '<i')[1]
        command[6] = 0x00
        command[7] = 0x00
        command[8] = address.contents[3][1]  # 软元件代码（L）
        command[9] = address.contents[3][0]  # 软元件代码（H）
        command[10] = length % 256
        command[11] = length // 256  # 长度
        command[12: 12 + len(address.contents[8])] = address.contents[8]
        return IOTBaseCommon.IOTNetResult.create_success([command])

    def _get_write_command_qna_3e_ascii(self, address: Optional[IOTBaseCommon.IOTNetResult]):
        length = len(address.contents[8]) // 2
        if address.contents[6] is True:
            length = len(address.contents[8])

        # 默认信息----注意：高低字节交错
        command = bytearray(42 + len(address.contents[8]))
        command[0] = 0x35  # 副标题
        command[1] = 0x30
        command[2] = 0x30
        command[3] = 0x30
        command[4] = MitsubishiTools.build_bytes_from_data(self.network)[0]  # 网络号
        command[5] = MitsubishiTools.build_bytes_from_data(self.network)[1]
        command[6] = 0x46  # PLC编号
        command[7] = 0x46
        command[8] = 0x30  # 目标模块IO编号
        command[9] = 0x33
        command[10] = 0x46
        command[11] = 0x46
        command[12] = MitsubishiTools.build_bytes_from_data(self.network_station)[0]  # 目标模块站号
        command[13] = MitsubishiTools.build_bytes_from_data(self.network_station)[1]
        command[14] = MitsubishiTools.build_bytes_from_data(len(command)-18, 4)[0]  # 请求数据长度
        command[15] = MitsubishiTools.build_bytes_from_data(len(command)-18, 4)[1]
        command[16] = MitsubishiTools.build_bytes_from_data(len(command)-18, 4)[2]
        command[17] = MitsubishiTools.build_bytes_from_data(len(command)-18, 4)[3]
        command[18] = 0x30  # CPU监视定时器
        command[19] = 0x30
        command[20] = 0x31
        command[21] = 0x30
        command[22] = 0x31  # 批量读取数据命令
        command[23] = 0x34
        command[24] = 0x30
        command[25] = 0x31
        command[26] = 0x30  # 以点为单位还是字为单位成批读取
        command[27] = 0x30
        command[28] = 0x30
        command[29] = 0x31 if address.contents[6] else 0x30
        command[30] = address.contents[1].encode('ascii')[0]  # 软元件类型
        command[31] = address.contents[1].encode('ascii')[1]
        command[32:38] = MitsubishiTools.build_bytes_from_address(address.contents[2], address.contents[11])  # 起始地址的地位
        command[38:42] = MitsubishiTools.build_bytes_from_data(length, 4)  # 软元件点数
        command[42: 42 + len(address.contents[8])] = address.contents[8]
        return IOTBaseCommon.IOTNetResult.create_success([command])


class IOTPlcMitsubishi(IOTDriver):

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
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '2/192.168.1.184/6000', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '2/0.0.0.0/6000', 'enum': [], 'tip': ''})
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
        # version/ip/port
        info_list = device_address.split('/')
        return {'host': info_list[1] if len(info_list) > 1 else '', 'port': int(float(info_list[2])) if len(info_list) > 2 else 102, 'type': int(float(info_list[0])) if len(info_list) > 1 else 2}

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
            if 'type' in info.keys():
                client = MitsubishiClient(MitsubishiVersion(info['type']), info['host'], info['port'], self.configs.get('timeout'))
                client.logging(call_logging=self.logging)
                result = client.connect()
                if result.is_success is True and client.get_connected() is True:
                    self.clients[address] = client
                else:
                    raise Exception(f"{result.msg}")
        return self.clients.get(address)

    def _send_read_cmd(self, address: str, mitsubishi_list: list):
        try:
            if self._get_client(address) is not None and len(mitsubishi_list) > 0:
                result = self._get_client(address).read(mitsubishi_list)
                if isinstance(result, IOTBaseCommon.IOTNetResult):
                    if result.is_success is True:
                        for item in result.contents:
                            if isinstance(item, IOTBaseCommon.IOTNetResult):
                                if item.is_success:
                                    if item.contents[9] is True:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[7]}", **self.gen_read_write_result(True, item.contents[8]))
                                    else:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[7]}", **self.gen_read_write_result(False, item.contents[10]))
                                else:
                                    self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[7]}", **self.gen_read_write_result(False, item.msg))
                    else:
                        raise Exception(f"{result.msg}")
        except Exception as e:
            for (ad, type) in mitsubishi_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__()))

    def _read_address(self, *args, **kwargs) -> dict:
        start = time.time()
        (address, mitsubishis) = args
        results = {}
        units = IOTBaseCommon.chunk_list(mitsubishis, self.configs.get('multi_read'))
        for unit in units:
            self._send_read_cmd(address, unit)
            self.delay(self.configs.get('cmd_interval', 0.3))
        self.logging(content=f"plc({address}) read: {len(mitsubishis)} response: {results} group: {len(units)} cost: {'{:.2f}'.format(time.time() - start)}", pos=self.stack_pos)
        return results

    def _read(self, read_items: dict):
        if len(read_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(read_items), f"{self}")
            for address, mitsubishis in read_items.items():
                jobs.submit_task(self._read_address, address, mitsubishis)
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

    def _send_write_cmd(self, address: str, mitsubishi_list: list):
        try:
            if self._get_client(address) is not None and len(mitsubishi_list) > 0:
                result = self._get_client(address).write(mitsubishi_list)
                if isinstance(result, IOTBaseCommon.IOTNetResult):
                    if result.is_success is True:
                        for item in result.contents:
                            if isinstance(item, IOTBaseCommon.IOTNetResult):
                                if item.is_success:
                                    if item.contents[9] is True:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[7]}",  **self.gen_read_write_result(True, item.contents[9], False))
                                    else:
                                        self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[7]}",  **self.gen_read_write_result(False, item.contents[10], False))
                                else:
                                    self.update_device(f"{address}", f"{item.contents[0]}_{item.contents[7]}",  **self.gen_read_write_result(False, item.msg, False))
                    else:
                        raise Exception(f"{result.msg}")
        except Exception as e:
            for (ad, type, value) in mitsubishi_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__(), False))

    def _write_address(self, *args, **kwargs) -> dict:
        (address, mitsubishis) = args
        results = {}
        units = IOTBaseCommon.chunk_list(mitsubishis, self.configs.get('multi_read'))
        for unit in units:
            self._send_write_cmd(address, unit)
            self.delay(self.configs.get('cmd_interval', 0.3))
        return results

    def _write(self, write_items: dict):
        if len(write_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(write_items), f"{self}")
            for address, mitsubishis in write_items.items():
                jobs.submit_task(self._write_address, address, mitsubishis)
            return jobs.done()
        return {}

    def _release_server(self, address: str):
        try:
            pass
        except:
            pass

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_plc_mitsubishi.py({pos})"
