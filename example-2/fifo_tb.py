
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
import logging

testData = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 
            0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
            0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 
            0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F]


async def fifo_write(dut, data):
  dut.data_in.value = data
  dut.wr.value = 1
  
  await RisingEdge(dut.clk)
  dut.wr.value = 0

async def fifo_read(dut):
  dut.rd.value = 1

  await RisingEdge(dut.clk)
  dut.rd.value = 0

@cocotb.test()
async def fifo_tb(dut):
  logger = logging.getLogger("my_testbench")
  
  # Initialize System Clock
  clock = Clock(dut.clk, 10, units="ns")
  cocotb.start_soon(clock.start())
  
  dut.reset.value = 1
  dut.data_in.value = 0x00
  dut.rd.value = 0
  dut.wr.value = 0
  
  await Timer(40, unit="ns")
  await RisingEdge(dut.clk)

  dut.reset.value = 0

  assert dut.empty.value == 1, Exception()

  for data in testData:
    logger.info(data)
    await fifo_write(dut, data)

  await RisingEdge(dut.clk)

  assert dut.full.value == 1, Exception()
  assert dut.empty.value == 0, Exception()
  assert dut.wr_rdy.value == 0, Exception()

  await Timer(40, unit="ns")

  for i in range(32):
    await fifo_read(dut)

  await RisingEdge(dut.clk)

  assert dut.full.value == 0, Exception()
  assert dut.empty.value == 1, Exception()
  assert dut.rd_rdy.value == 0, Exception()

  await Timer(40, unit="ns")

  
