BG_DARK = "#05060f"
BG_PANEL = "#0b0e1e"
BG_PANEL_LIGHT = "#11142a"
BORDER = "#22264a"
ACCENT_BLUE = "#4f6bff"
ACCENT_PURPLE = "#8a4fff"
ACCENT_CYAN = "#22d3ee"
ACCENT_PINK = "#ec4899"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
ERROR = "#ef4444"
TEXT_PRIMARY = "#e6e8ff"
TEXT_SECONDARY = "#8a8fb8"

FONT_FAMILY = "Segoe UI"

STYLESHEET = f"""
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: '{FONT_FAMILY}';
    font-size: 13px;
}}

QMainWindow {{
    background-color: {BG_DARK};
}}

#Sidebar {{
    background-color: {BG_PANEL};
    border-right: 1px solid {BORDER};
}}

#NavButton {{
    text-align: left;
    padding: 10px 18px;
    border: none;
    border-left: 3px solid transparent;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    letter-spacing: 1px;
    background: transparent;
}}

#NavButton:hover {{
    color: {TEXT_PRIMARY};
    background-color: {BG_PANEL_LIGHT};
}}

#NavButton[active="true"] {{
    color: {ACCENT_CYAN};
    border-left: 3px solid {ACCENT_CYAN};
    background-color: {BG_PANEL_LIGHT};
}}

#HeaderPanel {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
}}

QFrame#Card, QFrame#Panel {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QLabel#TitleLabel {{
    font-size: 26px;
    font-weight: 800;
    color: {TEXT_PRIMARY};
    letter-spacing: 1px;
}}

QLabel#SubtitleLabel {{
    color: {TEXT_SECONDARY};
    font-size: 13px;
}}

QLabel#SectionLabel {{
    color: {ACCENT_CYAN};
    font-weight: 700;
    letter-spacing: 1px;
    font-size: 11px;
}}

QLabel#StatValue {{
    font-size: 24px;
    font-weight: 800;
    color: {ACCENT_CYAN};
}}

QLabel#StatLabel {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
    letter-spacing: 1px;
}}

QPushButton {{
    background-color: {BG_PANEL_LIGHT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 9px 16px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QPushButton:hover {{
    border: 1px solid {ACCENT_CYAN};
    color: {ACCENT_CYAN};
}}

QPushButton#PrimaryButton {{
    background-color: {ACCENT_PURPLE};
    border: 1px solid {ACCENT_PURPLE};
    color: white;
}}

QPushButton#PrimaryButton:hover {{
    background-color: {ACCENT_BLUE};
    border: 1px solid {ACCENT_BLUE};
}}

QPushButton#SuccessButton {{
    background-color: {SUCCESS};
    border: 1px solid {SUCCESS};
    color: #04220f;
}}

QProgressBar {{
    background-color: {BG_PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT_PRIMARY};
    height: 16px;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_PURPLE}, stop:1 {ACCENT_CYAN});
    border-radius: 6px;
}}

QTableWidget {{
    background-color: {BG_PANEL};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
}}

QHeaderView::section {{
    background-color: {BG_PANEL_LIGHT};
    color: {TEXT_SECONDARY};
    border: none;
    padding: 6px;
    font-weight: 700;
}}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {BG_PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 6px;
    color: {TEXT_PRIMARY};
}}

QScrollArea {{
    border: none;
}}

QSlider::groove:horizontal {{
    background: {BORDER};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {ACCENT_CYAN};
    width: 14px;
    margin: -6px 0;
    border-radius: 7px;
}}
"""
