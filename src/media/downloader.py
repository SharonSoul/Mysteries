"""
Asset Downloading & Organization Module.
Downloads approved assets safely, validates file integrity with Pillow,
and organizes files into project and media-library trees.
"""

import logging
from pathlib import Path
from typing import Optional
import requests
from PIL import Image

from config.settings import HTTP_USER_AGENT
from src.models import MediaAsset

logger = logging.getLogger(__name__)


class AssetDownloader:
    """Handles controlled, validated asset downloads."""

    def __init__(self, user_agent: str = HTTP_USER_AGENT):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def download_asset(
        self,
        asset: MediaAsset,
        destination_dir: Path,
        custom_filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Downloads a single media asset, verifies file integrity,
        and saves it to the specified destination directory.
        """
        if not asset.original_url:
            logger.error("Cannot download asset %s: No original_url provided.", asset.asset_title)
            return None

        destination_dir.mkdir(parents=True, exist_ok=True)
        filename = custom_filename or asset.file_name
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        target_path = destination_dir / safe_filename

        # If already downloaded and valid, return existing
        if target_path.exists() and target_path.stat().st_size > 5000:
            if self._validate_image(target_path):
                logger.info("Asset already exists and is valid: %s", target_path)
                asset.local_path = str(target_path)
                return target_path

        try:
            logger.info("Downloading asset '%s' from %s", asset.asset_title, asset.original_url)
            resp = self.session.get(asset.original_url, stream=True, timeout=30)
            if resp.status_code != 200:
                logger.error("Download failed for %s (Status %d)", asset.original_url, resp.status_code)
                return None

            with open(target_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            # File size sanity check (under 5KB is likely a broken redirect or error HTML page)
            if target_path.stat().st_size < 5000:
                logger.error("Downloaded file is suspiciously small (%d bytes). Discarding.", target_path.stat().st_size)
                target_path.unlink(missing_ok=True)
                return None

            # Validate image structure
            if not self._validate_image(target_path):
                logger.error("Image file integrity check failed for %s. Discarding.", target_path)
                target_path.unlink(missing_ok=True)
                return None

            asset.local_path = str(target_path)
            logger.info("Successfully downloaded and validated: %s", target_path)
            return target_path

        except Exception as e:
            logger.error("Error downloading asset %s: %s", asset.asset_title, e)
            if target_path.exists():
                target_path.unlink(missing_ok=True)
            return None

    def _validate_image(self, file_path: Path) -> bool:
        """Verifies that the downloaded file is a readable image."""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.debug("Image validation failed for %s: %s", file_path, e)
            return False
