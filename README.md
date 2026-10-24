# Offline JARVIS Arc Reactor

A wearable **Arc Reactor with a fully offline JARVIS-style voice assistant**, powered by a Raspberry Pi 5 and an Arduino Nano ESP32.

The system performs wake-word detection, speech recognition, local AI inference, and text-to-speech entirely on-device. An Arduino Nano ESP32 independently controls the Arc Reactor's lighting animations using Arduino Modulino Pixels.

No cloud AI API is required during normal operation.

---

## Features

- Fully offline voice assistant
- `"Hey Jarvis"` wake-word detection
- Local speech-to-text with Vosk
- Local conversational AI with Qwen3
- Local text-to-speech with Piper TTS
- Raspberry Pi 5 main computer
- Arduino Nano ESP32 dedicated lighting controller
- Arduino Modulino Pixels RGB lighting
- Visual feedback for listening, thinking, speaking, and other states
- USB microphone input
- Stereo speaker output through an Adafruit Speaker Bonnet
- Portable battery-powered operation
- Wearable Arc Reactor enclosure
- Simple Raspberry Pi ↔ Arduino serial protocol
- No cloud dependency during normal operation

---

# Demo

A normal interaction looks like this:

```text
User:
Hey Jarvis

User:
Wake up

JARVIS becomes active.

User:
Hey Jarvis
How are you?

JARVIS responds through the speakers.

User:
Hey Jarvis
What is the largest planet?

JARVIS:
Jupiter.

User:
Hey Jarvis
Go to sleep
```

Throughout the interaction, the Arc Reactor changes lighting state to indicate what JARVIS is doing.

For a complete demonstration sequence, see:

[`docs/DEMO.md`](docs/DEMO.md)

---

# How It Works

The system is split between two computers.

## Raspberry Pi 5

The Raspberry Pi handles:

- microphone input
- wake-word detection
- speech recognition
- command processing
- local LLM inference
- text-to-speech
- speaker output
- sleep/wake state
- lighting-state commands

## Arduino Nano ESP32

The Arduino handles:

- receiving lighting commands over USB serial
- maintaining Arc Reactor lighting state
- running LED animations
- controlling the Modulino Pixels

The basic architecture is:

```text
                    USER
                      │
                      │ voice
                      ▼
             ATR4650-USB Microphone
                      │
                      ▼
              ┌───────────────┐
              │ Raspberry Pi  │
              │       5       │
              └───────┬───────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
 Voice / AI Pipeline          Lighting Commands
        │                           │
        │                           │ USB Serial
        ▼                           ▼
    Piper TTS              Arduino Nano ESP32
        │                           │
        ▼                           ▼
 Speaker Bonnet              Modulino Pixels
        │
        ▼
     Speakers
```

For a deeper technical explanation, see:

[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

# Voice and AI Pipeline

A normal question passes through several local components:

```text
Microphone
    │
    ▼
OpenWakeWord
    │
    ▼
Vosk
    │
    ▼
Command Router
    │
    ├── Canned Response
    │
    └── Qwen3 Local LLM
              │
              ▼
          Piper TTS
              │
              ▼
           Speakers
```

The major software components are:

| Component | Purpose |
|---|---|
| OpenWakeWord | Detects `"Hey Jarvis"` |
| Vosk | Converts speech to text |
| Qwen3 | Generates local conversational responses |
| llama-cpp-python | Runs the GGUF language model |
| Piper TTS | Generates JARVIS speech |
| PySerial | Communicates with the Arduino |
| Arduino Modulino | Controls the Arc Reactor LEDs |

---

# Offline Operation

One of the main goals of this project is complete local operation.

After initial installation and model downloads, normal use does **not** require:

- OpenAI API access
- cloud speech recognition
- cloud text-to-speech
- cloud wake-word detection
- remote LLM inference
- internet access

The runtime pipeline stays on the Raspberry Pi:

```text
OpenWakeWord
     ↓
Vosk
     ↓
Qwen3
     ↓
Piper TTS
```

The Arduino lighting controller is also completely local.

---

# Interaction Model

JARVIS begins in sleep mode.

Wake it with:

```text
Hey Jarvis
```

Then:

```text
Wake up
```

Once awake, each new interaction still begins with:

```text
Hey Jarvis
```

For example:

```text
Hey Jarvis
What is a black hole?
```

To return JARVIS to sleep:

```text
Hey Jarvis
Go to sleep
```

This wake-word-per-command design is intentional.

It helps prevent nearby conversations from being interpreted as commands, especially when the system is being worn at a noisy event.

---

# Listening Window

After detecting `"Hey Jarvis"`, the system gives the user approximately:

```text
6 seconds
```

to speak the command.

The microphone captures at:

```text
44100 Hz
```

and the audio is converted to:

```text
16000 Hz
```

for the speech-processing models.

---

# Arc Reactor Lighting States

The Arc Reactor provides visual feedback for the current JARVIS state.

| State | Lighting Effect |
|---|---|
| `IDLE` | Solid orange |
| `WAKE` | Blue animation left → right |
| `LISTENING` | Solid blue |
| `THINKING` | Red pixel bouncing 1 → 8 → 1 |
| `SPEAKING` | Breathing green |
| `DONE` | Blue animation right → left |
| `OFF` | All LEDs off |

The Raspberry Pi sends simple state commands such as:

```text
LISTENING
THINKING
SPEAKING
```

The Arduino owns the animation logic.

---

# Why Use Both a Raspberry Pi and Arduino?

The two devices have different responsibilities.

```text
Raspberry Pi:

"What is JARVIS doing?"
```

```text
Arduino Nano ESP32:

"What should that state look like?"
```

This keeps AI processing separate from real-time lighting animation.

For example:

```text
Raspberry Pi
    │
    │ "THINKING"
    ▼
Arduino Nano ESP32
    │
    ▼
Run red bouncing-pixel animation
```

The Pi does not need to continuously send individual LED values.

---

# Main Hardware

The final system uses:

- Raspberry Pi 5
- Arduino Nano ESP32 with headers
- Arduino Modulino Pixels
- Audio-Technica ATR4650-USB microphone
- Adafruit I2S 3W Stereo Speaker Bonnet
- CQRobot 3W / 4Ω enclosed speakers
- Belkin BoostCharge Pro 3-Port Laptop Power Bank 20K
- custom 3D-printed Arc Reactor components
- Everbilt M3 hardware
- industrial-strength Velcro

For exact parts and purchase links, see:

[`docs/PARTS.md`](docs/PARTS.md)

---

# Main Software

The project uses:

```text
Python 3
OpenWakeWord
Vosk
Qwen3 GGUF
llama-cpp-python
Piper TTS
SoundDevice
SciPy
PySerial
Arduino CLI
Arduino Modulino library
```

---

# Repository Structure

```text
offline-jarvis-arc-reactor/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── jarvis_ai.py
│   └── jarvis_lights.py
│
├── firmware/
│   └── JarvisModulinoLights/
│       └── JarvisModulinoLights.ino
│
└── docs/
    ├── QUICKSTART.md
    ├── PARTS.md
    ├── INSTALL.md
    ├── USAGE.md
    ├── ARCHITECTURE.md
    ├── TROUBLESHOOTING.md
    ├── FAQ.md
    ├── DEVELOPMENT.md
    └── DEMO.md
```

Large AI models, virtual environments, generated audio, and local runtime files are intentionally excluded from Git.

---

# Documentation

## Quick Start

Already installed everything and just want to run JARVIS?

[`docs/QUICKSTART.md`](docs/QUICKSTART.md)

---

## Parts

Exact hardware, purchase links, modifications, screws, and required CAD files:

[`docs/PARTS.md`](docs/PARTS.md)

---

## Installation

Complete Raspberry Pi, Python, model, audio, and Arduino setup:

[`docs/INSTALL.md`](docs/INSTALL.md)

---

## Usage

How to wake JARVIS, ask questions, understand light states, and put it back to sleep:

[`docs/USAGE.md`](docs/USAGE.md)

---

## Architecture

Technical explanation of the complete voice, AI, audio, serial, and lighting system:

[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Troubleshooting

Solutions for power, USB, Arduino, microphone, audio, model, and runtime issues:

[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

---

## FAQ

Answers to common questions about the hardware, software, offline architecture, and design decisions:

[`docs/FAQ.md`](docs/FAQ.md)

---

## Development

How to modify the wake word, listening timeout, local model, voice, canned responses, serial protocol, and lighting animations:

[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)

---

## Demo

A ready-to-use demonstration flow for showing the project:

[`docs/DEMO.md`](docs/DEMO.md)

---

# Quick Start

If the project has already been installed on the Raspberry Pi:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

Then say:

```text
Hey Jarvis
```

followed by:

```text
Wake up
```

For the complete quick-start guide:

[`docs/QUICKSTART.md`](docs/QUICKSTART.md)

---

# Installation

For a new Raspberry Pi setup, start with:

[`docs/INSTALL.md`](docs/INSTALL.md)

The setup includes:

1. Raspberry Pi system packages
2. Python virtual environment
3. Python dependencies
4. Piper TTS
5. OpenWakeWord models
6. Vosk model
7. Qwen3 GGUF model
8. Speaker Bonnet configuration
9. USB microphone configuration
10. Arduino CLI
11. Nano ESP32 support
12. Modulino library
13. firmware compilation and upload

---

# Running JARVIS

Once installed:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

A normal session is:

```text
SLEEP
  │
  │ "Hey Jarvis"
  ▼
WAKE
  │
  ▼
LISTENING
  │
  ▼
THINKING
  │
  ▼
SPEAKING
  │
  ▼
DONE
  │
  ▼
WAIT FOR NEXT "HEY JARVIS"
```

---

# Local AI Model

The current conversational model is:

```text
Qwen3-0.6B-Q8_0.gguf
```

It runs locally through:

```text
llama-cpp-python
```

A small model was chosen because this project prioritizes:

- offline execution
- Raspberry Pi compatibility
- reasonable response latency
- lower memory requirements
- lower power consumption

A larger cloud model would provide stronger answers, but that would defeat one of the project's primary goals: running the entire interaction locally.

---

# Speech Recognition

Speech-to-text is handled by:

```text
Vosk
```

using:

```text
vosk-model-small-en-us-0.15
```

Vosk was selected because it can run locally on the Raspberry Pi without requiring an external speech-recognition service.

---

# Text-to-Speech

Speech output is generated using:

```text
Piper TTS
```

with the voice:

```text
en_GB-northern_english_male-medium
```

Piper runs in a separate Python virtual environment from the main JARVIS application.

---

# Wake-Word Detection

The wake phrase is:

```text
Hey Jarvis
```

Wake-word recognition is handled locally by OpenWakeWord.

The current wake model is:

```text
hey_jarvis_v0.1.onnx
```

---

# Lighting Architecture

The Raspberry Pi does not directly render individual animation frames.

Instead:

```text
jarvis_ai.py
      │
      ▼
jarvis_lights.py
      │
      │ USB Serial
      ▼
Arduino Nano ESP32
      │
      ▼
JarvisModulinoLights.ino
      │
      ▼
Modulino Pixels
```

This creates a clean boundary between interaction logic and visual behavior.

---

# Serial Protocol

The Raspberry Pi and Nano ESP32 communicate at:

```text
115200 baud
```

The Arduino normally appears as:

```text
/dev/ttyACM0
```

Supported lighting commands include:

```text
OFF
IDLE
WAKE
LISTENING
THINKING
SPEAKING
DONE
```

The deliberately simple text protocol makes the lighting system easy to test and debug.

---

# Audio Architecture

Input:

```text
ATR4650-USB
      │
      ▼
Raspberry Pi
      │
      ▼
SoundDevice
```

Output:

```text
Piper TTS
      │
      ▼
ALSA
      │
      ▼
MAX98357A Speaker Bonnet
      │
      ▼
CQRobot Speakers
```

---

# Power

The wearable setup uses a:

```text
Belkin BoostCharge Pro 3-Port Laptop Power Bank 20K
```

Stable Raspberry Pi power is important.

Insufficient power can cause symptoms such as:

- USB disconnects
- Nano ESP32 disappearing
- microphone disconnects
- serial failures
- lighting becoming unresponsive

If multiple USB devices begin behaving unexpectedly, check power before assuming the software is broken.

See:

[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

---

# Development Workflow

The normal development workflow is:

```text
Mac
 │
 │ edit in Zed
 ▼
GitHub Desktop
 │
 │ commit + push
 ▼
GitHub
 │
 │ git pull
 ▼
Raspberry Pi
 │
 │ test on hardware
 ▼
Repeat
```

This keeps GitHub as the shared source of truth while allowing the Raspberry Pi to remain primarily a runtime and hardware-testing environment.

See:

[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)

---

# Example Full Request

A complete interaction travels through the system like this:

```text
1. User says "Hey Jarvis"

2. OpenWakeWord detects the phrase

3. Raspberry Pi sends WAKE to the Arduino

4. Arc Reactor runs wake animation

5. JARVIS listens for the question

6. Vosk converts speech into text

7. Raspberry Pi sends THINKING

8. Request is routed to a canned response or Qwen3

9. A text response is produced

10. Raspberry Pi sends SPEAKING

11. Piper generates speech

12. Speaker Bonnet plays the response

13. Raspberry Pi sends DONE

14. JARVIS waits for the next "Hey Jarvis"
```

---

# Project Design Goals

## Offline First

Normal voice interaction should work without internet access.

## Wearable

The system should remain practical for costume/event use.

## Understandable

Each subsystem should have a clear responsibility.

## Debuggable

Hardware components should be testable independently.

## Responsive

Simple interactions should avoid unnecessary AI inference.

## Visual

The Arc Reactor should communicate JARVIS's current state without requiring the user to look at a terminal.

---

# Troubleshooting Philosophy

When debugging, check the system from the bottom up:

```text
Power
  ↓
USB
  ↓
Hardware detection
  ↓
Arduino
  ↓
Microphone
  ↓
Speakers
  ↓
Python environment
  ↓
AI models
  ↓
JARVIS application
```

This prevents software debugging from masking a hardware or power problem.

The complete troubleshooting guide is here:

[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

---

# Photos

Photos of the completed Arc Reactor and wearable setup can be added here later.

A useful future repository layout would be:

```text
assets/
├── arc-reactor-front.jpg
├── arc-reactor-back.jpg
├── electronics-layout.jpg
└── complete-costume.jpg
```

Then those images can be displayed directly in this README.

---

# Project Status

The core Offline JARVIS Arc Reactor system includes:

- [x] Raspberry Pi voice assistant
- [x] `"Hey Jarvis"` wake word
- [x] offline speech recognition
- [x] offline local LLM
- [x] offline text-to-speech
- [x] sleep / wake interaction flow
- [x] canned responses
- [x] Arduino Nano ESP32 lighting controller
- [x] Modulino Pixels integration
- [x] interaction-state lighting
- [x] portable power
- [x] wearable Arc Reactor hardware
- [x] installation documentation
- [x] usage documentation
- [x] troubleshooting documentation
- [x] architecture documentation
- [x] development documentation
- [x] demo documentation

---

# Documentation Index

| Guide | Purpose |
|---|---|
| [`QUICKSTART.md`](docs/QUICKSTART.md) | Start an already-installed JARVIS |
| [`PARTS.md`](docs/PARTS.md) | Hardware, links, and CAD files |
| [`INSTALL.md`](docs/INSTALL.md) | Set up the complete system |
| [`USAGE.md`](docs/USAGE.md) | Operate JARVIS |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Understand how everything works |
| [`TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Diagnose failures |
| [`FAQ.md`](docs/FAQ.md) | Common questions |
| [`DEVELOPMENT.md`](docs/DEVELOPMENT.md) | Modify and extend the project |
| [`DEMO.md`](docs/DEMO.md) | Demonstrate the finished system |

---

# Final System

```text
                         HUMAN
                           │
                           ▼
                    ATR4650-USB
                           │
                           ▼
                ┌──────────────────┐
                │  Raspberry Pi 5  │
                │                  │
                │ OpenWakeWord     │
                │ Vosk             │
                │ Qwen3            │
                │ Piper TTS        │
                │ JARVIS Logic     │
                └───────┬─────┬────┘
                        │     │
                 Audio  │     │ USB Serial
                        │     │
                        ▼     ▼
                Speaker     Arduino
                 Bonnet    Nano ESP32
                    │          │
                    ▼          ▼
                 Speakers   Modulino
                              Pixels
                                │
                                ▼
                           ARC REACTOR
```

**Offline voice. Local AI. Physical feedback. Wearable JARVIS.**
