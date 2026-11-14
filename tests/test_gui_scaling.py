from cuadre.gui.scaling import (
    DEFAULT_ZOOM,
    MAX_ZOOM,
    MIN_ZOOM,
    clamp_zoom,
    scaled,
)


def test_default_zoom_is_100_percent():
    assert DEFAULT_ZOOM == 100


def test_clamp_zoom_enforces_supported_range():
    assert clamp_zoom(MIN_ZOOM - 10) == MIN_ZOOM
    assert clamp_zoom(MAX_ZOOM + 10) == MAX_ZOOM
    assert clamp_zoom(110) == 110


def test_scaled_metric_tracks_zoom_and_never_returns_zero():
    assert scaled(20, 100) == 20
    assert scaled(20, 80) == 16
    assert scaled(20, 130) == 26
    assert scaled(1, 80) == 1
