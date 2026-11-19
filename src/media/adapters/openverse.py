"""
Openverse API Adapter.
Queries the official Openverse API (formerly CC Search), enforces commercial
reusability filters, and extracts structured attribution data.
"""

import logging
from typing import Any
import requests

from config.settings import OPENVERSE_API_ENDPOINT, OPENVERSE_CLIENT_ID, OPENVERSE_CLIENT_SECRET
from src.media.adapters.base import BaseMediaAdapter
from src.models import LicenseStatus, MediaAsset

logger = logging.getLogger(__name__)


def _map_openverse_license(raw_license: str) -> LicenseStatus:
    raw = (raw_license or "").lower()
    if raw in ("pdm", "cc0", "public domain"):
        return LicenseStatus.PUBLIC_DOMAIN if raw == "pdm" else LicenseStatus.CC0
    elif raw == "by":
        return LicenseStatus.CC_BY
    elif raw == "by-sa":
        return LicenseStatus.CC_BY_SA
    elif "nc" in raw:
        return LicenseStatus.PROHIBITED_NC
    elif "nd" in raw:
        return LicenseStatus.PROHIBITED_ND
    return LicenseStatus.UNKNOWN


class OpenverseAdapter(BaseMediaAdapter):
    """Adapter for the official Openverse Creative Commons image search API."""

    def __init__(self, client_id: str = None, client_secret: str = None):
        super().__init__(name="openverse")
        self.client_id = client_id or OPENVERSE_CLIENT_ID
        self.client_secret = client_secret or OPENVERSE_CLIENT_SECRET

    def verify_connection(self) -> dict[str, Any]:
        """Verifies Openverse API reachability and status."""
        try:
            resp = self.session.get(
                OPENVERSE_API_ENDPOINT,
                params={"q": "archaeology", "page_size": 1, "license_type": "commercial"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("result_count", 0)
                return {
                    "service": "Openverse",
                    "status": "connected",
                    "authenticated": True,  # Public rate-limited tier active
                    "total_available": total,
                    "message": "Openverse API connection verified."
                }
            elif resp.status_code == 429:
                return {
                    "service": "Openverse",
                    "status": "rate_limited",
                    "authenticated": False,
                    "message": "Openverse rate limit reached. Back off before retrying."
                }
            return {
                "service": "Openverse",
                "status": "error",
                "authenticated": False,
                "status_code": resp.status_code,
                "message": resp.text
            }
        except requests.RequestException as e:
            return {
                "service": "Openverse",
                "status": "network_error",
                "authenticated": False,
                "message": str(e)
            }

    def search(self, query: str, max_results: int = 10) -> list[MediaAsset]:
        """
        Search Openverse for commercially reusable imagery.
        Filter strictly by license_type=commercial to exclude NC and ND media.
        """
        cache_key = f"openverse_{query}_{max_results}"
        cached = self._get_cached_data(cache_key)
        if cached:
            logger.info("Using cached Openverse results for '%s'", query)
            return [MediaAsset(**item) for item in cached]

        params = {
            "q": query,
            "license_type": "commercial",  # Excludes NC and ND
            "page_size": min(max(max_results, 3), 30)
        }

        try:
            resp = self.session.get(OPENVERSE_API_ENDPOINT, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error("Openverse API error: status %d", resp.status_code)
                return []

            data = resp.json()
            results = data.get("results", [])
            assets: list[MediaAsset] = []

            for item in results:
                raw_lic = item.get("license", "")
                license_status = _map_openverse_license(raw_lic)

                if license_status in (LicenseStatus.PROHIBITED_NC, LicenseStatus.PROHIBITED_ND, LicenseStatus.UNKNOWN):
                    continue

                attribution = item.get("attribution", "")
                if not attribution:
                    creator = item.get("creator", "Unknown")
                    attribution = f'"{item.get("title", "Image")}" by {creator} is licensed under CC {raw_lic.upper()}'

                asset = MediaAsset(
                    file_name=f"openverse_{item.get('id', 'item')}.jpg",
                    asset_title=item.get("title", "Openverse Image")[:120],
                    creator=item.get("creator", "Unknown")[:80],
                    original_url=item.get("url", ""),
                    source_repository="Openverse",
                    license=license_status,
                    license_url=item.get("license_url", "https://creativecommons.org/"),
                    attribution_requirements=attribution,
                    width=item.get("width"),
                    height=item.get("height")
                )
                assets.append(asset)

            self._set_cached_data(cache_key, [a.to_dict() for a in assets])
            return assets
        except requests.RequestException as e:
            logger.error("Openverse search failed for '%s': %s", query, e)
            return []
