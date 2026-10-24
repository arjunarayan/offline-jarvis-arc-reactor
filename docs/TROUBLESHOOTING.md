# Troubleshooting

This guide covers problems encountered while building and running the **Offline JARVIS Arc Reactor**.

For installation instructions, see [`INSTALL.md`](INSTALL.md).

For the hardware list, see [`PARTS.md`](PARTS.md).

---

# 1. Start Here

If something suddenly stops working, check the system in this order:

```text
Power
  ↓
USB connections
  ↓
Arduino connection
  ↓
Microphone
  ↓
Speaker output
  ↓
Python environment
  ↓
AI models
  ↓
JARVIS application
```

Many problems that appear to be software or Arduino failures can actually be caused by unstable Raspberry Pi power.

---

# 2. Raspberry Pi Undervoltage

## Symptoms

Possible symptoms include:

- Arduino suddenly disconnects
- `/dev/ttyACM0` disappears
- lights stop responding
- USB devices repeatedly reconnect
- microphone disappears
- JARVIS becomes unstable after running for several minutes
- Linux reports USB disconnects
- Arduino reconnects under a different USB identity

Check the Raspberry Pi throttling state:

```bash
vcgencmd get_throttled
```

A healthy result is:

```text
throttled=0x0
```

Also check the kernel log:

```bash
dmesg -T | grep -Ei "under-voltage|voltage|usb|disconnect"
```

If you see undervoltage warnings or repeated USB resets, fix the power problem before debugging the software.

## Fix

Use:

- a sufficiently powerful USB-C power source
- a high-quality USB-C cable
- the Belkin BoostCharge Pro power bank used by this project, or another source capable of reliably powering the Raspberry Pi 5

Avoid weak USB power sources and cables that cannot carry enough current.

---

# 3. Arduino Nano ESP32 Disappears

JARVIS normally communicates with the Nano ESP32 through:

```text
/dev/ttyACM0
```

Check whether the port exists:

```bash
ls /dev/ttyACM*
```

If it exists, you should see something similar to:

```text
/dev/ttyACM0
```

You can also run:

```bash
arduino-cli board list
```

## If No Port Appears

Check USB devices:

```bash
lsusb
```

Then inspect recent kernel messages:

```bash
dmesg -T | tail -50
```

Look for:

- USB disconnects
- USB resets
- Arduino devices
- Espressif devices
- `ttyACM` assignments

Unplug the Nano ESP32, wait a few seconds, and reconnect it.

Then run:

```bash
arduino-cli board list
```

again.

---

# 4. Nano Appears as an Espressif/JTAG Device

During development, the Nano ESP32 sometimes appeared as an Espressif/JTAG-related USB device instead of immediately appearing as the expected Arduino serial device.

This does not automatically mean the Nano is damaged.

Try:

1. Disconnecting the Nano.
2. Waiting several seconds.
3. Reconnecting it.
4. Running:

```bash
arduino-cli board list
```

5. Checking:

```bash
ls /dev/ttyACM*
```

If USB identities repeatedly change while the system is running, also check Raspberry Pi power and undervoltage logs.

---

# 5. Permission Denied on `/dev/ttyACM0`

If JARVIS reports a serial permission error, check the port:

```bash
ls -l /dev/ttyACM0
```

Check your groups:

```bash
groups
```

On Raspberry Pi OS, serial access is commonly provided through the `dialout` group.

Add the current user if necessary:

```bash
sudo usermod -aG dialout $USER
```

Then log out and back in, or reboot:

```bash
sudo reboot
```

---

# 6. Arduino Port Changed

Linux may occasionally assign a different number such as:

```text
/dev/ttyACM1
```

instead of:

```text
/dev/ttyACM0
```

Check with:

```bash
arduino-cli board list
```

or:

```bash
ls /dev/ttyACM*
```

If JARVIS is configured specifically for `/dev/ttyACM0`, either reconnect the Arduino so it receives the expected port or update the serial-device setting in the lighting controller.

---

# 7. Arduino Firmware Does Not Compile

The firmware is located at:

```text
firmware/JarvisModulinoLights/JarvisModulinoLights.ino
```

The correct board is:

```text
arduino:esp32:nano_nora
```

Compile with:

```bash
arduino-cli compile \
    --fqbn arduino:esp32:nano_nora \
    --board-options PinNumbers=byGPIONumber \
    firmware/JarvisModulinoLights
```

## `Modulino.h` or Arduino Modulino Library Missing

Install the library:

```bash
arduino-cli lib update-index
arduino-cli lib install "Arduino_Modulino"
```

Then compile again.

---

# 8. Modulino Pixels Do Not Work Correctly

The Nano ESP32 build uses GPIO pin numbering.

Make sure the compile command includes:

```text
--board-options PinNumbers=byGPIONumber
```

Without the correct pin-numbering configuration, the Modulino library may not communicate with the hardware correctly.

Compile again using:

```bash
arduino-cli compile \
    --fqbn arduino:esp32:nano_nora \
    --board-options PinNumbers=byGPIONumber \
    firmware/JarvisModulinoLights
```

Then upload the firmware again.

---

# 9. Firmware Upload Fails

First identify the Arduino port:

```bash
arduino-cli board list
```

If the port is:

```text
/dev/ttyACM0
```

upload with:

```bash
arduino-cli upload \
    -p /dev/ttyACM0 \
    --fqbn arduino:esp32:nano_nora \
    --board-options PinNumbers=byGPIONumber \
    firmware/JarvisModulinoLights
```

If the upload fails:

1. Make sure no other program currently has the serial port open.
2. Stop JARVIS if it is running.
3. Disconnect and reconnect the Nano.
4. Check the port again.
5. Retry the upload.

---

# 10. Arc Reactor Lights Do Not Respond

First verify that the Nano is connected:

```bash
arduino-cli board list
```

Check that the expected serial port exists:

```bash
ls /dev/ttyACM*
```

Then verify that JARVIS can open the port.

If the lights worked initially but stop responding after several minutes, check for USB resets:

```bash
dmesg -T | grep -Ei "usb|ttyACM|disconnect|under-voltage"
```

A power problem can cause the Nano to disconnect even while the Raspberry Pi itself continues running.

---

# 11. Test the Lighting Controller Separately

When diagnosing lighting problems, separate the Arduino from the rest of JARVIS.

The firmware accepts commands such as:

```text
OFF
IDLE
WAKE
LISTENING
THINKING
SPEAKING
DONE
```

This helps determine whether the problem is:

```text
JARVIS software
      ↓
serial connection
      ↓
Arduino firmware
      ↓
Modulino Pixels
```

If the Arduino responds correctly when tested separately, the problem is probably higher in the software stack.

---

# 12. Microphone Is Not Detected

The project uses the:

```text
Audio-Technica ATR4650-USB
```

Check Linux recording devices:

```bash
arecord -l
```

Then activate the project environment:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
```

List SoundDevice devices:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Look for:

```text
ATR4650
```

If it is missing:

1. Disconnect the microphone.
2. Reconnect it.
3. Try another Raspberry Pi USB port.
4. Run `arecord -l` again.
5. Check `dmesg` for USB errors.

---

# 13. Wrong Microphone Device

The JARVIS code searches for a microphone whose name contains:

```text
ATR4650
```

If the operating system reports the microphone under a different name, automatic device selection may fail.

Run:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

and inspect the exact device name.

If necessary, update the microphone-device matching logic in `src/jarvis_ai.py`.

---

# 14. Wake Word Does Not Trigger

The wake phrase is:

```text
Hey Jarvis
```

Check that these OpenWakeWord files exist:

```text
src/models/openwakeword/hey_jarvis_v0.1.onnx
src/models/openwakeword/melspectrogram.onnx
src/models/openwakeword/embedding_model.onnx
```

Also verify that ONNX Runtime is installed:

```bash
source .venv/bin/activate
python -c "import onnxruntime; print('ONNX Runtime OK')"
```

If the model loads correctly but detection is unreliable:

- move the ATR4650 closer to your mouth
- reduce background noise
- speak the full wake phrase clearly
- confirm that the correct microphone is selected

---

# 15. JARVIS Hears the Wake Word but Not the Command

JARVIS uses:

```text
44100 Hz
```

for microphone capture and converts the audio to:

```text
16000 Hz
```

for the speech-processing models.

If wake-word detection works but command transcription does not:

1. Check that the Vosk model exists.
2. Check microphone input.
3. Speak closer to the microphone.
4. Test in a quieter environment.

The Vosk model should be located at:

```text
src/models/vosk-model-small-en-us-0.15/
```

---

# 16. Vosk Model Missing

If JARVIS reports that the speech-recognition model cannot be loaded, check:

```bash
ls src/models/vosk-model-small-en-us-0.15
```

If the directory does not exist, follow the Vosk installation section in [`INSTALL.md`](INSTALL.md).

---

# 17. Local LLM Does Not Load

The Qwen model should exist at:

```text
src/models/llm/Qwen3-0.6B-Q8_0.gguf
```

Check it:

```bash
ls -lh src/models/llm/
```

If the model is missing, JARVIS cannot generate local conversational responses.

Also verify `llama-cpp-python`:

```bash
source .venv/bin/activate
python -c "import llama_cpp; print('llama-cpp-python OK')"
```

---

# 18. Piper TTS Does Not Start

Piper uses its own virtual environment:

```text
src/.piper-venv/
```

Verify it:

```bash
src/.piper-venv/bin/python -m piper --help
```

If that fails, recreate the environment:

```bash
rm -rf src/.piper-venv
python3 -m venv src/.piper-venv
src/.piper-venv/bin/python -m pip install --upgrade pip
src/.piper-venv/bin/python -m pip install piper-tts
```

---

# 19. Piper Voice Model Missing

The voice files should be:

```text
src/models/piper/en_GB-northern_english_male-medium.onnx
src/models/piper/en_GB-northern_english_male-medium.onnx.json
```

Check:

```bash
ls -lh src/models/piper/
```

Both the `.onnx` model and `.onnx.json` configuration file are required.

---

# 20. No Sound From the Speakers

Check Linux playback devices:

```bash
aplay -l
```

Look for:

```text
MAX98357A
```

The JARVIS software expects:

```text
plughw:CARD=MAX98357A,DEV=0
```

Test the speakers directly:

```bash
speaker-test \
    -D plughw:CARD=MAX98357A,DEV=0 \
    -c 2 \
    -t sine
```

If this produces no sound, troubleshoot the audio hardware before troubleshooting JARVIS.

---

# 21. Check Speaker Wiring

The CQRobot speakers connect directly to the Speaker Bonnet screw terminals.

The original JST connectors were removed and the wires stripped.

Check that:

- the wires are securely clamped
- no loose strands touch adjacent terminals
- exposed copper is not excessive
- both speakers are connected properly
- the Speaker Bonnet is seated correctly on the Pi GPIO header

Always power off the Raspberry Pi before changing speaker wiring.

---

# 22. MAX98357A Device Is Missing

Check:

```bash
aplay -l
```

If `MAX98357A` is missing, inspect:

```text
/boot/firmware/config.txt
```

The configuration should include:

```text
dtparam=i2s=on
dtoverlay=max98357a
```

If the normal onboard audio entry is enabled:

```text
dtparam=audio=on
```

the installation guide configures it as:

```text
#dtparam=audio=on
```

After changing the boot configuration, reboot:

```bash
sudo reboot
```

---

# 23. JARVIS Keeps Repeating an Intro or Response

If JARVIS repeatedly says the same startup or introductory phrase:

1. Stop the program with `Ctrl+C`.
2. Restart it.
3. Watch the terminal output.
4. Determine whether the repeated speech is caused by repeated wake detections or repeated application state transitions.
5. Check that the microphone is not picking up JARVIS's own speaker output and triggering another interaction.

Keep the microphone physically separated from the speakers when possible.

Reducing speaker volume during testing can also help determine whether audio feedback is involved.

---

# 24. JARVIS Hears Its Own Voice

Because both the microphone and speakers are active on the same wearable system, JARVIS may sometimes hear its own TTS output.

Possible fixes:

- keep the microphone closer to the user's mouth
- move the speakers farther from the microphone
- reduce speaker volume
- do not process microphone commands while JARVIS is speaking

The software's interaction state should prevent normal speech recognition from treating JARVIS's own response as a new user command.

---

# 25. Lights Freeze While JARVIS Still Runs

Check whether the serial port still exists:

```bash
ls /dev/ttyACM*
```

Then:

```bash
arduino-cli board list
```

If the Arduino disappeared, inspect:

```bash
dmesg -T | tail -100
```

Look for:

```text
USB disconnect
USB reset
ttyACM
under-voltage
```

During development, unstable Raspberry Pi power was an important cause of this type of behavior.

---

# 26. Python Package Import Error

Activate the correct environment:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
```

Then reinstall the repository requirements:

```bash
python -m pip install -r requirements.txt
```

If the missing package is ONNX Runtime:

```bash
python -m pip install onnxruntime
```

Verify:

```bash
python -c "import numpy, scipy, sounddevice, openwakeword, vosk, llama_cpp, serial; print('Dependencies OK')"
```

---

# 27. Wrong Python Environment

Check:

```bash
which python
```

When the main project environment is active, the path should point somewhere inside:

```text
offline-jarvis-arc-reactor/.venv/
```

Piper is different: it intentionally uses:

```text
src/.piper-venv/
```

Do not install the entire JARVIS application into the Piper environment.

---

# 28. JARVIS Starts but Immediately Exits

Run JARVIS directly from a terminal:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

Read the final error shown before the program exits.

Common causes include:

- missing AI model
- missing Python dependency
- microphone not detected
- incorrect audio device
- serial-device problem
- missing Piper environment

Fix the first reported error before diagnosing later components.

---

# 29. `git pull` Would Overwrite Local Changes

If you modified files directly on the Raspberry Pi and then try:

```bash
git pull
```

Git may refuse because the remote repository has newer versions of the same files.

Before doing anything destructive, run:

```bash
git status
```

Do not use commands such as:

```text
git reset --hard
```

unless you are certain the local changes are no longer needed.

The project is normally edited and committed through the Mac/GitHub workflow, then pulled onto the Pi.

---

# 30. Recommended Debugging Commands

These commands are useful when diagnosing the system:

## Raspberry Pi Power

```bash
vcgencmd get_throttled
```

## Recent Kernel Messages

```bash
dmesg -T | tail -100
```

## USB Devices

```bash
lsusb
```

## Arduino Serial Ports

```bash
ls /dev/ttyACM*
```

## Arduino Detection

```bash
arduino-cli board list
```

## Audio Output Devices

```bash
aplay -l
```

## Audio Input Devices

```bash
arecord -l
```

## Python Audio Devices

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## Git State

```bash
git status
```

---

# 31. Debug One Layer at a Time

When something fails, avoid changing multiple parts of the system simultaneously.

Use this order:

```text
1. Verify Raspberry Pi power
2. Verify USB devices
3. Verify Arduino connection
4. Verify Arduino firmware
5. Verify LEDs
6. Verify microphone
7. Verify speakers
8. Verify Python dependencies
9. Verify model files
10. Run JARVIS
```

This makes it much easier to determine which component is actually failing.

---

# Still Having Problems?

Start JARVIS manually:

```bash
cd ~/offline-jarvis-arc-reactor
source .venv/bin/activate
python src/jarvis_ai.py
```

Then capture:

```text
1. The exact error shown in the terminal
2. Output of vcgencmd get_throttled
3. Output of arduino-cli board list
4. Output of aplay -l
5. Output of arecord -l
```

Those five pieces of information cover most hardware and runtime failures in this project.
