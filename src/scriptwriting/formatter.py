"""
Scriptwriting & AV Script Formatting Module.
Generates two-column Audio/Visual scripts and validates timing constraints.
"""

from pathlib import Path
from typing import Optional
from src.models import ScriptScene


class ScriptFormatter:
    """Formats and validates documentary scripts."""

    WORDS_PER_MINUTE = 135

    @classmethod
    def estimate_duration_seconds(cls, text: str) -> float:
        words = len(text.split())
        return round((words / cls.WORDS_PER_MINUTE) * 60, 2)

    @classmethod
    def format_av_script(
        cls,
        title: str,
        project_slug: str,
        format_type: str,
        scenes: list[ScriptScene],
        output_path: Optional[Path] = None
    ) -> str:
        total_words = sum(len(s.narration_text.split()) for s in scenes)
        total_duration = sum(s.estimated_duration_seconds for s in scenes)

        lines = [
            f"# Audio/Visual Script: {title}",
            f"**Project**: `{project_slug}` | **Format**: `{format_type.upper()}`",
            f"**Total Words**: {total_words} | **Estimated Duration**: {round(total_duration, 1)} seconds\n",
            "| Scene # & Timecode | Visual Direction (What We See) | Narration (What We Hear) | Audio Design (SFX / Music) |",
            "|---|---|---|---|"
        ]

        for s in scenes:
            lines.append(
                f"| **{s.scene_id}**<br>({s.timecode_start}) | {s.visual_direction} | *\"{s.narration_text}\"* | {s.sound_design} |"
            )

        content = "\n".join(lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        return content
