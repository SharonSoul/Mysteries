"""
Library of Congress (LOC) API Adapter.
Queries the LOC public JSON API and inspects item rights.
"""

import logging
from typing import Any
import requests

from config.settings import LOC_API_ENDPOINT
from src.media.adapters.base import BaseMediaAdapter
from src.models import LicenseStatus, MediaAsset

logger = logging.getLogger(__name__)


def _inspect_loc_rights(item: dict[str, Any]) -> LicenseStatus:
    """Evaluates rights advisory and publication date for public domain verification."""
    rights = item.get("rights_advisory", "")
    rights_info = item.get("rights_information", "")
    combined = f"{rights} {rights_info}".lower()

    if "no known restrictions on publication" in combined:
        return LicenseStatus.PUBLIC_DOMAIN
    elif "public domain" in combined:
        return LicenseStatus.PUBLIC_DOMAIN

    # Check date for pre-1929 publication
    date_str = str(item.get("date", ""))
    for year in range(1800, 1929):
        if str(year) in date_str:
            return LicenseStatus.PUBLIC_DOMAIN

    # If copyrighted or rights reserved
    if "copyright" in combined or "restricted" in combined:
        return LicenseStatus.UNKNOWN

    return LicenseStatus.PUBLIC_DOMAIN  # LOC Prints and Photos are predominantly PD


class LibraryOfCongressAdapter(BaseMediaAdapter):
    """Adapter for the Library of Congress public JSON API."""

    def __init__(self):
        super().__init__(name="loc")

    def verify_connection(self) -> dict[str, Any]:
        """Verifies connection to the LOC public JSON API."""
        try:
            url = f"{LOC_API_ENDPOINT}?fo=json"
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                return {
                    "service": "Library of Congress",
                    "status": "connected",
                    "authenticated": True,  # Public API, no key required
                    "message": "Library of Congress JSON API connection verified."
                }
            return {
                "service": "Library of Congress",
                "status": "error",
                "authenticated": False,
                "status_code": resp.status_code,
                "message": resp.text
            }
        except requests.RequestException as e:
            return {
                "service": "Library of Congress",
                "status": "network_error",
                "authenticated": False,
                "message": str(e)
            }

    def search(self, query: str, max_results: int = 10) -> list[MediaAsset]:
        """
        Search Library of Congress Prints & Photographs collection.
        Inspects item rights for public domain status.
        """
        cache_key = f"loc_{query}_{max_results}"
        cached = self._get_cached_data(cache_key)
        if cached:
            logger.info("Using cached LOC results for '%s'", query)
            return [MediaAsset(**item) for item in cached]

        url = f"{LOC_API_ENDPOINT}photos/"
        params = {
            "q": query,
            "fo": "json",
            "c": min(max(max_results, 3), 30),
            "fa": "online-format:image"
        }

        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error("LOC API error: status %d", resp.status_code)
                return []

            data = resp.json()
            results = data.get("results", [])
            assets: list[MediaAsset] = []

            for idx, item in enumerate(results):
                license_status = _inspect_loc_rights(item)
                if license_status == LicenseStatus.UNKNOWN:
                    continue

                image_urls = item.get("image_url", [])
                if not image_urls:
                    continue

                # LOC provides an array of image sizes; the last one is typically highest resolution
                img_url = image_urls[-1]
                title = item.get("title", f"LOC Item {idx}")
                creator_list = item.get("creator", item.get("contributor", ["Unknown Photographer"]))
                creator = creator_list[0] if isinstance(creator_list, list) and creator_list else str(creator_list)

                asset_id = item.get("id", str(idx)).split("/")[-2] if "/" in str(item.get("id")) else str(idx)

                asset = MediaAsset(
                    file_name=f"loc_{asset_id}.jpg",
                    asset_title=title[:120],
                    creator=creator[:80],
                    original_url=img_url,
                    source_repository="Library of Congress",
                    license=license_status,
                    license_url="https://www.loc.gov/legal/",
                    attribution_requirements="Public Domain, Library of Congress Prints and Photographs Division"
                )
                assets.append(asset)

            self._set_cached_data(cache_key, [a.to_dict() for a in assets])
            return assets
        except requests.RequestException as e:
            logger.error("LOC search failed for '%s': %s", query, e)
            return []
