"""Application-wide visual scaling helpers."""

from __future__ import annotations


MIN_ZOOM = 80
MAX_ZOOM = 130
ZOOM_STEP = 10
DEFAULT_ZOOM = 100


def clamp_zoom(value: int) -> int:
    """Return a supported zoom percentage."""
    return max(MIN_ZOOM, min(MAX_ZOOM, int(value)))


def scaled(value: int, zoom: int) -> int:
    """Scale a pixel/point metric and keep it at least one unit."""
    return max(1, round(value * clamp_zoom(zoom) / 100))
