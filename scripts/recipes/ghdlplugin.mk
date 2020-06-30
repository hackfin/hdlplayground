GHDL_PLUGIN_UPSTREAM = $(HOME)/src/ghdl-yosys-plugin

FIXED_REVISION = 20f45f5

all: install

$(GHDL_PLUGIN_UPSTREAM):
	[ -e $(dir $@) ] || install -d $(dir $@)
	cd $(dir $@) && \
	git clone https://github.com/ghdl/ghdl-yosys-plugin.git $(notdir $@)
	cd $(GHDL_PLUGIN_UPSTREAM) && git checkout $(FIXED_REVISION)

install: $(GHDL_PLUGIN_UPSTREAM)
	sudo $(MAKE) -C $(GHDL_PLUGIN_UPSTREAM) install

test:
	@echo SKIPPING TESTS

.PHONY: install test
