import os
from myhdl import Cosimulation
import subprocess

HOME = os.environ['HOME']
# Local MyHDL checkout:
MYHDL_COSIMULATION = HOME + "/src/myhdl/myhdl-yosys/cosimulation/icarus"

# The icarus verilog prefix:
IVL_PREFIX = "/usr"
# Where ECP cell simulation libs are found:

try:
	from config import *
except ImportError:
	pass

IVL_MODULE_PATH_ARGS = [ '-M', IVL_PREFIX + '/lib/ivl' ]

def setupCosimulationIcarus(options, parameters, kwargs, \
	srcprefix = "", tbprefix = None):
	try:
		libfiles = options['libfiles']
	except KeyError:
		libfiles = ""

	if not tbprefix:
		tbprefix = srcprefix

	name = options['name']
	if 'tbname' in options:
		tbname = options['tbname']
	else:
		tbname = name

	objfile = "%s.o" % name
	if os.path.exists(objfile):
	    os.remove(objfile)

	analyze_cmd = ['iverilog' ]
	analyze_cmd += ['-s', "tb_" + tbname]
	analyze_cmd += ['-D', "mixed_hdl"]

	src = srcprefix + '%s.v' % name
	tbsrc = tbprefix + 'tb_%s.v' % tbname
	
	for p in parameters.keys():
		analyze_cmd += [ '-P', 'tb_%s.%s=%s' % (tbname, p, parameters[p]) ]

	analyze_cmd += ['-o', objfile, src, tbsrc]
	analyze_cmd += libfiles
	print(analyze_cmd)
	subprocess.call(analyze_cmd)
	simulate_cmd = ['vvp', '-m', MYHDL_COSIMULATION + '/myhdl.vpi']
	simulate_cmd += IVL_MODULE_PATH_ARGS
	simulate_cmd += [objfile]
	c = Cosimulation(simulate_cmd, **kwargs)
	c.name = name
	return c


