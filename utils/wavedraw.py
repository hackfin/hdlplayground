# Auxiliaries to display a waveform

import sys

from  Verilog_VCD import parse_vcd

def to_wave(desc, trigger, delta, context = None):
	def from_bitvec(x, wtype = None, context = None):
		if x[0] == 'x':
			return ('x', "")
		else:
			try:
				return ('=', "%02x " % (int(x, 2)))
			except ValueError:
				return ('x', "")

	def from_string(x, wtype, context = None):
		if wtype == 'string':
			if context != None:
				d = context[1]
				if x in d:
					c = d[x]
				else:
					c = context[0]
					d[x] = c
					if c == 5:
						context[0] = 3
					else:
						context[0] = c + 1

				return ('%d' % c, [x,])
			else:
				return ('=', [x,])
		else:
			raise ValueError("unhandled string")

		
	def from_bit(x, wtype = None, context = None):
		return (x, x)
	
	def to_none_bit(x):
		return '.', None
	
	def to_none_data(x):
		if x == None:
			return '.', None
		else: 
			return '.', None
		
	

	l, wform, wtype, spec = desc

	a = ''

	# Create a simple color context, starting with code '3'
	context = [3, {} ]

	# If we have a delta config, override default delta
	if spec and 'delta' in spec:
		delta = spec['delta']

	if wtype == 'string':
		from_val = from_string
		to_none = to_none_data
		b = []
	else:
		b = ''

		if l > 1:
			from_val = from_bitvec
			to_none = to_none_data
		else:
			from_val = from_bit
			to_none = to_none_bit

	trigger = trigger[1]

	if wform == trigger:
		for i in trigger:
			val = from_val(i[1])
			a += val[0]
			b += val[1]
		return a, b
	
	cur = trigger[0][0]
	next_evt = wform[0][0] # First event
	j = 0
	n = len(wform)
	lastval = wform[0][1]

	last = trigger[-1][0] + 100
	for i in trigger:
		cur = i[0]
		if cur >= next_evt - delta:
			val = from_val(wform[j][1], wtype, context)
			a += val[0]
			if val[1]:
				b += val[1]
				lastval = val[1]
			j += 1
			if j == n:
				next_evt = last			   
			else:
				next_evt = wform[j][0]
		else:
			v = to_none(lastval)
			a += v[0]
			if v[1]:
				b += v[1]

	# print(a, "--", b)
	return a, b


def vcd2wave(vcdfile, trigname, cfg = None, delta = 4):
	"""Simple conversion of VCD file.
Requires passing of the name of the trigger signal, normally the highest
running clock in the system. The signals are sampled according to that
clock and returned as schematic waveform for wavedrom display"""
	vcd = parse_vcd(vcdfile)

	vcd_dict = {}
	if cfg == None:
		for nm, t in vcd.items():
			trace = t['nets'][0]
			identifier = trace['hier'] + '.' + trace['name']
			s = int(trace['size'])
			tp = trace['type']
			if 'tv' in t:
				vcd_dict[identifier] = (s, t['tv'], tp, None)
			else:
				print("Warning: no timevalue for %s" % identifier)
				vcd_dict[identifier] = (s, [(0, 'x')], tp, None)
				print(t)
	else:
		for nm, t in vcd.items():
			trace = t['nets'][0]
			identifier = trace['hier'] + '.' + trace['name']
			s = int(trace['size'])
			tp = trace['type']
			if 'tv' in t:
				if identifier in cfg:
					vcd_dict[identifier] = (s, t['tv'], tp, cfg[identifier])
				elif identifier == trigname:
					vcd_dict[trigname] = (s, t['tv'], tp, None)
			else:
				print("Warning: no timevalue for %s" % identifier)

	wdwave = {}
	signals = []
	try:
		trigger = vcd_dict[trigname] # Get trigger signal
	except KeyError:
		print("Choose one of:")
		for n, _ in vcd_dict.items():
			print(n)
		raise ValueError("Signal not found")
	
	for n, wave in vcd_dict.items():

		try:
			wdwaveform, data = to_wave(wave, trigger, delta)
		except AssertionError:
			print("Failed to create waveform for '%s'" % n)

		if data != "":
			trace = { 'name' : n, 'wave' : wdwaveform, 'data' : data}
		else:
			trace = { 'name' : n, 'wave' : wdwaveform}

		signals.append(trace)
		
	wdrom = { 'signal' : signals}	 
	return wdrom


