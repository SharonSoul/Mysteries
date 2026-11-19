"""Unit tests for scriptwriting and storyboard planner."""

from pathlib import Path
from src.models import ScriptScene
from src.scriptwriting.formatter import ScriptFormatter
from src.storyboard.planner import StoryboardPlanner


def test_script_duration_estimation():
    text = "In the spring of 1900, sponge divers sheltering from a storm found an ancient machine."
    duration = ScriptFormatter.estimate_duration_seconds(text)
    assert 5.0 <= duration <= 9.0


def test_av_script_formatting(tmp_path: Path):
    scenes = [
        ScriptScene(
            scene_id="scene_01",
            timecode_start="00:00.00",
            visual_direction="Push in on ancient bronze artifact.",
            narration_text="Beneath the waves lay an impossible relic.",
            sound_design="Sub-bass pulse.",
            estimated_duration_seconds=5.0
        )
    ]
    output = tmp_path / "script.md"
    content = ScriptFormatter.format_av_script("Antikythera", "antikythera", "shorts", scenes, output)
    assert output.exists()
    assert "scene_01" in content
    assert "Beneath the waves lay an impossible relic." in content


def test_storyboard_planner():
    scenes = [
        ScriptScene(
            scene_id="scene_01",
            timecode_start="00:00.00",
            visual_direction="Photo of divers",
            narration_text="Divers found the wreckage.",
            sound_design="Wind howling",
            estimated_duration_seconds=4.0
        ),
        ScriptScene(
            scene_id="scene_02",
            timecode_start="00:04.00",
            visual_direction="Gear teeth close up",
            narration_text="Gears were revealed.",
            sound_design="Clockwork ticking",
            estimated_duration_seconds=5.0
        )
    ]
    asset_map = {"scene_01": "media/images/divers.jpg"}
    sb_scenes = StoryboardPlanner.build_storyboard_scenes(scenes, asset_map)
    assert len(sb_scenes) == 2
    assert sb_scenes[0].visual_asset_path == "media/images/divers.jpg"
    assert sb_scenes[0].motion_type == "zoom_in"
    assert sb_scenes[1].motion_type == "pan_left"
    assert sb_scenes[1].transition_type == "crossfade"
