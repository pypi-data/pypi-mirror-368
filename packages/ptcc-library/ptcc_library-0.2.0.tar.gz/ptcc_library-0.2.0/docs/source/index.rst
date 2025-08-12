.. ptcc_library documentation master file, created by
   sphinx-quickstart on Tue May 27 12:37:46 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ptcc_library documentation
==========================


This is a modular Python library for communicating with PTCC hardware devices over a custom byte-based protocol. It supports message construction, parsing, throttled I/O communication, device detection, and callback-based event handling.

* Project Homepage: https://gitlab.com/vigophotonics/ptcc-library
* Download Page: https://pypi.org/project/ptcc-library
* Product Page: https://vigophotonics.com/product/programmable-smart-ptcc-01-tec-controller-series/

Features
--------
* Communication with PTCC devices and modules
* Simplified message generation for communication
* Interface abstraction for serial or custom communication backends
* Auto-detection of PTCC device/module types (NOMEM, MEM, LAB_M)
* Full PtccObject and PtccMessage encoding/decoding support
* Callback registration for received object IDs
* Values retrieving and setting in SI units

You can find source code at `git <https://gitlab.com/vigophotonics/ptcc-library>`_.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   ptcc_library.Overview
   ptcc_library.Installation
   ptcc_library.Examples
   ptcc_library

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`