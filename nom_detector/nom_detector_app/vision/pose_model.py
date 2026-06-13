"""Ensure BlazePose lite .task model exists (auto-download once)."""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

# Official MediaPipe-hosted asset (pinned path)
_POSE_LITE_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)
_MIN_BYTES = 50_000


def ensure_pose_landmarker_task(project_root: Path) -> Path:
    """
    Return path to pose_landmarker_lite.task under ``project_root/models``.

    Downloads on first run if missing or too small.
    """
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    out = models_dir / "pose_landmarker_lite.task"

    if out.is_file() and out.stat().st_size >= _MIN_BYTES:
        return out

    part = out.with_suffix(".task.download")
    if part.exists():
        part.unlink()

    req = urllib.request.Request(
        _POSE_LITE_URL,
        headers={"User-Agent": "nom-detector/1.0 (mediapipe pose landmarker)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} while downloading pose model") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"network error while downloading pose model: {e}") from e

    if len(data) < _MIN_BYTES:
        raise RuntimeError("downloaded pose model file is too small (incomplete?)")

    part.write_bytes(data)
    part.replace(out)
    return out
