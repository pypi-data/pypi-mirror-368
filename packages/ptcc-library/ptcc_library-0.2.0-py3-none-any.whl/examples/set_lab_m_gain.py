from ptcc_library import *

import serial


def gain_callback(gain):
    try:
        # Try to convert the integer value to an enum member
        gain_name = GainVoltPerVolt(gain).name
        print(f"Lab_M Gain = {gain_name} [V/V]")
    except ValueError:
        # If the value is not in the enum, print the raw bit value
        print(f"Lab_M Gain = {gain} (Bit Value)")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.MODULE_LAB_M_PARAMS_GAIN, gain_callback)

    device.write_msg_set_module_lab_m_gain(GainVoltPerVolt.X5)

    while True:
        byte = ser.read(1)
        if byte:
            device.receiver.add_byte(byte[0])
