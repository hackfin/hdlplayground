# Bitfields implementation
#
# taken from @hls python HDL generator by section5.ch
#

import operator

from myhdl.conversion.yshelper import Implementation, ConstSignal, yosys
from myhdl import GeneratorClass, blackbox, inference

	
# These operators are supported:
_IMPLEMENT_OPS = {
        '__add__': operator.add,
        '__sub__': operator.sub,
        '__and__': operator.and_,
        '__or__' : operator.or_,
        '__xor__': operator.xor
    }

def binop_wrapper(c):
    "Decorator wrapper to implement the above operations for the decorated class"
    for n, op in _IMPLEMENT_OPS.items():
        setattr(c, n, c._make_binop(op))
    return c   

@binop_wrapper
class BinopIntResult(GeneratorClass):
	__name__ = "GeneratorClass Binop"
	@classmethod 
	def _make_binop(this, op):
		def binop(self, other):
			res = op(int(self), int(other))
			return BitVal(res)
		return binop

class BitVal(BinopIntResult):
	def __init__(self, val):
		self.val = val
		
	def __int__(self):
		return self.val
		
	
class Bitfield(BinopIntResult):
	__slots__ = [ 'lsb', 'msb', 'val' ]
	
	def __init__(self, lsb, msb, val = 0xff):
		self.lsb = lsb
		self.msb = msb
		self.val = val 

	def __int__(self):
		return self.as_int()
		
	def implement(self, node, a):
		"""This implementation function is mandatory for a GeneratorClass
		object. For yosys, it creates logic 'inline' to infer the slicing
		behaviour."""
		
		@blackbox
		def bitslice(val):
			"""A bit slicing and comparator logic. Note that the `val` argument is a yosys
			Signal object, unlike a HLS signal object from a @hls/@component entity"""
			@inference(yosys)
			def implementation(module, sm):
				n = self.msb - self.lsb + 1
				sm.q = module.addSignal(None, 1)
				portion = val.extract(self.lsb, n)
				c = ConstSignal(self.val, n)
				identifier = yosys.new_id(node, "cmp")
				module.addEq(identifier, c, portion, sm.q, False)

			return implementation
		
		return bitslice(a)
	   
	def as_mask(self):
		"Returns integer bit mask for logical integer operations"
		return ( ~(~0 << (self.msb - self.lsb + 1)) << self.lsb )

	def as_int(self):
		"Returns shifted bitfield value as int"
		return self.val << self.lsb
	
	def as_slice(self):
		"Returns slice from Bitfield for signal extraction"
		return slice(self.msb + 1, self.lsb)
	
	def __call__(self, v):
		"Implements match function for integer and classes with `.val` member"
		if isinstance(v, int):
			return ( (v & self.as_mask()) >> self.lsb == self.val )
		else:	 
			return v[self.as_slice()] == self.val
