"""
Dual port RAM test suite

(c) 2020   <hackfin@section5.ch>
        
LICENSE: GPL v2

See ramgen for configuration of 'IMPLEMENTED' variable

Synthesises: VHDL: TRELLIS_DPR16X4 primitives

"""

from ramgen import *

IMPLEMENTED = IMPLEMENTATION_MYHDL_ONLY

@block
def dpram_r2w1_raw(a, b, HEXFILE = False):
	"""Synthesizes for ECP5_DP16KD in Verilog, but not in VHDL"""
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]
	addr_a, addr_b = [ Signal(modbv(0)[len(a.addr):]) for i in range(2) ]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	@always(a.clk.posedge)
	def port_a_proc():
		if a.ce:
			addr_a.next = a.addr
			if a.we:
				mem[a.addr].next = a.write

	@always(b.clk.posedge)
	def port_b_proc():
		if b.ce:
			addr_b.next = b.addr

	@always_comb
	def assign():
	  a.read.next = mem[addr_a];
	  b.read.next = mem[addr_b];

	return instances()

@block
def dpram_r2w1_raw_verify(a, b):
	"Verification TB, read after write"
	@instance
	def stim():
		a.ce.next = 1
		b.ce.next = 1

		a.addr.next = 0
		b.addr.next = -1
		a.write.next = 0x2000

		yield a.clk.negedge
		a.we.next = 1
		yield a.clk.negedge
		a.we.next = 0

		for i in range(1, 20):

			a.write.next = 0x2000 + i
			a.addr.next = i
			yield a.clk.negedge
			a.we.next = 1
			yield a.clk.negedge
			a.we.next = 0

			b.addr.next = i - 1
			yield b.clk.posedge

			# Must not yet be expected data
			if b.read == 0x2000 + i - 1:
				raise ValueError("Mismatch B / 0")
			yield b.clk.posedge
			# Now must be expected data
			if b.read != 0x2000 + i - 1:
				raise ValueError("Mismatch B / 1")


		print("Simulation Done")

	return instances()

if __name__ == '__main__':

	# Make sure to use a minimum of 7 address bits to map to a
	# DP16KD primitive
	run(dpram_r2w1_raw, dpram_r2w1_raw_verify, IMPLEMENTED, 7)
