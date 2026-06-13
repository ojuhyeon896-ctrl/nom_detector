"""Application paths and vision thresholds."""

from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def _asset(*candidates: str) -> Path:
    for name in candidates:
        p = ASSETS / name
        if p.is_file():
            return p
    return ASSETS / candidates[0]


BG_MAIN = _asset("bg_main_bright.png", "bg_main_bright.png.png")
BG_SUB = _asset("bg_sub_bright.png", "bg_sub_bright.png.png")

POSTURE_GUIDE_IMAGE = _asset("posture_guide.png", "posture_guide.png.png")
POSTURE_GUIDE_TEXT = (
    "모니터 상단과 눈높이를 맞추고, 귀-어깨-골반이 수직선상에 놓이도록 허리를 펴고 앉으세요."
)

HOW_TO_USE: List[Tuple[Path, str]] = [
    (
        _asset("how_1.png", "how_1.png.png"),
        "PC와 스마트폰에 Iriun Webcam을 설치하고 같은 Wi-Fi에 연결해 카메라를 준비하세요.",
    ),
    (
        _asset("how_2.png", "how_2.png.png"),
        "상황에 따라 방해 금지가 필요하면 '백그라운드 모드'를 체크하세요.",
    ),
    (
        _asset("how_3.png", "how_3.png.png"),
        "[모니터링 시작]을 누른 뒤, 바른 자세를 취하고 [기준값 측정]을 진행하세요.",
    ),
    (
        _asset("how_4.png", "how_4.png.png"),
        "집중해서 공부하세요! 자세가 흐트러져 경고가 뜨면 즉시 바른 자세로 고쳐 앉으세요.",
    ),
    (
        _asset("how_5.png", "how_5.png.png"),
        "할 일을 마친 후 [통계]를 확인하여, 내 자세가 무너지는 패턴과 흐트러진 시간을 점검하세요.",
    ),
]

CAT_IDLE = _asset("cat_idle.png", "cat_idle.png.png")
CAT_PUNCH = _asset("cat_punch.png", "cat_punch.png.png")

POSE_MIN_VISIBILITY = 0.5
MOVING_AVERAGE_WINDOW = 7
WARN_DEG = 6.0
DANGER_DEG = 12.0

CALIBRATION_SECONDS = 3
CAT_WANDER_INTERVAL_MS = 75
CAT_PUNCH_ANIM_MS = 900
FLASH_PULSE_COUNT = 3

STATS_BUCKET_MINUTES = 5
STATS_SAMPLE_INTERVAL_SEC = 2.0

DEFAULT_CAMERA_INDEX = -1
