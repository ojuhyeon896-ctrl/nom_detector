"""Camera probing and auto-selection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np


@dataclass
class CameraProbe:
    index: int
    ok: bool
    width: int = 0
    height: int = 0
    sharpness: float = 0.0
    score: float = -1.0


def _open_camera(index: int) -> cv2.VideoCapture:
    # On Windows, DSHOW usually gives more stable webcam enumeration.
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(index)
    return cap


def _probe_one(index: int) -> CameraProbe:
    cap = _open_camera(index)
    if not cap.isOpened():
        cap.release()
        return CameraProbe(index=index, ok=False)

    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return CameraProbe(index=index, ok=False)

    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Prefer higher resolution cameras (often phone virtual cams).
    # Small bonus for non-zero index because laptop built-in camera is commonly 0.
    score = float(w * h) + min(sharpness, 300.0) * 300.0 + (25_000.0 if index > 0 else 0.0)
    return CameraProbe(index=index, ok=True, width=w, height=h, sharpness=sharpness, score=score)


def select_camera_index(
    preferred_index: int = -1,
    scan_limit: int = 8,
) -> Tuple[Optional[int], List[CameraProbe]]:
    """
    Select camera index.

    - If preferred_index >= 0, use it when readable.
    - If preferred_index < 0, auto-scan [0, scan_limit) and pick best-scoring camera.
    """
    if preferred_index >= 0:
        probe = _probe_one(preferred_index)
        return (preferred_index if probe.ok else None), [probe]

    results: List[CameraProbe] = []
    for i in range(max(1, int(scan_limit))):
        p = _probe_one(i)
        results.append(p)

    alive = [p for p in results if p.ok]
    if not alive:
        return None, results

    best = max(alive, key=lambda p: p.score)
    return best.index, results

