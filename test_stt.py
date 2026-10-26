
import os
from pathlib import Path

from dotenv import load_dotenv
from gnani.stt import GnaniSTTClient

# Load API credentials from .env
load_dotenv()

api_key = os.getenv("GNANI_API_KEY_ID")

if not api_key:
    raise ValueError(
        "GNANI_API_KEY_ID is missing from your .env file"
    )

# Check that the TTS audio exists
audio_path = Path("tts_test.wav")

if not audio_path.exists():
    raise FileNotFoundError(
        "tts_test.wav not found. Run test_tts.py first."
    )

# Create the STT client
client = GnaniSTTClient(api_key=api_key)

# Transcribe the generated audio
result = client.transcribe(
    audio=audio_path,
    language_code="en-IN",
    format="verbatim"
)

print("\n--- Scam Gym: Prisma STT Result ---")
print(result)

