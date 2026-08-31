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

  assign empty = size_count == 0 ? 1 : 0;
  assign full = size_count == WIDTH ? 1 : 0;

  assign rd_valid = rd & rd_rdy & ~empty;
  assign wr_valid = wr & wr_rdy & ~full;

  always @(clk, reset) begin
    if(reset) begin
      for (i = 0; i < DEPTH-1; i=i+1) begin
        mem[i] <= 0;
      end    
      rd_idx <= 0;
      wr_idx <= 0;
      size_count <= 0;
    end 
    else if(posedge clk) begin
      if (wr_valid) begin
        mem[rd_idx] <= data_in;
        wr_idx <= (wr_idx + 1) == WIDTH ? 0 : (wr_idx + 1);
      end

      if (rd_valid) begin
        data_out <= mem[rd_idx];
        rd_idx <= (rd_idx + 1) == WIDTH ? 0 : (rd_idx + 1);
      end

      if (rd_valid and wr_valid) begin
        size_count <= size_count;
      end
      else if (rd_valid) begin
        size_count <= size_count - 1;
      end
      else if (wr_valid) begin
        size_count <= size_count + 1;
      end
    end
  end
endmodule
