"""Session statistics: dwell time, events, time-series samples."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from nom_detector_app import config
from nom_detector_app.core.posture import PostureLevel


@dataclass
class PostureEvent:
    """Discrete WARNING/DANGER onset during monitoring."""

    elapsed_sec: float
    level: PostureLevel


@dataclass
class TimelineSample:
    elapsed_sec: float
    severity: int  # 0=NORMAL, 1=WARNING, 2=DANGER


class SessionStatsTracker:
    def __init__(self) -> None:
        self._seconds: Dict[PostureLevel, float] = {
            PostureLevel.NORMAL: 0.0,
            PostureLevel.WARNING: 0.0,
            PostureLevel.DANGER: 0.0,
        }
        self._current = PostureLevel.UNKNOWN
        self._last_mono = time.monotonic()
        self._session_start_mono: Optional[float] = None
        self._running = False
        self._events: List[PostureEvent] = []
        self._timeline: List[TimelineSample] = []
        self._last_sample_mono = 0.0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._current = PostureLevel.UNKNOWN
        now = time.monotonic()
        self._session_start_mono = now
        self._last_mono = now
        self._last_sample_mono = now
        self._events.clear()
        self._timeline.clear()

    def stop(self) -> None:
        if not self._running:
            return
        self._flush()
        self._sample_timeline(force=True)
        self._running = False
        self._current = PostureLevel.UNKNOWN

    def reset(self) -> None:
        was = self._running
        if was:
            self.stop()
        self._seconds = {
            PostureLevel.NORMAL: 0.0,
            PostureLevel.WARNING: 0.0,
            PostureLevel.DANGER: 0.0,
        }
        self._events.clear()
        self._timeline.clear()
        if was:
            self.start()

    def _elapsed(self) -> float:
        if self._session_start_mono is None:
            return 0.0
        return max(0.0, time.monotonic() - self._session_start_mono)

    @staticmethod
    def _severity(level: PostureLevel) -> int:
        if level == PostureLevel.DANGER:
            return 2
        if level == PostureLevel.WARNING:
            return 1
        if level == PostureLevel.NORMAL:
            return 0
        return 0

    def set_state(self, state: PostureLevel) -> None:
        if not self._running:
            return

        prev = self._current
        if state == PostureLevel.UNKNOWN:
            self._flush_to_unknown()
            self._sample_timeline(force=True)
            return
        if state != prev:
            self._flush()
            if state in (PostureLevel.WARNING, PostureLevel.DANGER):
                self._events.append(PostureEvent(self._elapsed(), state))
            self._current = state
        self._sample_timeline()

    def _sample_timeline(self, force: bool = False) -> None:
        if not self._running or self._current == PostureLevel.UNKNOWN:
            return
        now = time.monotonic()
        interval = float(config.STATS_SAMPLE_INTERVAL_SEC)
        if not force and (now - self._last_sample_mono) < interval:
            return
        self._last_sample_mono = now
        self._timeline.append(
            TimelineSample(self._elapsed(), self._severity(self._current))
        )

    def _flush_to_unknown(self) -> None:
        self._flush()
        self._current = PostureLevel.UNKNOWN

    def _flush(self) -> None:
        now = time.monotonic()
        elapsed = max(0.0, now - self._last_mono)
        self._last_mono = now
        if self._current in self._seconds:
            self._seconds[self._current] += elapsed

    def seconds(self, level: PostureLevel) -> float:
        return float(self._seconds.get(level, 0.0))

    @property
    def events(self) -> List[PostureEvent]:
        return list(self._events)

    @property
    def timeline(self) -> List[TimelineSample]:
        return list(self._timeline)

    @property
    def total_tracked_seconds(self) -> float:
        return sum(self._seconds.values())

    def bucketed_event_counts(self) -> Tuple[List[float], List[int], List[int]]:
        """Per N-minute bucket: WARNING count, DANGER count (line chart)."""
        bucket_min = max(1, int(config.STATS_BUCKET_MINUTES))
        bucket_sec = bucket_min * 60.0
        if not self._events:
            return [0.0], [0], [0]

        max_elapsed = max(e.elapsed_sec for e in self._events)
        n_buckets = int(max_elapsed // bucket_sec) + 1
        n_buckets = max(n_buckets, 1)
        warn = [0] * n_buckets
        danger = [0] * n_buckets
        labels: List[float] = []

        for i in range(n_buckets):
            labels.append(i * bucket_min)

        for ev in self._events:
            idx = min(int(ev.elapsed_sec // bucket_sec), n_buckets - 1)
            if ev.level == PostureLevel.WARNING:
                warn[idx] += 1
            elif ev.level == PostureLevel.DANGER:
                danger[idx] += 1

        return labels, warn, danger

    def pattern_insight_text(self) -> str:
        """Human-readable posture-collapse pattern summary."""
        total = self.total_tracked_seconds
        warn_s = self.seconds(PostureLevel.WARNING)
        danger_s = self.seconds(PostureLevel.DANGER)
        bad_s = warn_s + danger_s

        if total < 30 and not self._events:
            return "아직 분석할 데이터가 충분하지 않습니다. 모니터링 후 다시 확인해 주세요."

        lines: List[str] = []

        if self._events:
            warn_ev = [e for e in self._events if e.level == PostureLevel.WARNING]
            danger_ev = [e for e in self._events if e.level == PostureLevel.DANGER]
            if len(self._events) >= 2:
                gaps = [
                    self._events[i + 1].elapsed_sec - self._events[i].elapsed_sec
                    for i in range(len(self._events) - 1)
                ]
                avg_min = (sum(gaps) / len(gaps)) / 60.0
                if avg_min >= 1.0:
                    lines.append(
                        f"평균 {avg_min:.0f}분마다 자세가 흐트러지는 패턴이 있습니다."
                    )
                else:
                    lines.append(
                        f"평균 {avg_min * 60:.0f}초마다 자세가 흐트러지는 패턴이 있습니다."
                    )
            lines.append(
                f"경고 {len(warn_ev)}회 · 위험 {len(danger_ev)}회가 기록되었습니다."
            )
        else:
            lines.append("이번 세션에서는 경고·위험 이벤트가 거의 없었습니다. 훌륭해요!")

        if total > 0 and bad_s > 0:
            ratio = 100.0 * bad_s / total
            lines.append(
                f"모니터링 시간 중 약 {ratio:.0f}% 구간에서 자세가 흐트러졌습니다."
            )

        peak_hour = self._peak_bad_hour_label()
        if peak_hour:
            lines.append(peak_hour)

        return "\n".join(lines)

    def _peak_bad_hour_label(self) -> str:
        if not self._events:
            return ""
        buckets: Dict[int, int] = {}
        for ev in self._events:
            minute = int(ev.elapsed_sec // 60)
            buckets[minute] = buckets.get(minute, 0) + 1
        if not buckets:
            return ""
        peak_min = max(buckets, key=buckets.get)
        start = peak_min
        end = peak_min + 1
        return f"특히 시작 후 {start}~{end}분 구간에 자세 붕괴가 집중되었습니다."
