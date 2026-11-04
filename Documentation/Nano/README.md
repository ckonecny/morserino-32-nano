# Morserino-32 Nano — hardware & wiring

This page describes how to build the Nano. For what the Nano is and how it
differs from the Morserino-32 Pocket, see the [main README](../../README.md).

![Wiring overview](wiring.svg)

> **Status:** the pin assignments below are taken from the firmware
> (`Software/src/platformio.ini`, environment `nano-adafruit-feather`) and are
> authoritative. The header names (D5, A2, …) follow Adafruit's pinout for
> board #5691 — please check them against the silkscreen of your board.
> Photos of the real build are still to be added (see
> [`images/`](images/)).

## Bill of material

*Work in progress — quantities and sources are provisional.*

| # | Part | Qty | Notes |
|---|---|---|---|
| 1 | [Adafruit ESP32-S3 Reverse TFT Feather](https://www.adafruit.com/product/5691) (#5691) | 1 | MCU, 240×135 TFT, 3 buttons, USB-C, LiPo charger, MAX17048 fuel gauge |
| 2 | PCM5102A I²S DAC breakout | 1 | headphone audio; no codec init needed |
| 3 | 3.5 mm stereo jack (headphones) | 1 | connected to the DAC board |
| 4 | 3.5 mm stereo jack (key / paddle) | 1 | tip = dit, ring = dah, sleeve = GND |
| 5 | Tactile push button | 1 | the external **FN** button |
| 6 | LiPo cell, 3.7 V, JST-PH | 1 | optional — runs from USB without it |
| 7 | Wire, pin headers, enclosure | – | to be specified |

*(to be completed: exact part numbers, prices, enclosure / 3D-print files)*

## Pin assignment

### Audio (PCM5102A, I²S)

| Feather pin | GPIO | PCM5102A |
|---|---|---|
| D12 | 12 | BCK |
| A4 | 14 | LCK (LRCK) |
| A2 | 16 | DIN |
| 3V3 | – | VIN |
| GND | – | GND |

On the DAC board, tie **SCK**, **FMT**, **FLT** and **DEMP** to GND and **XSMT** to 3V3
(un-mute), unless your breakout already does this with solder jumpers.
The output goes to a headphone jack; there is no speaker amplifier.

### Key / paddle and buttons

| Function | Feather pin | GPIO | Wiring |
|---|---|---|---|
| Paddle left (dit) | D9 | 9 | jack tip → pin, sleeve → GND (internal pull-up) |
| Paddle right (dah) | D10 | 10 | jack ring → pin |
| **FN** button | D5 | 5 | button between pin and GND |
| Keyer out (optional) | D11 | 11 | drives a transmitter keying stage (transistor / optocoupler) |

No external resistors are needed: the firmware enables the internal pull-ups,
and the key just shorts the pin to GND.

### Built-in parts (no wiring)

| Part | Used for |
|---|---|
| Button **D0** (top, BOOT) | encoder "turn right" (+1) |
| Button **D1** (middle) | encoder click / select |
| Button **D2** (bottom) | encoder "turn left" (−1) |
| ST7789 TFT, 240×135 | display (landscape) |
| MAX17048 (I²C 0x36) | battery voltage / charge |

Keep GPIO 0–4, 7 and 35–36 / 40–42 / 45 free: they are used by the board itself.

## Photos

*To be added:* `images/` — build photos, inside view, finished device.
