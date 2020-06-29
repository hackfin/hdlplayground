"""
Dual port RAM test suite

(c) 2020   <hackfin@section5.ch>
        
LICENSE: GPL v2

See ramgen for configuration of 'IMPLEMENTED' variable

Currently false-detected with one asynchronous READ port, synthesises
into TRELLIS_DPR16X4 primitives

"""


from ramgen import *

IMPLEMENTED = IMPLEMENTATION_VERILOG_MODEL

@block
def dpram_r2w1_verify(a, b):
	"Verification TB, read before write"
	@instance
	def stim():
		a.ce = 1
		b.ce = 1

		for i in range(10):
			a.addr.next = i
			b.addr.next = i
			a.write.next = 0xface
			yield a.clk.negedge
			a.we.next = 1

			yield a.clk.negedge
			a.we.next = 0

			if a.read != 0xface:
				raise ValueError("Mismatch 'transparent' A / 0")

			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xface:
				raise ValueError("Mismatch A -> B / 0")

		
			yield a.clk.negedge
			a.write.next = 0xdead
			a.we.next = 1
			yield a.clk.negedge

			a.we.next = 0

			yield a.clk.posedge
			
			# Read 'transparent' (writethrough):
			if a.read != 0xdead:
				raise ValueError("Mismatch 'transparent' A / 1")

			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xdead:
				raise ValueError("Mismatch A -> B / 1")

		print("Simulation Done")

	return instances()

if __name__ == '__main__':
	run(dpram_r2w1_wt, dpram_r2w1_verify, IMPLEMENTED, 7)
