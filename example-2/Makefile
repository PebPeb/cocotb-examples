
SIM ?= verilator
EXTRA_ARGS += --trace --trace-structs

PYTHON_FILES = fifo_tb.py
VERILOG_SOURCES = fifo.v

TEST ?= fifo_tb

MODULE = $(TEST)
COCOTB_TOPLEVEL = fifo
COCOTB_REDUCED_LOG_FMT = 1

# Cocotb makefile include
include $(shell cocotb-config --makefiles)/Makefile.sim
