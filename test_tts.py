
import os
from pathlib import Path

from dotenv import load_dotenv
from gnani.tts import GnaniTTSClient, AudioConfig

# Load credentials from the project's .env file
load_dotenv()

api_key = os.getenv("GNANI_API_KEY_ID")

if not api_key:
    raise ValueError(
        "GNANI_API_KEY_ID is missing from your .env file"
    )

# Create the Gnani TTS client
client = GnaniTTSClient(api_key=api_key)

# Generate speech using Timbre
audio = client.synthesize(
    text="Hello! Welcome to Scam Gym. Let's learn to identify scam calls.",
    voice="Pranav",
    model="timbre-v2.5",
    language="en-IN",
    speed=1.0,
    audio_config=AudioConfig(
        container="wav",
        sample_rate=48000
    )
)

# Save the generated audio
output_path = Path("tts_test.wav")
output_path.write_bytes(audio)

print(f"TTS successful! Audio saved to: {output_path.resolve()}")
print(f"Audio size: {len(audio)} bytes")
