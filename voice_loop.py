import os
from pathlib import Path

import sounddevice as sd
from dotenv import load_dotenv
from scipy.io.wavfile import write
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient, AudioConfig

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


def choose_reply(transcript: str) -> str:
    """Pick the simulated scammer's next line from what the player said."""
    text = transcript.lower().strip()

    if not text:
        return "Hello? Are you still there?"

    if any(w in text for w in ("who are you", "proof", "call back", "1930", "hang up")):
        return "Why so many questions? This is urgent. Answer me now."

    if "otp" in text:
        return "Good. Read the code to me right now."

    return "Please listen carefully. This is an important call."


MAX_TURNS = 3


def run_call():
    print("SIMULATION: this is a fake scam call for practice. All data is fake.")
    print("Say 'hang up' to end the call.\n")

    for turn in range(1, MAX_TURNS + 1):
        print(f"--- Turn {turn} of {MAX_TURNS} ---")
        input("Press Enter, then speak for 5 seconds...")
        transcript = listen()
        print("You said:", repr(transcript))

        if "hang up" in transcript.lower():
            print("You hung up. Call ended.")
            return

        reply = choose_reply(transcript)
        print("Scammer:", reply)

        if speak(reply):
            os.startfile("reply.wav")
            input("Press Enter after the reply finishes playing...")

    print("Call ended: you survived all turns.")


if __name__ == "__main__":
    run_call()