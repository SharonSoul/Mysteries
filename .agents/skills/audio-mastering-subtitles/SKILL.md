---
name: audio-mastering-subtitles
description: Master voiceovers, background music, atmospheric sound design, and generate synchronized subtitles (SRT/ASS) for YouTube documentary videos. Use when mixing audio tracks, ducking music under narration, normalizing to -14 LUFS, generating subtitles from timestamps, or styling captions for YouTube Shorts and long-form documentaries.
license: MIT
metadata: {"audio_standards": ["-14_LUFS", "-1dB_TP"], "subtitle_formats": ["SRT", "ASS", "VTT"]}
---

# Audio Mastering & Subtitle Synchronization

This skill governs the acoustic environment, sound design, and caption synchronization for **Mysteries & Unexplained History** documentaries.

## Sound Design Principles for Historical Mysteries

1. **Voice Primacy**: The narrator's voice must always remain intelligible, crisp, and prominent. Never let music overpower spoken historical detail.
2. **Atmospheric Bedding**: Use ambient soundscapes (distant wind, subtle water resonance, ancient low-frequency drones, reverberant strings) rather than repetitive pop or upbeat rhythms.
3. **Punctuation SFX**: Use tactile sound effects to underscore visual discoveries:
   - Ancient stone scraping when revealing tomb entrances.
   - Subdued metal clockwork ticking for mechanical anomalies.
   - Deep sub-bass drops for mind-bending revelations or unanswered questions.

## Audio Processing Pipeline

```
Raw ElevenLabs Narration (WAV)
       │
       ▼
1. High-Pass Filter (Cut below 80 Hz to eliminate sub-rumble)
       │
       ▼
2. Subtle Presence EQ (+2 dB at 3.5 kHz for vocal clarity)
       │
       ▼
3. Sidechain Compression Ducking with Ambient Music (-8 dB to -12 dB ducking)
       │
       ▼
4. EBU R128 Loudness Normalization (-14 LUFS, -1 dB True Peak)
```

### Complete Audio Mastering via FFmpeg

```bash
# 1. Clean and EQ Narration
ffmpeg -i narration_raw.wav -af "highpass=f=80,equalizer=f=3500:t=q:w=1.5:g=2.5" -c:a pcm_s16le narration_clean.wav

# 2. Mix Narration + Music with Dynamic Ducking
ffmpeg -i narration_clean.wav -i ambient_music.wav -filter_complex "[1:a]volume=0.30[music_bed];[music_bed][0:a]sidechaincompress=threshold=0.08:ratio=4:attack=50:release=350[ducked_music];[0:a][ducked_music]amix=inputs=2:duration=first:dropout_transition=2[mixed]" -map "[mixed]" -c:a pcm_s16le mixed_temp.wav

# 3. Master to YouTube EBU R128 (-14 LUFS)
ffmpeg -i mixed_temp.wav -af "loudnorm=I=-14:TP=-1.0:LRA=7" -c:a aac -b:a 192k final_mastered_audio.m4a
```

## Speech-to-Text and Subtitle Generation (Whisper Standard)

Local Whisper (specifically `faster-whisper` for fast CTranslate2 inference) is the permanent studio standard for generating subtitles:
- **Audio-First Transcription**: Always generate subtitles from the final approved narration audio file, NEVER directly from the original script text.
- **Word-Level Timing**: Extract word-level or segment timestamps from Whisper to construct precise SRT subtitles.
- **Human-in-the-Loop Review**: Check subtitle timing, punctuation, proper noun spellings (e.g. *Antikythera*, *Archimedes*, *Derek de Solla Price*), and formatting before final video burn or export.
- **No Paid External STT**: Never call ElevenLabs or other paid cloud APIs for speech-to-text or transcription when local Whisper is available.

```python
from pathlib import Path
from faster_whisper import WhisperModel

def transcribe_narration_to_srt(audio_path: Path, srt_output_path: Path, model_size: str = "base") -> list[dict]:
    """
    Transcribes approved narration audio using local faster-whisper and generates an SRT file.
    """
    # Use CPU with int8 or float32, or CUDA if available
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio_path), beam_size=5, word_timestamps=True)
    
    cues = []
    with open(srt_output_path, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(segments, start=1):
            cue = {
                "index": idx,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            cues.append(cue)
            
            start_str = format_timestamp(segment.start)
            end_str = format_timestamp(segment.end)
            f.write(f"{idx}\n{start_str} --> {end_str}\n{segment.text.strip()}\n\n")
            
    return cues
```

## Subtitle Guidelines & Readability Standards

### Sizing and Line Constraints
- **Max Characters per Line**: 32–36 characters (desktop / long-form), 24–28 characters (mobile / Shorts).
- **Max Lines**: 2 lines per display block (preferably 1 single line for Shorts).
- **Duration**: Minimum 1.2 seconds, maximum 3.5 seconds per cue.
- **Reading Speed**: Target 14–17 characters per second (CPS) for comfortable reading.

### Subtitle Generator (Converting Timestamp Dict to SRT)

```python
from datetime import timedelta
from pathlib import Path

def format_timestamp(seconds: float) -> str:
    """Formats float seconds into SRT timestamp HH:MM:SS,mmm"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def write_srt(cues: list[dict], output_path: Path):
    """
    cues format: [{'start': 0.0, 'end': 2.4, 'text': 'In the spring of 1900...'}, ...]
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, cue in enumerate(cues, start=1):
            start_str = format_timestamp(cue["start"])
            end_str = format_timestamp(cue["end"])
            f.write(f"{idx}\n{start_str} --> {end_str}\n{cue['text'].strip()}\n\n")
```

### Visual Subtitle Styling for Video Burn-In

When burning subtitles into the final MP4 using FFmpeg:

**Shorts Style (Dynamic, centered, high-impact):**
```text
subtitles=captions.srt:force_style='FontName=Arial Black,FontSize=22,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2.5,Shadow=1,Alignment=2,MarginV=140'
```
*(Yellow primary text with black outline, centered higher up to avoid YouTube Shorts UI overlay at the bottom).*

**Long-Form Documentary Style (Clean, cinematic):**
```text
subtitles=captions.srt:force_style='FontName=Montserrat,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=1.8,Shadow=0.5,Alignment=2,MarginV=40'
```
*(Crisp white text with subtle dark halo, bottom centered, broadcast documentary aesthetic).*
