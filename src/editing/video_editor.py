"""
FFmpeg Video Editing & Rendering Engine.
Handles scene generation, motion effects (Ken Burns), vertical cropping,
audio ducking, loudness normalization, and subtitle burning.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

from config.settings import AUDIO_SPECS, VIDEO_SPECS

import os

logger = logging.getLogger(__name__)


def find_ffmpeg_binary(binary_name: str = "ffmpeg") -> str:
    """Auto-detects ffmpeg/ffprobe on PATH or WinGet package paths."""
    found = shutil.which(binary_name)
    if found:
        return found

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        candidates = list(Path(local_app_data).glob(f"Microsoft/WinGet/**/{binary_name}.exe"))
        if candidates:
            return str(candidates[0])

    return binary_name


class FFmpegVideoEditor:
    """Orchestrates local FFmpeg video and audio processing commands."""

    def __init__(self, ffmpeg_path: str = None, ffprobe_path: str = None):
        self.ffmpeg = ffmpeg_path or find_ffmpeg_binary("ffmpeg")
        self.ffprobe = ffprobe_path or find_ffmpeg_binary("ffprobe")

    def check_ffmpeg_available(self) -> dict[str, Any]:
        """Verifies presence of ffmpeg and ffprobe on system PATH or WinGet."""
        ffmpeg_found = Path(self.ffmpeg).exists() or bool(shutil.which(self.ffmpeg))
        ffprobe_found = Path(self.ffprobe).exists() or bool(shutil.which(self.ffprobe))

        version_str = ""
        if ffmpeg_found:
            try:
                res = subprocess.run([self.ffmpeg, "-version"], capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    version_str = res.stdout.splitlines()[0]
            except Exception:
                ffmpeg_found = False

        return {
            "ffmpeg": ffmpeg_found,
            "ffprobe": ffprobe_found,
            "version": version_str,
            "path": self.ffmpeg
        }

    def render_image_motion_clip(
        self,
        image_path: Path,
        output_clip_path: Path,
        duration: float = 5.0,
        format_type: str = "longform",
        motion_type: str = "zoom_in",
        fps: int = 30
    ) -> Path:
        """
        Creates an animated video clip from a still image using Ken Burns pan/zoom.
        Supports both 16:9 long-form and 9:16 vertical shorts.
        """
        specs = VIDEO_SPECS.get(format_type, VIDEO_SPECS["longform"])
        width, height = specs["width"], specs["height"]
        frames = int(duration * fps)

        output_clip_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type == "shorts":
            # Blurred background + foreground scaled fit
            filter_str = (
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},boxblur=20:5[bg];"
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
            )
        else:
            # 16:9 Ken Burns motion
            if motion_type == "zoom_in":
                filter_str = f"scale=8000:-1,zoompan=z='min(zoom+0.0015,1.20)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={width}x{height}:fps={fps}"
            elif motion_type == "zoom_out":
                filter_str = f"scale=8000:-1,zoompan=z='max(1.20-0.0015*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={width}x{height}:fps={fps}"
            elif motion_type == "pan_left":
                filter_str = f"scale=-1:1440,zoompan=z=1.15:x='(iw-iw/zoom)*(1-on/({frames}-1))':y='ih/2-(ih/zoom/2)':d={frames}:s={width}x{height}:fps={fps}"
            elif motion_type == "pan_right":
                filter_str = f"scale=-1:1440,zoompan=z=1.15:x='(iw-iw/zoom)*(on/({frames}-1))':y='ih/2-(ih/zoom/2)':d={frames}:s={width}x{height}:fps={fps}"
            else:  # static
                filter_str = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"

        cmd = [
            self.ffmpeg, "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-filter_complex" if format_type == "shorts" else "-vf", filter_str,
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            str(output_clip_path)
        ]

        logger.info("Rendering scene motion clip: %s", output_clip_path)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output_clip_path

    def mix_and_duck_audio(
        self,
        narration_path: Path,
        music_path: Path,
        output_audio_path: Path,
        music_bed_volume: float = 0.25,
        ducking_ratio: float = 4.0
    ) -> Path:
        """
        Mixes speech narration with background music, lowering music
        volume automatically during speech (sidechain compression).
        """
        output_audio_path.parent.mkdir(parents=True, exist_ok=True)

        filter_complex = (
            f"[1:a]volume={music_bed_volume}[music_bed];"
            f"[music_bed][0:a]sidechaincompress=threshold=0.08:ratio={ducking_ratio}:attack=50:release=350[ducked_music];"
            f"[0:a][ducked_music]amix=inputs=2:duration=first:dropout_transition=2[mixed]"
        )

        cmd = [
            self.ffmpeg, "-y",
            "-i", str(narration_path),
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[mixed]",
            "-c:a", "pcm_s16le",
            str(output_audio_path)
        ]

        logger.info("Ducking and mixing audio into %s", output_audio_path)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output_audio_path

    def normalize_loudness(self, input_audio: Path, output_audio: Path) -> Path:
        """
        Applies EBU R128 loudness normalization to -14 LUFS for YouTube.
        """
        output_audio.parent.mkdir(parents=True, exist_ok=True)
        lufs = AUDIO_SPECS["target_lufs"]
        tp = AUDIO_SPECS["true_peak_db"]
        lra = AUDIO_SPECS["loudness_range"]

        cmd = [
            self.ffmpeg, "-y",
            "-i", str(input_audio),
            "-af", f"loudnorm=I={lufs}:TP={tp}:LRA={lra}",
            "-c:a", AUDIO_SPECS["codec"],
            "-b:a", AUDIO_SPECS["bitrate"],
            str(output_audio)
        ]

        logger.info("Normalizing audio loudness to %s LUFS", lufs)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output_audio

    def burn_subtitles(
        self,
        video_input: Path,
        subtitles_srt: Path,
        video_output: Path,
        format_type: str = "longform"
    ) -> Path:
        """
        Burns subtitles directly into video with clean outline typography.
        """
        video_output.parent.mkdir(parents=True, exist_ok=True)
        # Windows path escaping for subtitles filter
        escaped_srt = str(subtitles_srt).replace("\\", "/").replace(":", "\\:")

        if format_type == "shorts":
            # Centered higher up to avoid YouTube Shorts UI overlay
            style = "FontName=Arial Black,FontSize=20,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2.5,Shadow=1,Alignment=2,MarginV=140"
        else:
            # Broadcast documentary style
            style = "FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=1.8,Shadow=0.5,Alignment=2,MarginV=45"

        cmd = [
            self.ffmpeg, "-y",
            "-i", str(video_input),
            "-vf", f"subtitles={escaped_srt}:force_style='{style}'",
            "-c:v", "libx264",
            "-c:a", "copy",
            str(video_output)
        ]

        logger.info("Burning subtitles into final export %s", video_output)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return video_output
