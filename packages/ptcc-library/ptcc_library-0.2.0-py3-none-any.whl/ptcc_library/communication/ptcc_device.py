# Author: Wojciech Szczytko
# Created: 2025-04-25
from typing import Union

from abc import abstractmethod
from typing import override

from ptcc_library.ptcc_defines import ModuleType, DeviceRegister, PtccCtrl, GainVoltPerVolt, CallbackPtccObjectID, \
    PtccMessageReceiveStatus, PtccValues
from ptcc_library.ptcc_object import PtccObject
from ptcc_library.communication.ptcc_communication_iface import CommunicationInterface, ThrottledCommunication
from ptcc_library.communication.ptcc_protocol import (PtccMessageReceiver,
                                                      generate_msg_get_device_iden,
                                                      generate_msg_get_module_iden,
                                                      generate_msg_get_monitor,
                                                      generate_msg_get_basic_params,
                                                      generate_msg_get_config,
                                                      generate_msg_set_cooler_disabled,
                                                      generate_msg_set_cooler_enabled,
                                                      generate_msg_set_cooler_auto,
                                                      generate_msg_set_module_param,
                                                      generate_msg_set_fan,
                                                      generate_msg_set_max_current,
                                                      generate_msg_set_temperature,
                                                      generate_msg_set_module_lab_m_param,
                                                      generate_msg_set_module_lab_m_offset,
                                                      generate_msg_set_supply_voltage,
                                                      generate_msg_get_lab_m_monitor,
                                                      generate_msg_get_lab_m_params,
                                                      generate_msg_set_module_lab_m_detector_voltage_bias,
                                                      generate_msg_set_module_lab_m_detector_current_bias_compensation,
                                                      generate_msg_set_module_lab_m_gain,
                                                      generate_msg_set_module_lab_m_varactor,
                                                      generate_msg_set_module_lab_m_transimpedance_low,
                                                      generate_msg_set_module_lab_m_transimpedance_high,
                                                      generate_msg_set_module_lab_m_coupling_ac,
                                                      generate_msg_set_module_lab_m_coupling_dc,
                                                      generate_msg_set_module_lab_m_bandwidth_low,
                                                      generate_msg_set_module_lab_m_bandwidth_mid,
                                                      generate_msg_set_module_lab_m_bandwidth_high
                                                      )


class PtccDevice:
    """
    High-level interface for communicating with a PTCC device.

    This class wraps a lower-level communication interface and handles message construction,
    throttling, and dispatching for PTCC commands. It optionally connects to a message
    receiver for returning values from received messages.

    Use detect_device() for ensuring correct device/module type is used.

    Parameters
    ----------
    comm : CommunicationInterface
        A low-level communication object that handles byte-level I/O with the device.
    receiver : PtccMessageReceiver, optional
        An optional receiver instance to manage incoming messages. If not provided, a default
        `PtccMessageReceiver` will be used.

    Attributes
    ----------
    comm : ThrottledCommunication
        A communication wrapper that ensures a minimum delay (0.55s) between message transmissions.
    receiver : PtccMessageReceiver
        The object responsible for receiving and decoding incoming PTCC messages.
    """

    def __init__(self, comm: CommunicationInterface, receiver: PtccMessageReceiver = None):

        self.comm = ThrottledCommunication(comm, min_delay=0.55)
        if receiver is None:
            self.receiver = PtccMessageReceiver()
        else:
            self.receiver = receiver

    @property
    def module_type(self) -> ModuleType:
        """
        ModuleType : type of module connected to PTCC device.
        """

        if isinstance(self, PtccNoMemDevice):
            module_type = ModuleType.NOMEM
        elif isinstance(self, PtccLabMDevice):
            module_type = ModuleType.LAB_M
        elif isinstance(self, PtccMemDevice):
            module_type = ModuleType.MEM
        else:
            module_type = ModuleType.NONE

        return module_type

    def write_msg_get_device_iden(self):
        """
        Sends a message to PTCC device.
        Used for reading identification data of PTCC device.

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
        msg = generate_msg_get_device_iden()
        self.comm.write(bytes(msg))
        
    def write_msg_get_config(self):
        """
        Sends a message to PTCC device.
        Used for reading PTCC device type.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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
        msg = generate_msg_get_config()
        self.comm.write(bytes(msg))

    @abstractmethod
    def write_msg_get_module_iden(self):
        """
        Sends a message to PTCC device.
        Used for reading identification and configuration data of module connected to PTCC device.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_get_monitor(self):
        """
        Sends a message to PTCC device.
        Used for reading measured parameters of no memory module connected to PTCC device.

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
        msg = generate_msg_get_monitor()
        self.comm.write(bytes(msg))

    @abstractmethod
    def write_msg_get_lab_m_monitor(self):
        """
        Sends a message to PTCC device.
        Used for reading measured lab_m parameters of module connected to PTCC device.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_get_basic_params(self, target: DeviceRegister = DeviceRegister.USER_SET):
        """
        Sends a message to PTCC device.
        Used for reading configuration (power, cooling) data for module connected to PTCC device.

        Parameters
        ----------
        target: DeviceRegister
            Specifies which type of register should be read:
            DeviceRegister.DEFAULT - register for default setting.
            DeviceRegister.USER_SET - register for user setting.
            DeviceRegister.USER_MIN - register for max allowed setting.
            DeviceRegister.USER_MAX - register for min allowed setting.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_get_lab_m_params(self,  target: DeviceRegister = DeviceRegister.USER_SET):
        """
        Sends a message to PTCC device.
        Used for reading lab_m configuration data for module connected to PTCC device.

        Parameters
        ----------
        target: DeviceRegister
            Specifies which type of register should be read:
            DeviceRegister.DEFAULT - register for default setting.
            DeviceRegister.USER_SET - register for user setting.
            DeviceRegister.USER_MIN - register for max allowed setting.
            DeviceRegister.USER_MAX - register for min allowed setting.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_param(self, ptcc_object: PtccObject):
        """
        Sends a message to PTCC device.
        Used for setting and saving lab_m parameters.

        Parameters
        ----------
        ptcc_object: PtccObject
            PTCC object to send as configuration.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_cooler_disabled(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving operating mode of TEC as disabled.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_cooler_enabled(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving operating mode of TEC as enabled (Cooler will work with fixed supply current).

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_cooler_auto(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving operating mode of TEC as auto.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_param(self, ptcc_object: PtccObject):
        """
        Sends a message to PTCC device.
        Used for setting and saving module parameters.

        Parameters
        ----------
        ptcc_object: PtccObject
            PTCC object to send as configuration. Objects ID must be from BASIC_PARAMS_IDS list.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_fan(self, mode: PtccCtrl):
        """
        Sends a message to PTCC device.
        Used for setting and saving operation state of fan control.

        Parameters
        ----------
        mode: PtccCtrl
            operation state of fan control. On, Off or Auto.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_supply_voltage(self, supp_ctrl_mode: PtccCtrl, supply_voltage_positive: float,
                                     supply_voltage_negative: float):
        """
        Sends a message to PTCC device.
        Used for setting output voltage values of power lines.

        Parameters
        ----------
        supp_ctrl_mode: PtccCtrl
            Variable is used to set operating mode of power supply output. AUTO mode is used to protect the detector.
        supply_voltage_positive: float
            Represented in Volts. Responsible for setting output voltage value of positive power line.
        supply_voltage_negative: float
            Represented in Volts. Responsible for setting output voltage value of positive power line.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

        Example
        -------
        write_msg_set_supply_voltage(supp_ctrl_mode=PtccCtrl.AUTO, supply_voltage_positive=9.0, supply_voltage_negative=-9.0)
        """

    @abstractmethod
    def write_msg_set_max_current(self, value_in_amperes: float):
        """
        Sends a message to PTCC device.
        Used for setting maximum current for TEC output.

        Parameters
        ----------
        value_in_amperes: float
            Represented in Amperes. Describes maximum current for TEC output.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_temperature(self, value_in_kelvins: int):
        """
        Sends a message to PTCC device.
        Used for setting and saving desired detector temperature.

        Parameters
        ----------
        value_in_kelvins: int
            Represented in Kelvins. Describes desired detector temperature.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_detector_voltage_bias(self, bias_value_in_volts: float):
        """
        Sends a message to PTCC device.
        Used for setting and saving value of detector bias voltage for lab_m module.

        Parameters
        ----------
        bias_value_in_volts: float
            detector bias voltage in Volts. Must be in the range [0.0, 1.0].

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_detector_current_bias_compensation(self, bias_value_in_ampers: float):
        """
        Sends a message to PTCC device.
        Used for setting and saving value of bias current compensation for lab_m module.

        Parameters
        ----------
        bias_value_in_ampers: float
            lab_m currrent bias compensation in Ampers. Must be in the range [0.0, 0.01].

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_gain(self, gain: Union[GainVoltPerVolt, int]):
        """
        Sends a message to PTCC device.
        Used for setting and saving value of second stage gain for lab_m module.

        Parameters
        ----------
        gain: Union[GainVoltPerVolt, int]
            lab_m gain. If integer (bit value) is provided the value must be in range [0, 256].

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

        Example
        -------
        write_msg_set_module_lab_m_gain(GainVoltPerVolt.X5)
            Sets gain equal to 5 V/V.
        write_msg_set_module_lab_m_gain(75)
            Sets gain equal to 5 V/V corresponding to number 75 [bit value].
        """

    @abstractmethod
    def write_msg_set_module_lab_m_offset(self, offset_value_in_volts: float):
        """
        Sends a message to PTCC device.
        Used for setting and saving lab_m output DC offset for lab_m module.

        Parameters
        ----------
        offset_value_in_volts: float
            lab_m output DC offset. Must be in the range [-1.0, 1.0].

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_varactor(self, compensation: int):
        """
        Sends a message to PTCC device.
        Used for setting and saving frequency compensation for the preamplifier first stage for lab_m module.

        Parameters
        ----------
        compensation: int
            lab_m frequency compensation.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_transimpedance_low(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving transimpedance of first stage preamplifier as LOW for lab_m module.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_transimpedance_high(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving transimpedance of first stage preamplifier as HIGH for lab_m module.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_coupling_ac(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving the coupling mode as AC for lab_m module for lab_m module.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_coupling_dc(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving the coupling mode as DC for lab_m module.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_bandwidth_low(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving value of bandwidth as LOW (1.5 MHz) for lab_m module.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_bandwidth_mid(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving value of bandwidth as MID (15 MHz) for lab_m module.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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

    @abstractmethod
    def write_msg_set_module_lab_m_bandwidth_high(self):
        """
        Sends a message to PTCC device.
        Used for setting and saving value of bandwidth as HIGH (Depends on detector parameters and first stage
        transimpedance) for lab_m module.

        Raises
        ------
        TypeError
            Raised to indicate that this message type is unsupported for specified device/module type.
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


class PtccNoMemDevice(PtccDevice):

    def __init__(self, comm: CommunicationInterface, receiver: PtccMessageReceiver = None):
        super().__init__(comm, receiver)

    @override
    def write_msg_get_module_iden(self):
        msg = generate_msg_get_module_iden(ModuleType.NOMEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_get_lab_m_monitor(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_get_basic_params(self, target: DeviceRegister = DeviceRegister.USER_SET):
        msg = generate_msg_get_basic_params(ModuleType.NOMEM, target)
        self.comm.write(bytes(msg))

    @override
    def write_msg_get_lab_m_params(self, target: DeviceRegister = DeviceRegister.USER_SET):
        msg = generate_msg_get_lab_m_params(ModuleType.NOMEM, target)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_param(self, ptcc_object: PtccObject):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_offset(self, offset_value_in_volts: float):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_cooler_disabled(self):
        msg = generate_msg_set_cooler_disabled(ModuleType.NOMEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_cooler_enabled(self):
        msg = generate_msg_set_cooler_enabled(ModuleType.NOMEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_cooler_auto(self):
        msg = generate_msg_set_cooler_auto(ModuleType.NOMEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_param(self, ptcc_object: PtccObject):
        msg = generate_msg_set_module_param(ModuleType.NOMEM, ptcc_object)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_fan(self, mode: PtccCtrl):
        msg = generate_msg_set_fan(ModuleType.NOMEM, mode)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_supply_voltage(self, supp_ctrl_mode: PtccCtrl, supply_voltage_positive: float,
                                     supply_voltage_negative: float):
        msg = generate_msg_set_supply_voltage(ModuleType.NOMEM, supp_ctrl_mode, supply_voltage_positive,
                                              supply_voltage_negative)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_max_current(self, value_in_amperes: float):
        msg = generate_msg_set_max_current(ModuleType.NOMEM, value_in_amperes)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_temperature(self, value_in_kelvins: int):
        msg = generate_msg_set_temperature(ModuleType.NOMEM, value_in_kelvins)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_detector_voltage_bias(self, bias_value_in_volts: float):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_detector_current_bias_compensation(self, bias_value_in_ampers: float):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_gain(self, gain: Union[GainVoltPerVolt, int]):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_varactor(self, compensation: int):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_transimpedance_low(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_transimpedance_high(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_coupling_ac(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_coupling_dc(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_bandwidth_low(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_bandwidth_mid(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_bandwidth_high(self):
        raise TypeError("module type does not support this message")


class PtccMemDevice(PtccDevice):

    def __init__(self, comm: CommunicationInterface, receiver: PtccMessageReceiver = None):
        super().__init__(comm, receiver)

    @override
    def write_msg_get_module_iden(self):
        msg = generate_msg_get_module_iden(ModuleType.MEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_get_lab_m_monitor(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_get_basic_params(self, target: DeviceRegister = DeviceRegister.USER_SET):
        msg = generate_msg_get_basic_params(ModuleType.MEM, target)
        self.comm.write(bytes(msg))

    @override
    def write_msg_get_lab_m_params(self, target: DeviceRegister = DeviceRegister.USER_SET):
        msg = generate_msg_get_lab_m_params(ModuleType.MEM, target)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_param(self, ptcc_object: PtccObject):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_offset(self, offset_value_in_volts: float):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_cooler_disabled(self):
        msg = generate_msg_set_cooler_disabled(ModuleType.MEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_cooler_enabled(self):
        msg = generate_msg_set_cooler_enabled(ModuleType.MEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_cooler_auto(self):
        msg = generate_msg_set_cooler_auto(ModuleType.MEM)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_param(self, ptcc_object: PtccObject):
        msg = generate_msg_set_module_param(ModuleType.MEM, ptcc_object)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_fan(self, mode: PtccCtrl):
        msg = generate_msg_set_fan(ModuleType.MEM, mode)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_supply_voltage(self, supp_ctrl_mode: PtccCtrl, supply_voltage_positive: float,
                                     supply_voltage_negative: float):
        msg = generate_msg_set_supply_voltage(ModuleType.MEM, supp_ctrl_mode, supply_voltage_positive,
                                              supply_voltage_negative)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_max_current(self, value_in_amperes: float):
        msg = generate_msg_set_max_current(ModuleType.MEM, value_in_amperes)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_temperature(self, value_in_kelvins: int):
        msg = generate_msg_set_temperature(ModuleType.MEM, value_in_kelvins)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_detector_voltage_bias(self, bias_value_in_volts: float):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_detector_current_bias_compensation(self, bias_value_in_ampers: float):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_gain(self, gain: Union[GainVoltPerVolt, int]):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_varactor(self, compensation: int):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_transimpedance_low(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_transimpedance_high(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_coupling_ac(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_coupling_dc(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_bandwidth_low(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_bandwidth_mid(self):
        raise TypeError("module type does not support this message")

    @override
    def write_msg_set_module_lab_m_bandwidth_high(self):
        raise TypeError("module type does not support this message")


class PtccLabMDevice(PtccMemDevice):

    def __init__(self, comm: CommunicationInterface, receiver: PtccMessageReceiver = None):
        super().__init__(comm, receiver)

    @override
    def write_msg_get_lab_m_monitor(self):
        msg = generate_msg_get_lab_m_monitor(ModuleType.LAB_M)
        self.comm.write(bytes(msg))

    @override
    def write_msg_get_lab_m_params(self, target: DeviceRegister = DeviceRegister.USER_SET):
        msg = generate_msg_get_lab_m_params(ModuleType.LAB_M, target)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_param(self, ptcc_object: PtccObject):
        msg = generate_msg_set_module_lab_m_param(ModuleType.LAB_M, ptcc_object)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_offset(self, offset_value_in_volts: float):
        msg = generate_msg_set_module_lab_m_offset(ModuleType.LAB_M, offset_value_in_volts)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_supply_voltage(self, supp_ctrl_mode: PtccCtrl, supply_voltage_positive: float,
                                     supply_voltage_negative: float):
        msg = generate_msg_set_supply_voltage(ModuleType.LAB_M, supp_ctrl_mode, supply_voltage_positive,
                                              supply_voltage_negative)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_detector_voltage_bias(self, bias_value_in_volts: float):
        msg = generate_msg_set_module_lab_m_detector_voltage_bias(ModuleType.LAB_M, bias_value_in_volts)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_detector_current_bias_compensation(self, bias_value_in_ampers: float):
        msg = generate_msg_set_module_lab_m_detector_current_bias_compensation(ModuleType.LAB_M,
                                                                               bias_value_in_ampers)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_gain(self, gain: Union[GainVoltPerVolt, int]):
        msg = generate_msg_set_module_lab_m_gain(ModuleType.LAB_M, gain)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_varactor(self, compensation: int):
        msg = generate_msg_set_module_lab_m_varactor(ModuleType.LAB_M, compensation)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_transimpedance_low(self):
        msg = generate_msg_set_module_lab_m_transimpedance_low(ModuleType.LAB_M)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_transimpedance_high(self):
        msg = generate_msg_set_module_lab_m_transimpedance_high(ModuleType.LAB_M)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_coupling_ac(self):
        msg = generate_msg_set_module_lab_m_coupling_ac(ModuleType.LAB_M)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_coupling_dc(self):
        msg = generate_msg_set_module_lab_m_coupling_dc(ModuleType.LAB_M)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_bandwidth_low(self):
        msg = generate_msg_set_module_lab_m_bandwidth_low(ModuleType.LAB_M)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_bandwidth_mid(self):
        msg = generate_msg_set_module_lab_m_bandwidth_mid(ModuleType.LAB_M)
        self.comm.write(bytes(msg))

    @override
    def write_msg_set_module_lab_m_bandwidth_high(self):
        msg = generate_msg_set_module_lab_m_bandwidth_high(ModuleType.LAB_M)
        self.comm.write(bytes(msg))


def detect_device(comm: CommunicationInterface, receiver: PtccMessageReceiver = None) -> PtccDevice:
    """
    Detects the connected PTCC module type and returns an appropriate device interface instance.

    This function sends a query to the connected PTCC device to identify type of module connected to it by
    requesting monitor information. Based on the response, it instantiates and returns
    the appropriate subclass of `PtccDevice`.

    Parameters
    ----------
    comm : CommunicationInterface
        The communication interface to send and receive data from the PTCC device.
    receiver : PtccMessageReceiver, optional
        An optional receiver to be passed to the constructed `PtccDevice` instance.
        If not provided, a new receiver will be created internally.

    Returns
    -------
    PtccDevice
        A specific subclass of `PtccDevice` based on the detected module type.

    Raises
    ------
    IOError
        If no response is received from the device after repeated attempts.
    ValueError
        If the received module type is not recognized.

    Notes
    -----
    The function reads bytes from the communication interface until a complete and valid
    message is received or the timeout threshold is reached. module type detection is
    based on a response to the `generate_msg_get_monitor` query.
    """
    temp_receiver = PtccMessageReceiver()
    device_responded = False
    device_type = "NONE"

    def iden_callback(dev_type):
        nonlocal device_responded
        nonlocal device_type
        device_responded = True
        device_type = dev_type

    temp_receiver.register_callback(CallbackPtccObjectID.PTCC_MONITOR_MODULE_TYPE, iden_callback)
    comm.write(bytes(generate_msg_get_monitor()))

    timeout = 0
    while not device_responded:
        if timeout > 256:
            raise IOError("No response from device")
        timeout += 1
        byte = comm.read(1)  # Read 1 byte at a time
        if byte:
            if PtccMessageReceiveStatus.FINISHED == temp_receiver.add_byte(byte[0]):  # Convert bytes -> int
                temp_receiver.reset()
                break

    if device_type == PtccValues.PTCC_MONITOR_MODULE_TYPE_VALUES_LIST[ModuleType.NONE.value]:
        return PtccDevice(comm, receiver)
    elif device_type == PtccValues.PTCC_MONITOR_MODULE_TYPE_VALUES_LIST[ModuleType.NOMEM.value]:
        return PtccNoMemDevice(comm, receiver)
    elif device_type == PtccValues.PTCC_MONITOR_MODULE_TYPE_VALUES_LIST[ModuleType.MEM.value]:
        return PtccMemDevice(comm, receiver)
    elif device_type == PtccValues.PTCC_MONITOR_MODULE_TYPE_VALUES_LIST[ModuleType.LAB_M.value]:
        return PtccLabMDevice(comm, receiver)
    else:
        raise ValueError("module type not recognized")
