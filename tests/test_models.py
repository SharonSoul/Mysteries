"""Unit tests for core models."""

import pytest
from src.models import (
    EpistemicTier,
    LicenseStatus,
    MediaAsset,
    FactCheckClaim,
    ScriptScene,
    StoryboardScene,
    ProductionManifest
)


def test_media_asset_to_dict():
    asset = MediaAsset(
        file_name="test.jpg",
        asset_title="Ancient Relic",
        creator="Archaeologist John",
        original_url="https://example.com/relic.jpg",
        source_repository="Wikimedia Commons",
        license=LicenseStatus.PUBLIC_DOMAIN,
        license_url="https://creativecommons.org/publicdomain/mark/1.0/",
        intended_scene="scene_01",
        attribution_requirements="Public Domain"
    )
    d = asset.to_dict()
    assert d["file_name"] == "test.jpg"
    assert d["license"] == "public_domain"
    assert d["intended_scene"] == "scene_01"


def test_fact_check_claim_to_dict():
    claim = FactCheckClaim(
        claim_id="C01",
        statement="The Antikythera mechanism was discovered in 1901.",
        epistemic_tier=EpistemicTier.ESTABLISHED_FACT,
        primary_citation="Price, D. (1974)",
        verified=True
    )
    d = claim.to_dict()
    assert d["epistemic_tier"] == "established_fact"
    assert d["verified"] is True


def test_production_manifest_lifecycle():
    manifest = ProductionManifest(
        project_slug="test-mystery",
        title="The Mystery of Oak Island",
        format_type="shorts",
        target_duration_seconds=60.0
    )
    assert manifest.stages.research == "pending"
    assert manifest.stages.human_approval == "pending"
    d = manifest.to_dict()
    assert d["project_slug"] == "test-mystery"
    assert d["format_type"] == "shorts"
