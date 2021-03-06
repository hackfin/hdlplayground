#!/usr/bin/env python3

def write_bus_ports(f, ada_bits, adb_bits, dia_bits, dib_bits, doa_bits, dob_bits):
	ada_conn = [".ADA%d(%s)" % (i, ada_bits[i]) for i in range(len(ada_bits))]
	adb_conn = [".ADB%d(%s)" % (i, adb_bits[i]) for i in range(len(adb_bits))]
	dia_conn = [".DIA%d(%s)" % (i, dia_bits[i]) for i in range(len(dia_bits))]
	dib_conn = [".DIB%d(%s)" % (i, dib_bits[i]) for i in range(len(dib_bits))]
	doa_conn = [".DOA%d(%s)" % (i, doa_bits[i]) for i in range(len(doa_bits))]
	dob_conn = [".DOB%d(%s)" % (i, dob_bits[i]) for i in range(len(dob_bits))]
	print("    %s," % ",\n".join(ada_conn), file=f)
	print("    %s," % ",\n".join(adb_conn), file=f)
	print("    %s," % ",\n".join(dia_conn), file=f)
	print("    %s," % ",\n".join(dib_conn), file=f)
	print("    %s," % ",\n".join(doa_conn), file=f)
	print("    %s," % ",\n".join(dob_conn), file=f)

def write_bus_ports_pdp(f, adw_bits, adr_bits, di_bits, do_bits, be_bits):
	adw_conn = [".ADW%d(%s)" % (i, adw_bits[i]) for i in range(len(adw_bits))]
	adr_conn = [".ADR%d(%s)" % (i, adr_bits[i]) for i in range(len(adr_bits))]
	di_conn = [".DI%d(%s)" % (i, di_bits[i]) for i in range(len(di_bits))]
	do_conn = [".DO%d(%s)" % (i, do_bits[i]) for i in range(len(do_bits))]
	be_conn = [".BE%d(%s)" % (i, be_bits[i]) for i in range(len(be_bits))]
	print("    %s," % ", ".join(adw_conn), file=f)
	print("    %s," % ", ".join(adr_conn), file=f)
	print("    %s," % ", ".join(di_conn), file=f)
	print("    %s," % ", ".join(do_conn), file=f)
	print("    %s," % ", ".join(be_conn), file=f)

with open("techlibs/ecp5/bram_conn_1.vh", "w") as f:
	ada_bits = ["A1ADDR[%d]" % i for i in range(14)]
	adb_bits = ["B1ADDR[%d]" % i for i in range(14)]
	dia_bits = ["A1WRITE[0]"] + ["1'b0" for i in range(17)]
	dib_bits = ["B1WRITE[0]"] + ["1'b0" for i in range(17)]
	doa_bits = ["A1READ[0]"]
	dob_bits = ["B1READ[0]"]
	write_bus_ports(f, ada_bits, adb_bits, dia_bits, dib_bits, doa_bits, dob_bits)

with open("techlibs/ecp5/bram_conn_2.vh", "w") as f:
	ada_bits = ["1'b0"] + ["A1ADDR[%d]" % i for i in range(13)]
	adb_bits = ["1'b0"] + ["B1ADDR[%d]" % i for i in range(13)]
	dia_bits = ["A1WRITE[%d]" % i for i in range(2)] + ["1'b0" for i in range(16)]
	dib_bits = ["B1WRITE[%d]" % i for i in range(2)] + ["1'b0" for i in range(16)]
	doa_bits = ["A1READ[%d]" % i for i in range(2)]
	dob_bits = ["B1READ[%d]" % i for i in range(2)]
	write_bus_ports(f, ada_bits, adb_bits, dia_bits, dib_bits, doa_bits, dob_bits)

with open("techlibs/ecp5/bram_conn_4.vh", "w") as f:
	ada_bits = ["1'b0", "1'b0"] + ["A1ADDR[%d]" % i for i in range(12)]
	adb_bits = ["1'b0", "1'b0"] + ["B1ADDR[%d]" % i for i in range(12)]
	dia_bits = ["A1WRITE[%d]" % i for i in range(4)] + ["1'b0" for i in range(14)]
	dib_bits = ["B1WRITE[%d]" % i for i in range(4)] + ["1'b0" for i in range(14)]
	doa_bits = ["A1READ[%d]" % i for i in range(4)]
	dob_bits = ["B1READ[%d]" % i for i in range(4)]
	write_bus_ports(f, ada_bits, adb_bits, dia_bits, dib_bits, doa_bits, dob_bits)

with open("techlibs/ecp5/bram_conn_9.vh", "w") as f:
	ada_bits = ["1'b0", "1'b0", "1'b0"] + ["A1ADDR[%d]" % i for i in range(11)]
	adb_bits = ["1'b0", "1'b0", "1'b0"] + ["B1ADDR[%d]" % i for i in range(11)]
	dia_bits = ["A1WRITE[%d]" % i for i in range(9)] + ["1'b0" for i in range(9)]
	dib_bits = ["B1WRITE[%d]" % i for i in range(9)] + ["1'b0" for i in range(9)]
	doa_bits = ["A1READ[%d]" % i for i in range(9)]
	dob_bits = ["B1READ[%d]" % i for i in range(9)]
	write_bus_ports(f, ada_bits, adb_bits, dia_bits, dib_bits, doa_bits, dob_bits)

with open("techlibs/ecp5/bram_conn_18.vh", "w") as f:
	ada_bits = ["A1WE", "A1WE", "1'b0", "1'b0"] + ["A1ADDR[%d]" % i for i in range(10)]
	adb_bits = ["B1WE", "B1WE", "1'b0", "1'b0"] + ["B1ADDR[%d]" % i for i in range(10)]
	dia_bits = ["A1WRITE[%d]" % i for i in range(18)]
	dib_bits = ["B1WRITE[%d]" % i for i in range(18)]
	doa_bits = ["A1READ[%d]" % i for i in range(18)]
	dob_bits = ["B1READ[%d]" % i for i in range(18)]
	write_bus_ports(f, ada_bits, adb_bits, dia_bits, dib_bits, doa_bits, dob_bits)

with open("techlibs/ecp5/bram_conn_36.vh", "w") as f:
	adw_bits = ["A1ADDR[%d]" % i for i in range(9)]
	adr_bits = ["1'b0", "1'b0", "1'b0", "1'b0", "1'b0"] + ["B1ADDR[%d]" % i for i in range(9)]
	di_bits = ["A1WRITE[%d]" % i for i in range(36)]
	do_bits = ["B1READ[%d]" % (i + 18) for i in range(18)] + ["B1READ[%d]" % i for i in range(18)]
	be_bits = ["A1EN[%d]" % i for i in range(4)]
	write_bus_ports_pdp(f, adw_bits, adr_bits, di_bits, do_bits, be_bits)
