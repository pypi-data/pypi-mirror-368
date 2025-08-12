# PTCC Communication Framework

A modular Python library for communicating with PTCC hardware devices over a custom byte-based protocol. It supports message construction, parsing, throttled I/O communication, device detection, and callback-based event handling.

- Project Homepage: https://gitlab.com/vigophotonics/ptcc-library
- Download Page: https://pypi.org/project/ptcc-library
- Product Page: https://vigophotonics.com/product/programmable-smart-ptcc-01-tec-controller-series/


## Features
- Communication with PTCC devices and modules
- Simplified message generation for communication
- Interface abstraction for serial or custom communication backends
- Auto-detection of PTCC device/module types (NOMEM, MEM, LAB_M)
- Full PtccObject and PtccMessage encoding/decoding support
- Callback registration for received object IDs
- Values retrieving and setting in SI units

## Documentation
Full documentation can be found at https://ptcc-library.readthedocs.io/


## Installation
`ptcc_library` can be installed from PyPI:
``pip install ptcc-library``

Detailed information can be found at https://pypi.org/project/ptcc-library


## Quick Start Example

### 1. Detect and Connect to Device
To communicate with your hardware, the library first needs an active communication channel. 
This is typically a `serial` port object that you create and configure. 
You pass this communication object to the `detect_device()` function. 
If a compatible `device` is found, the function returns a device object, which is your primary interface for all further interactions.

```python
from ptcc_library import detect_device
import serial

with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
        device = detect_device(comm=ser)
```

### 2. Register Callbacks
A callback is a function you write that is automatically executed when a specific piece of data arrives from the device. 
This allows you to react to incoming information asynchronously. 
You link your function to a data ID using `device.receiver.register_callback()`. 
You can also pass an optional `context` argument, which is a static value supplied to your callback, useful for identifying a measurement's source.

```python
from ptcc_library import CallbackPtccObjectID


def name_callback(name):
        print("Module Name:", name)


def temp_callback(temp, context):
        print(f"Temperature: {temp} K ({context})")


device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN_NAME, name_callback)
device.receiver.register_callback(CallbackPtccObjectID.MODULE_BASIC_PARAMS_T_DET, temp_callback, "live")
```

### 3. Send Messages

The `device` object provides straightforward methods for sending commands and requests to the hardware, typically named `write_msg_*`. 
For example, `write_msg_get_module_iden()` requests identity information, while `write_msg_set_temperature()` commands the device to change its temperature. 
When the device responds, it will trigger the corresponding callbacks you registered.

```python
device.write_msg_get_module_iden()
device.write_msg_set_temperature(value_in_kelvins=230)
```


### 4. Handle Incoming Data

The library does not read from the serial port on its own. 
Your application is responsible for reading incoming bytes and feeding them to the library's receiver. 
You must implement a loop that reads data and passes it to `device.receiver.add_byte()` or `device.receiver.add_bytes()`. 
As the receiver processes data, it automatically finds complete messages and triggers the appropriate callbacks.


```python
while True:
    byte = ser.read(1)
    if byte:
        if device.receiver.add_byte(byte[0]) == PtccMessageReceiveStatus.FINISHED:
                print("New message received")
```


### Handle Containers

The device communicates by sending data in packets called containers.
Each container holds a collection of related data objects.
To process full data as it arrives, you must register a callback function that will be executed when a specific type of container is received.

Container IDs include:

* `DEVICE_IDEN`
* `MODULE_IDEN`
* `PTCC_CONFIG`
* `PTCC_MONITOR`
* `MODULE_BASIC_PARAMS`
* `MODULE_LAB_M_MONITOR`
* `MODULE_LAB_M_PARAMS`

```python

def iden_callback(objects):
    for o in objects:
        print(f"{o.name} = {o.value}")
device.receiver.register_callback(CallbackPtccObjectID.DEVICE_IDEN, iden_callback)
```

## Product Page

<p align="center">
  <a href="https://vigophotonics.com/product/programmable-smart-ptcc-01-tec-controller-series/">
    <img src="docs/source/_static/PTCC-01-TEC-controllers-2048x1051.jpg" alt="Photo of the PTCC-01 TEC Controller" width="400">
  </a>
</p>

PTCC-01 is a series of programmable, precision, low-noise thermoelectric cooler controllers.
They are designed to operate with VIGO infrared detection modules.
- Product Page: https://vigophotonics.com/product/programmable-smart-ptcc-01-tec-controller-series/



## 👤 Author

**Wojciech Szczytko**  
[wszczytko@vigo.com.pl](mailto:wszczytko@vigo.com.pl)  
GitLab: [@wszczytko1](https://gitlab.com/wszczytko1)
        [@wszczytko](https://gitlab.com/wszczytko)
        [@wszczytk](https://gitlab.com/wszczytk)