import os

HOME = os.environ['HOME']

MYHDL_COSIMULATION = HOME + "/src/myhdl/myhdl-yosys/cosimulation/icarus"
YOSYS_TECHLIBS  = "/usr/share/yosys"
ECP5_LIB = "lib/techlibs/ecp5"
XHDL_PLUGIN = "/usr/share/yosys/plugins/ghdl.so"

import sys
sys.path.append("..")
