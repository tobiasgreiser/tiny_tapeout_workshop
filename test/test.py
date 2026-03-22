# NOTE: I used this tb as a starting point:
# https://github.com/urish/tt-rom-vga-screensaver/blob/main/test/test.py

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

# Set clock period to 40 ns (25 MHz)
CLOCK_PERIOD = 40

# Set VGA timing parameters matching hvsync_generator.v
H_DISPLAY = 640
H_FRONT   =  16
H_SYNC    =  96
H_BACK    =  48
V_DISPLAY = 480
V_FRONT   =  10
V_SYNC    =   2
V_BACK    =  33

# Derived constants
H_SYNC_START = H_DISPLAY + H_FRONT
H_SYNC_END = H_SYNC_START + H_SYNC
H_TOTAL = H_SYNC_END + H_BACK
V_SYNC_START = V_DISPLAY + V_FRONT
V_SYNC_END = V_SYNC_START + V_SYNC
V_TOTAL = V_SYNC_END + V_BACK

def ue_out_binary(dut):
    return '{0:08b}'.format(dut.uo_out.value.to_unsigned())
def ue_out_binary_at_index(dut, i):
    return int(ue_out_binary(dut)[i])

def check_square_bounds(x,y, min_x=0, max_x=15, min_y=0, max_y=15):
    assert min_x <= x, "White pixel present but not expected at this position."
    assert x <= max_x, "White pixel present but not expected at this position."
    assert min_y <= y, "White pixel present but not expected at this position."
    assert y <= max_y, "White pixel present but not expected at this position."

@cocotb.test()
async def test_hsync(dut):
    # Set up the clock
    clock = Clock(dut.clk, CLOCK_PERIOD, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset the design
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    assert ue_out_binary_at_index(dut, 0) == 1, "Unexpected hsync pattern"
    await ClockCycles(dut.clk, H_DISPLAY)
    assert ue_out_binary_at_index(dut, 0) == 1, "Unexpected hsync pattern"
    await ClockCycles(dut.clk, H_FRONT-1)
    assert ue_out_binary_at_index(dut, 0) == 1, "Unexpected hsync pattern"
    await ClockCycles(dut.clk, 1)
    assert ue_out_binary_at_index(dut, 0) == 0, "Unexpected hsync pattern"
    await ClockCycles(dut.clk, H_SYNC-1)
    assert ue_out_binary_at_index(dut, 0) == 0, "Unexpected hsync pattern"
    await ClockCycles(dut.clk, 1)
    assert ue_out_binary_at_index(dut, 0) == 1, "Unexpected hsync pattern"

@cocotb.test()
async def test_project(dut):
    # Set up the clock
    clock = Clock(dut.clk, CLOCK_PERIOD, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset the design
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Checks for correct position of square on the screen
    square_present = False
    for y in range(V_TOTAL):
        for x in range(H_TOTAL):
            if ue_out_binary_at_index(dut, 5) == 1:
                dut._log.info("Found white pixel at " + str(x) + ", " + str(y))
                check_square_bounds(x, y)
                assert ue_out_binary_at_index(dut, 5) == ue_out_binary_at_index(dut, 6) == ue_out_binary_at_index(dut, 7), "Pixel is not white."
                square_present = True
            await ClockCycles(dut.clk, 1)

    assert square_present, "Square was not found anywhere on the screen."

@cocotb.test()
async def test_input(dut):
    # Set up the clock
    clock = Clock(dut.clk, CLOCK_PERIOD, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset the design
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    move_by_n_pixels = 10

    # Move square by 10 pixels to the right and wait until frame is updated
    dut.ui_in.value = 2 # Set 2nd bit
    await ClockCycles(dut.clk, H_TOTAL*V_TOTAL*move_by_n_pixels)
    dut.ui_in.value = 0

    # Checks for correct position of square on the screen
    square_present = False
    for y in range(V_TOTAL):
        for x in range(H_TOTAL):
            if ue_out_binary_at_index(dut, 5) == 1:
                dut._log.info("Found white pixel at " + str(x) + ", " + str(y))
                check_square_bounds(x, y, min_x=0+move_by_n_pixels, max_x=15+move_by_n_pixels)
                assert ue_out_binary_at_index(dut, 5) == ue_out_binary_at_index(dut, 6) == ue_out_binary_at_index(dut, 7), "Pixel is not white."
                square_present = True
            await ClockCycles(dut.clk, 1)

    assert square_present, "Square was not found anywhere on the screen."
