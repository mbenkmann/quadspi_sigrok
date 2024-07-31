##
## This file is (NOT YET) part of the libsigrokdecode project.
##
## Copyright (C) 2024 Matthias S. Benkmann <matthias@winterdrache.de>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

'''
The QUAD SPI (Serial Peripheral Interface) protocol decoder supports synchronous
SPI(-like) protocols with a clock line and 1, 2 or 4 bidirectional data lines.
The first byte (command) determines which lines are used to transmit the
following bytes based on the chosen command set (e.g. SPI Memory)

IO0/MOSI is required. Other IOs are optional.
'''

from .pd import Decoder
