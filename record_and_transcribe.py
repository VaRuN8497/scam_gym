
import os
from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write
from dotenv import load_dotenv
from gnani.stt import GnaniSTTClient

load_dotenv()

api_key = os.getenv("GNANI_API_KEY_ID")
if not api_key:
    raise ValueError("GNANI_API_KEY_ID is missing from .env")

# Microphone device 3 from your device list
MICROPHONE_ID = 3
SAMPLE_RATE = 16000
DURATION = 5

output_path = Path("my_voice.wav")

client = GnaniSTTClient(api_key=api_key)

print("Get ready! Speak clearly after recording starts.")
input("Press Enter to start recording...")

print("Recording for 5 seconds. Speak now!")

recording = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=MICROPHONE_ID
)
sd.wait()

write(str(output_path), SAMPLE_RATE, recording)
print(f"Audio saved to {output_path.resolve()}")

print("Sending your recording to Prisma STT...")
result = client.transcribe(
    audio=output_path,
    language_code="en-IN",
    format="verbatim"
)

print("\n--- What Scam Gym heard ---")
print(result.get("transcript", result))
