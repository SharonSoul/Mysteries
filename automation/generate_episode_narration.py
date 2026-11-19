import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from src.narration.generator import ElevenLabsNarrationEngine
from src.subtitles.generator import SubtitleGenerator

AUDIO_DIR = Path("projects/antikythera-mechanism-short/audio")
SUBTITLES_DIR = Path("projects/antikythera-mechanism-short/subtitles")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)

with open("projects/antikythera-mechanism-short/script.json", "r", encoding="utf-8") as f:
    script_data = json.load(f)

scenes = script_data["scenes"]
engine = ElevenLabsNarrationEngine()

print("=== 1. GENERATING ELEVENLABS NARRATION SCENE-BY-SCENE ===")
total_chars = 0
scene_audio_files = []
credit_records = []

for s in scenes:
    scene_id = s["scene_id"]
    text = s["narration_text"]
    char_count = len(text)
    total_chars += char_count
    
    out_file = AUDIO_DIR / f"{scene_id.lower()}.mp3"
    if not out_file.exists() or out_file.stat().st_size == 0:
        print(f"Generating audio for {scene_id} ({char_count} chars)...")
        engine.generate_narration(text, out_file)
        print(f"  -> Saved {out_file.name} ({out_file.stat().st_size} bytes)")
    else:
        print(f"Audio already generated for {scene_id} ({out_file.stat().st_size} bytes)")
    
    scene_audio_files.append(out_file)
    credit_records.append({
        "scene_id": scene_id,
        "text": text,
        "character_count": char_count,
        "credits_consumed": char_count,
        "audio_file": str(out_file)
    })

# Save credit consumption record
credit_summary = {
    "project_id": "antikythera-mechanism-short",
    "timestamp": datetime.now().isoformat(),
    "voice_id": engine.voice_id,
    "model_id": "eleven_multilingual_v2",
    "total_scenes": len(scenes),
    "total_characters": total_chars,
    "total_estimated_credits": total_chars,
    "scene_breakdown": credit_records
}

with open("projects/antikythera-mechanism-short/elevenlabs_credits.json", "w", encoding="utf-8") as f:
    json.dump(credit_summary, f, indent=2)

print(f"\n[CREDITS LOGGED] Total characters: {total_chars}. Logged to elevenlabs_credits.json.")

# 2. Concatenate into full continuous audio using FFmpeg concat
final_audio_path = AUDIO_DIR / "final_narration.mp3"
concat_list_file = AUDIO_DIR / "concat_list.txt"

with open(concat_list_file, "w", encoding="utf-8") as f:
    for audio_file in scene_audio_files:
        clean_path = str(audio_file.resolve()).replace("\\", "/")
        f.write(f"file '{clean_path}'\n")

print(f"\n=== 2. CONCATENATING AUDIO TO {final_audio_path.name} ===")
from src.editing.video_editor import FFmpegVideoEditor
editor = FFmpegVideoEditor()

concat_cmd = [
    editor.ffmpeg,
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_list_file),
    "-c", "copy",
    str(final_audio_path)
]
subprocess.run(concat_cmd, check=True)
print(f"Concatenated full audio: {final_audio_path} ({final_audio_path.stat().st_size} bytes)")

# 3. Transcribe with local faster-whisper
print("\n=== 3. TRANSCRIBING FINAL NARRATION WITH LOCAL WHISPER ===")
srt_output = SUBTITLES_DIR / "subtitles.srt"
cues, srt_path = SubtitleGenerator.transcribe_with_whisper(
    audio_path=final_audio_path,
    output_srt=srt_output,
    model_size="base",
    format_type="shorts"
)

# Also save transcription JSON
transcription_json = SUBTITLES_DIR / "whisper_transcription.json"
with open(transcription_json, "w", encoding="utf-8") as f:
    json.dump(cues, f, indent=2)

print(f"Whisper transcription generated {len(cues)} subtitle cues:")
for c in cues[:5]:
    print(f"  [{c['start']}s -> {c['end']}s]: {c['text']}")

print("\nNarration and subtitle generation successfully complete!")
