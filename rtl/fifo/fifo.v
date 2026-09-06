// FIFO

module fifo #(
  WIDTH=8,
  DEPTH=32
) (
  input  wire clk, 
  input  wire reset,
  input  wire [WIDTH-1:0] data_in,
  output reg  [WIDTH-1:0] data_out,
  output wire wr_rdy,
  output wire rd_rdy,
  input  wire rd,
  input  wire wr,
  output wire full,
  output wire empty
);
  
  reg [WIDTH-1:0] mem [0:DEPTH-1];

  reg [$clog2(DEPTH)-1:0] rd_idx = 0;
  reg [$clog2(DEPTH)-1:0] wr_idx = 0;
  reg [$clog2(DEPTH):0] size_count = 0;

  wire rd_valid;
  wire wr_valid;

  // Initialize Memory to Zero
  integer i = 0;
  initial begin
    for (i = 0; i < DEPTH-1; i=i+1) begin
      mem[i] = 0;
    end    
  end

  assign empty = size_count == 0 ? 1 : 0;
  assign full = size_count == DEPTH ? 1 : 0;

  assign wr_rdy = ~full;
  assign rd_rdy = ~empty;

  assign rd_valid = rd & rd_rdy;
  assign wr_valid = wr & wr_rdy;

  always @(posedge clk, posedge reset) begin
    if(reset) begin  
      rd_idx <= 0;
      wr_idx <= 0;
      size_count <= 0;
      data_out <= 0;
    end 
    else if(clk) begin
      if (wr_valid) begin
        mem[wr_idx] <= data_in;
        wr_idx <= (wr_idx + 1) == DEPTH ? 0 : (wr_idx + 1);
      end

      if (rd_valid) begin
        data_out <= mem[rd_idx];
        rd_idx <= (rd_idx + 1) == DEPTH ? 0 : (rd_idx + 1);
      end

      if (rd_valid && ~wr_valid) begin
        size_count <= size_count - 1;
      end
      else if (wr_valid && ~rd_valid) begin
        size_count <= size_count + 1;
      end
    end
  end


  `ifdef COCOTB_SIM
  initial begin
    $dumpfile ("fifo.vcd");
    $dumpvars (0);
  end
  `endif
endmodule
