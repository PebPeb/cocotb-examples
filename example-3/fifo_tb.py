import logging

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly

import pyuvm
from pyuvm import *

class fifo_transaction(uvm_sequence_item):
  def __init__(self, name="fifo_transaction"):
    super().__init__(name)
    self.write = False
    self.read = False
    self.data = 0

class write_seq_item(fifo_transaction):
  def __init__(self, data):
    super().__init__("write_seq_item")
    self.write = True
    self.data = data
        
class read_seq_item(fifo_transaction):
  def __init__(self):
    super().__init__("read_seq_item")
    self.read = True

class idle_seq_item(fifo_transaction):
  def __init__(self):
    super().__init__("idle_seq_item")
    
class fifo_sequence(uvm_sequence):
  async def body(self):
    data = [0x01, 0x0f, 0xff]
    for value in data:
      transaction = write_seq_item(value)
      await self.start_item(transaction)
      await self.finish_item(transaction)
    
    for i in range(2):
      transaction = idle_seq_item()
      await self.start_item(transaction)
      await self.finish_item(transaction)
    
    for i in range(len(data)):
      transaction = read_seq_item()
      await self.start_item(transaction)
      await self.finish_item(transaction)
      
    for i in range(2):
      transaction = idle_seq_item()
      await self.start_item(transaction)
      await self.finish_item(transaction)
    
class fifo_driver(uvm_driver):
  def __init__(self, name, parent):
    super().__init__(name, parent)

  def build_phase(self):
    super().build_phase()
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
      else:
        await RisingEdge(self.dut.clk)
      self.seq_item_port.item_done()
      
class fifo_monitor(uvm_monitor):
  def __init__(self, name, parent):
    super().__init__(name, parent)

  def build_phase(self):
    super().build_phase()
    self.ap = uvm_analysis_port("ap", self)
    self.dut = ConfigDB().get(self, "", "dut")

  async def monitor_read(self):
    if self.dut.rd.value and self.dut.rd_rdy.value:
      await RisingEdge(self.dut.clk)
      t = fifo_transaction()
      t.read = True
      t.data = int(self.dut.data_out.value)
      self.ap.write(t)

  async def monitor_write(self):
    if self.dut.wr.value and self.dut.wr_rdy.value:
      t = fifo_transaction()
      t.write = True
      t.data = int(self.dut.data_in.value)
      self.ap.write(t)

  async def run_phase(self):
    while True:
      await RisingEdge(self.dut.clk)
      cocotb.start_soon(self.monitor_write())
      cocotb.start_soon(self.monitor_read())

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
    self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
    self.monitor.ap.connect(self.scoreboard.analysis_export)

@pyuvm.test()
class fifo_test(uvm_test):
  def __init__(self, name, parent):
    super().__init__(name, parent)

  def build_phase(self):
    ConfigDB().set(None, "*", "dut", cocotb.top)
    self.dut = ConfigDB().get(self, "", "dut")
    self.env = fifo_env("env", self)

  async def run_phase(self):
    self.raise_objection()
    
    clock = Clock(self.dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    await Timer(1, unit="ns")
    
    sequence = fifo_sequence("sequence")
    await sequence.start(
      self.env.sequencer
    )

    self.drop_objection()
