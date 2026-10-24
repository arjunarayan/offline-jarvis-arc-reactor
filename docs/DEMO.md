# Demo Guide

This guide provides a simple demonstration flow for the **Offline JARVIS Arc Reactor**.

It is intended for showing the project to another person at home, at school, at an event, or during a project presentation.

For normal operation, see [`USAGE.md`](USAGE.md).

For a shorter startup guide, see [`QUICKSTART.md`](QUICKSTART.md).

---

# 1. Demo Goals

A good demonstration should show the major capabilities of the project without taking too long.

The demo should demonstrate:

- offline wake-word detection
- speech recognition
- local AI inference
- text-to-speech
- Arc Reactor lighting
- wake and sleep states
- Raspberry Pi and Arduino integration

A complete demo can usually be performed in a few minutes.

---

# 2. Before the Demo

Check that the following are connected:

- Raspberry Pi 5
- ATR4650-USB microphone
- Speaker Bonnet
- CQRobot speakers
- Arduino Nano ESP32
- Modulino Pixels
- power bank or other suitable Pi power source

Make sure the Nano ESP32 is connected to the Raspberry Pi through USB.

---

# 3. Check Power

Before starting, verify that the Raspberry Pi is not reporting power problems:

```bash id="rq5c3j"
vcgencmd get_throttled
```

A healthy result is:

```text id="tp9j12"
throttled=0x0
```

If the Pi reports undervoltage, fix the power issue before beginning the demo.

---

# 4. Check the Arduino

Verify that the Nano ESP32 is detected:

```bash id="bfxl63"
arduino-cli board list
```

It should normally appear on a device such as:

```text id="lfgy5m"
/dev/ttyACM0
```

If the Arduino is missing, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

# 5. Start JARVIS

On the Raspberry Pi:

```bash id="h3slcl"
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

Wait for JARVIS to finish loading.

Do not begin speaking until startup is complete.

---

# 6. Explain the Project

A simple introduction for the demo is:

```text id="p1pydm"
This is an offline JARVIS voice assistant built around a Raspberry Pi 5.

The Pi handles the microphone, wake word, speech recognition, local AI, and text-to-speech.

An Arduino Nano ESP32 controls the Arc Reactor lighting.

The entire interaction can run without an internet connection.
```

---

# 7. Demonstrate Wake-Up

Say:

```text id="4hhjx5"
Hey Jarvis
```

Then:

```text id="1fwjiq"
Wake up
```

Watch the Arc Reactor respond.

This demonstrates:

- wake-word detection
- microphone input
- JARVIS state handling
- Raspberry Pi to Arduino communication
- Arc Reactor animation

---

# 8. Demonstrate a Canned Response

Use a simple known phrase:

```text id="okp23j"
Hey Jarvis
How are you?
```

This demonstrates a fast response that does not require full local LLM inference.

Explain that common phrases can be handled directly for faster responses.

---

# 9. Demonstrate the Local AI

Next, ask a general knowledge question.

For example:

```text id="zpxj1d"
Hey Jarvis
What is the largest planet?
```

or:

```text id="eqe2og"
Hey Jarvis
Explain gravity in one sentence.
```

This demonstrates:

```text id="rw8jqf"
Voice
  ↓
Vosk speech recognition
  ↓
Qwen local language model
  ↓
Piper TTS
  ↓
Speakers
```

The answer is generated locally on the Raspberry Pi.

---

# 10. Point Out the Lighting States

During the interaction, explain that the Arc Reactor communicates JARVIS's current state visually.

| State | Effect |
|---|---|
| `IDLE` | Solid orange |
| `WAKE` | Blue animation left → right |
| `LISTENING` | Solid blue |
| `THINKING` | Red bouncing pixel |
| `SPEAKING` | Breathing green |
| `DONE` | Blue animation right → left |

This demonstrates that the lighting is part of the user interface, not just decoration.

---

# 11. Explain the Raspberry Pi / Arduino Split

A useful short explanation is:

```text id="vy6z23"
The Raspberry Pi decides what JARVIS is doing.

The Arduino decides what that state should look like on the LEDs.
```

The communication path is:

```text id="v1mubd"
Raspberry Pi
     │
     │ USB serial
     ▼
Arduino Nano ESP32
     │
     ▼
Modulino Pixels
```

This keeps the LED animations independent from AI processing.

---

# 12. Demonstrate Sleep Mode

Say:

```text id="v5he8e"
Hey Jarvis
Go to sleep
```

JARVIS returns to sleep mode.

Explain that the application remains running.

It simply waits for the next wake phrase.

---

# 13. Demonstrate Re-Wake

To show that sleep mode is not program shutdown, wake JARVIS again:

```text id="8kqp58"
Hey Jarvis
```

Then:

```text id="r2z9fb"
Wake up
```

This demonstrates the complete standby cycle.

---

# 14. Suggested Full Demo Script

A simple complete demo is:

```text id="jdyypk"
Presenter:

This is an offline JARVIS assistant running on a Raspberry Pi 5.
The AI, speech recognition, and voice generation all run locally.
The Arduino controls the Arc Reactor lighting.

User:

Hey Jarvis

Wake up

Hey Jarvis

How are you?

Hey Jarvis

What is the largest planet?

Hey Jarvis

Go to sleep
```

This demonstrates almost every major subsystem without requiring a long presentation.

---

# 15. What Is Happening Internally?

During a normal question:

```text id="1ql3s9"
User speaks
     │
     ▼
ATR4650 microphone
     │
     ▼
OpenWakeWord
     │
     ▼
Vosk
     │
     ▼
Qwen3
     │
     ▼
Piper TTS
     │
     ▼
Speaker Bonnet
     │
     ▼
Speakers
```

At the same time:

```text id="hi33xp"
JARVIS state
     │
     ▼
jarvis_lights.py
     │
     ▼
USB serial
     │
     ▼
Nano ESP32
     │
     ▼
Modulino Pixels
```

---

# 16. Demonstrating Offline Operation

If you specifically want to prove that JARVIS works offline, disconnect the Raspberry Pi from the internet before starting the demo.

Then perform the normal interaction:

```text id="g4en5x"
Hey Jarvis
Wake up
```

followed by:

```text id="18ykm0"
Hey Jarvis
What is the largest planet?
```

The system should still perform:

- wake-word detection
- speech recognition
- local LLM inference
- TTS
- lighting control

No cloud API is required.

---

# 17. Good Demo Questions

Short questions work best.

Examples:

```text id="9sso2p"
Hey Jarvis
What is the largest planet?
```

```text id="cw72jq"
Hey Jarvis
What is a black hole?
```

```text id="iz8jmh"
Hey Jarvis
Explain gravity in one sentence.
```

```text id="mxn5ex"
Hey Jarvis
Why is the sky blue?
```

```text id="ddvow8"
Hey Jarvis
What is the speed of light?
```

Short questions produce a cleaner voice demo than requests requiring long explanations.

---

# 18. Questions to Avoid During a Demo

Avoid questions that require:

- current news
- current weather
- live sports scores
- internet searches
- very recent facts
- extremely long answers

The current JARVIS system is intentionally offline and does not have live web access.

---

# 19. Demo in a Loud Environment

At a party or event:

- keep the microphone close to your mouth
- speak directly toward it
- wait for the wake indication before asking the question
- keep questions short
- avoid standing directly beside loud speakers

The ATR4650 works best when the user's voice is much closer to the microphone than the surrounding noise.

---

# 20. If Wake Detection Fails During a Demo

Try again with:

```text id="o57jjw"
Hey Jarvis
```

spoken clearly and close to the microphone.

If it repeatedly fails:

1. Check that the microphone is still connected.
2. Check for USB problems.
3. Restart JARVIS if necessary.
4. Check Raspberry Pi power.

Do not spend the entire demonstration changing software settings.

---

# 21. If the Arc Reactor Stops Responding

Check whether the Nano ESP32 is still connected:

```bash id="rkd9yj"
arduino-cli board list
```

If it has disappeared, also check:

```bash id="wf6vvw"
vcgencmd get_throttled
```

and:

```bash id="aljk3i"
dmesg -T | tail -50
```

USB instability may indicate a power problem.

---

# 22. If JARVIS Gives a Strange AI Answer

The Qwen model is intentionally small enough to run locally on the Raspberry Pi.

It may occasionally:

- misunderstand a question
- provide an incomplete answer
- give a weaker answer than a large cloud model

For a reliable demo, use short, straightforward questions.

The purpose of the project is to demonstrate a fully local wearable AI pipeline rather than compete with large cloud AI systems.

---

# 23. What to Highlight During a Technical Demo

For a technical audience, emphasize:

## Offline AI

The complete runtime works locally.

## Multi-Model Pipeline

Different models perform different jobs:

```text id="obc368"
OpenWakeWord → wake phrase
Vosk         → speech-to-text
Qwen3        → language generation
Piper        → text-to-speech
```

## Hardware Separation

```text id="cpvzyh"
Pi      → intelligence
Arduino → lighting
```

## Simple Protocol

The Pi sends commands such as:

```text id="xmv7jf"
LISTENING
THINKING
SPEAKING
```

rather than controlling individual LED frames.

## Wearability

The Arc Reactor itself stays lightweight while heavier compute and power components can remain in a pouch.

---

# 24. What to Highlight During a Non-Technical Demo

For a non-technical audience, keep it simple:

```text id="9v4td8"
It recognizes "Hey Jarvis."

It listens to what I say.

It understands the question locally.

It answers through the speakers.

The Arc Reactor changes color depending on what JARVIS is doing.

And it does all of that without needing the internet.
```

---

# 25. Ending the Demo

Finish with:

```text id="plr5j8"
Hey Jarvis
Go to sleep
```

Then, if the project is no longer needed, stop the program from the Raspberry Pi terminal with:

```text id="i69ux1"
Ctrl+C
```

---

# Demo Checklist

Before presenting:

```text id="bgr2k8"
[ ] Raspberry Pi powered correctly

[ ] ATR4650 microphone detected

[ ] Speakers working

[ ] Nano ESP32 detected

[ ] Modulino Pixels responding

[ ] JARVIS starts successfully

[ ] Wake phrase works

[ ] Canned response works

[ ] Local LLM response works

[ ] Piper speech works

[ ] Sleep command works

[ ] No undervoltage warnings
```

---

# Recommended Short Demo

If you only have about one minute:

```text id="0cs88e"
1. Explain that everything runs offline.

2. Say:
   "Hey Jarvis"
   "Wake up"

3. Say:
   "Hey Jarvis"
   "How are you?"

4. Say:
   "Hey Jarvis"
   "What is the largest planet?"

5. Point out the Arc Reactor light changes.

6. Say:
   "Hey Jarvis"
   "Go to sleep"
```

This demonstrates the complete project with minimal setup or explanation.
