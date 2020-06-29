`resetall
`timescale 1 ns / 1 ps

`celldefine


module gsr_pur_assign(gsr_sig, pur_sig);
	output gsr_sig, pur_sig;

reg pur;
reg gsr;

assign gsr_sig = gsr;
assign pur_sig = pur;

initial begin
pur = 1'b0; // Low active
gsr = 1'b0;
#10
pur = 1'b1;
gsr = 1'b1;
end
endmodule
`endcelldefine
