"""
Research Dossier Management.
Compiles comprehensive research files for projects.
"""

from pathlib import Path
from typing import Optional
from config.settings import RESEARCH_DIR


class ResearchDossierManager:
    """Creates and manages research dossiers in the research-library."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or RESEARCH_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_dossier(
        self,
        project_slug: str,
        title: str,
        core_mystery: str,
        timeline_events: list[str],
        archaeological_evidence: list[str],
        academic_theories: list[str],
        bibliography: list[str]
    ) -> Path:
        proj_dir = self.base_dir / project_slug
        proj_dir.mkdir(parents=True, exist_ok=True)
        dossier_path = proj_dir / "research_dossier.md"

        content = [
            f"# Research Dossier: {title}",
            f"**Project Slug**: {project_slug}\n",
            "## 1. Core Mystery & Investigative Scope",
            core_mystery,
            "\n## 2. Chronological Timeline",
            "\n".join(f"- {event}" for event in timeline_events) if timeline_events else "- None recorded.",
            "\n## 3. Archaeological & Physical Evidence",
            "\n".join(f"- {ev}" for ev in archaeological_evidence) if archaeological_evidence else "- None recorded.",
            "\n## 4. Academic Theories & Debates",
            "\n".join(f"- {th}" for th in academic_theories) if academic_theories else "- None recorded.",
            "\n## 5. Annotated Bibliography & Sources",
            "\n".join(f"1. {src}" for src in bibliography) if bibliography else "1. None recorded.",
            ""
        ]

        with open(dossier_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

        return dossier_path
