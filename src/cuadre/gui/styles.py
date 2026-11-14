"""Centralized visual identity and stylesheet generation."""

from cuadre.gui.scaling import scaled

CHARCOAL = "#2B2B2B"
NAVY = "#3F3F54"
ORANGE = "#F48B25"
YELLOW = "#EEDA63"
LIGHT = "#F4F4F4"
WHITE = "#FFFFFF"
MUTED = "#777783"
BORDER = "#E2E2E6"


def build_stylesheet(zoom: int = 100) -> str:
    body = scaled(14, zoom)
    small = scaled(12, zoom)
    heading = scaled(24, zoom)
    title = scaled(18, zoom)
    radius = scaled(7, zoom)
    padding = scaled(10, zoom)
    return f"""
        QWidget {{
            color: {CHARCOAL};
            background: {LIGHT};
            font-family: 'Lato', 'Arial', sans-serif;
            font-size: {body}px;
        }}
        QMainWindow {{ background: {LIGHT}; }}
        QFrame#header {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: {radius}px;
        }}
        QLabel#brandPlaceholder {{
            color: {NAVY};
            font-family: 'Montserrat', 'Arial', sans-serif;
            font-size: {heading}px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        QLabel#storeLine {{
            color: {NAVY};
            font-family: 'Montserrat', 'Arial', sans-serif;
            font-size: {small}px;
            font-weight: 600;
        }}
        QLabel#screenTitle {{
            color: {CHARCOAL};
            font-family: 'Montserrat', 'Arial', sans-serif;
            font-size: {title}px;
            font-weight: 700;
        }}
        QLabel#metadata {{ color: {MUTED}; font-size: {small}px; }}
        QLabel#zoomLabel {{ color: {MUTED}; font-size: {small}px; }}
        QPushButton {{
            min-width: {scaled(32, zoom)}px;
            min-height: {scaled(30, zoom)}px;
            padding: 0 {padding}px;
            border: 1px solid {BORDER};
            border-radius: {radius}px;
            background: {WHITE};
            color: {NAVY};
            font-weight: 600;
        }}
        QPushButton:hover {{ border-color: {ORANGE}; }}
        QPushButton:pressed {{ background: {YELLOW}; }}
        QFrame#contentSurface {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: {radius}px;
        }}
        QLabel#placeholderText {{ color: {MUTED}; }}
        QMenuBar {{ background: {LIGHT}; color: {CHARCOAL}; }}
        QMenu {{ background: {WHITE}; color: {CHARCOAL}; }}
    """
