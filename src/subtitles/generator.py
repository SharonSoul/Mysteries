"""
Subtitle Synchronization & SRT/ASS Generator.
Transforms timestamps and text cues into synchronized subtitle streams.
"""

from datetime import timedelta
from pathlib import Path
from typing import Any, Optional


def format_srt_time(seconds: float) -> str:
    """Formats float seconds into standard SRT timecode HH:MM:SS,mmm"""
    total_millis = int(round(seconds * 1000))
    hours = total_millis // 3_600_000
    minutes = (total_millis % 3_600_000) // 60_000
    secs = (total_millis % 60_000) // 1000
    millis = total_millis % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class SubtitleGenerator:
    """Generates and validates synchronized subtitle files."""

    @classmethod
    def create_srt_from_cues(cls, cues: list[dict[str, Any]], output_file: Path) -> Path:
        """
        Takes cues: [{'start': 0.0, 'end': 2.5, 'text': '...'}]
        Writes a valid UTF-8 .srt file.
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        lines = []

        for idx, cue in enumerate(cues, start=1):
            start_str = format_srt_time(cue["start"])
            end_str = format_srt_time(cue["end"])
            text = cue["text"].strip()

            lines.append(f"{idx}")
            lines.append(f"{start_str} --> {end_str}")
            lines.append(text)
            lines.append("")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return output_file

    @classmethod
    def generate_cues_from_alignment(
        cls,
        text: str,
        alignment: Any,
        format_type: str = "longform"
    ) -> list[dict[str, Any]]:
        """
        Processes ElevenLabs character/word alignment into readable subtitle chunks.
        Clamps max characters per line according to video format (28 for shorts, 36 for longform).
        """
        max_chars = 28 if format_type == "shorts" else 36
        words = text.split()
        if not words:
            return []

        # If alignment details are present
        char_start_times = getattr(alignment, "character_start_times_seconds", [])
        char_end_times = getattr(alignment, "character_end_times_seconds", [])

        if not char_start_times or len(char_start_times) != len(text):
            # Fallback estimation based on average speaking duration
            total_duration = max(len(words) / 2.2, 3.0)
            chunk_duration = total_duration / len(words)
            cues = []
            curr_chunk = []
            chunk_start = 0.0

            for idx, word in enumerate(words):
                curr_chunk.append(word)
                chunk_text = " ".join(curr_chunk)
                if len(chunk_text) >= max_chars or idx == len(words) - 1:
                    chunk_end = (idx + 1) * chunk_duration
                    cues.append({
                        "start": round(chunk_start, 2),
                        "end": round(chunk_end, 2),
                        "text": chunk_text
                    })
                    curr_chunk = []
                    chunk_start = chunk_end
            return cues

        # Group words by character offsets
        cues = []
        curr_words = []
        chunk_start = 0.0
        char_idx = 0

        for word in words:
            # Find start index of word in text
            word_start_idx = text.find(word, char_idx)
            word_end_idx = word_start_idx + len(word) - 1
            char_idx = word_end_idx + 1

            if not curr_words:
                chunk_start = char_start_times[word_start_idx]

            curr_words.append(word)
            chunk_text = " ".join(curr_words)

            if len(chunk_text) >= max_chars or word == words[-1]:
                chunk_end = char_end_times[min(word_end_idx, len(char_end_times) - 1)]
                cues.append({
                    "start": round(chunk_start, 2),
                    "end": round(max(chunk_end, chunk_start + 1.0), 2),
                    "text": chunk_text
                })
                curr_words = []

        return cues

    @classmethod
    def transcribe_with_whisper(
        cls,
        audio_path: Path,
        output_srt: Optional[Path] = None,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        format_type: str = "shorts"
    ) -> tuple[list[dict[str, Any]], Path]:
        """
        Transcribes approved narration audio using local faster-whisper.
        Extracts word-level timestamps, formats them into optimal subtitle cues,
        and saves a standard SRT file.
        """
        try:
            from faster_whisper import WhisperModel
            import faster_whisper.audio as fwa
            import faster_whisper.transcribe as fwt
            import av
            import numpy as np

            # Compatibility patch for PyAV 14+ / 19+ (metadata_errors removed from av.open)
            if not getattr(fwa, "_patched_for_av_19", False):
                import io, gc

                def _safe_decode_audio(input_file, sampling_rate=16000, split_stereo=False):
                    resampler = av.audio.resampler.AudioResampler(
                        format="s16",
                        layout="mono" if not split_stereo else "stereo",
                        rate=sampling_rate,
                    )
                    raw_buffer = io.BytesIO()
                    dtype = None
                    with av.open(input_file, mode="r") as container:
                        frames = container.decode(audio=0)
                        frames = fwa._ignore_invalid_frames(frames)
                        frames = fwa._group_frames(frames, 500000)
                        frames = fwa._resample_frames(frames, resampler)
                        for frame in frames:
                            arr = frame.to_ndarray()
                            dtype = arr.dtype
                            raw_buffer.write(arr)
                    del resampler
                    gc.collect()
                    audio = np.frombuffer(raw_buffer.getbuffer(), dtype=dtype).astype(np.float32) / 32768.0
                    if split_stereo:
                        return audio[0::2], audio[1::2]
                    return audio

                fwa.decode_audio = _safe_decode_audio
                fwt.decode_audio = _safe_decode_audio
                fwa._patched_for_av_19 = True

        except ImportError:
            raise RuntimeError("faster-whisper is not installed. Please install faster-whisper>=1.0.0.")

        max_chars = 28 if format_type == "shorts" else 36
        
        # Pre-decode audio using safe decoder to avoid any external PyAV keyword mismatches
        audio_arr = fwa.decode_audio(str(audio_path))

        # Load model (base or tiny for fast CPU inference)
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        segments, info = model.transcribe(audio_arr, beam_size=5, word_timestamps=True)

        cues: list[dict[str, Any]] = []
        for segment in segments:
            if segment.words:
                curr_words = []
                chunk_start = None
                for w in segment.words:
                    word_clean = w.word.strip()
                    if not word_clean:
                        continue
                    if chunk_start is None:
                        chunk_start = w.start
                    curr_words.append(word_clean)
                    chunk_text = " ".join(curr_words)

                    if len(chunk_text) >= max_chars or w == segment.words[-1]:
                        chunk_end = max(w.end, chunk_start + 0.8)
                        cues.append({
                            "start": round(chunk_start, 2),
                            "end": round(chunk_end, 2),
                            "text": chunk_text
                        })
                        curr_words = []
                        chunk_start = None
            else:
                cues.append({
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip()
                })

        if not output_srt:
            output_srt = audio_path.with_suffix(".srt")

        cls.create_srt_from_cues(cues, output_srt)
        return cues, output_srt
