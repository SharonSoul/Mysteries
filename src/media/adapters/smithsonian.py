"""
Smithsonian Open Access API Adapter.
Queries the official Smithsonian Open Access API and strictly filters
for media confirmed under Creative Commons Zero (CC0).
"""

import logging
from typing import Any
import requests

from config.settings import SMITHSONIAN_API_ENDPOINT, SMITHSONIAN_API_KEY
from src.media.adapters.base import BaseMediaAdapter
from src.models import LicenseStatus, MediaAsset

logger = logging.getLogger(__name__)


class SmithsonianAdapter(BaseMediaAdapter):
    """Adapter for the official Smithsonian Open Access API."""

    def __init__(self, api_key: str = None):
        super().__init__(name="smithsonian")
        self.api_key = api_key or SMITHSONIAN_API_KEY

    def verify_connection(self) -> dict[str, Any]:
        """Verifies API key and Smithsonian Open Access connectivity."""
        if not self.api_key or self.api_key.startswith("your_"):
            return {
                "service": "Smithsonian Open Access",
                "status": "missing_credentials",
                "authenticated": False,
                "message": "SMITHSONIAN_API_KEY is not configured in .env."
            }

        try:
            url = f"{SMITHSONIAN_API_ENDPOINT}search"
            resp = self.session.get(
                url,
                params={"api_key": self.api_key, "q": "artifact", "rows": 1, "online_media_type": "Images"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("response", {}).get("rowCount", 0)
                return {
                    "service": "Smithsonian Open Access",
                    "status": "connected",
                    "authenticated": True,
                    "total_available": total,
                    "message": "Smithsonian Open Access API connection verified."
                }
            elif resp.status_code in (401, 403):
                return {
                    "service": "Smithsonian Open Access",
                    "status": "auth_failed",
                    "authenticated": False,
                    "message": f"Smithsonian API key rejected (status {resp.status_code})."
                }
            else:
                return {
                    "service": "Smithsonian Open Access",
                    "status": "error",
                    "authenticated": False,
                    "status_code": resp.status_code,
                    "message": resp.text
                }
        except requests.RequestException as e:
            return {
                "service": "Smithsonian Open Access",
                "status": "network_error",
                "authenticated": False,
                "message": str(e)
            }

    def search(self, query: str, max_results: int = 10) -> list[MediaAsset]:
        """
        Search Smithsonian Open Access collections.
        Only returns assets confirmed as available under CC0.
        """
        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("Smithsonian search skipped: API key missing.")
            return []

        cache_key = f"smithsonian_{query}_{max_results}"
        cached = self._get_cached_data(cache_key)
        if cached:
            logger.info("Using cached Smithsonian results for '%s'", query)
            return [MediaAsset(**item) for item in cached]

        url = f"{SMITHSONIAN_API_ENDPOINT}search"
        params = {
            "api_key": self.api_key,
            "q": query,
            "rows": min(max(max_results, 3), 30),
            "online_media_type": "Images"
        }

        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error("Smithsonian API error: status %d", resp.status_code)
                return []

            data = resp.json()
            rows = data.get("response", {}).get("rows", [])
            assets: list[MediaAsset] = []

            for row in rows:
                content = row.get("content", {})
                descriptive = content.get("descriptiveNonRepeating", {})

                # Strict CC0 check
                usage = descriptive.get("metadata_usage", {}).get("access", "")
                if "CC0" not in usage.upper():
                    continue

                online_media = descriptive.get("online_media", {}).get("media", [])
                if not online_media:
                    continue

                # Locate primary image resource
                first_media = online_media[0]
                img_url = first_media.get("content")
                if not img_url:
                    resources = first_media.get("resources", [])
                    if resources:
                        img_url = resources[0].get("url")

                if not img_url:
                    continue

                title = row.get("title", "Smithsonian Artifact")
                unit_code = descriptive.get("unit_code", "Smithsonian Institution")
                item_id = row.get("id", "item")

                asset = MediaAsset(
                    file_name=f"smithsonian_{item_id}.jpg",
                    asset_title=title[:120],
                    creator=unit_code,
                    original_url=img_url,
                    source_repository="Smithsonian Open Access",
                    license=LicenseStatus.CC0,
                    license_url="https://creativecommons.org/publicdomain/zero/1.0/",
                    attribution_requirements=f"CC0 (Smithsonian Institution, {unit_code})"
                )
                assets.append(asset)

            self._set_cached_data(cache_key, [a.to_dict() for a in assets])
            return assets
        except requests.RequestException as e:
            logger.error("Smithsonian search failed for '%s': %s", query, e)
            return []
