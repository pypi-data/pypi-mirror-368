import time

from ptcc_library import *

import serial


def lab_m_params_callback(objects):
    print("-------------------------------------------------")
    for o in objects:
        print(f"{o.name} = {o.value}")
    print("-------------------------------------------------")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.MODULE_LAB_M_PARAMS, lab_m_params_callback)

    device.write_msg_get_lab_m_params()

    while True:
        byte = ser.read(1)
        if byte:
            if device.receiver.add_byte(byte[0]) == PtccMessageReceiveStatus.FINISHED:
                time.sleep(1)
                device.write_msg_get_lab_m_params()
