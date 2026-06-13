"""Global Qt Style Sheets and typography."""

from __future__ import annotations

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

FONT_FAMILY = '"Segoe UI", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif'

APP_STYLESHEET = f"""
QWidget {{
    font-family: {FONT_FAMILY};
    font-size: 13px;
    color: #1e293b;
}}

QLabel#HeroTitle {{
    font-size: 72px;
    font-weight: 800;
    color: #0d47a1;
    letter-spacing: -1px;
}}

QLabel#HeroSubtitle {{
    font-size: 20px;
    font-weight: 500;
    color: #455a64;
}}

QCheckBox#HomeBackgroundCheck {{
    font-size: 19px;
    font-weight: 700;
    color: #1a237e;
    spacing: 14px;
    padding: 10px 18px;
    background: rgba(255, 255, 255, 0.78);
    border-radius: 8px;
    border: 1px solid rgba(30, 107, 168, 0.25);
}}

QCheckBox#HomeBackgroundCheck::indicator {{
    width: 26px;
    height: 26px;
    border-radius: 6px;
    border: 1px solid rgba(30, 107, 168, 0.45);
    background: rgba(255, 255, 255, 0.92);
}}

QCheckBox#HomeBackgroundCheck::indicator:checked {{
    background: #1565c0;
    border-color: #0d47a1;
}}

QLabel#ScreenTitle {{
    font-size: 28px;
    font-weight: 700;
    color: #0d47a1;
}}

QLabel#SectionTitle {{
    font-size: 20px;
    font-weight: 700;
    color: #1565c0;
    padding-top: 8px;
}}

QLabel#ManualCaption {{
    font-size: 16px;
    font-weight: 500;
    color: #263238;
    line-height: 1.45;
}}

QLabel#ManualStep {{
    font-size: 14px;
    font-weight: 700;
    color: #0d47a1;
    min-width: 28px;
}}

QPushButton {{
    background-color: rgba(255, 255, 255, 0.94);
    color: #1a237e;
    border: 1px solid rgba(30, 107, 168, 0.28);
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 600;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: #ffffff;
    border-color: #1e6ba8;
    color: #0d47a1;
}}

QPushButton:pressed {{
    background-color: #e3f2fd;
}}

QPushButton:disabled {{
    background-color: rgba(245, 247, 250, 0.85);
    color: #90a4ae;
    border-color: #cfd8dc;
}}

QPushButton#Primary {{
    background-color: #1565c0;
    color: #ffffff;
    border: 1px solid #0d47a1;
    font-size: 16px;
}}

QPushButton#Primary:hover {{
    background-color: #1976d2;
}}

QPushButton#Primary:pressed {{
    background-color: #0d47a1;
}}

QLabel#StatusBadge {{
    font-size: 15px;
    font-weight: 700;
    padding: 8px 16px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(30, 107, 168, 0.2);
}}

QLabel#StatusBadge[nomState="NORMAL"] {{
    color: #2e7d32;
    border-color: rgba(46, 125, 50, 0.35);
    background: rgba(232, 245, 233, 0.92);
}}

QLabel#StatusBadge[nomState="WARNING"] {{
    color: #e65100;
    border-color: rgba(230, 81, 0, 0.35);
    background: rgba(255, 243, 224, 0.94);
}}

QLabel#StatusBadge[nomState="DANGER"] {{
    color: #b71c1c;
    border-color: rgba(183, 28, 28, 0.4);
    background: rgba(255, 235, 238, 0.94);
}}

QLabel#StatusBadge[nomState="UNKNOWN"] {{
    color: #546e7a;
}}

QLabel#StatsInsight {{
    font-size: 15px;
    font-weight: 500;
    color: #37474f;
    padding: 14px 18px;
    background: rgba(255, 255, 255, 0.88);
    border-radius: 8px;
    border: 1px solid rgba(30, 107, 168, 0.18);
}}
"""


def apply_app_style(app: QApplication) -> None:
    app.setStyleSheet(APP_STYLESHEET)
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
