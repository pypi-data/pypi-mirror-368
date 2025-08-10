
# KittenTTS Example

This project demonstrates how to use the **KittenTTS** text-to-speech model to convert text into a `.wav` audio file.

## Features
- Convert any given text into natural-sounding speech.
- Choose a specific voice for the generated audio.
- Control the playback speed.

## Requirements
Install the required Python packages:
```bash
apt install espeak
pip install KittenTTS
```

## Usage

Below is a minimal working example:

```python
import soundfile as sf
from kittentts import KittenTTS  
# Initialize the model
model = KittenTTS()

# Generate speech
audio_data = model.generate(
    text="hi who are you",
    voice="expr-voice-2-m",
    speed=1.0
)

# Save output as a WAV file
sf.write("test.wav", audio_data, 24000)
```

## Parameters

* **text** *(str)*: The text you want to convert to speech.
* **voice** *(str)*: The voice preset to use (e.g., `"expr-voice-2-m"`).
* **speed** *(float)*: Playback speed multiplier (1.0 = normal speed).

## Reference
https://github.com/KittenML/KittenTTS

## Implementation with GUI
https://huggingface.co/spaces/shethjenil/KittenTTS