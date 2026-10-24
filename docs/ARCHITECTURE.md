# Architecture

This document describes the software and hardware architecture of the **Offline JARVIS Arc Reactor**.

The system is designed to run locally on a Raspberry Pi while using an Arduino Nano ESP32 as a dedicated Arc Reactor lighting controller.

For installation instructions, see [`INSTALL.md`](INSTALL.md).

For normal operation, see [`USAGE.md`](USAGE.md).

For hardware details, see [`PARTS.md`](PARTS.md).

For common failures, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

# 1. System Overview

The project is divided into two main computing systems:

```text
┌───────────────────────────────────────────┐
│              Raspberry Pi 5               │
│                                           │
│  Wake-word detection                      │
│  Speech recognition                       │
│  Conversation / local LLM                 │
│  Text-to-speech                           │
│  Interaction state                        │
│  Lighting commands                        │
└───────────────────┬───────────────────────┘
                    │
                    │ USB Serial
                    ▼
┌───────────────────────────────────────────┐
│           Arduino Nano ESP32              │
│                                           │
│  Receives lighting commands               │
│  Runs LED animations                      │
│  Controls Modulino Pixels                 │
└───────────────────┬───────────────────────┘
                    │
                    ▼
             Modulino Pixels
```

The Raspberry Pi handles the computationally expensive voice and AI tasks.

The Arduino handles real-time visual effects.

---

# 2. High-Level Architecture

```text
                         USER
                          │
                          │ voice
                          ▼
                 ATR4650-USB Microphone
                          │
                          ▼
                    Raspberry Pi 5
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
     Voice / AI Pipeline         Lighting Controller
            │                           │
            │                           │ USB Serial
            │                           ▼
            │                  Arduino Nano ESP32
            │                           │
            │                           ▼
            │                   Modulino Pixels
            │
            ▼
        Piper TTS
            │
            ▼
      Speaker Bonnet
            │
            ▼
      CQRobot Speakers
```

---

# 3. Raspberry Pi Responsibilities

The Raspberry Pi 5 is the main computer.

It is responsible for:

- capturing microphone audio
- detecting the wake phrase
- recording commands
- converting speech to text
- deciding whether a command can use a canned response
- sending general questions to the local language model
- generating speech
- playing speech through the speakers
- managing sleep and awake states
- telling the Arduino which lighting state to display

The main application is:

```text
src/jarvis_ai.py
```

Lighting communication is handled by:

```text
src/jarvis_lights.py
```

---

# 4. Arduino Responsibilities

The Arduino Nano ESP32 is dedicated to Arc Reactor lighting.

It does not perform:

- speech recognition
- wake-word detection
- language-model inference
- text-to-speech
- conversational logic

Instead, it receives simple commands from the Raspberry Pi and translates them into LED animations.

The firmware is:

```text
firmware/JarvisModulinoLights/JarvisModulinoLights.ino
```

This separation keeps lighting responsive even while the Raspberry Pi is busy performing AI inference.

---

# 5. Audio Input Pipeline

Voice input begins at the Audio-Technica ATR4650-USB microphone.

The complete path is:

```text
Human speech
     │
     ▼
ATR4650-USB
     │
     │ USB audio
     ▼
Raspberry Pi
     │
     ▼
SoundDevice
     │
     ▼
Audio processing
```

The microphone operates at:

```text
44100 Hz
```

The AI speech-processing pipeline operates at:

```text
16000 Hz
```

The application therefore resamples microphone audio before sending it to the wake-word and speech-recognition components.

---

# 6. Audio Configuration

The final audio configuration uses:

```text
Microphone sample rate: 44100 Hz
Model sample rate:      16000 Hz
Block size:             3528 samples
Channels:               1
Sample format:          int16
```

Conceptually:

```text
ATR4650
44.1 kHz audio
     │
     ▼
Audio block
     │
     ▼
Resampling
     │
     ▼
16 kHz audio
     │
     ├────────► OpenWakeWord
     │
     └────────► Vosk
```

---

# 7. Wake-Word Detection

JARVIS uses **OpenWakeWord**.

The wake phrase is:

```text
Hey Jarvis
```

Required models include:

```text
hey_jarvis_v0.1.onnx
melspectrogram.onnx
embedding_model.onnx
```

These files are stored under:

```text
src/models/openwakeword/
```

The wake-word detector runs locally.

No cloud wake-word service is used.

---

# 8. Sleep State

When JARVIS is asleep, the full conversational pipeline does not continuously process nearby speech.

Instead, the system primarily waits for:

```text
Hey Jarvis
```

Conceptually:

```text
             ┌─────────────────┐
             │      SLEEP      │
             └────────┬────────┘
                      │
              microphone audio
                      │
                      ▼
              OpenWakeWord
                      │
              "Hey Jarvis"?
                │          │
               no         yes
                │          │
                └────┐     ▼
                     │   WAKE
                     │
                     └── continue waiting
```

This makes the interaction more deliberate and reduces accidental command processing.

---

# 9. Wake Sequence

The intended wake flow is:

```text
User: "Hey Jarvis"
        │
        ▼
Wake phrase detected
        │
        ▼
WAKE lighting animation
        │
        ▼
Listen for command
        │
        ▼
User: "Wake up"
        │
        ▼
JARVIS enters awake mode
```

Once awake, each new interaction still begins with:

```text
Hey Jarvis
```

JARVIS therefore does not become a continuously listening conversational assistant after wake-up.

---

# 10. Command Capture

After the wake phrase is detected, the system opens a limited listening window.

The configured listening period is approximately:

```text
6 seconds
```

The user speaks during this interval.

Captured audio is then passed to Vosk.

```text
Hey Jarvis
    │
    ▼
Wake detected
    │
    ▼
LISTENING
    │
    ▼
Record command audio
    │
    ▼
Vosk
    │
    ▼
Recognized text
```

---

# 11. Speech Recognition

Speech-to-text is performed locally using **Vosk**.

The model is:

```text
vosk-model-small-en-us-0.15
```

and is stored under:

```text
src/models/vosk-model-small-en-us-0.15/
```

Vosk converts the captured 16 kHz audio into text.

For example:

```text
Audio:
"what is the largest planet"

        ↓

Vosk

        ↓

Text:
what is the largest planet
```

---

# 12. Command Routing

After speech is converted to text, JARVIS determines what type of request it received.

Conceptually:

```text
Recognized text
      │
      ▼
Command routing
      │
      ├──── Wake / sleep command
      │
      ├──── Canned response
      │
      └──── General question
                     │
                     ▼
                 Local LLM
```

This avoids using the language model when a simple deterministic action is enough.

---

# 13. Canned Responses

Some commands can be answered directly.

For example:

```text
How are you?
```

can use a predefined response rather than sending the request through the local language model.

Advantages include:

- faster responses
- predictable behavior
- reduced CPU usage
- reduced LLM latency

The local LLM is reserved for questions that need generated answers.

---

# 14. Local Language Model

General conversational questions are handled by a local **Qwen3** model.

The current model file is:

```text
Qwen3-0.6B-Q8_0.gguf
```

stored at:

```text
src/models/llm/Qwen3-0.6B-Q8_0.gguf
```

The model runs through:

```text
llama-cpp-python
```

The processing path is:

```text
Recognized question
        │
        ▼
Prompt construction
        │
        ▼
Qwen3 GGUF
        │
        ▼
Generated text
```

No cloud language-model API is required.

---

# 15. Why a Small Local LLM?

The system is designed around a wearable Raspberry Pi.

A smaller model provides several advantages:

- lower memory use
- lower CPU requirements
- faster local inference
- no network dependency
- better portability
- lower power usage than much larger models

The tradeoff is that response quality and knowledge are more limited than large cloud-hosted models.

For this project, offline operation and responsiveness are more important than maximum model capability.

---

# 16. Text-to-Speech

Generated text is converted back into speech using **Piper TTS**.

The final voice model is:

```text
en_GB-northern_english_male-medium
```

The model files are:

```text
en_GB-northern_english_male-medium.onnx
en_GB-northern_english_male-medium.onnx.json
```

stored under:

```text
src/models/piper/
```

Piper itself runs from a separate virtual environment:

```text
src/.piper-venv/
```

---

# 17. Why Piper Has a Separate Environment

The main JARVIS Python environment and the Piper environment are kept separate.

Conceptually:

```text
Repository
│
├── .venv/
│      └── Main JARVIS dependencies
│
└── src/
       └── .piper-venv/
              └── Piper TTS
```

This isolates Piper's dependencies from the main application environment.

---

# 18. Audio Output Pipeline

The text-to-speech path is:

```text
Generated response
       │
       ▼
Piper TTS
       │
       ▼
Generated audio
       │
       ▼
ALSA
       │
       ▼
MAX98357A Speaker Bonnet
       │
       ▼
CQRobot speakers
       │
       ▼
User hears JARVIS
```

The Raspberry Pi audio device used by the project is:

```text
plughw:CARD=MAX98357A,DEV=0
```

---

# 19. Interaction State Machine

The JARVIS interaction can be represented as a state machine.

```text
                      ┌──────────────┐
                      │    SLEEP     │
                      └──────┬───────┘
                             │
                        Hey Jarvis
                             │
                             ▼
                      ┌──────────────┐
                      │     WAKE     │
                      └──────┬───────┘
                             │
                             ▼
                      ┌──────────────┐
                      │  LISTENING   │
                      └──────┬───────┘
                             │
                      speech captured
                             │
                             ▼
                      ┌──────────────┐
                      │   THINKING   │
                      └──────┬───────┘
                             │
                       answer ready
                             │
                             ▼
                      ┌──────────────┐
                      │   SPEAKING   │
                      └──────┬───────┘
                             │
                      speech finished
                             │
                             ▼
                      ┌──────────────┐
                      │     DONE     │
                      └──────┬───────┘
                             │
                             ▼
                    wait for next wake
```

A sleep command returns the system to:

```text
SLEEP
```

---

# 20. Lighting State Machine

Each major JARVIS state has a corresponding visual effect.

```text
JARVIS State      Arduino Command      Lighting

Idle              IDLE                 Solid orange

Wake detected     WAKE                 Blue left → right

Listening         LISTENING            Solid blue

Thinking          THINKING             Red bouncing pixel

Speaking          SPEAKING             Breathing green

Finished          DONE                 Blue right → left

Lights disabled   OFF                  All LEDs off
```

The Raspberry Pi sends only the state command.

The Arduino determines how the animation itself is rendered.

---

# 21. Raspberry Pi to Arduino Protocol

Communication uses USB serial.

Typical connection:

```text
Raspberry Pi
    │
    │ /dev/ttyACM0
    │ 115200 baud
    ▼
Arduino Nano ESP32
```

The protocol intentionally uses simple text commands.

Examples:

```text
IDLE
WAKE
LISTENING
THINKING
SPEAKING
DONE
OFF
```

This keeps the protocol easy to debug manually.

---

# 22. Why Use a Simple Serial Protocol?

The project does not require a complex binary protocol.

Each command represents a state rather than individual LED operations.

For example, the Pi sends:

```text
THINKING
```

instead of sending commands such as:

```text
LED 1 red
LED 2 off
LED 3 off
move to LED 2
wait 100 ms
...
```

The Arduino owns those animation details.

This reduces communication between the two computers.

---

# 23. Lighting Responsibility Boundary

The division of responsibility is:

```text
Raspberry Pi decides:

"What is JARVIS doing?"

              │
              ▼

Arduino decides:

"What should that state look like?"
```

For example:

```text
Raspberry Pi:
THINKING

        ↓

Arduino:
Run red bouncing-pixel animation
```

This is a cleaner architecture than having the Raspberry Pi continuously control every LED frame.

---

# 24. Failure Isolation

Separating the voice system and lighting controller also helps troubleshooting.

For example:

```text
Voice works + lights fail
        │
        ▼
Investigate:
USB serial
Arduino
Modulino Pixels
```

Whereas:

```text
Lights work + voice fails
        │
        ▼
Investigate:
Microphone
Vosk
OpenWakeWord
Qwen
Piper
Audio output
```

This makes the system easier to debug.

---

# 25. Offline Architecture

All major runtime components are local:

```text
┌─────────────────────────────┐
│       Raspberry Pi 5        │
│                             │
│  OpenWakeWord               │
│  Vosk                       │
│  Qwen3                      │
│  Piper TTS                  │
│  Application logic          │
└─────────────────────────────┘
```

Normal operation does not require:

- OpenAI API
- cloud speech recognition
- cloud text-to-speech
- cloud wake-word detection
- remote LLM inference

Internet access is primarily required during setup and software/model downloads.

---

# 26. Repository Architecture

The repository is organized roughly as:

```text
offline-jarvis-arc-reactor/
│
├── README.md
├── requirements.txt
│
├── docs/
│   ├── PARTS.md
│   ├── INSTALL.md
│   ├── USAGE.md
│   ├── TROUBLESHOOTING.md
│   ├── ARCHITECTURE.md
│   └── ASSEMBLY.md
│
├── src/
│   ├── jarvis_ai.py
│   └── jarvis_lights.py
│
└── firmware/
    └── JarvisModulinoLights/
        └── JarvisModulinoLights.ino
```

Large model files, virtual environments, generated audio, and local runtime files are intentionally excluded from Git.

---

# 27. Software Responsibilities

## `jarvis_ai.py`

Main JARVIS application.

Responsible for:

- microphone input
- wake-word detection
- speech recognition
- sleep/wake state
- command routing
- local LLM interaction
- Piper TTS
- audio playback
- coordinating lighting states

## `jarvis_lights.py`

Lighting communication layer.

Responsible for:

- opening the Arduino serial connection
- sending lighting state commands
- isolating lighting control from the main voice logic

## `JarvisModulinoLights.ino`

Arduino firmware.

Responsible for:

- receiving serial commands
- tracking the current lighting state
- generating LED animations
- controlling the eight Modulino Pixels

---

# 28. Complete Request Path

A full conversational request travels through the system like this:

```text
1. User says:
   "Hey Jarvis"

             ↓

2. ATR4650 captures audio

             ↓

3. OpenWakeWord detects wake phrase

             ↓

4. Pi sends WAKE to Arduino

             ↓

5. Arduino starts blue wake animation

             ↓

6. Pi enters LISTENING

             ↓

7. User asks question

             ↓

8. Vosk converts audio to text

             ↓

9. Pi sends THINKING to Arduino

             ↓

10. Command router checks request

             ↓

11. Canned response OR Qwen3

             ↓

12. Text response produced

             ↓

13. Pi sends SPEAKING to Arduino

             ↓

14. Piper converts text to audio

             ↓

15. Speaker Bonnet plays response

             ↓

16. Pi sends DONE to Arduino

             ↓

17. System waits for next "Hey Jarvis"
```

---

# 29. Hardware Communication Diagram

```text
                         ┌──────────────────┐
                         │ ATR4650-USB Mic  │
                         └────────┬─────────┘
                                  │ USB
                                  ▼
                         ┌──────────────────┐
                         │  Raspberry Pi 5  │
                         └──────┬─────┬─────┘
                                │     │
                    GPIO / I2S  │     │ USB serial
                                │     │
             ┌──────────────────┘     └──────────────────┐
             ▼                                           ▼
┌────────────────────────┐                  ┌────────────────────────┐
│ MAX98357A Speaker      │                  │ Arduino Nano ESP32     │
│ Bonnet                 │                  │                        │
└───────────┬────────────┘                  └───────────┬────────────┘
            │                                           │
            ▼                                           ▼
┌────────────────────────┐                  ┌────────────────────────┐
│ CQRobot Speakers       │                  │ Modulino Pixels        │
└────────────────────────┘                  └────────────────────────┘
```

---

# 30. Design Priorities

The architecture prioritizes:

## Offline Operation

Voice recognition, AI, and TTS all execute locally.

## Simple Interaction

Every interaction starts with:

```text
Hey Jarvis
```

This avoids continuous conversational listening.

## Clear Responsibility Boundaries

The Raspberry Pi handles intelligence.

The Arduino handles lighting.

## Debuggability

The serial protocol uses readable commands.

Each hardware subsystem can be tested independently.

## Portability

The complete system can operate from a battery pack without requiring internet access.

## Wearable Operation

The computational hardware can remain in a pouch while the Arc Reactor itself contains only the components necessary for the wearable visual effect.

---

# Architecture Summary

The entire system can be summarized as:

```text
VOICE INPUT
    │
    ▼
ATR4650
    │
    ▼
Raspberry Pi 5
    │
    ├── OpenWakeWord
    │
    ├── Vosk
    │
    ├── Qwen3
    │
    ├── Piper TTS
    │
    └── JARVIS state machine
    │
    ├─────────────────────────────┐
    │                             │
    ▼                             ▼
Speaker Bonnet              USB Serial
    │                             │
    ▼                             ▼
Speakers                  Nano ESP32
                                  │
                                  ▼
                           Modulino Pixels
```

The result is a self-contained, offline voice assistant integrated with a wearable Arc Reactor lighting system.
