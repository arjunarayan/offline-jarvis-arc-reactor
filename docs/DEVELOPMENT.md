# Development Guide

This guide explains how to modify, test, and extend the **Offline JARVIS Arc Reactor**.

It is intended for development after the initial hardware and software setup is already working.

For installation, see [`INSTALL.md`](INSTALL.md).

For system architecture, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

For troubleshooting, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

# 1. Repository Structure

The main source files are:

```text
offline-jarvis-arc-reactor/
│
├── src/
│   ├── jarvis_ai.py
│   └── jarvis_lights.py
│
├── firmware/
│   └── JarvisModulinoLights/
│       └── JarvisModulinoLights.ino
│
├── docs/
│
└── requirements.txt
```

The responsibilities are:

```text
jarvis_ai.py
    │
    ├── microphone
    ├── wake word
    ├── speech recognition
    ├── command handling
    ├── local LLM
    ├── text-to-speech
    └── interaction state
```

```text
jarvis_lights.py
    │
    └── Raspberry Pi → Arduino serial communication
```

```text
JarvisModulinoLights.ino
    │
    ├── receive lighting commands
    └── run Modulino Pixel animations
```

---

# 2. Recommended Development Workflow

The recommended workflow is:

```text
Mac
 │
 │ edit code
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
 │ test on real hardware
 ▼
Repeat
```

Use the Mac as the main editing environment and the Raspberry Pi as the runtime/testing environment.

This reduces the chance of creating conflicting versions of the same file.

---

# 3. Updating the Pi

After committing and pushing changes from the Mac, run on the Raspberry Pi:

```bash
cd ~/offline-jarvis-arc-reactor
git pull
```

Then activate the main Python environment:

```bash
source .venv/bin/activate
```

Run JARVIS:

```bash
python src/jarvis_ai.py
```

---

# 4. Main JARVIS Application

Most behavior changes belong in:

```text
src/jarvis_ai.py
```

This file controls the main voice-assistant pipeline.

Conceptually:

```text
Microphone
    ↓
Wake-word detector
    ↓
Command recording
    ↓
Speech-to-text
    ↓
Command router
    ↓
Canned response OR local LLM
    ↓
Piper TTS
    ↓
Speaker output
```

It also coordinates the Arc Reactor lighting state during each stage.

---

# 5. Changing the Listening Window

The current command-listening window is approximately:

```text
6 seconds
```

If you want JARVIS to listen for longer or shorter commands, modify the listening-duration configuration in:

```text
src/jarvis_ai.py
```

When changing it, keep in mind:

## Shorter Window

Advantages:

- faster timeout
- more responsive interaction
- less accidental background audio

Disadvantages:

- long questions may be cut off

## Longer Window

Advantages:

- allows longer questions
- gives the user more time to begin speaking

Disadvantages:

- slower failure recovery
- more background noise may be captured

For the wearable version, six seconds is a useful compromise.

---

# 6. Audio Configuration

The current microphone settings are:

```text
MIC_SAMPLE_RATE   = 44100
MODEL_SAMPLE_RATE = 16000
BLOCK_SIZE        = 3528
```

The microphone captures at 44.1 kHz.

Audio is then converted to 16 kHz for the speech-processing models.

Be careful when modifying these values.

OpenWakeWord and Vosk expect audio in formats suitable for their models.

Changing sample rates without updating the resampling pipeline can break:

- wake-word detection
- speech recognition
- command capture

---

# 7. Changing the Microphone

The current build searches for an input device whose name contains:

```text
ATR4650
```

If you replace the microphone, first inspect available devices:

```bash
source .venv/bin/activate
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Find the new microphone's device name.

Then update the microphone-selection logic in:

```text
src/jarvis_ai.py
```

Prefer matching part of the device name rather than relying only on a numeric device index.

Numeric indexes can change after rebooting or reconnecting USB devices.

---

# 8. Changing the Wake Word

The current wake phrase is:

```text
Hey Jarvis
```

Wake-word detection uses OpenWakeWord.

The model is stored under:

```text
src/models/openwakeword/
```

The current wake-word model is:

```text
hey_jarvis_v0.1.onnx
```

To change the wake phrase:

1. Obtain or create a compatible OpenWakeWord model.
2. Place it in the OpenWakeWord model directory.
3. Update the model path used by `jarvis_ai.py`.
4. Test detection with the microphone.
5. Adjust thresholds if necessary.

Changing the displayed phrase alone will not change what OpenWakeWord recognizes.

---

# 9. Wake-Word Detection Threshold

Wake-word systems normally use a confidence threshold to decide whether audio contains the wake phrase.

A lower threshold makes JARVIS easier to wake but increases accidental triggers.

A higher threshold reduces false activations but may require clearer speech.

Conceptually:

```text
LOW THRESHOLD

More sensitive
    │
    ├── easier wake
    └── more false positives
```

```text
HIGH THRESHOLD

Less sensitive
    │
    ├── fewer false positives
    └── may miss wake phrase
```

When tuning wake detection, test in the environment where the Arc Reactor will actually be used.

A quiet room and a loud party can behave very differently.

---

# 10. Changing Speech Recognition

JARVIS currently uses:

```text
Vosk
```

with:

```text
vosk-model-small-en-us-0.15
```

The model directory is:

```text
src/models/vosk-model-small-en-us-0.15/
```

A different Vosk model can be used by:

1. Downloading the model.
2. Placing it under `src/models/`.
3. Updating the model path in `jarvis_ai.py`.
4. Testing recognition speed and accuracy.

Larger models may improve recognition but require more memory and storage.

---

# 11. Adding Canned Responses

Canned responses bypass the local language model.

They are useful for phrases where the answer should be:

- immediate
- predictable
- short
- repeatable

Example:

```text
User:
How are you?

        ↓

Canned response

        ↓

JARVIS speaks immediately
```

To add one, locate the command/phrase handling section in:

```text
src/jarvis_ai.py
```

Add the recognized phrase and desired response before the request falls through to the local LLM.

Good candidates include:

```text
How are you?
Who are you?
What can you do?
Good morning.
Good night.
```

Avoid creating huge lists of canned questions when the local LLM can already answer them.

---

# 12. Changing a Canned Response

Find the corresponding phrase in:

```text
src/jarvis_ai.py
```

Then modify only the response text.

After changing it:

1. Save the file.
2. Commit and push.
3. Pull onto the Pi.
4. Start JARVIS.
5. Speak the command.
6. Verify the response.

---

# 13. Changing Sleep and Wake Commands

The intended interaction model is:

```text
SLEEP
  │
  │ Hey Jarvis
  ▼
Listen for command
  │
  │ Wake up
  ▼
AWAKE
```

While awake:

```text
Hey Jarvis
    ↓
Command
```

To sleep again:

```text
Hey Jarvis
Go to sleep
```

If adding synonyms, keep their behavior consistent.

For example, phrases such as:

```text
Go to sleep
Go offline
Power off
Shut down
```

may be interpreted as JARVIS standby commands rather than actual Raspberry Pi shutdown commands.

Do not accidentally connect casual voice commands directly to operating-system shutdown unless that behavior is explicitly desired.

---

# 14. Changing the Local LLM

The current model is:

```text
Qwen3-0.6B-Q8_0.gguf
```

stored at:

```text
src/models/llm/Qwen3-0.6B-Q8_0.gguf
```

The model is loaded through:

```text
llama-cpp-python
```

To try another model:

1. Obtain a compatible GGUF model.
2. Place it in `src/models/llm/`.
3. Update the model path in `jarvis_ai.py`.
4. Restart JARVIS.
5. Measure response speed and quality.

---

# 15. Choosing a Different LLM

For a wearable Raspberry Pi project, consider:

```text
Model size
    │
    ├── RAM usage
    ├── startup time
    ├── inference speed
    ├── CPU utilization
    └── answer quality
```

A larger model is not automatically better for this project.

For example:

```text
Smaller model
    │
    ├── faster
    ├── lower RAM
    └── weaker answers
```

```text
Larger model
    │
    ├── better potential answers
    ├── slower
    └── more RAM / CPU
```

Wearable responsiveness should be considered alongside model quality.

---

# 16. Changing the LLM Prompt

The system prompt or prompt-building logic determines how the local LLM is instructed to respond.

This behavior belongs in:

```text
src/jarvis_ai.py
```

Possible adjustments include:

- response length
- personality
- verbosity
- formatting
- whether answers should be conversational
- whether the model should avoid unsupported claims

For a wearable voice assistant, shorter answers generally work better than long paragraphs.

The user has to listen to the response rather than scan text on a screen.

---

# 17. Changing the TTS Voice

Piper TTS models are stored under:

```text
src/models/piper/
```

The current voice is:

```text
en_GB-northern_english_male-medium
```

To change the voice:

1. Download another Piper `.onnx` model.
2. Download its matching `.onnx.json` file.
3. Place both under `src/models/piper/`.
4. Update the Piper voice path in `jarvis_ai.py`.
5. Restart JARVIS.

Both files are required.

---

# 18. Testing Piper Separately

When debugging speech output, test Piper independently from the rest of JARVIS.

First verify the Piper environment:

```bash
src/.piper-venv/bin/python -m piper --help
```

If Piper itself works but JARVIS cannot speak, investigate:

- model path
- generated audio path
- ALSA playback
- Speaker Bonnet configuration

This prevents an audio-output problem from being confused with an AI problem.

---

# 19. Changing the Speaker Output Device

The current audio output is:

```text
plughw:CARD=MAX98357A,DEV=0
```

This corresponds to the MAX98357A-based Speaker Bonnet.

Check available playback devices with:

```bash
aplay -l
```

If a different output device is used, update the playback configuration in:

```text
src/jarvis_ai.py
```

Do not assume card numbers such as `card 0` or `card 1` will remain identical across every system.

Named devices are generally easier to recognize.

---

# 20. Lighting Communication

Raspberry Pi lighting commands are handled by:

```text
src/jarvis_lights.py
```

The Pi communicates with the Nano ESP32 over USB serial.

The normal connection is:

```text
Device: /dev/ttyACM0
Baud:   115200
```

The Arduino receives simple text commands.

---

# 21. Existing Lighting Commands

The protocol includes:

```text
OFF
IDLE
WAKE
LISTENING
THINKING
SPEAKING
DONE
```

The Pi chooses the state.

The Arduino determines the visual effect.

---

# 22. Adding a New Lighting State

Suppose you want to add:

```text
ERROR
```

You would update both sides.

## Raspberry Pi

Add support in:

```text
src/jarvis_lights.py
```

so the Pi can send:

```text
ERROR
```

## Arduino

Update:

```text
firmware/JarvisModulinoLights/JarvisModulinoLights.ino
```

to recognize:

```text
ERROR
```

and define its animation.

Conceptually:

```text
Python
   │
   │ "ERROR"
   ▼
USB Serial
   │
   ▼
Arduino
   │
   ▼
Error animation
```

Both sides must agree on the command name.

---

# 23. Changing an Existing Animation

Lighting animations belong in:

```text
firmware/JarvisModulinoLights/JarvisModulinoLights.ino
```

The existing visual states are:

```text
IDLE       → solid orange
WAKE       → blue left → right
LISTENING  → solid blue
THINKING   → red bouncing pixel
SPEAKING   → breathing green
DONE       → blue right → left
OFF        → all LEDs off
```

To change an animation, modify the Arduino firmware rather than the Python AI application.

This keeps the responsibility boundary clean.

---

# 24. Testing Arduino Changes

After editing the firmware, compile it:

```bash
arduino-cli compile \
    --fqbn arduino:esp32:nano_nora \
    --board-options PinNumbers=byGPIONumber \
    firmware/JarvisModulinoLights
```

Find the Nano:

```bash
arduino-cli board list
```

Then upload:

```bash
arduino-cli upload \
    -p /dev/ttyACM0 \
    --fqbn arduino:esp32:nano_nora \
    --board-options PinNumbers=byGPIONumber \
    firmware/JarvisModulinoLights
```

Use the actual serial port if it differs from `/dev/ttyACM0`.

---

# 25. Test Components Independently

When developing, avoid starting the entire JARVIS stack for every problem.

Test the failing layer separately.

For example:

## Microphone

```bash
arecord -l
```

and:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## Speakers

```bash
speaker-test \
    -D plughw:CARD=MAX98357A,DEV=0 \
    -c 2 \
    -t sine
```

## Arduino

```bash
arduino-cli board list
```

## Power

```bash
vcgencmd get_throttled
```

## Python Dependencies

```bash
python -c "import numpy, scipy, sounddevice, openwakeword, vosk, llama_cpp, serial; print('Dependencies OK')"
```

---

# 26. Debugging Strategy

Use this order:

```text
Hardware power
     ↓
USB connectivity
     ↓
Individual hardware device
     ↓
Operating-system recognition
     ↓
Python/library access
     ↓
Individual subsystem
     ↓
Full JARVIS application
```

Avoid changing code until you know the hardware itself is working.

For example, if `/dev/ttyACM0` does not exist, editing the LED animation will not solve the problem.

---

# 27. Generated Files

Runtime-generated files should not be committed to Git.

Examples include:

```text
*.wav
*.log
__pycache__/
```

AI model files also remain local:

```text
*.gguf
*.onnx
models/
```

Virtual environments are local:

```text
.venv/
.piper-venv/
```

The project's `.gitignore` prevents these from being committed accidentally.

---

# 28. Secrets and Environment Files

Do not commit:

```text
.env
```

or any file containing:

- passwords
- API keys
- access tokens
- private credentials

The current JARVIS runtime is designed to operate without cloud API credentials.

---

# 29. Adding a Python Dependency

If new application code requires another Python package:

1. Install it into `.venv`.
2. Test the feature.
3. Add the dependency to:

```text
requirements.txt
```

Do not rely only on a package being manually installed on one Raspberry Pi.

A fresh installation should be reproducible from the repository.

---

# 30. Do Not Add Piper to the Main Environment

Piper intentionally uses:

```text
src/.piper-venv/
```

Keep its runtime separate from:

```text
.venv/
```

unless the architecture is intentionally redesigned.

---

# 31. Git Workflow

Before changing code on the Pi:

```bash
cd ~/offline-jarvis-arc-reactor
git status
```

Ideally, the working tree should be clean before pulling new work.

Update with:

```bash
git pull
```

For the normal project workflow:

```text
Edit on Mac
     ↓
Review changes in GitHub Desktop
     ↓
Commit
     ↓
Push
     ↓
Pull on Pi
     ↓
Test
```

---

# 32. Commit Changes in Logical Groups

Avoid placing unrelated changes into a single commit.

Good examples:

```text
Improve wake-word handling
```

```text
Add ERROR lighting state
```

```text
Update Piper voice configuration
```

```text
Increase command listening timeout
```

This makes it easier to understand or undo a change later.

---

# 33. Development Checklist

Before considering a feature complete, test:

```text
[ ] JARVIS starts successfully

[ ] Hey Jarvis is detected

[ ] Microphone records the command

[ ] Vosk produces reasonable text

[ ] Canned commands still work

[ ] Qwen responds to general questions

[ ] Piper produces speech

[ ] Speakers play the response

[ ] Arduino remains connected

[ ] All lighting states work

[ ] Go to sleep works

[ ] JARVIS can wake again

[ ] No Raspberry Pi undervoltage occurs

[ ] No repeated USB disconnects occur
```

---

# 34. Test the Complete Voice Flow

After a meaningful code change, test at least:

```text
Hey Jarvis
Wake up
```

Then:

```text
Hey Jarvis
How are you?
```

Then a general LLM question:

```text
Hey Jarvis
What is the largest planet?
```

Then:

```text
Hey Jarvis
Go to sleep
```

Finally wake it again.

This checks both conversational paths and state transitions.

---

# 35. Preserve Offline Operation

One of the core design goals is:

```text
Normal operation = no internet required
```

When adding new features, prefer solutions that preserve this property.

Before introducing a cloud service, consider whether the feature can run locally.

The offline architecture is one of the defining characteristics of the project.

---

# 36. Preserve the Pi / Arduino Boundary

As the project grows, keep this responsibility split:

```text
Raspberry Pi

"What is JARVIS doing?"
```

```text
Arduino Nano ESP32

"What should that state look like?"
```

AI and interaction logic belong on the Pi.

Detailed LED animation logic belongs on the Arduino.

This keeps the architecture understandable and maintainable.

---

# 37. Keep Voice Responses Appropriate for Audio

A response that looks good on a screen may not sound good when spoken aloud.

When changing prompts or canned responses, prefer:

- short sentences
- natural wording
- limited lists
- minimal formatting
- concise answers

JARVIS is primarily an audio interface.

---

# 38. Before Pushing a Change

Check GitHub Desktop carefully.

Make sure you are not committing:

```text
AI models
virtual environments
generated WAV files
logs
.env files
macOS metadata
temporary files
```

Review the diff before committing.

Then use a descriptive commit message.

---

# Development Summary

When extending the project, think of JARVIS as four layers:

```text
┌─────────────────────────────────────┐
│  Interaction                        │
│  Wake / sleep / commands            │
├─────────────────────────────────────┤
│  Voice + AI                         │
│  OpenWakeWord / Vosk / Qwen / Piper │
├─────────────────────────────────────┤
│  Hardware Communication             │
│  Audio / USB serial                 │
├─────────────────────────────────────┤
│  Physical Output                    │
│  Speakers / Nano / Modulino Pixels  │
└─────────────────────────────────────┘
```

When modifying one layer, test that layer independently before debugging the entire system.
