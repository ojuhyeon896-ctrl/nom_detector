"""Posture statistics — time-series and pattern analysis."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from nom_detector_app import config
from nom_detector_app.stats.matplotlib_font import configure_matplotlib_korean_font
from nom_detector_app.stats.tracker import SessionStatsTracker
from nom_detector_app.ui.widgets.background_screen import BackgroundScreen

configure_matplotlib_korean_font()

# Figure margins tuned for Korean titles / Y-axis labels (Windows Malgun Gothic).
_LAYOUT_SINGLE = dict(left=0.14, right=0.96, top=0.90, bottom=0.14)
_LAYOUT_DUAL = dict(left=0.16, right=0.97, top=0.96, bottom=0.10, hspace=0.62)


class StatisticsScreen(BackgroundScreen):
    def __init__(self, stats: SessionStatsTracker, parent=None) -> None:
        super().__init__(config.BG_SUB, parent)
        self.stats = stats

        title = QLabel("내 거북목 통계")
        title.setObjectName("ScreenTitle")

        hint = QLabel(
            "시간이 지날수록 자세가 어떻게 흐트러졌는지, "
            f"구간별({config.STATS_BUCKET_MINUTES}분) 경고·위험 발생 횟수를 분석합니다."
        )
        hint.setObjectName("ManualCaption")
        hint.setWordWrap(True)

        self._figure = Figure(figsize=(7.4, 8.2), facecolor="none", dpi=96)
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setMinimumHeight(520)
        self._canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.lbl_insight = QLabel()
        self.lbl_insight.setObjectName("StatsInsight")
        self.lbl_insight.setWordWrap(True)
        self.lbl_insight.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.btn_back = QPushButton("메인으로")
        self.btn_back.setMinimumHeight(48)
        self.btn_back.setCursor(Qt.PointingHandCursor)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(10)
        root.addWidget(title)
        root.addWidget(hint)
        root.addWidget(self._canvas, 1)
        root.addWidget(self.lbl_insight)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.btn_back)
        root.addLayout(row)

    @staticmethod
    def _style_axis(ax, *, title: str, xlabel: str | None = None, ylabel: str | None = None) -> None:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=16)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=11, labelpad=10)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=11, labelpad=12)
        ax.tick_params(axis="both", labelsize=10, pad=6)
        ax.grid(True, alpha=0.25, linestyle="--")

    def _apply_layout(self, dual: bool) -> None:
        params = _LAYOUT_DUAL if dual else _LAYOUT_SINGLE
        self._figure.subplots_adjust(**params)

    def refresh_chart(self) -> None:
        configure_matplotlib_korean_font()
        self._figure.clear()

        bucket_min = int(config.STATS_BUCKET_MINUTES)
        x_labels, warn_counts, danger_counts = self.stats.bucketed_event_counts()
        timeline = self.stats.timeline
        dual = bool(timeline and self.stats.events)

        if not timeline and not self.stats.events:
            ax = self._figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "아직 기록된 데이터가 없습니다.\n모니터링을 시작한 뒤 다시 확인해 주세요.",
                ha="center",
                va="center",
                fontsize=13,
                color="#546e7a",
            )
            ax.axis("off")
            self.lbl_insight.setText(self.stats.pattern_insight_text())
            self._apply_layout(dual=False)
            self._canvas.draw_idle()
            return

        ax_ts = None
        ax_bar = None

        if timeline:
            gs = self._figure.add_gridspec(2, 1, height_ratios=[1.08, 1.0])
            ax_ts = self._figure.add_subplot(gs[0])
            ax_bar = self._figure.add_subplot(gs[1])
        else:
            ax_bar = self._figure.add_subplot(111)

        if ax_ts is not None and timeline:
            minutes = [s.elapsed_sec / 60.0 for s in timeline]
            severity = [s.severity for s in timeline]
            ax_ts.fill_between(minutes, severity, step="post", alpha=0.22, color="#ef5350")
            ax_ts.step(
                minutes,
                severity,
                where="post",
                color="#c62828",
                linewidth=2.0,
                label="자세 붕괴 강도",
            )
            ax_ts.set_ylim(-0.12, 2.45)
            ax_ts.set_yticks([0, 1, 2])
            ax_ts.set_yticklabels(["정상", "경고", "위험"])
            self._style_axis(
                ax_ts,
                title="시간 경과에 따른 자세 상태 (시계열)",
                xlabel="경과 시간 (분)",
            )
            ax_ts.legend(loc="upper right", fontsize=10, framealpha=0.9, borderpad=0.6)

        if self.stats.events and ax_bar is not None:
            ax_bar.plot(
                x_labels,
                warn_counts,
                marker="o",
                markersize=7,
                linewidth=2.2,
                color="#fb8c00",
                label="경고 (WARNING)",
            )
            ax_bar.plot(
                x_labels,
                danger_counts,
                marker="s",
                markersize=7,
                linewidth=2.2,
                color="#e53935",
                label="위험 (DANGER)",
            )
            self._style_axis(
                ax_bar,
                title="구간별 경고·위험 발생 횟수",
                xlabel=f"구간 시작 (분, {bucket_min}분 단위)",
                ylabel="발생 횟수",
            )
            ax_bar.legend(loc="upper right", fontsize=10, framealpha=0.9, borderpad=0.6)
            ax_bar.set_xticks(x_labels)
            ymax = max(max(warn_counts), max(danger_counts), 1)
            ax_bar.set_ylim(0, ymax + 0.6)
        elif ax_bar is not None:
            ax_bar.text(
                0.5,
                0.5,
                "경고·위험 이벤트가 없어\n구간별 꺾은선 그래프를 표시할 수 없습니다.",
                ha="center",
                va="center",
                fontsize=12,
                color="#78909c",
            )
            ax_bar.axis("off")

        self.lbl_insight.setText(self.stats.pattern_insight_text())
        self._apply_layout(dual=dual or (ax_ts is not None and ax_bar is not None))
        self._canvas.draw_idle()
