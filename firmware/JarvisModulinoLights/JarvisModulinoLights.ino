#include <Arduino_Modulino.h>

// ============================================================
// JARVIS ARC REACTOR LIGHTING
// Arduino Nano ESP32 + Modulino Pixels
//
// Serial protocol expected by jarvis_lights.py:
//   OFF
//   IDLE
//   WAKE
//   LISTENING
//   THINKING
//   SPEAKING
//   DONE
//
// Baud: 115200
//
// THINKING animation:
//   One red pixel bounces:
//   1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8
//                                  then
//   8 -> 7 -> 6 -> 5 -> 4 -> 3 -> 2 -> 1
//
// All animations use millis(), not delay(), so a new serial
// command can interrupt an animation immediately.
// ============================================================


ModulinoPixels pixels;


// ============================================================
// COLORS / BRIGHTNESS
// ============================================================

const uint8_t IDLE_BRIGHTNESS = 18;
const uint8_t BLUE_BRIGHTNESS = 35;
const uint8_t THINKING_BRIGHTNESS = 42;

const uint8_t SPEAKING_MIN_BRIGHTNESS = 8;
const uint8_t SPEAKING_MAX_BRIGHTNESS = 42;


// Orange is custom because Modulino's built-in palette does
// not include the exact JARVIS idle orange we want.
const ModulinoColor IDLE_ORANGE(
        255,
        72,
        0
);


// ============================================================
// ANIMATION SPEEDS
// ============================================================

const unsigned long WAKE_STEP_MS = 80;
const unsigned long THINKING_STEP_MS = 90;
const unsigned long DONE_STEP_MS = 80;
const unsigned long SPEAKING_STEP_MS = 28;


// ============================================================
// STATE
// ============================================================

enum LightState {
        STATE_OFF,
        STATE_IDLE,
        STATE_WAKE,
        STATE_LISTENING,
        STATE_THINKING,
        STATE_SPEAKING,
        STATE_DONE
};

LightState currentState = STATE_OFF;


// ============================================================
// SERIAL INPUT
// ============================================================

String serialBuffer;


// ============================================================
// WAKE STATE
// ============================================================

int wakePixel = 0;
unsigned long wakeLastStep = 0;


// ============================================================
// THINKING STATE
// ============================================================

int thinkingPixel = 0;
int thinkingDirection = 1;
unsigned long thinkingLastStep = 0;


// ============================================================
// SPEAKING STATE
// ============================================================

int speakingBrightness = SPEAKING_MIN_BRIGHTNESS;
int speakingDirection = 1;
unsigned long speakingLastStep = 0;


// ============================================================
// DONE STATE
// ============================================================

int donePixel = 7;
unsigned long doneLastStep = 0;


// ============================================================
// PIXEL HELPERS
// ============================================================

void showAll(
        ModulinoColor color,
        uint8_t brightness
) {

        for (
                int i = 0;
                i < 8;
                i++
        ) {

                pixels.set(
                        i,
                        color,
                        brightness
                );
        }

        pixels.show();
}


void clearAll() {

        pixels.clear();
        pixels.show();
}


void showSinglePixel(
        int pixel,
        ModulinoColor color,
        uint8_t brightness
) {

        pixels.clear();

        pixels.set(
                pixel,
                color,
                brightness
        );

        pixels.show();
}


// ============================================================
// STATE ENTRY
// ============================================================

void enterState(
        LightState newState
) {

        currentState = newState;

        unsigned long now = millis();


        switch (
                currentState
        ) {


                // ------------------------------------------------
                // OFF
                // ------------------------------------------------

                case STATE_OFF:

                        clearAll();

                        break;


                // ------------------------------------------------
                // IDLE
                // Solid orange.
                // ------------------------------------------------

                case STATE_IDLE:

                        showAll(
                                IDLE_ORANGE,
                                IDLE_BRIGHTNESS
                        );

                        break;


                // ------------------------------------------------
                // WAKE
                // Blue fills from pixel 1 -> pixel 8,
                // then remains solid blue.
                // ------------------------------------------------

                case STATE_WAKE:

                        clearAll();

                        wakePixel = 0;
                        wakeLastStep = (
                                now
                                - WAKE_STEP_MS
                        );

                        break;


                // ------------------------------------------------
                // LISTENING
                // Solid blue.
                // ------------------------------------------------

                case STATE_LISTENING:

                        showAll(
                                BLUE,
                                BLUE_BRIGHTNESS
                        );

                        break;


                // ------------------------------------------------
                // THINKING
                // One red pixel bouncing left/right.
                // ------------------------------------------------

                case STATE_THINKING:

                        thinkingPixel = 0;
                        thinkingDirection = 1;

                        showSinglePixel(
                                thinkingPixel,
                                RED,
                                THINKING_BRIGHTNESS
                        );

                        thinkingLastStep = now;

                        break;


                // ------------------------------------------------
                // SPEAKING
                // All green with a smooth breathing brightness.
                // ------------------------------------------------

                case STATE_SPEAKING:

                        speakingBrightness =
                                SPEAKING_MIN_BRIGHTNESS;

                        speakingDirection = 1;

                        showAll(
                                GREEN,
                                speakingBrightness
                        );

                        speakingLastStep = now;

                        break;


                // ------------------------------------------------
                // DONE
                // Start solid blue, then turn pixels off
                // from right -> left. Finish in IDLE.
                // ------------------------------------------------

                case STATE_DONE:

                        showAll(
                                BLUE,
                                BLUE_BRIGHTNESS
                        );

                        donePixel = 7;

                        doneLastStep = (
                                now
                                - DONE_STEP_MS
                        );

                        break;
        }
}


// ============================================================
// ANIMATIONS
// ============================================================

void updateWake(
        unsigned long now
) {

        if (
                now
                - wakeLastStep
                < WAKE_STEP_MS
        ) {

                return;
        }

        wakeLastStep = now;


        if (
                wakePixel
                < 8
        ) {

                // Rebuild the complete frame on every step.
                // This guarantees WAKE is visibly an ON/fill
                // animation rather than depending on the
                // Pixels library's previous buffered state.
                pixels.clear();

                for (
                        int i = 0;
                        i <= wakePixel;
                        i++
                ) {

                        pixels.set(
                                i,
                                BLUE,
                                BLUE_BRIGHTNESS
                        );
                }

                pixels.show();

                wakePixel++;

                return;
        }


        // Explicitly finish with all eight pixels blue.
        // Remain solid blue until the next JARVIS command.
        showAll(
                BLUE,
                BLUE_BRIGHTNESS
        );
}


void updateThinking(
        unsigned long now
) {

        if (
                now
                - thinkingLastStep
                < THINKING_STEP_MS
        ) {

                return;
        }

        thinkingLastStep = now;


        thinkingPixel +=
                thinkingDirection;


        if (
                thinkingPixel
                >= 7
        ) {

                thinkingPixel = 7;
                thinkingDirection = -1;
        }

        else if (
                thinkingPixel
                <= 0
        ) {

                thinkingPixel = 0;
                thinkingDirection = 1;
        }


        showSinglePixel(
                thinkingPixel,
                RED,
                THINKING_BRIGHTNESS
        );
}


void updateSpeaking(
        unsigned long now
) {

        if (
                now
                - speakingLastStep
                < SPEAKING_STEP_MS
        ) {

                return;
        }

        speakingLastStep = now;


        speakingBrightness +=
                speakingDirection;


        if (
                speakingBrightness
                >= SPEAKING_MAX_BRIGHTNESS
        ) {

                speakingBrightness =
                        SPEAKING_MAX_BRIGHTNESS;

                speakingDirection = -1;
        }

        else if (
                speakingBrightness
                <= SPEAKING_MIN_BRIGHTNESS
        ) {

                speakingBrightness =
                        SPEAKING_MIN_BRIGHTNESS;

                speakingDirection = 1;
        }


        showAll(
                GREEN,
                speakingBrightness
        );
}


void updateDone(
        unsigned long now
) {

        if (
                now
                - doneLastStep
                < DONE_STEP_MS
        ) {

                return;
        }

        doneLastStep = now;


        if (
                donePixel
                >= 0
        ) {

                pixels.clear(
                        donePixel
                );

                pixels.show();

                donePixel--;

                return;
        }


        enterState(
                STATE_IDLE
        );
}


// ============================================================
// STATE UPDATE
// ============================================================

void updateAnimation() {

        unsigned long now = millis();


        switch (
                currentState
        ) {

                case STATE_WAKE:

                        updateWake(
                                now
                        );

                        break;


                case STATE_THINKING:

                        updateThinking(
                                now
                        );

                        break;


                case STATE_SPEAKING:

                        updateSpeaking(
                                now
                        );

                        break;


                case STATE_DONE:

                        updateDone(
                                now
                        );

                        break;


                default:

                        break;
        }
}


// ============================================================
// SERIAL COMMAND HANDLING
// ============================================================

void handleCommand(
        String command
) {

        command.trim();
        command.toUpperCase();


        if (
                command == "OFF"
        ) {

                enterState(
                        STATE_OFF
                );
        }

        else if (
                command == "IDLE"
        ) {

                enterState(
                        STATE_IDLE
                );
        }

        else if (
                command == "WAKE"
        ) {

                enterState(
                        STATE_WAKE
                );
        }

        else if (
                command == "LISTENING"
        ) {

                enterState(
                        STATE_LISTENING
                );
        }

        else if (
                command == "THINKING"
        ) {

                enterState(
                        STATE_THINKING
                );
        }

        else if (
                command == "SPEAKING"
        ) {

                enterState(
                        STATE_SPEAKING
                );
        }

        else if (
                command == "DONE"
        ) {

                enterState(
                        STATE_DONE
                );
        }
}


void readSerialCommands() {

        while (
                Serial.available()
        ) {

                char incoming =
                        Serial.read();


                if (
                        incoming == '\n'
                ) {

                        handleCommand(
                                serialBuffer
                        );

                        serialBuffer = "";

                        continue;
                }


                if (
                        incoming == '\r'
                ) {

                        continue;
                }


                if (
                        serialBuffer.length()
                        < 32
                ) {

                        serialBuffer +=
                                incoming;
                }

                else {

                        // Drop malformed / excessively long input.
                        serialBuffer = "";
                }
        }
}


// ============================================================
// SETUP
// ============================================================

void setup() {

        Serial.begin(
                115200
        );


        Modulino.begin();


        if (
                !pixels.begin()
        ) {

                // If Pixels cannot be found, leave the program
                // alive so the serial interface still exists.
                // This makes wiring problems easier to diagnose.

                while (
                        true
                ) {

                        readSerialCommands();
                        delay(
                                10
                        );
                }
        }


        // Match the existing JARVIS behavior:
        // when the Nano starts, show IDLE orange.
        enterState(
                STATE_IDLE
        );
}


// ============================================================
// LOOP
// ============================================================

void loop() {

        // Always check serial first so any state can be
        // interrupted immediately by the next JARVIS command.
        readSerialCommands();


        // Then advance whichever non-blocking animation is active.
        updateAnimation();
}
