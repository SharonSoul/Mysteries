"""
Configuration and settings management for Autonomous Documentary Studio.
Loads environment variables from .env safely.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
SRC_DIR = PROJECT_ROOT / "src"
MEDIA_LIBRARY_DIR = PROJECT_ROOT / "media-library"
PROJECTS_DIR = PROJECT_ROOT / "projects"
LOGS_DIR = PROJECT_ROOT / "logs"
EXPORTS_DIR = PROJECT_ROOT / "exports"
LICENSING_DIR = PROJECT_ROOT / "licensing-records"
RESEARCH_DIR = PROJECT_ROOT / "research-library"

# Load environment variables
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Credentials
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "NOpBlnGInO9m6vDvFkFC")

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
SMITHSONIAN_API_KEY = os.getenv("SMITHSONIAN_API_KEY", "")
OPENVERSE_CLIENT_ID = os.getenv("OPENVERSE_CLIENT_ID", "")
OPENVERSE_CLIENT_SECRET = os.getenv("OPENVERSE_CLIENT_SECRET", "")

# API Endpoints
PIXABAY_API_ENDPOINT = "https://pixabay.com/api/"
WIKIMEDIA_COMMONS_ENDPOINT = "https://commons.wikimedia.org/w/api.php"
LOC_API_ENDPOINT = "https://www.loc.gov/"
SMITHSONIAN_API_ENDPOINT = "https://api.si.edu/openaccess/api/v1.0/"
OPENVERSE_API_ENDPOINT = "https://api.openverse.org/v1/images/"

# Cache settings
CACHE_EXPIRY_HOURS = 24
HTTP_USER_AGENT = "MysteriesDocumentaryStudio/1.0 (Research & Documentary Studio; contact@example.com)"

# Video Specifications
VIDEO_SPECS = {
    "shorts": {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": "9:16",
        "fps": 30,
        "min_duration": 40,
        "max_duration": 90,
    },
    "longform": {
        "width": 1920,
        "height": 1080,
        "aspect_ratio": "16:9",
        "fps": 30,
        "min_duration": 600,
        "max_duration": 900,
    }
}

# Audio Specifications
AUDIO_SPECS = {
    "target_lufs": -14.0,
    "true_peak_db": -1.0,
    "loudness_range": 7.0,
    "sample_rate": 44100,
    "codec": "aac",
    "bitrate": "192k"
}

def verify_credentials() -> dict[str, bool]:
    """Returns status of configured credentials without exposing secrets."""
    return {
        "elevenlabs": bool(ELEVENLABS_API_KEY and not ELEVENLABS_API_KEY.startswith("your_")),
        "elevenlabs_voice_id": bool(ELEVENLABS_VOICE_ID),
        "pixabay": bool(PIXABAY_API_KEY and not PIXABAY_API_KEY.startswith("your_")),
        "smithsonian": bool(SMITHSONIAN_API_KEY and not SMITHSONIAN_API_KEY.startswith("your_")),
        "openverse": bool(OPENVERSE_CLIENT_ID and not OPENVERSE_CLIENT_ID.startswith("your_")),
    }
