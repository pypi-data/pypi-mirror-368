import time

from typing import List, Dict, Any, Union, Optional

from .base import IOTBaseCommon, IOTDriver

"""
https://flat2010.github.io/2020/02/23/Omron-Fins%E5%8D%8F%E8%AE%AE/

FINS(Factory Interface Network Service)协议

地址
    DM区  D100
    CIO区 C100
    WR区 W100
    HR区 H100
    AR区 A100
"""


class OmronFinsMessage(IOTBaseCommon.IOTNetMessage):
    """用于欧姆龙通信的Fins协议的消息解析规则"""

    def get_head_length(self) -> int:
        """协议头数据长度，也即是第一次接收的数据长度"""
        return 8

    def get_content_length(self) -> int:
        """二次接收的数据长度"""
        if self.heads is not None:
            return IOTBaseCommon.DataTransform.unpack_bytes(self.heads[4:8], '>i')
        else:
            return 0

    def check_response(self) -> bool:
        """回复报文校验"""
        if self.heads is not None:
            if self.heads[0: 4] == bytes.fromhex('46 49 4E 53'):
                return True
            else:
                return False
        else:
            return False


# 初始化指令交互报文
class OmronFinsConstant:
    basic_cmd = bytearray([0x46, 0x49, 0x4E, 0x53,    # Magic字段  0x46494E53 对应的ASCII码，即FINS
                           0x00, 0x00, 0x00, 0x0C,    # Length字段 表示其后所有字段的总长度
                           0x00, 0x00, 0x00, 0x00,    # Command字段
                           0x00, 0x00, 0x00, 0x00,    # Error Code字段
                           0x00, 0x00, 0x00, 0x0B     # Client/Server Node Address字段
                           ])


# 基础方法
class OmronFinsTools:

    @staticmethod
    def parse_address(address: str, type: int):
        """解析数据地址"""
        result = IOTBaseCommon.IOTNetResult()
        try:
            # 0: address 1:area 2:start 3: bit_code 4: is_bit 5 bit_addres 6: word_code 7:type 8:value 9: result 10: msg
            result.contents[0] = address
            result.contents[1] = address[0:1]
            result.contents[7] = type

            if address[0].upper() == 'D':   # DM区
                result.contents[3] = 0x02
                result.contents[6] = 0x82
            elif address[0].upper() == 'C':  # CIO区
                result.contents[3] = 0x30
                result.contents[6] = 0xB0
            elif address[0].upper() == 'W':  # WR区
                result.contents[3] = 0x31
                result.contents[6] = 0xB1
            elif address[0].upper() == 'H':  # HR区
                result.contents[3] = 0x32
                result.contents[6] = 0xB2
            elif address[0].upper() == 'A':  # AR区
                result.contents[3] = 0x33
                result.contents[6] = 0xB3
            elif address[0].upper() == 'E':
                # E区，比较复杂，需要专门的计算
                block = int(address.split(".")[0][1:], 16)
                if block < 16:
                    result.contents[3] = 0x20 + block
                    result.contents[6] = 0xA0 + block
                else:
                    result.contents[3] = 0xE0 + block - 16
                    result.contents[6] = 0x60 + block - 16
            else:
                raise Exception(f"unsupport type({address})")

            if address[0].upper() == 'E':
                splits = address.split(".")
                result.contents[4] = True if len(splits) > 2 else False

                if result.contents[4] is True:
                    # 位操作
                    addr = int(splits[1])
                    result.contents[5] = bytearray(3)
                    result.contents[5][0] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[1]
                    result.contents[5][1] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[0]
                    result.contents[5][2] = int(splits[2])
                    if result.contents[5][2] > 15:
                        return IOTBaseCommon.IOTNetResult(msg=f"The bit address entered can only be between 0-15")
                else:
                    # 字操作
                    addr = int(splits[1])
                    result.contents[5] = bytearray(3)
                    result.contents[5][0] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[1]
                    result.contents[5][1] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[0]
            else:
                splits = address[1:].split(".")
                result.contents[4] = True if len(splits) > 1 else False

                if result.contents[4] is True:
                    # 位操作
                    addr = int(splits[0])
                    result.contents[5] = bytearray(3)
                    result.contents[5][0] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[1]
                    result.contents[5][1] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[0]
                    result.contents[5][2] = int(splits[1])
                    if result.contents[5][2] > 15:
                        return IOTBaseCommon.IOTNetResult(msg=f"The bit address entered can only be between 0-15")
                else:
                    # 字操作
                    addr = int(address[1:])
                    result.contents[2] = addr
                    result.contents[5] = bytearray(3)
                    result.contents[5][0] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[1]
                    result.contents[5][1] = IOTBaseCommon.DataTransform.pack_value(addr, '<i')[0]
            result.is_success = True
            return result

        except Exception as e:
            result.msg = e.__str__()
            return result

    @staticmethod
    def get_real_command(address: Optional[IOTBaseCommon.IOTNetResult] = None):
        """生成一个读取字数据指令头的通用方法"""
        if address is None:
            raise Exception(f"address is empty")

        length, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(IOTBaseCommon.DataTransform.TypeFormat(address.contents[7]))

        command = bytearray(8)
        command[0] = 0x01
        command[1] = 0x01  # 命令码 0101读 0102写
        command[2] = address.contents[3] if address.contents[4] else address.contents[6]   # 存储区代码
        command[3:3 + len(address.contents[5])] = address.contents[5]  # 数据起始地址
        command[6] = length // 256  # 读取长度
        command[7] = length % 256

        return IOTBaseCommon.IOTNetResult.create_success([command])

    @staticmethod
    def get_write_command(address: Optional[IOTBaseCommon.IOTNetResult] = None):
        if address is None:
            raise Exception(f"address is empty")

        length, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(
            IOTBaseCommon.DataTransform.TypeFormat(address.contents[7]))

        command = bytearray(8 + len(address.contents[8]))
        command[0] = 0x01
        command[1] = 0x02  # Memory Area Read 内存区域写
        command[2] = address.contents[3] if address.contents[4] else address.contents[6]  # Memory Area Code
        command[3:3 + len(address.contents[5])] = address.contents[5]  # Beginning address
        if address.contents[4] is True:
            command[6] = length // 256
            command[7] = length % 256
        else:
            command[6] = length // 2 // 256
            command[7] = length // 2 % 256

        command[8:] = address.contents[8]
        return IOTBaseCommon.IOTNetResult.create_success([command])

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
    def check_response(response: Optional[Union[bytearray, bytes]], is_read: bool):
        # 数据有效性分析
        if len(response) >= 16:

            # 检查返回的状态
            buffer = response[12:16]
            buffer.reverse()
            status = IOTBaseCommon.DataTransform.unpack_bytes(buffer, '<i')
            if status != 0:
                return IOTBaseCommon.IOTNetResult(code=status, msg=OmronFinsTools.get_status_description(status))

            if len(response) >= 30:
                # 01 01 00 00
                status = response[28] * 256 + response[29]  # 结束码 00 00
                if status > 0:
                    return IOTBaseCommon.IOTNetResult(code=status, msg="Data Receive exception")

                if is_read is False:
                    return IOTBaseCommon.IOTNetResult.create_success([bytearray(0)])

                # 返回读取的数据
                content = bytearray(len(response) - 30)
                if len(content) > 0:
                    content[0:len(content)] = response[30:]
                return IOTBaseCommon.IOTNetResult.create_success([content])

        return IOTBaseCommon.IOTNetResult(msg="Data Receive exception")


class OmronFinsClient(IOTBaseCommon.IOTNetworkDeviceClient):

    def __init__(self, host: str, port: int, sa1: int = 0x0B, timeout: int = 10):
        super().__init__(host, port, timeout)

        self.sa1 = sa1  # SA1 客户端节点编号
        self.da1 = 0x01  # DA1 服务器节点编号
        """
                DA2(即Destination unit address，目标单元地址)
                0x00：PC(CPU)
                0xFE： SYSMAC NET Link Unit or SYSMAC LINK Unit connected to network；
                0x10~0x1F：CPU总线单元 ，其值等于10 + 单元号(前端面板中配置的单元号)
                """
        self.dest_address = 0x0  # (即Destination unit address，目标单元地址)

    def get_net_msg(self):
        return OmronFinsMessage()

    def initialization_on_connect(self, socket):
        """在连接上欧姆龙PLC后，需要进行一步握手协议"""
        cmd = OmronFinsConstant.basic_cmd
        cmd[19] = self.sa1

        # 握手信号
        read = self.read_from_socket(socket, cmd)
        if read.is_success is False:
            return read

        # 检查返回的状态
        buffer = read.contents[0][12:16]
        buffer.reverse()
        status = IOTBaseCommon.DataTransform.unpack_bytes(buffer, '<i')
        if status != 0:
            return IOTBaseCommon.IOTNetResult(code=status, msg=OmronFinsTools.get_status_description(status))

        # 提取PLC及上位机的节点地址
        if len(read.contents[0]) >= 20:
            self.sa1 = read.contents[0][19]
        if len(read.contents[0]) >= 24:
            self.da1 = read.contents[0][23]

        # 返回成功的信号
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_disconnect(self, socket):
        return IOTBaseCommon.IOTNetResult.create_success()

    def read(self, address: Union[tuple, list]):
        """从PLC读取数据，地址格式为I100，Q100，DB20.100，M100，T100，C100以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type) in address:
                tmp = OmronFinsTools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                results.append(tmp)
            return self._read(results)
        elif isinstance(address, tuple):
            result = OmronFinsTools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            return self._read([result])

    def write(self, address: Union[tuple, list]):
        """将数据写入到PLC数据，地址格式为I100，Q100，DB20.100，M100，以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type, value) in address:
                tmp = OmronFinsTools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                tmp.contents[8] = IOTBaseCommon.DataTransform.convert_value(value, IOTBaseCommon.DataTransform.TypeFormat(type), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.BADC)
                results.append(tmp)
            return self._write(results)
        elif isinstance(address, tuple):
            result = OmronFinsTools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            result.contents[8] = IOTBaseCommon.DataTransform.convert_value(address[2], IOTBaseCommon.DataTransform.TypeFormat(address[1]), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.BADC)
            return self._write([result])

    def ping(self):
        return self.get_socket().is_success

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
            valid = OmronFinsTools.check_response(read.contents[0], True)
            if valid.is_success is False:
                address.contents[9] = False
                address.contents[10] = valid.msg
                continue

            length, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(IOTBaseCommon.DataTransform.TypeFormat(address.contents[7]))
            response_data = bytearray(length)
            response_data[0: length] = valid.contents[0][0: length]
            address.contents[9] = True
            address.contents[8] = IOTBaseCommon.DataTransform.convert_value(response_data, IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, IOTBaseCommon.DataTransform.TypeFormat(address.contents[7]), format=IOTBaseCommon.DataTransform.DataFormat.BADC, pos=0)

        return IOTBaseCommon.IOTNetResult.create_success(addresss)

    def _write(self, addresss: list):
        """基础的写入数据的操作支持"""
        for address in addresss:
            command = self.get_command(address, is_read=False)
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
            valid = OmronFinsTools.check_response(read.contents[0], False)
            if valid.is_success is False:
                address.contents[9] = False
                address.contents[10] = valid.msg
                continue

            address.contents[9] = True
        return IOTBaseCommon.IOTNetResult.create_success(addresss)

    def _pack_command(self, cmd: bytes):
        command = bytearray(26 + len(cmd))
        command[0:4] = OmronFinsConstant.basic_cmd[0:4]
        command[4:8] = IOTBaseCommon.DataTransform.pack_value(len(command) - 8, '>i')  # 长度
        command[11] = 0x02

        command[16] = 0x80  # ICF 信息控制字段
        command[17] = 0x00  # RSV 保留字段
        command[18] = 0x02  # GCT 网关计数
        command[19] = 0x00  # DNA 目标网络地址 00:表示本地网络  0x01~0x7F:表示远程网络
        command[20] = self.da1  # DA1 目标节点编号 0x01~0x3E:SYSMAC LINK网络中的节点号 0x01~0x7E:YSMAC NET网络中的节点号 0xFF:广播传输
        command[21] = self.dest_address  # DA2 目标单元地址
        command[22] = 0x00  # SNA 源网络地址 取值及含义同DNA字段
        command[23] = self.sa1  # SA1 源节点编号 取值及含义同DA1字段
        command[24] = 0x00  # SA2 源单元地址 取值及含义同DA2字段
        command[25] = 0x00  # SID Service ID 取值0x00~0xFF，产生会话的进程的唯一标识

        command[26:] = cmd
        return IOTBaseCommon.IOTNetResult.create_success([command])

    def get_command(self, address: Optional[IOTBaseCommon.IOTNetResult] = None, is_read: bool = True):
        """生成一个读取字数据指令头的通用方法"""
        command = OmronFinsTools.get_real_command(address) if is_read else OmronFinsTools.get_write_command(address)
        if command.is_success is False:
            return command

        return self._pack_command(command.contents[0])


class OmronFinsServer(IOTBaseCommon.IOTNetworkDeviceServer):

    def __init__(self, host: str, port: int, sa1: int = 0x0B, timeout: int = 10):
        super().__init__(host, port, timeout)
        self.sa1 = sa1  # SA1 客户端节点编号
        self.da1 = 0x01  # DA1 服务器节点编号
        """
                DA2(即Destination unit address，目标单元地址)
                0x00：PC(CPU)
                0xFE： SYSMAC NET Link Unit or SYSMAC LINK Unit connected to network；
                0x10~0x1F：CPU总线单元 ，其值等于10 + 单元号(前端面板中配置的单元号)
                """
        self.dest_address = 0x0  # (即Destination unit address，目标单元地址)
        self.word_length = 2

    def get_net_msg(self):
        return OmronFinsMessage()

    def initialization_on_connect(self, socket):
        # 返回成功的信号
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_disconnect(self, socket):
        return IOTBaseCommon.IOTNetResult.create_success()

    def extra_on_receive(self, socket, datas: bytes):
        if len(datas) >= 20 and IOTBaseCommon.DataTransform.compare_bytes(bytearray(datas), OmronFinsConstant.basic_cmd, 16):
            self.send(socket, bytes.fromhex('46 49 4E 53 00 00 00 10 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01'))
        else:
            self._analyze_data(datas, socket)

    def simulate(self, address: Union[tuple, list]):
        """将数据写入到PLC数据，地址格式为I100，Q100，DB20.100，M100，以字节为单位"""
        if isinstance(address, list):
            results = []
            for (adr, type, value) in address:
                tmp = OmronFinsTools.parse_address(adr, type)
                if tmp.is_success is False:
                    return IOTBaseCommon.IOTNetResult.create_fail(tmp)
                tmp.contents[8] = IOTBaseCommon.DataTransform.convert_value(value, IOTBaseCommon.DataTransform.TypeFormat(type), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.BADC)
                results.append(tmp)
            return self._simulate(results)
        elif isinstance(address, tuple):
            result = OmronFinsTools.parse_address(address[0], address[1])
            if result.is_success is False:
                return IOTBaseCommon.IOTNetResult.create_fail(result)
            result.contents[8] = IOTBaseCommon.DataTransform.convert_value(address[2], IOTBaseCommon.DataTransform.TypeFormat(address[1]), IOTBaseCommon.DataTransform.TypeFormat.BYTE_ARRAY, format=IOTBaseCommon.DataTransform.DataFormat.BADC)
            return self._simulate([result])

    def _pack_command(self, cmd: bytes):
        command = bytearray(26 + len(cmd))
        command[0:4] = OmronFinsConstant.basic_cmd[0:4]
        command[4:8] = IOTBaseCommon.DataTransform.pack_value(len(command) - 8, '>i')  # 长度
        command[11] = 0x02

        command[16] = 0x80  # ICF 信息控制字段
        command[17] = 0x00  # RSV 保留字段
        command[18] = 0x02  # GCT 网关计数
        command[19] = 0x00  # DNA 目标网络地址 00:表示本地网络  0x01~0x7F:表示远程网络
        command[20] = self.da1  # DA1 目标节点编号 0x01~0x3E:SYSMAC LINK网络中的节点号 0x01~0x7E:YSMAC NET网络中的节点号 0xFF:广播传输
        command[21] = self.dest_address  # DA2 目标单元地址
        command[22] = 0x00  # SNA 源网络地址 取值及含义同DNA字段
        command[23] = self.sa1  # SA1 源节点编号 取值及含义同DA1字段
        command[24] = 0x00  # SA2 源单元地址 取值及含义同DA2字段
        command[25] = 0x00  # SID Service ID 取值0x00~0xFF，产生会话的进程的唯一标识

        command[26:] = cmd
        return IOTBaseCommon.IOTNetResult.create_success([command])

    def _simulate(self, addresss: list):
        """基础的写入数据的操作支持"""
        for address in addresss:
            command = OmronFinsTools.get_write_command(address)
            if command.is_success is True:
                command = self._pack_command(command.contents[0])
                if command.is_success is True:
                    self._analyze_data(command.contents[0])

    def _analyze_data(self, datas: bytes, socket=None):
        if len(datas) > 21:
            is_bit = datas[28] == 0x02 or datas[28] == 0x30 or datas[28] == 0x31 or datas[28] == 0x32 or datas[28] == 0x33
            address_lenght = 1 if is_bit else 2
            read_write_length = datas[32] * 256 + datas[33]     # 读写数据长度
            data_key = f"omron-{datas[28]}"
            if data_key not in self.values.keys():
                self.values[data_key] = bytearray(65536)
            begin_address = datas[30] + datas[29] * 256
            bit_address = datas[31]
            if datas[27] == 0x01:  # 读
                db_byte_array = self.values.get(data_key)
                data_lenght = read_write_length * address_lenght    # 数据的字节长度
                response_data = bytearray(30 + data_lenght)
                response_data[0:30] = bytes.fromhex('46 49 4E 53 00 00 00 1A 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')         
                response_data[4:8] = IOTBaseCommon.DataTransform.convert_values_to_bytes(22 + data_lenght, IOTBaseCommon.DataTransform.TypeFormat.INT32, little_endian=False)

                if is_bit is True:
                    response_data[30: 30 + data_lenght] = db_byte_array[begin_address * 16 + bit_address: begin_address * 16 + bit_address + data_lenght]
                else:
                    response_data[30: 30 + data_lenght] = db_byte_array[begin_address * address_lenght: begin_address * address_lenght + data_lenght]
                if socket:
                    self.send(socket, response_data)
            elif datas[27] == 0x02:  # 写
                db_byte_array = self.values.get(data_key)
                value_byte = bytearray(len(datas) - 34)
                value_byte[0:] = datas[34: 34 + len(value_byte)]
                if is_bit is True:
                    db_byte_array[begin_address * 16 + bit_address: begin_address * 16 + bit_address + len(value_byte)] = value_byte
                else:
                    db_byte_array[begin_address * address_lenght: begin_address * address_lenght + len(value_byte)] = value_byte
                self.values[data_key] = db_byte_array
                if socket:
                    self.send(socket, bytes.fromhex('46 49 4E 53 00 00 00 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'))


class IOTPlcOmronFins(IOTDriver):

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
            templates.extend([{'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                              {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''}])
            if mode == 0:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '192.168.1.184/9600/11', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': '设备地址' if lan == 'ch' else 'device address'.upper(), 'code': 'point_device_address', 'type': 'string', 'default': '0.0.0.0/9600/11', 'enum': [], 'tip': ''})
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

    def _gen_key(self, area, db: int, start: int, length: int) -> str:
        return f"{area}_{db}_{start}_{length}"

    def _get_address_info(self, device_address: str) -> dict:
        # ip/port/sa1
        info_list = device_address.split('/')
        return {'host': info_list[0] if len(info_list) > 1 else '', 'port': int(float(info_list[1])) if len(info_list) > 2 else 9600, 'sa1': int(float(info_list[2])) if len(info_list) > 3 else 11}

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
            if len(info) > 0:
                client = OmronFinsClient(info['host'], info['port'], info['sa1'], self.configs.get('timeout'))
                client.logging(call_logging=self.logging)
                result = client.connect()
                if result.is_success is True and client.get_connected() is True:
                    self.clients[address] = client
                else:
                    raise Exception(f"{result.msg}")
        return self.clients.get(address)

    def _send_read_cmd(self, address: str, omron_item_list: list):
        try:
            if self._get_client(address) is not None and len(omron_item_list) > 0:
                result = self._get_client(address).read(omron_item_list)
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
            for (ad, type) in omron_item_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__()))

    def _read_address(self, *args, **kwargs) -> dict:
        start = time.time()
        (address, omron_items) = args
        results = {}
        units = IOTBaseCommon.chunk_list(omron_items, self.configs.get('multi_read'))
        for unit in units:
            self._send_read_cmd(address, unit)
            self.delay(self.configs.get('cmd_interval', 0.3))
        self.logging(content=f"plc({address}) read: {len(omron_items)} response: {results} group: {len(units)} cost: {'{:.2f}'.format(time.time() - start)}", pos=self.stack_pos)
        return results

    def _read(self, read_items: dict):
        if len(read_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(read_items), f"{self}")
            for address, omron_items in read_items.items():
                jobs.submit_task(self._read_address, address, omron_items)
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

    def _send_write_cmd(self, address: str, omron_item_list: list):
        try:
            if self._get_client(address) is not None and len(omron_item_list) > 0:
                result = self._get_client(address).write(omron_item_list)
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
            for (ad, type, value) in omron_item_list:
                self.update_device(f"{address}", f"{ad}_{type}", **self.gen_read_write_result(False, e.__str__(), False))

    def _write_address(self, *args, **kwargs) -> dict:
        (address, omron_items) = args
        results = {}
        units = IOTBaseCommon.chunk_list(omron_items, self.configs.get('multi_read'))
        for unit in units:
            self._send_write_cmd(address, unit)
            self.delay(self.configs.get('cmd_interval', 0.3))
        return results

    def _write(self, write_items: dict):
        if len(write_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(write_items), f"{self}")
            for address, omron_items in write_items.items():
                jobs.submit_task(self._write_address, address, omron_items)
            return jobs.done()
        return {}

    def _get_server(self, address: str):
        server = self.servers.get(address, {}).get('server')
        if server is None:
            info = self._get_address_info(address)
            if len(info) > 0:
                server = OmronFinsServer(info['host'], info['port'], info['sa1'])
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
        return f"iot_plc_omron.py({pos})"
