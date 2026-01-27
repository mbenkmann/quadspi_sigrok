QUADSPI Protocol Decoder

A protocol decoder for SPI, Dual SPI and Quad SPI (QSPI) for use with

sigrok/pulseview.

The QUAD SPI (Serial Peripheral Interface) protocol decoder supports synchronous

SPI(-like) protocols with a clock line and 1, 2 or 4 bidirectional data lines.

The first byte (command) determines which lines are used to transmit the

following bytes based on the chosen command set (e.g. SPI Memory).

IO0/MOSI is required. Other IOs are optional.



My Fixes and Compatibility Notes

Python 3.4 Compatibility (Windows PulseView Nightly)

PulseView’s Windows x64 nightly builds currently embed an older Python interpreter (Python 3.4/3.5), which does not support f-strings or several other Python 3.6+ features.

The original used f-strings extensively, causing PulseView to fail with "SyntaxError: invalid syntax"

and silently skip loading the decoder.



What Was Fixed

This updated version:

• 	Replaces all f-strings with ".format()" calls

• 	Removes other Python 3.6 only syntax

• 	Ensures compatibility with PulseView’s embedded Python

• 	Verified that the decoder loads and runs correctly on Windows x64 nightly builds

Verified Working Environment

• 	PulseView 0.5.0git (a Windows x64 nightly)

• 	sigrokdecode API v3

• 	Decoder installed in C:\\Users\\USER\\AppData\\Roaming\\sigrok\\libsigrokdecode\\decoders\\qspi after setting the custom decoder directory environment variable SIGROKDECODE\_DIR

