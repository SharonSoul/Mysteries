"""Unit tests for subtitle synchronization and formatting."""

from pathlib import Path
from src.subtitles.generator import SubtitleGenerator, format_srt_time


def test_format_srt_time():
    assert format_srt_time(0.0) == "00:00:00,000"
    assert format_srt_time(65.5) == "00:01:05,500"
    assert format_srt_time(3661.123) == "01:01:01,123"


def test_write_srt_file(tmp_path: Path):
    cues = [
        {"start": 0.0, "end": 2.5, "text": "In the spring of 1900,"},
        {"start": 2.5, "end": 5.0, "text": "divers found something impossible."}
    ]
    srt_file = tmp_path / "test.srt"
    SubtitleGenerator.create_srt_from_cues(cues, srt_file)
    assert srt_file.exists()
    content = srt_file.read_text(encoding="utf-8")
    assert "00:00:00,000 --> 00:00:02,500" in content
    assert "In the spring of 1900," in content
    assert "00:00:02,500 --> 00:00:05,000" in content
