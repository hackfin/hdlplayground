# RAM templates
#
# This file is part of the gensoc package
#
# 2016, <hackfin@section5.ch>
#
# 2020: Adapted for yosys BRAM model

WIDTH = 16
DEPTH = 7

from myhdl import Signal, intbv


a_clk, b_clk     = [ Signal(bool()) for i in range(2) ]
a_addr, b_addr   = [ Signal(intbv()[DEPTH:]) for i in range(2) ]
a_read, b_read   = [ Signal(intbv()[WIDTH:]) for i in range(2) ]
a_write, b_write = [ Signal(intbv()[WIDTH:]) for i in range(2) ]
a_we, b_we       = [ Signal(bool()) for i in range(2) ]
a_re, b_re       = [ Signal(bool()) for i in range(2) ]

# Extra case for granular writes:
h_we, l_we       = [ Signal(bool()) for i in range(2) ]

# Assign some ID:
for sig in [ "a_clk", "b_clk", "a_addr", "b_addr", "a_read",
	"b_read", "a_write", "b_write", "a_we", "b_we", "a_re", "b_re",
	"h_we", "l_we" ]:

	locals()[sig]._name = sig

impl_r1w1_dc = {
	"MEMID"           : "impl_r1w1_dualclock",
    "RD_CLK_ENABLE"   : "1",
    "RD_CLK_POLARITY" : "1",
    "RD_PORTS"        : 1,
    "RD_TRANSPARENT"  : "00",
    "SIZE"            : 1 << DEPTH,
    "WIDTH"           : WIDTH,
    "WR_CLK_ENABLE"   : '1',
    "WR_CLK_POLARITY" : '1',
    "WR_PORTS"        : 1,
	# wires
    "RD_ADDR"         : [ a_addr ],
    "RD_CLK"          : [ a_clk ],
    "RD_DATA"         : [ a_read ],
    "RD_EN"           : [ a_re ],
    "WR_ADDR"         : [ b_addr ],
    "WR_CLK"          : [ b_clk ],
    "WR_DATA"         : [ b_write ],
    "WR_EN"           : [ b_we for i in range(WIDTH) ]
	
}

impl_r2w1_dc = {
	"MEMID"           : "impl_r2w1_dualclock",
    "RD_CLK_ENABLE"   : "11",
    "RD_CLK_POLARITY" : "11",
    "RD_PORTS"        : 2,
    "RD_TRANSPARENT"  : "00",
    "SIZE"            : 128,
    "WIDTH"           : WIDTH,
    "WR_CLK_ENABLE"   : '1',
    "WR_CLK_POLARITY" : '1',
    "WR_PORTS"        : 1,
	# wires
    "RD_ADDR"         : [ a_addr, b_addr ],
    "RD_CLK"          : [ a_clk, b_clk ],
    "RD_DATA"         : [ a_read, b_read ],
    "RD_EN"           : [ a_re, b_re ],
    "WR_ADDR"         : [ a_addr ],
    "WR_CLK"          : [ a_clk ],
    "WR_DATA"         : [ a_write ],
    "WR_EN"           : [ a_we for i in range(WIDTH) ]
	
}

impl_r2w1_hl_dc = {
	"MEMID"           : "impl_r2w1_dualclock",
    "RD_CLK_ENABLE"   : "11",
    "RD_CLK_POLARITY" : "11",
    "RD_PORTS"        : 2,
    "RD_TRANSPARENT"  : "00",
    "SIZE"            : 128,
    "WIDTH"           : WIDTH,
    "WR_CLK_ENABLE"   : '1',
    "WR_CLK_POLARITY" : '1',
    "WR_PORTS"        : 1,
	# wires
    "RD_ADDR"         : [ a_addr, b_addr ],
    "RD_CLK"          : [ a_clk, b_clk ],
    "RD_DATA"         : [ a_read, b_read ],
    "RD_EN"           : [ a_re, b_re ],
    "WR_ADDR"         : [ a_addr ],
    "WR_CLK"          : [ a_clk ],
    "WR_DATA"         : [ a_write ],
    "WR_EN"           : [ h_we for i in range(WIDTH >> 1) ] + [ l_we for i in range(WIDTH >> 1) ]
	
}

impl_r2w1_dc10 = impl_r2w1_dc.copy()

impl_r2w1_dc10['MEMID'] =   "impl_r2w1_dualclock_b"
impl_r2w1_dc10['WR_ADDR'] = [ b_addr ]
impl_r2w1_dc10['WR_CLK']  = [ b_clk ]
impl_r2w1_dc10['WR_DATA'] = [ b_write ]
impl_r2w1_dc10['WR_EN']   = [ b_we for i in range(WIDTH) ]

impl_r2w2_dc = {
	"MEMID"           : "impl_r2w2_dualclock",
    "RD_CLK_ENABLE"   : "11",
    "RD_CLK_POLARITY" : "11",
    "RD_PORTS"        : 2,
    "RD_TRANSPARENT"  : "00",
    "SIZE"            : 128,
    "WIDTH"           : WIDTH,
    "WR_CLK_ENABLE"   : '11',
    "WR_CLK_POLARITY" : '11',
    "WR_PORTS"        : 2,
	# wires
    "RD_ADDR"         : [ a_addr, b_addr ],
    "RD_CLK"          : [ a_clk, b_clk ],
    "RD_DATA"         : [ a_read, b_read ],
    "RD_EN"           : [ a_re, b_re ],
    "WR_ADDR"         : [ a_addr, b_addr ],
    "WR_CLK"          : [ a_clk, b_clk ],
    "WR_DATA"         : [ a_write, b_write ],
	# These must be concatenated in the right order:
    "WR_EN"           : [ a_we for i in range(WIDTH) ] + [ b_we for i in range(WIDTH)  ]
	
}

MODES = [ 'NONE', 'WO', 'RO', 'RW' ]


__all__ =  [ impl_r2w1_dc, impl_r2w1_dc10,  impl_r2w2_dc ]


class PortInfo:
	def __init__(self, desc, i):
		self.wrmode = desc['wrmode'][i]
		self.clkpol = desc['clkpol'][i]
		self.clocks = desc['clocks'][i]
		self.transp = desc['transp'][i]
		self.ports  = desc['ports'][i]
		self._index = i
		self.mapped_port = None

	def __repr__(self):
		return "<Port %s %s clkid=%d>" % (self.getId(), MODES[self.wrmode], self.clocks)

	def mapto(self, i):
		print("Map %s to port[%s]" % (repr(self), i))
		self.mapped_port = i

	def ismapped(self):
		return self.mapped_port != None

	def getId(self):
		return chr(self._index + ord('A'))	


class UnmappedError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return(repr(self.value))
