"""
Fact-Checking and Epistemic Verification Module.
Implements the 6-tier truth classification framework for historical mysteries.
"""

import logging
from pathlib import Path
from typing import Optional

from config.settings import RESEARCH_DIR
from src.models import EpistemicTier, FactCheckClaim

logger = logging.getLogger(__name__)


class HistoricalFactChecker:
    """Manages claim verification and epistemic status grading."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or RESEARCH_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def validate_claim(self, claim: FactCheckClaim) -> tuple[bool, str]:
        """
        Validates claim adherence to non-negotiable research rules.
        """
        if not claim.statement or len(claim.statement.strip()) < 10:
            return False, "Claim statement is empty or too brief."

        if not claim.primary_citation:
            return False, "Missing primary citation or scholarly reference."

        if claim.epistemic_tier == EpistemicTier.SPECULATION:
            return True, "Flagged as Speculation: Must be phrased as an unproven theory in script."

        if claim.epistemic_tier == EpistemicTier.UNEXPLAINED_MYSTERY:
            return True, "Flagged as Unexplained Mystery: Script must present lack of definitive consensus."

        return True, f"Claim classified as {claim.epistemic_tier.value}."

    def generate_ledger(self, project_slug: str, claims: list[FactCheckClaim]) -> Path:
        """
        Outputs a structured Fact-Check Ledger markdown file into research-library/.
        """
        proj_dir = self.output_dir / project_slug
        proj_dir.mkdir(parents=True, exist_ok=True)
        ledger_path = proj_dir / "fact_check_ledger.md"

        lines = [
            f"# Fact-Check & Verification Ledger: {project_slug}",
            f"**Total Claims Checked**: {len(claims)}\n",
            "| Claim ID | Statement | Epistemic Classification | Primary Citation | Verification Status | Notes |",
            "|---|---|---|---|---|---|"
        ]

        for c in claims:
            status_mark = "Verified" if c.verified else "Pending Review"
            tier_display = c.epistemic_tier.value.replace("_", " ").title()
            lines.append(
                f"| `{c.claim_id}` | {c.statement[:60]} | **{tier_display}** | {c.primary_citation[:40]} | `{status_mark}` | {c.notes} |"
            )

        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info("Saved fact-check ledger to %s", ledger_path)
        return ledger_path
