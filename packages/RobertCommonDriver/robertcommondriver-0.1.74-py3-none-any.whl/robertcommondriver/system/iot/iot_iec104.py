from construct import Padding, BitStruct, Bit, Bits, Flag, Struct, ULInt32, ULInt16, EmbeddedBitStruct, Embed, ExprAdapter, Nibble, Container, If, BitField, LFloat32, Magic, Byte, Array, Switch, Pass
from enum import IntEnum
from datetime import timedelta, datetime
from collections import deque
from scapy.fields import ByteEnumField, ConditionalField, Field, PacketField, LEShortField, ShortField, XByteField, ByteField, PacketListField
from scapy.packet import Packet, Padding as pack_padding, NoPayload
from struct import unpack, pack
from typing import List, Dict, Any, Optional, Union
from threading import Lock

from .base import IOTBaseCommon, IOTDriver


'''
pip install scapy==2.4.5
'''

"""
ACPI
    68(1)
    长度(1)
    控制域(4)
        I帧
            发送序号， 接收序号
        S帧
            01 00 接收序号
        U帧
            0x 00 00 00
ASDU
    类型(1)
        监视方向
            1 单点遥信（带品质 不带时标）
            2 双点遥信
            13 段浮点遥测（带品质 不带时标）
        控制方向
            45 单点遥控
        监视方向系统类型
            70 初始化结束
        控制方向系统类型
            100 总召
            101 累积量召唤
            102 读命令
            103 时钟同步
    限定词(1)
        SQ = 0 地址连续 SQ=1地址不连续
    传送原因(2)
        PN
            6 激活
            7 激活确认
            8 停止激活
    地址(2)
    (信息体)(长度-10)
        连续信息传输型
            带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 信息体数据 品质描述词(1字节) 绝对时标(7字节)
            不带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 信息体数据 品质描述词(1字节)
            带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 信息体数据(1字节) 绝对时标(7字节)
            不带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 信息体数据(1字节)
        非连续信息传输型
            带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 地址编号(3字节) 信息体数据 品质描述词(1字节) 绝对时标(7字节)
            不带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 地址编号(3字节) 信息体数据 品质描述词(1字节)
            带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 地址编号(3字节) 信息体数据(1字节) 绝对时标(7字节)
            不带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 地址编号(3字节) 信息体数据(1字节)
                
        遥控和设定值
            单点遥控(1字节)   (S/E QU[6:2] RES SCS)
                S/E = 0 遥控执行命令；S/E=1 遥控选择命令；
                QU = 0 被控占内部确定遥控输出方式，不有控制站选择；
                    1 短脉冲方式输出
                    2 长脉冲方式输出
                    3 持续脉冲方式输出
                其他值没有定义
                RES ：保留位
                SCS ： 设置值； 0 = 控开 ；1 = 控合 
            双点遥控(1字节)   (S/E QU[6:2] DCS)
                S/E = 0 遥控执行命令；S/E=1 遥控选择命令；
                QU = 0 被控占内部确定遥控输出方式，不有控制站选择；
                    1 短脉冲方式输出
                    2 长脉冲方式输出
                    3 持续脉冲方式输出
                DCS； 0 无效控制
                    1 控分
                    2 控合
                    3 无效控制
            设定值QOS
            
    遥信：1H-4000H（512）
    遥测：4001H-5000H，首地址：16385（256）
    遥控：6001H-6100H，首地址：24577（128）
    设点：6201H-6400H
    电度：6401H-6600H
    
过程描述
    建立tcp连接；
    主站给从站发送启动帧；报文：68 04 07 00 00 00
    从站收到启动帧，给主站发送启动确认帧；报文：68 04 0B 00 00 00
    主站给从站发送总召唤；报文：68 0E 00 00 00 00 64 01 06 00 01 00 00 00 00 14
    从站收到主站的总召唤命令，给主站发送总召唤确认；
    报文：68 0E 00 00 02 00 64 01 07 00 01 00 00 00 00 14
    从站上传遥信，遥测，电度等I帧信息帧，发送完毕从站发送总召唤结束帧；
    主站收到从站发送的结束帧，会回复一个S帧的确认帧；
    进入下一个周期（其中如何数据有变化，从站需要主动上报）
"""


class IECDefine:

    # 显示类型
    ASDU_DISPLAY = 0    # 0 原值 1 英文 2 中文

    @staticmethod
    def convert_dispay(maps: dict, value: Any, type: int = 1):
        """转换显示"""
        if type == 1:
            if isinstance(maps, dict):
                values = maps.get(value, ['', ''])
                if isinstance(values, list):
                    if len(values) >= 2:
                        return values[0]
                else:
                    return values
        elif type == 2:
            if isinstance(maps, dict):
                values = maps.get(value, ['', ''])
                if isinstance(values, list):
                    if len(values) >= 2:
                        return values[1]
                else:
                    return values
        return value

    # 类型标识(1字节)
    ASDU_TYPE = {
        0x01:  'M_SP_NA_1',    #单点遥信(带品质描述 不带时标)
        0x03:  'M_DP_NA_1',    #双点遥信(带品质描述 不带时标)
        0x05:  'M_ST_NA_1',    #步位置信息(带品质描述 不带时标)
        0x07:  'M_BO_NA_1',    #32比特串(带品质描述 不带时标)
        0x09:  'M_ME_NA_1',    #规一化遥测值(带品质描述 不带时标)
        0x0B:  'M_ME_NB_1',    #标度化遥测值(带品质描述 不带时标)
        0x0D:  'M_ME_NC_1',    #短浮点遥测值(带品质描述 不带时标)
        0x0F:  'M_IT_NA_1',    #累积量(带品质描述 不带时标)
        0x14:  'M_PS_NA_1',    #成组单点遥信(只带变量标志)
        0x15:  'M_ME_ND_1',    #规一化遥测值(不带品质描述 不带时标)
        0x1E:  'M_SP_TB_1',    #单点遥信(带品质描述 带绝对时标)
        0x1F:  'M_DP_TB_1',    #双点遥信(带品质描述 带绝对时标)
        0x20:  'M_ST_TB_1',    #步位置信息(带品质描述 带绝对时标)
        0x21:  'M_BO_TB_1',    #32比特串(带品质描述 带绝对时标)
        0x22:  'M_ME_TD_1',    #规一化遥测值(带品质描述 带绝对时标)
        0x23:  'M_ME_TE_1',    #标度化遥测值(带品质描述 带绝对时标)
        0x24:  'M_ME_TF_1',    #短浮点遥测值(带品质描述 带绝对时标)
        0x25:  'M_IT_TB_1',    #累积量(带品质描述 带绝对时标)
        0x26:  'M_EP_TD_1',    #继电保护装置事件(带品质描述 带绝对时标)
        0x27:  'M_EP_TE_1',    #继电保护装置成组启动事件(带品质描述 带绝对时标)
        0x28:  'M_EP_TF_1',    #继电保护装置成组出口信息(带品质描述 带绝对时标)
        0x2D:  'C_SC_NA_1',    #单点遥控(一个报文只有一个遥控信息体 不带时标)
        0x2E:  'C_DC_NA_1',    #双点遥控(一个报文只有一个遥控信息体 不带时标)
        0x2F:  'C_RC_NA_1',    #升降遥控(一个报文只有一个遥控信息体 不带时标)
        0x30:  'C_SE_NA_1',    #规一化设定值(一个报文只有一个设定值 不带时标)
        0x31:  'C_SE_NB_1',    #标度化设定值(一个报文只有一个设定值 不带时标)
        0x32:  'C_SE_NC_1',    #短浮点设定值(一个报文只有一个设定值 不带时标)
        0x33:  'C_SE_ND_1',    #32比特串(一个报文只有一个设定值 不带时标)
        0x3A:  'C_SE_TA_1',    #单点遥控(一个报文只有一个设定值 带时标)
        0x3B:  'C_SE_TB_1',    #双点遥控(一个报文只有一个设定值 带时标)
        0x3C:  'C_SE_TC_1',    #升降遥控(一个报文只有一个设定值 带时标)
        0x3D:  'C_SE_TD_1',    #规一化设定值(一个报文只有一个设定值 带时标)
        0x3E:  'C_SE_TE_1',    #标度化设定值(一个报文只有一个设定值 带时标)
        0x3F:  'C_SE_TF_1',    #短浮点设定值(一个报文只有一个设定值 带时标)
        0x40:  'C_SE_TG_1',    #32比特串(一个报文只有一个设定值 带时标)
        0x46:  'M_EI_NA_1',    #初始化结束(从站发送，主站收到时候会做一次总召)
        0x64:  'C_IC_NA_1',    #总召
        0x65:  'C_CI_NA_1',    #累积量召唤
        0x66:  'C_RD_NA_1',    #读命令
        0x67:  'C_CS_NA_1',    #时钟同步命令
        0x69:  'C_RS_NA_1',    #复位进程命令
        0x6B:  'C_TS_NA_1',    #带时标的测试命令
        0x88:  'C_SE_NE_1',    #规一化设定值(一个报文可以包含多个设定值 不带时标)
    }

    # 帧类型
    APCI_TYPE = {
        0x00: 'I',
        0x01: 'S',
        0x03: 'U'
    }

    # U帧类型
    APCI_U_TYPE = {
        0x01: 'STARTDT act',    # U帧-激活传输启动
        0x02: 'STARTDT con',    # U帧-确认激活传输启动
        0x04: 'STOPDT act',     # U帧-停止传输
        0x08: 'STOPDT con',     # U帧-停止确认
        0x10: 'TESTFR act',     # U帧-测试询问帧
        0x20: 'TESTFR con',     # U帧-测试询确认
    }

    # 可变结构限定词(1字节)
    ASDU_SQ = {
        0X00: 0,
        0x80: 1  # 信息对象的地址连续 总召唤时，为了压缩信息传输时间SQ=
    }

    # 传送原因(2字节)
    ASDU_CAUSE = {
        0: 'not used',
        1: 'per/cyc',  # 周期 循环
        2: 'back',  # 背景扫描
        3: 'spont',  # 突发
        4: 'init',  # 初始化
        5: 'req',  # 请求或被请求
        6: 'act',  # 激活
        7: 'act config',  # 激活确认
        8: 'deact',  # 停止激活
        9: 'deact config',  # 停止激活确认
        10: 'act term',  # 激活终止
        11: 'retrem',  # 远方命令引起的返送信息
        12: 'retloc',  # 当地命令引起的返送信息
        13: 'file',
        20: 'inrogen',  # 响应站召唤
        21: 'inro1',  # 响应第1组召唤
        22: 'inro2',  # 响应第2组召唤
        23: 'inro3',
        24: 'inro4',
        25: 'inro5',
        26: 'inro6',
        27: 'inro7',
        28: 'inro8',
        29: 'inro9',
        30: 'inro10',
        31: 'inro11',
        32: 'inro12',
        33: 'inro13',
        34: 'inro14',
        35: 'inro15',
        36: 'inro16',
        37: 'reqcogen',  # 响应累积量站召唤
        38: 'reqco1',
        39: 'reqco2',
        40: 'reqco3',
        41: 'reqco4',
        44: 'unknown type identification',  # 未知的类型标识
        45: 'unknown cause of transmission',  # 未知的传送原因
        46: 'unknown common address of ASDU',  # 未知的应用服务数据单元公共地址
        47: 'unknown information object address'  # 未知的信息对象地址
    }

    # 传送原因 P/N
    ASDU_PN = {
        0x00: 'Positive confirm',
        0x40: 'Negative confirm'
    }

    # 溢出标识符
    ASDU_OV = {
        0X00: 'no overflow',    # 未溢出
        0x01: 'overflow'    # 溢出
    }

    # 二进制读数 计数器被调整
    ASDU_CA = {
        0X00: 'not adjusted',  # 未被调整
        0x01: 'adjusted'  # 被调整
    }

    # 封锁标识符
    ASDU_BL = {
        0X00: 'not blocked',    # 未被封锁
        0x10: 'blocked'     # 被封锁
    }

    # 取代标识符
    ASDU_SB = {
        0X00: 'not substituted',    # 未被取代
        0x20: 'substituted' # 被取代
    }

    # 刷新标识符
    ASDU_NT = {
        0X00: 'topical',    # 刷新成果
        0x40: 'not topical' # 刷新未成功
    }

    # 有效标志位
    ASDU_IV = {
        0X00: 'valid',      # 状态有效
        0x80: 'invalid'     # 状态无效
    }

    # 遥测品质描述词
    ASDU_QDS_FLAGS = ['OV', 'RES', 'RES', 'RES', 'BL', 'SB', 'NT', 'IV']

    # 双点信息品质描述词
    ASDU_DIQ_FLAGS = ['SPI', 'SPI', 'RES', 'RES', 'BL', 'SB', 'NT', 'IV']

    # 单点信息品质描述词
    ASDU_SIQ_FLAGS = ['SPI', 'RES', 'RES', 'RES', 'BL', 'SB', 'NT', 'IV']

    # 遥控命令方式
    ASDU_SEL_EXEC = {
        0x00: 'Execute',    # 遥控执行命令
        0x80: 'Select',
        0x01: 'Select',     # 遥控选择命令
    }

    ASDU_QL = {
        0x00: 'no use',
    }

    for i in range(1, 64):
        ASDU_QL[i] = f"preserve the accuracy of supporting equipment"    # 为配套设备保准保留

    for i in range(64, 128):
        ASDU_QL[i] = f"reserved for special access"    # 为特殊通途保留

    ASDU_BSID = {
        0x00: 'positive confirmation of selection, request, stop activation or deletion',  # 选择、请求、停止激活或删除的肯定确认
        0x01: 'negative confirmation of selection, request, stop activation or deletion',  # 选择、请求、停止激活或删除的否定确认
    }

    ASDU_STATUS = {
        0x00: 'no use',
    }

    for i in range(1, 16):
        ASDU_STATUS[i] = f"preserve the accuracy of supporting equipment"    # 为配套设备保准保留

    for i in range(16, 32):
        ASDU_STATUS[i] = f"reserved for special access"    # 为特殊通途保留

    ASDU_WORD = {
        0x00: 'no use', # 缺省
        0x01: 'select file',   # 选择文件
        0x02: 'request file',  # 请求文件
        0x03: 'stop activating files',  # 停止激活文件
        0x04: 'delete file',  # 删除文件
        0x05: 'select section',  # 选择节
        0x06: 'request section',  # 请求节
        0x07: 'stop activating sections',  # 停止激活节
    }

    for i in range(8, 11):
        ASDU_WORD[i] = f"standard determiner {i}"    # 标准限定词

    for i in range(11, 16):
        ASDU_WORD[i] = f"specific determiner {i}"    # 特定限定词

    ASDU_AFQ_WORD = {
        0x00: 'no use',  # 缺省
        0x01: 'positive recognition of file transfer',  # 文件传输的肯定认可
        0x02: 'negative recognition of file transfer',  # 文件传输的否定认可
        0x03: 'positive recognition of section transmission',  # 节传输的肯定认可
        0x04: 'negative recognition of section transmission',  # 节传输的否定认可
    }

    for i in range(4, 11):
        ASDU_AFQ_WORD[i] = f"standard determiner {i}"  # 标准限定词

    for i in range(11, 16):
        ASDU_AFQ_WORD[i] = f"specific determiner {i}"  # 特定限定词

    ASDU_ERR = {
        0x00: 'no use', # 缺省
        0x01: 'no requested storage space',   # 无请求的存储空间
        0x02: 'checksum error',  # 校验和错
        0x03: 'unexpected communication services',  # 非所期望的通信服务
        0x04: 'unexpected file name',  # 非所期望的文件名称
        0x05: 'unexpected section name',  # 非所期望的节名称
    }

    for i in range(6, 11):
        ASDU_ERR[i] = f"standard error {i}"    # 标准错误

    for i in range(11, 16):
        ASDU_ERR[i] = f"specific error {i}"    # 特定错误

    ASDU_LSQ = {
        0x00: 'no use',  # 缺省
        0x01: 'file transfer without stopping activation',  # 不带停止激活的文件传输
        0x02: 'file transfer with stop activation',  # 带停止激活的文件传输
        0x03: 'section transmission without stop activation',  # 不带停止激活的节传输
        0x04: 'ection transmission with stop activation',  # 带停止激活的节传输
    }

    for i in range(5, 128):
        ASDU_LSQ[i] = f"standard last paragraph determiner {i}"  # 标准最后节段限定词

    for i in range(128, 256):
        ASDU_LSQ[i] = f"specific last paragraph determiner {i}"  # 特定最后节段限定词

    # 遥控输出方式
    ASDU_QU = {
        0x00: 'no pulse defined',
        0x01: 'short pulse duration (circuit-breaker)',  # 短脉冲方式输出
        0x02: 'long pulse duration',  # 长脉冲方式输出
        0x03: 'persistent output',  # 持续脉冲方式输出
        0x04: 'Standard',
        0x05: 'Standard',
        0x06: 'Standard',
        0x07: 'Standard',
        0x08: 'Standard',
        0x09: 'reserved',
        0x0A: 'reserved',
        0x0B: 'reserved',
        0x0C: 'reserved',
        0x0D: 'reserved',
        0x0E: 'reserved',
        0x0F: 'reserved',
        0x10: 'Specific',
        0x11: 'Specific',
        0x12: 'Specific',
        0x13: 'Specific',
        0x14: 'Specific',
        0x15: 'Specific',
        0x16: 'Specific',
        0x17: 'Specific',
        0x18: 'Specific',
        0x19: 'Specific',
        0x1A: 'Specific',
        0x1B: 'Specific',
        0x1C: 'Specific',
        0x1D: 'Specific',
        0x1E: 'Specific',
        0x1F: 'Specific',
    }

    # 单点遥控设置值
    ASDU_SCS = {
        0x00: 'OFF',    # 控开
        0x01: 'ON'      # 控合
    }

    # 双点遥控设置值
    ASDU_DCS = {
        0x00: 'inactivity control',  # 无效控制
        0x01: 'OFF',  # 控分
        0x02: 'ON',  # 控合
        0x03: 'inactivity control',  # 无效控制
    }

    # 升降命令 RCS
    ASDU_RCS = {
        0x00: 'inactivity control',  # 不允许
        0x01: 'OFF',  # 降一步
        0x02: 'ON',  # 升一步
        0x03: 'inactivity control',  # 不允许
    }

    #
    ASDU_SU = {
        0X80: 'summer time',
        0x00: 'normal time'
    }

    # Day Of Week
    ASDU_DOW = {
        0x00: 'undefined',
        0x01: 'monday',
        0x02: 'tuesday',
        0x03: 'wednesday',
        0x04: 'thursday',
        0x05: 'friday',
        0x06: 'saturday',
        0x07: 'sunday'
    }

    # 过度
    ASDU_TRANSIENT = {
        0x00: 'not in transient',   # 设备未在瞬变状态
        0x80: 'in transient'   # 设备处于瞬变状态
    }

    ASDU_QOI = {
        0x00: 'no use',
        0x14: 'Station interrogation (global)',
        0x15: 'Interrogation of group 1',
        0x16: 'Interrogation of group 2',
        0x17: 'Interrogation of group 3',
        0x18: 'Interrogation of group 4',
        0x19: 'Interrogation of group 5',
        0x1A: 'Interrogation of group 6',
        0x1B: 'Interrogation of group 7',
        0x1C: 'Interrogation of group 8',
        0x1D: 'Interrogation of group 9',
        0x1E: 'Interrogation of group 10',
        0x1F: 'Interrogation of group 11',
        0x20: 'Interrogation of group 12',
        0x21: 'Interrogation of group 13',
        0x22: 'Interrogation of group 14',
        0x23: 'Interrogation of group 15',
        0x24: 'Interrogation of group 16'
    }

    for i in range(1, 20):
        ASDU_QOI[i] = f"reserved for supporting standards"    # 为配套标准保留

    # 单点遥信状态值
    ASDU_SPI = {
        0x00: 'OFF',     # 开
        0x01: 'ON'     # 合
    }

    # 双点遥信状态
    ASDU_DPI = {
        0x00: 'Indeterminate or Intermediate state',    # 不确定状态或中间装填
        0x01: 'Determined state OFF',   # 确定状态的开
        0x02: 'Determined state ON',    # 确定状态的合
        0x03: 'Indeterminate state'     # 不确定状态或中间装填
    }

    # 计数量 FRZ
    ASDU_FRZ = {
        0x00: 'request count quantity',  # 请求计数量
        0x01: 'freeze without reset',  # 冻结不带复位
        0x02: 'freeze band reset',  # 冻结带复位
        0x03: 'count reset'  # 计数量复位
    }

    # 计数量
    ASDU_RQT = {
        0x00: 'quantity not calculated using request',
        0x01: 'total request count',
        0x02: 'request count quantity group 1',
        0x03: 'request count quantity group 2',
        0x04: 'request count quantity group 3',
        0x05: 'request count quantity group 4',
    }

    for i in range(6, 32):
        ASDU_RQT[i] = f"reserved for supporting standards {i}"

    for i in range(32, 64):
        ASDU_RQT[i] = f"reserved for special purposes {i}"

    # GS
    ASDU_GS = {
        0x01: 'total startup',
        0x00: 'no total start',
    }

    # A相保护
    ASDU_SL_A = {
        0x01: 'A-phase protection activation',     # A相保护启动
        0x00: 'A-phase protection not activated',        # A相保护未启动
    }

    ASDU_SL_B = {
        0x01: 'B-phase protection activation',     # B相保护启动
        0x00: 'B-phase protection not activated',    # B相保护未启动
    }

    ASDU_SL_C = {
        0x01: 'C-phase protection activation',      # C相保护启动
        0x00: 'C-phase protection not activated',   # C相保护未启动
    }

    ASDU_SLE = {
        0x01: 'Ground current protection activation',   # 接地电流保护启动
        0x00: 'Ground current protection not activated',  # 接地电流保护未启动
    }

    ASDU_SRD = {
        0x01: 'reverse protection activation',     # 反向保护启动
        0x00: 'reverse protection not activated',    # 反向保护未启动
    }

    ASDU_GC = {
        0x01: 'general command output to output circuit',     # 总命令输出至输出电路
        0x00: 'no general command output to output circuit',    # 无总命令输出至输出电路
    }

    ASDU_GL_A = {
        0x01: 'command output to A-phase output circuit',    # 命令输出至A相输出电路
        0x00: 'no command output to A-phase output circuit',   # 无命令输出至A相输出电路
    }

    ASDU_GL_B = {
        0x01: 'command output to B-phase output circuit',    # 命令输出至B相输出电路
        0x00: 'no command output to B-phase output circuit',   # 无命令输出至B相输出电路
    }

    ASDU_GL_C = {
        0x01: 'command output to C-phase output circuit',    # 命令输出至C相输出电路
        0x00: 'no command output to C-phase output circuit',   # 无命令输出至C相输出电路
    }

    # 参数种类
    ASDU_KPA = {
        0x00: 'unused',     # 未用
        0x01: 'threshold',    # 门限值
        0x02: 'smoothing coefficient (filtering time constant)',   # 平滑系数（滤波时间常数）
        0x03: 'lower limit for transmitting measurement values',   # 传送测量值的下限
        0x04: 'upper limit for transmitting measurement values',   # 传送测量值的上限
    }

    for i in range(5, 32):
        ASDU_KPA[i] = f"standard measured value parameter determiner {i}"  # 标准测量值参数限定词

    for i in range(32, 64):
        ASDU_KPA[i] = f"specific measured value parameter determiner{i}"  # 特定测量值参数限定词

    # 当地参数改变
    ASDU_LPC = {
        0x01: 'change', # 改变
        0x00: 'unchanged',    # 未改变
    }

    # 参数在运行
    ASDU_POP = {
        0x01: 'not running',    # 未运行
        0x00: 'running',     # 运行
    }

    ASDU_QPA = {
        0x00: 'unused',     # 未用
        0x01: 'activate/stop the parameters loaded before activation (information object address=0)',   # 激活/停止激活之前装载的参数(信息对象地址=0)
        0x02: 'activate/deactivate the parameters of the addressed information object',  # 激活/停止激活所寻址信息对象的参数
        0x03: 'activating/deactivating the addressed information object for continuous cyclic or periodic transmission',  # 激活/停止激活所寻址的持续循环或周期传输的信息对象
    }

    for i in range(4, 128):
        ASDU_QPA[i] = f"standard parameter activation determiner {i}"   # 标准参数激活限定词

    for i in range(128, 256):
        ASDU_QPA[i] = f"specific parameter activation determiner{i}"   # 特定参数激活限定词

    ASDU_QRP = {
        0x00: 'not adopted',    # 未采用
        0x01: 'total reset of processes',   # 进程的总复位
        0x02: 'reset the time marked information waiting for processing in the event buffer',     # 复位事件缓冲区等待处理的带时标的信息
    }

    for i in range(3, 128):
        ASDU_QRP[i] = f"standard reset process command determiner {i}"     # 标准复位进程命令限定词

    for i in range(128, 256):
        ASDU_QRP[i] = f"specific reset process command determiner {i}"     # 特定复位进程命令限定词

    # 初始化原因
    ASDU_U17 = {
        0x00: 'Local power switch on',
        0x01: 'Local manual reset',
        0x02: 'Remote reset',
    }

    for i in range(3, 128):
        ASDU_U17[i] = 'Undefined'

    ASDU_BS1 = {
        0x00: 'Initialization with unchanged local parameters',
        0x80: 'Initialization after change of local parameters'
    }


class IECPacket:

    class Q(Packet):
        """品质描述词公有信息"""
        name = 'Q'
        fields_desc = [
            ByteField('BL', None),
            ByteField('SB', None),
            ByteField('NT', None),
            ByteField('IV', None)
        ]

        def do_dissect(self, s):
            self.BL = IECDefine.ASDU_BL[s[0] & 0b10000]
            self.SB = IECDefine.ASDU_SB[s[0] & 0b100000]
            self.NT = IECDefine.ASDU_NT[s[0] & 0b1000000]
            self.IV = IECDefine.ASDU_IV[s[0] & 0b10000000]
            return s

    class SIQ(Packet):
        """7.2.6.1 带品质描述词的单点信息"""
        name = 'SIQ'
        fields_desc = [
            ByteField('SPI', None),
            ByteField('BL', None),
            ByteField('SB', None),
            ByteField('NT', None),
            ByteField('IV', None)
        ]

        def do_dissect(self, s):
            self.SPI = IECDefine.ASDU_SPI[s[0] & 0b1]
            self.BL = IECDefine.ASDU_BL[s[0] & 0b10000]
            self.SB = IECDefine.ASDU_SB[s[0] & 0b100000]
            self.NT = IECDefine.ASDU_NT[s[0] & 0b1000000]
            self.IV = IECDefine.ASDU_IV[s[0] & 0b10000000]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class DIQ(Packet):
        """7.2.6.2带品质描述词的双点信息"""
        name = 'QDS'

        fields_desc = [
            ByteField('DPI', False),
            ByteField('BL', None),
            ByteField('SB', None),
            ByteField('NT', None),
            ByteField('IV', None)
        ]

        def do_dissect(self, s):
            self.DPI = IECDefine.ASDU_DPI[s[0] & 0b11]
            self.BL = IECDefine.ASDU_BL[s[0] & 0b10000]
            self.SB = IECDefine.ASDU_SB[s[0] & 0b100000]
            self.NT = IECDefine.ASDU_NT[s[0] & 0b1000000]
            self.IV = IECDefine.ASDU_IV[s[0] & 0b10000000]

            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QDS(Packet):
        """7.2.6.3 品质描述词"""
        name = 'QDS'
        fields_desc = [
            ByteField('OV', None),
            ByteField('BL', None),
            ByteField('SB', None),
            ByteField('NT', None),
            ByteField('IV', None)
        ]

        def do_dissect(self, s):
            self.OV = IECDefine.ASDU_OV[s[0] & 0b1]
            self.BL = IECDefine.ASDU_BL[s[0] & 0b10000]
            self.SB = IECDefine.ASDU_SB[s[0] & 0b100000]
            self.NT = IECDefine.ASDU_NT[s[0] & 0b1000000]
            self.IV = IECDefine.ASDU_IV[s[0] & 0b10000000]

            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QDP(Packet):
        """7.2.6.4 继电保护设备事件的品质描述词"""
        name = 'QDP'
        fields_desc = [
            ByteField('EI', False),
            ByteField('BL', None),
            ByteField('SB', None),
            ByteField('NT', None),
            ByteField('IV', None)
        ]

        def do_dissect(self, s):
            self.EI = IECDefine.ASDU_IV[s[0] & 0b1]
            self.BL = IECDefine.ASDU_BL[s[0] & 0b10000]
            self.SB = IECDefine.ASDU_SB[s[0] & 0b100000]
            self.NT = IECDefine.ASDU_NT[s[0] & 0b1000000]
            self.IV = IECDefine.ASDU_IV[s[0] & 0b10000000]

            return s[1:]

        def extract_padding(self, s):
            return None, s

    class VTI(Packet):
        """7.2.6.5 带瞬变状态指示的值"""
        name = 'VTI'
        fields_desc = [
            ByteField('Value', False),
            ByteField('Transient', None)
        ]

        def do_dissect(self, s):
            self.Value = s[0] & 0b1111111 # unpack('b', (s[0] & 0b1111111) << 1)[0] >> 1   # 取后七位  左移一位 以有符号单字节整型解析 右移一位
            self.Transient = IECDefine.ASDU_TRANSIENT[s[0] & 0b1]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class NVA(Packet):
        """7.2.6.6 规一化值"""
        name = 'NVA'
        fields_desc = [
            ShortField('NVA', None),
        ]

        def do_dissect(self, s):
            if s[0] & 0b10000000 == 0b10000000:
                # 标志位为1时
                if s[0] == 0b10000000 and s[1] == 0b0:
                    self.NVA = -1
                else:
                    self.NVA = unpack('>H', s[0:2])[0] / 32768
            else:
                # 标志位为0时
                self.NVA = unpack('>H', s[0:2])[0] / 32768
            return s[2:]

        def extract_padding(self, s):
            return None, s

    class SVA(Packet):
        """7.2.6.7 标度化值"""
        name = 'SVA'
        fields_desc = [
            ShortField('SVA', None),
        ]

        def do_dissect(self, s):
            self.SVA = unpack('>h', s[0:2])[0]
            return s[2:]

        def extract_padding(self, s):
            return None, s

    class BCR(Packet):
        """7.2.6.9 二进制计数器读数"""
        name = 'BCR'
        fields_desc = [
            ByteField('V', None),    # 计数读数
            ByteField('SQ', None),    # 顺序记号
            ByteField('CY', None),    #
            ByteField('CA', None),
            ByteField('IV', None)
        ]

        def do_dissect(self, s):
            cp8 = s[4]
            self.V = unpack('<i', s[:4])[0]
            self.SQ = cp8 & 0b11111
            self.CY = IECDefine.ASDU_OV[cp8 & 0b100000]
            self.CA = IECDefine.ASDU_CA[cp8 & 0b1000000]
            self.IV = IECDefine.ASDU_IV[cp8 & 0b10000000]
            return s[5:]

        def extract_padding(self, s):
            return None, s

    class SEP(Packet):
        """7.2.6.10 继电保护设备事件的品质描述词"""
        name = 'SEP'
        fields_desc = [
            ByteField('ES', None),
            ByteField('EI', None),
            ByteField('BL', None),
            ByteField('SB', None),
            ByteField('NT', None),
            ByteField('IV', None)
        ]

        def do_dissect(self, s):
            self.EI = IECDefine.ASDU_IV[s[0] & 0b1]
            self.ES = IECDefine.ASDU_DPI[s[0] & 0b11]
            self.BL = IECDefine.ASDU_BL[s[0] & 0b10000]
            self.SB = IECDefine.ASDU_SB[s[0] & 0b100000]
            self.NT = IECDefine.ASDU_NT[s[0] & 0b1000000]
            self.IV = IECDefine.ASDU_IV[s[0] & 0b10000000]

            return s[1:]

        def extract_padding(self, s):
            return None, s

    class SPE(Packet):
        """7.2.6.11 继电保护设备启动事件"""
        name = 'SPE'
        fields_desc = [
            ByteField('GS', None),
            ByteField('SL1', None),
            ByteField('SL2', None),
            ByteField('SL3', None),
            ByteField('SLE', None),
            ByteField('SRD', None)
        ]

        def do_dissect(self, s):
            self.GS = IECDefine.ASDU_GS[s[0] & 0b1]
            self.SL1 = IECDefine.ASDU_SL_A[s[0] & 0b10]
            self.SL2 = IECDefine.ASDU_SL_B[s[0] & 0b100]
            self.SL3 = IECDefine.ASDU_SL_C[s[0] & 0b1000]
            self.SLE = IECDefine.ASDU_SLE[s[0] & 0b10000]
            self.SRD = IECDefine.ASDU_SRD[s[0] & 0b100000]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class OCI(Packet):
        """7.2.6.12 继电保护设备输出电路信息"""
        name = 'OCI'
        fields_desc = [
            ByteField('GC', None),
            ByteField('CL1', None),
            ByteField('CL2', None),
            ByteField('CL3', None)
        ]

        def do_dissect(self, s):
            self.GC = IECDefine.ASDU_GC[s[0] & 0b1]
            self.CL1 = IECDefine.ASDU_GL_A[s[0] & 0b10]
            self.CL2 = IECDefine.ASDU_GL_B[s[0] & 0b100]
            self.CL3 = IECDefine.ASDU_GL_C[s[0] & 0b1000]

            return s[1:]

        def extract_padding(self, s):
            return None, s

    class BSI(Packet):
        """7.2.6.13 二进制状态信息"""
        name = 'BSI'
        fields_desc = [
            ByteField('LSS', None),     # 当地显示子系统
            ByteField('RAM', None),  # 变位遥信使遥控 升降 设定命令取消
            ByteField('UPS', None),  # UPS状态
            ByteField('AGC', None),  # 自动发电控制
            ByteField('TRRL', None),  # 遥控转当地
            ByteField('U', None),  # 无人值班
            ByteField('SR', None),  # 系统重新启动
            ByteField('CS', None),  # 冷启动
            ByteField('SS', None),  # 系统自检
            ByteField('PF', None),     # 电源故障
            ByteField('STI', None),     # 短时间干扰
            ByteField('PSUF', None),  # 电源单元有故障
            ByteField('Value', None),
        ]

        def do_dissect(self, s):
            self.Value = ''.join(format(bt, '08b') for bt in s[0:4])
            self.RAM = self.BSI[0]  # 1
            self.LSS = self.BSI[6]  # 7
            self.UPS = self.BSI[16]   # 17
            self.TRRL = self.BSI[18]  # 19
            self.U = self.BSI[19]  # 20
            self.AGC = self.BSI[20]   # 21
            self.SR = self.BSI[24]  # 25
            self.CS = self.BSI[25] # 26
            self.SS = self.BSI[26]  # 27
            self.PF = self.BSI[29]  # 30
            self.STI = self.BSI[30]  # 31
            self.PSUF = self.BSI[31]  # 32
            return s[4:]

        def extract_padding(self, s):
            return None, s

    class FBP(Packet):
        """7.2.6.14 固定测试字，两个八位位组"""
        name = 'FBP'
        fields_desc = [
            ShortField('FBP', None),
        ]

        def do_dissect(self, s):
            self.FBP = unpack('>h', s[0:2])[0]
            return s[2:]

        def extract_padding(self, s):
            return None, s

    class SCO(Packet):
        """7.2.6.15 单命令"""
        name = 'SCO'

        fields_desc = [
            ByteField('SE', None),
            ByteField('QU', None),
            ByteField('SCS', None),
        ]

        def do_dissect(self, s):
            self.QU = IECDefine.ASDU_QU[(s[0] & 0b01111100) >> 2]
            self.SE = IECDefine.ASDU_SEL_EXEC[s[0] & 0b10000000]
            self.SCS = IECDefine.ASDU_SCS[s[0] & 0b1]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class DCO(Packet):
        """7.2.6.16 双命令"""
        name = 'DCO'
        fields_desc = [
            ByteField('SE', None),
            ByteField('QU', None),
            ByteField('DCS', None),
        ]

        def do_dissect(self, s):
            self.QU = IECDefine.ASDU_QU[(s[0] & 0b01111100) >> 2]
            self.SE = IECDefine.ASDU_SEL_EXEC[s[0] & 0b10000000]
            self.DCS = IECDefine.ASDU_DCS[s[0] & 0b11]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class RCO(Packet):
        """7.2.6.17 步调节命令"""
        name = 'RCO'
        fields_desc = [
            ByteField('SE', None),
            ByteField('QU', None),
            ByteField('RCS', None),
        ]

        def do_dissect(self, s):
            self.QU = IECDefine.ASDU_QU[(s[0] & 0b01111100) >> 2]
            self.SE = IECDefine.ASDU_SEL_EXEC[s[0] & 0b10000000]
            self.RCS = IECDefine.ASDU_RCS[s[0] & 0b11],  # TODO
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class CP56Time(Packet):
        """7.2.6.18 七个八位位组二进制时间 该时间为增量时间信息，其增量的参考日期协商确定"""
        name = 'CP56Time'

        fields_desc = [
            ByteField('S', None),
            ByteField('Min', None),
            ByteField('IV', None),
            ByteField('Hour', None),
            ByteField('SU', None),
            ByteField('Day', None),
            ByteField('WeekDay', None),
            ByteField('Month', None),
            ByteField('Year', None),
        ]

        def do_dissect(self, s):
            self.S = unpack('<H', s[0:2])[0] / 1000  # 单位：秒(s)
            self.Min = int(s[2] & 0b111111)
            self.IV = IECDefine.ASDU_IV[s[2] & 0b10000000]
            self.Hour = int(s[3] & 0b11111)
            self.SU = IECDefine.ASDU_SU[s[3] & 0b10000000]
            self.Day = int(s[4] & 0b11111)
            self.WeekDay = IECDefine.ASDU_DOW[s[4] & 0b11100000]
            self.Month = int(s[5] & 0b1111)
            self.Year = int(s[6] & 0b1111111)
            return s[7:]

        def extract_padding(self, s):
            return None, s

    class CP24Time(Packet):
        """7.2.6.19 解析 三个八位位组二进制时间 该时间为增量时间信息，其增量的参考日期协商确定"""
        name = 'CP24Time'
        fields_desc = [
            ByteField('S', None),
            ByteField('Min', None),
            ByteField('IV', None),
        ]

        def do_dissect(self, s):
            self.S = unpack('<H', s[0:2])[0] / 1000  # 单位：秒(s)
            self.Min = int(s[2] & 0b111111)
            self.IV = IECDefine.ASDU_IV[s[2] & 0b10000000]
            return s[3:]

        def extract_padding(self, s):
            return None, s

    class CP16Time(Packet):
        """7.2.6.20 二个八位位组二进制时间 该时间为增量时间信息，其增量的参考日期协商确定"""
        name = 'CP16Time'
        fields_desc = [
            ByteField('S', None),
        ]

        def do_dissect(self, s):
            self.S = unpack('<H', s[0:2])[0] / 1000  # 单位：秒(s)
            return s[2:]

        def extract_padding(self, s):
            return None, s

    class COI(Packet):
        """7.2.6.21 初始化原因"""
        name = 'COI'
        fields_desc = [
            ByteField('U17', None),
            ByteField('BS1', None),
        ]

        def do_dissect(self, s):
            self.U17 = IECDefine.ASDU_U17[s[0] & 0b1111111]
            self.BS1 = IECDefine.ASDU_BS1[s[0] & 0b10000000]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QOI(Packet):
        """7.2.6.22 召唤限定词"""
        name = 'QOI'
        fields_desc = [
            ByteField('QOI', None),
        ]

        def do_dissect(self, s):
            self.QOI = IECDefine.ASDU_QOI.get(s[0])
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QCC(Packet):
        """7.2.6.22 召唤限定词"""
        name = 'QCC'
        fields_desc = [
            ByteField('QCC', None),
        ]

        def do_dissect(self, s):
            self.QCC = s[0]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QCC1(Packet):
        """7.2.6.23 计数量召唤命令限定词"""
        name = 'QCC'
        fields_desc = [
            ByteField('RQT', None),
            ByteField('FRZ', None),
        ]

        def do_dissect(self, s):
            self.FRZ = IECDefine.ASDU_FRZ[(s[0] & 0b11000000) >> 6]
            self.RQT = IECDefine.ASDU_RQT[s[0] & 0b111111]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QPM(Packet):
        """7.2.6.24 测量值参数限定词"""
        name = 'QPM'
        fields_desc = [
            ByteField('KPA', None),
            ByteField('LPC', None),
            ByteField('POP', None),
        ]

        def do_dissect(self, s):
            self.KPA = IECDefine.ASDU_KPA[s[0] & 0b111111]
            self.LPC = IECDefine.ASDU_LPC[s[0] & 0b1000000]
            self.POP = IECDefine.ASDU_POP[s[0] & 0b10000000]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QPA(Packet):
        """7.2.6.25 参数激活限定词"""
        name = 'QPA'
        fields_desc = [
            ByteField('QPA', None)
        ]

        def do_dissect(self, s):
            self.QPA = IECDefine.ASDU_QPA[s[0]]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QOC(Packet):
        """7.2.6.26 命令限定词"""
        name = 'QOC'
        fields_desc = [
            ByteField('QU', None),
            ByteField('SE', None)
        ]

        def do_dissect(self, s):
            self.QU = IECDefine.ASDU_QU[(s[0] & 0b01111100) >> 2]
            self.SE = IECDefine.ASDU_SEL_EXEC[s[0] & 0b10000000]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QRP(Packet):
        """7.2.6.27 复位进程命令限定词"""
        name = 'QRP'

        fields_desc = [
            ByteField('QRP', None),
        ]

        def do_dissect(self, s):
            self.QRP = IECDefine.ASDU_QRP[s[0]]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class FRQ(Packet):
        """7.2.6.28 文件准备就绪限定词"""
        name = 'FRQ'
        fields_desc = [
            ByteField('U17', None),
            ByteField('BSID', None),
        ]

        def do_dissect(self, s):
            self.U17 = IECDefine.ASDU_QL[s[0] & 0b1111111]
            self.BSID = IECDefine.ASDU_BSID[s[0] & 0b10000000]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class SRQ(Packet):
        """7.2.6.29 节准备就绪限定词"""
        name = 'SRQ'
        fields_desc = [
            ByteField('U17', None),
            ByteField('BS1', None),
        ]

        def do_dissect(self, s):
            self.U17 = IECDefine.ASDU_QL[s[0] & 0b1111111]
            self.BS1 = 'not ready' if s[0] & 0b10000000 else 'ready'
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class SCQ(Packet):
        """7.2.6.30 选择和召唤限定词"""
        name = 'SCQ'
        fields_desc = [
            ByteField('Word', None),
            ByteField('Err', None),
        ]

        def do_dissect(self, s):
            self.Word = IECDefine.ASDU_WORD[s[0] & 0b1111]
            self.Err = IECDefine.ASDU_ERR[(s[0] & 0b11110000) >> 4]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class LSQ(Packet):
        """7.2.6.31 最后的节和段的限定词"""
        name = 'LSQ'
        fields_desc = [
            ByteField('LSQ', None),
        ]

        def do_dissect(self, s):
            self.LSQ = IECDefine.ASDU_LSQ[s[0]]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class AFQ(Packet):
        """7.2.6.32 文件认可或节认可限定词"""
        name = 'AFQ'
        fields_desc = [
            ByteField('Word', None),
            ByteField('Err', None),
        ]

        def do_dissect(self, s):
            self.Word = IECDefine.ASDU_AFQ_WORD[s[0] & 0b1111]
            self.Err = IECDefine.ASDU_ERR[(s[0] & 0b11110000) >> 4]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class NOF(Packet):
        """7.2.6.33 文件名称"""
        name = 'NOF'
        fields_desc = [
            ByteField('NAME', None),
        ]

        def do_dissect(self, s):
            self.NAME = s if s[0] else 'no use'
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class NOS(Packet):
        """7.2.6.34 节名称"""
        name = 'NOS'
        fields_desc = [
            ByteField('NOS', None),
        ]

        def do_dissect(self, s):
            self.NOS = s[0] if s[0] else '缺省'
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class LOF(Packet):
        """7.2.6.35 文件或节的长度"""
        name = 'LOF'
        fields_desc = [
            ShortField('LOF', None),
        ]

        def do_dissect(self, s):
            self.LOF = unpack('<I', s[0:1])[0]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class LOS(Packet):
        """7.2.6.36 段的长度"""
        name = 'LOS'
        fields_desc = [
            ShortField('LOS', None),
        ]

        def do_dissect(self, s):
            self.LOS = s[0]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class CHS(Packet):
        """7.2.6.37 校验和"""
        name = 'CHS'
        fields_desc = [
            ShortField('CHS', None),
        ]

        def do_dissect(self, s):
            self.CHS = s[0]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class SOF(Packet):
        """7.2.6.38 文件状态"""
        name = 'SOF'
        fields_desc = [
            ByteField('STATUS', None),
            ByteField('LFD', None),
            ByteField('FOR', None),
            ByteField('FA', None),
        ]

        def do_dissect(self, s):
            self.STATUS = IECDefine.ASDU_STATUS[s[0] & 0b11111]
            self.LFD = 'final catalog file' if s[0] & 0b100000 else 'there are also directory files behind it'
            self.FOR = 'define subdirectory names' if s[0] & 0b1000000 else 'define file name'
            self.FA = 'file transfer activated' if s[0] & 0b10000000 else 'file waiting for transfer'
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class QOS(Packet):
        """7.2.6.39 设定命令限定词"""
        name = 'QOS'
        fields_desc = [
            ByteField('QL', False),
            ByteField('SE', None)
        ]

        def do_dissect(self, s):
            self.QL = IECDefine.ASDU_QL[s[0] & 0b1111111]
            self.SE = IECDefine.ASDU_SEL_EXEC[s[0] & 0b10000000]
            return s[1:]

        def extract_padding(self, s):
            return None, s

    class SCD(Packet):
        """7.2.6.40 状态和状态变位检出"""
        name = 'SCD'
        fields_desc = [
            ByteField('ST', None),
            ByteField('CD', None)
        ]

        def do_dissect(self, s):
            self.ST = bin(s[1]).strip('0b') + bin(s[0]).strip('0b')    # 字节1-2是连续的16位遥信状态
            self.CD = bin(s[3]).strip('0b') + bin(s[2]).strip('0b')    # 字节3-4是对应的变位标志，1表示变位，0表示未变位
            return s[4:]

        def extract_padding(self, s):
            return None, s

    class LEFloatField(Field):
        def __init__(self, name, default):
            Field.__init__(self, name, default, '<f')

    class LEIntField(Field):
        def __init__(self, name, default):
            Field.__init__(self, name, default, '<i')

    class SignedShortField(Field):
        def __init__(self, name, default):
            Field.__init__(self, name, default, "<h")

    class IOAID(Field):

        def __init__(self, name, default):
            Field.__init__(self, name, default, '<I')

        def addfield(self, pkt, s, val):
            if val is None:
                return s
            return s + pack('BBB', int(val & 0xff), int((val & 0xff00) / 0x0100), int((val & 0xff0000) / 0x010000))
            #return s + pack('BB', int(val & 0xff), int((val & 0xff00) / 0x0100))  # NOTE: For malformed packets

        def getfield(self, pkt, s):
            return s[3:], self.m2i(pkt, unpack(self.fmt, s[:3] + b'\x00')[0])
            #return s[2:], self.m2i(pkt, unpack(self.fmt, s[:2] + b'\x00\x00')[0])


class IECData:

    class IOA1(Packet):
        """7.3.1.1 M_SP_NA_1 单点遥信(带品质描述 不带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SIQ', None, IECPacket.SIQ)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SIQ.SPI}

    class IOA2(Packet):
        """7.3.1.2 M_SP_TA_1 带时标的单点信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SIQ', None, IECPacket.SIQ),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SIQ.SPI}

    class IOA3(Packet):
        """7.3.1.3 M_DP_NA_1 双点遥信(带品质描述 不带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DIQ', None, IECPacket.DIQ)
        ]

        def value(self) -> dict:
            return {self.IOA: self.DIQ.DPI}

    class IOA4(Packet):
        """7.3.1.4 M_DP_TA_1 带时标的双点信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DIQ', None, IECPacket.DIQ),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.DIQ.DPI}

    class IOA5(Packet):
        """7.3.1.5 M_ST_NA_1 步位置信息(带品质描述 不带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('VTI', None, IECPacket.VTI),
            PacketField('QDS', None, IECPacket.QDS)
        ]

        def value(self) -> dict:
            return {self.IOA: self.VTI.Value}

    class IOA6(Packet):
        """7.3.1.6 M_ST_TA_1 带时标的步位置信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('VTI', None, IECPacket.VTI),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.VTI.Value}

    class IOA7(Packet):
        """7.3.1.7 M_BO_NA_1 32比特串(带品质描述 不带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('BSI', None, IECPacket.BSI),
            PacketField('QDS', None, IECPacket.QDS)
        ]

        def value(self) -> dict:
            return {}

    class IOA8(Packet):
        """7.3.1.8 M_BO_TA_1 带时标的32比特串"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('BSI', None, IECPacket.BSI),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA9(Packet):
        """ 7.3.1.9 M_ME_NA_1 规一化遥测值(带品质描述 不带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NVA', None, IECPacket.NVA),    # TODO
            PacketField('QDS', None, IECPacket.QDS)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NVA.NVA}

    class IOA10(Packet):
        """ 7.3.1.10 M_ME_TA_1 规一化遥测值(带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NVA', None, IECPacket.NVA),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NVA.NVA}

    class IOA11(Packet):
        """7.3.1.11 M_ME_NB_1 测量值，标度化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SVA', None, IECPacket.SVA),
            PacketField('QDS', None, IECPacket.QDS)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SVA.SVA}

    class IOA12(Packet):
        """7.3.1.12 M_ME_TB_1 测量值，带时标的标度化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SVA', None, IECPacket.SVA),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SVA.SVA}

    class IOA13(Packet):
        """7.3.1.13 M_ME_NC_1 短浮点遥测值(带品质描述 不带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),
            PacketField('QDS', None, IECPacket.QDS)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA14(Packet):
        """7.3.1.14 M_ME_TC_1 短浮点遥测值(带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA15(Packet):
        """7.3.1.15 M_IT_NA_1 累计量"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('BCR', None, IECPacket.BCR)
        ]

        def value(self) -> dict:
            return {self.IOA: self.BCR.V}

    class IOA16(Packet):
        """7.3.1.16 M_IT_TA_1 带时标的累计量"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('BCR', None, IECPacket.BCR),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.BCR.V}

    class IOA17(Packet):
        """7.3.1.17 M_EP_TA_1 带时标的继电保护设备事件"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SEP', None, IECPacket.SEP),
            PacketField('CP16Time', None, IECPacket.CP16Time),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA18(Packet):
        """7.3.1.18 M_EP_TB_1 带时标的继电保护设备成组启动事件"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SPE', None, IECPacket.SPE),
            PacketField('QDP', None, IECPacket.QDP),
            PacketField('CP16Time', None, IECPacket.CP16Time),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA19(Packet):
        """7.3.1.19 M_EP_TC_1 带时标的继电保护设备成组输出电路信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('OCI', None, IECPacket.OCI),
            PacketField('QDP', None, IECPacket.QDP),
            PacketField('CP16Time', None, IECPacket.CP16Time),
            PacketField('CP24Time', None, IECPacket.CP24Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA20(Packet):
        """7.3.1.20 M_PS_NA_1 带变位检出的成组单点信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SCD', None, IECPacket.SCD),
            PacketField('QDS', None, IECPacket.QDS)
        ]

        def value(self) -> dict:
            return {}

    class IOA21(Packet):
        """ 7.3.1.21 M_ME_ND_1 规一化遥测值(不带品质描述 不带时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NVA', None, IECPacket.NVA)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NVA.NVA}

    class IOA22(Packet):
        """ 7.3.1.22 M_SP_TB_1 带时标CP56Time2a的单点信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SIQ', None, IECPacket.SIQ),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SIQ.SPI}

    class IOA23(Packet):
        """ 7.3.1.23 M_DP_TB_1 带时标CP56Time2a的双点信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DIQ', None, IECPacket.DIQ),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.DIQ.DPI}

    class IOA24(Packet):
        """ 7.3.1.24 M_ST_TB_1 带时标的步位置信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('VTI', None, IECPacket.VTI),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.VTI.Value}

    class IOA25(Packet):
        """ 7.3.1.25 M_BO_TB_1 带时标CP56Time2a的32比特串"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('BSI', None, IECPacket.BSI),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA26(Packet):
        """ 7.3.1.26 M_ME_TD_1 测量值，带时标CP56Time2a的规一化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NVA', None, IECPacket.NVA),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]
        def value(self) -> dict:
            return {self.IOA: self.NVA.NVA}

    class IOA30(Packet):
        """7.3.1.30 M_SP_TB_1 单点遥信(带品质描述 带绝对时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SIQ', None, IECPacket.SIQ),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SIQ.SPI}

    class IOA31(Packet):
        """M_DP_TB_1 双点遥信(带品质描述 带绝对时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DIQ', None, IECPacket.DIQ),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.DIQ.DPI}

    class IOA35(Packet):
        """ 7.3.1.27 M_ME_TE_1 测量值，带时标CP56Time2a的标度化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SVA', None, IECPacket.SVA),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SVA.SVA}

    class IOA36(Packet):
        """ 7.3.1.28 M_ME_TF_1 测量值，带时标CP56Time2a的短浮点数"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),
            PacketField('QDS', None, IECPacket.QDS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA37(Packet):
        """ 7.3.1.29 M_IT_TB_1 带时标CP56Time2a的累计量"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('BCR', None, IECPacket.BCR),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.BCR.V}

    class IOA38(Packet):
        """7.3.1.30 M_EP_TD_1 带时标CP56Time2a的继电保护设备事件"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SEP', None, IECPacket.SEP),
            PacketField('CP16Time', None, IECPacket.CP16Time),
            PacketField('CP56Time', None, IECPacket.CP56Time),
        ]

        def value(self) -> dict:
            return {}

    class IOA39(Packet):
        """7.3.1.31 M_EP_TE_1 带时标CP56Time2a的继电保护设备成组启动事件"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SEP', None, IECPacket.SEP),
            PacketField('QDP', None, IECPacket.QDP),
            PacketField('CP16Time', None, IECPacket.CP16Time),
            PacketField('CP56Time', None, IECPacket.CP56Time),
        ]

        def value(self) -> dict:
            return {}

    class IOA40(Packet):
        """# 7.3.1.32 M_EP_TF_1 带时标CP56Time2a的继电保护设备成组输出电路信息"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('OCI', None, IECPacket.OCI),
            PacketField('QDP', None, IECPacket.QDP),
            PacketField('CP16Time', None, IECPacket.CP16Time),
            PacketField('CP56Time', None, IECPacket.CP56Time),
        ]

        def value(self) -> dict:
            return {}

    class IOA42(Packet):
        """M_EP_TD_1 继电保护装置事件(带品质描述 带绝对时标)"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('CP16Time', None, IECPacket.CP16Time),  # CP16Time
            PacketField('CP56Time', None, IECPacket.CP56Time),
        ]

        def value(self) -> dict:
            return {}

    class IOA45(Packet):
        """7.3.2.1 C_SC_NA_1 单命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SCO', None, IECPacket.SCO)
        ]

        def value(self) -> dict:
            return {}

    class IOA46(Packet):
        """7.3.2.2 C_DC_NA_1 双命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DCO', None, IECPacket.DCO)
        ]

        def value(self) -> dict:
            return {}

    class IOA47(Packet):
        """7.3.2.3 C_RC_NA_1 步调节命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('RCO', None, IECPacket.RCO)
        ]

        def value(self) -> dict:
            return {}

    class IOA48(Packet):
        """7.3.2.4 C_SE_NA_1 设定命令，规一化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NVA', None, IECPacket.NVA),
            PacketField('QOS', None, IECPacket.QOS)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NVA.NVA}

    class IOA49(Packet):
        """7.3.2.5 C_SE_NB_1 设定命令，标度化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SVA', None, IECPacket.SVA),    # StrField("Value", '', fmt="H", remain=0)
            PacketField('QOS', None, IECPacket.QOS)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SVA.SVA}

    class IOA50(Packet):
        """ 7.3.2.6C_SE_NC_1 设定命令，短浮点数"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),  # StrField("Value", '', fmt="f", remain=0)
            PacketField('QOS', None, IECPacket.QOS)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA51(Packet):
        """C_BO_NA_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEIntField('Value', None) # StrField("Value", '', fmt="I", remain=0)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA58(Packet):
        """C_SC_TA_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SCO', None, IECPacket.SCO),    # XByteField("SCO", 0x80),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA59(Packet):
        """C_DC_TA_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DCO', None, IECPacket.DCO),    # XByteField("DCO", 0x80),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA60(Packet):
        """C_RC_TA_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('RCO', None, IECPacket.RCO),    # XByteField("RCO", 0x80),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA61(Packet):
        """C_SE_TA_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEIntField('Value', None),    # StrField("Value", '', fmt="H", remain=0),
            PacketField('QOS', None, IECPacket.QOS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA62(Packet):
        """C_SE_TB_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEIntField('Value', None),    # StrField("Value", '', fmt="H", remain=0),
            PacketField('QOS', None, IECPacket.QOS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA63(Packet):
        """C_SE_TC_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),  # StrField("Value", '', fmt="f", remain=0),
            PacketField('QOS', None, IECPacket.QOS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA64(Packet):
        """C_BO_TA_1"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEIntField('Value', None),    # StrField("Value", '', fmt="I", remain=0)
            PacketField('CP56Time', None, IECPacket.CP56Time)   # PacketField("CP56Time", CP56Time, Packet)]
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA70(Packet):
        """ 7.3.3 M_EI_NA_1 初始化结束"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('COI', None, IECPacket.COI),
        ]

        def value(self) -> dict:
            return {}

    class IOA100(Packet):
        """7.3.4.1 C_IC_NA_1 召唤命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            #PacketField('QOI', None, IECPacket.QOI)   #PacketField('QOI', None, IECPacket.QOI)
            ByteEnumField('QOI', None, IECDefine.ASDU_QOI),
        ]

        def value(self) -> dict:
            return {}

    class IOA101(Packet):
        """7.3.4.2 C_CI_NA_1 计数量召唤命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            ByteField('QCC', None)
        ]

        def value(self) -> dict:
            return {}

    class IOA102(Packet):
        """7.3.4.3 C_RD_NA_1 读命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
        ]

        def value(self) -> dict:
            return {}

    class IOA103(Packet):
        """7.3.4.4 C_CS_NA_1 时钟同步命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA104(Packet):
        """7.3.4.5 C_TS_NA_1 测试命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('FBP', None, IECPacket.FBP)
        ]

        def value(self) -> dict:
            return {self.IOA: self.FBP.FBP}

    class IOA105(Packet):
        """7.3.4.6 C_RP_NA_1 复位进程命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('QRP', None, IECPacket.QRP)
        ]

        def value(self) -> dict:
            return {self.IOA: self.QRP.QRP}

    class IOA106(Packet):
        """7.3.4.7 C_CD_NA_1 延时获得命令"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('CP16Time', None, IECPacket.CP16Time)
        ]

        def value(self) -> dict:
            return {}

    class IOA110(Packet):
        """7.3.5.1 P_ME_NA_1 测量值参数，规一化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NVA', None, IECPacket.NVA),
            PacketField('QPM', None, IECPacket.QPM)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NVA.NVA}

    class IOA111(Packet):
        """7.3.5.2 P_ME_NB_1 测试值参数，标度化值"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SVA', None, IECPacket.SVA),
            PacketField('QPM', None, IECPacket.QPM)
        ]

        def value(self) -> dict:
            return {self.IOA: self.SVA.SVA}

    class IOA112(Packet):
        """7.3.5.3 P_ME_NC_1 测量值参数，短浮点数"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),
            PacketField('QPM', None, IECPacket.QPM)
        ]

        def value(self) -> dict:
            return {self.IOA: self.Value}

    class IOA113(Packet):
        """7.3.5.4 P_AC_NA_1 参数激活"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('QPA', None, IECPacket.QPA)
        ]

        def value(self) -> dict:
            return {self.IOA: self.QPA.QPA}

    class IOA120(Packet):
        """7.3.6.1 F_FR_NA_1 文件准备就绪"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NOF', None, IECPacket.NOF),
            PacketField('LOF', None, IECPacket.LOF),
            PacketField('FRQ', None, IECPacket.FRQ)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NOF.NAME}

    class IOA121(Packet):
        """7.3.6.2 F_SR_NA_1 节准备就绪"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NOF', None, IECPacket.NOF),
            PacketField('NOS', None, IECPacket.NOS),
            PacketField('LOF', None, IECPacket.LOF),
            PacketField('SRQ', None, IECPacket.SRQ)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NOF.NAME}

    class IOA122(Packet):
        """7.3.6.3 F_SC_NA_1 召唤目录，选择文件，召唤文件，召唤节"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NOF', None, IECPacket.NOF),
            PacketField('NOS', None, IECPacket.NOS),
            PacketField('SCQ', None, IECPacket.SCQ),
        ]

        def value(self) -> dict:
            return {self.IOA: self.NOF.NAME}

    class IOA123(Packet):
        """7.3.6.4 F_LS_NA_1 最后的节，最后的段"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NOF', None, IECPacket.NOF),
            PacketField('NOS', None, IECPacket.NOS),
            PacketField('LSQ', None, IECPacket.LSQ),
            PacketField('CHS', None, IECPacket.CHS),
        ]

        def value(self) -> dict:
            return {self.IOA: self.NOF.NAME}

    class IOA124(Packet):
        """7.3.6.5 F_AF_NA_1 认可文件，认可节"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NOF', None, IECPacket.NOF),
            PacketField('NOS', None, IECPacket.NOS),
            PacketField('AFQ', None, IECPacket.AFQ),
        ]

        def value(self) -> dict:
            return {self.IOA: self.NOF.NAME}

    class IOA125(Packet):
        """7.3.6.6 F_SG_NA_1 段"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NOF', None, IECPacket.NOF),
            PacketField('NOS', None, IECPacket.NOS),
            PacketField('LOS', None, IECPacket.LOS),
        ]

        def value(self) -> dict:
            return {self.IOA: self.NOF.NAME}

    class IOA126(Packet):
        """7.3.6.7 F_DR_TA_1 目录"""
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('NOF', None, IECPacket.NOF),
            PacketField('LOF', None, IECPacket.LOF),
            PacketField('SOF', None, IECPacket.SOF),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

        def value(self) -> dict:
            return {self.IOA: self.NOF.NAME}

    IOAS = {
        1: IOA1,    # 单点遥信(带品质描述 不带时标)
        2: IOA2,
        3: IOA3,    # 双点遥信(带品质描述 不带时标)
        4: IOA4,
        5: IOA5,    # 步位置信息(带品质描述 不带时标)
        7: IOA7,    # 32比特串(带品质描述 不带时标)
        9: IOA9,    # 规一化遥测值(带品质描述 不带时标)
        10: IOA10,
        11: IOA11,  # 标度化值(带品质描述 不带时标)
        12: IOA12,
        13: IOA13,  # 短浮点遥测值(带品质描述 不带时标)
        14: IOA14,
        15: IOA15,  # 累积量(带品质描述 不带时标)
        16: IOA16,
        20: IOA20,
        21: IOA21,
        30: IOA30,  # 单点遥信(带品质描述 带绝对时标)
        31: IOA31,  # 双点遥信(带品质描述 带绝对时标)
        36: IOA36,  # 短浮点遥测值(带品质描述 带绝对时标)
        37: IOA37,   # 累积量(带品质描述 带绝对时标)
        45: IOA45,  # 单点遥控(一个报文只有一个遥控信息体 不带时标)
        50: IOA50,   # 短浮点设定值(一个报文只有一个设定值 不带时标)
        70: IOA70,   # 初始化结束(从站发送，主站收到时候会做一次总召)
        100: IOA100,    # 总召
        101: IOA101,  # 电能脉冲召唤命令
        103: IOA103,     # 时钟同步命令
    }

    IOALEN = {
        1: 4,   # 单点遥信(带品质描述 不带时标) 地址3字节+数据1字节
        2: 7,   # 带3个字节短时标的单点遥信 地址3字节+数据1字节+时标3字节
        3: 4,   # 双点遥信(带品质描述 不带时标) 地址3字节+数据1字节
        4: 7,   # 带3个字节短时标的双点遥信(带品质描述 带时标) 地址3字节+数据1字节+时标3字节
        5: 5,
        6: 8,
        7: 8,
        8: 11,
        9: 6,     # 规一化遥测值(带品质描述 不带时标)  地址3字节+信息体长度3字节
        10: 9,      # 带3个字节时标且具有品质描述的测量值， 地址3字节+遥测值占6个字节
        11: 6,      # 不带时标的标度化值 地址3字节+遥测值占3个字节
        12: 9,   # 带3个字节时标标度化值， 地址3字节+遥测值占6个字节
        13: 8,  # 短浮点遥测值(带品质描述 不带时标) 地址3字节+遥测值占5个字节
        14: 11,     # 带3个字节时标短浮点遥测值(带品质描述 带时标) 地址3字节+遥测值占8个字节
        15: 8,      # 电能脉冲计数量 地址3字节+电能量5个字节
        16: 11,     # 电能脉冲计数量 地址3字节+电能量5个字节 + 时标3字节
        17: 9,
        18: 10,
        19: 10,
        20: 8,  # 具有状态变为检测的成组单点遥信，每个字节包括8个遥信
        21: 5,  # 带3个字节时标且具有品质描述的短浮点遥测值(带品质描述 不带时标) 地址3字节+遥测值占2个字节
        22: 11,
        23: 11,
        24: 12,
        25: 15,
        26: 13,
        30: 11,     # 单点遥信(带品质描述 带绝对时标)  地址3字节+数据1字节 + 时标7字节
        31: 11,     # 双点遥信(带品质描述 带绝对时标)  地址3字节+数据1字节 + 时标7字节
        35: 13,
        36: 15,
        37: 15,     # 电能脉冲计数量 地址3字节+电能量5个字节 + 时标7字节
        38: 13,
        39: 14,
        40: 14,
        45: 4,
        46: 4,
        47: 4,
        48: 6,
        49: 6,
        50: 8,
        51: 7,
        70: 4,
        100: 4,
        101: 4,
        103: 10,
        104: 5,
        105: 4,
        106: 5,
        110: 6,
        111: 6,
        112:  8,
        113: 4,
        121: 7,
        122: 6,
        123: 7,
        124: 6,
        126: 13
    }


class IECFrameDefine:

    class UFrame(IntEnum):
        TESTFR_CON = 0x83,  # 心跳应答（确认）
        TESTFR_ACT = 0x43,  # 心跳请求（激活）

        STOPDT_CON = 0x23,  # 关闭链路应答（确认）
        STOPDT_ACT = 0x13,  # 关闭链路请求（激活）

        STARTDT_CON = 0x0b,  # 建立链路应答（确认）
        STARTDT_ACT = 0x07,  # 建立链路请求（激活）

    class TYP(IntEnum):
        # 监视方向的过程信息
        M_SP_NA_1 = 1,  # 单点信息
        M_SP_TA_1 = 2,  # 带时标的单点信息
        M_DP_NA_1 = 3,  # 双点信息
        M_DP_TA_1 = 4,  # 带时标的双点信息
        M_ST_NA_1 = 5,  # 步位置信息
        M_ST_TA_1 = 6,  # 带时标的步位置信息
        M_BO_NA_1 = 7,  # 32比特串
        M_BO_TA_1 = 8,  # 带时标的32比特串
        M_ME_NA_1 = 9,  # 测量值，归一化值
        M_ME_TA_1 = 10,  # 测量值，带时标的归一化值
        M_ME_NB_1 = 11,  # 测量值，标度化值
        M_ME_TB_1 = 12,  # 测量值，带时标的标度化值
        M_ME_NC_1 = 13,  # 测量值，短浮点数
        M_ME_TC_1 = 14,  # 测量值，带时标的短浮点数
        M_IT_NA_1 = 15,  # 累计量
        M_IT_TA_1 = 16,  # 带时标的累计量
        # M_EP_TA_1 = 17,  # 带时标的继电保护设备事件
        # M_EP_TB_1 = 18,  # 带时标的继电保护设备成组启动事件
        # M_EP_TC_1 = 19,  # 带时标的继电保护设备成组输出电路信息
        M_PS_NA_1 = 20,  # 具有状态变位检出的成组单点信息
        M_ME_ND_1 = 21,  # 测量值，不带品质描述的归一化值
        M_SP_TB_1 = 30,  # 带时标CP56Time2a的单点信息
        M_DP_TB_1 = 31,  # 带时标CP56Time2a的双点信息
        M_ST_TB_1 = 32,  # 带时标CP56Time2a的步位置信息
        M_BO_TB_1 = 33,  # 带时标CP56Time2a的32位串
        M_ME_TD_1 = 34,  # 带时标CP56Time2a的归一化测量值
        M_ME_TE_1 = 35,  # 测量值，带时标CP56Time2a的标度化值
        M_ME_TF_1 = 36,  # 测量值，带时标CP56Time2a的短浮点数
        M_IT_TB_1 = 37,  # 带时标CP56Time2a的累计值
        M_EP_TD_1 = 38,  # 带时标CP56Time2a的继电保护装置事件
        # M_EP_TE_1 = 39,  # 带时标CP56Time2a的继电保护装置成组启动事件
        # M_EP_TF_1 = 40,  # 带时标CP56Time2a的继电保护装置成组输出电路信息
        # 控制方向的过程信息
        C_SC_NA_1 = 45,  # 单命令
        C_DC_NA_1 = 46,  # 双命令
        C_RC_NA_1 = 47,  # 步调节命令
        C_SE_NA_1 = 48,  # 设定值命令，归一化值
        C_SE_NB_1 = 49,  # 设定值命令，标度化值
        C_SE_NC_1 = 50,  # 设定值命令，短浮点数
        C_BO_NA_1 = 51,  # 设定值命令，32比特串
        C_SC_TA_1 = 58,  # 带时标CP56Time2a的单命令
        C_DC_TA_1 = 59,  # 带时标CP56Time2a的双命令
        C_RC_TA_1 = 60,  # 带时标CP56Time2a的步调节命令
        C_SE_TA_1 = 61,  # 带时标CP56Time2a的设定值命令，归一化值
        C_SE_TB_1 = 62,  # 带时标CP56Time2a的设定值命令，标度化值
        C_SE_TC_1 = 63,  # 带时标CP56Time2a的设定值命令，短浮点数
        C_BO_TA_1 = 64,  # 带时标CP56Time2a的32比特串
        # 监视方向的系统信息
        M_EI_NA_1 = 70,  # 初始化结束
        # 控制方向的系统信息
        C_IC_NA_1 = 100,  # 总召唤命令
        C_CI_NA_1 = 101,  # 电能脉冲召唤命令
        C_RD_NA_1 = 102,  # 读命令
        C_CS_NA_1 = 103,  # 时钟同步命令
        # C_TS_NA_1 = 103,  # 测试命令
        # C_RP_NA_1 = 105,  # 复位进程命令
        # C_TS_NA_1 = 107,  # 带时标CP56Time2a的测试命令
        # 控制方向的参数命令
        # P_ME_NA_1 = 110,  # 测量值参数，归一化值
        # P_ME_NB_1 = 111,  # 测量值参数，标度化值
        # P_ME_NC_1 = 112,  # 测量值参数，短浮点数
        # P_AC_NA_1 = 113,  # 参数激活
        # 文件传输
        # F_FR_NA_1 = 120,  # 文件已准备好
        # F_SR_NA_1 = 121,  # 节已准备好
        # F_SC_NA_1 = 122,  # 召唤目录，选择文件，召唤文件，召唤节
        # F_LS_NA_1 = 123,  # 最后的节，最后的段
        # F_AF_NA_1 = 124,  # 确认文件，确认节
        # F_SG_NA_1 = 125,  # 段
        # F_DR_TA_1 = 126,  # 目录（监视方向有效）
        # F_SC_NB_1 = 127,  # 查询日志(QueryLog)

    class Cause(IntEnum):
        unused = 0,  # 未用
        percyc = 1,  # 周期、循环
        back = 2,  # 背景扫描
        spont = 3,  # 突发（自发）
        init = 4,  # 初始化
        req = 5,  # 请求或者被请求
        act = 6,  # 激活
        actcon = 7,  # 激活确认
        deact = 8,  # 停止激活
        deactcon = 9,  # 停止激活确认
        actterm = 10,  # 激活终止
        retrem = 11,  # 远方命令引起的返送信息
        retloc = 12,  # 当地命令引起的返送信息
        file = 13,  # 文件传输
        introgen = 20,  # 响应站召唤
        inro1 = 21,  # 响应第1组召唤
        inro2 = 22,  # 响应第2组召唤
        inro3 = 23,  # 响应第3组召唤
        inro4 = 24,  # 响应第4组召唤
        inro5 = 25,  # 响应第5组召唤
        inro6 = 26,  # 响应第6组召唤
        inro7 = 27,  # 响应第7组召唤
        inro8 = 28,  # 响应第8组召唤
        inro9 = 29,  # 响应第9组召唤
        inro10 = 30,  # 响应第10组召唤
        inro11 = 31,  # 响应第11组召唤
        inro12 = 32,  # 响应第12组召唤
        inro13 = 33,  # 响应第13组召唤
        inro14 = 34,  # 响应第14组召唤
        inro15 = 35,  # 响应第15组召唤
        inro16 = 36,  # 响应第16组召唤
        reqcogen = 37,  # 响应计数量（累计量）站（总）召唤
        reqco1 = 38,  # 响应第1组计数量（累计量）召唤
        reqco2 = 39,  # 响应第2组计数量（累计量）召唤
        reqco3 = 40,  # 响应第3组计数量（累计量）召唤
        reqco4 = 41,  # 响应第4组计数量（累计量）召唤
        badtyp = 44,  # 未知的类型标识
        badre = 45,  # 未知的传送原因
        badad = 46,  # 未知的应用服务数据单元公共地址
        badad2 = 47,  # 未知的信息对象地址

    # 带品质描述词的单点信息
    SIQ = BitStruct(
        "SIQ",
        Bit("IV"),  # 0 有效 1 无效
        Bit("NT"),  # 0 当前值 1 非当前值
        Bit("SB"),  # 0 未被取代 1 被取代
        Bit("BL"),  # 0 未被闭锁 1 被闭锁
        Padding(3),
        Bit("value"),  # 单点信息 0 开 1 合
    )

    # 带品质描述词的双点信息
    DIQ = BitStruct(
        "DIQ",
        Bit("IV"),  # 0 有效 1 无效
        Bit("NT"),  # 0 当前值 1 非当前值
        Bit("SB"),  # 0 未被取代 1 被取代
        Bit("BL"),  # 0 未被闭锁 1 被闭锁
        Padding(2),
        Bits("value", 2),  # 双点信息 0 中间状态 1 确定开 2 确定合 3 不确定
    )

    # 品质描述词
    QDS = BitStruct(
        "QDS",
        Bit("IV"),  # 0 有效 1 无效
        Bit("NT"),  # 0 当前值 1 非当前值
        Bit("SB"),  # 0 未被取代 1 被取代
        Bit("BL"),  # 0 未被闭锁 1 被闭锁
        Padding(3),
        Flag("OV", truth=0, falsehood=1, default=True),  # 0 未溢出 1 溢出
    )

    # 继电保护设备事件的品质描述词
    QDP = BitStruct(
        "QDP",
        Bit("IV"),  # 0 有效 1 无效
        Bit("NT"),  # 0 当前值 1 非当前值
        Bit("SB"),  # 0 未被取代 1 被取代
        Bit("BL"),  # 0 未被闭锁 1 被闭锁
        Bit("EI"),  # 0 动作时间有效 1 动作时间无效
        Padding(3),
    )

    # 带瞬变状态指示的值
    VTI = BitStruct(
        "VTI",
        Flag("VT"),  # 0 设备未在瞬变状态 1 设备处于瞬变状态
        Bits("value", 7),  # 值
    )

    # 二进制计数器读数
    BCR = Struct(
        "BCR",
        ULInt32("value"),  # 读数
        EmbeddedBitStruct(
            Bit("IV"),  # 0 有效 1 无效
            Bit("CA"),  # 0 上次读数后计数器未被调整 1 被调整
            Bit("CY"),  # 0 未溢出 1 溢出
            Bits("sq", 5),  # 0~31 顺序号
        ),
    )

    # 继电保护设备单个事件
    SEP = BitStruct(
        "SEP",
        Bit("IV"),  # 0 有效 1 无效
        Bit("NT"),  # 0 当前值 1 非当前值
        Bit("SB"),  # 0 未被取代 1 被取代
        Bit("BL"),  # 0 未被闭锁 1 被闭锁
        Bit("EI"),  # 0 动作时间有效 1 动作时间无效
        Padding(1),
        Bits("value", 2),  # 事件状态 0 中间状态 1 确定开 2 确定合 3 不确定
    )

    # 测量值参数限定词
    QPM = BitStruct(
        "QPM",
        Bit("POP"),  # 0 运行 1 未运行
        Bit("LPC"),  # 0 未改变 1 改变
        Bits("KPA", 6),  # 参数类别 0 未用 1 门限值 2 平滑系数（滤波时间常数） 3 下限 4 上限
    )

    # 设定命令限定词
    QOS = BitStruct(
        "QOS",
        Bit("se"),  # 0 执行 1 选择
        Bits("QL", 7),  # 0 缺省
    )

    # 二进制时间
    cp56time2a = ExprAdapter(
        Struct(
            "cp56time2a",
            ULInt16("Millisecond"),  # 0~59999
            EmbeddedBitStruct(
                Bit("IV"),  # 0 有效 1 无效
                Padding(1),
                Bits("Minute", 6),  # 0~59
                Bit("SU"),  # 0 标准时间 1 夏季时间
                Padding(2),
                Bits("Hour", 5),  # 0~23
                Bits("Week", 3),  # 1~7
                Bits("Day", 5),  # 1~31
                Padding(4),
                Nibble("Month"),  # 1~12
                Padding(1),
                Bits("Year", 7),  # 0~99  取年份的后两位 例如: 2015 -> 15
            )
        ),
        encoder=lambda time, ctx: Container(Year=time.year % 2000,
                                            Month=time.month, Day=time.day,
                                            Week=time.isoweekday(),
                                            Hour=time.hour, SU=0,
                                            Minute=time.minute, IV=0,
                                            Millisecond=time.microsecond // 1000 + time.second * 1000),
        decoder=lambda obj, ctx: datetime(year=obj.Year + 2000,
                                                   month=obj.Month, day=obj.Day,
                                                   hour=obj.Hour,
                                                   minute=obj.Minute,
                                                   second=obj.Millisecond // 1000,
                                                   microsecond=obj.Millisecond % 1000 * 1000)
    )

    @staticmethod
    def _decode_cp24time2a(obj, _):
        now = datetime.now()
        return datetime(now.year, now.month, now.day, now.hour, minute=obj.Minute, second=obj.Millisecond // 1000, microsecond=obj.Millisecond % 1000 * 1000)

    # 二进制时间
    cp24time2a = ExprAdapter(
        Struct("cp24time2a",
               ULInt16("Millisecond"),  # 0~59999
               EmbeddedBitStruct(
                   Bit("IV"),  # 0 有效 1 无效
                   Padding(1),
                   Bits("Minute", 6),  # 0~59
               )),
        encoder=lambda time, ctx: Container(Minute=time.minute, IV=0, Millisecond=time.microsecond // 1000 + time.second * 1000),
        decoder=_decode_cp24time2a
    )

    # 单命令
    SCO = BitStruct(
        "SCO",
        Bit("se"),  # 0 执行 1 选择
        Bits("QU", 5),  # 0 无定义 1 短脉冲持续时间 2 长脉冲持续时间 3 持续输出
        Padding(1),
        Bit("value"),  # 单命令状态 0 开 1 合
    )

    # 双命令
    DCO = BitStruct(
        "DCO",
        Bit("se"),  # 0 执行 1 选择
        Bits("QU", 5),  # 0 无定义 1 短脉冲持续时间 2 长脉冲持续时间 3 持续输出
        Bits("value", 2),  # 双命令状态 0 不允许 1 开 2 合 3 不允许
    )

    # 步调节命令
    RCO = BitStruct(
        "RCO",
        Bit("se"),  # 0 执行 1 选择
        Bits("QU", 5),  # 0 无定义 1 短脉冲持续时间 2 长脉冲持续时间 3 持续输出
        Bits("value", 2),  # 双命令状态 0 不允许 1 降一步 2 升一步 3 不允许
    )

    # 1 单点信息
    ASDU_M_SP_NA_1 = Struct(
        "ASDU_M_SP_NA_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        Embed(SIQ),
    )

    # 2 带时标的单点信息
    ASDU_M_SP_TA_1 = Struct(
        "ASDU_M_SP_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(SIQ),
        cp24time2a,
    )

    # 3 双点信息
    ASDU_M_DP_NA_1 = Struct(
        "ASDU_M_DP_NA_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        Embed(DIQ),
    )

    # 4 带时标的双点信息
    ASDU_M_DP_TA_1 = Struct(
        "ASDU_M_DP_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(DIQ),
        cp24time2a,
    )

    # 5 步位置信息
    ASDU_M_ST_NA_1 = Struct(
        "ASDU_M_ST_NA_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        Embed(VTI),
        Embed(QDS),
    )

    # 6 带时标的步位置信息
    ASDU_M_ST_TA_1 = Struct(
        "ASDU_M_ST_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(VTI),
        Embed(QDS),
        cp24time2a,
    )

    # 7 32比特串
    ASDU_M_BO_NA_1 = Struct(
        "ASDU_M_BO_NA_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        ULInt32("value"),
        Embed(QDS),
    )

    # 8 带时标的32比特串
    ASDU_M_BO_TA_1 = Struct(
        "ASDU_M_BO_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt32("value"),
        Embed(QDS),
        cp24time2a,
    )

    # 9 测量值，归一化值
    ASDU_M_ME_NA_1 = Struct(
        "ASDU_M_ME_NA_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        ULInt16("value"),
        Embed(QDS),
    )

    # 10 测量值，带时标的归一化值
    ASDU_M_ME_TA_1 = Struct(
        "ASDU_M_ME_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QDS),
        cp24time2a,
    )

    # 11 测量值，标度化值
    ASDU_M_ME_NB_1 = Struct(
        "ASDU_M_SP_NB_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        ULInt16("value"),
        Embed(QDS),
    )

    # 12 测量值，带时标的标度化值
    ASDU_M_ME_TB_1 = Struct(
        "ASDU_M_ME_TB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QDS),
        cp24time2a,
    )

    # 13 测量值，短浮点数
    ASDU_M_ME_NC_1 = Struct(
        "ASDU_M_ME_NC_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        LFloat32("value"),
        Embed(QDS),
    )

    # 14 测量值，带时标短浮点数
    ASDU_M_ME_TC_1 = Struct(
        "ASDU_M_ME_TC_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        LFloat32("value"),
        Embed(QDS),
        cp24time2a,
    )

    # 15 累计量
    ASDU_M_IT_NA_1 = Struct(
        "ASDU_M_IT_NA_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        Embed(BCR),
    )

    # 16 带时标的累计量
    ASDU_M_IT_TA_1 = Struct(
        "ASDU_M_IT_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(BCR),
        cp24time2a,
    )

    # 20 具有状态变位检出的成组单点信息
    ASDU_M_PS_NA_1 = Struct(
        "ASDU_M_PS_NA_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        ULInt16("value"),  # 每一位 0 开 1 合
        ULInt16("CD"),  # 每一位 0 ST对应位未改变 1 ST对应位有改变
        Embed(QDS),
    )

    # 21 测量值，不带品质描述的归一化值
    ASDU_M_ME_ND_1 = Struct(
        "ASDU_M_ME_ND_1",
        EmbeddedBitStruct(If(lambda ctx: ctx._.sq == 0, BitField("address", 24, swapped=True))),
        ULInt16("value"),
    )

    # 30 带时标CP56Time2a的单点信息
    ASDU_M_SP_TB_1 = Struct(
        "ASDU_M_SP_TB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(SIQ),
        cp56time2a,
    )

    # 31 带时标CP56Time2a的双点信息
    ASDU_M_DP_TB_1 = Struct(
        "ASDU_M_DP_TB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(DIQ),
        cp56time2a,
    )

    # 32 带时标CP56Time2a的步位置信息
    ASDU_M_ST_TB_1 = Struct(
        "ASDU_M_ST_TB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(VTI),
        Embed(QDS),
        cp56time2a,
    )

    # 33 带时标CP56Time2a的32位串
    ASDU_M_BO_TB_1 = Struct(
        "ASDU_M_BO_TB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt32("value"),
        Embed(QDS),
        cp56time2a,
    )

    # 34 带时标CP56Time2a的归一化测量值
    ASDU_M_ME_TD_1 = Struct(
        "ASDU_M_ME_TD_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QDS),
        cp56time2a,
    )

    # 35 测量值，带时标CP56Time2a的标度化值
    ASDU_M_ME_TE_1 = Struct(
        "ASDU_M_ME_TE_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QDS),
        cp56time2a,
    )

    # 36 测量值，带时标CP56Time2a的短浮点数
    ASDU_M_ME_TF_1 = Struct(
        "ASDU_M_ME_TF_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        LFloat32("value"),
        Embed(QDS),
        cp56time2a,
    )

    # 37 带时标CP56Time2a的累计值
    ASDU_M_IT_TB_1 = Struct(
        "ASDU_M_IT_TB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(BCR),
        cp56time2a,
    )

    # 38 带时标CP56Time2a的继电保护装置事件
    ASDU_M_EP_TD_1 = Struct(
        "ASDU_M_EP_TD_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(SEP),
        ULInt16("CP16Time2a"),
        cp56time2a,
    )

    # 45 单命令
    ASDU_C_SC_NA_1 = Struct(
        "ASDU_C_SC_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(SCO),
    )

    # 46 双命令
    ASDU_C_DC_NA_1 = Struct(
        "ASDU_C_DC_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(DCO),
    )

    # 47 步调节命令
    ASDU_C_RC_NA_1 = Struct(
        "ASDU_C_RC_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(RCO),
    )

    # 48 设定值命令，归一化值
    ASDU_C_SE_NA_1 = Struct(
        "ASDU_C_SE_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QOS),
    )

    # 49 设定值命令，标度化值
    ASDU_C_SE_NB_1 = Struct(
        "ASDU_C_SE_NB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QOS),
    )

    # 50 设定值命令，短浮点数
    ASDU_C_SE_NC_1 = Struct(
        "ASDU_C_SE_NC_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        LFloat32("value"),
        Embed(QOS),
    )

    # 51 设定值命令，32位比特串
    ASDU_C_BO_NA_1 = Struct(
        "ASDU_C_BO_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt32("value"),
    )

    # 58 带时标CP56Time2a的单命令
    ASDU_C_SC_TA_1 = Struct(
        "ASDU_C_SC_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(SCO),
        cp56time2a,
    )

    # 59 带时标CP56Time2a的双命令
    ASDU_C_DC_TA_1 = Struct(
        "ASDU_C_DC_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(DCO),
        cp56time2a,
    )

    # 60 带时标CP56Time2a的步调节命令
    ASDU_C_RC_TA_1 = Struct(
        "ASDU_C_RC_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        Embed(RCO),
        cp56time2a,
    )

    # 61 带时标CP56Time2a的设定值命令，归一化值
    ASDU_C_SE_TA_1 = Struct(
        "ASDU_C_SE_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QOS),
        cp56time2a,
    )

    # 62 带时标CP56Time2a的设定值命令，标度化值
    ASDU_C_SE_TB_1 = Struct(
        "ASDU_C_SE_TB_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt16("value"),
        Embed(QOS),
        cp56time2a,
    )

    # 63 带时标CP56Time2a的设定值命令，短浮点数
    ASDU_C_SE_TC_1 = Struct(
        "ASDU_C_SE_TC_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        LFloat32("value"),
        Embed(QOS),
        cp56time2a,
    )

    # 64 带时标CP56Time2a的32比特串
    ASDU_C_BO_TA_1 = Struct(
        "ASDU_C_BO_TA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        ULInt32("value"),
        cp56time2a,
    )

    # 70 M_EI_NA_1 初始化结束
    ASDU_M_EI_NA_1 = Struct(
        "ASDU_M_EI_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
    )

    # 100 总召唤命令
    ASDU_C_IC_NA_1 = Struct(
        "ASDU_C_IC_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        # ULInt8("QOI"),  # 0 未用 20 站召唤（总招） 21~36 第1~16组召唤
        Magic(b"\x14"),
    )

    # 101 电能脉冲召唤命令
    ASDU_C_CI_NA_1 = Struct(
        "ASDU_C_CI_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
        # EmbeddedBitStruct(
        #     Bits("FRZ", 2),
        #     # 0 读（无冻结复位） 1 计数量冻结不带复位（累加值） 2 冻结带复位（增量信息） 3 计数量复位
        #     Bits("RQT", 6),  # 0 未用 1~4 请求1~4组计数量 5 请求总的计数量（总招）
        # ),

    )

    # 102 读命令
    ASDU_C_RD_NA_1 = Struct(
        "ASDU_C_RD_NA_1",
        EmbeddedBitStruct(BitField("address", 24, swapped=True)),  # 信息对象地址
    )

    # 103 时钟同步命令
    ASDU_C_CS_NA_1 = Struct(
        "ASDU_C_CS_NA_1",
        Padding(3),
        cp56time2a,
    )


class IECFrame:

    ASDU_Part = Struct(
        "ASDU",
        # 类型标识
        ExprAdapter(Byte("TYP"), encoder=lambda obj, ctx: obj, decoder=lambda obj, ctx: IECFrameDefine.TYP(obj & 0xff)),
        # 可变结构限定词
        EmbeddedBitStruct(
            Bit("sq"),  # 单个或者顺序寻址 0 信息对象地址不连续（包含地址） 1 信息对象地址连续（不包含地址）
            Bits("sq_count", 7),  # 数目 0 不含信息对象 1~127 信息元素的数目
        ),
        # # 传送原因 COT
        ExprAdapter(ULInt16("Cause"), encoder=lambda obj, ctx: obj, decoder=lambda obj, ctx: IECFrameDefine.Cause(obj & 0x3F)),

        # ASDU公共地址
        ULInt16("GlobalAddress"),  # 0 未用 1~65534 站地址 65535 全局地址
        EmbeddedBitStruct(If(lambda ctx: ctx.sq == 1, BitField("StartAddress", 24, swapped=True))),
        # 信息对象

        Array(lambda ctx: ctx.sq_count, Switch("data", keyfunc=lambda ctx: ctx.TYP.name, default=Pass, cases={name: getattr(IECFrameDefine, f'ASDU_{name}') for name in IECFrameDefine.TYP.__members__}),),
    )

    @staticmethod
    def exact_names(obj):
        if obj.__class__.__name__ == "Struct":
            content = Container()
            for sub_con in obj.subcons:
                if sub_con is not None:
                    content.update(IECFrame.exact_names(sub_con))
            return content
        elif obj.__class__.__name__ in ("Restream", "Reconfig", "Buffered"):
            return IECFrame.exact_names(obj.subcon)
        return {} if obj.name is None else {obj.name: datetime.now() if obj.name in ("cp56time2a", "cp24time2a") else 0}

    @staticmethod
    def init_frame(_, apci1=None, apci2=None, typ=None, cause=IECFrameDefine.Cause.unused, sq_count=1, sq=0):
        cc = Container(APCI1=apci1, APCI2=apci2, length=0, ASDU=None)
        if typ is not None:
            cc.ASDU = Container(TYP=typ, sq=sq, sq_count=sq_count, StartAddress=0, Cause=cause, GlobalAddress=1, data=list())
            for num in range(cc.ASDU.sq_count):
                cc.ASDU.data.append(IECFrame.exact_names(globals()["ASDU_" + typ.name]))
        return cc

    @staticmethod
    def build_isu(_, obj):
        build_bin = IECFrame.iec_104.build(obj)
        return b"\x68%c%b" % (len(build_bin) - 2, build_bin[2:])

    iec_head = Struct(
        "iec104_head",
        Magic(b"\x68"),
        Byte("length"),  # 帧长度（不算帧头和长度，总帧长=length+2）
    )

    iec_104 = Struct(
        "iec104",
        Magic(b"\x68"),
        Byte("length"),
        ExprAdapter(
            ULInt16("APCI1"),
            encoder=lambda obj, ctx: obj if isinstance(obj, IECFrameDefine.UFrame) else 1 if obj == "S" else obj << 1,
            decoder=lambda obj, ctx: obj >> 1 if obj & 1 == 0 else "S" if obj & 3 == 1 else IECFrameDefine.UFrame(obj),
        ),
        ExprAdapter(
            ULInt16("APCI2"),
            encoder=lambda obj, ctx: 0 if obj is None else obj << 1,
            decoder=lambda obj, ctx: obj >> 1,
        ),
        # 只有I帧包含ASDU部分，S和U帧没有
        If(lambda ctx: not isinstance(ctx.APCI1, IECFrameDefine.UFrame) and ctx.APCI1 != 'S', ASDU_Part),
    )

    setattr(Struct, "init_frame", classmethod(init_frame))
    setattr(Struct, "build_isu", classmethod(build_isu))


class IOTIEC104(IOTDriver):

    class ASDU(Packet):
        name = 'ASDU'

        fields_desc = [
            ByteEnumField('Type', None, IECDefine.ASDU_TYPE),
            ByteEnumField('SQ', None, IECDefine.ASDU_SQ),
            ByteField('Num', 0),
            ByteEnumField('Cause', None, IECDefine.ASDU_CAUSE),
            ByteEnumField('PN', 0x00, IECDefine.ASDU_PN),
            ByteField('Test', None),
            ByteField('OA', None),
            LEShortField('Addr', None),
            PacketListField('IOA', None)
        ]

        def do_dissect(self, s):
            self.Type = s[0] & 0xff   # 类型(1)
            self.SQ = s[1] & 0x80 == 0x80   # 限定词(1)
            self.Num = s[1] & 0x7f  # 数量
            self.Cause = s[2] & 0x3F    # 原因
            self.PN = s[2] & 0x40   # 第6位为P/N = 0 肯定 ； P/N = 1 否定 （正常为P/N = 0；P/N = 1说明该报文无效
            self.Test = s[2] & 0x80 # 第7为为测试 T = 0 未试验 ； T = 1 试验 （一般 T= 0）
            self.OA = s[3]          # 源发地址：用来记录来时哪个主站的响应数据，一般写 0；
            self.Addr = unpack('<H', s[4:6])[0] # 公共地址

            flag = True
            IOAS = list()
            remain = s[6:]

            idx = 6
            offset = 0
            if self.Type not in IECData.IOAS.keys():
                raise Exception(f"unsupport type({self.Type}")
            else:
                ioa_type = IECData.IOAS.get(self.Type)
                ioa_length = IECData.IOALEN.get(self.Type)
                if self.SQ:
                    for i in range(1, self.Num + 1):
                        if flag:
                            if len(remain[:ioa_length]) >= ioa_length:
                                if ioa_type is not None:
                                    IOAS.append(ioa_type(remain[:ioa_length]))
                                    offset = IOAS[0].IOA
                                remain = remain[ioa_length:]
                                idx = idx + ioa_length
                                ioa_length = ioa_length - 3
                        else:
                            if len(remain[:ioa_length]) >= ioa_length:
                                _offset = pack("<H", (i - 1) + offset) + b'\x00'  # See 7.2.2.1 of IEC 60870-5-101
                                if ioa_type is not None:
                                    IOAS.append(ioa_type(_offset + remain[:ioa_length]))
                                remain = remain[ioa_length:]
                                idx = idx + ioa_length
                        flag = False
                else:
                    for i in range(1, self.Num + 1):
                        if len(remain[:ioa_length]) >= ioa_length:
                            if ioa_type is not None:
                                IOAS.append(ioa_type(remain[: ioa_length]))
                            remain = remain[ioa_length:]
                            idx = idx + ioa_length
            self.IOA = IOAS
            return s[idx:]

        def do_build(self):
            s = bytearray()
            s.append(self.Type)
            s.append(self.SQ | self.Num)
            s.append(self.Test | self.PN | self.Cause)
            s.append(self.OA)
            s.append(int(self.Addr) & 0xff)
            s.append(int(self.Addr) >> 8)
            s = bytes(s)
            if self.IOA is not None:
                for i in self.IOA:
                    s += i.build()

            return s

        def info(self, pkt: Packet = None):
            pkt = self if pkt is None else pkt
            values = {}
            for key in pkt.fields.keys():
                if isinstance(pkt.fields[key], list):
                    for filed in pkt.fields[key]:
                        if isinstance(filed, Packet):
                            if filed.name not in values.keys():
                                values[filed.name] = []
                            values[filed.name].append(self.info(filed))
                elif isinstance(pkt.fields[key], Packet):
                    values[pkt.fields[key].name] = self.info(pkt.fields[key])
                else:
                    values[key] = pkt.fields[key]
            return values

        def values(self):
            if isinstance(self.IOA, list) and len(self.IOA) > 0:
                return {f"{self.Type}_{k}": v for IOA in self.IOA for k, v in IOA.value().items()}
            return {}

    class APCI(Packet):
        name = 'ACPI'

        fields_desc = [
            XByteField('START', 0x68),      # 68H
            ByteField('ApduLen', 4),        # 长度
            ByteEnumField('Type', 0x00, IECDefine.APCI_TYPE),   # 帧类型
            ConditionalField(XByteField('UType', None), lambda pkt: pkt.Type == 0x03),  # U帧类型
            ConditionalField(ShortField('Tx', 0x00), lambda pkt: pkt.Type == 0x00),
            ConditionalField(ShortField('Rx', 0x00), lambda pkt: pkt.Type < 3),
        ]

        def do_dissect(self, s):
            self.START = s[0]       # 68H
            self.ApduLen = s[1]     # 长度
            self.Type = s[2] & 0x03 if bool(s[2] & 0x01) else 0x00
            if self.Type == 3:      # U帧
                self.UType = (s[2] & 0xfc) >> 2
            else:
                if self.Type == 0:  # I帧
                    self.Tx = (s[3] << 7) | (s[2] >> 1)
                self.Rx = (s[5] << 7) | (s[4] >> 1)
            return s[6:]

        def dissect(self, s):
            s = self.pre_dissect(s)
            s = self.do_dissect(s)
            s = self.post_dissect(s)
            payl, pad = self.extract_padding(s)
            self.do_dissect_payload(payl)
            if pad:
                self.add_payload(IOTIEC104.APDU(pad))

        def do_build(self):
            s = list(range(6))
            s[0] = 0x68
            s[1] = self.ApduLen
            if self.Type == 0x03:
                s[2] = ((self.UType << 2) & 0xfc) | self.Type
                s[3] = 0
                s[4] = 0
                s[5] = 0
            else:
                if self.Type == 0x00:
                    s[2] = ((self.Tx << 1) & 0x00fe) | self.Type
                    s[3] = ((self.Tx << 1) & 0xff00) >> 8
                else:
                    s[2] = self.Type
                    s[3] = 0
                s[4] = (self.Rx << 1) & 0x00fe
                s[5] = ((self.Rx << 1) & 0xff00) >> 8
            s = bytes(s)
            if self.haslayer('ASDU'):
                s += self.payload.build()
            return s

        def extract_padding(self, s):
            if self.Type == 0x00 and self.ApduLen > 4:
                return s[:self.ApduLen - 4], s[self.ApduLen - 4:]
            return None, s

        def do_dissect_payload(self, s):
            if s is not None:
                p = IOTIEC104.ASDU(s, _internal=1, _underlayer=self)
                self.add_payload(p)

        def info(self):
            values = {}
            for key in self.fields.keys():
                values[key] = self.fields[key]
            return values

    class APDU(Packet):
        name = 'APDU'

        def dissect(self, s):
            s = self.pre_dissect(s)
            s = self.do_dissect(s)
            s = self.post_dissect(s)
            payl, pad = self.extract_padding(s)
            self.do_dissect_payload(payl)
            if pad:
                if pad[0] in [0x68]:
                    self.add_payload(IOTIEC104.APDU(pad, _internal=1, _underlayer=self))
                else:
                    self.add_payload(pack_padding(pad))

        def do_dissect(self, s):
            apci = IOTIEC104.APCI(s, _internal=1, _underlayer=self)
            self.add_payload(apci)

        def info(self):
            values = {}
            if not isinstance(self.payload, NoPayload):
                values[self.payload.name] = self.payload.info()
                if not isinstance(self.payload.payload, NoPayload):
                    values[self.payload.payload.name] = self.payload.payload.info()
            return values

    class ASDU_C(Packet):
        name = 'ASDU'

        fields_desc = [
            ByteEnumField('Type', None, IECDefine.ASDU_TYPE),
            ByteEnumField('SQ', None, IECDefine.ASDU_SQ),
            ByteField('Num', 0),
            ByteEnumField('Cause', None, IECDefine.ASDU_CAUSE),
            ByteEnumField('PN', 0x00, IECDefine.ASDU_PN),
            ByteField('Test', None),
            ByteField('OA', None),
            LEShortField('Addr', None),
            PacketListField('IOA', None)
        ]

        def do_dissect(self, s):
            self.Type = s[0] & 0xff   # 类型(1)
            self.SQ = s[1] & 0x80 == 0x80   # 限定词(1)
            self.Num = s[1] & 0x7f  # 数量
            self.Cause = s[2] & 0x3F    # 原因
            self.PN = s[2] & 0x40   # 第6位为P/N = 0 肯定 ； P/N = 1 否定 （正常为P/N = 0；P/N = 1说明该报文无效
            self.Test = s[2] & 0x80 # 第7为为测试 T = 0 未试验 ； T = 1 试验 （一般 T= 0）
            self.OA = s[3]          # 源发地址：用来记录来时哪个主站的响应数据，一般写 0；
            self.Addr = unpack('<H', s[4:6])[0] # 公共地址

            flag = True
            IOAS = list()
            remain = s[6:]
            idx = 6
            self.IOA = IOAS
            return s[idx:]

        def do_build(self):
            s = bytearray()
            s.append(self.Type)
            s.append(self.SQ | self.Num)
            s.append(self.Test | self.PN | self.Cause)
            s.append(self.OA)
            s.append(int(self.Addr) & 0xff)
            s.append(int(self.Addr) >> 8)
            s = bytes(s)
            if self.IOA is not None:
                for i in self.IOA:
                    s += i.build()

            return s

        def info(self, pkt: Packet = None):
            pkt = self if pkt is None else pkt
            values = {}
            for key in pkt.fields.keys():
                if isinstance(pkt.fields[key], list):
                    for filed in pkt.fields[key]:
                        if isinstance(filed, Packet):
                            if filed.name not in values.keys():
                                values[filed.name] = []
                            values[filed.name].append(self.info(filed))
                elif isinstance(pkt.fields[key], Packet):
                    values[pkt.fields[key].name] = self.info(pkt.fields[key])
                else:
                    values[key] = pkt.fields[key]
            return values

    class APCI_C(Packet):
        name = 'ACPI'

        fields_desc = [
            XByteField('START', 0x68),      # 68H
            ByteField('ApduLen', 4),        # 长度
            ByteEnumField('Type', 0x00, IECDefine.APCI_TYPE),   # 帧类型
            ConditionalField(XByteField('UType', None), lambda pkt: pkt.Type == 0x03),  # U帧类型
            ConditionalField(ShortField('Tx', 0x00), lambda pkt: pkt.Type == 0x00),
            ConditionalField(ShortField('Rx', 0x00), lambda pkt: pkt.Type < 3),
        ]

        def do_dissect(self, s):
            self.START = s[0]       # 68H
            self.ApduLen = s[1]     # 长度
            self.Type = s[2] & 0x03 if bool(s[2] & 0x01) else 0x00
            if self.Type == 3:      # U帧
                self.UType = (s[2] & 0xfc) >> 2
            else:
                if self.Type == 0:  # I帧
                    self.Tx = (s[3] << 7) | (s[2] >> 1)
                self.Rx = (s[5] << 7) | (s[4] >> 1)
            return s[6:]

        def dissect(self, s):
            s = self.pre_dissect(s)
            s = self.do_dissect(s)
            s = self.post_dissect(s)
            payl, pad = self.extract_padding(s)
            self.do_dissect_payload(payl)
            if pad:
                self.add_payload(IOTIEC104.APDU_C(pad))

        def do_build(self):
            s = list(range(6))
            s[0] = 0x68
            s[1] = self.ApduLen
            if self.Type == 0x03:
                s[2] = ((self.UType << 2) & 0xfc) | self.Type
                s[3] = 0
                s[4] = 0
                s[5] = 0
            else:
                if self.Type == 0x00:
                    s[2] = ((self.Tx << 1) & 0x00fe) | self.Type
                    s[3] = ((self.Tx << 1) & 0xff00) >> 8
                else:
                    s[2] = self.Type
                    s[3] = 0
                s[4] = (self.Rx << 1) & 0x00fe
                s[5] = ((self.Rx << 1) & 0xff00) >> 8
            s = bytes(s)
            if self.haslayer('ASDU'):
                s += self.payload.build()
            return s

        def extract_padding(self, s):
            if self.Type == 0x00 and self.ApduLen > 4:
                return s[:self.ApduLen - 4], s[self.ApduLen - 4:]
            return None, s

        def do_dissect_payload(self, s):
            if s is not None:
                p = IOTIEC104.ASDU_C(s, _internal=1, _underlayer=self)
                self.add_payload(p)

        def info(self):
            values = {}
            for key in self.fields.keys():
                values[key] = self.fields[key]
            return values

    class APDU_C(Packet):
        name = 'APDU'

        def dissect(self, s):
            s = self.pre_dissect(s)
            s = self.do_dissect(s)
            s = self.post_dissect(s)
            payl, pad = self.extract_padding(s)
            self.do_dissect_payload(payl)
            if pad:
                if pad[0] in [0x68]:
                    self.add_payload(IOTIEC104.APDU_C(pad, _internal=1, _underlayer=self))
                else:
                    self.add_payload(pack_padding(pad))

        def do_dissect(self, s):
            apci = IOTIEC104.APCI_C(s, _internal=1, _underlayer=self)
            self.add_payload(apci)

        def info(self):
            values = {}
            if not isinstance(self.payload, NoPayload):
                values[self.payload.name] = self.payload.info()
                if not isinstance(self.payload.payload, NoPayload):
                    values[self.payload.payload.name] = self.payload.payload.info()
            return values

    class IEC104:
        """IEC连接参数"""

        T0 = 10  # 30s 主站连接从站超时 - 连接建立超时
        T1 = 15  # 15s 发送U帧测试帧到收到测试确认帧的时间 如果超时关闭连接(发送I帧或U帧后，等待对方应答，等待超过T1则重启链路) - 发送或测试超时
        T2 = 10  # 10s 从站主动上报数据（突发）到收到S帧确认帧的时间  从站相应召唤到收到S帧确认帧的时间(接收到I帧后等待T2时间，然后发送对I帧的应答) - 无数据报文超时  从站发送完所有I帧，但未收到S帧
        T3 = 20  # 20s 没有任何数据时的超时时间，超时发送U帧测试帧 其中 t3>t1>t2(T3时间内未收到任何报文，发送TESTFR) - 长期空闲超时
        K = 12  # 从站发送12个AODU报文就必须收到确认帧，否则关闭数据传送，用于从站(发送方在有k个I格式报文未得到对方的确认时，将停止数据传送)
        W = 8  # 主站收到8个APDU就必须回复一个S帧的确认帧，用于主站(接收方最迟在接收了w个I格式报文后应发出认可) w不能超过k的2/3

        def __init__(self, host: str, port: int,  t0: Optional[float] = 10, t1: Optional[float] = 15, t2: Optional[float] = 10, t3: Optional[float] = 20, k: Optional[int] = 12, w: Optional[int] = 8, **kwargs):
            self.T0 = t0 if t0 is not None else self.T0
            self.T1 = t1 if t1 is not None else self.T1
            self.T2 = t2 if t2 is not None else self.T2
            self.T3 = t3 if t3 is not None else self.T3
            self.K = k if k is not None else self.K
            self.W = w if w is not None else self.W
            self.HOST = host
            self.PORT = port
            self.PZ = kwargs.get('pz', 0)     # 总召间隔时间
            self.PD = kwargs.get('pd', 0)     # 电度间隔

            self.is_connected = False   # 连接状态
            self.client = None      # TCP连接
            self.last_frame_received_time = None  # 最后收到数据时间
            self.last_frame_received_i_time = None  # 最后收到I帧数据时间
            self.last_frame_send_time = None  # 最后发送数据时间
            self.last_frame_send_u_time = None      # 最后发送U帧时间 需要确认 否则认为超时
            self.last_frame_send_s_time = None      # 最后发送S帧时间
            self.last_frame_send_z_time = None      # 最后发送总召时间
            self.last_frame_send_d_time = None      # 最后发送电度召唤时间

            self.event_for_startdt_con = 0      # 等待启动命令事件
            self.event_for_zongzhao = 0         # 等待总召结束事件 0:send 1: config 2 terminal
            self.event_for_diandu = 0           # 等待电度结束事件

            self.rsn_i = 0    # 接收到的I帧 用于判断是否发送S帧
            self.ssn = 0        # 最新发送序列号
            self.rsn = 0        # 最新收到的接收序列号
            self.logging_call = None

        def __str__(self):
            return f"{self.HOST}:{self.PORT}"

        def __del__(self):
            self.exit()

        def exit(self):
            self.set_is_connected(False)

        def set_logging(self, logging_call):
            self.logging_call = logging_call

        def logging(self, content: str):
            if self.logging_call:
                self.logging_call(content=content)

        def info(self, **kwargs) -> dict:
            return {'ssn': self.ssn, 'rsn_i': self.rsn_i, 'rsn': self.rsn, 'last_frame_received_time': self.last_frame_received_time, 'last_frame_received_i_time': self.last_frame_received_i_time, 'last_frame_send_time': self.last_frame_send_time, 'last_frame_send_u_time': self.last_frame_send_u_time, 'last_frame_send_s_time': self.last_frame_send_s_time, 'last_frame_send_z_time': self.last_frame_send_z_time, 'last_frame_send_d_time': self.last_frame_send_d_time, 'is_connected': self.check_is_connected()}

        def connect(self, callbacks: Optional[dict] = None):
            client = IOTBaseCommon.IECSocketClient(self.HOST, self.PORT, self.T0, self.T3, callbacks=callbacks)
            self.set_is_connected(True, client)

        def set_is_connected(self, is_connected, client: Optional[Any] = None):
            """设置连接状态"""
            self.is_connected = is_connected
            if is_connected is True:
                self.client = client if client is not None else self.client
            else:
                try:
                    if self.client is not None:
                        self.client.exit()
                except:
                    pass
                finally:
                    self.client = None

        def check_is_connected(self) -> bool:
            """获取连接状态"""
            return self.is_connected and self.client and self.client.check_invalid()

        def parse(self, datas: bytes) -> tuple:
            """初步解析"""
            self.last_frame_received_time = IOTBaseCommon.get_datetime()

            type, options = '', {}
            if datas[2] & 1 == 0 and len(datas) >= 12:  # I-Frame
                self.rsn_i += 1
                self.last_frame_received_i_time = IOTBaseCommon.get_datetime()
                self.rsn = self.inc_counter((datas[3] << 7) | ((datas[2] & 0xFE) >> 1))
                options['rsn'] = self.rsn
                options['type_id'] = datas[6]  # 类型(1)
                options['cause_id'] = datas[8] & 0x3F  # 原因
                type = 'I'
                if options['type_id'] == 100:  # 总召
                    if options['cause_id'] == 7:  # 总召确认
                        self.event_for_zongzhao = 1
                    elif options['cause_id'] == 10:  # 总召结束
                        self.event_for_zongzhao = 2
                elif options['type_id'] == 101:  # 电能脉冲召唤命令
                    if options['cause_id'] == 7:  # 电能确认
                        self.event_for_diandu = 1
                    elif options['cause_id'] == 10:  # 电能结束
                        self.event_for_diandu = 2
                elif options['type_id'] == 103:  # 时钟同步
                    pass
            elif datas[2] & 3 == 1:  # S-Frame
                type = 'S'
            elif datas[2] & 3 == 3:  # U-Frame
                type = 'U'
                options['u_type'] = (datas[2] & 0xfc) >> 2
                if options['u_type'] == 0x02:  # U帧激活确认 发送总召命令
                    self.last_frame_send_u_time = None
                    self.event_for_startdt_con = 1
                elif options['u_type'] == 0x08:  # U帧结束确认
                    self.set_is_connected(False)
                elif options['u_type'] == 0x10:  # U帧测试确认
                    self.send_u_frame(0x20)
                elif options['u_type'] == 0x20:  # U帧测试回复
                    self.last_frame_send_u_time = None
            return type, options

        def send_frame(self, datas) -> bool:
            """发送数据"""
            if self.check_is_connected():
                self.client.send(datas)
                self.last_frame_send_time = IOTBaseCommon.get_datetime()
                return True
            return False

        def send_i_frame(self, type_id: int, cause_id: int) -> str:
            """发送I帧"""
            datas = None
            if type_id == 100:  # 总召
                pkt = IOTIEC104.APDU()
                pkt /= IOTIEC104.APCI(ApduLen=14, Type=0x00, Tx=self.ssn, Rx=self.rsn)
                pkt /= IOTIEC104.ASDU(Type=100, SQ=0, Cause=6, Num=1, Test=0, OA=0, Addr=1, IOA=[IECData.IOAS[100](IOA=0, QOI=0x14)])
                datas = pkt.build()
            elif type_id == 101:  # 电能脉冲召唤
                pkt = IOTIEC104.APDU()
                pkt /= IOTIEC104.APCI(ApduLen=14, Type=0x00, Tx=self.ssn, Rx=self.rsn)
                pkt /= IOTIEC104.ASDU(Type=101, SQ=0, Cause=6, Num=1, Test=0, OA=0, Addr=1, IOA=[IECData.IOAS[101](IOA=0, QCC=0x0)])
                datas = pkt.build()

            content = ''
            if isinstance(datas, bytes) and len(datas) > 0 and self.send_frame(datas) is True:
                self.ssn = self.inc_counter(self.ssn)
                if type_id == 100:
                    self.last_frame_send_z_time = IOTBaseCommon.get_datetime()
                    self.event_for_zongzhao = 0
                elif type_id == 101:
                    self.last_frame_send_d_time = IOTBaseCommon.get_datetime()
                    self.event_for_diandu = 0
                content = f"iec104({self}) send I {self.ssn} ({IOTBaseCommon.DataTransform.format_bytes(datas)})"
                self.logging(content)
            return content

        def send_s_frame(self) -> str:
            """检查是否发送S确认帧"""
            content = ''
            if self.rsn_i >= self.W > 0:
                datas = (IOTIEC104.APDU() / IOTIEC104.APCI(ApduLen=4, Type=0x01, Rx=self.rsn)).build()
                if self.send_frame(datas) is True:
                    self.rsn_i = 0
                    self.last_frame_send_s_time = IOTBaseCommon.get_datetime()
                    content = f"iec104({self}) send S ({IOTBaseCommon.DataTransform.format_bytes(datas)})"
                    self.logging(content)
            return content

        def send_u_frame(self, utype: int) -> str:
            """发送U帧"""
            content = ''
            datas = (IOTIEC104.APDU() / IOTIEC104.APCI(ApduLen=4, Type=0x03, UType=utype)).build()
            if self.send_frame(datas) is True:
                if utype in [0x01, 0x10]:
                    self.last_frame_send_u_time = IOTBaseCommon.get_datetime()
                content = f"iec104({self}) send U ({IOTBaseCommon.DataTransform.format_bytes(datas)})"
                self.logging(content)
            return content

        def inc_counter(self, value):
            return value + 1 if value < 32767 else 0

        def auto_cmd(self):
            """自动命令"""
            if self.check_is_connected() is True:

                if self.event_for_startdt_con == 0:   # 尚未收到激活命令
                    # T0 没收到激活命令 结束
                    if isinstance(self.last_frame_send_u_time, datetime) and (IOTBaseCommon.get_datetime() - self.last_frame_send_u_time).total_seconds() > self.T0 > 0:
                        self.set_is_connected(False)
                        return
                else:
                    # T1 15s 未收到U帧回复(发送I帧或U帧后，等待对方应答，等待超过T1则重启链路)
                    if self.check_is_connected() is True and isinstance(self.last_frame_send_u_time, datetime) and 0 < self.T1 < (IOTBaseCommon.get_datetime() - self.last_frame_send_u_time).total_seconds():
                        self.set_is_connected(False)
                        return

                    # T2 10s 从站主动上报数据（突发）到收到S帧确认帧的时间  从站相应召唤到收到S帧确认帧的时间(接收到I帧后等待T2时间，然后发送对I帧的应答) - 无数据报文超时  从站发送完所有I帧，但未收到S帧
                    if self.check_is_connected() is True and isinstance(self.last_frame_received_i_time, datetime) and 0 < self.T2 < (IOTBaseCommon.get_datetime() - self.last_frame_received_i_time).total_seconds() and (self.last_frame_send_s_time is None or self.last_frame_send_s_time < self.last_frame_received_i_time):
                        self.send_s_frame()

                    # T3 20s 有任何数据时的超时时间，超时发送U帧测试帧 t3>t1>t2
                    if self.check_is_connected() is True and 0 < self.T3 < (IOTBaseCommon.get_datetime() - max(self.last_frame_received_time, self.last_frame_send_time)).total_seconds():
                        self.send_u_frame(0x10)
                        return

                    # 总召
                    if self.event_for_zongzhao != 2 and isinstance(self.last_frame_send_z_time, datetime) and (IOTBaseCommon.get_datetime() - self.last_frame_send_z_time).total_seconds() < self.T3:  # 总召命令未超时 不允许发送新总召或者电能命令
                        return

                    # 电度
                    if self.event_for_diandu != 2 and isinstance(self.last_frame_send_d_time, datetime) and (IOTBaseCommon.get_datetime() - self.last_frame_send_d_time).total_seconds() < self.T3:  # 电能命令未超时 不允许发送新总召或者电能命令
                        return

                    # 优先总召
                    if self.check_is_connected() is True and (self.last_frame_send_z_time is None or 0 < self.PZ < (IOTBaseCommon.get_datetime() - self.last_frame_send_z_time).total_seconds()):
                        self.send_i_frame(type_id=100, cause_id=6)

                    # 电度
                    if self.check_is_connected() is True and (self.last_frame_send_d_time is None or 0 < self.PZ < (IOTBaseCommon.get_datetime() - self.last_frame_send_d_time).total_seconds()):
                        self.send_i_frame(type_id=101, cause_id=6)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock_client = Lock()
        self.reinit()

    def reinit(self):
        self.iec104 = self.IEC104(self.configs.get('host'), self.configs.get('port'), t0=self.configs.get('timeout', 10), w=self.configs.get('s_interval', 8), pz=self.configs.get('zongzhao_interval', 8), pd=self.configs.get('dianneng_interval', 8))
        self.iec104.set_logging(self.logging)
        self.threads = {}   # 线程
        self.values = {}
        self.thread_exit = False
        self.cache_queue = deque(maxlen=2000)   # Queue()

    def exit(self):
        self._release_client()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': True, 'name': '点地址' if lan == 'ch' else 'Address', 'code': 'point_address', 'type': 'int', 'default': 16385, 'enum': [], 'tip': ''},
                {'required': True, 'name': '点类型' if lan == 'ch' else 'Type'.upper(), 'code': 'point_type', 'type': 'int', 'default': 13, 'enum': [], 'tip': ''},
                {'required': False, 'name': '点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
            ])
        elif type == 'config':
            templates.extend([
                {'required': True, 'name': '地址' if lan == 'ch' else 'Host', 'code': 'host', 'type': 'string', 'default': '192.168.1.1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '端口' if lan == 'ch' else 'Port', 'code': 'port', 'type': 'int', 'default': 2404, 'enum': [], 'tip': ''},
                {'required': True, 'name': '超时(s)' if lan == 'ch' else 'Timeout(s)', 'code': 'timeout', 'type': 'float', 'default': 10, 'enum': [], 'tip': ''},
                {'required': False, 'name': '总召(s)' if lan == 'ch' else 'ZongZhao Interval(s)', 'code': 'zongzhao_interval', 'type': 'int', 'default': 900, 'enum': [], 'tip': ''},
                {'required': False, 'name': '总召超时(s)' if lan == 'ch' else 'ZongZhao Timeout(s)', 'code': 'zongzhao_timeout', 'type': 'int', 'default': 30, 'enum': [], 'tip': ''},
                {'required': False, 'name': '电能召唤(s)' if lan == 'ch' else 'DianNeng Interval(s)', 'code': 'dianneng_interval', 'type': 'int', 'default': 60, 'enum': [], 'tip': ''},
                {'required': False, 'name': '电能召唤超时(s)' if lan == 'ch' else 'DianNeng Timeout(s)', 'code': 'dianneng_timeout', 'type': 'int', 'default': 30, 'enum': [], 'tip': ''},
                {'required': False, 'name': 'S帧' if lan == 'ch' else 'S Interval', 'code': 's_interval', 'type': 'int', 'default': 0, 'enum': [], 'tip': ''},
                {'required': False, 'name': '超时U帧测试(s)' if lan == 'ch' else 'U Test Timeout(s)', 'code': 'u_test_timeout', 'type': 'int', 'default': 15, 'enum': [], 'tip': ''},    # 超时发送U帧
            ])

        return templates

    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        names = kwargs.get('names', list(self.points.keys()))
        self.update_results(names, True, None)
        read_items = []
        for name in names:
            point = self.points.get(name)
            if point:
                type = point.get('point_type')  # 单点遥信
                address = point.get('point_address')    # 点地址
                if type is not None and address is not None:
                    read_items.append(f"{type}_{address}")

        self._read(list(set(read_items)))

        for name in names:
            point = self.points.get(name)
            if point:
                type = point.get('point_type')  # 单点遥信
                address = point.get('point_address')  # 点地址
                if type is not None and address is not None:
                    value = self._get_value(name, f"{self.configs.get('host')}:{self.configs.get('port')}", address, type)
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
            result = [False, 'Unknown']
            if point:
                type = point.get('point_type')  # 单点遥信
                address = point.get('point_address')  # 点地址
                if type is not None and address is not None:
                    self._write(type, address, value)
                    result = self.get_device_property(f"{self.configs.get('host')}:{self.configs.get('port')}", f"{type}_{address}", [self.get_write_quality, self.get_write_result])
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
        return self.iec104 and self.iec104.check_is_connected()

    def _read(self, read_items: list):
        try:
            if len(read_items) > 0 and self._get_client():
                pass
        except Exception as e:
            for read_item in read_items:
                self.update_device(f"{self.configs.get('host')}:{self.configs.get('port')}", read_item, **self.gen_read_write_result(False, e.__str__()))

    def _write(self, type: int, address: int, value):
        raise NotImplementedError()

    def _release_client(self):
        with self.lock_client:
            self.thread_exit = True
            if self.iec104:
                self.iec104.set_is_connected(False)
            try:
                for name, thread in self.threads.items():
                    thread.join(5)
                    IOTBaseCommon.stop_thread(thread)
            except Exception as e:
                pass
            finally:
                self.reinit()

    def _get_client(self):
        try:
            if self.iec104.check_is_connected() is False:
                self._release_client()

                self.iec104.connect(callbacks={'handle_connect': self.handle_connect, 'handle_close': self.handle_close, 'handle_error': self.handle_error, 'handle_data': self.handle_data})

            if self.iec104.check_is_connected() is False:
                raise Exception(f"Unconnected")
        except Exception as e:
            raise Exception(f"connect fail({e.__str__()})")
        return self.iec104.check_is_connected()

    def handle_connect(self, client):
        # 连接成功 U帧启动报文
        self.iec104.set_is_connected(True, client)
        self.create_auo_cmd_frame_thread()

    # 关闭事件
    def handle_close(self, client, reason: str):
        self.iec104.set_is_connected(False)
        self.logging(content=f"iec104({client}) close({reason})", level='ERROR', pos=self.stack_pos)

    def handle_error(self, client, msg: str):
        self.iec104.set_is_connected(False)
        self.logging(content=f"iec104({client}) error({msg})", level='ERROR', pos=self.stack_pos)

    def set_data_cache(self, datas: tuple):
        self.cache_queue.append(datas)

    def analyze_data_cache_thread(self):
        while self.thread_exit is False:
            while self.thread_exit is False and len(self.cache_queue) > 0:
                self.analyze_data_cache(self.cache_queue.popleft(), True)
                self.delay(0.001)
            self.delay(0.1)

    def analyze_data_cache(self, caches: Union[List, tuple], is_frame_parse: bool = True):
        if isinstance(caches, tuple) and len(caches) >= 2:
            send, datas, options = caches
            try:
                if isinstance(datas, bytes) and len(datas) > 0:
                    if isinstance(send, str) and len(send) > 0:
                        self.logging(content=f"{send} cache: {len(self.cache_queue)}", pos=self.stack_pos)
                    self.logging(content=f"iec104({self.iec104}) recv I {options.get('rsn')} {self._get_frame_name(options.get('type_id'), options.get('cause_id'))}", pos=self.stack_pos)
                    if is_frame_parse is True:
                        frame = IECFrame.iec_104.parse(datas)   # 解析速度快
                        self.update_device(f"{self.configs.get('host')}:{self.configs.get('port')}", values={f"{frame.ASDU.TYP}_{v.address}" if frame.ASDU.sq == 0 else f"{frame.ASDU.TYP}_{frame.ASDU.StartAddress + i}": self.gen_read_write_result(True, v.value) for i, v in enumerate(frame.ASDU.data) if hasattr(v, 'value')})
                    else:
                        self.update_device(f"{self.configs.get('host')}:{self.configs.get('port')}", values={k: self.gen_read_write_result(True, v) for k, v in IOTIEC104.ASDU(datas[6:]).values().items()})
            except (Exception, BaseException) as e:
                self.logging(content=f"iec104({self.iec104}) analyze data fail({e.__str__()}) {len(datas)}[{self.format_bytes(datas)}]", level='ERROR', pos=self.stack_pos)

    def handle_data(self, client, datas: bytes):
        try:
            if isinstance(datas, bytes) and len(datas) > 2 and client is not None:
                type, options = self.iec104.parse(datas)
                if type == 'I':  # I-Frame
                    self.set_data_cache((self.iec104.send_s_frame(), datas, options))
                else:  # S-Frame
                    self.logging(content=f"iec104({client}) recv {type}: [{self.format_bytes(datas)}]", pos=self.stack_pos)
        except Exception as e:
            self.logging(content=f"iec104({client}) handle data fail({e.__str__()})({self.format_bytes(datas)})", level='ERROR', pos=self.stack_pos)

    def _get_value(self, name: str, device_address: str, address: str, type: int):
        try:
            [result, value] = self.get_device_property(device_address, f"{type}_{address}", [self.get_read_quality, self.get_read_result])
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

    def _get_frame_name(self, type_id: int, cause_id: int) -> str:
        return f"{IECDefine.ASDU_TYPE.get(type_id)} {IECDefine.ASDU_CAUSE.get(cause_id)}"

    def create_auo_cmd_frame_thread(self):
        """启动命令线程"""
        thread_name = f"iecclient({self.configs.get('host')}:{self.configs.get('port')}) cmd"
        self.threads[thread_name] = IOTBaseCommon.function_thread(self.send_auo_cmd_frame_thread, True, thread_name)

        thread_name = f"iecclient({self.configs.get('host')}:{self.configs.get('port')}) analyze"
        self.threads[thread_name] = IOTBaseCommon.function_thread(self.analyze_data_cache_thread, True, thread_name)
        for name, thread in self.threads.items():
            thread.start()

    def send_auo_cmd_frame_thread(self):
        """命令线程"""
        try:
            self.iec104.send_u_frame(0x01)
        except (Exception, BaseException) as e:
            pass

        while self.iec104 and self.iec104.check_is_connected() is True:
            self.delay(0.5)
            try:
                self.iec104.auto_cmd()
            except (Exception, BaseException) as e:
                self.logging(content=f"iec104({self.iec104}) send data fail({e.__str__()})", level='ERROR', pos=self.stack_pos)
                self.delay(2)

    def format_bytes(self, data: bytes) -> str:
        if isinstance(data, bytes):
            return ' '.join(["%02X" % x for x in data]).strip()
        return ''

    @property
    def stack_pos(self, pos: int = 900):
        return f"iot_iec104.py({pos})"

    def info(self, **kwargs) -> dict:
        return self.iec104.info() if self.iec104 else {}