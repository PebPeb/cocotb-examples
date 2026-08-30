// FIFO


module fifo #(
  WIDTH=8,
  DEPTH=32
) (
  input  clk, 
  input  reset,
  input  [WIDTH-1:0] data_in,
  output [WIDTH-1:0] data_out,
  output wr_rdy,
  output rd_rdy,
  input  rd,
  input  wr,
  output full,
  output empty
);
  
  reg [WIDTH-1:0] mem [0:DEPTH-1];

  reg [$clog2(WIDTH)-1:0] rd_idx = 0;
  reg [$clog2(WIDTH)-1:0] wr_idx = 0;
  reg [$clog2(WIDTH):0] size_count = 0;

  wire rd_valid;
  wire wr_valid;

  // Initialize Memory to Zero
  integer i = 0;
  initial begin
    for (i = 0; i < DEPTH-1; i=i+1) begin
      mem[i] <= 0;
    end    
  end

  assign 

  assign empty = size_count == 0 ? 1 : 0;
  assign full = size_count == WIDTH ? 1 : 0;

  assign rd_valid = rd & rd_rdy & ~empty;
  assign wr_valid = wr & wr_rdy & ~full;

  always @(clk, reset) begin
    if(reset) begin
      for (i = 0; i < DEPTH-1; i=i+1) begin
        mem[i] <= 0;
      end    
    end 
    else if(posedge clk) begin
      if (wr_valid) begin
        
      end
      if (rd_valid) begin

      end
    end
  end
endmodule
