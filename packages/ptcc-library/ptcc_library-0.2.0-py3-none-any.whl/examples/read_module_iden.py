from ptcc_library import *

import serial


def read_name_callback(name):
    print(f"Name =", name)


def read_serial_number_callback(serial_number):
    print(f"Serial number =", serial_number)


def iden_callback(objects):
    print("-------------------------------------------------")
    for o in objects:
        print(f"{o.name} = {o.value}")
    print("-------------------------------------------------")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN_NAME, read_name_callback)
    device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN_SERIAL, read_serial_number_callback)
    device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN, iden_callback)

    device.write_msg_get_module_iden()

    while True:
        byte = ser.read(1)
        if byte:
            device.receiver.add_byte(byte[0])
