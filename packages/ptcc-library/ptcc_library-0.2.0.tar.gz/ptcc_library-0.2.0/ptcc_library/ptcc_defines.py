# Author: Wojciech Szczytko
# Created: 2025-03-28
import ctypes
from enum import Enum

START_BYTE = 0x24
STOP_BYTE = 0x23


class ValType(Enum):
    """
    Enum for identifying PTCC data types.
    """
    CONTAINER = 0
    CSTR = 1
    INT8 = 2
    UINT8 = 3
    INT16 = 4
    UINT16 = 5
    INT32 = 6
    UINT32 = 7
    FLOAT = 8
    DATE_TIME = 9
    SERIAL_NUMBER = 10
    BOOL = 11


class PtccCtrl(Enum):
    """
    Enum for setting operating mode of PTCC
    """
    AUTO = 0
    OFF = 1
    ON = 2


class PtccTimeStruct(ctypes.Structure):
    """
    PTCC time format.
    """
    _fields_ = (
        ('msec', ctypes.c_uint16),
        ('sec', ctypes.c_uint8),
        ('min', ctypes.c_uint8),
        ('hour', ctypes.c_uint8),
        ('day', ctypes.c_uint8),
        ('mon', ctypes.c_uint8),
        ('year', ctypes.c_uint8)
    )


class PtccObjectID(Enum):
    """
    Enum for all possible PtccObject ids.

    Attributes
    ----------
    GET_PTCC_CONFIG
        Container. Command is used to read PTCC device type.
    GET_PTCC_MONITOR
        Container. Command is used to read measured parameters of no memory module connected to PTCC device.
    GET_PTCC_MOD_NO_MEM_IDEN
        Container. Command is used to read identification and configuration data of module connected to PTCC device.
    GET_PTCC_MOD_NO_MEM_USER_SET
        Container. Command is used to read user settings.
    GET_PTCC_MOD_NO_MEM_USER_MIN
        Container. Command is used to read minimum settings.
    GET_PTCC_MOD_NO_MEM_USER_MAX
        Container. Command is used to read maximum settings.
    GET_PTCC_MOD_NO_MEM_DEFAULT
        Container. Command is used to read default configuration data.
    SET_PTCC_MOD_NO_MEM_USER_SET
        Container. Command is used to set and save user settings.
    GET_MODULE_IDEN
        Container. Command is used to read identification and configuration data of module connected to PTCC device.
    GET_MODULE_USER_SET
        Container. Command is used to read basic user settings.
    GET_MODULE_USER_MIN
        Container. Command is used to read minimum basic settings.
    GET_MODULE_USER_MAX
        Container. Command is used to read maximum basic settings.
    GET_MODULE_DEFAULT
        Container. Command is used to read default configurations.
    SET_MODULE_USER_SET
        Container. Command is used to set and save basic user settings.
    GET_MODULE_LAB_M_MONITOR
        Container. Command is used to read measured lab_m parameters of module connected to PTCC device.
    GET_MODULE_LAB_M_USER_SET
        Container. Command is used to read configuration.
    GET_MODULE_LAB_M_USER_MIN
        Container. Command is used to read minimum settings.
    GET_MODULE_LAB_M_USER_MAX
        Container. Command is used to read maximum settings.
    GET_MODULE_LAB_M_DEFAULT
        Container. Command is used to read default configuration.
    SET_MODULE_LAB_M_USER_SET
        Container. Command is used to set and save configuration.
    PTCC_CONFIG
        Container. Stores PTCC_CONFIG objects.
    PTCC_MONITOR
        Container. Stores PTCC_MONITOR objects.
    MODULE_IDEN
        Container. Stores MODULE_IDEN objects.
    MODULE_BASIC_PARAMS
        Container. Stores MODULE_BASIC_PARAMS objects.
    MODULE_LAB_M_MONITOR
        Container. Stores MODULE_LAB_M_MONITOR objects.
    MODULE_LAB_M_PARAMS
        Container. Stores MODULE_LAB_M_PARAMS objects.
    GET_DEVICE_IDEN
        Container. Command is used to read identification data of PTCC device.
    DEVICE_IDEN
        Container. Stores DEVICE_IDEN objects.
    PTCC_CONFIG_VARIANT
        PTCC_CONFIG object. Determines the version of PTTC device.
        Data Value:
            See PTCC_CONFIG_VARIANT_VALUES.
    PTCC_CONFIG_NO_MEM_COMPATIBLE
        PTCC_CONFIG object. Responsible for availability of EEPROM memory.
        Data Value:
            True
                EEPROM memory available.
            False
                EEPROM memory unavailable.
    PTCC_MONITOR_SUP_ON
        SMARTTEC_MONITOR object. Checks operation state of power supply lines.
        Data Value:
            True
                Power supply lines are active.
            False
                Power supply lines are inactive.
    PTCC_MONITOR_I_SUP_PLUS
        SMARTTEC_MONITOR object. Reads current value of positive supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_I_SUP_MINUS
        SMARTTEC_MONITOR object. Reads current value of negative supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_FAN_ON
        SMARTTEC_MONITOR object. Checks operation state of fan output.
        Data Value:
            True;
                Enable fan output.
            False
                Disable fan output.
    PTCC_MONITOR_I_FAN_PLUS
        SMARTTEC_MONITOR object. Reads output current value of fan output.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_I_TEC
        SMARTTEC_MONITOR object. Reads current value of TEC output.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_U_TEC
        SMARTTEC_MONITOR object. Reads output voltage value of TEC.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_U_SUP_PLUS
        SMARTTEC_MONITOR object. Reads output voltage value of positive supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_U_SUP_MINUS
        SMARTTEC_MONITOR object. Reads output voltage value of negative supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_T_DET
        SMARTTEC_MONITOR object. Reads detector temperature in Kelvins.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_T_INT
        SMARTTEC_MONITOR object. Reads detector temperature in Celsius degrees.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_PWM
        SMARTTEC_MONITOR object. Reads PWM settings of TEC controller.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_STATUS
        SMARTTEC_MONITOR object.
        Data Value:
            See status_messages and error_messages.
            Status code:
                 - 0 – detector is cooled, temperature is equal(-/+ 1 K) to temperature defined by user.
                 - 1 – during the cooling proces.
                 - 2 - the cooling is deactivated. Check PTTC settings.
                 - 3 - cooler is working with fixed current.
            Error code:
                 - 128 - “detector overheat” - the set temperature could not be reached during 120 second.
                 - 129 - Measured current value is higher then maximum current value. PTTC power is off.
                 - 130 - TEC circuit open connection.
                 - 131 - TEC circuit is closed connection.
                 - 132 - thermistor circuit open connection.
                 - 133 - thermistor circuit closed connection.
                 - 134 - the temperature inside PTCC is higher than limit.
                 - 135 - the connected module without memory is not compatible or no module is connected.
                 - 136 - memory was detected but there are some communication problem.
                 - 137 – PIP data fault, there are some communication problem.
                 - 138 - Communication with memory data fault, there are some communication problem.
                 - 139 - PTTC memory fault.
                 - 140 - Lab M is incompatible.
                 - 141 - Memory is incompatible. When the error status code appears the re-turn of the PTTC devices might be required.
    PTCC_MONITOR_MODULE_TYPE
        SMARTTEC_MONITOR object. Reads type of module.
        Data Value
            See PTCC_MONITOR_MODULE_TYPE_VALUES.
    PTCC_MONITOR_TH_ADC
        SMARTTEC_MONITOR object. Reads voltage value of thermistor.
        Data Value
            Available PtccUnits.
    MODULE_IDEN_TYPE
        MODULE_IDEN object. Describes type of memory.
        Data Value
            See MODULE_IDEN_TYPE_VALUES.
    MODULE_IDEN_FIRM_VER
        MODULE_IDEN object. Describes version of firmware.
        Data Value
            UINT16.
    MODULE_IDEN_HARD_VER
        MODULE_IDEN object. Describes version of hardware.
        Data Value
            UINT16.
    MODULE_IDEN_NAME
        MODULE_IDEN object. Describes module name.
        Data Value
            CSTR. See MODULE_IDEN_NAME_SIZE.
    MODULE_IDEN_SERIAL
        MODULE_IDEN object. Describes module serial number.
        Data Value
            SERIAL_NUMBER.
    MODULE_IDEN_DET_NAME
        MODULE_IDEN object. Describes detector name.
        Data Value
            CSTR. See MODULE_IDEN_DET_NAME_SIZE.
    MODULE_IDEN_DET_SERIAL
        MODULE_IDEN object. Describes detector serial number.
        Data Value
            SERIAL_NUMBER.
    MODULE_IDEN_PROD_DATE
        MODULE_IDEN object. Describes date of manufacture of the module.
        Data Value
            DATE_TIME.
    MODULE_IDEN_TEC_TYPE
        MODULE_IDEN object.
        Data Value
            See MODULE_IDEN_TEC_TYPE_VALUES.
    MODULE_IDEN_TH_TYPE
        MODULE_IDEN object. Describes thermistor type.
        Data Value
            UINT8.
    MODULE_IDEN_TEC_PARAM1
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TEC_PARAM2
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TEC_PARAM3
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TEC_PARAM4
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM1
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM2
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM3
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM4
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_COOL_TIME
        MODULE_IDEN object. Responsible for setting maximum time of cooling module.
        If the module does not reach desired temperature it will be turned off.
        Data Value
            UINT16.
    MODULE_BASIC_PARAMS_SUP_CTRL
        MODULE_BASIC_PARAMS object. Describes operating modes of power supply lines.
        Data Value
            See MODULE_BASIC_PARAMS_SUP_CTRL_VALUES.
    MODULE_BASIC_PARAMS_U_SUP_PLUS
        MODULE_BASIC_PARAMS object. Responsible for setting output voltage value of positive power line.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_U_SUP_MINUS
        MODULE_BASIC_PARAMS object. Responsible for setting output voltage value of negative power line.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_FAN_CTRL
        MODULE_BASIC_PARAMS object. Describes operation state of fan control.
        Data Value
            See MODULE_BASIC_PARAMS_FAN_CTRL_VALUES.
    MODULE_BASIC_PARAMS_TEC_CTRL
        MODULE_BASIC_PARAMS object. Describes operating modes of TEC cooler.
        Data Value
            See MODULE_BASIC_PARAMS_TEC_CTRL_VALUES.
    MODULE_BASIC_PARAMS_PWM
        MODULE_BASIC_PARAMS object. Describes PWM settings of TEC.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_I_TEC_MAX
        MODULE_BASIC_PARAMS object. Describes maximum current for TEC output.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_T_DET
        MODULE_BASIC_PARAMS object. Describes detector temperature in Kelvins.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_SUP_PLUS
        MODULE_LAB_M_MONITOR object. Reads voltage value of positive power line.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_SUP_MINUS
        MODULE_LAB_M_MONITOR object. Reads voltage value of negative power line.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_FAN_PLUS
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TEC_PLUS
        MODULE_LAB_M_MONITOR object. Reads maximum current for TEC positive output.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TEC_MINUS
        MODULE_LAB_M_MONITOR object. Reads maximum current for TEC negative output.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TH1
        MODULE_LAB_M_MONITOR object. Reads voltage value of thermistor pin 1.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TH2
        MODULE_LAB_M_MONITOR object. Reads voltage value of thermistor pin 2.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_U_DET
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_U_1ST
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_U_OUT
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TEMP
        MODULE_LAB_M_MONITOR object. Reads module enclosure temperature in Celsius degrees.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_PARAMS_DET_U
        MODULE_LAB_M_PARAMS object. Describes value of voltage bias.
        Data Value
            UINT16. Variable range 0...256 corresponds to 0-1V.
    MODULE_LAB_M_PARAMS_DET_I
        MODULE_LAB_M_PARAMS object. Describes value of current bias compensation.
        Data Value
            UINT16. Variable range 0...256 corresponds to 0-10mA.
    MODULE_LAB_M_PARAMS_GAIN
        MODULE_LAB_M_PARAMS object. Responsible for setting gain in the second stage.
        Data Value
            UINT16.
    MODULE_LAB_M_PARAMS_OFFSET
        MODULE_LAB_M_PARAMS object. Responsible for setting offset value.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_PARAMS_VARACTOR
        MODULE_LAB_M_PARAMS object. Responsible for frequency compensation for the preamplifier first stage.
        Data Value
            UINT16.
    MODULE_LAB_M_PARAMS_TRANS
        MODULE_LAB_M_PARAMS object. Responsible for transimpedance of first stage preamplifier.
        Data Value
            See MODULE_LAB_M_PARAMS_TRANS_VALUES.
    MODULE_LAB_M_PARAMS_ACDC
        MODULE_LAB_M_PARAMS object. Responsible for the coupling mode.
        Data Value
            See MODULE_LAB_M_PARAMS_ACDC_VALUES.
    MODULE_LAB_M_PARAMS_BW
        MODULE_LAB_M_PARAMS object. Describes value of bandwidth.
        Data Value
            See MODULE_LAB_M_PARAMS_BW_VALUES.
    DEVICE_IDEN_TYPE
        DEVICE_IDEN object. Describes type of device.
        Data Value
            UINT16.
    DEVICE_IDEN_FIRM_VER
        DEVICE_IDEN object. Describes devices version of firmware.
        Data Value
            UINT16.
    DEVICE_IDEN_HARD_VER
        DEVICE_IDEN object. Describes devices version of hardware.
        Data Value
            UINT16.
    DEVICE_IDEN_NAME
        DEVICE_IDEN object. Describes device name.
        Data Value
            CSTR. See DEVICE_IDEN_NAME_SIZE.
    DEVICE_IDEN_SERIAL
        DEVICE_IDEN object. Describes device serial number.
        Data Value
            SERIAL_NUMBER.
    DEVICE_IDEN_PROD_DATE
        DEVICE_IDEN object. Describes date of device prodution.
        Data Value
            SERIAL_NUMBER.
    """
    # container types
    GET_PTCC_CONFIG = 1280
    GET_PTCC_MONITOR = 1312
    GET_PTCC_MOD_NO_MEM_IDEN = 1536
    GET_PTCC_MOD_NO_MEM_USER_SET = 1600
    GET_PTCC_MOD_NO_MEM_USER_MIN = 1632
    GET_PTCC_MOD_NO_MEM_USER_MAX = 1664
    GET_PTCC_MOD_NO_MEM_DEFAULT = 1568
    SET_PTCC_MOD_NO_MEM_USER_SET = 1616
    GET_MODULE_IDEN = 2048
    GET_MODULE_USER_SET = 2144
    GET_MODULE_USER_MIN = 2176
    GET_MODULE_USER_MAX = 2208
    GET_MODULE_DEFAULT = 2112
    SET_MODULE_USER_SET = 2160
    GET_MODULE_LAB_M_MONITOR = 2560
    GET_MODULE_LAB_M_USER_SET = 2720
    GET_MODULE_LAB_M_USER_MIN = 2752
    GET_MODULE_LAB_M_USER_MAX = 2784
    GET_MODULE_LAB_M_DEFAULT = 2688
    SET_MODULE_LAB_M_USER_SET = 2736
    PTCC_CONFIG = 6144
    PTCC_MONITOR = 7168
    MODULE_IDEN = 8192
    MODULE_BASIC_PARAMS = 9216
    MODULE_LAB_M_MONITOR = 11264
    MODULE_LAB_M_PARAMS = 12288
    GET_DEVICE_IDEN = 32
    DEVICE_IDEN = 256
    # other objects
    PTCC_CONFIG_VARIANT = 6163
    PTCC_CONFIG_NO_MEM_COMPATIBLE = 6187
    PTCC_MONITOR_SUP_ON = 7195
    PTCC_MONITOR_I_SUP_PLUS = 7204
    PTCC_MONITOR_I_SUP_MINUS = 7220
    PTCC_MONITOR_FAN_ON = 7243
    PTCC_MONITOR_I_FAN_PLUS = 7252
    PTCC_MONITOR_I_TEC = 7268
    PTCC_MONITOR_U_TEC = 7284
    PTCC_MONITOR_U_SUP_PLUS = 7300
    PTCC_MONITOR_U_SUP_MINUS = 7316
    PTCC_MONITOR_T_DET = 7334
    PTCC_MONITOR_T_INT = 7348
    PTCC_MONITOR_PWM = 7365
    PTCC_MONITOR_STATUS = 7379
    PTCC_MONITOR_MODULE_TYPE = 7395
    PTCC_MONITOR_TH_ADC = 7415
    MODULE_IDEN_TYPE = 8211
    MODULE_IDEN_FIRM_VER = 8229
    MODULE_IDEN_HARD_VER = 8245
    MODULE_IDEN_NAME = 8257
    MODULE_IDEN_SERIAL = 8282
    MODULE_IDEN_DET_NAME = 8289
    MODULE_IDEN_DET_SERIAL = 8314
    MODULE_IDEN_PROD_DATE = 8329
    MODULE_IDEN_TEC_TYPE = 8339
    MODULE_IDEN_TH_TYPE = 8355
    MODULE_IDEN_TEC_PARAM1 = 8376
    MODULE_IDEN_TEC_PARAM2 = 8392
    MODULE_IDEN_TEC_PARAM3 = 8408
    MODULE_IDEN_TEC_PARAM4 = 8424
    MODULE_IDEN_TH_PARAM1 = 8440
    MODULE_IDEN_TH_PARAM2 = 8456
    MODULE_IDEN_TH_PARAM3 = 8472
    MODULE_IDEN_TH_PARAM4 = 8488
    MODULE_IDEN_COOL_TIME = 8581
    MODULE_BASIC_PARAMS_SUP_CTRL = 9235
    MODULE_BASIC_PARAMS_U_SUP_PLUS = 9252
    MODULE_BASIC_PARAMS_U_SUP_MINUS = 9268
    MODULE_BASIC_PARAMS_FAN_CTRL = 9283
    MODULE_BASIC_PARAMS_TEC_CTRL = 9299
    MODULE_BASIC_PARAMS_PWM = 9317
    MODULE_BASIC_PARAMS_I_TEC_MAX = 9332
    MODULE_BASIC_PARAMS_T_DET = 9351
    MODULE_LAB_M_MONITOR_SUP_PLUS = 11284
    MODULE_LAB_M_MONITOR_SUP_MINUS = 11300
    MODULE_LAB_M_MONITOR_FAN_PLUS = 11316
    MODULE_LAB_M_MONITOR_TEC_PLUS = 11332
    MODULE_LAB_M_MONITOR_TEC_MINUS = 11348
    MODULE_LAB_M_MONITOR_TH1 = 11364
    MODULE_LAB_M_MONITOR_TH2 = 11380
    MODULE_LAB_M_MONITOR_U_DET = 11396
    MODULE_LAB_M_MONITOR_U_1ST = 11412
    MODULE_LAB_M_MONITOR_U_OUT = 11428
    MODULE_LAB_M_MONITOR_TEMP = 11444
    MODULE_LAB_M_PARAMS_DET_U = 12309
    MODULE_LAB_M_PARAMS_DET_I = 12325
    MODULE_LAB_M_PARAMS_GAIN = 12341
    MODULE_LAB_M_PARAMS_OFFSET = 12357
    MODULE_LAB_M_PARAMS_VARACTOR = 12373
    MODULE_LAB_M_PARAMS_TRANS = 12387
    MODULE_LAB_M_PARAMS_ACDC = 12403
    MODULE_LAB_M_PARAMS_BW = 12419
    DEVICE_IDEN_TYPE = 277
    DEVICE_IDEN_FIRM_VER = 293
    DEVICE_IDEN_HARD_VER = 309
    DEVICE_IDEN_NAME = 321
    DEVICE_IDEN_SERIAL = 346
    DEVICE_IDEN_PROD_DATE = 361


class CallbackPtccObjectID(Enum):
    """
    Enum for all possible PtccObject ids which can be used for setting callbacks.

    Attributes
    ----------
    PTCC_CONFIG
        Container. Stores PTCC_CONFIG objects.
    PTCC_MONITOR
        Container. Stores PTCC_MONITOR objects.
    MODULE_IDEN
        Container. Stores MODULE_IDEN objects.
    MODULE_BASIC_PARAMS
        Container. Stores MODULE_BASIC_PARAMS objects.
    MODULE_LAB_M_MONITOR
        Container. Stores MODULE_LAB_M_MONITOR objects.
    MODULE_LAB_M_PARAMS
        Container. Stores MODULE_LAB_M_PARAMS objects.
    GET_DEVICE_IDEN
        Container. Command is used to read configuration data.
    DEVICE_IDEN
        Container. Stores DEVICE_IDEN objects.
    PTCC_CONFIG_VARIANT
        PTCC_CONFIG object. Determines the version of PTTC device.
        Data Value:
            See PTCC_CONFIG_VARIANT_VALUES.
    PTCC_CONFIG_NO_MEM_COMPATIBLE
        PTCC_CONFIG object. Responsible for availability of EEPROM memory.
        Data Value:
            True
                EEPROM memory available.
            False
                EEPROM memory unavailable.
    PTCC_MONITOR_SUP_ON
        SMARTTEC_MONITOR object. Checks operation state of power supply lines.
        Data Value:
            True
                Power supply lines are active.
            False
                Power supply lines are inactive.
    PTCC_MONITOR_I_SUP_PLUS
        SMARTTEC_MONITOR object. Reads current value of positive supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_I_SUP_MINUS
        SMARTTEC_MONITOR object. Reads current value of negative supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_FAN_ON
        SMARTTEC_MONITOR object. Checks operation state of fan output.
        Data Value:
            True;
                Enable fan output.
            False
                Disable fan output.
    PTCC_MONITOR_I_FAN_PLUS
        SMARTTEC_MONITOR object. Reads output current value of fan output.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_I_TEC
        SMARTTEC_MONITOR object. Reads current value of TEC output.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_U_TEC
        SMARTTEC_MONITOR object. Reads output voltage value of TEC.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_U_SUP_PLUS
        SMARTTEC_MONITOR object. Reads output voltage value of positive supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_U_SUP_MINUS
        SMARTTEC_MONITOR object. Reads output voltage value of negative supply line.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_T_DET
        SMARTTEC_MONITOR object. Reads detector temperature in Kelvins.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_T_INT
        SMARTTEC_MONITOR object. Reads detector temperature in Celsius degrees.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_PWM
        SMARTTEC_MONITOR object. Reads PWM settings of TEC controller.
        Data Value:
            Available PtccUnits.
    PTCC_MONITOR_STATUS
        SMARTTEC_MONITOR object.
        Data Value:
            See status_messages and error_messages.
            Status code:
                 - 0 – detector is cooled, temperature is equal(-/+ 1 K) to temperature defined by user.
                 - 1 – during the cooling proces.
                 - 2 - the cooling is deactivated. Check PTTC settings.
                 - 3 - cooler is working with fixed current.
            Error code:
                 - 128 - “detector overheat” - the set temperature could not be reached during 120 second.
                 - 129 - Measured current value is higher then maximum current value. PTTC power is off.
                 - 130 - TEC circuit open connection.
                 - 131 - TEC circuit is closed connection.
                 - 132 - thermistor circuit open connection.
                 - 133 - thermistor circuit closed connection.
                 - 134 - the temperature inside PTCC is higher than limit.
                 - 135 - the connected module without memory is not compatible or no module is connected.
                 - 136 - memory was detected but there are some communication problem.
                 - 137 – PIP data fault, there are some communication problem.
                 - 138 - Communication with memory data fault, there are some communication problem.
                 - 139 - PTTC memory fault.
                 - 140 - Lab M is incompatible.
                 - 141 - Memory is incompatible. When the error status code appears the re-turn of the PTTC devices might be required.
    PTCC_MONITOR_MODULE_TYPE
        SMARTTEC_MONITOR object. Reads type of module.
        Data Value
            See PTCC_MONITOR_MODULE_TYPE_VALUES.
    PTCC_MONITOR_TH_ADC
        SMARTTEC_MONITOR object. Reads voltage value of thermistor.
        Data Value
            Available PtccUnits.
    MODULE_IDEN_TYPE
        MODULE_IDEN object. Describes type of memory.
        Data Value
            See MODULE_IDEN_TYPE_VALUES.
    MODULE_IDEN_FIRM_VER
        MODULE_IDEN object. Describes version of firmware.
        Data Value
            UINT16.
    MODULE_IDEN_HARD_VER
        MODULE_IDEN object. Describes version of hardware.
        Data Value
            UINT16.
    MODULE_IDEN_NAME
        MODULE_IDEN object. Describes module name.
        Data Value
            CSTR. See MODULE_IDEN_NAME_SIZE.
    MODULE_IDEN_SERIAL
        MODULE_IDEN object. Describes module serial number.
        Data Value
            SERIAL_NUMBER.
    MODULE_IDEN_DET_NAME
        MODULE_IDEN object. Describes detector name.
        Data Value
            CSTR. See MODULE_IDEN_DET_NAME_SIZE.
    MODULE_IDEN_DET_SERIAL
        MODULE_IDEN object. Describes detector serial number.
        Data Value
            SERIAL_NUMBER.
    MODULE_IDEN_PROD_DATE
        MODULE_IDEN object. Describes date of manufacture of the module.
        Data Value
            DATE_TIME.
    MODULE_IDEN_TEC_TYPE
        MODULE_IDEN object.
        Data Value
            See MODULE_IDEN_TEC_TYPE_VALUES.
    MODULE_IDEN_TH_TYPE
        MODULE_IDEN object. Describes thermistor type.
        Data Value
            UINT8.
    MODULE_IDEN_TEC_PARAM1
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TEC_PARAM2
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TEC_PARAM3
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TEC_PARAM4
        MODULE_IDEN object. Describes TEC parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM1
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM2
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM3
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_TH_PARAM4
        MODULE_IDEN object. Describes thermistor parameters.
        Data Value
            FLOAT.
    MODULE_IDEN_COOL_TIME
        MODULE_IDEN object. Responsible for setting maximum time of cooling module.
        If the module does not reach desired temperature it will be turned off.
        Data Value
            UINT16.
    MODULE_BASIC_PARAMS_SUP_CTRL
        MODULE_BASIC_PARAMS object. Describes operating modes of power supply lines.
        Data Value
            See MODULE_BASIC_PARAMS_SUP_CTRL_VALUES.
    MODULE_BASIC_PARAMS_U_SUP_PLUS
        MODULE_BASIC_PARAMS object. Responsible for setting output voltage value of positive power line.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_U_SUP_MINUS
        MODULE_BASIC_PARAMS object. Responsible for setting output voltage value of negative power line.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_FAN_CTRL
        MODULE_BASIC_PARAMS object. Describes operation state of fan control.
        Data Value
            See MODULE_BASIC_PARAMS_FAN_CTRL_VALUES.
    MODULE_BASIC_PARAMS_TEC_CTRL
        MODULE_BASIC_PARAMS object. Describes operating modes of TEC cooler.
        Data Value
            See MODULE_BASIC_PARAMS_TEC_CTRL_VALUES.
    MODULE_BASIC_PARAMS_PWM
        MODULE_BASIC_PARAMS object. Describes PWM settings of TEC.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_I_TEC_MAX
        MODULE_BASIC_PARAMS object. Describes maximum current for TEC output.
        Data Value
            Available PtccUnits.
    MODULE_BASIC_PARAMS_T_DET
        MODULE_BASIC_PARAMS object. Describes detector temperature in Kelvins.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_SUP_PLUS
        MODULE_LAB_M_MONITOR object. Reads voltage value of positive power line.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_SUP_MINUS
        MODULE_LAB_M_MONITOR object. Reads voltage value of negative power line.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_FAN_PLUS
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TEC_PLUS
        MODULE_LAB_M_MONITOR object. Reads maximum current for TEC positive output.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TEC_MINUS
        MODULE_LAB_M_MONITOR object. Reads maximum current for TEC negative output.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TH1
        MODULE_LAB_M_MONITOR object. Reads voltage value of thermistor pin 1.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TH2
        MODULE_LAB_M_MONITOR object. Reads voltage value of thermistor pin 2.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_U_DET
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_U_1ST
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_U_OUT
        MODULE_LAB_M_MONITOR object.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_MONITOR_TEMP
        MODULE_LAB_M_MONITOR object. Reads module enclosure temperature in Celsius degrees.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_PARAMS_DET_U
        MODULE_LAB_M_PARAMS object. Describes value of voltage bias.
        Data Value
            UINT16. Variable range 0...256 corresponds to 0-1V.
    MODULE_LAB_M_PARAMS_DET_I
        MODULE_LAB_M_PARAMS object. Describes value of current bias compensation.
        Data Value
            UINT16. Variable range 0...256 corresponds to 0-10mA.
    MODULE_LAB_M_PARAMS_GAIN
        MODULE_LAB_M_PARAMS object. Responsible for setting gain in the second stage.
        Data Value
            UINT16.
    MODULE_LAB_M_PARAMS_OFFSET
        MODULE_LAB_M_PARAMS object. Responsible for setting offset value.
        Data Value
            Available PtccUnits.
    MODULE_LAB_M_PARAMS_VARACTOR
        MODULE_LAB_M_PARAMS object. Responsible for frequency compensation for the preamplifier first stage.
        Data Value
            UINT16.
    MODULE_LAB_M_PARAMS_TRANS
        MODULE_LAB_M_PARAMS object. Responsible for transimpedance of first stage preamplifier.
        Data Value
            See MODULE_LAB_M_PARAMS_TRANS_VALUES.
    MODULE_LAB_M_PARAMS_ACDC
        MODULE_LAB_M_PARAMS object. Responsible for the coupling mode.
        Data Value
            See MODULE_LAB_M_PARAMS_ACDC_VALUES.
    MODULE_LAB_M_PARAMS_BW
        MODULE_LAB_M_PARAMS object. Describes value of bandwidth.
        Data Value
            See MODULE_LAB_M_PARAMS_BW_VALUES.
    DEVICE_IDEN_TYPE
        DEVICE_IDEN object. Describes type of device.
        Data Value
            UINT16.
    DEVICE_IDEN_FIRM_VER
        DEVICE_IDEN object. Describes devices version of firmware.
        Data Value
            UINT16.
    DEVICE_IDEN_HARD_VER
        DEVICE_IDEN object. Describes devices version of hardware.
        Data Value
            UINT16.
    DEVICE_IDEN_NAME
        DEVICE_IDEN object. Describes device name.
        Data Value
            CSTR. See DEVICE_IDEN_NAME_SIZE.
    DEVICE_IDEN_SERIAL
        DEVICE_IDEN object. Describes device serial number.
        Data Value
            SERIAL_NUMBER.
    DEVICE_IDEN_PROD_DATE
        DEVICE_IDEN object. Describes date of device prodution.
        Data Value
            SERIAL_NUMBER.
    """
    # container types
    PTCC_CONFIG = PtccObjectID.PTCC_CONFIG.value
    PTCC_MONITOR = PtccObjectID.PTCC_MONITOR.value
    MODULE_IDEN = PtccObjectID.MODULE_IDEN.value
    MODULE_BASIC_PARAMS = PtccObjectID.MODULE_BASIC_PARAMS.value
    MODULE_LAB_M_MONITOR = PtccObjectID.MODULE_LAB_M_MONITOR.value
    MODULE_LAB_M_PARAMS = PtccObjectID.MODULE_LAB_M_PARAMS.value
    GET_DEVICE_IDEN = PtccObjectID.GET_DEVICE_IDEN.value
    DEVICE_IDEN = PtccObjectID.DEVICE_IDEN.value
    # other objects
    PTCC_CONFIG_VARIANT = PtccObjectID.PTCC_CONFIG_VARIANT.value
    PTCC_CONFIG_NO_MEM_COMPATIBLE = PtccObjectID.PTCC_CONFIG_NO_MEM_COMPATIBLE.value
    PTCC_MONITOR_SUP_ON = PtccObjectID.PTCC_MONITOR_SUP_ON.value
    PTCC_MONITOR_I_SUP_PLUS = PtccObjectID.PTCC_MONITOR_I_SUP_PLUS.value
    PTCC_MONITOR_I_SUP_MINUS = PtccObjectID.PTCC_MONITOR_I_SUP_MINUS.value
    PTCC_MONITOR_FAN_ON = PtccObjectID.PTCC_MONITOR_FAN_ON.value
    PTCC_MONITOR_I_FAN_PLUS = PtccObjectID.PTCC_MONITOR_I_FAN_PLUS.value
    PTCC_MONITOR_I_TEC = PtccObjectID.PTCC_MONITOR_I_TEC.value
    PTCC_MONITOR_U_TEC = PtccObjectID.PTCC_MONITOR_U_TEC.value
    PTCC_MONITOR_U_SUP_PLUS = PtccObjectID.PTCC_MONITOR_U_SUP_PLUS.value
    PTCC_MONITOR_U_SUP_MINUS = PtccObjectID.PTCC_MONITOR_U_SUP_MINUS.value
    PTCC_MONITOR_T_DET = PtccObjectID.PTCC_MONITOR_T_DET.value
    PTCC_MONITOR_T_INT = PtccObjectID.PTCC_MONITOR_T_INT.value
    PTCC_MONITOR_PWM = PtccObjectID.PTCC_MONITOR_PWM.value
    PTCC_MONITOR_STATUS = PtccObjectID.PTCC_MONITOR_STATUS.value
    PTCC_MONITOR_MODULE_TYPE = PtccObjectID.PTCC_MONITOR_MODULE_TYPE.value
    PTCC_MONITOR_TH_ADC = PtccObjectID.PTCC_MONITOR_TH_ADC.value
    MODULE_IDEN_TYPE = PtccObjectID.MODULE_IDEN_TYPE.value
    MODULE_IDEN_FIRM_VER = PtccObjectID.MODULE_IDEN_FIRM_VER.value
    MODULE_IDEN_HARD_VER = PtccObjectID.MODULE_IDEN_HARD_VER.value
    MODULE_IDEN_NAME = PtccObjectID.MODULE_IDEN_NAME.value
    MODULE_IDEN_SERIAL = PtccObjectID.MODULE_IDEN_SERIAL.value
    MODULE_IDEN_DET_NAME = PtccObjectID.MODULE_IDEN_DET_NAME.value
    MODULE_IDEN_DET_SERIAL = PtccObjectID.MODULE_IDEN_DET_SERIAL.value
    MODULE_IDEN_PROD_DATE = PtccObjectID.MODULE_IDEN_PROD_DATE.value
    MODULE_IDEN_TEC_TYPE = PtccObjectID.MODULE_IDEN_TEC_TYPE.value
    MODULE_IDEN_TH_TYPE = PtccObjectID.MODULE_IDEN_TH_TYPE.value
    MODULE_IDEN_TEC_PARAM1 = PtccObjectID.MODULE_IDEN_TEC_PARAM1.value
    MODULE_IDEN_TEC_PARAM2 = PtccObjectID.MODULE_IDEN_TEC_PARAM2.value
    MODULE_IDEN_TEC_PARAM3 = PtccObjectID.MODULE_IDEN_TEC_PARAM3.value
    MODULE_IDEN_TEC_PARAM4 = PtccObjectID.MODULE_IDEN_TEC_PARAM4.value
    MODULE_IDEN_TH_PARAM1 = PtccObjectID.MODULE_IDEN_TH_PARAM1.value
    MODULE_IDEN_TH_PARAM2 = PtccObjectID.MODULE_IDEN_TH_PARAM2.value
    MODULE_IDEN_TH_PARAM3 = PtccObjectID.MODULE_IDEN_TH_PARAM3.value
    MODULE_IDEN_TH_PARAM4 = PtccObjectID.MODULE_IDEN_TH_PARAM4.value
    MODULE_IDEN_COOL_TIME = PtccObjectID.MODULE_IDEN_COOL_TIME.value
    MODULE_BASIC_PARAMS_SUP_CTRL = PtccObjectID.MODULE_BASIC_PARAMS_SUP_CTRL.value
    MODULE_BASIC_PARAMS_U_SUP_PLUS = PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS.value
    MODULE_BASIC_PARAMS_U_SUP_MINUS = PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS.value
    MODULE_BASIC_PARAMS_FAN_CTRL = PtccObjectID.MODULE_BASIC_PARAMS_FAN_CTRL.value
    MODULE_BASIC_PARAMS_TEC_CTRL = PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL.value
    MODULE_BASIC_PARAMS_PWM = PtccObjectID.MODULE_BASIC_PARAMS_PWM.value
    MODULE_BASIC_PARAMS_I_TEC_MAX = PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX.value
    MODULE_BASIC_PARAMS_T_DET = PtccObjectID.MODULE_BASIC_PARAMS_T_DET.value
    MODULE_LAB_M_MONITOR_SUP_PLUS = PtccObjectID.MODULE_LAB_M_MONITOR_SUP_PLUS.value
    MODULE_LAB_M_MONITOR_SUP_MINUS = PtccObjectID.MODULE_LAB_M_MONITOR_SUP_MINUS.value
    MODULE_LAB_M_MONITOR_FAN_PLUS = PtccObjectID.MODULE_LAB_M_MONITOR_FAN_PLUS.value
    MODULE_LAB_M_MONITOR_TEC_PLUS = PtccObjectID.MODULE_LAB_M_MONITOR_TEC_PLUS.value
    MODULE_LAB_M_MONITOR_TEC_MINUS = PtccObjectID.MODULE_LAB_M_MONITOR_TEC_MINUS.value
    MODULE_LAB_M_MONITOR_TH1 = PtccObjectID.MODULE_LAB_M_MONITOR_TH1.value
    MODULE_LAB_M_MONITOR_TH2 = PtccObjectID.MODULE_LAB_M_MONITOR_TH2.value
    MODULE_LAB_M_MONITOR_U_DET = PtccObjectID.MODULE_LAB_M_MONITOR_U_DET.value
    MODULE_LAB_M_MONITOR_U_1ST = PtccObjectID.MODULE_LAB_M_MONITOR_U_1ST.value
    MODULE_LAB_M_MONITOR_U_OUT = PtccObjectID.MODULE_LAB_M_MONITOR_U_OUT.value
    MODULE_LAB_M_MONITOR_TEMP = PtccObjectID.MODULE_LAB_M_MONITOR_TEMP.value
    MODULE_LAB_M_PARAMS_DET_U = PtccObjectID.MODULE_LAB_M_PARAMS_DET_U.value
    MODULE_LAB_M_PARAMS_DET_I = PtccObjectID.MODULE_LAB_M_PARAMS_DET_I.value
    MODULE_LAB_M_PARAMS_GAIN = PtccObjectID.MODULE_LAB_M_PARAMS_GAIN.value
    MODULE_LAB_M_PARAMS_OFFSET = PtccObjectID.MODULE_LAB_M_PARAMS_OFFSET.value
    MODULE_LAB_M_PARAMS_VARACTOR = PtccObjectID.MODULE_LAB_M_PARAMS_VARACTOR.value
    MODULE_LAB_M_PARAMS_TRANS = PtccObjectID.MODULE_LAB_M_PARAMS_TRANS.value
    MODULE_LAB_M_PARAMS_ACDC = PtccObjectID.MODULE_LAB_M_PARAMS_ACDC.value
    MODULE_LAB_M_PARAMS_BW = PtccObjectID.MODULE_LAB_M_PARAMS_BW.value
    DEVICE_IDEN_TYPE = PtccObjectID.DEVICE_IDEN_TYPE.value
    DEVICE_IDEN_FIRM_VER = PtccObjectID.DEVICE_IDEN_FIRM_VER.value
    DEVICE_IDEN_HARD_VER = PtccObjectID.DEVICE_IDEN_HARD_VER.value
    DEVICE_IDEN_NAME = PtccObjectID.DEVICE_IDEN_NAME.value
    DEVICE_IDEN_SERIAL = PtccObjectID.DEVICE_IDEN_SERIAL.value
    DEVICE_IDEN_PROD_DATE = PtccObjectID.DEVICE_IDEN_PROD_DATE.value


ALL_TYPE_COMMANDS = {
    PtccObjectID.GET_DEVICE_IDEN,
    PtccObjectID.GET_PTCC_CONFIG
}

NO_MEM_TYPE_COMMANDS = {PtccObjectID.GET_PTCC_MONITOR,
                        PtccObjectID.GET_PTCC_MOD_NO_MEM_IDEN,
                        PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_SET,
                        PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_MIN,
                        PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_MAX,
                        PtccObjectID.GET_PTCC_MOD_NO_MEM_DEFAULT,
                        PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
                        }

MEM_TYPE_COMMANDS = {PtccObjectID.GET_MODULE_IDEN,
                     PtccObjectID.GET_MODULE_USER_SET,
                     PtccObjectID.GET_MODULE_USER_MIN,
                     PtccObjectID.GET_MODULE_USER_MAX,
                     PtccObjectID.GET_MODULE_DEFAULT,
                     PtccObjectID.SET_MODULE_USER_SET,
                     }

LAB_M_TYPE_COMMANDS = {PtccObjectID.GET_MODULE_IDEN,
                       PtccObjectID.GET_MODULE_USER_SET,
                       PtccObjectID.GET_MODULE_USER_MIN,
                       PtccObjectID.GET_MODULE_USER_MAX,
                       PtccObjectID.GET_MODULE_DEFAULT,
                       PtccObjectID.SET_MODULE_USER_SET,

                       PtccObjectID.GET_MODULE_LAB_M_MONITOR,
                       PtccObjectID.GET_MODULE_LAB_M_USER_SET,
                       PtccObjectID.GET_MODULE_LAB_M_USER_MIN,
                       PtccObjectID.GET_MODULE_LAB_M_USER_MAX,
                       PtccObjectID.GET_MODULE_LAB_M_DEFAULT,
                       PtccObjectID.SET_MODULE_LAB_M_USER_SET,
                       }

CONTAINER_IDS = {
    PtccObjectID.GET_PTCC_CONFIG,
    PtccObjectID.GET_PTCC_MONITOR,
    PtccObjectID.GET_PTCC_MOD_NO_MEM_IDEN,
    PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_SET,
    PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_MIN,
    PtccObjectID.GET_PTCC_MOD_NO_MEM_USER_MAX,
    PtccObjectID.GET_PTCC_MOD_NO_MEM_DEFAULT,
    PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET,
    PtccObjectID.GET_MODULE_IDEN,
    PtccObjectID.GET_MODULE_USER_SET,
    PtccObjectID.GET_MODULE_USER_MIN,
    PtccObjectID.GET_MODULE_USER_MAX,
    PtccObjectID.GET_MODULE_DEFAULT,
    PtccObjectID.SET_MODULE_USER_SET,
    PtccObjectID.GET_MODULE_LAB_M_MONITOR,
    PtccObjectID.GET_MODULE_LAB_M_USER_SET,
    PtccObjectID.GET_MODULE_LAB_M_USER_MIN,
    PtccObjectID.GET_MODULE_LAB_M_USER_MAX,
    PtccObjectID.GET_MODULE_LAB_M_DEFAULT,
    PtccObjectID.SET_MODULE_LAB_M_USER_SET,
    PtccObjectID.PTCC_CONFIG,
    PtccObjectID.PTCC_MONITOR,
    PtccObjectID.MODULE_IDEN,
    PtccObjectID.MODULE_BASIC_PARAMS,
    PtccObjectID.MODULE_LAB_M_MONITOR,
    PtccObjectID.MODULE_LAB_M_PARAMS,
    PtccObjectID.GET_DEVICE_IDEN,
    PtccObjectID.DEVICE_IDEN,
}

SET_CONTAINER_IDS = {
    PtccObjectID.SET_PTCC_MOD_NO_MEM_USER_SET: PtccObjectID.MODULE_BASIC_PARAMS,
    PtccObjectID.SET_MODULE_USER_SET: PtccObjectID.MODULE_BASIC_PARAMS,
    PtccObjectID.SET_MODULE_LAB_M_USER_SET: PtccObjectID.MODULE_LAB_M_PARAMS
}


class PtccUnits:
    """
    SI units used in TecObjects.
    """
    PTCC_MONITOR_I_SUP_PLUS_UNIT = "A"
    PTCC_MONITOR_I_SUP_MINUS_UNIT = "A"
    PTCC_MONITOR_I_FAN_PLUS_UNIT = "A"
    PTCC_MONITOR_I_TEC_UNIT = "A"
    PTCC_MONITOR_U_TEC_UNIT = "V"
    PTCC_MONITOR_U_SUP_PLUS_UNIT = "V"
    PTCC_MONITOR_U_SUP_MINUS_UNIT = "V"
    PTCC_MONITOR_T_DET_UNIT = "K"
    PTCC_MONITOR_T_INT_UNIT = "C"
    MONITOR_TH_ADC = "mV"
    MODULE_BASIC_PARAMS_U_SUP_PLUS_UNIT = "V"
    MODULE_BASIC_PARAMS_U_SUP_MINUS_UNIT = "V"
    MODULE_BASIC_PARAMS_I_TEC_MAX_UNIT = "A"
    MODULE_BASIC_PARAMS_T_DET_UNIT = "K"
    MODULE_LAB_M_MONITOR_SUP_PLUS_UNIT = "V"
    MODULE_LAB_M_MONITOR_SUP_MINUS_UNIT = "V"
    MODULE_LAB_M_MONITOR_FAN_PLUS_UNIT = "V"
    MODULE_LAB_M_MONITOR_TEC_PLUS_UNIT = "A"
    MODULE_LAB_M_MONITOR_TEC_MINUS_UNIT = "A"
    MODULE_LAB_M_MONITOR_TH1_UNIT = "V"
    MODULE_LAB_M_MONITOR_TH2_UNIT = "V"
    MODULE_LAB_M_MONITOR_U_DET_UNIT = "V"
    MODULE_LAB_M_MONITOR_U_1ST_UNIT = "V"
    MODULE_LAB_M_MONITOR_U_OUT_UNIT = "V"
    MODULE_LAB_M_MONITOR_TEMP_UNIT = "C"


LOOKUP_UNITS = {PtccObjectID.PTCC_MONITOR_I_SUP_PLUS: PtccUnits.PTCC_MONITOR_I_SUP_PLUS_UNIT,
                PtccObjectID.PTCC_MONITOR_I_SUP_MINUS: PtccUnits.PTCC_MONITOR_I_SUP_MINUS_UNIT,
                PtccObjectID.PTCC_MONITOR_I_FAN_PLUS: PtccUnits.PTCC_MONITOR_I_FAN_PLUS_UNIT,
                PtccObjectID.PTCC_MONITOR_I_TEC: PtccUnits.PTCC_MONITOR_I_TEC_UNIT,
                PtccObjectID.PTCC_MONITOR_U_TEC: PtccUnits.PTCC_MONITOR_U_TEC_UNIT,
                PtccObjectID.PTCC_MONITOR_U_SUP_PLUS: PtccUnits.PTCC_MONITOR_U_SUP_PLUS_UNIT,
                PtccObjectID.PTCC_MONITOR_U_SUP_MINUS: PtccUnits.PTCC_MONITOR_U_SUP_MINUS_UNIT,
                PtccObjectID.PTCC_MONITOR_T_DET: PtccUnits.PTCC_MONITOR_T_DET_UNIT,
                PtccObjectID.PTCC_MONITOR_T_INT: PtccUnits.PTCC_MONITOR_T_INT_UNIT,
                PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS: PtccUnits.MODULE_BASIC_PARAMS_U_SUP_PLUS_UNIT,
                PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS: PtccUnits.MODULE_BASIC_PARAMS_U_SUP_MINUS_UNIT,
                PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX: PtccUnits.MODULE_BASIC_PARAMS_I_TEC_MAX_UNIT,
                PtccObjectID.MODULE_BASIC_PARAMS_T_DET: PtccUnits.MODULE_BASIC_PARAMS_T_DET_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_SUP_PLUS: PtccUnits.MODULE_LAB_M_MONITOR_SUP_PLUS_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_SUP_MINUS: PtccUnits.MODULE_LAB_M_MONITOR_SUP_MINUS_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_FAN_PLUS: PtccUnits.MODULE_LAB_M_MONITOR_FAN_PLUS_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_TEC_PLUS: PtccUnits.MODULE_LAB_M_MONITOR_TEC_PLUS_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_TEC_MINUS: PtccUnits.MODULE_LAB_M_MONITOR_TEC_MINUS_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_TH1: PtccUnits.MODULE_LAB_M_MONITOR_TH1_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_TH2: PtccUnits.MODULE_LAB_M_MONITOR_TH2_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_U_DET: PtccUnits.MODULE_LAB_M_MONITOR_U_DET_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_U_1ST: PtccUnits.MODULE_LAB_M_MONITOR_U_1ST_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_U_OUT: PtccUnits.MODULE_LAB_M_MONITOR_U_OUT_UNIT,
                PtccObjectID.MODULE_LAB_M_MONITOR_TEMP: PtccUnits.MODULE_LAB_M_MONITOR_TEMP_UNIT,
                }


class PtccMinMax:
    """
    Minimum and maximum values for data in PtccObjects.


    Use MIN_VALUES and MAX_VALUES for mapping.
    """
    PTCC_CONFIG_VARIANT_MIN = 0
    PTCC_CONFIG_VARIANT_MAX = 2
    PTCC_MONITOR_I_SUP_PLUS_MIN = 0
    PTCC_MONITOR_I_SUP_PLUS_MAX = 20475
    PTCC_MONITOR_I_SUP_MINUS_MIN = -20475
    PTCC_MONITOR_I_SUP_MINUS_MAX = 0
    PTCC_MONITOR_I_FAN_PLUS_MIN = 0
    PTCC_MONITOR_I_FAN_PLUS_MAX = 4095
    PTCC_MONITOR_I_TEC_MIN = 0
    PTCC_MONITOR_I_TEC_MAX = 20475
    PTCC_MONITOR_U_TEC_MIN = 0
    PTCC_MONITOR_U_TEC_MAX = 20475
    PTCC_MONITOR_U_SUP_PLUS_MIN = 0
    PTCC_MONITOR_U_SUP_PLUS_MAX = 20475
    PTCC_MONITOR_U_SUP_MINUS_MIN = -20475
    PTCC_MONITOR_U_SUP_MINUS_MAX = 0
    PTCC_MONITOR_T_DET_MIN = 0
    PTCC_MONITOR_T_DET_MAX = 400000
    PTCC_MONITOR_T_INT_MIN = 0
    PTCC_MONITOR_T_INT_MAX = 1500
    PTCC_MONITOR_PWM_MIN = 0
    PTCC_MONITOR_PWM_MAX = 65535
    PTCC_MONITOR_MODULE_TYPE_MIN = 0
    PTCC_MONITOR_MODULE_TYPE_MAX = 3
    MODULE_IDEN_TYPE_MIN = 0
    MODULE_IDEN_TYPE_MAX = 3
    MODULE_BASIC_PARAMS_SUP_CTRL_MIN = 0
    MODULE_BASIC_PARAMS_SUP_CTRL_MAX = 2
    MODULE_BASIC_PARAMS_U_SUP_PLUS_MIN = 3000
    MODULE_BASIC_PARAMS_U_SUP_PLUS_MAX = 15000
    MODULE_BASIC_PARAMS_U_SUP_MINUS_MIN = -15000
    MODULE_BASIC_PARAMS_U_SUP_MINUS_MAX = -3000
    MODULE_BASIC_PARAMS_FAN_CTRL_MIN = 0
    MODULE_BASIC_PARAMS_FAN_CTRL_MAX = 2
    MODULE_BASIC_PARAMS_TEC_CTRL_MIN = 0
    MODULE_BASIC_PARAMS_TEC_CTRL_MAX = 2
    MODULE_BASIC_PARAMS_PWM_MIN = 0
    MODULE_BASIC_PARAMS_PWM_MAX = 65535
    MODULE_BASIC_PARAMS_I_TEC_MAX_MIN = 0
    MODULE_BASIC_PARAMS_I_TEC_MAX_MAX = 20475
    MODULE_BASIC_PARAMS_T_DET_MIN = 100000
    MODULE_BASIC_PARAMS_T_DET_MAX = 400000
    MODULE_USER_SET_BANK_INDEX_MIN = 0
    MODULE_USER_SET_BANK_INDEX_MAX = 3
    MODULE_LAB_M_MONITOR_SUP_PLUS_MIN = 0
    MODULE_LAB_M_MONITOR_SUP_PLUS_MAX = 20475
    MODULE_LAB_M_MONITOR_SUP_MINUS_MIN = -20480
    MODULE_LAB_M_MONITOR_SUP_MINUS_MAX = 20470
    MODULE_LAB_M_MONITOR_FAN_PLUS_MIN = 0
    MODULE_LAB_M_MONITOR_FAN_PLUS_MAX = 20475
    MODULE_LAB_M_MONITOR_TEC_PLUS_MIN = -20480
    MODULE_LAB_M_MONITOR_TEC_PLUS_MAX = 20470
    MODULE_LAB_M_MONITOR_TEC_MINUS_MIN = -20480
    MODULE_LAB_M_MONITOR_TEC_MINUS_MAX = 20470
    MODULE_LAB_M_MONITOR_TH1_MIN = -2048
    MODULE_LAB_M_MONITOR_TH1_MAX = 2047
    MODULE_LAB_M_MONITOR_TH2_MIN = 0
    MODULE_LAB_M_MONITOR_TH2_MAX = 2047
    MODULE_LAB_M_MONITOR_U_DET_MIN = -2048
    MODULE_LAB_M_MONITOR_U_DET_MAX = 2047
    MODULE_LAB_M_MONITOR_U_1ST_MIN = -4096
    MODULE_LAB_M_MONITOR_U_1ST_MAX = 4094
    MODULE_LAB_M_MONITOR_U_OUT_MIN = -10240
    MODULE_LAB_M_MONITOR_U_OUT_MAX = 10235
    MODULE_LAB_M_MONITOR_TEMP_MIN = 0
    MODULE_LAB_M_MONITOR_TEMP_MAX = 1000
    MODULE_LAB_M_PARAMS_DET_U_MIN = 0
    MODULE_LAB_M_PARAMS_DET_U_MAX = 256
    MODULE_LAB_M_PARAMS_DET_I_MIN = 0
    MODULE_LAB_M_PARAMS_DET_I_MAX = 256
    MODULE_LAB_M_PARAMS_GAIN_MIN = 0
    MODULE_LAB_M_PARAMS_GAIN_MAX = 256
    MODULE_LAB_M_PARAMS_OFFSET_MIN = 0
    MODULE_LAB_M_PARAMS_OFFSET_MAX = 256
    MODULE_LAB_M_PARAMS_VARACTOR_MIN = 0
    MODULE_LAB_M_PARAMS_VARACTOR_MAX = 4095
    MODULE_LAB_M_PARAMS_TRANS_MIN = 0
    MODULE_LAB_M_PARAMS_TRANS_MAX = 1
    MODULE_LAB_M_PARAMS_ACDC_MIN = 0
    MODULE_LAB_M_PARAMS_ACDC_MAX = 1
    MODULE_LAB_M_PARAMS_BW_MIN = 0
    MODULE_LAB_M_PARAMS_BW_MAX = 2


MIN_VALUES = {PtccObjectID.PTCC_CONFIG_VARIANT: PtccMinMax.PTCC_CONFIG_VARIANT_MIN,
              PtccObjectID.PTCC_MONITOR_I_SUP_PLUS: PtccMinMax.PTCC_MONITOR_I_SUP_PLUS_MIN,
              PtccObjectID.PTCC_MONITOR_I_SUP_MINUS: PtccMinMax.PTCC_MONITOR_I_SUP_MINUS_MIN,
              PtccObjectID.PTCC_MONITOR_I_FAN_PLUS: PtccMinMax.PTCC_MONITOR_I_FAN_PLUS_MIN,
              PtccObjectID.PTCC_MONITOR_I_TEC: PtccMinMax.PTCC_MONITOR_I_TEC_MIN,
              PtccObjectID.PTCC_MONITOR_U_TEC: PtccMinMax.PTCC_MONITOR_U_TEC_MIN,
              PtccObjectID.PTCC_MONITOR_U_SUP_PLUS: PtccMinMax.PTCC_MONITOR_U_SUP_PLUS_MIN,
              PtccObjectID.PTCC_MONITOR_U_SUP_MINUS: PtccMinMax.PTCC_MONITOR_U_SUP_MINUS_MIN,
              PtccObjectID.PTCC_MONITOR_T_DET: PtccMinMax.PTCC_MONITOR_T_DET_MIN,
              PtccObjectID.PTCC_MONITOR_T_INT: PtccMinMax.PTCC_MONITOR_T_INT_MIN,
              PtccObjectID.PTCC_MONITOR_PWM: PtccMinMax.PTCC_MONITOR_PWM_MIN,
              PtccObjectID.PTCC_MONITOR_MODULE_TYPE: PtccMinMax.PTCC_MONITOR_MODULE_TYPE_MIN,
              PtccObjectID.MODULE_IDEN_TYPE: PtccMinMax.MODULE_IDEN_TYPE_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_SUP_CTRL: PtccMinMax.MODULE_BASIC_PARAMS_SUP_CTRL_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS: PtccMinMax.MODULE_BASIC_PARAMS_U_SUP_PLUS_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS: PtccMinMax.MODULE_BASIC_PARAMS_U_SUP_MINUS_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_FAN_CTRL: PtccMinMax.MODULE_BASIC_PARAMS_FAN_CTRL_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL: PtccMinMax.MODULE_BASIC_PARAMS_TEC_CTRL_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_PWM: PtccMinMax.MODULE_BASIC_PARAMS_PWM_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX: PtccMinMax.MODULE_BASIC_PARAMS_I_TEC_MAX_MIN,
              PtccObjectID.MODULE_BASIC_PARAMS_T_DET: PtccMinMax.MODULE_BASIC_PARAMS_T_DET_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_SUP_PLUS: PtccMinMax.MODULE_LAB_M_MONITOR_SUP_PLUS_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_SUP_MINUS: PtccMinMax.MODULE_LAB_M_MONITOR_SUP_MINUS_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_FAN_PLUS: PtccMinMax.MODULE_LAB_M_MONITOR_FAN_PLUS_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_TEC_PLUS: PtccMinMax.MODULE_LAB_M_MONITOR_TEC_PLUS_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_TEC_MINUS: PtccMinMax.MODULE_LAB_M_MONITOR_TEC_MINUS_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_TH1: PtccMinMax.MODULE_LAB_M_MONITOR_TH1_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_TH2: PtccMinMax.MODULE_LAB_M_MONITOR_TH2_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_U_DET: PtccMinMax.MODULE_LAB_M_MONITOR_U_DET_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_U_1ST: PtccMinMax.MODULE_LAB_M_MONITOR_U_1ST_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_U_OUT: PtccMinMax.MODULE_LAB_M_MONITOR_U_OUT_MIN,
              PtccObjectID.MODULE_LAB_M_MONITOR_TEMP: PtccMinMax.MODULE_LAB_M_MONITOR_TEMP_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_DET_U: PtccMinMax.MODULE_LAB_M_PARAMS_DET_U_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_DET_I: PtccMinMax.MODULE_LAB_M_PARAMS_DET_I_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_GAIN: PtccMinMax.MODULE_LAB_M_PARAMS_GAIN_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_OFFSET: PtccMinMax.MODULE_LAB_M_PARAMS_OFFSET_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_VARACTOR: PtccMinMax.MODULE_LAB_M_PARAMS_VARACTOR_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_TRANS: PtccMinMax.MODULE_LAB_M_PARAMS_TRANS_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_ACDC: PtccMinMax.MODULE_LAB_M_PARAMS_ACDC_MIN,
              PtccObjectID.MODULE_LAB_M_PARAMS_BW: PtccMinMax.MODULE_LAB_M_PARAMS_BW_MIN,
              }

MAX_VALUES = {PtccObjectID.PTCC_CONFIG_VARIANT: PtccMinMax.PTCC_CONFIG_VARIANT_MAX,
              PtccObjectID.PTCC_MONITOR_I_SUP_PLUS: PtccMinMax.PTCC_MONITOR_I_SUP_PLUS_MAX,
              PtccObjectID.PTCC_MONITOR_I_SUP_MINUS: PtccMinMax.PTCC_MONITOR_I_SUP_MINUS_MAX,
              PtccObjectID.PTCC_MONITOR_I_FAN_PLUS: PtccMinMax.PTCC_MONITOR_I_FAN_PLUS_MAX,
              PtccObjectID.PTCC_MONITOR_I_TEC: PtccMinMax.PTCC_MONITOR_I_TEC_MAX,
              PtccObjectID.PTCC_MONITOR_U_TEC: PtccMinMax.PTCC_MONITOR_U_TEC_MAX,
              PtccObjectID.PTCC_MONITOR_U_SUP_PLUS: PtccMinMax.PTCC_MONITOR_U_SUP_PLUS_MAX,
              PtccObjectID.PTCC_MONITOR_U_SUP_MINUS: PtccMinMax.PTCC_MONITOR_U_SUP_MINUS_MAX,
              PtccObjectID.PTCC_MONITOR_T_DET: PtccMinMax.PTCC_MONITOR_T_DET_MAX,
              PtccObjectID.PTCC_MONITOR_T_INT: PtccMinMax.PTCC_MONITOR_T_INT_MAX,
              PtccObjectID.PTCC_MONITOR_PWM: PtccMinMax.PTCC_MONITOR_PWM_MAX,
              PtccObjectID.PTCC_MONITOR_MODULE_TYPE: PtccMinMax.PTCC_MONITOR_MODULE_TYPE_MAX,
              PtccObjectID.MODULE_IDEN_TYPE: PtccMinMax.MODULE_IDEN_TYPE_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_SUP_CTRL: PtccMinMax.MODULE_BASIC_PARAMS_SUP_CTRL_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS: PtccMinMax.MODULE_BASIC_PARAMS_U_SUP_PLUS_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS: PtccMinMax.MODULE_BASIC_PARAMS_U_SUP_MINUS_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_FAN_CTRL: PtccMinMax.MODULE_BASIC_PARAMS_FAN_CTRL_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL: PtccMinMax.MODULE_BASIC_PARAMS_TEC_CTRL_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_PWM: PtccMinMax.MODULE_BASIC_PARAMS_PWM_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX: PtccMinMax.MODULE_BASIC_PARAMS_I_TEC_MAX_MAX,
              PtccObjectID.MODULE_BASIC_PARAMS_T_DET: PtccMinMax.MODULE_BASIC_PARAMS_T_DET_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_SUP_PLUS: PtccMinMax.MODULE_LAB_M_MONITOR_SUP_PLUS_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_SUP_MINUS: PtccMinMax.MODULE_LAB_M_MONITOR_SUP_MINUS_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_FAN_PLUS: PtccMinMax.MODULE_LAB_M_MONITOR_FAN_PLUS_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_TEC_PLUS: PtccMinMax.MODULE_LAB_M_MONITOR_TEC_PLUS_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_TEC_MINUS: PtccMinMax.MODULE_LAB_M_MONITOR_TEC_MINUS_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_TH1: PtccMinMax.MODULE_LAB_M_MONITOR_TH1_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_TH2: PtccMinMax.MODULE_LAB_M_MONITOR_TH2_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_U_DET: PtccMinMax.MODULE_LAB_M_MONITOR_U_DET_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_U_1ST: PtccMinMax.MODULE_LAB_M_MONITOR_U_1ST_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_U_OUT: PtccMinMax.MODULE_LAB_M_MONITOR_U_OUT_MAX,
              PtccObjectID.MODULE_LAB_M_MONITOR_TEMP: PtccMinMax.MODULE_LAB_M_MONITOR_TEMP_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_DET_U: PtccMinMax.MODULE_LAB_M_PARAMS_DET_U_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_DET_I: PtccMinMax.MODULE_LAB_M_PARAMS_DET_I_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_GAIN: PtccMinMax.MODULE_LAB_M_PARAMS_GAIN_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_OFFSET: PtccMinMax.MODULE_LAB_M_PARAMS_OFFSET_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_VARACTOR: PtccMinMax.MODULE_LAB_M_PARAMS_VARACTOR_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_TRANS: PtccMinMax.MODULE_LAB_M_PARAMS_TRANS_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_ACDC: PtccMinMax.MODULE_LAB_M_PARAMS_ACDC_MAX,
              PtccObjectID.MODULE_LAB_M_PARAMS_BW: PtccMinMax.MODULE_LAB_M_PARAMS_BW_MAX,
              }


class ModuleType(Enum):
    """
    Type of module connected to PTCC device.

    Attributes
    ----------
    NONE
        module not connected
    NOMEM
        standard IR module without memory EEPROM. Basic device settings are stored in Ptcc memory.
    MEM
        standard IR module with built-in memory. Basic device settings are stored in memory.
    LAB_M
        module LAB_M - communication via RS232 line, half-duplex. Data stored in memory.
    """
    NONE = 0
    NOMEM = 1
    MEM = 2
    LAB_M = 3


class PtccValues:
    """
    String representations of values returned by PTCC device.

    Use LOOKUP_VALUE_LISTS for mapping.
    """
    PTCC_CONFIG_VARIANT_VALUES = "Basic#OEM#Advanced"
    PTCC_CONFIG_VARIANT_VALUES_LIST = ["Basic", "OEM", "Advanced"]
    PTCC_MONITOR_MODULE_TYPE_VALUES = "NONE#NOMEM#MEM#LABM"
    PTCC_MONITOR_MODULE_TYPE_VALUES_LIST = ["NONE", "NOMEM", "MEM", "LABM"]
    MODULE_IDEN_TYPE_VALUES = "NONE#NOMEM#MEM#LABM"
    MODULE_IDEN_TYPE_VALUES_LIST = ["NONE", "NOMEM", "MEM", "LABM"]
    MODULE_IDEN_TEC_TYPE_VALUES = "NONE#NOMEM#MEM#LABM"
    MODULE_IDEN_TEC_TYPE_VALUES_LIST = ["NONE", "NOMEM", "MEM", "LABM"]
    MODULE_BASIC_PARAMS_SUP_CTRL_VALUES = "AUTO#OFF#ON"
    MODULE_BASIC_PARAMS_SUP_CTRL_VALUES_LIST = ["AUTO", "OFF", "ON"]
    MODULE_BASIC_PARAMS_FAN_CTRL_VALUES = "AUTO#OFF#ON"
    MODULE_BASIC_PARAMS_FAN_CTRL_VALUES_LIST = ["AUTO", "OFF", "ON"]
    MODULE_BASIC_PARAMS_TEC_CTRL_VALUES = "AUTO#OFF#ON"
    MODULE_BASIC_PARAMS_TEC_CTRL_VALUES_LIST = ["AUTO", "OFF", "ON"]
    MODULE_LAB_M_PARAMS_TRANS_VALUES = "LOW#HIGH"
    MODULE_LAB_M_PARAMS_TRANS_VALUES_LIST = ["LOW", "HIGH"]
    MODULE_LAB_M_PARAMS_ACDC_VALUES = "AC#DC"
    MODULE_LAB_M_PARAMS_ACDC_VALUES_LIST = ["AC", "DC"]
    MODULE_LAB_M_PARAMS_BW_VALUES = "LOW#MID#HIGH"
    MODULE_LAB_M_PARAMS_BW_VALUES_LIST = ["LOW", "MID", "HIGH"]


LOOKUP_VALUE_LISTS = {PtccObjectID.PTCC_CONFIG_VARIANT: PtccValues.PTCC_CONFIG_VARIANT_VALUES_LIST,
                      PtccObjectID.PTCC_MONITOR_MODULE_TYPE: PtccValues.PTCC_MONITOR_MODULE_TYPE_VALUES_LIST,
                      PtccObjectID.MODULE_IDEN_TYPE: PtccValues.MODULE_IDEN_TYPE_VALUES_LIST,
                      PtccObjectID.MODULE_BASIC_PARAMS_SUP_CTRL: PtccValues.MODULE_BASIC_PARAMS_SUP_CTRL_VALUES_LIST,
                      PtccObjectID.MODULE_BASIC_PARAMS_FAN_CTRL: PtccValues.MODULE_BASIC_PARAMS_FAN_CTRL_VALUES_LIST,
                      PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL: PtccValues.MODULE_BASIC_PARAMS_TEC_CTRL_VALUES_LIST,
                      PtccObjectID.MODULE_LAB_M_PARAMS_TRANS: PtccValues.MODULE_LAB_M_PARAMS_TRANS_VALUES_LIST,
                      PtccObjectID.MODULE_LAB_M_PARAMS_ACDC: PtccValues.MODULE_LAB_M_PARAMS_ACDC_VALUES_LIST,
                      PtccObjectID.MODULE_LAB_M_PARAMS_BW: PtccValues.MODULE_LAB_M_PARAMS_BW_VALUES_LIST,
                      }

BASIC_PARAMS_IDS = {PtccObjectID.MODULE_BASIC_PARAMS_SUP_CTRL, PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS,
                    PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS,
                    PtccObjectID.MODULE_BASIC_PARAMS_FAN_CTRL, PtccObjectID.MODULE_BASIC_PARAMS_TEC_CTRL,
                    PtccObjectID.MODULE_BASIC_PARAMS_PWM,
                    PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX, PtccObjectID.MODULE_BASIC_PARAMS_T_DET
                    }

LAB_M_PARAMS_IDS = {PtccObjectID.MODULE_LAB_M_PARAMS_DET_U, PtccObjectID.MODULE_LAB_M_PARAMS_DET_I,
                    PtccObjectID.MODULE_LAB_M_PARAMS_GAIN,
                    PtccObjectID.MODULE_LAB_M_PARAMS_OFFSET, PtccObjectID.MODULE_LAB_M_PARAMS_OFFSET,
                    PtccObjectID.MODULE_LAB_M_PARAMS_VARACTOR,
                    PtccObjectID.MODULE_LAB_M_PARAMS_TRANS, PtccObjectID.MODULE_LAB_M_PARAMS_ACDC,
                    PtccObjectID.MODULE_LAB_M_PARAMS_BW
                    }

status_messages = {
    0: "detector is cooled, temperature is equal(-/+ 1 K) to temperature defined by user.",
    1: "during the cooling proces.",
    2: "the cooling is deactivated. Check PTTC settings.",
    3: "cooler is working with fixed current."
}

error_messages = {
    128: "“detector overheat” - the set temperature could not be reached during 120 second.",
    129: "Measured current value is higher then maximum current value. PTTC power is off.",
    130: "TEC circuit open connection.",
    131: "TEC circuit is closed connection.",
    132: "thermistor circuit open connection.",
    133: "thermistor circuit closed connection.",
    134: "the temperature inside PTCC is higher than limit.",
    135: "the connected module without memory is not compatible or no module is connected.",
    136: "memory was detected but there are some communication problem.",
    137: "PIP data fault, there are some communication problem.",
    138: "Communication with memory data fault, there are some communication problem.",
    139: "PTTC memory fault.",
    140: "Lab M is incompatible.",
    141: "Memory is incompatible. When the error status code appears the re-turn of the PTTC devices might be required."
}


class PtccSize:
    """
    Contains size (in bytes) of names used by PTCC device.
    """
    MODULE_IDEN_NAME_SIZE = 32
    MODULE_IDEN_DET_NAME_SIZE = 32
    DEVICE_IDEN_NAME_SIZE = 32


class PtccComaPosition:
    """
    Contains coma positions for values returned by PTCC device.

    Use COMA_SCALED for mapping.
    """
    PTCC_MONITOR_I_SUP_PLUS_COMA_POS = 5
    PTCC_MONITOR_I_SUP_MINUS_COMA_POS = 5
    PTCC_MONITOR_I_FAN_PLUS_COMA_POS = 4
    PTCC_MONITOR_I_TEC_COMA_POS = 7
    PTCC_MONITOR_U_TEC_COMA_POS = 3
    PTCC_MONITOR_U_SUP_PLUS_COMA_POS = 3
    PTCC_MONITOR_U_SUP_MINUS_COMA_POS = 3
    PTCC_MONITOR_T_DET_COMA_POS = 3
    PTCC_MONITOR_T_INT_COMA_POS = 1
    MODULE_BASIC_PARAMS_U_SUP_PLUS_COMA_POS = 3
    MODULE_BASIC_PARAMS_U_SUP_MINUS_COMA_POS = 3
    MODULE_BASIC_PARAMS_I_TEC_MAX_COMA_POS = 4
    MODULE_BASIC_PARAMS_T_DET_COMA_POS = 3
    MODULE_LAB_M_MONITOR_SUP_PLUS_COMA_POS = 3
    MODULE_LAB_M_MONITOR_SUP_MINUS_COMA_POS = 3
    MODULE_LAB_M_MONITOR_FAN_PLUS_COMA_POS = 3
    MODULE_LAB_M_MONITOR_TEC_PLUS_COMA_POS = 4
    MODULE_LAB_M_MONITOR_TEC_MINUS_COMA_POS = 4
    MODULE_LAB_M_MONITOR_TH1_COMA_POS = 3
    MODULE_LAB_M_MONITOR_TH2_COMA_POS = 3
    MODULE_LAB_M_MONITOR_U_DET_COMA_POS = 3
    MODULE_LAB_M_MONITOR_U_1ST_COMA_POS = 3
    MODULE_LAB_M_MONITOR_U_OUT_COMA_POS = 3
    MODULE_LAB_M_MONITOR_TEMP_COMA_POS = 1


COMA_SCALED = {PtccObjectID.PTCC_MONITOR_I_SUP_PLUS: PtccComaPosition.PTCC_MONITOR_I_SUP_PLUS_COMA_POS,
               PtccObjectID.PTCC_MONITOR_I_SUP_MINUS: PtccComaPosition.PTCC_MONITOR_I_SUP_MINUS_COMA_POS,
               PtccObjectID.PTCC_MONITOR_I_FAN_PLUS: PtccComaPosition.PTCC_MONITOR_I_FAN_PLUS_COMA_POS,
               PtccObjectID.PTCC_MONITOR_I_TEC: PtccComaPosition.PTCC_MONITOR_I_TEC_COMA_POS,
               PtccObjectID.PTCC_MONITOR_U_TEC: PtccComaPosition.PTCC_MONITOR_U_TEC_COMA_POS,
               PtccObjectID.PTCC_MONITOR_U_SUP_PLUS: PtccComaPosition.PTCC_MONITOR_U_SUP_PLUS_COMA_POS,
               PtccObjectID.PTCC_MONITOR_U_SUP_MINUS: PtccComaPosition.PTCC_MONITOR_U_SUP_MINUS_COMA_POS,
               PtccObjectID.PTCC_MONITOR_T_DET: PtccComaPosition.PTCC_MONITOR_T_DET_COMA_POS,
               PtccObjectID.PTCC_MONITOR_T_INT: PtccComaPosition.PTCC_MONITOR_T_INT_COMA_POS,
               PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_PLUS: PtccComaPosition.MODULE_BASIC_PARAMS_U_SUP_PLUS_COMA_POS,
               PtccObjectID.MODULE_BASIC_PARAMS_U_SUP_MINUS: PtccComaPosition.MODULE_BASIC_PARAMS_U_SUP_MINUS_COMA_POS,
               PtccObjectID.MODULE_BASIC_PARAMS_I_TEC_MAX: PtccComaPosition.MODULE_BASIC_PARAMS_I_TEC_MAX_COMA_POS,
               PtccObjectID.MODULE_BASIC_PARAMS_T_DET: PtccComaPosition.MODULE_BASIC_PARAMS_T_DET_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_SUP_PLUS: PtccComaPosition.MODULE_LAB_M_MONITOR_SUP_PLUS_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_SUP_MINUS: PtccComaPosition.MODULE_LAB_M_MONITOR_SUP_MINUS_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_FAN_PLUS: PtccComaPosition.MODULE_LAB_M_MONITOR_FAN_PLUS_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_TEC_PLUS: PtccComaPosition.MODULE_LAB_M_MONITOR_TEC_PLUS_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_TEC_MINUS: PtccComaPosition.MODULE_LAB_M_MONITOR_TEC_MINUS_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_TH1: PtccComaPosition.MODULE_LAB_M_MONITOR_TH1_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_TH2: PtccComaPosition.MODULE_LAB_M_MONITOR_TH2_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_U_DET: PtccComaPosition.MODULE_LAB_M_MONITOR_U_DET_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_U_1ST: PtccComaPosition.MODULE_LAB_M_MONITOR_U_1ST_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_U_OUT: PtccComaPosition.MODULE_LAB_M_MONITOR_U_OUT_COMA_POS,
               PtccObjectID.MODULE_LAB_M_MONITOR_TEMP: PtccComaPosition.MODULE_LAB_M_MONITOR_TEMP_COMA_POS,
               }


class DeviceRegister(Enum):
    """
    Describes which type of register should be written/read.

    Attributes
    ----------
    DEFAULT
        register for default setting.
    USER_SET
        register for user setting.
    USER_MIN
        register for max allowed setting.
    USER_MAX
        register for min allowed setting.
    """
    DEFAULT = 0
    USER_SET = 1
    USER_MIN = 2
    USER_MAX = 3


class PtccMessageReceiveStatus(Enum):
    """
    Describes status of receiving PtccMessage

    Attributes
    ----------
    OVERFLOW
        Message finished before appending all bytes.
    NOT_BEGAN
        Message empty.
    IN_PROGRESS
        Message began forming. No end character.
    FINISHED
        Message finished and valid.
    """
    OVERFLOW = -2
    NOT_BEGAN = -1
    IN_PROGRESS = 0
    FINISHED = 1


class GainVoltPerVolt(Enum):
    """
    Used for setting gain multiplication.
    """
    X0_5 = 48
    X1 = 56
    X1_5 = 60
    X2 = 64
    X3 = 69
    X5 = 75
    X7 = 80
    X10 = 85
    X15 = 93
    X20 = 99
    X30 = 111


# Format: obj_id: ((raw_min, raw_max), (si_min, si_max))
LINEAR_MAPPED = {
    PtccObjectID.MODULE_LAB_M_PARAMS_DET_U: ((0, 256), (0.0, 1.0)),  # raw 0–256 -> 0–1 V
    PtccObjectID.MODULE_LAB_M_PARAMS_DET_I: ((0, 256), (0.0, 0.01)),  # raw 0–256 -> 0–0.01 A
    PtccObjectID.MODULE_LAB_M_PARAMS_OFFSET: ((0, 256), (1.0, -1.0)),  # raw 0–256 -> 1-(-1) V
}
