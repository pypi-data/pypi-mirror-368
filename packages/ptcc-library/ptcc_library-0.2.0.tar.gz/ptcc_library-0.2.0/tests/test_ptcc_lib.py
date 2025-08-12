import unittest
from ptcc_library import *

class TestTecLibrary20(unittest.TestCase):

    def test(self):
        msg = PtccMessage()
        msg.reset()
        assert msg.receive_status == PtccMessageReceiveStatus.NOT_BEGAN

        errors = 0
        try:
            msg.append_byte(ord('b'))
        except ValueError as ve:
            errors += 1
        assert msg.receive_status == PtccMessageReceiveStatus.NOT_BEGAN

        errors = 0
        try:
            msg.append_byte(START_BYTE)
        except Exception:
            errors += 1
        assert msg.receive_status == PtccMessageReceiveStatus.IN_PROGRESS
        assert errors == 0

        errors = 0
        try:
            for i in range(0, 40):
                msg.append_byte(ord('a'))
        except ValueError as ve:
            errors += 1
        assert errors == 0

        msg.reset()
        errors = 0
        test_data = b'$050000040F01#'
        try:
            for byte in test_data:
                msg.append_byte(int(byte))
        except:
            errors += 1
        assert errors == 0
        assert msg.receive_status == PtccMessageReceiveStatus.FINISHED
        obj = "hello"
        try:
            obj = msg.to_ptcc_object()
        except ValueError:
            errors += 1
        assert errors == 0
        assert isinstance(obj, PtccObject)

        msg.reset()
        errors = 0
        test_data = b'$050000040F02#'  # Wrong CRC
        try:
            for byte in test_data:
                msg.append_byte(int(byte))
        except ValueError:
            errors += 1
        assert errors == 0
        try:
            obj = msg.to_ptcc_object()
        except ValueError:
            errors += 1
        assert errors == 1

        msg.reset()
        obj = "hello"
        errors = 0
        test_data = b'$1800000E1813000501182B000500D80B#'
        try:
            msg.append_bytes(test_data)
        except ValueError:
            errors += 1
        try:
            obj = msg.to_ptcc_object()
        except ValueError:
            errors += 1
        assert isinstance(obj, PtccObject)
        assert errors == 0
        assert obj.is_container
        assert len(obj.objects) == 2
        assert obj.objects[0].obj_id == PtccObjectID.PTCC_CONFIG_VARIANT.value
        assert obj.objects[1].obj_id == PtccObjectID.PTCC_CONFIG_NO_MEM_COMPATIBLE.value

        msg.reset()
        msg = PtccMessage.generate_msg_get_config()
        expected_msg = [ord(x) for x in "$050000040F01#"]
        assert msg.raw_message == expected_msg

        msg = PtccMessage(create_get_ptcc_message(PtccObjectID.GET_PTCC_MONITOR))
        expected_msg = [ord(x) for x in "$05200004C500#"]
        assert msg.raw_message == expected_msg

    def test_receiver(self):
        receiver = PtccMessageReceiver(clear_all_after_receive=False)

        test_data = b'$050000040F02#'  # Wrong CRC

        for byte in test_data:
            receiver.add_byte(byte)

        assert len(receiver.errors) == 1

        receiver.reset()
        test_data = b'$1800000E1813000501182B000500D80B#'

        for byte in test_data:
            receiver.add_byte(byte)

        assert len(receiver.errors) == 0
        assert len(receiver.messages) == 1
        assert len(receiver.objects) == 1

        receiver.reset()
        test_data = b'qqqqq$1800000E1813000501182B000500D80B#aaaaaa$050000040F01#aaaaaaaaaaaaa'

        receiver.add_bytes(test_data)

        assert len(receiver.errors) == 0
        assert len(receiver.messages) == 2
        assert len(receiver.objects) == 2

        receiver.reset()
        test_data = b'qqqqq$1800000E1813000501ghr182B000500D80B#aaaaaa$050000040F01#aaaaaaaaaaaaa'

        receiver.add_bytes(test_data)

        assert len(receiver.errors) == 3
        assert len(receiver.messages) == 2
        assert len(receiver.objects) == 2

    def test_ptcc_protocol_callbacks(self):

        # Example usage:
        def my_config_variant_callback(value, user_data):
            # Process the configuration variant
            print("Config variant callback:", value)
            print(f"User data is: {user_data}")

        def my_monitor_status_callback(value):
            print("Monitor status callback:", value)

        # Assuming these IDs are defined as constants or enum values, e.g.:
        PTCC_MONITOR_STATUS = PtccObjectID.PTCC_MONITOR_STATUS.value

        handler = PtccMessageReceiver()
        handler.register_callback(CallbackPtccObjectID.PTCC_CONFIG_VARIANT, my_config_variant_callback, "Present")
        handler.register_callback(PTCC_MONITOR_STATUS, my_monitor_status_callback)

        # Then later, when an object is received:
        class DummyObj:
            # Dummy class for demonstration
            def __init__(self, id, data, value):
                self.obj_id = id
                self.data = data
                self.value = value
                self.is_container = False

        handler.obj_received_callback(DummyObj(PtccObjectID.PTCC_CONFIG_VARIANT.value, "variant_data", 0))
        handler.obj_received_callback(DummyObj(PTCC_MONITOR_STATUS, "status_data", 1))


if __name__ == "__main__":
    unittest.main()
