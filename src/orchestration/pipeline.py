"""
Production Orchestration Module.
Coordinates the end-to-end documentary pipeline across research, scriptwriting,
media sourcing, narration, video assembly, and quality control.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import PROJECTS_DIR, LOGS_DIR
from src.licensing.verifier import LicensingVerifier
from src.media.discovery import MediaDiscoveryManager
from src.media.downloader import AssetDownloader
from src.models import (
    MediaAsset,
    ProductionManifest,
    ProductionStageStatus,
    ScriptScene,
    StoryboardScene,
)
from src.narration.generator import ElevenLabsNarrationEngine
from src.qc.auditor import DocumentaryQCAuditor
from src.research.fact_checker import HistoricalFactChecker
from src.scriptwriting.formatter import ScriptFormatter
from src.storyboard.planner import StoryboardPlanner
from src.subtitles.generator import SubtitleGenerator
from src.thumbnail.generator import ThumbnailGenerator

logger = logging.getLogger(__name__)


class ProductionOrchestrator:
    """Manages project lifecycles, manifests, and stage execution."""

    def __init__(self, projects_dir: Optional[Path] = None):
        self.projects_dir = projects_dir or PROJECTS_DIR
        self.projects_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sub-modules
        self.discovery = MediaDiscoveryManager()
        self.downloader = AssetDownloader()
        self.licensing = LicensingVerifier()
        self.fact_checker = HistoricalFactChecker()
        self.qc = DocumentaryQCAuditor()
        self.narration = ElevenLabsNarrationEngine()

    def create_project(
        self,
        project_slug: str,
        title: str,
        format_type: str = "longform",
        target_duration: float = 600.0
    ) -> ProductionManifest:
        """Initializes a new isolated documentary project."""
        proj_dir = self.projects_dir / project_slug
        proj_dir.mkdir(parents=True, exist_ok=True)

        # Subfolders
        (proj_dir / "media" / "images" / "raw").mkdir(parents=True, exist_ok=True)
        (proj_dir / "media" / "audio").mkdir(parents=True, exist_ok=True)
        (proj_dir / "exports").mkdir(parents=True, exist_ok=True)

        manifest = ProductionManifest(
            project_slug=project_slug,
            title=title,
            format_type=format_type,
            target_duration_seconds=target_duration
        )

        self.save_manifest(manifest)
        logger.info("Initialized project %s at %s", project_slug, proj_dir)
        return manifest

    def load_manifest(self, project_slug: str) -> Optional[ProductionManifest]:
        """Loads an existing project manifest from disk."""
        manifest_file = self.projects_dir / project_slug / "manifest.json"
        if not manifest_file.exists():
            return None

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        manifest = ProductionManifest(
            project_slug=data["project_slug"],
            title=data["title"],
            format_type=data["format_type"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            target_duration_seconds=data["target_duration_seconds"],
            stages=ProductionStageStatus(**data["stages"]),
            scenes=[StoryboardScene(**s) for s in data["scenes"]],
            assets=[MediaAsset(**a) for a in data["assets"]],
            output_video_path=data.get("output_video_path"),
            output_thumbnail_path=data.get("output_thumbnail_path")
        )
        return manifest

    def save_manifest(self, manifest: ProductionManifest) -> Path:
        """Saves current manifest state to disk."""
        manifest.updated_at = datetime.now().isoformat()
        proj_dir = self.projects_dir / manifest.project_slug
        proj_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = proj_dir / "manifest.json"

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)

        return manifest_file

    def get_project_dir(self, project_slug: str) -> Path:
        return self.projects_dir / project_slug
