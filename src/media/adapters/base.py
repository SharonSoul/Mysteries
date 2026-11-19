"""
Base adapter class for cultural heritage and stock media APIs.
Handles caching, rate-limiting, and standard asset formatting.
"""

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

import requests

from config.settings import CACHE_EXPIRY_HOURS, HTTP_USER_AGENT, MEDIA_LIBRARY_DIR
from src.models import MediaAsset

logger = logging.getLogger(__name__)


class BaseMediaAdapter(ABC):
    """Abstract base class for all media providers."""

    def __init__(self, name: str, cache_dir: Optional[Path] = None):
        self.name = name
        self.cache_dir = cache_dir or (MEDIA_LIBRARY_DIR / "images" / "cache" / name)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": HTTP_USER_AGENT})

    def _get_cache_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{hashed}.json"

    def _get_cached_data(self, key: str) -> Optional[dict[str, Any]]:
        path = self._get_cache_path(key)
        if not path.exists():
            return None

        # Check TTL
        mtime = path.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours > CACHE_EXPIRY_HOURS:
            try:
                path.unlink()
            except OSError:
                pass
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _set_cached_data(self, key: str, data: dict[str, Any]) -> None:
        path = self._get_cache_path(key)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.warning("Failed to write cache for %s: %s", key, e)

    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> list[MediaAsset]:
        """Search provider for media assets matching the query."""
        pass

    @abstractmethod
    def verify_connection(self) -> dict[str, Any]:
        """Check API connectivity and credential readiness."""
        pass
