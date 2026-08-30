
import cocotb
from cocotb.triggers import Timer, RisingEdge
import logging

class myTestException(Exception):
  def __init__(self, operation: str) -> None:
    """Testing Exception"""
    self.operation = operation
    super().__init__(f"My Exception in {operation}")


@cocotb.test()
async def mux_tb(dut):
  logger = logging.getLogger("my_testbench")

  dut.a.value = 1
  dut.b.value = 0
  dut.sel.value = 0
  
  await Timer(10, unit="ns")
  assert dut.y.value == dut.a.value, myTestException("1")
  
  dut.sel.value = 1
  await Timer(10, unit="ns")
  assert dut.y.value == dut.b.value, myTestException("2")
  
  await Timer(10, unit="ns")


