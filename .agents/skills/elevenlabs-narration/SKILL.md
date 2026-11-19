---
name: elevenlabs-narration
description: Generate professional documentary narration, voiceovers, and speech audio using ElevenLabs API and Python SDK. Use when creating voiceovers for documentary scripts, generating narration for YouTube Shorts or long-form videos, tuning voice settings (stability, similarity boost, style exaggeration), or extracting word-level timestamps for subtitle synchronization.
license: MIT
metadata: {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "dependencies": ["elevenlabs>=1.0.0"]}
---

# ElevenLabs Documentary Narration

This skill guides the generation of cinematic, authoritative voiceovers for historical and mystery documentaries using the ElevenLabs Python SDK.

## Core Principles for Documentary Narration

- **Dedicated TTS Provider**: ElevenLabs is the studio's designated text-to-speech provider for cinematic voice narration. Do not switch narration providers without user approval.
- **Tone & Persona**: Historical mystery documentaries require a grounded, thoughtful, intriguing, and calm delivery. Avoid overly energetic "commercial" hype or robotic monotone.
- **Voice Selection**: Choose deep, narrative voices with rich timbre and clear diction (e.g., George, Adam, Marcus, Callum, or Charlotte).
- **Audio Quality**: Export audio in uncompressed WAV or high-bitrate MP3 (192kbps+) into `media-library/audio/` or the episode project folder.
- **Modularity**: Generate narration scene-by-scene or chapter-by-chapter rather than one massive audio block. This allows re-recording single lines without re-generating the entire documentary.
- **Credit & Consumption Tracking**: Always record and log actual character count and ElevenLabs credit consumption for every generation run.
- **Transcription Handoff**: Do NOT use ElevenLabs speech-to-text or transcription APIs for routine subtitle generation. Hand off the final approved narration audio directly to local Whisper (`faster-whisper`) for subtitle generation.

## Recommended Voice Settings

| Parameter | Recommended Value | Purpose |
|---|---|---|
| `model_id` | `eleven_multilingual_v2` or `eleven_v4` | Highest quality nuance, natural breathing, and pronunciation |
| `stability` | `0.45` – `0.55` | Balances consistent tone with emotional gravity; lower values add intrigue, higher values are steady |
| `similarity_boost` | `0.75` – `0.85` | Ensures voice fidelity and clarity across historical terms and names |
| `style` | `0.10` – `0.20` | Subtle stylistic emphasis without over-dramatization |
| `use_speaker_boost` | `True` | Enhances vocal presence against background music |

## Python Implementation

```python
import os
from pathlib import Path
from elevenlabs.client import ElevenLabs

def generate_scene_narration(
    text: str,
    output_path: Path,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb",  # Default: George
    model_id: str = "eleven_multilingual_v2"
) -> Path:
    """Generates narration for a single script scene and saves to disk."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable is not set.")
    
    client = ElevenLabs(api_key=api_key)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    audio_stream = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        voice_settings={
            "stability": 0.50,
            "similarity_boost": 0.80,
            "style": 0.15,
            "use_speaker_boost": True
        }
    )
    
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
            
    return output_path
```

## Word-Level Timestamps for Subtitles

To generate perfectly synchronized captions, request timestamped output:

```python
def generate_narration_with_timestamps(
    text: str,
    output_audio_path: Path,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
) -> dict:
    """Generates audio and word-level timing data for subtitle alignment."""
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    
    response = client.text_to_speech.convert_with_timestamps(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2"
    )
    
    # Save audio stream
    with open(output_audio_path, "wb") as f:
        f.write(response.audio_base64_decoded)
        
    # alignment dict contains characters/words and their start/end timestamps
    return response.alignment
```

## Production Workflow Checklist

1. **Pronunciation Guide**: For ancient languages, archaeological sites, or non-English proper nouns (e.g., Göbekli Tepe, Tiwanaku, Linear B, Tutankhamun), write phonetic aids in the script text if necessary (e.g., "guh-BEK-lee TEH-peh").
2. **Pacing & Pauses**: Use punctuation (`...`, `—`, commas, full stops) to introduce natural dramatic pauses.
3. **Audio File Organization**: Save all outputs into `media-library/audio/scenes/` using structured naming: `<project-name>_ch01_scene02_narration.mp3`.
4. **Credit Conservation**: Never generate full audio on unapproved or draft scripts. Only call ElevenLabs once the script has been fact-checked and approved by the user.
