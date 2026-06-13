"""Matplotlib Korean font configuration for statistics charts."""

from __future__ import annotations

import platform

import matplotlib.pyplot as plt

_CONFIGURED = False


def configure_matplotlib_korean_font() -> None:
    """
    Apply OS-appropriate Korean font and fix minus-sign rendering.

    Safe to call multiple times; runs only once per process.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    system = platform.system()
    if system == "Windows":
        plt.rc("font", family="Malgun Gothic")
    elif system == "Darwin":
        plt.rc("font", family="AppleGothic")
    else:
        plt.rc("font", family="NanumGothic")

    plt.rcParams["axes.unicode_minus"] = False
    _CONFIGURED = True
