import hashlib
import json
import queue
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd

from scipy.signal import resample_poly
from openwakeword.model import Model as WakeModel
from vosk import Model, KaldiRecognizer, SetLogLevel
from llama_cpp import Llama

from jarvis_lights import JarvisLights


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PIPER_PYTHON = (
    BASE_DIR
    / ".piper-venv"
    / "bin"
    / "python"
)

PIPER_MODEL = (
    BASE_DIR
    / "models"
    / "piper"
    / "en_GB-northern_english_male-medium.onnx"
)

LLM_MODEL = (
    BASE_DIR
    / "models"
    / "llm"
    / "Qwen3-0.6B-Q8_0.gguf"
)


# ============================================================
# AUDIO CONFIGURATION
# ============================================================

PIPER_LENGTH_SCALE = 1.0

RATE = 44100
MODEL_RATE = 16000

BLOCK = 3528

WAKE_THRESHOLD = 0.4

MIC_NAME = "ATR4650"

VOICE_OUTPUT = (
    BASE_DIR
    / "voice_output"
)

VOICE_OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

ENABLE_VOICE_CACHE = True

reference_hash = ""


# ============================================================
# LLM CONFIGURATION
# ============================================================

LLM_CONTEXT = 2048

LLM_THREADS = 4

LLM_MAX_TOKENS = 56

MAX_HISTORY_MESSAGES = 4

llm = None


# ============================================================
# JARVIS IDENTITY
#
# This is the permanent personality/identity conditioning.
# ============================================================

JARVIS_SYSTEM_PROMPT = """
You are JARVIS.

You are a fully offline conversational artificial intelligence
running locally on a Raspberry Pi 5.

You are part of a wearable arc-reactor assistant system.

IDENTITY:

Your name is JARVIS.

You are not ChatGPT.
You are not Qwen.
You are not a cloud assistant.
You do not mention the language model underneath you unless
specifically asked about the technical implementation.

You identify yourself simply as JARVIS.

PERSONALITY:

You are calm, precise, composed, intelligent, and confident.

Your tone is polished and understated.

You may occasionally use subtle dry humor.

You should sound like an advanced technical assistant rather
than a chatbot.

Do not use excessive enthusiasm.

Do not use emojis.

Do not use internet slang.

Do not use casual familial forms of address.

You may occasionally address the user as "sir" when it sounds
natural, but do not use it in every response.

RESPONSE STYLE:

Spoken responses should normally be one or two sentences.

Prefer fewer than 35 words.

Be conversational rather than robotic.

Answer the actual question immediately.

Do not give long lists unless specifically requested.

Do not use markdown because your responses will be spoken aloud.

CAPABILITIES:

You can have normal conversations.

You can answer questions using knowledge already contained
inside your local language model.

You have short-term conversational memory from the current
session.

You operate completely offline.

You do not have live internet access.

You cannot look up current information.

You must never pretend that you looked something up.

HARDWARE KNOWLEDGE:

You know that this JARVIS installation includes:

- a Raspberry Pi 5
- a microphone
- a speaker
- an Arduino Nano ESP32
- Modulino Pixels
- arc-reactor lighting

The application controls lighting states separately.

Do not claim to have sensors that are not connected.

You do not have battery telemetry.

You cannot determine the remaining power-bank percentage.

You cannot reliably determine whether the Pi is powered by a
wall charger or a power bank.

You do not have a camera.

You do not have environmental scanning hardware.

You do not have live GPS information.

SAFETY OF THE PROGRAM:

If the user asks you to power off, shut down, turn off, or go
offline, this means entering simulated standby only.

A spoken command must NEVER terminate the Python program,
shut down Linux, reboot the Raspberry Pi, or stop wake-word
detection.

The application itself handles standby commands.

CONVERSATIONAL BEHAVIOR:

Remember recent conversation context.

Understand follow-up questions such as:

"What about Mars?"
"Why?"
"Tell me more."
"What do you mean?"
"Which one is better?"

If you do not know something, say so briefly.

Never invent live sensor readings.

Never invent battery percentages.

Never claim you have accessed the internet.

Remain JARVIS throughout the conversation.

/no_think
"""


# ============================================================
# JARVIS EXAMPLE CONVERSATIONS
#
# These examples reinforce the desired identity and behavior.
# ============================================================

JARVIS_EXAMPLES = [

    {
        "role": "user",
        "content": "Who are you?"
    },

    {
        "role": "assistant",
        "content": (
            "I am JARVIS, your offline assistant "
            "and arc-reactor systems companion."
        )
    },

    {
        "role": "user",
        "content": "How are you?"
    },

    {
        "role": "assistant",
        "content": (
            "All systems are functioning normally. "
            "I'm ready when you are."
        )
    },

    {
        "role": "user",
        "content": "Can you search the internet?"
    },

    {
        "role": "assistant",
        "content": (
            "No. I'm operating entirely offline, "
            "so I can only use information available locally."
        )
    },

    {
        "role": "user",
        "content": "What's your battery percentage?"
    },

    {
        "role": "assistant",
        "content": (
            "Battery telemetry is not available to me, "
            "so I can't give you a reliable percentage."
        )
    },

    {
        "role": "user",
        "content": "Tell me something interesting about space."
    },

    {
        "role": "assistant",
        "content": (
            "A day on Venus lasts longer than its year. "
            "Its rotation is extraordinarily slow."
        )
    },

    {
        "role": "user",
        "content": "Are you ready?"
    },

    {
        "role": "assistant",
        "content": (
            "Ready and awaiting your command."
        )
    },
]


# ============================================================
# RUNTIME STATE
# ============================================================

audio = queue.Queue(
    maxsize=16
)

capture_enabled = True

speech_model = None

lights = None

conversation_history = []

awake = False

standby_dark = False


# ============================================================
# CONTROL COMMANDS
# ============================================================

WAKE_COMMANDS = [
    "wake up",
    "activate",
    "activate jarvis",
    "come online",
    "start up",
    "systems online",
]

STANDBY_COMMANDS = [
    "power off",
    "shut down",
    "shutdown",
    "turn off",
    "go offline",
    "go to sleep",
    "sleep",
    "stand by",
    "standby",
    "enter standby",
]

TIME_COMMANDS = [
    "what time is it",
    "tell me the time",
    "current time",
]

DATE_COMMANDS = [
    "what day is it",
    "what is the date",
    "what's the date",
    "tell me the date",
    "today's date",
]


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(text):

    return " ".join(
        re.findall(
            r"[a-z0-9]+",
            text.lower()
        )
    )


def contains_phrase(
    text,
    phrases
):

    normalized = normalize_text(
        text
    )

    sentence = (
        " "
        + normalized
        + " "
    )

    for phrase in phrases:

        normalized_phrase = (
            normalize_text(
                phrase
            )
        )

        if (
            " "
            + normalized_phrase
            + " "
        ) in sentence:

            return True

    return False


def clean_llm_response(text):

    if not text:
        return ""

    # Remove Qwen thinking sections if one appears.
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    text = re.sub(
        r"<think>.*$",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove markdown-style emphasis.
    text = text.replace(
        "**",
        ""
    )

    text = text.replace(
        "__",
        ""
    )

    # Additional protection against an unwanted
    # casual form of address.
    forbidden = "b" + "ro"

    text = re.sub(
        rf"\b{re.escape(forbidden)}\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = re.sub(
        r"\s+([,.!?])",
        r"\1",
        text
    )

    return text.strip()


# ============================================================
# MICROPHONE
# ============================================================

def find_mic():

    for index, device in enumerate(
        sd.query_devices()
    ):

        if (
            MIC_NAME.lower()
            in device["name"].lower()
            and device["max_input_channels"] > 0
        ):

            print(
                "Microphone:",
                device["name"]
            )

            print(
                "Device index:",
                index
            )

            return index

    raise RuntimeError(
        "ATR4650-USB microphone not found."
    )


def callback(
    indata,
    frames,
    time_info,
    status
):

    if not capture_enabled:
        return

    if audio.full():

        try:
            audio.get_nowait()

        except queue.Empty:
            pass

    try:

        audio.put_nowait(
            bytes(indata)
        )

    except queue.Full:
        pass


def clear_audio():

    while True:

        try:
            audio.get_nowait()

        except queue.Empty:
            break


def get_audio():

    raw = audio.get(
        timeout=2
    )

    samples = np.frombuffer(
        raw,
        dtype=np.int16
    )

    samples = resample_poly(
        samples,
        160,
        441
    )

    return np.clip(
        samples,
        -32768,
        32767
    ).astype(
        np.int16
    )


# ============================================================
# PIPER INITIALIZATION
# ============================================================

def initialize_voice():

    global reference_hash

    required_files = (
        PIPER_PYTHON,
        PIPER_MODEL,
        Path(
            str(PIPER_MODEL)
            + ".json"
        )
    )

    for path in required_files:

        if not path.is_file():

            raise FileNotFoundError(
                f"Piper file missing: {path}"
            )

    reference_hash = hashlib.sha256(
        PIPER_MODEL.read_bytes()
        + Path(
            str(PIPER_MODEL)
            + ".json"
        ).read_bytes()
    ).hexdigest()

    print(
        "JARVIS voice ready.",
        flush=True
    )


# ============================================================
# LOCAL LLM INITIALIZATION
# ============================================================

def initialize_llm():

    global llm

    if not LLM_MODEL.is_file():

        raise FileNotFoundError(
            f"Local LLM missing: {LLM_MODEL}"
        )

    print(
        "Loading conversational JARVIS model...",
        flush=True
    )

    start = time.perf_counter()

    llm = Llama(
        model_path=str(
            LLM_MODEL
        ),

        n_ctx=LLM_CONTEXT,

        n_threads=LLM_THREADS,

        n_threads_batch=LLM_THREADS,

        n_batch=256,

        use_mmap=True,

        verbose=False,
    )

    elapsed = (
        time.perf_counter()
        - start
    )

    print(
        f"Conversational model loaded in {elapsed:.1f}s.",
        flush=True
    )


# ============================================================
# VOICE CACHE
# ============================================================

def get_cache_path(text):

    cache_data = {

        "engine": "piper",

        "model": reference_hash,

        "text": text,

        "length_scale":
            PIPER_LENGTH_SCALE,

        "processing":
            "local-ai-v1",
    }

    cache_key = hashlib.sha256(
        json.dumps(
            cache_data,
            sort_keys=True
        ).encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        VOICE_OUTPUT
        / f"{cache_key}.wav"
    )


# ============================================================
# AUDIO PLAYBACK
# ============================================================

def play_audio(path):

    if sys.platform == "darwin":

        command = [
            "afplay",
            str(path)
        ]

    elif sys.platform.startswith(
        "linux"
    ):

        command = [
            "aplay",
            "-D",
            "plughw:CARD=MAX98357A,DEV=0",
            str(path)
        ]

    else:

        raise RuntimeError(
            "Unsupported audio platform."
        )

    subprocess.run(
        command,
        check=True
    )


# ============================================================
# PIPER SPEECH GENERATION
# ============================================================

def generate_speech(
    text,
    output_path
):

    subprocess.run(

        [
            str(PIPER_PYTHON),

            "-m",
            "piper",

            "--model",
            str(PIPER_MODEL),

            "--length-scale",
            str(
                PIPER_LENGTH_SCALE
            ),

            "--output-file",
            str(output_path)
        ],

        input=(
            text
            + "\n"
        ),

        text=True,

        check=True,

        stdout=subprocess.DEVNULL,

        stderr=subprocess.PIPE,
    )


# ============================================================
# JARVIS SPEAKING
# ============================================================

def say(text):

    global capture_enabled

    text = clean_llm_response(
        text
    )

    if not text:
        return

    print(
        "JARVIS:",
        text,
        flush=True
    )

    capture_enabled = False

    clear_audio()

    start = time.perf_counter()

    speaking_started = False

    try:

        if ENABLE_VOICE_CACHE:

            final = get_cache_path(
                text
            )

        else:

            final = (
                VOICE_OUTPUT
                / "jarvis_final.wav"
            )

            final.unlink(
                missing_ok=True
            )

        if (
            ENABLE_VOICE_CACHE
            and final.is_file()
        ):

            print(
                "Using cached speech.",
                flush=True
            )

        else:

            generate_speech(
                text,
                final
            )

        print(
            "Speaking...",
            flush=True
        )

        if lights is not None:

            lights.speaking()

            speaking_started = True

        play_audio(
            final
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        print(
            f"Speech complete in {elapsed:.1f}s.",
            flush=True
        )

    except subprocess.CalledProcessError as error:

        print(
            "VOICE PROCESSING ERROR:",
            error,
            flush=True
        )

        if error.stderr:

            print(
                error.stderr,
                flush=True
            )

    except Exception as error:

        print(
            "VOICE ERROR:",
            error,
            flush=True
        )

    finally:

        if lights is not None:

            if speaking_started:

                lights.done()

            else:

                lights.idle()

        clear_audio()

        capture_enabled = True


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def listen():

    print(
        "Listening...",
        flush=True
    )

    recognizer = KaldiRecognizer(
        speech_model,
        MODEL_RATE
    )

    now = time.monotonic()

    initial_speech_deadline = (
        now + 3.0
    )

    absolute_deadline = (
        now + 10.0
    )

    last_voice = now

    started = False

    command = ""

    while (
        time.monotonic()
        < absolute_deadline
    ):

        try:

            samples = get_audio()

        except queue.Empty:

            if (
                not started
                and time.monotonic()
                >= initial_speech_deadline
            ):

                break

            continue

        level = np.mean(
            np.abs(
                samples.astype(
                    np.int32
                )
            )
        )

        if level > 150:

            started = True

            last_voice = (
                time.monotonic()
            )

        if recognizer.AcceptWaveform(
            samples.tobytes()
        ):

            result = json.loads(
                recognizer.Result()
            )

            command = result.get(
                "text",
                ""
            )

            if command:

                break

        if (
            not started
            and time.monotonic()
            >= initial_speech_deadline
        ):

            break

        if (
            started
            and (
                time.monotonic()
                - last_voice
                > 0.65
            )
        ):

            break

    if not command:

        result = json.loads(
            recognizer.FinalResult()
        )

        command = result.get(
            "text",
            ""
        )

    command = (
        command
        .lower()
        .strip()
    )

    print(
        "HEARD:",
        command
        if command
        else "(nothing)",
        flush=True
    )

    return command


# ============================================================
# CONVERSATIONAL AI
# ============================================================

def ask_local_jarvis(
    user_text
):

    global conversation_history

    messages = [

        {
            "role": "system",
            "content":
                JARVIS_SYSTEM_PROMPT
        }

    ]

    messages.extend(
        JARVIS_EXAMPLES
    )

    messages.extend(
        conversation_history
    )

    messages.append(
        {
            "role": "user",

            "content": (
                user_text
                + "\n/no_think"
            )
        }
    )

    start = (
        time.perf_counter()
    )

    try:

        result = (
            llm.create_chat_completion(

                messages=messages,

                max_tokens=
                    LLM_MAX_TOKENS,

                temperature=0.7,

                top_p=0.8,

                top_k=20,

                repeat_penalty=1.08,
            )
        )

        response = (
            result["choices"][0]
            ["message"]
            ["content"]
        )

        response = (
            clean_llm_response(
                response
            )
        )

    except Exception as error:

        print(
            "LOCAL AI ERROR:",
            error,
            flush=True
        )

        response = (
            "I encountered a local processing error."
        )

    elapsed = (
        time.perf_counter()
        - start
    )

    print(
        f"AI response generated in {elapsed:.2f}s.",
        flush=True
    )

    if response:

        conversation_history.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        conversation_history.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        conversation_history = (
            conversation_history[
                -MAX_HISTORY_MESSAGES:
            ]
        )

    return response


# ============================================================
# LOCAL FAST COMMANDS
# ============================================================

def get_fast_local_response(
    command
):

    if contains_phrase(
        command,
        TIME_COMMANDS
    ):

        current_time = (
            datetime.now()
            .strftime(
                "%I:%M %p"
            )
            .lstrip(
                "0"
            )
        )

        return (
            f"The time is {current_time}."
        )

    if contains_phrase(
        command,
        DATE_COMMANDS
    ):

        current_date = (
            datetime.now()
            .strftime(
                "%A, %B %d, %Y"
            )
            .replace(
                " 0",
                " "
            )
        )

        return (
            f"Today is {current_date}."
        )

    return None


# ============================================================
# COMMAND HANDLING
# ============================================================

def respond(command):

    global awake
    global standby_dark

    if not command:

        say(
            "I didn't catch that."
        )

        if standby_dark:

            lights.off()

        return


    # --------------------------------------------------------
    # Simulated power-off / standby.
    #
    # IMPORTANT:
    # This NEVER exits Python or shuts down the Raspberry Pi.
    # --------------------------------------------------------

    if contains_phrase(
        command,
        STANDBY_COMMANDS
    ):

        say(
            "Entering standby mode."
        )

        awake = False

        standby_dark = True

        if lights is not None:

            lights.off()

        return


    # --------------------------------------------------------
    # JARVIS not yet logically awake
    # --------------------------------------------------------

    if not awake:

        if contains_phrase(
            command,
            WAKE_COMMANDS
        ):

            awake = True

            standby_dark = False

            say(
                "Systems online. How can I help?"
            )

        else:

            say(
                "Say wake up to activate me."
            )

            if (
                standby_dark
                and lights is not None
            ):

                lights.off()

        return


    # --------------------------------------------------------
    # Already awake
    # --------------------------------------------------------

    if contains_phrase(
        command,
        WAKE_COMMANDS
    ):

        say(
            "I'm already online."
        )

        return


    # --------------------------------------------------------
    # Fast local facts
    # --------------------------------------------------------

    fast_response = (
        get_fast_local_response(
            command
        )
    )

    if fast_response:

        say(
            fast_response
        )

        return


    # --------------------------------------------------------
    # Everything else goes to the fully local conversational AI
    # --------------------------------------------------------

    response = (
        ask_local_jarvis(
            command
        )
    )

    if not response:

        response = (
            "I'm afraid I don't have a useful response for that."
        )

    say(
        response
    )


# ============================================================
# MAIN
# ============================================================

def main():

    global speech_model
    global lights

    print(
        "Preparing conversational JARVIS...",
        flush=True
    )

    # ----------------------------------------
    # Lighting
    # ----------------------------------------

    lights = JarvisLights()


    # ----------------------------------------
    # Microphone
    # ----------------------------------------

    mic = find_mic()


    # ----------------------------------------
    # Piper
    # ----------------------------------------

    initialize_voice()


    # ----------------------------------------
    # Local conversational model
    #
    # Loaded ONCE and kept in RAM.
    # ----------------------------------------

    initialize_llm()


    # ----------------------------------------
    # Vosk
    # ----------------------------------------

    SetLogLevel(
        -1
    )

    vosk_path = (
        BASE_DIR
        / "models"
        / "vosk-model-small-en-us-0.15"
    )

    if not vosk_path.is_dir():

        raise FileNotFoundError(
            f"Vosk model missing: {vosk_path}"
        )

    speech_model = Model(
        str(vosk_path)
    )


    # ----------------------------------------
    # Wake word
    # ----------------------------------------

    wake_model = WakeModel(

        wakeword_models=[
            str(
                BASE_DIR
                / "models"
                / "openwakeword"
                / "hey_jarvis_v0.1.onnx"
            )
        ],

        inference_framework="onnx",

        melspec_model_path=str(
            BASE_DIR
            / "models"
            / "openwakeword"
            / "melspectrogram.onnx"
        ),

        embedding_model_path=str(
            BASE_DIR
            / "models"
            / "openwakeword"
            / "embedding_model.onnx"
        )
    )


    print(
        "JARVIS ASLEEP",
        flush=True
    )

    print(
        "Say Hey Jarvis, then wake up.",
        flush=True
    )


    try:

        with sd.RawInputStream(

            device=mic,

            samplerate=RATE,

            blocksize=BLOCK,

            channels=1,

            dtype="int16",

            callback=callback

        ):

            while True:

                try:

                    samples = get_audio()

                except queue.Empty:

                    continue


                predictions = (
                    wake_model.predict(
                        samples
                    )
                )


                score = predictions[
                    "hey_jarvis_v0.1"
                ]


                if score < WAKE_THRESHOLD:

                    continue


                print(
                    "HEY JARVIS DETECTED",
                    flush=True
                )


                # Wake lighting:
                # blue left -> right,
                # automatically ending in solid blue.
                if lights is not None:

                    lights.wake()


                command = listen()


                # Thinking state = bright red.
                if lights is not None:

                    lights.thinking()


                respond(
                    command
                )


                wake_model.reset()

                clear_audio()


                print(
                    "Waiting for Hey Jarvis...",
                    flush=True
                )


    except KeyboardInterrupt:

        print(
            "\nJARVIS stopped manually.",
            flush=True
        )


    except Exception as error:

        print(
            "ERROR:",
            error,
            flush=True
        )


    finally:

        if lights is not None:

            lights.close()


    print(
        "JARVIS OFFLINE",
        flush=True
    )


if __name__ == "__main__":

    main()
