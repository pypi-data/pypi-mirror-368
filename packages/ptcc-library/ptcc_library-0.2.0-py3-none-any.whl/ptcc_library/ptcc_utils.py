# Author: Wojciech Szczytko
# Created: 2025-04-03
from typing import Union

from datetime import datetime
import struct

from ptcc_library.ptcc_defines import ValType


def flatten(xss):
    return [x for xs in xss for x in xs]


def to_bytes(t: ValType, value) -> list[int]:
    """
        Converts a value to a list of byte values based on the provided Type.

        Returns a list of integers (0-255) that represent the bytes.
        """
    if t == ValType.CONTAINER:
        from ptcc_library.ptcc_object import PtccObject
        obj = PtccObject(value)
        return obj.raw_object
    elif t == ValType.CSTR:
        return list(str(value).encode())
    elif t == ValType.INT8:
        return list(int(value).to_bytes(1, byteorder='big', signed=True))
    elif t == ValType.UINT8:
        return list(int(value).to_bytes(1, byteorder='big', signed=False))
    elif t == ValType.INT16:
        return list(int(value).to_bytes(2, byteorder='big', signed=True))
    elif t == ValType.UINT16:
        return list(int(value).to_bytes(2, byteorder='big', signed=False))
    elif t == ValType.INT32:
        return list(int(value).to_bytes(4, byteorder='big', signed=True))
    elif t == ValType.UINT32:
        return list(int(value).to_bytes(4, byteorder='big', signed=False))
    elif t == ValType.FLOAT:
        return list(struct.pack('<f', float(value)))
    elif t == ValType.DATE_TIME:
        raise NotImplementedError("Conversion for DATE_TIME type is not implemented.")
    elif t == ValType.SERIAL_NUMBER:
        raise NotImplementedError("Conversion for SERIAL type is not implemented.")
    elif t == ValType.BOOL:
        return [1] if value else [0]
    else:
        raise ValueError(f"Unsupported type: {t}")


def from_bytes(t: ValType, input_list: Union[list[int], bytes, bytearray]) -> any:
    """
    Converts a list of bytes (integers 0–255) into a Python value based on the provided Type.
    """
    # For clarity, convert the list into a bytes object once.
    byte_value = bytes(input_list)

    if t == ValType.CSTR:
        # Convert list of bytes into a string.
        # Here we treat a null (0) byte as terminator: cut off at the first null byte.
        try:
            end = input_list.index(0)
            trimmed = input_list[:end]
        except ValueError:
            trimmed = input_list
        return bytes(trimmed).decode('utf-8')
    elif t == ValType.INT8:
        if len(input_list) != 1:
            raise ValueError("Expected 1 byte for INT8.")
        return int.from_bytes(byte_value, byteorder='big', signed=True)
    elif t == ValType.UINT8:
        if len(input_list) != 1:
            raise ValueError("Expected 1 byte for UINT8.")
        return int.from_bytes(byte_value, byteorder='big', signed=False)
    elif t == ValType.INT16:
        if len(input_list) != 2:
            raise ValueError("Expected 2 bytes for INT16.")
        return int.from_bytes(byte_value, byteorder='big', signed=True)
    elif t == ValType.UINT16:
        if len(input_list) != 2:
            raise ValueError("Expected 2 bytes for UINT16.")
        return int.from_bytes(byte_value, byteorder='big', signed=False)
    elif t == ValType.INT32:
        if len(input_list) != 4:
            raise ValueError("Expected 4 bytes for INT32.")
        return int.from_bytes(byte_value, byteorder='big', signed=True)
    elif t == ValType.UINT32:
        if len(input_list) != 4:
            raise ValueError("Expected 4 bytes for UINT32.")
        return int.from_bytes(byte_value, byteorder='big', signed=False)
    elif t == ValType.FLOAT:
        if len(input_list) != 4:
            raise ValueError("Expected 4 bytes for FLOAT.")
        # struct.unpack returns a tuple; extract the first element.
        return struct.unpack('<f', byte_value)[0]
    elif t == ValType.DATE_TIME:
        if len(input_list) != 8:
            raise ValueError("Expected 8 bytes for DATE_TIME.")
        # For DATE_TIME:
        # first 2 bytes: millisecond part, then 1 byte for sec, 1 for minute, 1 for hour, 1 for day, 1 for month, 1 for year.
        msec = int.from_bytes(byte_value[0:2], byteorder='big', signed=False)
        if msec >= 1000:
            msec = 0
        sec = byte_value[2]
        if sec >= 60:
            sec = 0
        minute = byte_value[3]
        if minute >= 60:
            minute = 0
        hour = byte_value[4]
        if hour >= 24:
            hour = 0
        day = byte_value[5]
        if day > 31:
            day = 0
        month = byte_value[6]
        if month > 12:
            month = 0
        year = byte_value[7]
        return datetime(year=1900 + year, month=month, day=day,
                        hour=hour, minute=minute, second=sec, microsecond=msec * 1000)
    elif t == ValType.SERIAL_NUMBER:
        if len(input_list) != 4:
            raise ValueError(f"Expected 4 bytes for SERIAL_NUMBER. Got: {input_list}")

        raw = int.from_bytes(input_list, byteorder='big', signed=False)

        if (raw & 0x80000000) == 0:
            # Method 1 – first bit is 0 → year + serial
            year = input_list[0]
            serial = int.from_bytes(input_list[1:], byteorder='big', signed=False)
            return f"{serial:06}-{year:02}"
        else:
            # Method 2 – first bit is 1 → full 32-bit number
            serial = raw & 0x7FFFFFFF
            return f"{serial:09}"
    elif t == ValType.BOOL:
        if len(input_list) != 1:
            raise ValueError("Expected 1 byte for BOOL.")
        return input_list[0] != 0
    elif t == ValType.CONTAINER:
        from ptcc_library.ptcc_object import PtccObject
        container = PtccObject(obj_id=0, data=input_list)
        return container.objects
    else:
        raise ValueError(f"Unsupported type: {t}")
