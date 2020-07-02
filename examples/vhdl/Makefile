# Makefile for blink example
#
# 2011, Martin Strubel <hackfin@section5.ch>
#
#

DUTIES = blinky blinky2

work-obj93.cf: blink.vhdl blink2.vhdl
	# Import our above example into the current 'work' cache 
	ghdl -i blink.vhdl
	ghdl -i blink2.vhdl

blinky: work-obj93.cf
	# Analyze, elaborate and build an exe from the top level entity 'blink' 
	ghdl -m blinky

blinky2: work-obj93.cf
	ghdl -m blinky2

test.vcd: blinky
	./blinky --vcd=test.vcd --stop-time=40us # Run the simulation and output a wave file

test2.vcd: blinky2
	./blinky2 --vcd=test2.vcd --stop-time=40us

all: $(DUTIES) test.vcd test2.vcd

.PHONY: clean all

clean:
	rm -f work-obj93.cf
	rm -f *.o $(DUTIES)
	rm -f *.vcd
