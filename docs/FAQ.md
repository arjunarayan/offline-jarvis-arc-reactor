# FAQ

This document answers common questions about the **Offline JARVIS Arc Reactor**.

For setup instructions, see [`INSTALL.md`](INSTALL.md).

For normal operation, see [`USAGE.md`](USAGE.md).

For troubleshooting, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

# Does JARVIS need the internet?

No.

After installation and model downloads are complete, normal JARVIS operation is fully offline.

The following components all run locally:

```text
Wake word       → OpenWakeWord
Speech-to-text  → Vosk
Conversation    → Qwen3
Text-to-speech  → Piper TTS
Lighting        → Arduino Nano ESP32
```

Internet access is mainly needed during setup for:

- cloning the repository
- installing packages
- downloading AI models
- updating software

---

# Does this use the OpenAI API?

No.

The project does not require the OpenAI API for normal operation.

The conversational model runs locally on the Raspberry Pi.

---

# What computer runs JARVIS?

The main computer is a:

```text
Raspberry Pi 5
```

The Raspberry Pi handles:

- microphone input
- wake-word detection
- speech recognition
- local AI inference
- text-to-speech
- audio playback
- interaction state
- lighting commands

---

# Why is there also an Arduino?

The Raspberry Pi handles the AI and voice system.

The Arduino Nano ESP32 handles Arc Reactor lighting.

The split is:

```text
Raspberry Pi
    │
    ├── Voice
    ├── AI
    ├── TTS
    └── Decides current state

            ↓ USB serial

Arduino Nano ESP32
    │
    └── Runs LED animations
```

This allows lighting animations to continue smoothly without depending on Raspberry Pi inference speed.

---

# Why not control the LEDs directly from the Raspberry Pi?

The Raspberry Pi could theoretically control LEDs directly.

However, using the Nano ESP32 provides:

- cleaner separation between AI and lighting
- simpler LED timing
- easier debugging
- dedicated animation control
- less dependence on Raspberry Pi GPIO timing
- a simple serial interface between the two systems

The Raspberry Pi only has to send commands such as:

```text
THINKING
```

The Arduino decides how that state should look.

---

# What LEDs are used?

The final build uses:

```text
Arduino Modulino Pixels
```

The board contains eight individually controllable RGB LEDs.

A separate LED strip is not required in the final build.

---

# Do I need Dupont jumper wires?

No.

Dupont jumper wires were considered during earlier versions of the build but are not required for the final system.

---

# What microphone does the project use?

The final build uses:

```text
Audio-Technica ATR4650-USB
```

It connects directly to the Raspberry Pi through USB.

---

# Why use a microphone close to the user's mouth?

This is a wearable system that may be used in noisy environments.

Keeping the microphone close to the user's mouth improves:

- wake-word detection
- speech recognition
- signal-to-noise ratio
- reliability at parties or events

---

# What speakers are used?

The project uses two:

```text
CQRobot 3W / 4Ω enclosed speakers
```

They connect to the Adafruit Speaker Bonnet.

The original JST connectors were removed and the wires were stripped so they could connect directly to the Bonnet terminals.

---

# What is the Speaker Bonnet?

The project uses the:

```text
Adafruit I2S 3W Stereo Speaker Bonnet
```

It provides amplified audio output from the Raspberry Pi to the speakers.

---

# What text-to-speech system is used?

The project uses:

```text
Piper TTS
```

Piper runs locally on the Raspberry Pi.

The selected voice is:

```text
en_GB-northern_english_male-medium
```

---

# What speech-recognition system is used?

The project uses:

```text
Vosk
```

The current speech-recognition model is:

```text
vosk-model-small-en-us-0.15
```

Speech recognition runs locally.

---

# What wake-word system is used?

The project uses:

```text
OpenWakeWord
```

The wake phrase is:

```text
Hey Jarvis
```

---

# Can I change the wake phrase?

Yes, but it is not just a text setting.

You need an OpenWakeWord model that recognizes the new phrase.

You would then need to update the wake-word configuration in the JARVIS code to use that model.

---

# Why does every command start with "Hey Jarvis"?

This is intentional.

Even after JARVIS is awake, each new interaction begins with:

```text
Hey Jarvis
```

This prevents the system from treating nearby conversation as commands.

It also provides a predictable interaction model for a wearable device.

---

# Why isn't JARVIS continuously conversational?

The project intentionally uses wake-word activation for each interaction.

The flow is:

```text
Hey Jarvis
     ↓
Question
     ↓
Response
     ↓
Wait for another "Hey Jarvis"
```

This was chosen over continuous conversation to reduce accidental activation and make the behavior easier to control in noisy environments.

---

# How long does JARVIS listen for a command?

The listening window is approximately:

```text
6 seconds
```

The user should begin speaking shortly after the listening state begins.

---

# Can I make the listening window longer?

Yes.

The listening duration is controlled by the Python application.

It can be changed in:

```text
src/jarvis_ai.py
```

See [`DEVELOPMENT.md`](DEVELOPMENT.md) for modification guidance.

---

# What language model is used?

The current model is:

```text
Qwen3-0.6B-Q8_0.gguf
```

It is loaded locally using:

```text
llama-cpp-python
```

---

# Why use such a small language model?

The model needs to run on a Raspberry Pi.

A small model provides:

- lower RAM usage
- faster inference
- lower power usage
- better portability
- complete offline operation

The tradeoff is that it is less capable than a large cloud-hosted model.

---

# Can I use a different LLM?

Yes.

A compatible GGUF model can potentially replace the current Qwen model.

However, larger models may:

- require more RAM
- respond much more slowly
- increase CPU load
- consume more power
- make the wearable experience less responsive

Any replacement should be tested directly on the Raspberry Pi.

---

# Why does JARVIS sometimes take time to answer?

The language model is running locally on the Raspberry Pi rather than on a cloud GPU.

The request path includes:

```text
Speech recognition
      ↓
Local LLM inference
      ↓
Text-to-speech generation
      ↓
Audio playback
```

The LLM inference stage is usually the most computationally expensive part.

---

# Can I change the voice?

Yes.

Piper supports multiple voice models.

To change the voice:

1. Download another compatible Piper model.
2. Download its matching `.onnx.json` configuration.
3. Update the voice-model path in the JARVIS code.

The current voice files are stored under:

```text
src/models/piper/
```

---

# Can JARVIS answer current internet questions?

Not by default.

The system is designed to operate offline.

The local language model only knows what is contained in the model itself and the context provided by the application.

There is no web-search component in the current architecture.

---

# Can JARVIS control smart-home devices?

Not in the current version.

The architecture could be extended with additional commands or integrations, but the current project focuses on:

- offline voice interaction
- local AI responses
- Arc Reactor lighting

---

# Can I add more canned responses?

Yes.

Canned responses are useful for commands where you want:

- instant responses
- predictable wording
- no LLM delay

They can be added in the main JARVIS application.

See [`DEVELOPMENT.md`](DEVELOPMENT.md).

---

# What do the light colors mean?

The final lighting states are:

| State | Effect |
|---|---|
| `IDLE` | Solid orange |
| `WAKE` | Blue animation left → right |
| `LISTENING` | Solid blue |
| `THINKING` | Red bouncing pixel |
| `SPEAKING` | Breathing green |
| `DONE` | Blue animation right → left |
| `OFF` | All LEDs off |

---

# Why does the Arc Reactor use different light states?

The lights provide visual feedback.

The user can immediately see whether JARVIS is:

- waiting
- awake
- listening
- thinking
- speaking
- finished

This is especially useful in noisy environments where audio cues may be difficult to hear.

---

# How does the Raspberry Pi communicate with the Arduino?

Through USB serial.

The typical device is:

```text
/dev/ttyACM0
```

The serial connection uses:

```text
115200 baud
```

The Pi sends commands such as:

```text
WAKE
LISTENING
THINKING
SPEAKING
DONE
```

---

# Why might `/dev/ttyACM0` disappear?

Possible causes include:

- Arduino reconnecting
- USB reset
- insufficient Raspberry Pi power
- USB cable problem
- Linux assigning a different port such as `/dev/ttyACM1`

See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

# Why is Raspberry Pi power so important?

The Raspberry Pi 5 can become unstable if the power source or cable cannot provide enough power.

During development, inadequate power could cause symptoms such as:

- USB devices disconnecting
- Arduino becoming unresponsive
- serial connections disappearing
- lighting failures

Power should therefore be one of the first things checked when multiple USB devices start behaving strangely.

---

# What battery powers the project?

The portable build uses the:

```text
Belkin BoostCharge Pro 3-Port Laptop Power Bank 20K
```

See [`PARTS.md`](PARTS.md) for the exact hardware information.

---

# Are the AI models stored in GitHub?

No.

Large model files are intentionally excluded from the repository.

Examples include:

```text
*.gguf
*.onnx
models/
```

The installation guide explains where to obtain and place them.

---

# Why aren't model files committed?

Model files can be hundreds of megabytes or larger.

Keeping them out of Git:

- keeps the repository small
- avoids unnecessary downloads
- avoids GitHub file-size problems
- keeps source code separate from runtime data

---

# Are Python virtual environments committed?

No.

Directories such as:

```text
.venv/
.piper-venv/
```

are local runtime environments and are excluded from Git.

They should be recreated during installation.

---

# Why does Piper use a separate virtual environment?

Piper has its own dependency environment.

Separating it from the main JARVIS environment reduces package conflicts and keeps the main runtime cleaner.

---

# Can I run this on something other than a Raspberry Pi 5?

Possibly, but the project is built and tested around a Raspberry Pi 5.

Another Linux computer may be able to run the software, but:

- audio configuration may differ
- GPIO/audio hardware may differ
- serial device names may differ
- performance may differ
- installation steps may need modification

---

# Can I run the Python code on a Mac?

Some individual software components could run on macOS, but the complete project is designed for Raspberry Pi OS and its connected hardware.

The full system depends on:

- Raspberry Pi audio configuration
- Speaker Bonnet
- Arduino USB serial
- wearable hardware

The Mac is primarily useful for editing the repository and using GitHub Desktop.

---

# How should I update the Raspberry Pi after changing code on the Mac?

The recommended workflow is:

```text
Mac
 │
 │ edit files
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
```

On the Raspberry Pi:

```bash
cd ~/offline-jarvis-arc-reactor
git pull
```

This keeps GitHub as the shared source of truth.

---

# Should I edit the same file on both the Pi and Mac?

Avoid doing that when possible.

Editing the same file independently on both machines can create Git conflicts.

A simpler workflow is:

1. Edit on the Mac.
2. Commit and push using GitHub Desktop.
3. Pull the changes onto the Pi.
4. Use the Pi primarily for testing.

---

# Where should I start if something breaks?

Use this order:

```text
Power
  ↓
USB
  ↓
Arduino
  ↓
Microphone
  ↓
Speakers
  ↓
Python environment
  ↓
Model files
  ↓
JARVIS application
```

Then consult [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

# Which document should I read?

## I want to get running quickly

See:

[`QUICKSTART.md`](QUICKSTART.md)

## I am installing everything

See:

[`INSTALL.md`](INSTALL.md)

## I want to understand how to use JARVIS

See:

[`USAGE.md`](USAGE.md)

## Something is broken

See:

[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)

## I want to understand how the system works

See:

[`ARCHITECTURE.md`](ARCHITECTURE.md)

## I want to modify the project

See:

[`DEVELOPMENT.md`](DEVELOPMENT.md)

## I want to see the hardware list

See:

[`PARTS.md`](PARTS.md)
