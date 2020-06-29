from myhdl._Signal import _Signal

def getid(x):
	if isinstance(x, _Signal):
		return x._name
	elif isinstance(x, str):
		return x
	else:
		if x.is_wire():
			s = x.as_wire().name.str()
			if len(s) > 0:
				return s + "::wire"
			else:
				return str(x.get_hash())
		else:
			return str(x.get_hash())

def extend(sig, width):
	if isinstance(sig, _Signal):
		return sig
	else:
		# Assume Yosys compatible API:
		sig.extend_u0(width)

