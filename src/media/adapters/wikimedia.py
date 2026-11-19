"""
Wikimedia Commons API Adapter.
Queries the official MediaWiki API, includes a customized User-Agent,
and extracts comprehensive licensing metadata.
"""

import logging
import re
from typing import Any
import requests

from config.settings import WIKIMEDIA_COMMONS_ENDPOINT
from src.media.adapters.base import BaseMediaAdapter
from src.models import LicenseStatus, MediaAsset

logger = logging.getLogger(__name__)


def _clean_html(raw_html: str) -> str:
    """Strip HTML tags from MediaWiki metadata fields."""
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", "", raw_html)
    return clean.strip()


def _map_wikimedia_license(short_name: str) -> LicenseStatus:
    """Maps Wikimedia Commons license string to LicenseStatus enum."""
    name = (short_name or "").lower()
    if "public domain" in name or "pd" in name:
        return LicenseStatus.PUBLIC_DOMAIN
    elif "cc0" in name:
        return LicenseStatus.CC0
    elif "cc-by-sa" in name or "cc by-sa" in name:
        return LicenseStatus.CC_BY_SA
    elif "cc-by" in name or "cc by" in name:
        return LicenseStatus.CC_BY
    elif "nc" in name:
        return LicenseStatus.PROHIBITED_NC
    elif "nd" in name:
        return LicenseStatus.PROHIBITED_ND
    return LicenseStatus.UNKNOWN


class WikimediaAdapter(BaseMediaAdapter):
    """Adapter for Wikimedia Commons MediaWiki API."""

    def __init__(self):
        super().__init__(name="wikimedia")

    def verify_connection(self) -> dict[str, Any]:
        """Tests live connectivity to Wikimedia Commons MediaWiki API."""
        try:
            params = {
                "action": "query",
                "meta": "siteinfo",
                "format": "json"
            }
            resp = self.session.get(WIKIMEDIA_COMMONS_ENDPOINT, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                sitename = data.get("query", {}).get("general", {}).get("sitename", "Wikimedia Commons")
                return {
                    "service": "Wikimedia Commons",
                    "status": "connected",
                    "authenticated": True,  # Public API, no key required
                    "sitename": sitename,
                    "message": "Wikimedia Commons MediaWiki API connection verified."
                }
            elif resp.status_code == 429:
                return {
                    "service": "Wikimedia Commons",
                    "status": "rate_limited",
                    "authenticated": True,
                    "message": "Wikimedia rate limit reached."
                }
            return {
                "service": "Wikimedia Commons",
                "status": "error",
                "authenticated": False,
                "status_code": resp.status_code,
                "message": resp.text
            }
        except requests.RequestException as e:
            return {
                "service": "Wikimedia Commons",
                "status": "network_error",
                "authenticated": False,
                "message": str(e)
            }

    def search(self, query: str, max_results: int = 10) -> list[MediaAsset]:
        """
        Search Wikimedia Commons for images in the File: namespace (6).
        Retrieves detailed imageinfo and extmetadata (License, Artist, Description).
        """
        cache_key = f"wikimedia_{query}_{max_results}"
        cached = self._get_cached_data(cache_key)
        if cached:
            logger.info("Using cached Wikimedia results for '%s'", query)
            return [MediaAsset(**item) for item in cached]

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap",
            "gsrnamespace": "6",
            "gsrlimit": min(max(max_results, 3), 30),
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
            "format": "json"
        }

        try:
            resp = self.session.get(WIKIMEDIA_COMMONS_ENDPOINT, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error("Wikimedia API error: status %d", resp.status_code)
                return []

            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            assets: list[MediaAsset] = []

            for page_id, page_data in pages.items():
                imageinfo_list = page_data.get("imageinfo", [])
                if not imageinfo_list:
                    continue

                info = imageinfo_list[0]
                metadata = info.get("extmetadata", {})

                raw_license = metadata.get("LicenseShortName", {}).get("value", "Unknown")
                license_status = _map_wikimedia_license(raw_license)

                # Skip prohibited non-commercial or no-derivatives media
                if license_status in (LicenseStatus.PROHIBITED_NC, LicenseStatus.PROHIBITED_ND):
                    logger.debug("Skipping asset due to license %s: %s", raw_license, page_data.get("title"))
                    continue

                artist = _clean_html(metadata.get("Artist", {}).get("value", "Unknown"))
                description = _clean_html(metadata.get("ImageDescription", {}).get("value", page_data.get("title", "")))
                license_url = metadata.get("LicenseUrl", {}).get("value", "https://commons.wikimedia.org/")

                # Attribution requirement string
                credit = _clean_html(metadata.get("Credit", {}).get("value", ""))
                attribution = f"{artist} via Wikimedia Commons ({raw_license})" if artist else f"Wikimedia Commons ({raw_license})"
                if credit:
                    attribution += f" - {credit}"

                title_clean = page_data.get("title", "Wikimedia_File").replace("File:", "").replace(" ", "_")

                asset = MediaAsset(
                    file_name=f"wikimedia_{page_id}_{title_clean[:40]}.jpg",
                    asset_title=description[:120] if description else title_clean,
                    creator=artist[:80] if artist else "Wikimedia Commons Uploader",
                    original_url=info.get("url", ""),
                    source_repository="Wikimedia Commons",
                    license=license_status,
                    license_url=license_url,
                    attribution_requirements=attribution,
                    width=info.get("width"),
                    height=info.get("height")
                )
                assets.append(asset)

            self._set_cached_data(cache_key, [a.to_dict() for a in assets])
            return assets
        except requests.RequestException as e:
            logger.error("Wikimedia search failed for '%s': %s", query, e)
            return []
