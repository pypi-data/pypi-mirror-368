__author__ = "Wojciech Szczytko"
__email__ = "wszczytko@vigo.com.pl"

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ptcc_library.ptcc_defines import (
    START_BYTE, STOP_BYTE,
    ValType, PtccCtrl, PtccTimeStruct, CONTAINER_IDS, PtccObjectID, PtccMessageReceiveStatus, PtccSize,
    ModuleType, CallbackPtccObjectID, BASIC_PARAMS_IDS, LAB_M_PARAMS_IDS,
    GainVoltPerVolt, LINEAR_MAPPED, DeviceRegister, status_messages, error_messages
)

from ptcc_library.communication.ptcc_communication_iface import CommunicationInterface
from ptcc_library.communication.ptcc_device import detect_device, PtccDevice, PtccNoMemDevice, \
    PtccLabMDevice, PtccMemDevice

from ptcc_library.ptcc_object import PtccObject

from ptcc_library.communication.ptcc_protocol import (
    PtccMessage,
    ptcc_message_to_ptcc_object, create_set_ptcc_message, create_get_ptcc_message, PtccMessageReceiver,
    generate_msg_get_device_iden,
    generate_msg_get_module_iden, generate_msg_get_monitor, generate_msg_get_basic_params, generate_msg_get_config,
    generate_msg_set_cooler_disabled, generate_msg_set_cooler_enabled,
    generate_msg_set_cooler_auto, generate_msg_set_module_param, generate_msg_set_fan,
    generate_msg_set_max_current, generate_msg_set_temperature, generate_msg_set_module_lab_m_param,
    generate_msg_set_module_lab_m_offset, generate_msg_set_supply_voltage,
    generate_msg_get_lab_m_monitor, generate_msg_get_lab_m_params,
    generate_msg_set_module_lab_m_detector_voltage_bias,
    generate_msg_set_module_lab_m_detector_current_bias_compensation,
    generate_msg_set_module_lab_m_gain, generate_msg_set_module_lab_m_varactor,
    generate_msg_set_module_lab_m_transimpedance_low, generate_msg_set_module_lab_m_transimpedance_high,
    generate_msg_set_module_lab_m_coupling_ac, generate_msg_set_module_lab_m_coupling_dc,
    generate_msg_set_module_lab_m_bandwidth_low, generate_msg_set_module_lab_m_bandwidth_mid,
    generate_msg_set_module_lab_m_bandwidth_high
)

from ptcc_library.ptcc_utils import flatten, to_bytes, from_bytes

# Define __all__ to specify what gets exposed when using `from ptcc_library import *`
__all__ = [
    # defines
    "START_BYTE", "STOP_BYTE", "ValType",
    "PtccCtrl", "PtccTimeStruct",
    "CONTAINER_IDS", "PtccObjectID", "PtccMessageReceiveStatus", "PtccSize",
    "ModuleType", "CallbackPtccObjectID", "BASIC_PARAMS_IDS", "LAB_M_PARAMS_IDS",
    "GainVoltPerVolt", "LINEAR_MAPPED", "DeviceRegister", "status_messages", "error_messages",

    # object
    "PtccObject",

    # protocol
    "ptcc_message_to_ptcc_object", "PtccMessage", "create_set_ptcc_message", "create_get_ptcc_message",
    "PtccMessageReceiver",
    "generate_msg_get_device_iden",
    "generate_msg_get_module_iden", "generate_msg_get_monitor", "generate_msg_get_basic_params",
    "generate_msg_get_config",
    "generate_msg_set_cooler_disabled", "generate_msg_set_cooler_enabled",
    "generate_msg_set_cooler_auto", "generate_msg_set_module_param", "generate_msg_set_fan",
    "generate_msg_set_max_current", "generate_msg_set_temperature", "generate_msg_set_module_lab_m_param",
    "generate_msg_set_module_lab_m_offset", "generate_msg_set_supply_voltage", "generate_msg_get_lab_m_monitor",
    "generate_msg_get_lab_m_params",
    "generate_msg_set_module_lab_m_detector_voltage_bias", "generate_msg_set_module_lab_m_gain",
    "generate_msg_set_module_lab_m_detector_current_bias_compensation",
    "generate_msg_set_module_lab_m_varactor", "generate_msg_set_module_lab_m_transimpedance_low",
    "generate_msg_set_module_lab_m_transimpedance_high", "generate_msg_set_module_lab_m_coupling_ac",
    "generate_msg_set_module_lab_m_coupling_dc", "generate_msg_set_module_lab_m_bandwidth_low",
    "generate_msg_set_module_lab_m_bandwidth_mid", "generate_msg_set_module_lab_m_bandwidth_high",

    # communication
    "CommunicationInterface",
    "detect_device", "PtccDevice", "PtccNoMemDevice", "PtccLabMDevice", "PtccMemDevice",

    # utilities
    "flatten", "to_bytes", "from_bytes"
]
