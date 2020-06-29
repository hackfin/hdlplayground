"""
Dual port RAM test suite

(c) 2020   <hackfin@section5.ch>
        
LICENSE: GPL v2

Version with H/L select, instances two memory units.

See ramgen for configuration of 'IMPLEMENTED' variable

"""

from myhdl import *

from ramgen import *

IMPLEMENTED = IMPLEMENTATION_VHDL_CUSTOM_MAPPED

@block
def dpram_r2w1_hl(a, b, HEXFILE = None, USE_CE = False):
	"H/L select variant"

	ah, al, bh, bl = [ DPport(len(a.addr), len(a.write)/2) for i in range(4) ]

	@always_comb
	def assign():
		ah.clk.next = a.clk
		al.clk.next = a.clk
		bh.clk.next = b.clk
		bl.clk.next = b.clk
		ah.we.next = a.we & a.sel[0]
		al.we.next = a.we & a.sel[1]
		bh.we.next = b.we & b.sel[0]
		bl.we.next = b.we & b.sel[1]

		ah.addr.next = a.addr
		al.addr.next = a.addr
		bh.addr.next = b.addr
		bl.addr.next = b.addr

		ah.write.next = a.write[16:8]
		al.write.next = a.write[8:0]
		bh.write.next = b.write[16:8]
		bl.write.next = b.write[8:0]

		a.read.next = concat(ah.read, al.read)
		b.read.next = concat(bh.read, bl.read)

	ram_h = dpram_r2w1(ah, bh)
	ram_l = dpram_r2w1(al, bl)



	return instances()

@block
def dpram_r2w1_hl_verify(a, b):
	"Verification TB, read before write"
	@instance
	def stim():
		a.ce.next = 1
		b.ce.next = 1
		a.sel.next = 0b11
		b.sel.next = 0b11

		for i in range(2 ** len(a.addr)):
			yield a.clk.posedge
			a.addr.next = i
			a.write.next = 0xface
			yield a.clk.negedge
			a.we.next = 1
			yield a.clk.negedge
			a.we.next = 0
	
			# On read-after-write, data can not yet be ready on port A:
			if a.read == 0xface:
				raise ValueError("Mismatch (transparent) A / 0")

			b.addr.next = i
			# Data is ready on port B:
			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xface:
				raise ValueError("Mismatch B / 1")

			yield a.clk.posedge
			a.addr.next = i
			a.write.next = 0xdead
			yield a.clk.negedge
			a.we.next = 1
			yield a.clk.negedge
			a.we.next = 0
	
			# On read-after-write, data can not yet be ready on port A:
			if a.read == 0xdead:
				raise ValueError("Mismatch (transparent) A / 1")

			b.addr.next = i
			# Data is ready on port B:
			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xdead:
				raise ValueError("Mismatch B / 2")


		print("Simulation Done")

	return instances()


if __name__ == '__main__':
	run(dpram_r2w1_hl, dpram_r2w1_hl_verify, IMPLEMENTED, 9)

