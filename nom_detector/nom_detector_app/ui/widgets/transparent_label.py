"""Transparent QLabel helper for PNG cat overlays (no rembg / no setMask)."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


def apply_transparent_cat_style(label: QLabel) -> None:
    """PyQt5 transparent rendering for already-transparent PNG assets."""
    label.setAttribute(Qt.WA_TranslucentBackground, True)
    label.setStyleSheet("background-color: transparent; border: none;")
    label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
    label.setAutoFillBackground(False)
