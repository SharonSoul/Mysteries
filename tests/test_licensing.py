"""Unit tests for licensing verification."""

import pytest
from pathlib import Path
from src.licensing.verifier import LicensingVerifier
from src.models import LicenseStatus, MediaAsset


def test_licensing_approval_rules():
    verifier = LicensingVerifier()

    # Public domain approved
    pd_asset = MediaAsset(
        file_name="pd.jpg",
        asset_title="Ancient Map",
        creator="Cartographer",
        original_url="https://example.com/map.jpg",
        source_repository="LOC",
        license=LicenseStatus.PUBLIC_DOMAIN,
        license_url="https://loc.gov"
    )
    approved, msg = verifier.verify_asset(pd_asset)
    assert approved is True

    # CC0 approved
    cc0_asset = MediaAsset(
        file_name="cc0.jpg",
        asset_title="Smithsonian Artifact",
        creator="Smithsonian",
        original_url="https://example.com/artifact.jpg",
        source_repository="Smithsonian",
        license=LicenseStatus.CC0,
        license_url="https://creativecommons.org/publicdomain/zero/1.0/"
    )
    approved, msg = verifier.verify_asset(cc0_asset)
    assert approved is True

    # Non-Commercial strictly rejected
    nc_asset = MediaAsset(
        file_name="nc.jpg",
        asset_title="Restricted Photo",
        creator="Photographer",
        original_url="https://example.com/photo.jpg",
        source_repository="Flickr",
        license=LicenseStatus.PROHIBITED_NC,
        license_url="https://creativecommons.org/licenses/by-nc/4.0/"
    )
    approved, msg = verifier.verify_asset(nc_asset)
    assert approved is False
    assert "Prohibited" in msg


def test_generate_licensing_report(tmp_path: Path):
    verifier = LicensingVerifier(output_dir=tmp_path)
    asset = MediaAsset(
        file_name="test.jpg",
        asset_title="Roman Coin",
        creator="British Museum",
        original_url="https://example.com/coin.jpg",
        source_repository="Wikimedia",
        license=LicenseStatus.CC_BY,
        license_url="https://creativecommons.org/licenses/by/4.0/",
        intended_scene="scene_01",
        attribution_requirements="Photo by BM via Wikimedia (CC BY 4.0)"
    )
    report_file = verifier.generate_report("roman-coins", [asset])
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Roman Coin" in content
    assert "CC BY 4.0" in content
    assert "Photo by BM via Wikimedia" in content
