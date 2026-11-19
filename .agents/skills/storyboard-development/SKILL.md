---
name: storyboard-development
description: Plan scene-by-scene visual breakdowns, motion instructions, transition timings, map overlays, and asset manifests for documentary production. Use when converting a completed script into an actionable production storyboard, assigning visual assets to timecodes, and specifying camera motion for FFmpeg rendering.
license: MIT
metadata: {"scope": "projects", "component": "storyboard"}
---

# Storyboard & Scene Planning

This skill guides the creation of scene-by-scene production storyboards that bridge scriptwriting with automated video editing in FFmpeg.

## Core Responsibilities

1. **Scene Segmentation**: Break the script down into discrete scenes (typically 3–7 seconds per visual asset).
2. **Visual Type Assignment**: Assign each scene a specific asset category:
   - `historical_photo`: Archival photography.
   - `map`: Antique or modern cartographic reference.
   - `manuscript`: Ancient text, codex, or papyrus scan.
   - `diagram`: Custom explanatory graphic or timeline.
   - `reconstruction`: Clearly labeled illustrative reconstruction (never presented as authentic footage).
3. **Motion Directives**: Define the camera movement for static imagery:
   - `zoom_in`: Slow push-in toward a specific detail (1.0x to 1.15x).
   - `zoom_out`: Slow pull-back revealing scale (1.15x to 1.0x).
   - `pan_left` / `pan_right`: Horizontal sweep across a map or panorama.
   - `static`: Stationary view for technical diagrams or high-detail inscriptions.
4. **Transition Selection**:
   - `cut`: Clean cut for rapid pacing and shorts.
   - `crossfade`: 0.5s dissolve between archival shots.
   - `dip_to_black`: 0.8s transition between major historical chapters.

## Production Storyboard Manifest Schema

Save storyboards in `projects/<project-slug>/storyboard.json` and a human-readable `storyboard.md`:

```json
{
  "project_slug": "antikythera-mechanism",
  "format": "longform",
  "resolution": [1920, 1080],
  "fps": 30,
  "scenes": [
    {
      "scene_id": "scene_01",
      "chapter": 1,
      "timecode_start": "00:00.00",
      "duration": 5.0,
      "narration_audio": "audio/scene_01_narration.wav",
      "visual_asset": "media/images/diving_boat_1900.jpg",
      "asset_type": "historical_photo",
      "motion": {
        "type": "zoom_in",
        "speed": 0.0015,
        "focal_point": [0.5, 0.4]
      },
      "transition": {
        "type": "crossfade",
        "duration": 0.5
      },
      "overlay_text": null
    }
  ]
}
```
