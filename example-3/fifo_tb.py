
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge

import pyuvm
from pyuvm import *

class fifo_transaction(uvm_sequence_item):
  def __init__(self, name="fifo_transaction"):
    super().__init__(name)
    self.write = False
    self.read = False
    self.data = 0

class fifo_sequence(uvm_sequence):
  async def body(self):
    for value in [100, 200, 300]:
      transaction = fifo_transaction()
      
      transaction.write = True
      transaction.data = value
      
      await self.start_item(transaction)
      await self.finish_item(transaction)

class fifo_driver(uvm_driver):
  def __init__(self, name, parent):
    super().__init__(name, parent)

  def build_phase(self):
    self.dut = ConfigDB().get(self, "", "dut")

  async def run_phase(self):
    while True:
      transaction = await self.seq_item_port.get_next_item()
      if transaction.write:
        self.dut.data_in.value = transaction.data
        self.dut.wr.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.wr.value = 0
      elif transaction.read:
        self.dut.rd.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.rd.value = 0
      await self.seq_item_port.item_done()
      
      
class fifo_monitor(uvm_monitor):
  def __init__(self, name, parent):
    super().__init__(name, parent)
    self.ap = uvm_analysis_port("ap", self)

  def build_phase(self):
    self.dut = ConfigDB().get(self, "", "dut")

  async def run_phase(self):
    while True:
      await RisingEdge(self.dut.clk)
      if self.dut.rd.value and not self.dut.empty.value:
        transaction = fifo_transaction()
        transaction.read = True
        transaction.data = int(self.dut.data_out.value)
        self.ap.write(transaction)

class fifo_scoreboard(uvm_subscriber):
  def __init__(self, name, parent):
    super().__init__(name, parent)
    self.expected = []

  def write(self, transaction):
    if transaction.write:
      self.expected.append(transaction.data)
    elif transaction.read:
      expected = self.expected.pop(0)
      assert transaction.data == expected, \
        f"Expected {expected}, got {transaction.data}"

class fifo_env(uvm_env):
  def __init__(self, name, parent):
    super().__init__(name, parent)

  def build_phase(self):
    self.driver = fifo_driver("driver", self)
    self.monitor = fifo_monitor("monitor", self)
    self.scoreboard = fifo_scoreboard("scoreboard", self)

    self.sequencer = uvm_sequencer(
      "sequencer",
      self
    )

  def connect_phase(self):
    self.driver.seq_item_port.connect(
      self.sequencer.seq_item_export
    )

    self.monitor.ap.connect(
      self.scoreboard.analysis_export
    )

class fifo_test(uvm_test):
  def __init__(self, name, parent):
    super().__init__(name, parent)

  def build_phase(self):
    self.env = fifo_env("env", self)

  async def run_phase(self):
    self.raise_objection()
    sequence = fifo_sequence("sequence")

    await sequence.start(
      self.env.sequencer
    )

    self.drop_objection()

@cocotb.test()
async def test_fifo(dut):
  cocotb.start_soon(
    Clock(dut.clk, 10, unit="ns").start()
  )

  ConfigDB().set(None, "*", "dut", dut)

  await uvm_root().run_test("fifo_test")
