# Author: Wojciech Szczytko
# Created: 2025-03-28
from typing import Union

from ptcc_library.ptcc_defines import MAX_VALUES, MIN_VALUES, ValType, CONTAINER_IDS, LOOKUP_VALUE_LISTS, COMA_SCALED, \
    LINEAR_MAPPED, PtccObjectID
from ptcc_library.ptcc_utils import to_bytes, from_bytes


class PtccObject:
    """
    Represents a basic object used in PTCC messages.

    PtccObject is the base class for all message components in the PTCC protocol.
    It can contain nested objects (if it’s a container), which are stored in the `objects` attribute.

    Parameters
    ----------
    raw_object : bytes or bytearray or list of int, optional
        Raw binary representation of the object. Used to parse and initialize the object.
    obj_id : int or PtccObjectID, optional
        Identifier for the object. Can be a plain integer or a PtccObjectID enum.
    data : bytes, bytearray, str, or list of int, optional
        Raw data payload for the object.
    data_value : any, optional
        Parsed or human-readable representation of the data, if applicable.
    value : any, optional
        The value represented in SI units. It is equivalent to `data_value`, but expressed using standard
        international units. If applicable.
    """
    def __init__(self,
                 raw_object: Union[bytes, bytearray, list[int]] = None,
                 obj_id: Union[int, PtccObjectID] = None,
                 data: Union[bytes, bytearray, str, list[int]] = None,
                 data_value: any = None, value: any = None):

        self._objects: list[PtccObject] = []  # Always present, empty for non-containers

        if raw_object:
            # Process raw_object...
            if isinstance(raw_object, (bytes, bytearray)):
                raw_object = list(raw_object)
            if len(raw_object) < 4:
                raise ValueError("Raw object too short")
            self._obj_id = (raw_object[0] << 8) + raw_object[1]
            self._dlen = (raw_object[2] << 8) + raw_object[3]
            self._raw_object = raw_object[:self._dlen]
            self._data = raw_object[4:self._dlen] if self._dlen > 4 else []
            # If the object is a container, you might populate `self._objects` here.
            if self.is_container:
                self._parse_container()
        elif obj_id is not None:
            if isinstance(obj_id, PtccObjectID):
                obj_id = obj_id.value

            if value is not None:
                data_value = _to_raw_value(obj_id, value)

            # Process based on provided obj_id and data.
            if data is None and data_value is None:
                raise ValueError("Please set data or data_value")

            if data_value is not None:
                if PtccObjectID(obj_id) in MAX_VALUES:
                    if MAX_VALUES[PtccObjectID(obj_id)] >= data_value >= MIN_VALUES[PtccObjectID(obj_id)]:
                        pass
                    else:
                        raise ValueError("Value out of range")

            self._obj_id = obj_id
            if data is not None:
                if isinstance(data, str):
                    self._data = to_bytes(ValType.CSTR, data)
                else:
                    self._data = list(data)
            else:
                dt = self.data_type
                try:
                    data_type = ValType(dt)
                except ValueError:
                    raise ValueError("Unknown data type: " + str(dt))
                self._data = to_bytes(data_type, data_value)
                if data_type == ValType.CONTAINER:
                    self._parse_container()
            self._dlen = len(self._data) + 4
            self._raw_object = to_bytes(ValType.UINT16, self._obj_id) + to_bytes(ValType.UINT16,
                                                                                 self._dlen) + self._data
            if self.is_container:
                self._parse_container()
            # self.raw_object = list(obj_id.to_bytes(2, 'big')) + [0, 0] + self.data
        else:
            raise ValueError("Invalid arguments: must provide raw_object or obj_id")

    def __str__(self) -> str:
        return "Ptcc Object: " + self._raw_object.__str__()

    def __eq__(self, other: "PtccObject") -> bool:
        return self._raw_object == other._raw_object

    @property
    def obj_id(self) -> int:
        """
        int: The full object ID of this PtccObject.

        Notes
        -----
        Encodes both the object type and data type.
        """
        return self._obj_id

    @property
    def name(self) -> str:
        """
        str: The full PtccObjectID name of this PtccObject.
        """
        return PtccObjectID(self._obj_id).name

    @property
    def data_type(self) -> int:
        """
        int: Represents data type of data contained in PtccObject.
        """
        return self._obj_id & 0x0F

    @property
    def raw_object(self) -> list[int]:
        """
        list[int]: Raw binary representation of the object.
        """
        return self._raw_object

    @property
    def data(self) -> list[int]:
        """
        list[int]: Raw binary representation of data contained in object.
        """
        return self._data

    @property
    def value(self) -> any:
        """
        list[int]: Represents value of data contained in PtccObject.

        Raises
        ------
        ValueError
            if no data is stored in PtccObject, or if value is out of expected range.
        """
        if not self.data:
            raise ValueError("Object does not contain any data")

        if self.obj_id in CONTAINER_IDS:
            return self.objects

        dtype = ValType(self.data_type)
        raw_value = from_bytes(dtype, self.data)

        try:
            obj_id = PtccObjectID(self.obj_id)
        except ValueError:
            return raw_value

        if obj_id in LOOKUP_VALUE_LISTS:
            return LOOKUP_VALUE_LISTS[obj_id][raw_value]

        if obj_id in COMA_SCALED:
            return raw_value / (10 ** COMA_SCALED[obj_id])

        if obj_id in LINEAR_MAPPED:
            (raw_min, raw_max), (si_min, si_max) = LINEAR_MAPPED[obj_id]
            if not raw_min <= raw_value <= raw_max:
                raise ValueError(
                    f"Raw value {raw_value} out of expected range [{raw_min}, {raw_max}] for {obj_id.name}")
            scale = (si_max - si_min) / (raw_max - raw_min)
            return si_min + (raw_value - raw_min) * scale

        if obj_id == PtccObjectID.PTCC_MONITOR_TH_ADC:
            adc_full_scale = 1048576
            ser_res = 100000.0
            denominator = adc_full_scale - raw_value
            return float('inf') if denominator == 0 else max(raw_value * ser_res / denominator, 0)

        passthrough_ids = {
            PtccObjectID.PTCC_CONFIG_NO_MEM_COMPATIBLE,
            PtccObjectID.PTCC_MONITOR_STATUS,
            PtccObjectID.MODULE_IDEN_TH_TYPE,
            PtccObjectID.DEVICE_IDEN_FIRM_VER,
            PtccObjectID.DEVICE_IDEN_SERIAL,
            PtccObjectID.DEVICE_IDEN_PROD_DATE,
            PtccObjectID.MODULE_IDEN_TEC_PARAM1,
            PtccObjectID.MODULE_IDEN_TEC_PARAM2,
            PtccObjectID.MODULE_IDEN_TEC_PARAM3,
            PtccObjectID.MODULE_IDEN_TEC_PARAM4,
            PtccObjectID.MODULE_IDEN_NAME,
            PtccObjectID.PTCC_MONITOR_PWM,
        }

        if obj_id in passthrough_ids:
            return raw_value

        return raw_value

    @property
    def objects(self) -> list["PtccObject"]:
        """
        list[PtccObject]: list of PtccObjects stored in container.
        May return empty list if PtccObject is not a container, or container is empty.
        """
        return self._objects

    @property
    def is_container(self) -> bool:
        """
        bool : check if PtccObject is a container.
        """
        return self.data_type == ValType.CONTAINER.value

    def unpack_container(self) -> list["PtccObject"]:
        """
        Returns
        -------
        list[PtccObject] : list of PtccObjects stored in container.

        Raises
        ------
        TypeError
            if PtccObject is not a container.
        """
        if self.is_container:
            return self._objects
        else:
            raise TypeError("Object is not a container")

    def flatten_container(self) -> list["PtccObject"]:
        """
        Flattens container

        Returns
        -------
        list[PtccObject] : list of PtccObjects stored in container and self.

        Raises
        ------
        TypeError
            if PtccObject is not a container.
        """
        if not self.is_container:
            raise TypeError("Object is not a container")

        flattened = []
        for obj in self._objects:
            if obj.is_container:
                flattened.extend(obj.flatten_container())
            else:
                flattened.append(obj)

        return [self] + flattened

    def _set_dlen(self, dlen: int) -> None:
        self._dlen += (dlen - self._dlen)

        obj_id_bytes = to_bytes(ValType.UINT16, self._obj_id)
        dlen_bytes = to_bytes(ValType.UINT16, self._dlen)

        self._raw_object = obj_id_bytes + dlen_bytes + self._data

    def _add_object_to_container(self, ptcc_object: "PtccObject") -> None:
        if self.is_container:
            if not isinstance(ptcc_object, PtccObject):
                raise TypeError("ptcc_object must be an instance of PtccObject")
            ptcc_object_raw_data = ptcc_object.raw_object
            self._set_dlen(self._dlen + len(ptcc_object_raw_data))
            self._objects.append(ptcc_object)
            self._data.extend(ptcc_object_raw_data)
            self._raw_object.extend(ptcc_object_raw_data)
        else:
            raise TypeError("Object is not a container")

    def pack_container(self, ptcc_objects: list["PtccObject"]) -> list[int]:
        """
        Adds objects to container

        Parameters
        ----------
        ptcc_objects: list[PtccObject]
            list of PtccObjects that should be stored in PtccObject.

        Returns
        -------
        list[int] : Raw binary representation of the object.

        Raises
        ------
        TypeError
            if PtccObject is not a container.
        TypeError
            if ptcc_objects contains types other than PtccObject.
        """
        if self.is_container:
            if not all(isinstance(obj, PtccObject) for obj in ptcc_objects):
                raise TypeError("ptcc_objects must be an instance of list[PtccObject]")
            for ptcc_object in ptcc_objects:
                self._add_object_to_container(ptcc_object)
            return self.raw_object
        else:
            raise TypeError("Object is not a container")

    def _parse_container(self) -> None:
        """Parse data into sub-objects and store them in _objects.

        Raises
        ------
            Errors invoked while creating PtccObjects
        """
        index = 0
        while index < len(self._data):
            try:
                obj = PtccObject(raw_object=self._data[index:])
            except Exception as e:
                raise e
            self._objects.append(obj)
            index += obj._dlen


def _to_raw_value(obj_id: Union[PtccObjectID, int], value: any) -> int:
    """
    Converts a real-world value back to raw integer based on object ID scaling or lookup.

    Returns
    -------
    int : Raw integer based on provided object ID scaling or lookup.

    Raise
    -----
    ValueError
        if value is out of expected range
    """
    if isinstance(obj_id, int):
        obj_id = PtccObjectID(obj_id)

    if obj_id in LINEAR_MAPPED:
        (raw_min, raw_max), (si_min, si_max) = LINEAR_MAPPED[obj_id]
        if not min(si_min, si_max) <= value <= max(si_min, si_max):
            raise ValueError(
                f"SI value {value} out of expected range [{si_min}, {si_max}] for {obj_id.name}"
            )
        scale = (raw_max - raw_min) / (si_max - si_min)
        raw = raw_min + (value - si_min) * scale
        return int(round(raw))

    if obj_id in COMA_SCALED:
        scale = 10 ** COMA_SCALED[obj_id]
        return int(round(value * scale))

    return int(value)
