# Attempts to map BRAM with various test scenarios

import dprams

from sigtypes import *

WO, RO, RW, ASYNC = [1, 2, 3, 4]

MARK_MAPPED = 0x80


ECP5_DPRAM = {
	'groups'           : 2,
	'ports'            : [1, 1],
	'wrmode'           : [RW, RW],
	'transp'           : [2, 3],
	'clocks'           : [2, 3],
	'clkpol'           : [2, 3]
}

ECP5_PDPRAM = {
	'groups'           : 2,
	'ports'            : [1, 1],
	'wrmode'           : [WO, RO],
	'transp'           : [2, 3],
	'clocks'           : [2, 3],
	'clkpol'           : [2, 3]
}

# A target (abstract) RAM primitive:
TARGET_TDP_RAM = {
	"CLK2"               : "input",
	"CLK3"               : "input",
    "A1ADDR"             : "input",
	"A1READ"             : "output",
	"A1WRITE"            : "input",
	"A1EN"               : "input",
	"B1ADDR"             : "input",
	"B1READ"             : "output",
	"B1WRITE"            : "input",
	"B1EN"               : "input"
}

def clkdomain_key(which, cell, j):
	"Generate a key for a port's clock domain"
	k = which + "_CLK"
	try:
		print(k, cell[k])
	except KeyError:
		print(cell)

	s = cell[k][j]
	# If it's a wire, get its name:
	wid = getid(s)
	idstring = wid + '_' + cell[k + '_POLARITY'][j]
	idstring += "_" + cell[k + "_ENABLE"][j]
	return idstring

def analyze_cell(cell, rules):
	print(60 * "=")
	print("Processing %s" % (cell['MEMID']))

	nports = rules['groups']
	portinfos = [ dprams.PortInfo(rules, i) for i in range(nports) ]

	wr_ports = cell['WR_PORTS']
	rd_ports = cell['RD_PORTS']

	print("Instance has %d write, %d read ports" % (wr_ports, rd_ports))

	# Collect ports:
	portmap = { }

	for j in range(rd_ports):
		clk_sigid = clkdomain_key("RD", cell, j)
		rp = ['RD_CLK', 'RD_ADDR', 'RD_EN' ]
		a = [ cell[n][j] for n in rp ]
		v = cell['RD_DATA'][j]
		if clk_sigid in portmap:
			portmap[clk_sigid][0] += v
		else:
			flags = RO
			if cell['RD_CLK_ENABLE'][j] == '0':
				flags |= ASYNC
			a.append(v)
			portmap[clk_sigid] = [ a, flags ]
	
	for j in range(wr_ports):
		clk_sigid = clkdomain_key("WR", cell, j)
		a = [ cell[n][j] for n in ['WR_CLK', 'WR_ADDR' ] ]
		v = [ cell[n][j] for n in ['WR_EN', 'WR_DATA' ] ]
		if clk_sigid in portmap:
			if a[1] != portmap[clk_sigid][0][1]:
				print("Possibly different address sources, ignoring for now")
				#raise TypeError("Shared R/W port can not have different address sources")
			portmap[clk_sigid][0] += v
			portmap[clk_sigid][1] |= WO
		else:
			a += v
			portmap[clk_sigid] = [ a, WO ]

	for i, pi in enumerate(portinfos):
		# print 40 * "-"
		# print "TRY :", pi

		# The wrmode flags are assumed sorted in descending order:
		items = portmap.items()
		for p in sorted(items, key=lambda x:x[1]):
			k = p[0]
			m = portmap[k][1]
			# Start mapping with highest capabilities:
			if m <= pi.wrmode and (m & pi.wrmode) == m:
				pi.mapto(k)
				portmap[k][1] |= MARK_MAPPED # Mark as mapped
				break

	for p in portmap.keys():
		if portmap[p][1] & MARK_MAPPED == 0:
			# TODO:
			# In this case we can attempt to 'grow' ports
			raise dprams.UnmappedError("Unmapped ports left: %s" % p)

	return [ portmap, portinfos ]

def UNDEFINED(size):
	return None


def map_cell(cell, portmaps, interface):
	"Map I/Os, return net list"

	index = 1

	dwidth = cell['WIDTH']

	new_dwidth = 18
	new_awidth = 10

	cell['WIDTH'] = new_dwidth
	cell['ABITS'] = new_awidth

	# print(portmaps)

	netlist = {}
	for p in portmaps[1]:
		k = p.mapped_port
		inst = portmaps[0][k]
		# print inst
		portid = p.getId() + "%d" % index 
		sigs = inst[0]
		flags = inst[1]
		netlist[ "CLK%d" % p.clocks ] = [ sigs[0], 'in' ]

		extend(sigs[1], new_awidth)
		netlist[ portid + "ADDR"] = [ sigs[1], 'in' ]
		i = 2
		if flags & RO:
			netlist[ portid + "RE"] = [sigs[i], 'in']
			i += 1
			extend(sigs[i], new_dwidth)
			netlist[ portid + "READ"] = [sigs[i], 'out']
			i += 1
		else:
			netlist[ portid + "RE"] = [ "0", 'in' ]
			netlist[ portid + "READ"] = UNDEFINED(new_dwidth)

		if flags & WO:
			netlist[ portid + "WE"] = [sigs[i], 'in']
			i += 1
			extend(sigs[i], new_dwidth)
			netlist[ portid + "WRITE"] = [sigs[i], 'in']
			i += 1
		else:
			netlist[ portid + "WE"] =  ["0", 'in']
			netlist[ portid + "WRITE"] = UNDEFINED(new_dwidth)

	
	return netlist

if __name__ == "__main__":
	for i in dprams.__all__:
		pmaps = analyze_cell(i, ECP5_DPRAM)
		nl = map_cell(i, pmaps, TARGET_TDP_RAM)

		print("============= MAP ==============")
		for n in nl.items():
			if n[1]:
				print(n[0], getid(n[1][0]))
			else:
				print(n)

	for i in [ dprams.impl_r1w1_dc ]:
		pm = analyze_cell(i, ECP5_PDPRAM)

	pm = analyze_cell(dprams.impl_r2w1_dc, ECP5_PDPRAM)

	try:
		pm = analyze_cell(dprams.impl_r2w2_dc, ECP5_PDPRAM)
		raise TypeError("This RAM can not be mapped")
	except dprams.UnmappedError:
		pass
