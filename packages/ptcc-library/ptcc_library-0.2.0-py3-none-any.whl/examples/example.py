from ptcc_library import *

import serial


def read_name_callback(name):
    print(f"name =", name)


def temperature_callback(value, user_data):
    print(f"Temperature = {value}")
    print(f"User data = {user_data}")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN_NAME, read_name_callback)
    device.receiver.register_callback(CallbackPtccObjectID.MODULE_BASIC_PARAMS_T_DET, temperature_callback, "present")

    device.write_msg_get_module_iden()
    device.write_msg_set_temperature(value_in_kelvins=230)

    while True:
        byte = ser.read(1)
        if byte:
            device.receiver.add_byte(byte[0])
