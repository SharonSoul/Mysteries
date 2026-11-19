"""
Visual Asset Discovery Module.
Coordinates multi-archive queries across Pixabay, Wikimedia Commons,
Library of Congress, Smithsonian, and Openverse.
"""

import logging
from typing import Optional

from src.media.adapters.loc import LibraryOfCongressAdapter
from src.media.adapters.openverse import OpenverseAdapter
from src.media.adapters.pixabay import PixabayAdapter
from src.media.adapters.smithsonian import SmithsonianAdapter
from src.media.adapters.wikimedia import WikimediaAdapter
from src.models import MediaAsset

logger = logging.getLogger(__name__)


class MediaDiscoveryManager:
    """Coordinates search across all configured media repositories."""

    def __init__(self):
        self.adapters = {
            "wikimedia": WikimediaAdapter(),
            "loc": LibraryOfCongressAdapter(),
            "smithsonian": SmithsonianAdapter(),
            "pixabay": PixabayAdapter(),
            "openverse": OpenverseAdapter(),
        }

    def check_all_connections(self) -> dict[str, dict]:
        """Runs health and connectivity checks on every media adapter."""
        results = {}
        for key, adapter in self.adapters.items():
            results[key] = adapter.verify_connection()
        return results

    def discover_assets(
        self,
        query: str,
        sources: Optional[list[str]] = None,
        max_per_source: int = 5
    ) -> list[MediaAsset]:
        """
        Discovers assets matching a query across selected sources.
        Prioritizes public domain and authentic cultural heritage sources.
        """
        selected_sources = sources or ["wikimedia", "loc", "smithsonian", "pixabay", "openverse"]
        aggregated: list[MediaAsset] = []

        for source_key in selected_sources:
            adapter = self.adapters.get(source_key)
            if not adapter:
                logger.warning("Unrecognized media adapter source: %s", source_key)
                continue

            try:
                results = adapter.search(query, max_results=max_per_source)
                aggregated.extend(results)
                logger.info("Found %d assets from %s for query '%s'", len(results), source_key, query)
            except Exception as e:
                logger.error("Failed to query %s for '%s': %s", source_key, query, e)

        return aggregated
