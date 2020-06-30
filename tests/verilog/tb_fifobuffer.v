`timescale 1ns/10ps

module tb_fifobuffer;

reg wren;
reg [7:0] idata;
wire iready;
wire [7:0] odata;
wire oready;
reg rden;
wire err;
reg reset;
reg clk = 0;

initial begin
 
    $from_myhdl(
        wren,
        idata,
        rden,
        reset,
        clk
    );
    $to_myhdl(
        iready,
        oready,
        err,
        odata
    );
end


initial begin
   $dumpfile("fifobuf.vcd");
    // $dumpvars(0,tb_fifobuffer_mapped);
    $dumpvars;
end

FifoBuffer dut(
    wren,
    idata,
    rden,
    reset,
    clk,
    iready,
    odata,
    oready,
    err
);

endmodule
