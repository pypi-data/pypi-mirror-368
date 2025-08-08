import random
import time
from robertcommondriver.system.iot.iot_plc_siemens1 import SiemensS7Net, SiemensVersion


def logging_print(**kwargs):
    print(kwargs)


def test_siemens():
    s7 = SiemensS7Net(SiemensVersion.S7_1500, '192.168.1.172')
    s7.SetSlotAndRack(0,1)
    aa = s7.Read('V2634', 2)
    print(aa)


test_siemens()