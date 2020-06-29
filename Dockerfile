FROM hackfin/myhdl_testing:jupyosys

RUN sudo apt-get update; sudo apt-get install -y \
	yosys-ghdl=0.9-testing-hpg yosys-techlibs=0.9-testing-hpg ghdl  ghdl-libs \
	tcl-dev libffi-dev libboost-python-dev libreadline-dev \
  libboost-filesystem-dev

COPY scripts/recipes/ghdlplugin.mk /home/pyosys

RUN sudo chown pyosys ghdlplugin.mk; make -f ghdlplugin.mk all

