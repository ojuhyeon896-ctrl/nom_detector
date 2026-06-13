"""Background vision thread: camera capture + MediaPipe Pose + smoothing."""

from __future__ import annotations

import math
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

from nom_detector_app import config
from nom_detector_app.vision.filters import MovingAverageFilter


def _neck_angle_and_screen_center(
    landmarks,
    frame_w: int,
    frame_h: int,
) -> Tuple[Optional[float], Optional[Tuple[int, int]]]:
    """
    Estimate forward-head proxy angle (degrees) and neck screen center (x, y).

    Uses ear–shoulder geometry (MediaPipe Pose): mid(ears) vs mid(shoulders).
    Returns None if visibility is poor.
    """
    lm = landmarks.landmark
    ls, rs = lm[11], lm[12]
    le, re = lm[7], lm[8]

    if (
        ls.visibility < config.POSE_MIN_VISIBILITY
        or rs.visibility < config.POSE_MIN_VISIBILITY
        or le.visibility < config.POSE_MIN_VISIBILITY
        or re.visibility < config.POSE_MIN_VISIBILITY
    ):
        return None, None

    sx = (ls.x + rs.x) * 0.5 * frame_w
    sy = (ls.y + rs.y) * 0.5 * frame_h
    ex = (le.x + re.x) * 0.5 * frame_w
    ey = (le.y + re.y) * 0.5 * frame_h

    dx = ex - sx
    dy = ey - sy
    angle_rad = math.atan2(abs(dx), max(1e-6, -dy))
    angle_deg = math.degrees(angle_rad)

    nx = int((sx + ex) * 0.5)
    ny = int((sy + ey) * 0.5)
    return float(angle_deg), (nx, ny)


def _bgr_to_qimage(bgr: np.ndarray) -> QImage:
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    return QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()


class VisionWorker(QThread):
    """Captures frames, runs MediaPipe Pose, emits UI-safe signals."""

    frame_ready = pyqtSignal(QImage)
    angle_ready = pyqtSignal(float)
    neck_screen_pos = pyqtSignal(int, int)
    pose_lost = pyqtSignal()
    fatal_error = pyqtSignal(str)

    def __init__(self, camera_index: int = 0, parent=None) -> None:
        super().__init__(parent)
        self._camera_index = camera_index
        self._running = False
        self._filter = MovingAverageFilter(config.MOVING_AVERAGE_WINDOW)

    def set_camera_index(self, index: int) -> None:
        self._camera_index = int(index)

    def reset_filter(self) -> None:
        self._filter.reset()

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        if not hasattr(mp, "solutions") or not hasattr(getattr(mp, "solutions", None), "pose"):
            self.fatal_error.emit(
                "MediaPipe 버전이 호환되지 않습니다.\n"
                "run.bat을 다시 실행해 자동 복구해 주세요."
            )
            return

        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            self.fatal_error.emit(
                "카메라를 열 수 없습니다.\n"
                "연결·다른 앱 점유·가상 카메라(Iriun) 순서 등을 확인해 주세요.\n"
                "(nom_detector_app\\config.py 의 DEFAULT_CAMERA_INDEX)"
            )
            return

        self._running = True
        try:
            mp_pose = mp.solutions.pose
            with mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            ) as pose:
                while self._running:
                    ok, frame = cap.read()
                    if not ok or frame is None:
                        continue

                    h, w = frame.shape[:2]
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    res = pose.process(rgb)

                    if res.pose_landmarks:
                        raw_angle, neck_xy = _neck_angle_and_screen_center(
                            res.pose_landmarks, w, h
                        )
                        if raw_angle is not None and neck_xy is not None:
                            smooth = self._filter.push(raw_angle)
                            self.angle_ready.emit(float(smooth))
                            self.neck_screen_pos.emit(int(neck_xy[0]), int(neck_xy[1]))
                        else:
                            self.pose_lost.emit()
                    else:
                        self.pose_lost.emit()

                    self.frame_ready.emit(_bgr_to_qimage(frame))
        except Exception as e:
            self.fatal_error.emit(f"비전 처리 중 오류:\n{e!s}")
        finally:
            cap.release()
