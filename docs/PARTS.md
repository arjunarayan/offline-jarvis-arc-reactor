# Parts List

This page lists the hardware used in the tested **Offline JARVIS Arc Reactor** build.

Where possible, both Micro Center and Amazon direct product links are included.

- No retailer search-result links are used.
- If the exact item is not available or could not be verified at one retailer,
  that is stated explicitly.
- Some mechanical parts came from Home Depot rather than Micro Center or Amazon.

---

## Main Electronics

| Component | Qty | Micro Center | Amazon | Notes |
|---|---:|---|---|---|
| Raspberry Pi 5 - 8GB | 1 | [Micro Center](https://www.microcenter.com/product/673711/raspberry-pi-5-8gb) | [Amazon](https://www.amazon.com/dp/B0CK2FCG1K) | Runs wake-word detection, speech recognition, local LLM inference, and text-to-speech |
| Arduino Nano ESP32 with Headers | 1 | [Micro Center](https://www.microcenter.com/product/704595/arduino-nano-esp32-with-headers) | [Amazon](https://www.amazon.com/dp/B0C947BHK5) | Controls the reactor lighting |
| Arduino Modulino Pixels - ABX00109 | 1 | [Micro Center](https://www.microcenter.com/product/707365/arduino-modulino-pixels) | [Amazon](https://www.amazon.com/dp/B0F8X5WG38) | Eight RGB LEDs used for all reactor animations |
| Audio-Technica ATR4650-USB Microphone | 1 | [Micro Center](https://www.microcenter.com/product/612859/audio-technica-atr4650-usb-omni-condenser-microphone) | [Amazon](https://www.amazon.com/dp/B07ZPBSTJP) | USB microphone used for wake-word detection and speech recognition |
| Adafruit I2S 3W Stereo Speaker Bonnet for Raspberry Pi - Product 3346 | 1 | [Micro Center](https://www.microcenter.com/product/474383/adafruit-industries-i2s-3w-stereo-speaker-bonnet-for-raspberry-pi-mini-kit) | No exact Amazon listing verified | [Adafruit direct](https://www.adafruit.com/product/3346) |
| CQRobot Enclosed 3W / 4 Ohm Speaker, JST PH2.0 version | 2 | No exact Micro Center CQRobot listing | No exact Amazon listing verified | [CQRobot direct](https://cqrobot.com/product/CQRLB4O3W-A) |
| Belkin BoostCharge Pro 3-Port Laptop Power Bank 20K - BPB020 | 1 | [Micro Center](https://www.microcenter.com/product/702628/belkin-boostcharge-pro-3-port-laptop-power-bank-20k) | [Amazon](https://www.amazon.com/dp/B0FZK1P5JH) | 20,000 mAh; up to 65 W USB-C Power Delivery |
| microSD card - 32GB or larger | 1 | [Micro Center - SanDisk Ultra PLUS 32GB](https://www.microcenter.com/product/609574/sandisk-ultra-plus-32gb-microsdhc-class-10-v10-flash-memory-card-w-adapter) | [Amazon - SanDisk Ultra 32GB](https://www.amazon.com/dp/B08GY9NYRM) | The exact card is not critical; 32GB or larger is recommended |

---

## Speaker Modification

The final build uses **CQRobot 3W / 4 Ohm enclosed speakers**.

The speakers originally came with JST connectors.

For this build:

1. The JST connectors were removed.
2. The speaker wires were stripped.
3. The exposed wire ends were connected directly to the screw terminals on the
   Adafruit Speaker Bonnet.
4. Speaker polarity was preserved when connecting the wires.

The CQRobot speakers themselves were not modified internally.

---

## Power

The tested portable power source is:

**Belkin BoostCharge Pro 3-Port Laptop Power Bank 20K - BPB020**

Purchase links:

- [Micro Center](https://www.microcenter.com/product/702628/belkin-boostcharge-pro-3-port-laptop-power-bank-20k)
- [Amazon](https://www.amazon.com/dp/B0FZK1P5JH)

Specifications:

- 20,000 mAh capacity
- Up to 65 W USB-C Power Delivery
- 2 x USB-C ports
- 1 x USB-A port
- Digital battery-status display

### Important power note

The Raspberry Pi 5, USB microphone, Arduino Nano ESP32, Modulino Pixels,
Speaker Bonnet, and local AI workload can create significant power demand.

During development, insufficient input voltage caused the Nano ESP32 to
disconnect and reconnect repeatedly over USB.

Use a good-quality USB-C cable and a sufficiently capable power source.

---

## Mechanical Hardware

### Everbilt M3 Screws

The final reactor uses metric **M3-0.5** machine screws.

| Screw | Qty Required | Purchase Link | Purpose |
|---|---:|---|---|
| Everbilt M3-0.5 x 20 mm machine screw | 3 | [Home Depot](https://www.homedepot.com/p/203091629) | Main front reactor shell |
| Everbilt M3-0.5 x 12 mm machine screw | 3 | [Home Depot](https://www.homedepot.com/p/204849608) | Inner crystal / enclosure assembly |

We purchased extra screws so that lost or damaged screws would not stop the
build.

The build had:

- 8 x M3-0.5 x 20 mm screws available
- 6 x M3-0.5 x 12 mm screws available

Only three of each length are required for the reactor itself.

---

## VELCRO Mounting Strips

VELCRO strips are used to secure parts of the wearable assembly while still
allowing them to be removed for maintenance.

Recommended type:

**VELCRO Brand Industrial Strength adhesive strips, black**

- [Home Depot - 4 in. x 2 in. Industrial Strength Strips](https://www.homedepot.com/p/202261921)
- [Amazon - VELCRO Brand Heavy Duty Industrial Strength Strips](https://www.amazon.com/dp/B0C53YS1H4)

Exact pack size is not important. The strips can be cut to the dimensions
needed for the build.

---

# 3D-Printed Parts

The final build does **not** require every STL from the original arc-reactor
model set.

The original front-shell and diffuser design is based on:

[Crash Works 3D Arc Reactor repository](https://github.com/crashworks3d/crashworks3d_arc_reactor)

Only the pieces used by this build should be printed.

---

## Gray / Silver Parts

### `lower_grid_and_caps.stl`

The large turbine / gear-looking front structure.

Quantity: **1**

Recommended color:

- Gray
- Silver

### `upper_grid.stl`

The thin decorative ring mounted over the front turbine.

Quantity: **1**

Recommended color:

- Gray
- Silver

---

## White / Translucent Parts

### `crystal_ring.stl`

The large outer white diffuser ring.

Quantity: **1**

Recommended material/color:

- White
- Translucent white

This piece helps diffuse the Modulino Pixels so the reactor looks more like a
single illuminated surface rather than a row of individual LEDs.

---

## Required Three-Piece Inner Crystal Stack

All three of these pieces are still required.

### `main_crystal_top.stl`

Quantity: **1**

This is the white piece that interfaces with the front gray shell.

### `main_crystal_bottom.stl`

Quantity: **1**

Part of the inner crystal structure.

### `main_crystal_enclosure.stl`

Quantity: **1**

The white enclosure piece with the three raised mounting posts.

These three parts form the required inner crystal stack:

```text
main_crystal_top
        +
main_crystal_bottom
        +
main_crystal_enclosure# Parts

This document lists the hardware and 3D-printed parts used in the final **Offline JARVIS Arc Reactor** build.

The final build uses a Raspberry Pi 5 for JARVIS, an Arduino Nano ESP32 for lighting control, Arduino Modulino Pixels for the reactor LEDs, an Audio-Technica USB microphone, and a Raspberry Pi Speaker Bonnet driving CQRobot speakers.

---

## Core Computer

### Raspberry Pi 5 — 8 GB

**Quantity:** 1

Runs the offline JARVIS software, wake-word detection, speech recognition, local LLM, Piper McLean TTS, and communication with the Arduino Nano ESP32.

- **Micro Center:** [Raspberry Pi 5 8 GB](https://www.microcenter.com/product/673711/raspberry-pi-5)
- **Amazon:** [Raspberry Pi 5 8 GB](https://www.amazon.com/dp/B0CK2FCG1K)

---

## Lighting Controller

### Arduino Nano ESP32 with Headers

**Quantity:** 1

Controls the Arc Reactor lighting animations and communicates with the Raspberry Pi over USB.

- **Micro Center:** [Arduino Nano ESP32 with Headers](https://www.microcenter.com/product/704595/arduino-nano-esp32-with-headers)
- **Amazon:** [Arduino Nano ESP32](https://www.amazon.com/dp/B0C947BHK5)

---

## Arc Reactor LEDs

### Arduino Modulino Pixels

**Quantity:** 1

The Modulino Pixels board contains **8 individually controllable RGB LEDs** and is used for all Arc Reactor lighting states and animations.

Examples include:

- IDLE — solid orange
- WAKE — moving blue animation
- LISTENING — solid blue
- THINKING — red bouncing-ball animation
- SPEAKING — breathing/flashing green
- DONE — blue shutdown animation
- OFF — all LEDs off

- **Amazon:** [Arduino Modulino Pixels](https://www.amazon.com/dp/B0F8X5WG38)
- **Micro Center:** No exact Modulino Pixels listing was used for this build.

**Important:** Dupont jumper wires are **not required** in the final build.

---

## Microphone

### Audio-Technica ATR4650-USB Omnidirectional Condenser Microphone

**Quantity:** 1

Used for the `"Hey Jarvis"` wake word and voice commands.

- **Micro Center:** [Audio-Technica ATR4650-USB](https://www.microcenter.com/product/612859/audio-technica-atr4650-usb-omni-condenser-microphone)
- **Amazon:** No exact Amazon listing was used for this build.

The microphone connects directly to the Raspberry Pi through USB.

---

## Audio Amplifier

### Adafruit I2S 3W Stereo Speaker Bonnet for Raspberry Pi

**Quantity:** 1

Provides digital I2S audio output and amplification for the speakers.

- **Micro Center:** [Adafruit I2S 3W Stereo Speaker Bonnet](https://www.microcenter.com/product/474383/adafruit-industries-i2s-3w-stereo-speaker-bonnet-for-raspberry-pi-mini-kit)
- **Adafruit:** [Adafruit I2S 3W Stereo Speaker Bonnet](https://www.adafruit.com/product/3346)
- **Amazon:** No exact Amazon listing was used for this build.

The Speaker Bonnet mounts directly onto the Raspberry Pi GPIO header.

---

## Speakers

### CQRobot 3W 4Ω Enclosed Speakers

**Quantity:** 1 pair / 2 speakers

Specifications:

- 3 W
- 4 Ω
- Enclosed rectangular speaker
- Originally supplied with JST-PH2.0 connectors

- **Amazon:** [CQRobot 3W 4Ω Speakers](https://www.amazon.com/dp/B0822Z4LPH)
- **CQRobot:** [CQRobot 4Ω 3W Speaker](https://cqrobot.com/product/CQRLB4O3W-B)
- **Micro Center:** No exact CQRobot speaker listing was used for this build.

### Modification Used in This Build

The original JST connectors were **cut off**.

The speaker wires were then **stripped** so the bare wires could connect directly to the screw terminals on the Adafruit Speaker Bonnet.

No JST adapter is required in the final build.

---

## Power Bank

### Belkin BoostCharge Pro 3-Port Laptop Power Bank 20K

**Model:** BPB020

**Quantity:** 1

Provides portable power for the Arc Reactor/JARVIS system.

Features used by this project:

- 20K-class battery capacity
- Up to 65 W USB-C Power Delivery
- 2 × USB-C ports
- 1 × USB-A port
- Can power multiple project components simultaneously

- **Belkin:** [BoostCharge Pro 3-Port Laptop Power Bank 20K](https://www.belkin.com/p/3-port-laptop-power-bank-20k/P-BPB020.html)
- **Amazon:** No exact Amazon listing was used for this build.
- **Micro Center:** No exact Micro Center listing was used for this build.

---

## Storage

### microSD Card

**Quantity:** 1

Used as the Raspberry Pi boot and storage device.

A microSD card was already available for this build, so no additional card was purchased specifically for the project.

---

## Mounting

### VELCRO Industrial Strength Strips

**Quantity:** 1 pack

Used to secure project components while still allowing them to be removed for maintenance.

- **Micro Center:** [VELCRO 90812 Industrial Strength 4" × 1" Strips](https://www.microcenter.com/product/663395/velcro-90812-industrial-strength-strips-4-x-1-titanium-gray-%2810-pack%29)
- **Amazon:** No exact Amazon listing was used for this build.

---

## Screws

The Arc Reactor assembly uses **M3-0.5 machine screws**.

### Everbilt M3-0.5 × 20 mm Machine Screws

**Build inventory:** 8 screws

Used for the larger Arc Reactor structural connections.

- **Home Depot:** [Everbilt M3-0.5 × 20 mm Machine Screws](https://www.homedepot.com/p/203091629)

### Everbilt M3-0.5 × 12 mm Machine Screws

**Build inventory:** 6 screws

Used for shorter Arc Reactor assembly connections.

- **Home Depot:** [Everbilt M3-0.5 × 12 mm Machine Screws](https://www.homedepot.com/p/204849608)

---

# 3D-Printed Parts

Only the following CAD/STL files are required for the final build.

There are **8 required STL files total**.

## Outer Reactor Structure

- `upper_grid.stl`
- `lower_grid_and_caps.stl`

## Crystal Ring

- `crystal_ring.stl`

## Three-Piece Crystal Stack

These three pieces form the central crystal stack:

1. `main_crystal_bottom.stl`
2. `main_crystal_enclosure.stl`
3. `main_crystal_top.stl`

## Rear Electronics Housing

- `rear_pod.stl`
- `rear_lid.stl`

The rear pod provides space for the electronics and speaker installation, while the rear lid closes the assembly.

---

## CAD File Summary

| File | Purpose |
|---|---|
| `upper_grid.stl` | Upper Arc Reactor structure |
| `lower_grid_and_caps.stl` | Lower structure and caps |
| `crystal_ring.stl` | Ring surrounding the central crystal |
| `main_crystal_bottom.stl` | Bottom of the three-piece crystal stack |
| `main_crystal_enclosure.stl` | Middle/enclosure section of the crystal stack |
| `main_crystal_top.stl` | Top of the three-piece crystal stack |
| `rear_pod.stl` | Rear electronics/speaker housing |
| `rear_lid.stl` | Rear housing lid |

---

# Parts Not Used in the Final Build

The following parts appeared during earlier prototypes but are **not required** for the final version:

- Dupont jumper wires
- Separate addressable LED strip
- Breadboard LED power module
- Separate LED level shifter
- Screen or display

The final lighting system is based on the **Arduino Nano ESP32 + Arduino Modulino Pixels**.
