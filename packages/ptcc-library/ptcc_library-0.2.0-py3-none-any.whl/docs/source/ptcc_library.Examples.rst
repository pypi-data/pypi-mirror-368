==========
 Examples
==========


Detect and Connect to Device
----------------------------
To communicate with your hardware, the library first needs an active communication channel.
This is typically a serial port object that you create and configure.
Example uses `serial <https://pyserial.readthedocs.io/en/latest/shortintro.html#opening-serial-ports>`_

You pass this communication object to the ``detect_device()`` function.
If a compatible device is found on that channel, the function will return a ``device`` object.
This object is your primary interface for all further interactions, such as sending commands and registering callbacks.


    >>> from ptcc_library import detect_device
    >>> import serial
    >>> with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    >>>     device = detect_device(comm=ser)

Register Callbacks
------------------
A callback is a function you write that is automatically executed when a specific piece of data arrives from the device.
This allows you to react to incoming information asynchronously without having to constantly poll for it.

You link your function to a data ID using ``device.receiver.register_callback()``.
You can also pass an optional ``context`` argument, which is a static value that will be supplied to your callback every time it's called.
This is useful for identifying the source or purpose of a measurement.

    >>> from ptcc_library import CallbackPtccObjectID
    >>> def name_callback(name):
            print("Module Name:", name)
    >>> def temp_callback(temp, context):
            print(f"Temperature: {temp} K ({context})")
    >>> device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN_NAME, name_callback)
    >>> device.receiver.register_callback(CallbackPtccObjectID.MODULE_BASIC_PARAMS_T_DET, temp_callback, "live")

Send Messages
-------------
The ``device`` object provides straightforward methods for sending commands and requests to the hardware.
These methods are typically named ``write_msg_*``.

For example, ``write_msg_get_module_iden()`` requests the module's identity information,
while`` ``write_msg_set_temperature()`` commands the device to change its temperature setpoint.
When the device responds to these messages, it will trigger the corresponding callbacks you have registered.

    >>> device.write_msg_get_module_iden()
    >>> device.write_msg_set_temperature(value_in_kelvins=230)


Handle Incoming Data
--------------------
The library does not read from the serial port on its own.
Your application is responsible for reading incoming bytes and feeding them to the library's receiver for processing.

You must implement a loop to read data from your communication channel.
Each byte read should be passed to the ``device.receiver.add_byte()`` method. You can also use ``device.receiver.add_bytes()`` for passing multiple bytes.
This method processes the byte/bytes and returns a status.  As it processes the data, it will automatically find complete messages and trigger any corresponding callbacks you have registered.
A return value of ``PtccMessageReceiveStatus.FINISHED`` indicates that a complete message has just been processed and its associated callback has been triggered.

    >>> while True:
    >>>     byte = ser.read(1)
    >>>     if byte:
    >>>         if device.receiver.add_byte(byte[0]) == PtccMessageReceiveStatus.FINISHED:
    >>>                 print("New message received")

Handle Containers
-----------------
The device communicates by sending data in packets called containers.
Each container holds a collection of related data objects.
To process full data as it arrives, you must register a callback function that will be executed when a specific type of container is received.

Container IDs include:

* ``DEVICE_IDEN``
* ``MODULE_IDEN``
* ``PTCC_CONFIG``
* ``PTCC_MONITOR``
* ``MODULE_BASIC_PARAMS``
* ``MODULE_LAB_M_MONITOR``
* ``MODULE_LAB_M_PARAMS``


    >>> def iden_callback(objects):
    >>>     for o in objects:
    >>>         print(f"{o.name} = {o.value}")
    >>> device.receiver.register_callback(CallbackPtccObjectID.DEVICE_IDEN, iden_callback)
