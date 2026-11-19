import subprocess
from pathlib import Path
from src.editing.video_editor import FFmpegVideoEditor

editor = FFmpegVideoEditor()
AUDIO_DIR = Path("projects/antikythera-mechanism-short/audio")

narration_wav = AUDIO_DIR / "final_narration.wav"
ambient_bed_wav = AUDIO_DIR / "ambient_bed.wav"
mastered_audio_wav = AUDIO_DIR / "mastered_audio.wav"
mastered_audio_m4a = AUDIO_DIR / "mastered_audio.m4a"

# 1. Synthesize a 95-second cinematic subsea atmospheric drone
# Low brownian rumble (subsea hydrophone feel) + gentle 65Hz / 130Hz mystery drone + reverb
print("Synthesizing atmospheric soundscape bed...")
bed_filter = (
    "anoisesrc=d=95:c=brown:r=44100:a=0.04[noise];"
    "sine=f=65:d=95[sub];"
    "sine=f=130:d=95[mid];"
    "[noise]lowpass=f=220,volume=0.4[ocean];"
    "[sub]volume=0.15[sub_bed];"
    "[mid]volume=0.08[mid_bed];"
    "[ocean][sub_bed][mid_bed]amix=inputs=3:dropout_transition=2,"
    "aecho=0.8:0.7:120:0.4,volume=0.35[bed]"
)

subprocess.run([
    editor.ffmpeg, "-y",
    "-filter_complex", bed_filter,
    "-map", "[bed]",
    "-c:a", "pcm_s16le",
    str(ambient_bed_wav)
], check=True, capture_output=True)
print(f"Generated atmospheric bed: {ambient_bed_wav.name} ({ambient_bed_wav.stat().st_size} bytes)")

# 2. Sidechain ducking: Duck ambient bed by -12 dB whenever narration is speaking
print("Mixing narration with dynamic sidechain ducking...")
mix_filter = (
    "[1:a]volume=0.25[music_bed];"
    "[music_bed][0:a]sidechaincompress=threshold=0.06:ratio=4:attack=50:release=350[ducked_music];"
    "[0:a][ducked_music]amix=inputs=2:duration=first:dropout_transition=2[mixed]"
)

temp_mixed = AUDIO_DIR / "temp_mixed.wav"
subprocess.run([
    editor.ffmpeg, "-y",
    "-i", str(narration_wav),
    "-i", str(ambient_bed_wav),
    "-filter_complex", mix_filter,
    "-map", "[mixed]",
    "-c:a", "pcm_s16le",
    str(temp_mixed)
], check=True, capture_output=True)

# 3. Master to YouTube EBU R128 (-14 LUFS, -1.0 dB True Peak)
print("Normalizing to YouTube standard -14 LUFS EBU R128...")
subprocess.run([
    editor.ffmpeg, "-y",
    "-i", str(temp_mixed),
    "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
    "-c:a", "pcm_s16le",
    str(mastered_audio_wav)
], check=True, capture_output=True)

# Also create high-quality AAC/M4A
subprocess.run([
    editor.ffmpeg, "-y",
    "-i", str(mastered_audio_wav),
    "-c:a", "aac",
    "-b:a", "192k",
    str(mastered_audio_m4a)
], check=True, capture_output=True)

print(f"Mastered audio produced: {mastered_audio_m4a.name} ({mastered_audio_m4a.stat().st_size} bytes)")

# Verify integrated loudness with ebur128
probe_cmd = [
    editor.ffmpeg,
    "-i", str(mastered_audio_m4a),
    "-af", "ebur128=framelog=verbose",
    "-f", "null",
    "-"
]
res = subprocess.run(probe_cmd, capture_output=True, text=True)
for line in res.stderr.splitlines():
    if "I:" in line or "Threshold:" in line or "LRA:" in line or "Peak:" in line:
        print(f"  [LOUDNORM AUDIT] {line.strip()}")
