FROM hackfin/myhdl_testing:jupyosys

RUN sudo apt-get update; sudo apt-get install -y \
	yosys-ghdl=0.9-testing-hpg yosys-techlibs=0.9-testing-hpg ghdl  ghdl-libs \
	tcl-dev libffi-dev libboost-python-dev libreadline-dev \
  libboost-filesystem-dev

# Hot fix for javascript error
RUN sudo pip3 install --upgrade git+https://github.com/hackfin/nbwavedrom.git

COPY . /home/pyosys/work

RUN sudo chown -R pyosys work; make -f work/scripts/recipes/ghdlplugin.mk all

