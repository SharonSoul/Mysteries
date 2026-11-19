"""
Storyboard & Scene Planning Module.
Converts script scenes into actionable storyboard manifests for FFmpeg editing.
"""

import json
from pathlib import Path
from typing import Optional
from src.models import StoryboardScene, ScriptScene


class StoryboardPlanner:
    """Plans scene-by-scene motion, transitions, and asset mapping."""

    @classmethod
    def build_storyboard_scenes(
        cls,
        script_scenes: list[ScriptScene],
        asset_map: Optional[dict[str, str]] = None
    ) -> list[StoryboardScene]:
        """
        Builds StoryboardScene objects from script scenes, matching
        visual asset paths and setting appropriate motion types.
        """
        asset_map = asset_map or {}
        storyboard: list[StoryboardScene] = []

        # Alternate motion types for visual dynamism
        motion_cycle = ["zoom_in", "pan_left", "zoom_out", "pan_right"]

        for idx, scene in enumerate(script_scenes):
            motion = motion_cycle[idx % len(motion_cycle)]
            asset_path = asset_map.get(scene.scene_id)

            sb_scene = StoryboardScene(
                scene_id=scene.scene_id,
                chapter_index=1,
                duration_seconds=max(scene.estimated_duration_seconds, 3.0),
                visual_asset_path=asset_path,
                narration_text=scene.narration_text,
                motion_type=motion,
                transition_type="crossfade" if idx > 0 else "cut",
                transition_duration=0.5
            )
            storyboard.append(sb_scene)

        return storyboard

    @classmethod
    def export_storyboard(cls, scenes: list[StoryboardScene], output_file: Path) -> Path:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "scene_id": s.scene_id,
                "chapter": s.chapter_index,
                "duration": s.duration_seconds,
                "visual_asset": s.visual_asset_path,
                "motion": s.motion_type,
                "transition": s.transition_type,
                "narration_text": s.narration_text
            }
            for s in scenes
        ]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output_file
