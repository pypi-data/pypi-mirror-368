from ptcc_library import *

import serial


def iden_callback(objects):
    for o in objects:
        print(f"{o.name} = {o.value}")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.DEVICE_IDEN, iden_callback)

    device.write_msg_get_device_iden()

    while True:
        byte = ser.read(1)
        if byte:
            device.receiver.add_byte(byte[0])
