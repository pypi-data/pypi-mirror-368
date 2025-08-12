from ptcc_library import *

import serial


def temperature_callback(value):
    print(f"Temperature = {value}")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.MODULE_BASIC_PARAMS_T_DET, temperature_callback)

    device.write_msg_set_temperature(value_in_kelvins=230)

    while True:
        byte = ser.read(1)
        if byte:
            device.receiver.add_byte(byte[0])
