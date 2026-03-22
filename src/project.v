/*
 * Copyright (c) 2026 Tobias Greiser
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_tobiasgreiser_move_vga_square(
  input  wire [7:0] ui_in,    // Dedicated inputs
  output wire [7:0] uo_out,   // Dedicated outputs
  input  wire [7:0] uio_in,   // IOs: Input path
  output wire [7:0] uio_out,  // IOs: Output path
  output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
  input  wire       ena,      // always 1 when the design is powered, so you can ignore it
  input  wire       clk,      // clock
  input  wire       rst_n     // reset_n - low to reset
);

  // VGA signals
  wire hsync;
  wire vsync;
  wire [1:0] R;
  wire [1:0] G;
  wire [1:0] B;
  wire video_active;
  wire [9:0] pix_x;
  wire [9:0] pix_y;

  // TinyVGA PMOD
  assign uo_out = {hsync, B[0], G[0], R[0], vsync, B[1], G[1], R[1]};

  // Unused outputs assigned to 0.
  assign uio_out = 0;
  assign uio_oe  = 0;

  // Suppress unused signals warning
  wire _unused_ok = &{ena, ui_in[7:6], uio_in};

  hvsync_generator hvsync_gen(
    .clk(clk),
    .reset(~rst_n),
    .hsync(hsync),
    .vsync(vsync),
    .display_on(video_active),
    .hpos(pix_x),
    .vpos(pix_y)
  );

  localparam X_MAX = 640;
  localparam Y_MAX = 480;

  reg [9:0] offset_x;
  reg [9:0] offset_y;
  reg [9:0] square_size;

  wire draw_square;
  wire [9:0] start_square_x;
  wire [9:0] start_square_y;
  wire [9:0] end_square_x;
  wire [9:0] end_square_y;

  // Define start end end point of square
  assign start_square_x = offset_x;
  assign start_square_y = offset_y;
  assign end_square_x = square_size + offset_x;
  assign end_square_y = square_size + offset_y;

  // Check if pixel is between start and end square
  assign draw_square = start_square_x < pix_x &&
      pix_x < end_square_x &&
      start_square_y < pix_y &&
      pix_y < end_square_y;

  // Update pixels according to draw_square
  assign R = video_active && draw_square ? 2'b11 : 2'b01;
  assign G = video_active && draw_square ? 2'b11 : 2'b01;
  assign B = video_active && draw_square ? 2'b11 : 2'b01;

  always @(posedge vsync, negedge rst_n) begin
    if (~rst_n) begin
      offset_x <= 0;
      offset_y <= 0;
      square_size <= 16;
    end else begin
      if (ui_in[0]) begin
        if (start_square_x > 0)
          offset_x <= offset_x - 1;
      end else if (ui_in[1]) begin
        if (end_square_x <= X_MAX)
          offset_x <= offset_x + 1;
      end

      if (ui_in[2]) begin
        if (start_square_y > 0)
          offset_y <= offset_y - 1;
      end else if (ui_in[3]) begin
        if (end_square_y <= Y_MAX)
          offset_y <= offset_y + 1;
      end

      if (ui_in[4]) begin
        if (square_size >= 8)
          square_size <= square_size - 1;
      end else if (ui_in[5]) begin
        if (square_size <= 64)
        square_size <= square_size + 1;
      end
    end
  end

endmodule
