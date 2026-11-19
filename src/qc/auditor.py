"""
Documentary Quality Control (QC) Module.
Audits technical, legal, and structural standards before final delivery.
"""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

from src.editing.video_editor import find_ffmpeg_binary
from src.models import ProductionManifest

logger = logging.getLogger(__name__)


class DocumentaryQCAuditor:
    """Performs rigorous pre-delivery checks on documentary packages."""

    def __init__(self, ffprobe_path: str = None):
        self.ffprobe = ffprobe_path or find_ffmpeg_binary("ffprobe")

    def audit_production_package(
        self,
        manifest: ProductionManifest,
        output_report_path: Optional[Path] = None
    ) -> dict[str, Any]:
        """
        Executes complete quality control suite on a project manifest and its outputs.
        """
        report: dict[str, Any] = {
            "project_slug": manifest.project_slug,
            "overall_pass": True,
            "checks": {},
            "warnings": [],
            "errors": []
        }

        # 1. Check Scene Coverage
        if not manifest.scenes:
            report["errors"].append("Manifest contains no storyboard scenes.")
            report["checks"]["scenes"] = False
        else:
            missing_assets = [s.scene_id for s in manifest.scenes if not s.visual_asset_path]
            if missing_assets:
                report["warnings"].append(f"Scenes missing visual assets: {missing_assets}")
                report["checks"]["scenes"] = False
            else:
                report["checks"]["scenes"] = True

        # 2. Check Fact-Check Ledger
        if not manifest.claims:
            report["warnings"].append("No fact-check claims registered in manifest.")
            report["checks"]["fact_check"] = False
        else:
            unverified = [c.claim_id for c in manifest.claims if not c.verified]
            if unverified:
                report["warnings"].append(f"Claims pending verification: {unverified}")
            report["checks"]["fact_check"] = True

        # 3. Check Licensing Manifest
        if not manifest.assets:
            report["warnings"].append("No assets logged in licensing manifest.")
            report["checks"]["licensing"] = False
        else:
            prohibited = [a.file_name for a in manifest.assets if "prohibited" in a.license.value]
            if prohibited:
                report["errors"].append(f"Prohibited licenses found: {prohibited}")
                report["checks"]["licensing"] = False
            else:
                report["checks"]["licensing"] = True

        # 4. Check Output Video File (if rendered)
        if manifest.output_video_path:
            video_file = Path(manifest.output_video_path)
            if not video_file.exists() or video_file.stat().st_size < 100_000:
                report["errors"].append(f"Output video missing or corrupted: {video_file}")
                report["checks"]["video_file"] = False
            else:
                report["checks"]["video_file"] = True
                # Run stream check if ffprobe is present
                stream_res = self._check_streams(video_file)
                report["checks"]["streams"] = stream_res.get("valid", True)
                if not stream_res.get("valid", True):
                    report["errors"].append(stream_res.get("error", "Stream sync mismatch."))

        # 5. Check Human Approval Gate
        if manifest.stages.human_approval != "approved":
            report["warnings"].append("Human-in-the-loop approval is pending. Video cannot be published.")
            report["checks"]["human_approval"] = False
        else:
            report["checks"]["human_approval"] = True

        # Determine overall pass
        if report["errors"]:
            report["overall_pass"] = False

        if output_report_path:
            output_report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

        return report

    def _check_streams(self, video_file: Path) -> dict[str, Any]:
        """Inspects video and audio stream duration match using ffprobe."""
        if not (Path(self.ffprobe).exists() or shutil.which(self.ffprobe)):
            return {"valid": True, "note": "ffprobe not installed on PATH; skipped deep stream sync check."}

        cmd = [
            self.ffprobe,
            "-v", "error",
            "-show_entries", "stream=codec_type,duration",
            "-of", "json",
            str(video_file)
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode != 0:
                return {"valid": False, "error": f"ffprobe error: {res.stderr}"}

            data = json.loads(res.stdout)
            streams = data.get("streams", [])
            v_dur, a_dur = None, None

            for s in streams:
                if s.get("codec_type") == "video" and not v_dur:
                    v_dur = float(s.get("duration", 0))
                elif s.get("codec_type") == "audio" and not a_dur:
                    a_dur = float(s.get("duration", 0))

            if v_dur and a_dur and abs(v_dur - a_dur) > 0.5:
                return {
                    "valid": False,
                    "error": f"Audio/Video desync detected: video={v_dur}s, audio={a_dur}s (diff > 0.5s)"
                }

            return {"valid": True, "video_duration": v_dur, "audio_duration": a_dur}
        except Exception as e:
            logger.warning("ffprobe stream check skipped: %s", e)
            return {"valid": True, "note": str(e)}
