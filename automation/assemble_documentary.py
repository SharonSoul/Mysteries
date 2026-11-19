import json
import os
import shutil
import subprocess
from pathlib import Path
from src.editing.video_editor import FFmpegVideoEditor

editor = FFmpegVideoEditor()

PROJECT_DIR = Path("projects/antikythera-mechanism-short")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_DIR = PROJECT_DIR / "audio"
VIDEO_DIR = PROJECT_DIR / "video"
SUBTITLES_DIR = PROJECT_DIR / "subtitles"
EXPORTS_DIR = Path("exports")

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Scene configurations
SCENES = [
    {
        "id": "scene_01",
        "image": ASSETS_DIR / "scene_01_antikythera_fragment_a.jpg",
        "audio": AUDIO_DIR / "scene_01.mp3",
        "motion": "zoom_in"
    },
    {
        "id": "scene_02",
        "image": ASSETS_DIR / "scene_02_antikythera_teeth.jpg",
        "audio": AUDIO_DIR / "scene_02.mp3",
        "motion": "zoom_in"
    },
    {
        "id": "scene_03",
        "image": ASSETS_DIR / "scene_03_antikythera_dials_replica.jpg",
        "audio": AUDIO_DIR / "scene_03.mp3",
        "motion": "zoom_out"
    },
    {
        "id": "scene_04",
        "image": ASSETS_DIR / "scene_04_antikythera_inscriptions.jpg",
        "audio": AUDIO_DIR / "scene_04.mp3",
        "motion": "zoom_in"
    },
    {
        "id": "scene_05",
        "image": ASSETS_DIR / "scene_05_antikythera_model.jpg",
        "audio": AUDIO_DIR / "scene_05.mp3",
        "motion": "zoom_in"
    }
]

print("=== 1. PROBING SCENE DURATIONS AND RENDERING VERTICAL CLIPS ===")
rendered_scene_clips = []

for sc in SCENES:
    sc_id = sc["id"]
    img_path = sc["image"]
    aud_path = sc["audio"]
    out_clip = VIDEO_DIR / f"{sc_id}_clip.mp4"
    
    # Get exact duration from audio
    res = subprocess.run([
        editor.ffprobe, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(aud_path)
    ], capture_output=True, text=True, check=True)
    duration = float(res.stdout.strip())
    total_frames = int(round(duration * 30))
    print(f"\nProcessing {sc_id}: {duration:.2f}s ({total_frames} frames)...")
    
    # Construct vertical Ken Burns filter:
    # Blurred background canvas (1080x1920) + animated foreground image
    # For zoom_in: zoom from 1.0 to 1.10
    # For zoom_out: zoom from 1.10 to 1.0
    if sc["motion"] == "zoom_in":
        zoom_expr = f"min(1.0+({0.10}*on/{total_frames}),1.10)"
    else:
        zoom_expr = f"max(1.10-({0.10}*on/{total_frames}),1.0)"

    clean_img_path = str(img_path.resolve()).replace("\\", "/")

    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]scale=1000:1500:force_original_aspect_ratio=decrease,"
        f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1000x1500:fps=30[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
    )

    cmd = [
        editor.ffmpeg, "-y",
        "-loop", "1",
        "-i", str(img_path),
        "-t", str(duration),
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-r", "30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "faster",
        "-crf", "20",
        str(out_clip)
    ]

    subprocess.run(cmd, check=True)
    print(f"  -> Rendered clip: {out_clip.name} ({out_clip.stat().st_size} bytes)")
    rendered_scene_clips.append(out_clip)

# 2. Concatenate scene clips
print("\n=== 2. CONCATENATING SCENE CLIPS ===")
concat_list = VIDEO_DIR / "scenes_concat_list.txt"
with open(concat_list, "w", encoding="utf-8") as f:
    for clip in rendered_scene_clips:
        clean = str(clip.resolve()).replace("\\", "/")
        f.write(f"file '{clean}'\n")

raw_concat_video = VIDEO_DIR / "video_assembled_raw.mp4"
subprocess.run([
    editor.ffmpeg, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_list),
    "-c", "copy",
    str(raw_concat_video)
], check=True)
print(f"Assembled video without audio: {raw_concat_video.name}")

# 3. Multiplex mastered audio and burn Whisper subtitles
print("\n=== 3. MULTIPLEXING MASTERED AUDIO AND BURNING WHISPER SUBTITLES ===")
mastered_audio = AUDIO_DIR / "mastered_audio.m4a"
subtitles_srt = SUBTITLES_DIR / "subtitles.srt"
final_output = VIDEO_DIR / "antikythera_mechanism_short.mp4"

# Subtitle filter path escaping for FFmpeg Windows
# For libass/subtitles on Windows, colons in drive letters need escaping (e.g. C\\:/path) or forward slashes
clean_srt = str(subtitles_srt.resolve()).replace("\\", "/").replace(":", "\\:")

# High-impact YouTube Shorts subtitle styling:
# Arial Black, FontSize=22, PrimaryColour=&H0000FFFF (Yellow), OutlineColour=&H00000000 (Black),
# BorderStyle=3 (Opaque box) or 1 with strong outline, Alignment=2 (Bottom Center), MarginV=140
sub_filter = (
    f"subtitles='{clean_srt}':force_style="
    f"'FontName=Arial Black,FontSize=22,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"
    f"BorderStyle=1,Outline=3.0,Shadow=1.5,Alignment=2,MarginV=140'"
)

cmd_final = [
    editor.ffmpeg, "-y",
    "-i", str(raw_concat_video),
    "-i", str(mastered_audio),
    "-vf", sub_filter,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "medium",
    "-crf", "19",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    str(final_output)
]

print("Rendering final MP4 release with burned subtitles and mastered audio...")
subprocess.run(cmd_final, check=True)
print(f"Final short rendered: {final_output} ({final_output.stat().st_size} bytes)")

# Copy to exports/
export_file = EXPORTS_DIR / "antikythera_mechanism_short.mp4"
shutil.copy2(final_output, export_file)
print(f"Exported copy created: {export_file} ({export_file.stat().st_size} bytes)")
