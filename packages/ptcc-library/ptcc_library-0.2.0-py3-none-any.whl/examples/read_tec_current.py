from ptcc_library import *

import serial


def current_callback(value):
    print(f"TEC Current = {value}")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.PTCC_MONITOR_I_TEC, current_callback)

    device.write_msg_get_monitor()

    while True:
        byte = ser.read(1)
        if byte:
            device.receiver.add_byte(byte[0])
