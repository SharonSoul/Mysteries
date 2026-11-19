"""
Pixabay API Adapter.
Queries the official Pixabay API, caches responses for 24h,
and adheres to rate limits and commercial terms.
"""

import logging
from typing import Any
import requests

from config.settings import PIXABAY_API_ENDPOINT, PIXABAY_API_KEY
from src.media.adapters.base import BaseMediaAdapter
from src.models import LicenseStatus, MediaAsset

logger = logging.getLogger(__name__)


class PixabayAdapter(BaseMediaAdapter):
    """Adapter for official Pixabay Image API."""

    def __init__(self, api_key: str = None):
        super().__init__(name="pixabay")
        self.api_key = api_key or PIXABAY_API_KEY

    def verify_connection(self) -> dict[str, Any]:
        """Verifies API key and service availability."""
        if not self.api_key or self.api_key.startswith("your_"):
            return {
                "service": "Pixabay",
                "status": "missing_credentials",
                "authenticated": False,
                "message": "PIXABAY_API_KEY is not configured in .env."
            }

        try:
            resp = self.session.get(
                PIXABAY_API_ENDPOINT,
                params={"key": self.api_key, "q": "nature", "per_page": 3},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "service": "Pixabay",
                    "status": "connected",
                    "authenticated": True,
                    "total_hits": data.get("total", 0),
                    "message": "Pixabay API connection verified."
                }
            elif resp.status_code == 400:
                return {
                    "service": "Pixabay",
                    "status": "auth_failed",
                    "authenticated": False,
                    "message": f"Pixabay authentication failed: {resp.text}"
                }
            else:
                return {
                    "service": "Pixabay",
                    "status": "error",
                    "authenticated": False,
                    "status_code": resp.status_code,
                    "message": resp.text
                }
        except requests.RequestException as e:
            return {
                "service": "Pixabay",
                "status": "network_error",
                "authenticated": False,
                "message": str(e)
            }

    def search(self, query: str, max_results: int = 10) -> list[MediaAsset]:
        """
        Search Pixabay for photographic assets matching query.
        Caches responses for 24 hours. Does NOT perform mass downloads.
        """
        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("Pixabay search skipped: API key missing.")
            return []

        cache_key = f"pixabay_{query}_{max_results}"
        cached = self._get_cached_data(cache_key)
        if cached:
            logger.info("Using cached Pixabay results for '%s'", query)
            return [MediaAsset(**item) for item in cached]

        params = {
            "key": self.api_key,
            "q": query,
            "image_type": "photo",
            "orientation": "all",
            "safesearch": "true",
            "per_page": min(max(max_results, 3), 50),
        }

        try:
            resp = self.session.get(PIXABAY_API_ENDPOINT, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error("Pixabay API returned status %d: %s", resp.status_code, resp.text)
                return []

            data = resp.json()
            hits = data.get("hits", [])
            assets: list[MediaAsset] = []

            for hit in hits:
                asset = MediaAsset(
                    file_name=f"pixabay_{hit['id']}.jpg",
                    asset_title=hit.get("tags", f"Pixabay Image {hit['id']}"),
                    creator=hit.get("user", "Pixabay Contributor"),
                    original_url=hit.get("largeImageURL", hit.get("webformatURL", "")),
                    source_repository="Pixabay",
                    license=LicenseStatus.PIXABAY_LICENSE,
                    license_url="https://pixabay.com/service/license-summary/",
                    attribution_requirements="Pixabay Content License (Free for commercial use, no attribution required)",
                    width=hit.get("imageWidth"),
                    height=hit.get("imageHeight")
                )
                assets.append(asset)

            self._set_cached_data(cache_key, [a.to_dict() for a in assets])
            return assets
        except requests.RequestException as e:
            logger.error("Pixabay search request failed for query '%s': %s", query, e)
            return []
