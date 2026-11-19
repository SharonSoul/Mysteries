---
name: python-automation-standards
description: Python development standards, modular architecture patterns, subprocess safety for FFmpeg, and error handling for the documentary studio automation pipeline. Use when writing, debugging, or reviewing Python automation scripts in the automation/ directory.
license: Apache-2.0
metadata: {"python_version": ">=3.10", "patterns": ["subprocess_safety", "modular_pipelines", "idempotency"]}
---

# Python Automation Standards for Documentary Studio

This skill defines software engineering practices and architectural patterns for building automated, modular production pipelines in the `automation/` directory of the **Mysteries & Unexplained History Documentary Studio**.

## Studio Architectural Principles

1. **Modular Independence**: Each step of the pipeline must be an independent, runnable Python module:
   - `automation/research_topic.py`
   - `automation/generate_script.py`
   - `automation/fetch_archival_media.py`
   - `automation/synthesize_narration.py`
   - `automation/generate_subtitles.py`
   - `automation/render_scenes.py`
   - `automation/assemble_documentary.py`
2. **Granular Regeneration**: The user must be able to re-render scene 4 or re-generate narration for chapter 2 without re-executing or re-rendering the entire 15-minute documentary.
3. **Idempotent Caching**: Check if intermediate assets (downloaded images, audio WAVs, rendered scene clips) already exist before downloading or rendering again.
4. **Environment Isolation**: Never hardcode API keys or secret tokens. Always access credentials via `os.getenv("ELEVENLABS_API_KEY")`.

## Safe Subprocess Execution for FFmpeg

On Windows, executing FFmpeg commands via Python requires careful path handling, escaping, and timeout monitoring:

```python
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def run_ffmpeg_command(cmd: list[str], timeout_seconds: int = 600) -> None:
    """
    Executes an FFmpeg command list safely with structured logging and timeout.
    Always pass arguments as a list of strings, never a raw shell string.
    """
    logger.info("Executing FFmpeg command: %s", " ".join(cmd))
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=True
        )
    except subprocess.TimeoutExpired as e:
        logger.error("FFmpeg process timed out after %d seconds: %s", timeout_seconds, e)
        raise
    except subprocess.CalledProcessError as e:
        logger.error("FFmpeg command failed with exit code %d.", e.returncode)
        logger.error("FFmpeg stderr: %s", e.stderr)
        raise RuntimeError(f"FFmpeg error: {e.stderr}") from e
```

## Structured Project Data Model

Use dataclasses or Pydantic to represent project states, scenes, and asset manifests:

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class Scene:
    scene_id: str
    chapter_index: int
    duration_seconds: float
    visual_asset_path: Path
    narration_text: str
    motion_type: str  # 'zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'static'
    audio_path: Optional[Path] = None
    rendered_clip_path: Optional[Path] = None

@dataclass
class DocumentaryProject:
    project_slug: str
    title: str
    format_type: str  # 'shorts' or 'longform'
    target_duration: float
    scenes: list[Scene] = field(default_factory=list)
```

## Error Handling & Logging

All automation runs must log to `logs/<module_name>_<date>.log`:

```python
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(module_name: str) -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{module_name}_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(module_name)
```
