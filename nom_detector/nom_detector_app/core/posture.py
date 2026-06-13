"""Posture level classification from calibrated neck angle."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from nom_detector_app import config


class PostureLevel(Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    DANGER = "DANGER"
    UNKNOWN = "UNKNOWN"

    @property
    def label_ko(self) -> str:
        return {
            PostureLevel.NORMAL: "정상",
            PostureLevel.WARNING: "경고",
            PostureLevel.DANGER: "위험",
            PostureLevel.UNKNOWN: "측정 대기",
        }[self]


def classify_posture(
    angle_deg: float,
    baseline_deg: Optional[float],
    warn_deg: float = config.WARN_DEG,
    danger_deg: float = config.DANGER_DEG,
) -> PostureLevel:
    """Return posture level from smoothed angle and calibrated baseline."""
    if baseline_deg is None:
        return PostureLevel.UNKNOWN
    dev = abs(float(angle_deg) - float(baseline_deg))
    if dev >= float(danger_deg):
        return PostureLevel.DANGER
    if dev >= float(warn_deg):
        return PostureLevel.WARNING
    return PostureLevel.NORMAL
