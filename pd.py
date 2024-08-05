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

import sigrokdecode as srd

INSTRUCTIONS = {
    # At this time there is only the instruction set "auto". It's supposed to include the
    # most commonly used commands across multiple chips.
    # More sets may be added if they have conflicting definitions for some instructions.
    'auto' : {0x90: # instruction code
              (3,   # number of address bytes ( |4 if Dual, |8 if Quad)
               0,   # number of dummy bytes ( |4 if Dual, |8 if Quad)
               2,   # data bytes (|1 if MOSI |2 if MISO |4 if Dual, |8 if Quad)
               ['Manufacturer/Device ID', 'MF/Dev ID']  # string list as for put (long to short)
               ),
               
               0x01: (0, 0, 1, ['Write status reg 1', 'Write SR1','W SR1']),
               0x02: (3, 0, 1, ['Write data', 'Write', 'W']),
               0x03: (3, 0, 2, ['Read data', 'Read', 'R']),
               0x04: (0, 0, 0, ['Write Disable', 'WrDis']),
               0x05: (0, 0, 2, ['Read status reg 1', 'Read SR1','R SR1']),
               0x06: (0, 0, 0, ['Write Enable', 'WrEn']),
               0x0B: (3, 1, 2, ['Read fast', 'Readf', 'Rf']),
               0x11: (0, 0, 1, ['Write status reg 3', 'Write SR3','W SR3']),
               0x15: (0, 0, 2, ['Read status reg 3', 'Read SR3','R SR3']),
               0x20: (3, 0, 0, ['4K Erase', 'E4K']),
               0x31: (0, 0, 1, ['Write status reg 2', 'Write SR2','W SR2']),
               0x35: (0, 0, 2, ['Read status reg 2', 'Read SR2','R SR2']),
               0x36: (3, 0, 0, ['Block lock', 'Lock', 'Lk']),
               0x39: (3, 0, 0, ['Block unlock', 'Unlock', 'UnLk']),
               0x3D: (3, 0, 2, ['Read block lock', 'Read lock','R Lk']),
               0x42: (3, 0, 1, ['Write security reg', 'Write Sec', 'W Sec']),
               0x44: (3, 0, 0, ['Erase security reg', 'Erase Sec', 'E Sec']),
               0x4B: (0, 4, 2, ['Read UID', 'UID']),
               0x48: (3, 1, 2, ['Read security reg', 'Read Sec', 'R Sec']),
               0x50: (0, 0, 0, ['Volatile Write Enable', 'VolWrEn']),
               0x52: (3, 0, 0, ['32K Erase', 'E32K']),
               0x5A: (3, 1, 2, ['Read SFDP', 'SFDP']),
               0x60: (0, 0, 0, ['Chip Erase', 'EChip']),
               0x66: (0, 0, 0, ['Enable Reset', 'RSTen']),
               0x75: (0, 0, 0, ['Suspend']),
               0x7A: (0, 0, 0, ['Resume']),
               0x7E: (0, 0, 0, ['Global block lock', 'Global lock', 'Glock']),
               0x98: (0, 0, 0, ['Global block unlock', 'Global unlock', 'Gunlock']),
               0x99: (0, 0, 0, ['Reset', 'RST']),
               0x9F: (0, 0, 2, ['JEDEC ID', 'JEDEC']),
               0xAB: (3, 0, 2, ['Power up/Device ID', 'PowUp/Dev ID']),
               0xB9: (0, 0, 0, ['Power-down']),
               0xC7: (0, 0, 0, ['Chip Erase', 'EChip']),
               0xD8: (3, 0, 0, ['64K Erase', 'E64K']),

               0x3B: (3, 2|4, 2|4, ['Read Dual O', 'DReadO']),

               0x92: (3|4, 1|4, 2|4, ['Mfr/Dev ID Dual I/O', 'IDDual']),
               0xBB: (3|4, 1|4, 2|4, ['Read Dual I/O', 'DReadIO']),

               0x32: (3, 0, 1|8, ['Write Quad', 'WQ']),
               0x6B: (3, 4|8, 2|8, ['Read Quad O', 'ReadQO', 'RQO']),

               0x94: (3|8, 3|8, 2|8, ['Mfr/Dev ID Quad I/O', 'IDQuad']),
               0xEB: (3|8, 3|8, 2|8, ['Read Quad I/O', 'ReadQ','RQ']),
               0x77: (0, 3|8, 1|8, ['Set Burst Wrap', 'Burst Wrap','BWrap']),
               }
}

class ChannelError(Exception):
    pass

class Decoder(srd.Decoder):
    api_version = 3
    id = 'qspi'
    name = 'QUADSPI'
    longname = '(Quad/Dual) Serial Peripheral Interface'
    desc = 'Full-duplex, synchronous, serial bus.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = []
    tags = ['Embedded/industrial']
    channels = (
        {'id': 'clk', 'name': 'CLK', 'desc': 'Clock'},
        {'id': 'mosi', 'name': 'MOSI', 'desc': 'Dual/Quad: IO0, Basic: Master out, Slave in'},
    )
    optional_channels = (
        {'id': 'miso', 'name': 'MISO', 'desc': 'Dual/Quad: IO1, Basic: Master in, Slave out'},
        {'id': 'io2',  'name': 'IO2',  'desc': 'Quad: IO2'},
        {'id': 'io3',  'name': 'IO3',  'desc': 'Quad: IO3'},
        {'id': 'cs',   'name': 'CS',   'desc': 'Chip Select'},
    )
    options = (
        {'id': 'clk_edge', 'desc': 'Sample data on CLK edge', 'default': 'rising',
            'values': ('rising', 'falling')},
        {'id': 'bitorder', 'desc': 'Bit order', 'default': 'msb-first',
            'values': ('msb-first', 'lsb-first')},
        {'id': 'proto', 'desc': 'Command set', 'default': 'auto',
            'values': ('auto',)},
    )
    annotations = (
        ('instr', 'Instruction code'),           # 0
        ('addr1', 'Address byte'),               # 1
        ('addr2', 'Address byte (Dual)'),        # 2
        ('addr4', 'Address byte (Quad)'),        # 3
        ('dummy1', 'Dummy byte'),                # 4
        ('dummy2', 'Dummy byte (Dual)'),         # 5
        ('dummy4', 'Dummy byte (Quad)'),         # 6
        ('master1', 'Master data byte'),         # 7
        ('master2', 'Master data byte (Dual)'),  # 8
        ('master4', 'Master data byte (Quad)'),  # 9
        ('slave1', 'Slave data byte'),           # 10
        ('slave2', 'Slave data byte (Dual)'),    # 11
        ('slave4', 'Slave data byte (Quad)'),    # 12
        ('instruction', 'Instruction'),          # 13
        ('address', 'Address'),                  # 14
        ('master',  'Master data'),              # 15
        ('slave',   'Slave data'),               # 16
        ('garbage', 'Undecodable'),              # 17
    )
    annotation_rows = (
        ('bytes', 'Raw bytes', (0,1,2,3,4,5,6,7,8,9,10,11,12)),
        ('parsed', 'Parsed bytes', (13,14,15,16)),
        ('error', 'Errors', (17,)),
    )
    
    def __init__(self):
        self.reset()

    def reset(self):
        self.samplerate = None        
        self.prev_clk_sample = 0
        self.prev_clk_period = 0
        self.reset_state()
    
    def reset_state(self):
        self.state = 0
        self.bitcount = 0
        self.byte = 0
        self.startsample = 0 # sample of 1st bit of current byte
        self.iolines = 1
        self.expected = 0
        self.address = 0
        self.current_ins = (0,0,0,[''])
        self.data = []
        self.blockstart = 0 # sample of 1st bit of current block (e.g. address)

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.instructions = INSTRUCTIONS[self.options["proto"]]

    def metadata(self, key, value):
       if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def flush_data(self):
        if self.expected == 1: # MOSI
            self.put_data(15, self.data)
        else:
            self.put_data(16, self.data)
        self.data.clear()

    def flush_and_restart(self):
        '''
        Flush any decoded and incompletely decoded data. After this function the next
        bit will be considered the 1st bit of a new instruction code.
        '''
        if self.state == 4: # Data
            self.flush_data()
        
        if self.bitcount > 0:
            self.put(self.startsample, self.samplenum, self.out_ann, [17,[ f"Incomplete: {self.byte:02x}"]])

        self.reset_state()

    def parse_bits(self, io0, io1, io2, io3):
        prev = self.prev_clk_sample
        self.prev_clk_sample = self.samplenum
        self.prev_clk_period = self.samplenum - prev
        
        if self.bitcount == 0:
            self.startsample = self.samplenum
            if self.blockstart == 0:
                self.blockstart = self.samplenum

        self.byte <<= 1
        
        if self.iolines == 2: # DUAL
            self.byte = ((self.byte | io1) << 1) | io0
        elif self.iolines == 4: # QUAD
            self.byte = ((((((self.byte | io3) << 1) | io2) << 1) | io1) << 1) | io0
        else: # normal SPI            
            self.byte |= io0 ^ io1  # XOR MOSI and MISO so we don't need to know which one is active
        
        self.bitcount += self.iolines

    def next_state(self):
        self.blockstart = 0
        ins = self.current_ins[0]
        if self.state < 2 and ins > 0:
            self.address = 0
            self.state = 2
        else:
            ins = self.current_ins[1]
            if self.state < 3 and ins > 0:
                self.state = 3
            else:
                ins = self.current_ins[2]                
                if self.state < 4 and ins > 0:
                    self.data.clear()
                    self.state = 4
                else:                    
                    self.state = 1
                    if self.iolines == 4:
                        ins = 8
                    elif self.iolines == 2:
                        ins = 4
                    else:
                        ins = 0
            
        self.expected = ins & 3
        if ins >= 8:
            self.iolines = 4
        elif ins >= 4:
            self.iolines = 2
        else:
            self.iolines = 1

    def parse_byte(self):
        if self.state == 0:
            self.put(self.startsample, self.samplenum, self.out_ann, [0,[ f"{self.byte:02x}"]])

            if self.byte in self.instructions:
                self.current_ins = self.instructions[self.byte]
                self.put(self.startsample, self.samplenum, self.out_ann, [13, self.current_ins[3]])
                self.next_state()
            else:
                self.state = 1    # Unknown basic SPI bytes (encoded as dummy1)
                self.iolines = 1
        
        elif self.state == 1:  # Unknown basic SPI bytes
            id = 4 + self.iolines - 1 - (self.iolines == 4)
            self.put(self.startsample, self.samplenum, self.out_ann, [id,[ f"{self.byte:02x}"]])

        elif self.state == 2:  # Address
            id = 1 + self.iolines - 1 - (self.iolines == 4)
            self.put(self.startsample, self.samplenum, self.out_ann, [id,[ f"{self.byte:02x}"]])
            self.address =  (self.address << 8) | self.byte
            if self.expected > 1:                
                self.expected -= 1
            else:
                self.put(self.blockstart, self.samplenum, self.out_ann, [14,[ f"Addr: 0x{self.address:06x}", f"A: 0x{self.address:06x}", f"0x{self.address:x}"]])
                self.next_state()

        elif self.state == 3:  # Dummy
            id = 4 + self.iolines - 1 - (self.iolines == 4)
            self.put(self.startsample, self.samplenum, self.out_ann, [id,[ f"{self.byte:02x}"]])
            if self.expected > 1:                
                self.expected -= 1
            else:        
                self.next_state()

        elif self.state == 4:  # Data
            if self.expected == 1: # MOSI
                id = 7
            else: # MISO
                id = 10
            id += self.iolines - 1 - (self.iolines == 4)
            self.put(self.startsample, self.samplenum, self.out_ann, [id,[ f"{self.byte:02x}"]])
            self.data.append(self.byte)
            if len(self.data) > 256:
                self.flush_data()
        
        self.byte = 0

    def put_data(self, id, data):
        hexbytes = " ".join(f"{dat:02x}" for dat in data)
        st = f"{len(data)}[{hexbytes}]"
        self.put(self.blockstart, self.samplenum, self.out_ann, [id,[ st ]])

    def decode(self):
        cond_clk_edge = {0: self.options["clk_edge"][0]}
        cond_cs_rise = {5: 'r'}
        while True:
            if not self.has_channel(5) and self.prev_clk_period > 0 and (self.state != 0 or self.bitcount > 0):
                cond_timeout = {'skip':2 * self.prev_clk_period}
                _, io0, io1, io2, io3, _ = self.wait([cond_clk_edge, cond_cs_rise, cond_timeout])
                if self.matched[2]:
                    print("Timeout")
            else:
                _, io0, io1, io2, io3, _ = self.wait([cond_clk_edge, cond_cs_rise])
            
            force_end = not self.matched[0]  # if we stopped due to anything other than CLK, force end of data

            if force_end:
                self.flush_and_restart()
            else:
                # pins that are not provided have value > 1 whereas valid pins are 0 or 1
                # convert unknown pin value to 0                
                io0 = int(io0 == 1)
                io1 = int(io1 == 1)
                io2 = int(io2 == 1)
                io3 = int(io3 == 1)

                self.parse_bits(io0,io1,io2,io3)

                if self.bitcount == 8:
                    self.parse_byte()
                    self.bitcount = 0
            

