from myhdl import *

@block
def clkgen(clk, DELAY):
	@always(delay(DELAY))
	def clkgen():
		clk.next = not clk

	return instances()

@block
def up_counter(clk, ce, reset, counter):

	@always_seq(clk.posedge, reset)
	def worker():
		if ce:
			counter.next = counter + 1
		else:
			counter.next = counter

	return instances()

@block
def lfsr8(clk, ce, reset, rval, dout):
	"""LFSR with all states"""
	v = Signal(modbv(rval)[8:])
	fb = Signal(bool())

	@always_seq(clk.posedge, reset)
	def worker():
		if ce == 1:
			v.next = concat(v[6], v[5], v[4], v[3] ^ fb, v[2] ^ fb, v[1] ^ fb, v[0], fb)

	@always_comb
	def assign():
		e = v[7:0] == 0
		fb.next = v[7] ^ e
		dout.next = v

	return instances()

