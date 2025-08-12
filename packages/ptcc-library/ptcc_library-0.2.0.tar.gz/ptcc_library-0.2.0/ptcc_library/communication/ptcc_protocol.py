# Author: Wojciech Szczytko
# Created: 2025-04-03
import inspect
import string
from typing import Callable, overload, Any, Tuple, Union

from ptcc_library.ptcc_utils import to_bytes
from ptcc_library.ptcc_object import PtccObject
from ptcc_library.ptcc_defines import SET_CONTAINER_IDS, CONTAINER_IDS, ValType, PtccMessageReceiveStatus, ModuleType, \
    DeviceRegister, PtccCtrl, GainVoltPerVolt, START_BYTE, CallbackPtccObjectID, LAB_M_PARAMS_IDS, BASIC_PARAMS_IDS, \
    PtccObjectID

CRC_POLY = 0x8005


def ptcc_message_to_ptcc_object(raw_msg: Union[list[int], bytearray, bytes]) -> PtccObject:
    """
    Converts a raw PTCC message into a `PtccObject`.

    This function parses a raw byte sequence (typically received over serial communication)
    formatted according to the PTCC protocol. It validates framing characters (`$` and `#`),
    checks message length, verifies the CRC, and decodes the message content into a PtccObject.

    Parameters
    ----------
    raw_msg : list of int, bytearray, or bytes
        The raw message bytes received from the device. Must begin with '$' and end with '#'.

    Returns
    -------
    PtccObject
        A PtccObject instance reconstructed from the decoded message content.

    Raises
    ------
    ValueError
        If the message is empty, improperly framed, too short, or fails CRC validation.

    Notes
    -----
    The function expects that the core object data is hex-encoded within the message.
    The format is as follows:
        - Starts with `$` (0x24)
        - Ends with `#` (0x23)
        - Contains a 4-character CRC before the final `#`
        - All object bytes are hex-encoded pairs (e.g., `'4A'` becomes byte 0x4A)
    """
    if len(raw_msg) == 0:
        raise ValueError("Raw message is empty")

    if raw_msg[0] != ord('$') or raw_msg[-1] != ord('#'):
        raise ValueError("Raw message does not represent a message. Missing '$' and/or '#'")

    if len(raw_msg) < 8:
        raise ValueError("Raw message does not represent a message. Too short")

    encoded_data_chars = raw_msg[1:-5]

    # Convert encoded hex character pairs back to bytes
    raw_obj = []
    for i in range(0, len(encoded_data_chars), 2):
        hex_str = chr(encoded_data_chars[i]) + chr(encoded_data_chars[i + 1])
        raw_obj.append(int(hex_str, 16))

    # Check if CRC is valid
    if not is_ptcc_message_crc_valid(raw_msg):
        raise ValueError("CRC mismatch! Data may be corrupted.")

    return PtccObject(raw_object=raw_obj)


def _is_valid_hex_char(c: int) -> bool:
    """Check if int represents a valid ASCII hex character."""
    return chr(c) in string.hexdigits  # string.hexdigits = '0123456789abcdefABCDEF'


def is_ptcc_message_crc_valid(raw_msg: Union[list[int], bytearray, bytes]) -> bool:
    """Check if crc of a message is valid.

    Parameters
    ----------
    raw_msg : list of int, bytearray, or bytes
        The raw message bytes received from the device. Must begin with '$' and end with '#'.

    Returns
    -------
    bool
        True if crc is valid and False if it is not.

    Raises
    ------
    ValueError
        If the message is empty, improperly framed, too short, or chars of crc are not represented in hex.

    Notes
    -----
    The function expects that the core object data is hex-encoded within the message.
    The format is as follows:
        - Starts with `$` (0x24)
        - Ends with `#` (0x23)
        - All object bytes are hex-encoded pairs (e.g., `'4A'` becomes byte 0x4A)
    """
    if len(raw_msg) == 0:
        raise ValueError("Raw message is empty")

    if raw_msg[0] != ord('$') or raw_msg[-1] != ord('#'):
        raise ValueError("Raw message does not represent a message. Missing '$' and/or '#'")

    if len(raw_msg) < 8:
        raise ValueError("Raw message does not represent a message. Too short")

    # Remove start and stop bytes
    encoded_msg = raw_msg[1:-1]
    # Extract encoded CRC (last four characters)
    encoded_crc_chars = encoded_msg[-4:]
    encoded_data_chars = encoded_msg[:-4]

    # Validate CRC characters before decoding
    for c in encoded_crc_chars:
        if not _is_valid_hex_char(c):
            raise ValueError(f"Invalid character in encoded CRC: {repr(chr(c))}")

    # Convert encoded CRC back to integer
    extracted_crc = int("".join(chr(c) for c in encoded_crc_chars), 16)

    # Convert encoded hex character pairs back to bytes
    raw_obj = []
    for i in range(0, len(encoded_data_chars), 2):
        hex_str = chr(encoded_data_chars[i]) + chr(encoded_data_chars[i + 1])
        raw_obj.append(int(hex_str, 16))

    # Compute CRC on extracted raw data
    computed_crc = calculate_ptcc_crc(raw_obj)

    # Check if CRC is valid
    return computed_crc == extracted_crc


@overload
def create_set_ptcc_message(set_command_id: Union[PtccObjectID, int], ptcc_objects: PtccObject) -> list[int]: ...


@overload
def create_set_ptcc_message(set_command_id: Union[PtccObjectID, int], ptcc_objects: list[PtccObject]) -> list[int]: ...


def create_set_ptcc_message(set_command_id: Union[PtccObjectID, int],
                            ptcc_objects: Union[PtccObject, list[PtccObject]]) -> \
        list[int]:
    """
    Creates a PTCC-formatted SET message containing the given PtccObject(s).

    This function constructs a nested container message where the inner container holds
    the user-provided PtccObject, and the outer container corresponds to a specific
    `set_command_id`. The message is encoded in hex pairs, CRC-validated, and wrapped
    in `$`...`#` markers as per PTCC protocol.

    Parameters
    ----------
    set_command_id : PtccObjectID or int
        The type of SET command to be sent. Must correspond to a container-type object
        listed in `SET_CONTAINER_IDS`.

    ptcc_objects : PtccObject or list of PtccObject
        One or more PtccObject instances to be included in the message payload.

    Returns
    -------
    list of int
        The complete PTCC message encoded as a list of ASCII values, ready to send over a byte stream.
        Message format: [ord('$')] + encoded_data + [ord('#')]

    Raises
    ------
    ValueError
        If the command ID or derived container ID is not a valid container type
        according to the PTCC protocol rules.

    Notes
    -----
    The function builds a nested container structure as required by PTCC’s SET message format:
        - Outer container = `set_command_id`
        - Inner container = `container_id` (from SET_CONTAINER_IDS lookup)
        - Payload = one or more PtccObjects

    The message structure is:
        $ + HEX_ENCODED([outer_container( inner_container( objects ) ) + CRC]) + #
    """

    if isinstance(ptcc_objects, PtccObject):
        ptcc_objects = [ptcc_objects]

    if isinstance(set_command_id, int):
        set_command_id = PtccObjectID(set_command_id)

    container_id = SET_CONTAINER_IDS.__getitem__(set_command_id)

    if isinstance(container_id, int):
        set_command_id = PtccObjectID(container_id)

    if set_command_id not in CONTAINER_IDS or container_id not in CONTAINER_IDS:
        raise ValueError("Expected container types for set_command_id and container_id")

    ptcc_container_object = PtccObject(
        raw_object=to_bytes(ValType.UINT16, container_id.value) + to_bytes(ValType.UINT16, 4))
    ptcc_container_object.pack_container(ptcc_objects)
    ptcc_set_container_object = PtccObject(
        raw_object=to_bytes(ValType.UINT16, set_command_id.value) + to_bytes(ValType.UINT16, 4))
    ptcc_set_container_object.pack_container([ptcc_container_object])

    raw_obj = ptcc_set_container_object.raw_object
    crc = to_bytes(ValType.UINT16, calculate_ptcc_crc(raw_obj))
    raw_obj += crc

    raw_msg = []
    for c in raw_obj:
        x_str = format(c, '02x').upper()
        raw_msg.append(ord(x_str[0]))
        raw_msg.append(ord(x_str[1]))

    return [ord('$')] + raw_msg + [ord('#')]


def create_get_ptcc_message(get_command_id: Union[PtccObjectID, int]) -> list[int]:
    """
    Creates a PTCC-formatted GET message for the specified command ID.

    This function builds a request message to retrieve data from a PTCC device.
    The message includes the command ID, is CRC-validated, hex-encoded, and framed
    with protocol-specific delimiters (`$` and `#`).

    Parameters
    ----------
    get_command_id : PtccObjectID or int
        The command identifier for the GET request. Must correspond to a valid PtccObjectID.

    Returns
    -------
    list of int
        The complete PTCC GET message encoded as a list of ASCII values, ready to transmit.
        Format: [ord('$')] + HEX_ENCODED_DATA + CRC + [ord('#')]

    Notes
    -----
    - The message body is composed of a PtccObject with no payload (`data=[]`), just an object ID.
    - The data is hex-encoded as ASCII character pairs (e.g., byte `0x4A` becomes `'4A'` → [ord('4'), ord('A')]).
    - A 2-byte CRC is calculated over the raw object and appended in hex format.
    - The message is framed with `$` and `#` characters as start/end delimiters.
    """

    if isinstance(get_command_id, int):
        get_command_id = PtccObjectID(get_command_id)

    ptcc_obj = PtccObject(raw_object=to_bytes(ValType.UINT16, get_command_id.value) + to_bytes(ValType.UINT16, 4))
    # ptcc_obj = PtccObject(obj_id=get_command_id.value, data=[])
    raw_obj = ptcc_obj.raw_object
    crc = calculate_ptcc_crc(raw_obj)

    encoded_data_list = [format(x, "02x").upper() for x in raw_obj]
    encoded_data = []
    for encoded_byte in encoded_data_list:
        encoded_data.append(ord(encoded_byte[0]))
        encoded_data.append(ord(encoded_byte[1]))
    encoded_crc = [ord(x) for x in format(crc, "04x").upper()]

    return [ord('$')] + encoded_data + encoded_crc + [ord('#')]


def calculate_ptcc_crc(buf: Union[bytearray, bytes, list[int]]) -> int:
    """
    Calculates CRC.

    Parameters
    ----------
    buf : Union[bytearray, bytes, list[int]]
        buffer of bytes based on which rc is calculated.

    Returns
    -------
    int
        crc value.
    """
    out = 0
    bits_read = 0
    # bit_flag = 0
    size = len(buf)
    index = 0
    while size > 0:
        current_byte = buf[index]
        bit_flag = out >> 15
        out <<= 1
        out = out % 65536
        out |= (current_byte >> bits_read) & 1
        bits_read += 1
        if bits_read > 7:
            bits_read = 0
            index += 1
            size -= 1
        if bit_flag:
            out ^= CRC_POLY
            out = out & 0xFFFF

    for idx in range(0, 16):
        bit_flag = out >> 15
        out <<= 1
        out = out % 65536
        if bit_flag:
            out ^= CRC_POLY
            out = out & 0xffff

    crc = 0
    i = 0x8000
    j = 0x0001
    while i != 0:
        if i & out:
            crc |= j
        i >>= 1
        j <<= 1
    return crc


class PtccMessage:
    """
    Represents a raw PTCC protocol message with validation.

    A PtccMessage encapsulates a raw PTCC message as a list of ASCII codes.
    It validates the structure of the message to ensure it conforms to expected
    PTCC protocol formatting rules.

    Parameters
    ----------
    raw_message : list of int, bytearray, or bytes, optional
        The raw message content represented as ASCII codes. If provided, the message is validated
        to ensure it starts with '$', ends with '#', and contains valid hexadecimal characters in between.

    Raises
    ------
    ValueError
        If the message:
        - Does not start with '$' (ASCII 36)
        - Contains invalid characters (must be '0'-'9' or 'A'-'F')
        - Contains embedded '$' or '#' characters (only allowed at start and end)
        - Ends with an invalid character (must be '#' or a valid hex digit)

    Attributes
    ----------
    _raw_message : list of int
        The validated raw message stored as a list of ASCII character codes.

    Notes
    -----
    This class is primarily intended for validating incoming or outgoing messages at a low level
    before further parsing into `PtccObject` structures or transmission over a communication interface.
    """

    def __init__(self, raw_message: Union[list[int], bytearray, bytes] = None):

        if raw_message is None:
            raw_message = []

        self._raw_message = list(raw_message)

        if len(self._raw_message) > 0:
            if self._raw_message[0] != ord('$'):
                raise ValueError("Raw message does not represent a message. Must start with '$' if present.")

        if len(self._raw_message) >= 2:
            for i, c in enumerate(self._raw_message[1:-1], start=1):
                if c in (ord('$'), ord('#')):
                    raise ValueError(
                        f"Raw message does not represent a message. Unexpected '$' or '#' at position {i}.")

                if not (48 <= c <= 57 or 65 <= c <= 70):  # '0'-'9' or 'A'-'F'
                    raise ValueError(
                        f"Raw message does not represent a message. Invalid hex character at position {i}: "
                        f"{repr(chr(c))}")

        if len(self._raw_message) >= 2 and self._raw_message[-1] not in (ord('#'), *range(48, 58), *range(65, 71)):
            raise ValueError(
                f"Raw message does not represent a message. Invalid final character: "
                f"{repr(chr(self._raw_message[-1]))}")

    def __str__(self) -> str:
        return "Ptcc Message: " + self._raw_message.__str__()

    def __eq__(self, other: "PtccMessage") -> bool:
        return self._raw_message == other._raw_message

    @property
    def raw_message(self) -> list[int]:
        """
        list[int]: The validated raw message stored as a list of ASCII character codes.
        """
        return self._raw_message

    @property
    def receive_status(self) -> PtccMessageReceiveStatus:
        """
        PtccMessageReceiveStatus: Describes if message is fully formed.
        """
        if len(self._raw_message) == 0:
            return PtccMessageReceiveStatus.NOT_BEGAN
        if self._raw_message[-1] == ord('#'):
            return PtccMessageReceiveStatus.FINISHED
        else:
            return PtccMessageReceiveStatus.IN_PROGRESS

    @property
    def is_crc_valid(self) -> bool:
        """
        bool: Returns True if message crc is valid or False if it is not valid.
        """
        return is_ptcc_message_crc_valid(self.raw_message)

    def append_byte(self, raw_byte: int) -> PtccMessageReceiveStatus:
        """
        Appends a single byte (ASCII code) to the raw message stream and returns the current receive status.

        This method is typically used in byte-wise message assembly scenarios, such as when
        receiving data from a serial port. It enforces PTCC framing and content rules
        to determine whether the message is valid, incomplete, or has overflowed.

        Parameters
        ----------
        raw_byte : int
            A single byte to append, expected to be the ASCII code of a valid PTCC character.
            The first byte must be '$' (ASCII 36), and characters must be valid hex digits or '#'.

        Returns
        -------
        PtccMessageReceiveStatus
            The current status of the message after appending the byte. Can be:
            - NOT_BEGAN: message has not started (waiting for `$`)
            - IN_PROGRESS: receiving hex data
            - FINISHED: received terminating `#`
            - OVERFLOW: too many characters were appended beyond expected length

        Raises
        ------
        ValueError
            If the message does not start with '$',
            or if an invalid character (non-hex and not '#') is appended.

        Notes
        -----
        This function performs strict validation:
        - First character must be '$'
        - Hexadecimal characters must be in range '0'-'9' or 'A'-'F'
        - Only one '#' is allowed, and only at the end
        """
        if len(self._raw_message) > 0:
            if self._raw_message[0] != ord('$'):
                raise ValueError("Raw message does not represent a message. Missing '$' as its first character")
        else:
            if raw_byte != ord('$'):
                raise ValueError("Raw message does not represent a message. Missing '$' as its first character")

        status = self.receive_status
        if status != PtccMessageReceiveStatus.FINISHED:
            if not _is_valid_hex_char(raw_byte) and (
                    status != PtccMessageReceiveStatus.NOT_BEGAN and raw_byte != ord('#')):
                raise ValueError("Raw message does not represent a message. Byte does not represent an ASCII character")
            self._raw_message.append(raw_byte)
            return self.receive_status
        # could not append another byte
        return PtccMessageReceiveStatus.OVERFLOW

    def append_bytes(self, raw_bytes: Union[list[int], bytearray, bytes]) \
            -> tuple[PtccMessageReceiveStatus, Union[list[int], bytearray, bytes]]:
        """
        Appends a multiple bytes (ASCII code) to the raw message stream and returns the current receive status.

        This method is typically used in byte-wise message assembly scenarios, such as when
        receiving data from a serial port. It enforces PTCC framing and content rules
        to determine whether the message is valid, incomplete, or has overflowed.

        Parameters
        ----------
        raw_bytes : Union[list[int], bytearray, bytes]
            Bytes to append, expected to be the ASCII code of a valid PTCC characters.
            The first byte must be '$' (ASCII 36), and characters must be valid hex digits or '#'.

        Returns
        -------
        PtccMessageReceiveStatus
            The current status of the message after appending the byte. Can be:
            - NOT_BEGAN: message has not started (waiting for `$`)
            - IN_PROGRESS: receiving hex data
            - FINISHED: received terminating `#`
            - OVERFLOW: too many characters were appended beyond expected length
        Union[list[int], bytearray, bytes]
            bytes that were not appended to message because message was completed during appending.

        Raises
        ------
        ValueError
            If the message does not start with '$',
            or if an invalid character (non-hex and not '#') is appended.

        Notes
        -----
        This function performs strict validation:
        - First character must be '$'
        - Hexadecimal characters must be in range '0'-'9' or 'A'-'F'
        - Only one '#' is allowed, and only at the end
        """
        i = 0
        while i < len(raw_bytes):
            status = self.append_byte(raw_bytes[i])
            if status == PtccMessageReceiveStatus.OVERFLOW:
                return PtccMessageReceiveStatus.OVERFLOW, raw_bytes[i:]
            if status == PtccMessageReceiveStatus.FINISHED:
                return PtccMessageReceiveStatus.FINISHED, raw_bytes[i + 1:]
            i += 1

        return self.receive_status, raw_bytes[i:]

    def to_ptcc_object(self) -> PtccObject:
        """
        Used to get PtccObject stored in PtccMessage.

        Returns
        -------
        PtccObject
            PTCC Object stored in message
        """
        if self.receive_status == PtccMessageReceiveStatus.FINISHED:
            return ptcc_message_to_ptcc_object(self._raw_message)
        else:
            raise ValueError("Raw message does not represent a complete message.")

    def reset(self):
        """
        Used to reset PtccMessage object.
        """
        self._raw_message = []

    @classmethod
    def generate_msg_get_device_iden(cls):
        """
        Generates message for reading identification data of PTCC device.
        """
        return cls(generate_msg_get_device_iden())

    @classmethod
    def generate_msg_get_module_iden(cls, module_type: ModuleType):
        """
        Generates message for reading identification and configuration data of module connected to PTCC device.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_IDEN
         - MODULE_IDEN_TYPE
         - MODULE_IDEN_FIRM_VER
         - MODULE_IDEN_HARD_VER
         - MODULE_IDEN_NAME
         - MODULE_IDEN_SERIAL
         - MODULE_IDEN_DET_NAME
         - MODULE_IDEN_DET_SERIAL
         - MODULE_IDEN_PROD_DATE
         - MODULE_IDEN_TEC_TYPE
         - MODULE_IDEN_TH_TYPE
         - MODULE_IDEN_TEC_PARAM1
         - MODULE_IDEN_TEC_PARAM2
         - MODULE_IDEN_TEC_PARAM3
         - MODULE_IDEN_TEC_PARAM4
         - MODULE_IDEN_TH_PARAM1
         - MODULE_IDEN_TH_PARAM2
         - MODULE_IDEN_TH_PARAM3
         - MODULE_IDEN_TH_PARAM4
         - MODULE_IDEN_COOL_TIME
        """
        return cls(generate_msg_get_module_iden(module_type))

    @classmethod
    def generate_msg_get_monitor(cls):
        """
        Generates message for reading measured parameters of no memory module connected to PTCC device.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - PTCC_MONITOR
         - PTCC_MONITOR_SUP_ON
         - PTCC_MONITOR_I_SUP_PLUS
         - PTCC_MONITOR_I_SUP_MINUS
         - PTCC_MONITOR_FAN_ON
         - PTCC_MONITOR_I_FAN_PLUS
         - PTCC_MONITOR_I_TEC
         - PTCC_MONITOR_U_TEC
         - PTCC_MONITOR_U_SUP_PLUS
         - PTCC_MONITOR_U_SUP_MINUS
         - PTCC_MONITOR_T_DET
         - PTCC_MONITOR_T_INT
         - PTCC_MONITOR_PWM
         - PTCC_MONITOR_STATUS
         - PTCC_MONITOR_MODULE_TYPE
         - PTCC_MONITOR_TH_ADC
        """
        return cls(generate_msg_get_monitor())

    @classmethod
    def generate_msg_get_lab_m_monitor(cls, module_type: ModuleType):
        """
        Generates message for reading measured lab_m parameters of module connected to PTCC device.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_MONITOR
         - MODULE_LAB_M_MONITOR_SUP_PLUS
         - MODULE_LAB_M_MONITOR_SUP_MINUS
         - MODULE_LAB_M_MONITOR_FAN_PLUS
         - MODULE_LAB_M_MONITOR_TEC_PLUS
         - MODULE_LAB_M_MONITOR_TEC_MINUS
         - MODULE_LAB_M_MONITOR_TH1
         - MODULE_LAB_M_MONITOR_TH2
         - MODULE_LAB_M_MONITOR_U_DET
         - MODULE_LAB_M_MONITOR_U_1ST
         - MODULE_LAB_M_MONITOR_U_OUT
         - MODULE_LAB_M_MONITOR_TEMP
        """
        return cls(generate_msg_get_lab_m_monitor(module_type))

    @classmethod
    def generate_msg_get_basic_params(cls, module_type: ModuleType,
                                      target: DeviceRegister = DeviceRegister.USER_SET):
        """
        Generates message for reading configuration (power, cooling) data for module connected to PTCC device.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        target: DeviceRegister
            Specifies which type of register should be read:
            DeviceRegister.DEFAULT - register for default setting.
            DeviceRegister.USER_SET - register for user setting.
            DeviceRegister.USER_MIN - register for max allowed setting.
            DeviceRegister.USER_MAX - register for min allowed setting.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message, or if target register is not recognized.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_BASIC_PARAMS
         - MODULE_BASIC_PARAMS_SUP_CTRL
         - MODULE_BASIC_PARAMS_U_SUP_PLUS
         - MODULE_BASIC_PARAMS_U_SUP_MINUS
         - MODULE_BASIC_PARAMS_FAN_CTRL
         - MODULE_BASIC_PARAMS_TEC_CTRL
         - MODULE_BASIC_PARAMS_PWM
         - MODULE_BASIC_PARAMS_I_TEC_MAX
         - MODULE_BASIC_PARAMS_T_DET
        """
        return cls(generate_msg_get_basic_params(module_type, target))

    @classmethod
    def generate_msg_get_lab_m_params(cls, module_type: ModuleType,
                                      target: DeviceRegister = DeviceRegister.USER_SET):
        """
        Generates message for reading lab_m configuration data for module connected to PTCC device.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        target: DeviceRegister
            Specifies which type of register should be read:
            DeviceRegister.DEFAULT - register for default setting.
            DeviceRegister.USER_SET - register for user setting.
            DeviceRegister.USER_MIN - register for max allowed setting.
            DeviceRegister.USER_MAX - register for min allowed setting.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_get_lab_m_params(module_type, target))

    @classmethod
    def generate_msg_get_config(cls):
        """
        Generates message for reading PTCC device type.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - PTCC_CONFIG
         - PTCC_CONFIG_VARIANT
         - PTCC_CONFIG_NO_MEM_COMPATIBLE
        """
        return cls(generate_msg_get_config())

    @classmethod
    def generate_msg_set_module_lab_m_param(cls, module_type: ModuleType,
                                            ptcc_object: PtccObject):
        """
        Generates message for setting and saving lab_m parameters.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        ptcc_object: PtccObject
            PTCC object to send as configuration.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_param(module_type,
                                                       ptcc_object))

    @classmethod
    def generate_msg_set_cooler_disabled(cls, module_type: ModuleType):
        """
        Generates message for setting and saving operating mode of TEC as disabled.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_BASIC_PARAMS
         - MODULE_BASIC_PARAMS_SUP_CTRL
         - MODULE_BASIC_PARAMS_U_SUP_PLUS
         - MODULE_BASIC_PARAMS_U_SUP_MINUS
         - MODULE_BASIC_PARAMS_FAN_CTRL
         - MODULE_BASIC_PARAMS_TEC_CTRL
         - MODULE_BASIC_PARAMS_PWM
         - MODULE_BASIC_PARAMS_I_TEC_MAX
         - MODULE_BASIC_PARAMS_T_DET
        """
        return cls(generate_msg_set_cooler_disabled(module_type))

    @classmethod
    def generate_msg_set_cooler_enabled(cls, module_type: ModuleType):
        """
        Generates message for setting and saving operating mode of TEC as enabled (Cooler will work with fixed supply
        current).

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_BASIC_PARAMS
         - MODULE_BASIC_PARAMS_SUP_CTRL
         - MODULE_BASIC_PARAMS_U_SUP_PLUS
         - MODULE_BASIC_PARAMS_U_SUP_MINUS
         - MODULE_BASIC_PARAMS_FAN_CTRL
         - MODULE_BASIC_PARAMS_TEC_CTRL
         - MODULE_BASIC_PARAMS_PWM
         - MODULE_BASIC_PARAMS_I_TEC_MAX
         - MODULE_BASIC_PARAMS_T_DET
        """
        return cls(generate_msg_set_cooler_enabled(module_type))

    @classmethod
    def generate_msg_set_cooler_auto(cls, module_type: ModuleType):
        """
        Generates message for setting and saving operating mode of TEC as auto.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_BASIC_PARAMS
         - MODULE_BASIC_PARAMS_SUP_CTRL
         - MODULE_BASIC_PARAMS_U_SUP_PLUS
         - MODULE_BASIC_PARAMS_U_SUP_MINUS
         - MODULE_BASIC_PARAMS_FAN_CTRL
         - MODULE_BASIC_PARAMS_TEC_CTRL
         - MODULE_BASIC_PARAMS_PWM
         - MODULE_BASIC_PARAMS_I_TEC_MAX
         - MODULE_BASIC_PARAMS_T_DET
        """
        return cls(generate_msg_set_cooler_auto(module_type))

    @classmethod
    def generate_msg_set_module_param(cls, module_type: ModuleType,
                                      ptcc_object: PtccObject):
        """
        Generates message for setting and saving module parameters.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        ptcc_object: PtccObject
            ID must be one of BASIC_PARAMS_IDS.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_param(module_type, ptcc_object))

    @classmethod
    def generate_msg_set_fan(cls, module_type: ModuleType, mode: PtccCtrl):
        """
        Generates message for setting and saving operation state of fan control.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        mode: PtccCtrl
            operation state of fan control. On, Off or Auto.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_BASIC_PARAMS
         - MODULE_BASIC_PARAMS_SUP_CTRL
         - MODULE_BASIC_PARAMS_U_SUP_PLUS
         - MODULE_BASIC_PARAMS_U_SUP_MINUS
         - MODULE_BASIC_PARAMS_FAN_CTRL
         - MODULE_BASIC_PARAMS_TEC_CTRL
         - MODULE_BASIC_PARAMS_PWM
         - MODULE_BASIC_PARAMS_I_TEC_MAX
         - MODULE_BASIC_PARAMS_T_DET
        """
        return cls(generate_msg_set_fan(module_type, mode))

    @classmethod
    def generate_msg_set_supply_voltage(cls, module_type: ModuleType,
                                        supp_ctrl_mode: PtccCtrl, supply_voltage_positive: float,
                                        supply_voltage_negative: float):
        """
        Generates message for setting output voltage values of power lines.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        supp_ctrl_mode: PtccCtrl
            Variable is used to set operating mode of power supply output. AUTO mode is used to protect the detector.
        supply_voltage_positive: float
            Represented in Volts. Responsible for setting output voltage value of positive power line.
        supply_voltage_negative: float
            Represented in Volts. Responsible for setting output voltage value of positive power line.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_supply_voltage(module_type,
                                                   supp_ctrl_mode, supply_voltage_positive,
                                                   supply_voltage_negative))

    @classmethod
    def generate_msg_set_max_current(cls, module_type: ModuleType, value_in_amperes: float):
        """
        Generates message for setting maximum current for TEC output.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        value_in_amperes: float
            Represented in Amperes. Describes maximum current for TEC output.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_BASIC_PARAMS
         - MODULE_BASIC_PARAMS_SUP_CTRL
         - MODULE_BASIC_PARAMS_U_SUP_PLUS
         - MODULE_BASIC_PARAMS_U_SUP_MINUS
         - MODULE_BASIC_PARAMS_FAN_CTRL
         - MODULE_BASIC_PARAMS_TEC_CTRL
         - MODULE_BASIC_PARAMS_PWM
         - MODULE_BASIC_PARAMS_I_TEC_MAX
         - MODULE_BASIC_PARAMS_T_DET
        """
        return cls(generate_msg_set_max_current(module_type, value_in_amperes))

    @classmethod
    def generate_msg_set_temperature(cls, module_type: ModuleType,
                                     value_in_kelvins: int):
        """
        Generates message for setting and saving desired detector temperature.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        value_in_kelvins: int
            Represented in Kelvins. Describes desired detector temperature.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_BASIC_PARAMS
         - MODULE_BASIC_PARAMS_SUP_CTRL
         - MODULE_BASIC_PARAMS_U_SUP_PLUS
         - MODULE_BASIC_PARAMS_U_SUP_MINUS
         - MODULE_BASIC_PARAMS_FAN_CTRL
         - MODULE_BASIC_PARAMS_TEC_CTRL
         - MODULE_BASIC_PARAMS_PWM
         - MODULE_BASIC_PARAMS_I_TEC_MAX
         - MODULE_BASIC_PARAMS_T_DET
        """
        return cls(generate_msg_set_temperature(module_type, value_in_kelvins))

    @classmethod
    def generate_msg_set_module_lab_m_detector_voltage_bias(cls, module_type: ModuleType,
                                                            bias_value_in_volts: float):
        """
        Generates message for setting and saving value of detector bias voltage for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        bias_value_in_volts: float
            lab_m voltage bias in Volts.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_detector_voltage_bias(module_type, bias_value_in_volts))

    @classmethod
    def generate_msg_set_module_lab_m_detector_current_bias_compensation(cls, module_type: ModuleType,
                                                                         bias_value_in_ampers: float):
        """
        Generates message for setting and saving value of bias current compensation for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        bias_value_in_ampers: float
            lab_m currrent bias compensation in Ampers.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_detector_current_bias_compensation(module_type,
                                                                                    bias_value_in_ampers))

    @classmethod
    def generate_msg_set_module_lab_m_gain(cls, module_type: ModuleType,
                                           gain: Union[GainVoltPerVolt, int]):
        """
        Generates message for setting and saving value of second stage gain for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        gain: Union[GainVoltPerVolt, int]
            lab_m gain.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_gain(module_type, gain))

    @classmethod
    def generate_msg_set_module_lab_m_offset(cls, module_type: ModuleType,
                                             offset_value_in_volts: float):
        """
        Generates message for setting and saving lab_m output DC offset for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        offset_value_in_volts: int
            lab_m offset.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_offset(module_type, offset_value_in_volts))

    @classmethod
    def generate_msg_set_module_lab_m_varactor(cls, module_type: ModuleType,
                                               compensation: int):
        """
        Generates message for setting and saving frequency compensation for the preamplifier first stage for lab_m
        module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.
        compensation: int
            lab_m frequency compensation.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_varactor(module_type, compensation))

    @classmethod
    def generate_msg_set_module_lab_m_transimpedance_low(cls, module_type: ModuleType):
        """
        Generates message for setting and saving transimpedance of first stage preamplifier as LOW for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_transimpedance_low(module_type))

    @classmethod
    def generate_msg_set_module_lab_m_transimpedance_high(cls, module_type: ModuleType):
        """
        Generates message for setting and saving transimpedance of first stage preamplifier as HIGH for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_transimpedance_high(module_type))

    @classmethod
    def generate_msg_set_module_lab_m_coupling_ac(cls, module_type: ModuleType):
        """
        Generates message for setting and saving the coupling mode as AC for lab_m module for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_coupling_ac(module_type))

    @classmethod
    def generate_msg_set_module_lab_m_coupling_dc(cls, module_type: ModuleType):
        """
        Generates message for setting and saving the coupling mode as DC for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_coupling_dc(module_type))

    @classmethod
    def generate_msg_set_module_lab_m_bandwidth_low(cls, module_type: ModuleType):
        """
        Generates message for setting and saving value of bandwidth as LOW (1.5 MHz) for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_bandwidth_low(module_type))

    @classmethod
    def generate_msg_set_module_lab_m_bandwidth_mid(cls, module_type: ModuleType):
        """
        Generates message for setting and saving value of bandwidth as MID (15 MHz) for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_bandwidth_mid(module_type))

    @classmethod
    def generate_msg_set_module_lab_m_bandwidth_high(cls, module_type: ModuleType):
        """
        Generates message for setting and saving value of bandwidth as HIGH (Depends on detector parameters and first
        stage transimpedance) for lab_m module.

        Parameters
        ----------
        module_type: ModuleType
            Specifies type of device/module for which the message is generated.

        Raises
        ------
        ValueError
            if module type is not supported for this kind of message.

        Notes
        -----
        PTCC device will respond to this message.
        You can set those CallbackPtccObjectID to see the response:

         - MODULE_LAB_M_PARAMS
         - MODULE_LAB_M_PARAMS_DET_U
         - MODULE_LAB_M_PARAMS_DET_I
         - MODULE_LAB_M_PARAMS_GAIN
         - MODULE_LAB_M_PARAMS_OFFSET
         - MODULE_LAB_M_PARAMS_VARACTOR
         - MODULE_LAB_M_PARAMS_TRANS
         - MODULE_LAB_M_PARAMS_ACDC
         - MODULE_LAB_M_PARAMS_BW
        """
        return cls(generate_msg_set_module_lab_m_bandwidth_high(module_type))


class PtccMessageReceiver:
    """
    Receives, assembles, and decodes PTCC protocol messages byte-by-byte.

    This class manages the incremental reception of raw PTCC messages, converting them
    into `PtccObject` instances once a full message is received and validated. It can optionally
    trigger user-defined callbacks for specific object IDs and handles message buffering and errors.

    Parameters
    ----------
    clear_all_after_receive : bool, optional
        If True (default), the internal state (messages, objects, and errors) is cleared after
        each successful message decode.

    Attributes
    ----------
    messages : list of PtccMessage
        Stores the list of currently received `PtccMessage` objects.
    objects : list of PtccObject
        Stores successfully decoded `PtccObject` instances.
    errors : list of Exception
        Captures exceptions raised during message parsing or decoding.
    clear_all_after_receive : bool
        Controls whether the internal state is cleared after a full message has been successfully received.
    callbacks : dict[int, Tuple[Callable[[Any, Any], None], Any]]
        A registry of callbacks mapped by object ID. Each callback takes a `PtccObject` and optional user data.
    """

    def __init__(self, clear_all_after_receive: bool = True):
        self.messages: list[PtccMessage] = []
        self.objects: list[PtccObject] = []
        self.errors: list[Exception] = []

        self.clear_all_after_receive = clear_all_after_receive

        # A registry mapping object IDs to callbacks.
        # Each callback gets a single argument (the received object) or more if needed.
        self.callbacks: dict[int, Tuple[Callable[[Any, Any], None], Any]] = {}

    def reset(self):
        """
        Clears all internal state, including callbacks.
        """
        self.clear_all()

        self.callbacks.clear()

    def add_byte(self, byte: int) -> PtccMessageReceiveStatus:
        """
        Processes an incoming byte and updates message state. Returns message receive status.
        """

        index = len(self.messages) - 1
        if index == -1 or self.messages[index].receive_status == PtccMessageReceiveStatus.FINISHED:
            if byte == START_BYTE:
                self.messages.append(PtccMessage([byte]))
        else:
            try:
                if self.messages[index].append_byte(byte) == PtccMessageReceiveStatus.FINISHED:
                    try:
                        obj = self.messages[index].to_ptcc_object()
                        self.objects.append(obj)
                        self.obj_received_callback(obj)
                        if self.clear_all_after_receive:
                            self.clear_all()
                        return PtccMessageReceiveStatus.FINISHED
                    except Exception as e:
                        self.errors.append(e)
            except Exception as e:
                self.errors.append(e)
        return PtccMessageReceiveStatus.IN_PROGRESS

    def clear_messages(self) -> None:
        """
        Clears all received raw messages.
        """
        self.messages.clear()

    def clear_objects(self) -> None:
        """
        Clears all decoded PtccObject instances.
        """
        self.objects.clear()

    def clear_errors(self) -> None:
        """
        Clears any parsing or decoding errors.
        """
        self.errors.clear()

    def clear_all(self) -> None:
        """
        Clears messages, objects, and errors.
        """
        self.clear_errors()
        self.clear_messages()
        self.clear_objects()

    @overload
    def register_callback(self, object_id: Union[int, 'CallbackPtccObjectID'], callback: Callable[[Any], None]) -> None:
        ...

    @overload
    def register_callback(self, object_id: Union[int, 'CallbackPtccObjectID'], callback: Callable[[Any, Any], None],
                          user_data: Any) -> None:
        ...

    def register_callback(
            self,
            object_id: Union[int, 'CallbackPtccObjectID'],
            callback: Union[Callable[[Any], None], Callable[[Any, Any], None]],
            user_data: Any = None
    ) -> None:
        """Register a callback function (with or without user data) for a particular object ID."""
        if isinstance(object_id, CallbackPtccObjectID):
            object_id = object_id.value

        # Check if the callback takes one or two parameters
        sig = inspect.signature(callback)
        num_params = len(sig.parameters)

        if num_params == 1:
            # Wrap the callback to ignore user_data
            def wrapped(event_data: Any, _: Any = None):
                return callback(event_data)
        elif num_params == 2:
            # Use as-is
            wrapped = callback
        else:
            raise ValueError("Callback must accept 1 or 2 arguments.")

        self.callbacks[object_id] = (wrapped, user_data)

    def obj_received_callback(self, obj: PtccObject) -> None:
        """
        Process a received object. If a callback is registered for this object's id,
        call it; if the object id is in ignored_objects, ignore it; otherwise raise an error.
        """
        if obj.is_container:
            for o in obj.objects:
                try:
                    self.obj_received_callback(o)
                except Exception as e:
                    self.errors.append(e)

        if obj.obj_id in self.callbacks:
            callback, user_data = self.callbacks[obj.obj_id]
            callback(obj.value, user_data)

    def add_bytes(self, bytes: Union[list[int], bytes, bytearray]) -> None:
        """
        Processes an incoming bytes and updates message state. Returns message receive status.
        """
        for b in bytes:
            self.add_byte(b)


def generate_msg_get_device_iden() -> list[int]:
    """
    Generates message for reading identification data of PTCC device.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - DEVICE_IDEN
     - DEVICE_IDEN_TYPE
     - DEVICE_IDEN_FIRM_VER
     - DEVICE_IDEN_HARD_VER
     - DEVICE_IDEN_NAME
     - DEVICE_IDEN_SERIAL
     - DEVICE_IDEN_PROD_DATE
    """
    return create_get_ptcc_message(PtccObjectID.GET_DEVICE_IDEN)


def generate_msg_get_module_iden(module_type: ModuleType) -> list[int]:
    """
    Generates message for reading identification and configuration data of module connected to PTCC device.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_IDEN
     - MODULE_IDEN_TYPE
     - MODULE_IDEN_FIRM_VER
     - MODULE_IDEN_HARD_VER
     - MODULE_IDEN_NAME
     - MODULE_IDEN_SERIAL
     - MODULE_IDEN_DET_NAME
     - MODULE_IDEN_DET_SERIAL
     - MODULE_IDEN_PROD_DATE
     - MODULE_IDEN_TEC_TYPE
     - MODULE_IDEN_TH_TYPE
     - MODULE_IDEN_TEC_PARAM1
     - MODULE_IDEN_TEC_PARAM2
     - MODULE_IDEN_TEC_PARAM3
     - MODULE_IDEN_TEC_PARAM4
     - MODULE_IDEN_TH_PARAM1
     - MODULE_IDEN_TH_PARAM2
     - MODULE_IDEN_TH_PARAM3
     - MODULE_IDEN_TH_PARAM4
     - MODULE_IDEN_COOL_TIME
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        msg = create_get_ptcc_message(PtccObjectID.GET_PTCC_MOD_NO_MEM_IDEN)
    elif module_type == ModuleType.MEM:
        msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_IDEN)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_get_module_iden(ModuleType.MEM)
    return msg


def generate_msg_get_monitor() -> list[int]:
    """
    Generates message for reading measured parameters of no memory module connected to PTCC device.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - PTCC_MONITOR
     - PTCC_MONITOR_SUP_ON
     - PTCC_MONITOR_I_SUP_PLUS
     - PTCC_MONITOR_I_SUP_MINUS
     - PTCC_MONITOR_FAN_ON
     - PTCC_MONITOR_I_FAN_PLUS
     - PTCC_MONITOR_I_TEC
     - PTCC_MONITOR_U_TEC
     - PTCC_MONITOR_U_SUP_PLUS
     - PTCC_MONITOR_U_SUP_MINUS
     - PTCC_MONITOR_T_DET
     - PTCC_MONITOR_T_INT
     - PTCC_MONITOR_PWM
     - PTCC_MONITOR_STATUS
     - PTCC_MONITOR_MODULE_TYPE
     - PTCC_MONITOR_TH_ADC
    """
    return create_get_ptcc_message(PtccObjectID.GET_PTCC_MONITOR)


def generate_msg_get_lab_m_monitor(module_type: ModuleType) -> list[int]:
    """
    Generates message for reading measured lab_m parameters of module connected to PTCC device.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_MONITOR
     - MODULE_LAB_M_MONITOR_SUP_PLUS
     - MODULE_LAB_M_MONITOR_SUP_MINUS
     - MODULE_LAB_M_MONITOR_FAN_PLUS
     - MODULE_LAB_M_MONITOR_TEC_PLUS
     - MODULE_LAB_M_MONITOR_TEC_MINUS
     - MODULE_LAB_M_MONITOR_TH1
     - MODULE_LAB_M_MONITOR_TH2
     - MODULE_LAB_M_MONITOR_U_DET
     - MODULE_LAB_M_MONITOR_U_1ST
     - MODULE_LAB_M_MONITOR_U_OUT
     - MODULE_LAB_M_MONITOR_TEMP
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_LAB_M_MONITOR)
    return msg


def generate_msg_get_basic_params(module_type: ModuleType, target: DeviceRegister = DeviceRegister.USER_SET) -> \
        list[int]:
    """
    Generates message for reading configuration (power, cooling) data for module connected to PTCC device.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    target: DeviceRegister
        Specifies which type of register should be read:
        DeviceRegister.DEFAULT - register for default setting.
        DeviceRegister.USER_SET - register for user setting.
        DeviceRegister.USER_MIN - register for max allowed setting.
        DeviceRegister.USER_MAX - register for min allowed setting.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message, or if target register is not recognized.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_BASIC_PARAMS
     - MODULE_BASIC_PARAMS_SUP_CTRL
     - MODULE_BASIC_PARAMS_U_SUP_PLUS
     - MODULE_BASIC_PARAMS_U_SUP_MINUS
     - MODULE_BASIC_PARAMS_FAN_CTRL
     - MODULE_BASIC_PARAMS_TEC_CTRL
     - MODULE_BASIC_PARAMS_PWM
     - MODULE_BASIC_PARAMS_I_TEC_MAX
     - MODULE_BASIC_PARAMS_T_DET
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        if target == DeviceRegister.DEFAULT:
            msg = create_get_ptcc_message(PtccObjectID.GET_PTCC_MOD_NO_MEM_DEFAULT)
        elif target == DeviceRegister.USER_SET:
            msg = create_get_ptcc_message(PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_SET)
        elif target == DeviceRegister.USER_MIN:
            msg = create_get_ptcc_message(PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_MIN)
        elif target == DeviceRegister.USER_MAX:
            msg = create_get_ptcc_message(PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_MAX)
        else:
            raise ValueError(f"Target not recognized: {target}")
    elif module_type == ModuleType.MEM:
        if target == DeviceRegister.DEFAULT:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_DEFAULT)
        elif target == DeviceRegister.USER_SET:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_USER_SET)
        elif target == DeviceRegister.USER_MIN:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_USER_MIN)
        elif target == DeviceRegister.USER_MAX:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_USER_MAX)
        else:
            raise ValueError(f"Target not recognized: {target}")
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_get_basic_params(ModuleType.MEM)
    return msg


def generate_msg_get_lab_m_params(module_type: ModuleType, target: DeviceRegister = DeviceRegister.USER_SET) -> \
        list[int]:
    """
    Generates message for reading lab_m configuration data for module connected to PTCC device.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    target: DeviceRegister
        Specifies which type of register should be read:
        DeviceRegister.DEFAULT - register for default setting.
        DeviceRegister.USER_SET - register for user setting.
        DeviceRegister.USER_MIN - register for max allowed setting.
        DeviceRegister.USER_MAX - register for min allowed setting.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message, or if target register is not recognized.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        if target == DeviceRegister.DEFAULT:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_LAB_M_DEFAULT)
        elif target == DeviceRegister.USER_SET:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_LAB_M_USER_SET)
        elif target == DeviceRegister.USER_MIN:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_LAB_M_USER_MIN)
        elif target == DeviceRegister.USER_MAX:
            msg = create_get_ptcc_message(PtccObjectID.GET_MODULE_LAB_M_USER_MAX)
        else:
            raise ValueError(f"Target not recognized: {target}")
    return msg


def generate_msg_get_config() -> list[int]:
    """
    Generates message for reading PTCC device type.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - PTCC_CONFIG
     - PTCC_CONFIG_VARIANT
     - PTCC_CONFIG_NO_MEM_COMPATIBLE
    """
    return create_get_ptcc_message(PtccObjectID.GET_PTCC_CONFIG)


def generate_msg_set_module_lab_m_param(module_type: ModuleType,
                                        ptcc_object: PtccObject) -> list[int]:
    """
    Generates message for setting and saving lab_m parameters.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    ptcc_object: PtccObject
        PTCC object to send as configuration.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        if PtccObjectID(ptcc_object.obj_id) not in LAB_M_PARAMS_IDS:
            raise ValueError(f"{ptcc_object.obj_id} is not a valid LAB_M Params Object ID")
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET, ptcc_objects=ptcc_object)
    return msg


def generate_msg_set_cooler_disabled(module_type: ModuleType) -> list[int]:
    """
    Generates message for setting and saving operating mode of TEC as disabled.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_BASIC_PARAMS
     - MODULE_BASIC_PARAMS_SUP_CTRL
     - MODULE_BASIC_PARAMS_U_SUP_PLUS
     - MODULE_BASIC_PARAMS_U_SUP_MINUS
     - MODULE_BASIC_PARAMS_FAN_CTRL
     - MODULE_BASIC_PARAMS_TEC_CTRL
     - MODULE_BASIC_PARAMS_PWM
     - MODULE_BASIC_PARAMS_I_TEC_MAX
     - MODULE_BASIC_PARAMS_T_DET
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL, data_value=1)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_object)
    elif module_type == ModuleType.MEM:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL, data_value=1)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_object)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_set_cooler_disabled(ModuleType.MEM)
    return msg


def generate_msg_set_cooler_enabled(module_type: ModuleType) -> list[int]:
    """
    Generates message for setting and saving operating mode of TEC as enabled (Cooler will work with fixed supply
    current).

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_BASIC_PARAMS
     - MODULE_BASIC_PARAMS_SUP_CTRL
     - MODULE_BASIC_PARAMS_U_SUP_PLUS
     - MODULE_BASIC_PARAMS_U_SUP_MINUS
     - MODULE_BASIC_PARAMS_FAN_CTRL
     - MODULE_BASIC_PARAMS_TEC_CTRL
     - MODULE_BASIC_PARAMS_PWM
     - MODULE_BASIC_PARAMS_I_TEC_MAX
     - MODULE_BASIC_PARAMS_T_DET
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL, data_value=2)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_object)
    elif module_type == ModuleType.MEM:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL, data_value=2)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_object)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_set_cooler_enabled(ModuleType.MEM)
    return msg


def generate_msg_set_cooler_auto(module_type: ModuleType) -> list[int]:
    """
    Generates message for setting and saving operating mode of TEC as auto.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_BASIC_PARAMS
     - MODULE_BASIC_PARAMS_SUP_CTRL
     - MODULE_BASIC_PARAMS_U_SUP_PLUS
     - MODULE_BASIC_PARAMS_U_SUP_MINUS
     - MODULE_BASIC_PARAMS_FAN_CTRL
     - MODULE_BASIC_PARAMS_TEC_CTRL
     - MODULE_BASIC_PARAMS_PWM
     - MODULE_BASIC_PARAMS_I_TEC_MAX
     - MODULE_BASIC_PARAMS_T_DET
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL, data_value=0)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_object)
    elif module_type == ModuleType.MEM:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL, data_value=0)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_object)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_set_cooler_auto(ModuleType.MEM)
    return msg


def generate_msg_set_module_param(module_type: ModuleType, ptcc_object: PtccObject) -> \
        list[int]:
    """
    Generates message for setting and saving module parameters.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    ptcc_object: PtccObject
        PTCC object to send as configuration. Objects ID must be from BASIC_PARAMS_IDS list.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        if PtccObjectID(ptcc_object.obj_id) not in BASIC_PARAMS_IDS:
            raise ValueError(f"{ptcc_object.obj_id} is not a valid Basic Params Object ID")
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_object)
    elif module_type == ModuleType.MEM:
        if PtccObjectID(ptcc_object.obj_id) not in BASIC_PARAMS_IDS:
            raise ValueError(f"{ptcc_object.obj_id} is not a valid Basic Params Object ID")
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_object)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_set_module_param(ModuleType.MEM, ptcc_object)
    return msg


def generate_msg_set_fan(module_type: ModuleType, mode: PtccCtrl) -> list[int]:
    """
    Generates message for setting and saving operation state of fan control.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    mode: PtccCtrl
        operation state of fan control. On, Off or Auto.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_BASIC_PARAMS
     - MODULE_BASIC_PARAMS_SUP_CTRL
     - MODULE_BASIC_PARAMS_U_SUP_PLUS
     - MODULE_BASIC_PARAMS_U_SUP_MINUS
     - MODULE_BASIC_PARAMS_FAN_CTRL
     - MODULE_BASIC_PARAMS_TEC_CTRL
     - MODULE_BASIC_PARAMS_PWM
     - MODULE_BASIC_PARAMS_I_TEC_MAX
     - MODULE_BASIC_PARAMS_T_DET
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:

        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_FAN_CTRL, value=mode.value)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_object)
    elif module_type == ModuleType.MEM:

        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_FAN_CTRL, value=mode.value)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_object)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_set_fan(ModuleType.MEM, mode)
    return msg


def generate_msg_set_supply_voltage(module_type: ModuleType, supp_ctrl_mode: PtccCtrl,
                                    supply_voltage_positive: float, supply_voltage_negative: float) -> list[int]:
    """
    Generates message for setting output voltage values of power lines.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    supp_ctrl_mode: PtccCtrl
        Variable is used to set operating mode of power supply output. AUTO mode is used to protect the detector.
    supply_voltage_positive: float
        Represented in Volts. Responsible for setting output voltage value of positive power line.
    supply_voltage_negative: float
        Represented in Volts. Responsible for setting output voltage value of positive power line.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        ptcc_objects = [
            PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_SUP_CTRL, value=supp_ctrl_mode.value),
            PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS, value=supply_voltage_positive),
            PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS, value=supply_voltage_negative),
        ]
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_objects)
    elif module_type == ModuleType.MEM:
        ptcc_objects = [
            PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_SUP_CTRL, value=supp_ctrl_mode.value),
            PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS, value=supply_voltage_positive),
            PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS, value=supply_voltage_negative),
        ]
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_objects)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_set_supply_voltage(ModuleType.MEM, supp_ctrl_mode, supply_voltage_positive,
                                              supply_voltage_negative)
    return msg


def generate_msg_set_max_current(module_type: ModuleType, value_in_amperes: float) -> list[int]:
    """
    Generates message for setting maximum current for TEC output.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    value_in_amperes: float
        Represented in Amperes. Describes maximum current for TEC output.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_BASIC_PARAMS
     - MODULE_BASIC_PARAMS_SUP_CTRL
     - MODULE_BASIC_PARAMS_U_SUP_PLUS
     - MODULE_BASIC_PARAMS_U_SUP_MINUS
     - MODULE_BASIC_PARAMS_FAN_CTRL
     - MODULE_BASIC_PARAMS_TEC_CTRL
     - MODULE_BASIC_PARAMS_PWM
     - MODULE_BASIC_PARAMS_I_TEC_MAX
     - MODULE_BASIC_PARAMS_T_DET
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:

        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX, value=value_in_amperes)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_object)
    elif module_type == ModuleType.MEM:

        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX, value=value_in_amperes)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_object)
    elif module_type == ModuleType.LAB_M:
        msg = generate_msg_set_max_current(ModuleType.MEM, value_in_amperes)
    return msg


def generate_msg_set_temperature(module_type: ModuleType, value_in_kelvins: int) -> list[int]:
    """
    Generates message for setting and saving desired detector temperature.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    value_in_kelvins: int
        Represented in Kelvins. Describes desired detector temperature.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_BASIC_PARAMS
     - MODULE_BASIC_PARAMS_SUP_CTRL
     - MODULE_BASIC_PARAMS_U_SUP_PLUS
     - MODULE_BASIC_PARAMS_U_SUP_MINUS
     - MODULE_BASIC_PARAMS_FAN_CTRL
     - MODULE_BASIC_PARAMS_TEC_CTRL
     - MODULE_BASIC_PARAMS_PWM
     - MODULE_BASIC_PARAMS_I_TEC_MAX
     - MODULE_BASIC_PARAMS_T_DET
    """
    msg = []
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:

        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_T_DET, value=value_in_kelvins)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                                      ptcc_objects=ptcc_object)
    elif module_type == ModuleType.MEM:

        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_BASIC_PARAMS_T_DET, value=value_in_kelvins)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_USER_SET, ptcc_objects=ptcc_object)
    elif module_type == ModuleType.LAB_M:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    return msg


def generate_msg_set_module_lab_m_detector_voltage_bias(module_type: ModuleType,
                                                        bias_value_in_volts: float) -> \
        list[int]:
    """
    Generates message for setting and saving value of detector bias voltage for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    bias_value_in_volts: float
        lab_m voltage bias in Volts.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_DET_U, value=bias_value_in_volts)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_detector_current_bias_compensation(module_type: ModuleType,
                                                                     bias_value_in_ampers: float) -> \
        list[int]:
    """
    Generates message for setting and saving value of bias current compensation for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    bias_value_in_ampers: float
        lab_m currrent bias compensation in Ampers.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_DET_I, value=bias_value_in_ampers)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_gain(module_type: ModuleType,
                                       gain: Union[GainVoltPerVolt, int]) -> \
        list[int]:
    """
    Generates message for setting and saving value of second stage gain for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    gain: Union[GainVoltPerVolt, int]
        lab_m gain.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if isinstance(gain, GainVoltPerVolt):
        gain = gain.value
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_GAIN, data_value=gain)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_offset(module_type: ModuleType,
                                         offset_value_in_volts: float) -> \
        list[int]:
    """
    Generates message for setting and saving lab_m output DC offset for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    offset_value_in_volts: int
        lab_m offset.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_OFFSET, value=offset_value_in_volts)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_varactor(module_type: ModuleType,
                                           compensation: int) -> \
        list[int]:
    """
    Generates message for setting and saving frequency compensation for the preamplifier first stage for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.
    compensation: int
        lab_m frequency compensation.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_VARACTOR, data_value=compensation)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_transimpedance_low(module_type: ModuleType) -> \
        list[int]:
    """
    Generates message for setting and saving transimpedance of first stage preamplifier as LOW for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_TRANS, data_value=0)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_transimpedance_high(module_type: ModuleType) -> \
        list[int]:
    """
    Generates message for setting and saving transimpedance of first stage preamplifier as HIGH for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_TRANS, data_value=1)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_coupling_ac(module_type: ModuleType) -> \
        list[int]:
    """
    Generates message for setting and saving the coupling mode as AC for lab_m module for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_ACDC, data_value=0)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_coupling_dc(module_type: ModuleType) -> \
        list[int]:
    """
    Generates message for setting and saving the coupling mode as DC for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_ACDC, data_value=1)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_bandwidth_low(module_type: ModuleType) -> \
        list[int]:
    """
    Generates message for setting and saving value of bandwidth as LOW (1.5 MHz) for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_BW, data_value=0)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_bandwidth_mid(module_type: ModuleType) -> \
        list[int]:
    """
    Generates message for setting and saving value of bandwidth as MID (15 MHz) for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_BW, data_value=1)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg


def generate_msg_set_module_lab_m_bandwidth_high(module_type: ModuleType) -> \
        list[int]:
    """
    Generates message for setting and saving value of bandwidth as HIGH (Depends on detector parameters and first stage
    transimpedance) for lab_m module.

    Parameters
    ----------
    module_type: ModuleType
        Specifies type of device/module for which the message is generated.

    Returns
    -------
    list[int]
        List of bytes of message a single message.

    Raises
    ------
    ValueError
        if module type is not supported for this kind of message.

    Notes
    -----
    PTCC device will respond to this message.
    You can set those CallbackPtccObjectID to see the response:

     - MODULE_LAB_M_PARAMS
     - MODULE_LAB_M_PARAMS_DET_U
     - MODULE_LAB_M_PARAMS_DET_I
     - MODULE_LAB_M_PARAMS_GAIN
     - MODULE_LAB_M_PARAMS_OFFSET
     - MODULE_LAB_M_PARAMS_VARACTOR
     - MODULE_LAB_M_PARAMS_TRANS
     - MODULE_LAB_M_PARAMS_ACDC
     - MODULE_LAB_M_PARAMS_BW
    """
    if module_type == ModuleType.NONE:
        raise ValueError("Unspecified module type")
    elif module_type == ModuleType.NOMEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.MEM:
        raise ValueError(f"Message not supported for this module type: {module_type}")
    elif module_type == ModuleType.LAB_M:
        ptcc_object = PtccObject(obj_id=PtccObjectID.MODULE_LAB_M_PARAMS_BW, data_value=2)
        msg = create_set_ptcc_message(set_command_id=PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                                      ptcc_objects=ptcc_object)
        return msg
