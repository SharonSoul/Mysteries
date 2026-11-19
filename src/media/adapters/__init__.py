"""Media adapters package."""

from src.media.adapters.base import BaseMediaAdapter
from src.media.adapters.pixabay import PixabayAdapter
from src.media.adapters.wikimedia import WikimediaAdapter
from src.media.adapters.loc import LibraryOfCongressAdapter
from src.media.adapters.smithsonian import SmithsonianAdapter
from src.media.adapters.openverse import OpenverseAdapter

__all__ = [
    "BaseMediaAdapter",
    "PixabayAdapter",
    "WikimediaAdapter",
    "LibraryOfCongressAdapter",
    "SmithsonianAdapter",
    "OpenverseAdapter",
]
