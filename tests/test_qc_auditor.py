"""Unit tests for quality control auditor."""

from src.models import (
    EpistemicTier,
    FactCheckClaim,
    LicenseStatus,
    MediaAsset,
    ProductionManifest,
    StoryboardScene
)
from src.qc.auditor import DocumentaryQCAuditor


def test_qc_auditor_empty_manifest():
    auditor = DocumentaryQCAuditor()
    manifest = ProductionManifest(
        project_slug="empty-test",
        title="Empty Project",
        format_type="longform"
    )
    report = auditor.audit_production_package(manifest)
    assert report["overall_pass"] is False
    assert len(report["errors"]) > 0


def test_qc_auditor_prohibited_license():
    auditor = DocumentaryQCAuditor()
    manifest = ProductionManifest(
        project_slug="license-fail-test",
        title="License Fail Project",
        format_type="longform"
    )
    manifest.scenes = [
        StoryboardScene(
            scene_id="s1",
            chapter_index=1,
            duration_seconds=5.0,
            visual_asset_path="media/img.jpg",
            narration_text="Test narration"
        )
    ]
    manifest.claims = [
        FactCheckClaim(
            claim_id="c1",
            statement="Sample claim statement for test.",
            epistemic_tier=EpistemicTier.ESTABLISHED_FACT,
            primary_citation="Test Journal (2020)",
            verified=True
        )
    ]
    manifest.assets = [
        MediaAsset(
            file_name="bad.jpg",
            asset_title="NC image",
            creator="Photographer",
            original_url="https://example.com/bad.jpg",
            source_repository="Web",
            license=LicenseStatus.PROHIBITED_NC,
            license_url="https://creativecommons.org/"
        )
    ]

    report = auditor.audit_production_package(manifest)
    assert report["overall_pass"] is False
    assert any("Prohibited licenses" in err for err in report["errors"])
