import time

from ptcc_library import *

import serial


def status_callback(status):
    if status in status_messages:
        print("Status code:")
        print(f"{status} – {status_messages[status]}")
    elif status in error_messages:
        print("Error code:")
        print(f"{status} – {error_messages[status]}")
    else:
        print(f"Unknown code: {status}")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)

    device.receiver.register_callback(CallbackPtccObjectID.PTCC_MONITOR_STATUS, status_callback)

    device.write_msg_get_monitor()

    while True:
        byte = ser.read(1)
        if byte:
            if device.receiver.add_byte(byte[0]) == PtccMessageReceiveStatus.FINISHED:
                time.sleep(4)
                device.write_msg_get_monitor()
