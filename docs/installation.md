# Installation

This guide installs the **Offline JARVIS Arc Reactor** software on a Raspberry Pi 5.

After the initial setup and model downloads are complete, JARVIS can operate entirely offline.

> All terminal commands in this guide should be run on the **Raspberry Pi**.

For the hardware used in this build, see [`PARTS.md`](PARTS.md).

---

# 1. Requirements

The final build uses:

- Raspberry Pi 5
- Raspberry Pi OS 64-bit
- Audio-Technica ATR4650-USB microphone
- Adafruit I2S 3W Stereo Speaker Bonnet
- 3W / 4Ω speakers
- Arduino Nano ESP32
- Arduino Modulino Pixels
- Internet access during initial installation

After installation, normal JARVIS operation does not require an internet connection.

---

# 2. Clone the Repository

On the Raspberry Pi:

```bash
cd ~
git clone https://github.com/arjunarayan/offline-jarvis-arc-reactor.git
cd offline-jarvis-arc-reactor
```

If the repository is already cloned:

```bash
cd ~/offline-jarvis-arc-reactor
git pull
```

---

# 3. Install Raspberry Pi System Packages

Update the Raspberry Pi:

```bash
sudo apt update
sudo apt upgrade -y
```

Install the required packages:

```bash
sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    git \
    curl \
    unzip \
    alsa-utils \
    libportaudio2 \
    portaudio19-dev
```

---

# 4. Create the Main Python Environment

From the repository root:

```bash
cd ~/offline-jarvis-arc-reactor
python3 -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Upgrade the Python packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

JARVIS uses packages including:

- NumPy
- SciPy
- SoundDevice
- OpenWakeWord
- Vosk
- llama-cpp-python
- PySerial

Install ONNX Runtime for OpenWakeWord:

```bash
python -m pip install onnxruntime
```

Verify the main Python dependencies:

```bash
python -c "import numpy, scipy, sounddevice, openwakeword, vosk, llama_cpp, serial; print('Python dependencies OK')"
```

Expected output:

```text
Python dependencies OK
```

---

# 5. Install Piper TTS

JARVIS uses **Piper TTS** for completely local text-to-speech.

The project uses a separate Python virtual environment for Piper.

Create it:

```bash
cd ~/offline-jarvis-arc-reactor
python3 -m venv src/.piper-venv
```

Install Piper:

```bash
src/.piper-venv/bin/python -m pip install --upgrade pip
src/.piper-venv/bin/python -m pip install piper-tts
```

Verify the installation:

```bash
src/.piper-venv/bin/python -m piper --help
```

---

# 6. Create the Model Directories

AI model files are not stored in the Git repository because they are large.

Create the required directories:

```bash
cd ~/offline-jarvis-arc-reactor

mkdir -p src/models/piper
mkdir -p src/models/llm
mkdir -p src/models/openwakeword
```

When setup is complete, the model directory should look similar to:

```text
src/
└── models/
    ├── llm/
    │   └── Qwen3-0.6B-Q8_0.gguf
    │
    ├── openwakeword/
    │   ├── hey_jarvis_v0.1.onnx
    │   ├── melspectrogram.onnx
    │   └── embedding_model.onnx
    │
    ├── piper/
    │   ├── en_GB-northern_english_male-medium.onnx
    │   └── en_GB-northern_english_male-medium.onnx.json
    │
    └── vosk-model-small-en-us-0.15/
```

---

# 7. Install the Piper Voice

The final JARVIS build uses the Piper voice:

```text
en_GB-northern_english_male-medium
```

The following two files are required:

```text
en_GB-northern_english_male-medium.onnx
en_GB-northern_english_male-medium.onnx.json
```

Place both files in:

```text
src/models/piper/
```

The final paths should be:

```text
src/models/piper/en_GB-northern_english_male-medium.onnx
src/models/piper/en_GB-northern_english_male-medium.onnx.json
```

---

# 8. Install the Local LLM

JARVIS uses a local GGUF language model:

```text
Qwen3-0.6B-Q8_0.gguf
```

Place the model in:

```text
src/models/llm/
```

The final path should be:

```text
src/models/llm/Qwen3-0.6B-Q8_0.gguf
```

The model is loaded locally using `llama-cpp-python`.

JARVIS does not require a cloud LLM API during normal operation.

---

# 9. Install the Vosk Speech Recognition Model

JARVIS uses:

```text
vosk-model-small-en-us-0.15
```

Download the model:

```bash
curl -L \
    https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip \
    -o /tmp/vosk-model.zip
```

Extract it:

```bash
unzip /tmp/vosk-model.zip -d src/models/
```

Remove the downloaded ZIP:

```bash
rm /tmp/vosk-model.zip
```

The final model directory should be:

```text
src/models/vosk-model-small-en-us-0.15/
```

---

# 10. Install the OpenWakeWord Models

JARVIS uses the wake phrase:

```text
Hey Jarvis
```

The project uses OpenWakeWord with ONNX models.

The required files are:

```text
hey_jarvis_v0.1.onnx
melspectrogram.onnx
embedding_model.onnx
```

Place them in:

```text
src/models/openwakeword/
```

The final paths should be:

```text
src/models/openwakeword/hey_jarvis_v0.1.onnx
src/models/openwakeword/melspectrogram.onnx
src/models/openwakeword/embedding_model.onnx
```

---

# 11. Configure the Speaker Bonnet

JARVIS sends audio through the Adafruit MAX98357A I2S Speaker Bonnet.

Edit the Raspberry Pi boot configuration:

```bash
sudo nano /boot/firmware/config.txt
```

If this line is enabled:

```text
dtparam=audio=on
```

comment it out:

```text
#dtparam=audio=on
```

Enable I2S and the MAX98357A overlay:

```text
dtparam=i2s=on
dtoverlay=max98357a
```

Save the file and reboot:

```bash
sudo reboot
```

After rebooting, list the available playback devices:

```bash
aplay -l
```

Look for a device named:

```text
MAX98357A
```

Test the speakers:

```bash
speaker-test \
    -D plughw:CARD=MAX98357A,DEV=0 \
    -c 2 \
    -t sine
```

Press:

```text
Ctrl+C
```

to stop the speaker test.

---

# 12. Verify the ATR4650-USB Microphone

Connect the Audio-Technica ATR4650-USB microphone to the Raspberry Pi.

List Linux recording devices:

```bash
arecord -l
```

Activate the JARVIS environment:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
```

List the devices detected by Python:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Look for a device containing:

```text
ATR4650
```

The final JARVIS audio configuration uses:

```text
Microphone sample rate: 44100 Hz
Model sample rate:      16000 Hz
Block size:             3528
Channels:               1
Audio format:           int16
```

The software resamples microphone audio from 44.1 kHz to 16 kHz before passing it to the speech and wake-word models.

---

# 13. Install Arduino CLI

The Arduino Nano ESP32 controls the Arc Reactor lights.

Check whether Arduino CLI is already installed:

```bash
arduino-cli version
```

If Arduino CLI is not installed:

```bash
cd ~
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

Install it system-wide:

```bash
sudo install -m 755 ~/bin/arduino-cli /usr/local/bin/arduino-cli
```

Verify:

```bash
arduino-cli version
```

---

# 14. Install Arduino Nano ESP32 Support

Update the Arduino board index:

```bash
arduino-cli core update-index
```

Install the Arduino ESP32 core:

```bash
arduino-cli core install arduino:esp32
```

The board identifier used by this project is:

```text
arduino:esp32:nano_nora
```

---

# 15. Install the Modulino Library

Install the Arduino Modulino library:

```bash
arduino-cli lib update-index
arduino-cli lib install "Arduino_Modulino"
```

The firmware uses:

```cpp
#include <Arduino_Modulino.h>
```

---

# 16. Compile the Arc Reactor Firmware

The Arduino firmware is stored at:

```text
firmware/JarvisModulinoLights/JarvisModulinoLights.ino
```

Connect the Nano ESP32 to the Raspberry Pi through USB.

Go to the repository:

```bash
cd ~/offline-jarvis-arc-reactor
```

Compile the firmware:

```bash
arduino-cli compile \
    --fqbn arduino:esp32:nano_nora \
    --board-options PinNumbers=byGPIONumber \
    firmware/JarvisModulinoLights
```

This project uses GPIO pin numbering with the Nano ESP32.

---

# 17. Find the Arduino USB Port

Run:

```bash
arduino-cli board list
```

The Nano ESP32 will normally appear as a serial device such as:

```text
/dev/ttyACM0
```

The JARVIS lighting controller communicates with the Arduino at:

```text
115200 baud
```

---

# 18. Upload the Arc Reactor Firmware

If the Nano ESP32 appears as `/dev/ttyACM0`, upload with:

```bash
arduino-cli upload \
    -p /dev/ttyACM0 \
    --fqbn arduino:esp32:nano_nora \
    --board-options PinNumbers=byGPIONumber \
    firmware/JarvisModulinoLights
```

After uploading, the Raspberry Pi can control the Modulino Pixels by sending serial commands to the Arduino.

Supported commands include:

```text
OFF
IDLE
WAKE
LISTENING
THINKING
SPEAKING
DONE
```

---

# 19. Check the Final Directory Structure

The important project files should look similar to:

```text
offline-jarvis-arc-reactor/
├── .gitignore
├── README.md
├── requirements.txt
│
├── docs/
│   ├── INSTALL.md
│   └── PARTS.md
│
├── firmware/
│   └── JarvisModulinoLights/
│       └── JarvisModulinoLights.ino
│
└── src/
    ├── jarvis_ai.py
    ├── jarvis_lights.py
    │
    ├── .piper-venv/
    │
    └── models/
        ├── llm/
        │   └── Qwen3-0.6B-Q8_0.gguf
        │
        ├── openwakeword/
        │   ├── hey_jarvis_v0.1.onnx
        │   ├── melspectrogram.onnx
        │   └── embedding_model.onnx
        │
        ├── piper/
        │   ├── en_GB-northern_english_male-medium.onnx
        │   └── en_GB-northern_english_male-medium.onnx.json
        │
        └── vosk-model-small-en-us-0.15/
```

Virtual environments, AI model files, generated audio, cache files, and other local runtime data should remain excluded from Git.

---

# 20. Run JARVIS

Before starting JARVIS, connect:

- ATR4650-USB microphone
- Speaker Bonnet
- Speakers
- Arduino Nano ESP32
- Modulino Pixels

Activate the Python environment:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
```

Start JARVIS:

```bash
python src/jarvis_ai.py
```

JARVIS initializes the major components:

1. Arduino lighting controller
2. USB microphone
3. Piper TTS
4. Local Qwen language model
5. Vosk speech recognition
6. OpenWakeWord

---

# 21. Using JARVIS

JARVIS begins in sleep mode.

To wake it, say:

```text
Hey Jarvis
```

Then:

```text
Wake up
```

While JARVIS is awake, every new command or question should still begin with:

```text
Hey Jarvis
```

For example:

```text
Hey Jarvis
How are you?
```

To return JARVIS to sleep mode:

```text
Hey Jarvis
Go to sleep
```

Sleep-related voice commands place JARVIS into standby.

They do not shut down the Raspberry Pi.

---

# 22. Arc Reactor Light States

The final firmware uses the following states:

| JARVIS State | Arc Reactor Effect |
|---|---|
| IDLE | Solid orange |
| WAKE | Blue animation from left to right |
| LISTENING | Solid blue |
| THINKING | Red pixel bouncing from 1 → 8 → 1 |
| SPEAKING | Breathing green |
| DONE | Blue shutdown animation from right to left |
| OFF | All LEDs off |

---

# 23. Offline Components

Once setup is complete, normal JARVIS operation is local.

The major software components are:

```text
Wake word       → OpenWakeWord
Speech-to-text  → Vosk
Conversation    → Qwen3 local GGUF model
Text-to-speech  → Piper TTS
Lighting        → Arduino Nano ESP32 + Modulino Pixels
```

No OpenAI API or other cloud AI service is required during normal operation.

---

# 24. Stop JARVIS

To terminate the Python program from the terminal:

```text
Ctrl+C
```

Spoken commands such as:

```text
Go to sleep
Power off
Shut down
Go offline
```

are treated as JARVIS standby commands.

They intentionally do not shut down Linux or power off the Raspberry Pi.

---

# Installation Complete

To start JARVIS again:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

Then say:

```text
Hey Jarvis
Wake up
```
