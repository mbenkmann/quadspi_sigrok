== Sigrok/Pulseview Protocol decoder for SPI, Dual SPI and Quad SPI (QSPI) == 

The QUAD SPI (Serial Peripheral Interface) protocol decoder supports synchronous
SPI(-like) protocols with a clock line and 1, 2 or 4 bidirectional data lines.
The first byte (command) determines which lines are used to transmit the
following bytes based on the chosen command set (e.g. SPI Memory).

CLK is required. IO0/MOSI is required. Other IOs are optional.
