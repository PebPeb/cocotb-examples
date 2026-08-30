
SIM ?= verilator

PYTHON_FILES = mux_tb.py
VERILOG_SOURCES = mux.v

TEST ?= mux_tb

MODULE = $(TEST)
COCOTB_TOPLEVEL = mux
COCOTB_REDUCED_LOG_FMT = 1

# Cocotb makefile include
include $(shell cocotb-config --makefiles)/Makefile.sim
