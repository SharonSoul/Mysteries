"""
Core domain models and data schemas for Autonomous Documentary Studio.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Any


class EpistemicTier(str, Enum):
    ESTABLISHED_FACT = "established_fact"
    SUPPORTED_INTERPRETATION = "supported_interpretation"
    DISPUTED_CLAIM = "disputed_claim"
    POPULAR_THEORY = "popular_theory"
    SPECULATION = "speculation"
    UNEXPLAINED_MYSTERY = "unexplained_mystery"


class LicenseStatus(str, Enum):
    PUBLIC_DOMAIN = "public_domain"
    CC0 = "cc0"
    CC_BY = "cc_by"
    CC_BY_SA = "cc_by_sa"
    PIXABAY_LICENSE = "pixabay_license"
    PROHIBITED_NC = "prohibited_non_commercial"
    PROHIBITED_ND = "prohibited_no_derivatives"
    UNKNOWN = "unknown"


@dataclass
class MediaAsset:
    file_name: str
    asset_title: str
    creator: str
    original_url: str
    source_repository: str  # Pixabay, Wikimedia, LOC, Smithsonian, Openverse
    license: LicenseStatus
    license_url: str
    download_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    intended_scene: str = ""
    attribution_requirements: str = ""
    local_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.license, str):
            try:
                self.license = LicenseStatus(self.license)
            except ValueError:
                self.license = LicenseStatus.UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["license"] = self.license.value
        return data


@dataclass
class FactCheckClaim:
    claim_id: str
    statement: str
    epistemic_tier: EpistemicTier
    primary_citation: str
    notes: str = ""
    verified: bool = False

    def __post_init__(self):
        if isinstance(self.epistemic_tier, str):
            try:
                self.epistemic_tier = EpistemicTier(self.epistemic_tier)
            except ValueError:
                self.epistemic_tier = EpistemicTier.UNEXPLAINED_MYSTERY

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["epistemic_tier"] = self.epistemic_tier.value
        return data


@dataclass
class ScriptScene:
    scene_id: str
    timecode_start: str
    visual_direction: str
    narration_text: str
    sound_design: str
    estimated_duration_seconds: float = 5.0


@dataclass
class StoryboardScene:
    scene_id: str
    chapter_index: int
    duration_seconds: float
    visual_asset_path: Optional[str]
    narration_text: str
    narration_audio_path: Optional[str] = None
    motion_type: str = "zoom_in"  # zoom_in, zoom_out, pan_left, pan_right, static
    transition_type: str = "crossfade"  # cut, crossfade, dip_black
    transition_duration: float = 0.5
    rendered_clip_path: Optional[str] = None


@dataclass
class ProductionStageStatus:
    research: str = "pending"          # pending, in_progress, completed, failed
    scriptwriting: str = "pending"
    storyboard: str = "pending"
    media_discovery: str = "pending"
    narration: str = "pending"
    subtitles: str = "pending"
    video_assembly: str = "pending"
    quality_control: str = "pending"
    human_approval: str = "pending"    # pending, approved, rejected


@dataclass
class ProductionManifest:
    project_slug: str
    title: str
    format_type: str                   # 'shorts' or 'longform'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    target_duration_seconds: float = 60.0
    stages: ProductionStageStatus = field(default_factory=ProductionStageStatus)
    scenes: list[StoryboardScene] = field(default_factory=list)
    assets: list[MediaAsset] = field(default_factory=list)
    claims: list[FactCheckClaim] = field(default_factory=list)
    output_video_path: Optional[str] = None
    output_thumbnail_path: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_slug": self.project_slug,
            "title": self.title,
            "format_type": self.format_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "target_duration_seconds": self.target_duration_seconds,
            "stages": asdict(self.stages),
            "scenes": [asdict(s) for s in self.scenes],
            "assets": [a.to_dict() for a in self.assets],
            "claims": [c.to_dict() for c in self.claims],
            "output_video_path": self.output_video_path,
            "output_thumbnail_path": self.output_thumbnail_path,
        }
