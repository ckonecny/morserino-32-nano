# Morserino-32 Nano — hardware & wiring

This page describes how to build the Nano. For what the Nano is and how it
differs from the Morserino-32 Pocket, see the [main README](../../README.md).

![The finished Nano](images/nano.jpg)

The case is 3D-printed; here it is next to a matchbox for scale, and opened up:

| Size | Inside |
|---|---|
| ![Nano next to a matchbox](images/case-size.jpg) | ![Inside the case](images/case-inside.jpg) |

## Bill of material

| # | Part | Qty | Source | Price | Notes |
|---|---|---|---|---|---|
| 1 | Adafruit ESP32-S3 Reverse TFT Feather — 4 MB Flash, 2 MB PSRAM, STEMMA QT (#5691) | 1 | [Adafruit](https://www.adafruit.com/product/5691) | 25 USD | MCU, 240×135 TFT, 3 buttons (D0/D1/D2), USB-C, LiPo charger, MAX17048 fuel gauge |
| 2 | PCM5102 I²S DAC module with 3.5 mm jack (pHAT format) | 1 | [Amazon.de](https://www.amazon.de/dp/B0F7LL4S8Z) (pack of 3) | 10 EUR per pack | purple board, pins SCK / BCK / DIN / LCK / GND / VIN; **the headphone jack is on this board** |
| 3 | Stereo jack 3.5 mm, PJ-320A, 4 pin, green/teal | 1 | [Amazon.de](https://www.amazon.de/dp/B0GS9WTZ6Q) (pack of 10) | 5 EUR per pack | the key / paddle jack |
| 4 | Tactile push button 6×6×5 mm, 2 pin | 1 | [Amazon.de](https://www.amazon.de/dp/B07XWYHPZH) (pack of 100) | 5 EUR per pack | the external **FN** button, on top of the case |
| 5 | LiPo cell 3.7 V, 800 mAh, type 752248, 2-pin PH 2.0 mm connector | 1 | [Amazon.de](https://www.amazon.de/dp/B0CSS7DX1T) | 10 EUR | optional — the Nano also runs from USB |
| 6 | Slide switch, PCB mount, ON-ON, 8.6×4.3×4 mm, angled | 1 | [BerryBase](https://www.berrybase.at/schiebeschalter-printmontage-on-on-2-stellig-8.6x4.3x4mm-gewinkelt) | 0.65 EUR | battery on/off switch, in the **+** lead of the LiPo |
| 7 | Hook-up wire, heat-shrink, Kapton tape, a little foam | – | – | – | see assembly notes |
| 8 | 3D-printed case | 1 | – | – | *(print files still to be added)* |

Prices are those of the listed pack, as given by the author (Nov 2026); several parts come in packs, so a single Nano costs less than the sum when you already own spares. **Check the polarity of the LiPo's connector against the Feather before plugging it in – a reversed battery destroys the board (see [Battery and power switch](#battery-and-power-switch)).**

| Feather and DAC | The teal key jack | The battery switch |
|---|---|---|
| ![Feather and DAC module](images/parts-feather-dac.jpg) | ![Key jack](images/key-jack.jpg) | ![Slide switch](images/slide-switch-2.jpg) |

## Wiring overview

![Wiring overview](wiring.svg)

> The pin assignments are taken from the firmware
> (`Software/src/platformio.ini`, environment `nano-adafruit-feather`) and
> match the photos of the build. Header names (D5, A2, …) are those printed on
> the Feather.

### Audio: PCM5102A (I²S)

| Feather pin | GPIO | Wire colour in the photos | DAC pin |
|---|---|---|---|
| D12 | 12 | green | BCK |
| A4 | 14 | yellow | LCK (LRCK) |
| A2 | 16 | white | DIN |
| 3V | – | red | VIN |
| GND | – | black | GND |

In addition, a short wire links **SCK to GND** on the DAC board (the black
loop in the photos). Headphones plug into the jack on the DAC board — there is
no speaker.

![DAC board, back](images/dac-back.jpg)
![DAC board, front](images/dac-front.jpg)

**Solder pads H1L–H4L** (filter, de-emphasis, soft-mute and I²S format) on the
back of the DAC board: leave them **exactly as delivered** — all four are
fitted at the factory and the Nano works with them untouched. No soldering on
these pads is needed.

### Key / paddle and FN button

| Function | Feather pin | GPIO | Wiring |
|---|---|---|---|
| Paddle left (dit) | D9 | 9 | key jack, light-blue wire |
| Paddle right (dah) | D10 | 10 | key jack, brown wire |
| Key jack, common | GND | – | key jack sleeve, black wire |
| **FN** button | D5 | 5 | button between pin (brown wire) and GND (black wire) |
| Keyer out (optional) | D11 | 11 | not used in this build |

No external resistors are needed: the firmware enables the internal pull-ups,
and the key just shorts the pin to GND.

![Wiring overview, photo](images/wiring-overview.jpg)

On the PJ-320A the three wired pads sit in a row: black (GND) on the outer pad,
brown (D10) in the middle, light-blue (D9) on the third; the fourth pad, next to
it, stays unused (it is the jack's switch contact). This matches the usual
convention of tip = dit and ring = dah, but the contact names are inferred from
the photo, not measured. If the paddles come out swapped, exchange the two wires
or use the swap option in the keyer preferences.

### Battery and power switch

> ⚠️ **IMPORTANT – check the battery plug polarity before the first connection!**
> JST-PH LiPo cells are **not** all wired the same way, and the Feather's
> battery connector is **not** protected against reverse polarity. Compare the
> battery's red (+) and black (−) wires with the **+ / −** marking at the
> Feather's battery connector, with a multimeter if in doubt. In the author's
> build the two pins in the plug had to be **swapped** (pulled out of the
> housing and re-inserted the other way round). A reversed battery destroys the
> board, and in the worst case also causes a problem on the USB port of the
> PC/Mac it is connected to. Never plug in USB and battery until the polarity
> is verified.

The LiPo's JST-PH plug goes into the Feather's battery connector. The slide
switch interrupts the red (+) wire; the black (−) wire goes straight through.
The cell charges via USB-C. Check the polarity of any LiPo you buy: JST-PH
cells are **not** all wired the same way.

![LiPo with slide switch](images/battery-with-switch.jpg)

### Built-in parts (no wiring)

| Part | Used for |
|---|---|
| Button **D0** (top, BOOT) | encoder "turn right" (+1) |
| Button **D1** (middle) | encoder click / select |
| Button **D2** (bottom) | encoder "turn left" (−1) |
| ST7789 TFT, 240×135 | display (landscape) |
| MAX17048 (I²C 0x36) | battery voltage / charge |

Do not use GPIO 0–4, 7, 35–36, 40–42 or 45 for anything else: the board itself
uses them.

![Feather running the firmware](images/feather-running.jpg)

## Assembly notes

- The DAC board sits **behind** the Feather. A piece of Kapton tape over the
  ESP32 module and a little foam keep the two boards from touching.
- The wires leave the Feather on its rear header pads and run to the DAC pins
  along the edge.

| Wiring, back | Close-up | Stack, side view |
|---|---|---|
| ![Wired boards](images/wiring-back.jpg) | ![Close-up](images/wiring-closeup-3v-gnd-a2-a4.jpg) | ![Side view](images/stack-side.jpg) |

![Close-up with Kapton tape](images/wiring-closeup-kapton.jpg)
