import os
from pathlib import Path

import sounddevice as sd
from dotenv import load_dotenv
from scipy.io.wavfile import write
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient, AudioConfig

from scenario1 import detect_move, new_call, step

load_dotenv()

MICROPHONE_ID = 3  # Headset (realme Buds Wireless 3) in the sounddevice list
SAMPLE_RATE = 16000
DURATION = 5


def listen(out_path: str = "my_turn.wav") -> str:
    """Record from the mic, transcribe with Prisma. Returns '' on any problem."""
    api_key = os.getenv("GNANI_API_KEY_ID")
    if not api_key:
        print("GNANI_API_KEY_ID is missing from .env")
        return ""

    try:
        print(f"Recording {DURATION}s. Speak now!")
        recording = sd.rec(
            int(DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            device=MICROPHONE_ID,
        )
        sd.wait()
        write(out_path, SAMPLE_RATE, recording)

        client = GnaniSTTClient(api_key=api_key)
        result = client.transcribe(
            audio=Path(out_path),
            language_code="en-IN",
            format="verbatim",
        )
        return (result.get("transcript") or "").strip()
    except Exception as e:
        print(f"Listen failed: {type(e).__name__}: {e}")
        return ""


def speak(text: str, out_path: str = "reply.wav") -> bool:
    """Turn text into a WAV file with Timbre. Returns True on success."""
    if not text.strip():
        print("Nothing to say.")
        return False

    api_key = os.getenv("GNANI_API_KEY_ID")
    if not api_key:
        print("GNANI_API_KEY_ID is missing from .env")
        return False

    try:
        client = GnaniTTSClient(api_key=api_key)
        audio = client.synthesize(
            text=text,
            voice="Pranav",
            model="timbre-v2.5",
            language="en-IN",
            speed=1.0,
            audio_config=AudioConfig(container="wav", sample_rate=48000),
        )
        Path(out_path).write_bytes(audio)
        return True
    except Exception as e:
        print(f"TTS failed: {type(e).__name__}: {e}")
        return False


def say(line: str):
    """Speak one scammer line and wait until the player has heard it."""
    print("Scammer:", line)
    if speak(line):
        os.startfile("reply.wav")
        input("Press Enter after the reply finishes playing...")


def run_call():
    print("SIMULATION: this is a fake scam call for practice. All data is fake.")
    print("Say 'hang up' to end the call.\n")

    state = new_call()
    say(state["line"])

    while state["outcome"] is None:
        input("Press Enter, then speak for 5 seconds...")
        transcript = listen()
        print("You said:", repr(transcript))

        move = detect_move(transcript)
        state = step(state, move)
        print(f"  [move={move}, score={state['score']}]")

        if state["outcome"] is None:
            say(state["line"])

    print(f"\nOutcome: {state['outcome']} | Score: {state['score']}")


if __name__ == "__main__":
    run_call()