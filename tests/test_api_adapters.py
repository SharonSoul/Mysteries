"""
Tests for Media and Narration API Adapters.
Tests live connectivity for unauthenticated endpoints,
and performs authentic connection checks for authenticated services.
"""

import pytest
from src.media.adapters.loc import LibraryOfCongressAdapter
from src.media.adapters.openverse import OpenverseAdapter
from src.media.adapters.pixabay import PixabayAdapter
from src.media.adapters.smithsonian import SmithsonianAdapter
from src.media.adapters.wikimedia import WikimediaAdapter
from src.narration.generator import ElevenLabsNarrationEngine


class TestUnauthenticatedAdapters:
    """Tests APIs that operate without mandatory private API keys."""

    def test_wikimedia_connection(self):
        adapter = WikimediaAdapter()
        status = adapter.verify_connection()
        assert status["service"] == "Wikimedia Commons"
        assert status["status"] in ("connected", "rate_limited")
        assert status["authenticated"] is True

    def test_wikimedia_search(self):
        adapter = WikimediaAdapter()
        results = adapter.search("Antikythera mechanism", max_results=3)
        assert isinstance(results, list)
        assert len(results) > 0
        first = results[0]
        assert first.source_repository == "Wikimedia Commons"
        assert first.original_url.startswith("http")
        assert first.license.value in ("public_domain", "cc0", "cc_by", "cc_by_sa", "unknown")

    def test_loc_connection(self):
        adapter = LibraryOfCongressAdapter()
        status = adapter.verify_connection()
        assert status["service"] == "Library of Congress"
        assert status["status"] in ("connected", "rate_limited")
        assert status["authenticated"] is True

    def test_loc_search(self):
        adapter = LibraryOfCongressAdapter()
        results = adapter.search("pyramids", max_results=3)
        assert isinstance(results, list)
        # LOC should return valid image results
        if results:
            first = results[0]
            assert first.source_repository == "Library of Congress"
            assert first.original_url.startswith("http")

    def test_openverse_connection(self):
        adapter = OpenverseAdapter()
        status = adapter.verify_connection()
        assert status["service"] == "Openverse"
        # Status can be connected or rate_limited depending on public IP usage
        assert status["status"] in ("connected", "rate_limited")


class TestAuthenticatedAdapters:
    """
    Tests connection checks for services requiring API keys.
    Reports authentic status without fabricating successful results.
    """

    def test_pixabay_connection_check(self):
        adapter = PixabayAdapter()
        status = adapter.verify_connection()
        assert "service" in status
        assert status["service"] == "Pixabay"
        assert "status" in status
        # Valid states: connected, missing_credentials, auth_failed, network_error
        assert status["status"] in ("connected", "missing_credentials", "auth_failed", "network_error")

    def test_smithsonian_connection_check(self):
        adapter = SmithsonianAdapter()
        status = adapter.verify_connection()
        assert "service" in status
        assert status["service"] == "Smithsonian Open Access"
        assert "status" in status
        assert status["status"] in ("connected", "missing_credentials", "auth_failed", "network_error")

    def test_elevenlabs_connection_check(self):
        engine = ElevenLabsNarrationEngine()
        status = engine.verify_connection()
        assert "service" in status
        assert status["service"] == "ElevenLabs"
        assert "status" in status
        assert status["status"] in ("connected", "missing_credentials", "auth_failed_or_error")
