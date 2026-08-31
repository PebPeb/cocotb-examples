
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
import logging

async def fifo_dump(dut, logger):
  logger.log("Hello")

async def fifo_write(dut, data):
  while not dut.wr_rdy.value:
    await RisingEdge(dut.clk)
  dut.data_in.value = data
  dut.wr.value = 1
  
  await RisingEdge(dut.clk)
  dut.wr.value = 0

@cocotb.test()
async def fifo_tb(dut):
  logger = logging.getLogger("my_testbench")
  
  # Initialize System Clock
  clock = Clock(dut.clk, 10, units="ns")
  cocotb.start_soon(clock.start())
  testData = [0xAA, 0xBB, 0xCC, 0xDD]

  dut.reset.value = 1
  dut.data_in.value = 0x00
  dut.rd.value = 0
  dut.wr.value = 0
  
  await Timer(40, unit="ns")
  
  for data in testData:
    await fifo_write(dut, data)
  
