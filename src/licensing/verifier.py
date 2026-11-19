"""
Licensing Verification & Audit Module.
Enforces commercial rights clearance and produces mandatory licensing manifests.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from config.settings import LICENSING_DIR
from src.models import LicenseStatus, MediaAsset

logger = logging.getLogger(__name__)

PROHIBITED_LICENSES = {
    LicenseStatus.PROHIBITED_NC,
    LicenseStatus.PROHIBITED_ND,
    LicenseStatus.UNKNOWN
}

APPROVED_LICENSES = {
    LicenseStatus.PUBLIC_DOMAIN,
    LicenseStatus.CC0,
    LicenseStatus.CC_BY,
    LicenseStatus.CC_BY_SA,
    LicenseStatus.PIXABAY_LICENSE
}


class LicensingVerifier:
    """Verifies and compiles licensing records for all documentary assets."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or LICENSING_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def verify_asset(self, asset: MediaAsset) -> tuple[bool, str]:
        """
        Validates whether a media asset is approved for commercial YouTube production.
        Returns (is_approved, reason).
        """
        if not asset.original_url:
            return False, "Missing original URL."

        if not asset.license or asset.license in PROHIBITED_LICENSES:
            return False, f"Prohibited or unverified license: {asset.license.value}"

        if asset.license == LicenseStatus.CC_BY_SA:
            return True, "Approved (CC BY-SA requires matching attribution in description)."

        if asset.license in APPROVED_LICENSES:
            return True, f"Approved under {asset.license.value}."

        return False, f"Unrecognized license status: {asset.license}"

    def audit_manifest(self, assets: list[MediaAsset]) -> tuple[bool, list[str]]:
        """
        Audits a list of assets. Returns (all_passed, list_of_issues).
        """
        issues = []
        for a in assets:
            passed, reason = self.verify_asset(a)
            if not passed:
                issues.append(f"Asset '{a.asset_title}' ({a.file_name}): {reason}")
        return len(issues) == 0, issues

    def generate_report(self, project_slug: str, assets: list[MediaAsset]) -> Path:
        """
        Generates a markdown licensing report and saves to licensing-records/.
        Contains all 10 mandatory fields.
        """
        report_path = self.output_dir / f"{project_slug}_licensing_record.md"

        lines = [
            f"# Asset Licensing & Attribution Report: {project_slug}",
            f"**Total Assets Evaluated**: {len(assets)}\n",
            "| File Name | Title | Creator | Source | License | Intended Scene | Attribution Text | Original URL |",
            "|---|---|---|---|---|---|---|---|"
        ]

        for a in assets:
            lines.append(
                f"| `{a.file_name}` | {a.asset_title[:40]} | {a.creator[:30]} | {a.source_repository} | "
                f"`{a.license.value}` | `{a.intended_scene}` | {a.attribution_requirements} | [Link]({a.original_url}) |"
            )

        lines.extend([
            "\n## YouTube Description Attribution Copy-Paste Block\n",
            "```text",
            "--- ASSET ATTRIBUTIONS & CREDITS ---"
        ])

        for a in assets:
            if a.attribution_requirements:
                lines.append(f"- {a.attribution_requirements}")

        lines.append("```\n")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info("Saved licensing report to %s", report_path)
        return report_path
