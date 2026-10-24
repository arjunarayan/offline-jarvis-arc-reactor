# Usage

This guide explains how to operate the **Offline JARVIS Arc Reactor** after installation is complete.

For installation instructions, see [`INSTALL.md`](INSTALL.md).

For troubleshooting, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

For hardware details, see [`PARTS.md`](PARTS.md).

---

# 1. Start JARVIS

Make sure the following are connected:

- Raspberry Pi 5
- ATR4650-USB microphone
- Speaker Bonnet and speakers
- Arduino Nano ESP32
- Modulino Pixels

On the Raspberry Pi:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

JARVIS will initialize its local components.

These include:

```text
OpenWakeWord     → wake-word detection
Vosk             → speech recognition
Qwen3            → local conversation model
Piper TTS        → speech generation
Nano ESP32       → Arc Reactor lighting
```

No internet connection is required during normal operation.

---

# 2. Sleep Mode

JARVIS starts in sleep mode.

While asleep, it waits for the wake phrase:

```text
Hey Jarvis
```

The Arc Reactor remains in its sleep/idle lighting state while JARVIS waits.

---

# 3. Wake JARVIS

To wake JARVIS, first say:

```text
Hey Jarvis
```

Then say:

```text
Wake up
```

JARVIS will transition from sleep mode into its active state.

---

# 4. Every Command Begins With "Hey Jarvis"

Even after JARVIS has been awakened, each new question or command must begin with:

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
What is a black hole?
```

This prevents JARVIS from continuously listening to every nearby conversation.

---

# 5. Interaction Flow

A normal interaction looks like this:

```text
User
 │
 │ "Hey Jarvis"
 ▼
Wake word detected
 │
 ▼
Arc Reactor enters WAKE state
 │
 ▼
JARVIS listens for the question
 │
 ▼
LISTENING
 │
 ▼
Speech converted to text
 │
 ▼
THINKING
 │
 ▼
Qwen generates response
 │
 ▼
SPEAKING
 │
 ▼
Piper TTS speaks response
 │
 ▼
DONE
 │
 ▼
Return to waiting state
```

---

# 6. Listening Window

After JARVIS begins listening for a command, the user has approximately:

```text
6 seconds
```

to speak.

For best results:

- begin speaking shortly after JARVIS starts listening
- speak clearly
- keep the microphone near your mouth
- avoid very loud background noise
- avoid extremely long questions

If no useful speech is detected during the listening window, JARVIS returns to its waiting state.

---

# 7. Asking Questions

JARVIS can answer general questions using its local Qwen model.

Example:

```text
Hey Jarvis
What is the largest planet?
```

Another example:

```text
Hey Jarvis
Explain gravity.
```

Because the language model runs entirely on the Raspberry Pi, responses may be slower than a cloud AI service.

The tradeoff is that the interaction remains offline.

---

# 8. Canned Commands

Some common phrases can be handled directly without needing a full language-model response.

For example:

```text
Hey Jarvis
How are you?
```

These responses are useful for short, predictable interactions where running the language model is unnecessary.

---

# 9. Put JARVIS Back to Sleep

Say:

```text
Hey Jarvis
Go to sleep
```

JARVIS returns to sleep mode.

Wake-word detection continues running.

To use JARVIS again:

```text
Hey Jarvis
```

followed by:

```text
Wake up
```

---

# 10. Sleep Is Not Raspberry Pi Shutdown

Commands such as:

```text
Go to sleep
Go offline
Shut down
Power off
```

are treated as JARVIS standby commands.

They do **not** shut down Raspberry Pi OS.

The Python application continues running and waits for the next wake sequence.

---

# 11. Arc Reactor Light States

The Arc Reactor visually indicates what JARVIS is doing.

| State | Light Effect | Meaning |
|---|---|---|
| `IDLE` | Solid orange | JARVIS is waiting |
| `WAKE` | Blue animation left → right | Wake phrase detected |
| `LISTENING` | Solid blue | JARVIS is listening |
| `THINKING` | Red pixel bouncing 1 → 8 → 1 | JARVIS is generating a response |
| `SPEAKING` | Breathing green | JARVIS is speaking |
| `DONE` | Blue shutdown animation right → left | Interaction is complete |
| `OFF` | All LEDs off | Lighting is disabled |

The lighting is controlled by the Arduino Nano ESP32 rather than directly by the Raspberry Pi.

---

# 12. Why the Arduino Controls the Lights

The Raspberry Pi runs the voice and AI system.

The Arduino Nano ESP32 handles lighting separately.

The communication path is:

```text
JARVIS software
      │
      ▼
jarvis_lights.py
      │
      ▼
USB serial
      │
      ▼
Arduino Nano ESP32
      │
      ▼
Modulino Pixels
```

This keeps light animations independent from AI processing.

---

# 13. Serial Lighting Commands

The Raspberry Pi can send these commands to the Nano ESP32:

```text
OFF
IDLE
WAKE
LISTENING
THINKING
SPEAKING
DONE
```

The Arduino firmware translates each command into the corresponding animation.

Normal users do not need to send these commands manually.

---

# 14. Speaking Clearly

For reliable voice recognition:

- keep the ATR4650 microphone close to your mouth
- speak at a normal volume
- say the complete wake phrase
- pause briefly after saying `Hey Jarvis`
- then speak the question clearly
- avoid placing the microphone directly beside a speaker

A handheld or near-mouth microphone position works better than placing the microphone far away on the costume.

---

# 15. Using JARVIS in a Noisy Environment

The project is designed for wearable use, including parties or events.

In loud environments:

1. Keep the microphone close to your mouth.
2. Speak the wake phrase clearly.
3. Wait for the wake indication.
4. Speak the command directly into the microphone.

The Arc Reactor light state helps show whether JARVIS actually detected the wake phrase.

If the reactor enters:

```text
WAKE
```

and then:

```text
LISTENING
```

JARVIS is ready for the command.

---

# 16. Avoiding Audio Feedback

JARVIS uses speakers and a microphone at the same time.

To reduce the chance of the microphone hearing JARVIS's own voice:

- keep the microphone away from the speakers
- keep the microphone closer to your mouth
- avoid unnecessarily high speaker volume
- wait until JARVIS finishes speaking before starting another interaction

---

# 17. Offline Operation

After installation, the complete interaction can run without internet access.

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
Qwen3
    │
    ▼
Piper TTS
    │
    ▼
Speakers
```

All of these components run locally on the Raspberry Pi.

---

# 18. What Requires Internet Access?

Internet access is only needed for tasks such as:

- initial operating-system setup
- installing Python packages
- installing Arduino packages
- downloading AI models
- cloning or updating the GitHub repository

Once those resources are installed locally, normal JARVIS conversations do not require the internet.

---

# 19. Stop the JARVIS Program

To completely stop the running application, use the Raspberry Pi terminal and press:

```text
Ctrl+C
```

This is different from telling JARVIS to sleep.

```text
"Go to sleep"
```

means:

```text
Keep running, but wait for the next wake command.
```

`Ctrl+C` means:

```text
Terminate the Python application.
```

---

# 20. Starting JARVIS Again

To restart it:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

Then use:

```text
Hey Jarvis
Wake up
```

---

# 21. Typical Demo

A simple demonstration sequence is:

```text
Hey Jarvis
Wake up
```

Wait for JARVIS to become active.

Then:

```text
Hey Jarvis
How are you?
```

Then ask a general question:

```text
Hey Jarvis
What is the speed of light?
```

Finally:

```text
Hey Jarvis
Go to sleep
```

This demonstrates:

- wake-word detection
- speech recognition
- local AI
- text-to-speech
- Arduino communication
- Arc Reactor lighting
- sleep/wake behavior

---

# Quick Reference

## Wake JARVIS

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

## Stop the Program

From the Raspberry Pi terminal:

```text
Ctrl+C
```

---

# Normal Operating Flow

```text
SLEEP
  │
  │ "Hey Jarvis" + "Wake up"
  ▼
AWAKE
  │
  │ "Hey Jarvis"
  ▼
LISTEN
  │
  ▼
THINK
  │
  ▼
SPEAK
  │
  ▼
WAIT FOR NEXT "HEY JARVIS"
  │
  │ "Hey Jarvis" + "Go to sleep"
  ▼
SLEEP
```
