---
name: ffmpeg-video-editor
description: Automate local video editing, image motion (Ken Burns effect), scene assembly, audio ducking, subtitle burning, and YouTube export formatting using local FFmpeg. Use whenever processing, cutting, concatenating video clips, creating motion from archival photos, mastering audio to -14 LUFS, or exporting MP4 videos for YouTube Shorts (9:16) or Long-form documentaries (16:9).
license: MIT
metadata: {"requires": {"tools": ["ffmpeg", "ffprobe"]}, "dependencies": ["ffmpeg>=6.1"]}
---

# FFmpeg Documentary Video Editor

This skill provides verified, production-ready FFmpeg command pipelines specifically designed for producing historical mystery documentaries and YouTube Shorts on Windows using local hardware acceleration.

## Hardware Acceleration (NVIDIA Quadro T2000)

When encoding H.264 video on the local NVIDIA Quadro GPU, use `h264_nvenc` with high-quality presets. If NVENC is unavailable, fallback gracefully to `libx264`.

```bash
# NVENC GPU encoding flag:
-c:v h264_nvenc -preset p5 -tune hq -b:v 8M -maxrate 12M -bufsize 16M

# CPU fallback:
-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p
```

## Essential Documentary Video Recipes

### 1. Ken Burns Effect (Slow Motion on Archival Photos)
Archival photos and historical maps must come alive with subtle, cinematic motion:

**Slow Zoom-In (5 seconds, 1080p 16:9):**
```bash
ffmpeg -loop 1 -i photo.jpg -vf "scale=8000:-1,zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30" -t 5 -c:v libx264 -pix_fmt yuv420p scene_zoomin.mp4
```

**Pan Left-to-Right Across Historical Map:**
```bash
ffmpeg -loop 1 -i map.jpg -vf "scale=-1:1440,zoompan=z=1.15:x='(iw-iw/zoom)*(on/(150-1))':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30" -t 5 -c:v libx264 -pix_fmt yuv420p scene_pan.mp4
```

### 2. YouTube Shorts Vertical Format (9:16 - 1080x1920)
For YouTube Shorts (40–90s), format content vertically:
- Center-crop high-resolution footage or fit with blurred background:

**Blurred Background Fit (Archival photo inside 9:16 vertical frame):**
```bash
ffmpeg -loop 1 -i archival_photo.jpg -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -t 5 -c:v libx264 -pix_fmt yuv420p short_scene.mp4
```

### 3. Scene Assembly & Cross-Dissolve Transitions
To smoothly concatenate scenes with a 0.5-second crossfade:
```bash
ffmpeg -i scene1.mp4 -i scene2.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=4.5[v];[0:a][1:a]acrossfade=d=0.5[a]" -map "[v]" -map "[a]" -c:v libx264 -c:a aac combined.mp4
```

### 4. Audio Mixing & Sidechain Ducking
Lower background music automatically whenever the ElevenLabs narrator speaks:
```bash
ffmpeg -i narration.wav -i background_music.wav -filter_complex "[1:a]volume=0.35[bg];[bg][0:a]sidechaincompress=threshold=0.08:ratio=4:attack=50:release=400[ducked_bg];[0:a][ducked_bg]amix=inputs=2:duration=first:dropout_transition=2[aout]" -map "[aout]" -c:a aac -b:a 192k mixed_audio.m4a
```

### 5. YouTube Loudness Normalization (-14 LUFS)
YouTube standardizes playback at `-14 LUFS` and `-1 dB True Peak`:
```bash
ffmpeg -i mixed_audio.m4a -af "loudnorm=I=-14:TP=-1.0:LRA=7" -c:a aac -b:a 192k mastered_audio.m4a
```

### 6. Burning Subtitles (.srt / .ass)
Burn synchronized subtitles with clean, high-contrast typography (e.g., Arial, Roboto, Montserrat with outline and subtle drop shadow):
```bash
ffmpeg -i final_video_no_subs.mp4 -vf "subtitles=captions.srt:force_style='FontName=Montserrat,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=1,MarginV=45'" -c:v libx264 -c:a copy final_video_with_subs.mp4
```

## Quality Checklist Before Final Export

1. **Resolution & Aspect Ratio**: 1920x1080 (16:9) for Long-form; 1080x1920 (9:16) for Shorts.
2. **Framerate**: Standardize all scenes to 30 fps (or 24 fps cinematic) before stitching to prevent desync.
3. **Pixel Format**: Always `-pix_fmt yuv420p` for maximum player and YouTube compatibility.
4. **Audio Sync**: Verify audio and video stream durations match exactly to prevent freeze frames or truncated narration.
5. **Color Standards**: Standard sRGB/Rec.709 color matrix; avoid unintended gamma shifts.
