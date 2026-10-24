# Quick Start

This guide is for a Raspberry Pi where the **Offline JARVIS Arc Reactor** has already been installed and configured.

If this is your first time setting up the project, follow [`INSTALL.md`](INSTALL.md) instead.

---

# 1. Connect the Hardware

Before starting JARVIS, make sure these are connected:

- Raspberry Pi 5
- Audio-Technica ATR4650-USB microphone
- Adafruit Speaker Bonnet
- CQRobot speakers
- Arduino Nano ESP32
- Arduino Modulino Pixels
- Power source

The Nano ESP32 should be connected to the Raspberry Pi through USB.

---

# 2. Check the Arduino

The Nano ESP32 normally appears as:

```text
/dev/ttyACM0
```

You can check it with:

```bash
arduino-cli board list
```

You should see the Nano ESP32 listed.

If it is missing, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

# 3. Start JARVIS

Open a terminal on the Raspberry Pi.

Go to the project:

```bash
cd ~/offline-jarvis-arc-reactor
```

Activate the Python environment:

```bash
source .venv/bin/activate
```

Start JARVIS:

```bash
python src/jarvis_ai.py
```

---

# 4. Wake JARVIS

JARVIS starts in sleep mode.

Say:

```text
Hey Jarvis
```

Then say:

```text
Wake up
```

JARVIS is now active.

---

# 5. Ask a Question

Every new command still begins with:

```text
Hey Jarvis
```

For example:

```text
Hey Jarvis
How are you?
```

or:

```text
Hey Jarvis
What is the largest planet?
```

After the wake phrase is detected, JARVIS gives you approximately **6 seconds** to speak your command.

---

# 6. Watch the Arc Reactor

The lights indicate what JARVIS is doing.

| State | Light Effect |
|---|---|
| `IDLE` | Solid orange |
| `WAKE` | Blue animation left → right |
| `LISTENING` | Solid blue |
| `THINKING` | Red bouncing pixel |
| `SPEAKING` | Breathing green |
| `DONE` | Blue animation right → left |
| `OFF` | LEDs off |

---

# 7. Put JARVIS to Sleep

Say:

```text
Hey Jarvis
Go to sleep
```

JARVIS returns to sleep mode but continues running.

To wake it again:

```text
Hey Jarvis
```

followed by:

```text
Wake up
```

---

# 8. Stop JARVIS Completely

To stop the Python application, go to the terminal where JARVIS is running and press:

```text
Ctrl+C
```

This terminates the application.

A spoken command such as:

```text
Go to sleep
```

does **not** terminate the Python program.

---

# 9. Start It Again

Any time you want to restart JARVIS:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

---

# Quick Command Reference

## Start

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

## Wake

```text
Hey Jarvis
Wake up
```

## Ask Something

```text
Hey Jarvis
<your question>
```

## Sleep

```text
Hey Jarvis
Go to sleep
```

## Stop Program

```text
Ctrl+C
```

---

# If Something Does Not Work

See:

- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) for common problems
- [`INSTALL.md`](INSTALL.md) for installation and configuration
- [`USAGE.md`](USAGE.md) for complete usage instructions
- [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the system works
- [`PARTS.md`](PARTS.md) for hardware information
