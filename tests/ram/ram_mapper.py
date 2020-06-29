# Python based RAM mapper
#
# <hackfin@section5.ch>
#
#

# FIXME: Eliminate libyosys
# from pyosys import libyosys as ys

from myhdl.conversion import yshelper as yh

from config import *

import sys
import map_bram
import dprams

PID = yh.PID
# Careful with _ID:
_ID = yh.ys.IdString

YOSYS_ECP5_LIBS = YOSYS_TECHLIBS + "/ecp5"

NOTICE = "\033[7;35m"
OFF = "\033[0m"


PARAM_TRANSLATE = { 
	"MEMID"           : None,
    "RD_CLK_ENABLE"   : str,
    "RD_CLK_POLARITY" : str,
    "RD_PORTS"        : int,
    "RD_TRANSPARENT"  : str,
    "ABITS"           : int,
    "SIZE"            : int,
    "WIDTH"           : int,
    "WR_CLK_ENABLE"   : str,
    "WR_CLK_POLARITY" : str,
    "WR_PORTS"        : int,
}

def notice(msg):
	print(NOTICE + msg + OFF)

def to_levels(v):
	s = ""
	for i in v:
		print(i)

def to_mem_impl_description(c):
	"Translates a memory cell info into a descriptor dictionary"
	d = {}

	conn = c.connections_
	parameters = c.parameters

	for it in parameters.items():
		k, v = it
		k = k.str()[1:]
		try:
			t = PARAM_TRANSLATE[k]
			if t == int:
				d[k] = v.as_int()
			elif t == str:
				d[k] = v.as_string()
			else:
				d[k] = v

		except KeyError:
			d[k] = v.as_string()

	nwp = d['WR_PORTS']
	nrp = d['RD_PORTS']
	width = d['WIDTH']
	abits = d['ABITS']

	for it in conn.items():
		k, v = it
		k = k.str()[1:]
		if k == 'WR_DATA':
			d[k] = [ v.extract(j * width, width) for j in range(nwp) ]
		elif k == 'RD_DATA':
			d[k] = [ v.extract(j * width, width) for j in range(nrp) ]
		elif k == 'WR_ADDR':
			d[k] = [ v.extract(j * abits, abits) for j in range(nwp) ]
		elif k == 'RD_ADDR':
			d[k] = [ v.extract(j * abits, abits) for j in range(nrp) ]
		elif k in [ 'WR_CLK', 'WR_EN' ]:
			d[k] = [ v.extract(j) for j in range(nwp) ]
		elif k in [ 'RD_CLK', 'RD_EN' ]:
			d[k] = [ v.extract(j) for j in range(nrp) ]
		else:
			d[k] = v

	return d

import inspect

def lineno():
	return inspect.currentframe().f_back.f_lineno

def mem_replace_cell(module, i, mem, mem_impl, nl, primitive_id):
	repl_cell = module.addCell(PID("meminst%d" % i), _ID(primitive_id))
	print("Added cell", repl_cell)

	width, abits = mem_impl['WIDTH'], mem_impl['ABITS']
	print("Phys. Data width: %d, Address width: %d" % (width, abits))
	nrp = mem_impl['RD_PORTS']

	param = {
		PID('INIT') :  yh.ys.Const("000000000000000"),
		PID('CFG_DBITS') :  yh.ys.Const(width, 8),
		PID('CFG_ABITS') :  yh.ys.Const(abits, 8)
	}

	repl_cell.parameters = param
	
	for k in nl.items():
		wirename = PID(k[0])
		if k[1]:
			s = k[1][0]
			if isinstance(s, yh.ys.SigSpec):
				name = wirename.str()
				wid = PID(k[0] + "%d" % i)
				# wid = ys.new_id(__name__, lineno(), k[0])
				w = module.addWire(wid, s.size())
				sw = yh.ys.SigSpec(w)

				if k[1][1] == 'out':
					print("Connect output", wirename.str())
					repl_cell.setPort(wirename, yh.ys.SigSpec(w))
					module.connect(s, sw)
				else:
					print("Connect input", name)
					repl_cell.setPort(wirename, sw)
					module.connect(sw, s)

			elif isinstance(s, str):
				if s in [ '0', '1' ]:
					c = yh.ys.Const.from_string(s)
					repl_cell.setPort(wirename, yh.ys.SigSpec(c))
				else:
					raise ValueError("Unsupported string value")

	module.remove(mem)


def map_tdp_memory(module, i, m, pid):
	"Map true dual port memory"

	mem_impl = to_mem_impl_description(m)
	pmaps = map_bram.analyze_cell(mem_impl, map_bram.ECP5_DPRAM)
	notice("Mapping...")
	# print(pmaps)
	nl = map_bram.map_cell(mem_impl, pmaps, map_bram.TARGET_TDP_RAM)
	for n in nl.items():
		# print(n)
		if n[1]:
			if n[1][1] == 'out':
				print(n[0], " => ", map_bram.getid(n[1][0]))
			else:
				print(n[0], " <= ", map_bram.getid(n[1][0]))
		else:
			print(n[0], " <= (others => 'X')")

	print("#### DONE ####")

	mem_replace_cell(module, i, m, mem_impl, nl, pid)

def dump_entity(c):
	conn = c.connections_
	parameters = c.parameters


	for k in parameters.items():
		i, v = k
		if i != PID("INIT"):
			print(k)

	print(40 * "-")

	for k in conn.keys():
		sig = conn[k]
		# print(k, sig, sig.size())

def yosys_dpram_mapper(plugin, cmd, files, top, mapped):
	design = yh.Design()
	TECHMAP = 1

	notice("Running YOSYS custom mapper")
	if plugin:
		yh.ys.load_plugin(plugin, [])

	print("Running command '%s'" % cmd)
	design.run(cmd)

	if not TECHMAP: # Without techmap
		design.run("read_verilog ecp5_dp16kd.v")

	# Pull these files from upstream:
	libdir = YOSYS_ECP5_LIBS

	design.run("read_verilog -lib %s/cells_sim.v %s/cells_bb.v" % (libdir, libdir))

	design.run("hierarchy -check -top %s" % (top))

	modules = design.design.selected_whole_modules_warn()
	for module in modules:
		# print(dir(module))
		memories = []
		for cell in module.selected_cells():
			if cell.type == "$mem":
				print(20 * "-")
				print("Found memory")
				dump_entity(cell)
				memories.append(cell)


	module = modules[0]
	for i, m in enumerate(memories):
		pid = "$__ECP5_DP16KD"
		# When not using techmap, bind to local blackbox definition:
		if not TECHMAP:
			pid = "\\" + pid

		map_tdp_memory(module, i, m, pid)

	design.run("write_ilang pre_map.il")

	# These we customize:
	customlib = ECP5_LIB

	if TECHMAP:
		notice("RUNNING TECH MAP PASS")
		design.run("stat")
		# a = input("HIT RETURN")
		design.run("debug techmap -map %s/brams_map.v" % customlib)
		# a = input("HIT RETURN")
		design.run("techmap -map %s/cells_map.v" % customlib)


	design.run("flatten")	
	design.run("hierarchy -check")	
	design.run("clean")	
	design.run("show -prefix %s -format ps" % mapped)	
	design.run("write_verilog -norename %s.v" % (mapped))
