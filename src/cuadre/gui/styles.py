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
RED = "#C62828"


def build_stylesheet(zoom: int = 100) -> str:
    body = scaled(14, zoom)
    small = scaled(12, zoom)
    heading = scaled(24, zoom)
    title = scaled(18, zoom)
    section = scaled(15, zoom)
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
            background: {NAVY};
            border: none;
            border-radius: {radius}px;
        }}
        QLabel#brandPlaceholder {{
            color: {WHITE};
            font-family: 'Montserrat', 'Arial', sans-serif;
            font-size: {heading}px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        }}
        QLabel#storeLine {{
            color: {YELLOW};
            font-family: 'Montserrat', 'Arial', sans-serif;
            font-size: {small}px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#screenTitle {{
            color: {WHITE};
            font-family: 'Montserrat', 'Arial', sans-serif;
            font-size: {title}px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#metadata {{
            color: {LIGHT};
            font-size: {small}px;
            background: transparent;
        }}

        QFrame#contentSurface {{
            background: {LIGHT};
            border: 1px solid {BORDER};
            border-radius: {radius}px;
        }}
        QLabel#previewTitle {{
            color: {NAVY};
            font-family: 'Montserrat', 'Arial', sans-serif;
            font-size: {title}px;
            font-weight: 700;
            font-style: italic;
            background: transparent;
            padding-top: {scaled(5, zoom)}px;
            padding-bottom: {scaled(2, zoom)}px;
        }}
        QLabel#previewRowLabel {{
            color: {CHARCOAL};
            font-size: {small}px;
            font-style: italic;
            background: transparent;
        }}
        QLabel#previewRowValue {{
            color: {CHARCOAL};
            font-size: {body}px;
            background: transparent;
        }}
        QLabel#previewNote {{
            color: {MUTED};
            font-size: {small}px;
            font-style: italic;
            background: transparent;
        }}
        QFrame#previewRow {{
            background: transparent;
            border-bottom: 1px solid {BORDER};
        }}
        QScrollArea, QScrollArea > QWidget > QWidget {{
            background: transparent;
            border: none;
        }}
        QFrame#footer {{
            background: {CHARCOAL};
            border: none;
            border-radius: {radius}px;
        }}
        QWidget#footerCenter, QWidget#zoomControls {{
            background: transparent;
        }}
        QLabel#footerLogo {{
            background: transparent;
            border: none;
        }}
        QLabel#footerText {{
            color: {YELLOW};
            font-size: {small}px;
            font-style: italic;
            background: transparent;
        }}
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

        QPushButton#printButton {{
            background: {NAVY};
            color: {WHITE};
            border: 1px solid {NAVY};
        }}
        QPushButton#printButton:hover {{ background: {CHARCOAL}; }}
        QPushButton#notifyButton {{
            background: {RED};
            color: {WHITE};
            border: 1px solid {RED};
        }}
        QPushButton#notifyButton:hover {{ background: #A51F1F; }}

        QLabel#placeholderText {{ color: {MUTED}; }}
        QMenuBar {{ background: {LIGHT}; color: {CHARCOAL}; }}
        QMenu {{ background: {WHITE}; color: {CHARCOAL}; }}
    """
