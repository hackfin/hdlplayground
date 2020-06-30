FROM hackfin/myhdl_testing:jupyosys

RUN sudo apt-get update; sudo apt-get install -y \
	yosys-ghdl=0.9-testing-hpg yosys-techlibs=0.9-testing-hpg ghdl  ghdl-libs \
	tcl-dev libffi-dev libboost-python-dev libreadline-dev \
  libboost-filesystem-dev

COPY . /home/pyosys/work

RUN sudo chown -R pyosys work; make -f work/scripts/recipes/ghdlplugin.mk all

