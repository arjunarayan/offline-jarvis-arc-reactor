import time

import serial


class JarvisLights:
    def __init__(self, port="/dev/ttyACM0", baud=115200):
        self.serial = None

        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=1,
                write_timeout=1,
            )

            # Opening the USB serial connection may reset the Nano.
            time.sleep(2)

            print("[LIGHTS] Connected to Nano ESP32")

            # JARVIS starts in idle mode.
            self.idle()

        except Exception as error:
            print(f"[LIGHTS] Could not connect: {error}")
            print("[LIGHTS] JARVIS will continue without lights.")

    def send(self, command):
        if self.serial is None:
            return

        try:
            message = command.strip().upper() + "\n"

            self.serial.write(
                message.encode("utf-8")
            )

            self.serial.flush()

            print(
                f"[LIGHTS] {command.upper()}",
                flush=True
            )

        except Exception as error:
            print(
                f"[LIGHTS] Send failed: {error}",
                flush=True
            )

    def off(self):
        self.send("OFF")

    def idle(self):
        self.send("IDLE")

    def wake(self):
        self.send("WAKE")

    def listening(self):
        self.send("LISTENING")

    def thinking(self):
        self.send("THINKING")

    def speaking(self):
        self.send("SPEAKING")

    def done(self):
        self.send("DONE")

    def close(self):
        if self.serial is None:
            return

        try:
            # When JARVIS itself exits, turn the reactor off.
            self.off()

            time.sleep(0.1)

            self.serial.close()

        except Exception:
            pass
