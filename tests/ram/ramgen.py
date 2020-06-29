"""
Dual port RAM test suite

Test case RAM generators module

(c) 2020   <hackfin@section5.ch>
        
LICENSE: GPL v2

"""

from myhdl import *
import subprocess

import sys
sys.path.append("..")

from ivl_cosim import *
from ram import ram_mapper

SRC_PREFIX = ""

# Implementation of the model. Determines what to co-simulate or verify
# against. If the yosys default BRAM pass has implemented a type of
# BRAM, you may set IMPLEMENTATION = IMPLEMENTATION_VHDL_YOSYS_MAPPED
# in the corresponding dpram*.py test case.

IMPLEMENTATION_MYHDL_ONLY, \
IMPLEMENTATION_VHDL_YOSYS_MAPPED, \
IMPLEMENTATION_VERILOG_MODEL, \
IMPLEMENTATION_VHDL_CUSTOM_MAPPED = range(4)

from config import *

# This is the modified simulation libs with vendor specific includes:
LIBFILES = [ ECP5_LIB + "/cells_sim.v", "-I", ECP5_LIB]
# These are the official yosys files with TDP deficiencies
# NOT USED FOR NOW.
# LIBFILES += [ YOSYS_TECHLIBS + "/ecp5/brams_map.v", "-I", YOSYS_TECHLIBS + "/ecp5"]

# LIBFILES += [ ECP5_LIB + "/brams_map.v", "-I", ECP5_LIB]

# If we simulate vendor libs, we need this one:
LIBFILES += [ ECP5_LIB + "/gsr_pur_assign.v"]

class DPport:
	def __init__(self, awidth, dwidth):
		self.clk = Signal(bool(0))
		self.we = Signal(bool(0))
		self.ce = Signal(bool(0))
		self.addr = Signal(modbv()[awidth:])
		self.write = Signal(modbv()[dwidth:])
		self.read = Signal(modbv()[dwidth:])
		# Low/high select:
		self.sel = Signal(intbv()[2:])


@block
def dummy(a, b):
	def worker():
		pass

	return instances()


@block
def meminit(mem, hexfile):
	size = len(mem)
	init_values = tuple([int(ss.val) for ss in mem])
	wsize = len(mem[0])

	@instance
	def initialize():
		for i in range(size):
			mem[i].next = init_values[i]
		yield delay(10)

	return instances()


meminit.verilog_code = """
initial begin
	$$readmemh(\"$hexfile\", $mem, $size);
end
"""

# Disabled memory init code for now

if 0:
	meminit.vhdl_code = """
		type ram_t is array(0 to $size-1) of unsigned($wsize-1 downto 0);

		impure function init_ram() return ram_t is
			file hexfile : text open read_mode is "$hexfile";
			variable l : line;
			variable hw : unsigned($wsize-1 downto 0);
			variable initmem : ram_t := (others => (others => '0'));
		begin
			for i in 0 to $size-1 loop
				exit when endfile(hexfile);
				readline(hexfile, l);
				report "read: " & l.all;
				hread(l, hw);
				initmem(i) := hw;
			end loop;

			return initmem;
		end function;
	"""


@block
def dpram_test(a, b, ent, CLKMODE, HEXFILE = False, verify = False):

	"Entities that are 'required' to work"

	# This is grown into duplicates, due to different clk domains
	# Would not be necessary for the ECP5.
	# ram_raw1 = dual_raw_v0(a, b)

	# This one has a common clock and translates fine
	# ram_raw2 = dual_raw_v0(pa, pb)

	# Both port clocks the same:
	if CLKMODE:
		b.clk.next = a.clk

	ram_tdp = ent(a, b, HEXFILE)

	return instances()

# Clean way to do this would be: determine the proper MyHDL function for the
# mangling.
def map_ports(portdict):
	"Auto-map port class members into mangled names, like: a.clk -> a_clk"
	pmap = { }
	for p in portdict.items():
		for v in p[1].__dict__.items():
			pmap[p[0] + "_" + v[0]] = getattr(p[1], v[0])
	return pmap
		

@block
def ram_v(name, a, b, HEXFILE):
	"Translated MyHDL -> Verilog cosimulation unit"
	params = { }
	signals = { "a": a, "b": b }
	options = { "name" : name, "libfiles" : LIBFILES} 
	portmap = map_ports(signals)
	return setupCosimulationIcarus(options, params, portmap, SRC_PREFIX)


@block
def ram_mapped_vhdl(name, a, b, HEXFILE = False):
	"""Translated MyHDL -> VHDL cosimulation unit, using synth_ecp5
script for default mapping"""

	mapped = name + "_mapped"
	l = ECP5_LIB
	map_cmd = ['yosys', '-m', 'ghdl',
		'-p',
		"""ghdl pck_myhdl_011.vhd %s.vhd -e %s;
			synth_ecp5;
			show -prefix %s -format ps ;
			write_verilog %s.v
 	""" % (name, name, mapped, mapped)]
	subprocess.call(map_cmd)
	params = { }

	signals = { "a": a, "b": b }
	options = { 'name' : mapped, 'tbname' : name, 'libfiles' : LIBFILES} 
	portmap = map_ports(signals)
	return setupCosimulationIcarus(options, params, portmap, SRC_PREFIX)

@block
def ram_mapped_myhdl(name, a, b, HEXFILE = False):
	"""MyHDL based RAM primitive mapping auxiliary"""
	mapped = name + "_mapped"

	files = "%s.vhd pck_myhdl_011.vhd" % name
	top =  name
	ram_mapper.yosys_dpram_mapper(XHDL_PLUGIN,
		"ghdl %s -e %s" % (files, top), files, top, mapped)

	# We don't have this parameter ATM
	# params = { 'ADDR_W' : len(a.addr) }
	params = {}
	signals = { "a": a, "b": b }
	options = { 'name' : mapped, 'tbname' : name, 'libfiles' : LIBFILES} 
	portmap = map_ports(signals)
	return setupCosimulationIcarus(options, params, portmap, SRC_PREFIX)

	
@block
def clkgen(clka, clkb, DELAY_A, DELAY_B):

	@instance
	def clkgen_a():
		while True:
			clka.next = not clka
			yield delay(DELAY_A)

	if DELAY_A == DELAY_B:
		@always_comb
		def assign():
			clkb.next = clka

	else:

		@instance
		def clkgen_b():
			while True:
				clkb.next = not clkb
				yield delay(DELAY_B)


	return instances()

############################################################################
# LIBRARY
#

@block
def dpram_r1w1(a, b, HEXFILE = None, USE_CE = False):
	"Synthesizing one read one write port DPRAM, synchronous read b4 write"
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	if USE_CE:
		@always(a.clk.posedge)
		def porta_proc():
			if a.ce:
				if a.we:
					if __debug__:
						print("Writing to ", a.addr)
					mem[a.addr].next = a.write

		@always(b.clk.posedge)
		def portb_proc():
			if b.ce:
				b.read.next = mem[b.addr]
	else:
		@always(a.clk.posedge)
		def porta_proc():
			if a.we:
				if __debug__:
					print("Writing to ", a.addr)
				mem[a.addr].next = a.write

		@always(b.clk.posedge)
		def portb_proc():
			b.read.next = mem[b.addr]


	return instances()



@block
def dpram_r2w1(a, b, HEXFILE = False, USE_CE = False):
	"Synthesizing two read one write port DPRAM, synchronous read b4 write"
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	if USE_CE:
		@always(a.clk.posedge)
		def porta_proc():
			if a.ce:
				if a.we:
					if __debug__:
						print("Writing to ", a.addr)
					mem[a.addr].next = a.write
				else:
					a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			if b.ce:
				b.read.next = mem[b.addr]
	else:
		@always(a.clk.posedge)
		def porta_proc():
			if a.we:
				if __debug__:
					print("Writing to ", a.addr)
				mem[a.addr].next = a.write
			else:
				a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			b.read.next = mem[b.addr]

	return instances()


@block
def dpram_r2w1_wt(a, b, HEXFILE = False, USE_CE = False):
	"Two read one write port DPRAM, writethrough"
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	if USE_CE:
		@always(a.clk.posedge)
		def porta_proc():
			if a.ce:
				if a.we:
					mem[a.addr].next = a.write
					a.read.next = a.write
				else:
					a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			if b.ce:
				b.read.next = mem[b.addr]
	else:
		@always(a.clk.posedge)
		def porta_proc():
			if a.we:
				mem[a.addr].next = a.write
				a.read.next = a.write
			else:
				a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			b.read.next = mem[b.addr]

	return instances()
	
############################################################################

@block
def dpram_tb(ent, ent_v, CLKMODE, HEXFILE, verify, addrbits):
	"Test with Co-Simulation"

	a = DPport(addrbits, 16)
	b = DPport(addrbits, 16)

	# Both port clocks the same:

	if ent_v:
		# Note: Trace can be flaky when using the wrong verilog version
		# Use a very recent release with MyHDL VPI support.
		ram_tdp_v = ent_v(ent.__name__, a, b, HEXFILE)
	else:
		ram_tdp = ent(a, b, HEXFILE)

 
	inst_clkgen = clkgen(a.clk, b.clk, 10, 11)
	inst_verify = verify(a, b)

	return instances()

def convert(which, MODE, ADDRBITS, trace = False):
	# d = dpram16_init(a, b)

	a = DPport(ADDRBITS, 16)
	b = DPport(ADDRBITS, 16)

	# Test bench currently not used
	dp = dpram_test(a, b, which, MODE, False)
	s = "test_" + which.__name__
	dp.convert("VHDL", name=s)
	dp.convert("Verilog", name=s)

	e = which(a, b)
	e.convert("VHDL", name=which.__name__)
	e.convert("Verilog", name=which.__name__, trace = trace)

	# test_init = dpram_r2w1(a, b, "../sw/bootrom_l.hex")
	# test_init.convert("VHDL")
	# test_init.convert("Verilog")

def testbench(which, verify, MODE=0, ADDRBITS=6):
	"Test bench to co-simulate against conversion/synthesis results"
	if MODE == IMPLEMENTATION_VHDL_YOSYS_MAPPED:
		# Use VHDL RAM model for mapping, co-simulate synthesized Verilog
		# output
		r = ram_mapped_vhdl
	elif MODE == IMPLEMENTATION_VERILOG_MODEL:
		# Use translated Verilog model:
		r = ram_v
	elif MODE == IMPLEMENTATION_VHDL_CUSTOM_MAPPED:
		# Translate using python based memory mapper via pyosys
		r = ram_mapped_myhdl
	else:
		r = None

	tb = dpram_tb(which, r, False, False, verify, ADDRBITS)
	# tb.convert("Verilog", name="tb")
	tb.config_sim(backend = 'myhdl', timescale="1ps", trace=True)
	tb.run_sim(2000)
	tb.quit_sim()


def run(which, verify, MODE=0, ADDRBITS=6):
	import sys
	if len(sys.argv) > 1:
		if sys.argv[1] == '-c':
			convert(which, MODE, ADDRBITS)
		else:
			raise ValueError("Invalid argument")
	else:
		convert(which, MODE, ADDRBITS)
		testbench(which, verify, MODE, ADDRBITS)
