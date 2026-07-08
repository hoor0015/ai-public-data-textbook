# -*- coding: utf-8 -*-
"""개념도 상자(FancyBboxPatch) 안의 글씨를 상자 크기에 맞춰 자동 확대/축소.

사용법: 그림 스크립트에서 `import figfit` 한 줄만 추가하면,
savefig 시점에 각 상자 안 가운데 정렬 텍스트의 크기를
상자를 최대한 채우는 크기로(여백 최소화) 다시 계산한다.
상자 밖 텍스트(캡션, 축, 주석)는 건드리지 않는다.
"""
import matplotlib.figure
from matplotlib.patches import FancyBboxPatch

MIN_PT = 9.0    # 최소 글자 크기 (pt)
MAX_PT = 26.0   # 최대 글자 크기 (pt)
FILL = 0.84     # 상자를 채우는 비율 (모서리 패딩 감안)


def _autofit(fig):
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    except Exception:
        return
    for ax in fig.axes:
        patches = [p for p in ax.patches if isinstance(p, FancyBboxPatch)]
        if not patches:
            continue
        for t in ax.texts:
            if t.get_ha() != "center" or t.get_va() != "center":
                continue
            if not t.get_text().strip():
                continue
            x, y = t.get_position()
            host = None
            for p in patches:
                px, py = p.get_x(), p.get_y()
                pw, ph = p.get_width(), p.get_height()
                if px <= x <= px + pw and py <= y <= py + ph:
                    if host is None or pw * ph < host.get_width() * host.get_height():
                        host = p
            if host is None:
                continue
            x0, y0 = ax.transData.transform((host.get_x(), host.get_y()))
            x1, y1 = ax.transData.transform(
                (host.get_x() + host.get_width(), host.get_y() + host.get_height()))
            bw, bh = abs(x1 - x0), abs(y1 - y0)
            tb = t.get_window_extent(renderer=renderer)
            if tb.width <= 0 or tb.height <= 0 or bw <= 0 or bh <= 0:
                continue
            scale = min(bw * FILL / tb.width, bh * FILL / tb.height)
            t.set_fontsize(max(MIN_PT, min(MAX_PT, t.get_fontsize() * scale)))


_orig_savefig = matplotlib.figure.Figure.savefig


def _savefig(self, *args, **kwargs):
    _autofit(self)
    return _orig_savefig(self, *args, **kwargs)


matplotlib.figure.Figure.savefig = _savefig
