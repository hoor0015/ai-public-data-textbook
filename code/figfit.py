# -*- coding: utf-8 -*-
"""개념도 도형(상자·원·타원·다이아몬드·다각형) 안의 글씨를 도형 크기에 맞춰 자동 확대/축소.

사용법: 그림 스크립트에서 `import figfit` 한 줄만 추가하면, savefig 시점에
각 도형 안 가운데 정렬 텍스트의 크기를 도형을 채우는 크기로 다시 계산한다.

v2 (2026-07-23):
- 지원 도형 확장: FancyBboxPatch·Rectangle(1.0), Ellipse·Circle(0.707),
  RegularPolygon·Polygon(꼭짓점 6 미만 0.5, 이상 0.7) — 괄호는 외접 bbox 대비 내접 사각형 비율.
- 크기 조화: 도형별 피팅 크기를 도형 텍스트 중앙값 × SPREAD로 캡하고, 도형 밖 텍스트가
  있으면 그 중앙값 × OUT_CAP으로도 캡하여 그림 전체 글씨 크기를 비슷하게 유지한다.
  (키우는 쪽 조화는 도형 넘침을 만들므로 캡은 축소 방향으로만 적용)
- 도형 밖 텍스트(캡션·축·화살표 라벨·데이터 수치)는 건드리지 않는다.

조정 변수(모듈 속성으로 덮어쓰기 가능):
  MIN_PT/MAX_PT 글자 크기 범위, FILL 도형 채움 비율,
  SPREAD 도형 간 상한 배수, OUT_CAP 도형 밖 중앙값 대비 상한 배수.
"""
import matplotlib.figure
from matplotlib.patches import (FancyBboxPatch, Rectangle, Ellipse,
                                RegularPolygon, Polygon)

MIN_PT = 9.0     # 최소 글자 크기 (pt)
MAX_PT = 26.0    # 최대 글자 크기 (pt)
FILL = 0.84      # 도형 가용 영역을 채우는 비율 (모서리 패딩 감안)
SPREAD = 1.15    # 도형 텍스트 크기 상한: 도형 텍스트 중앙값 × SPREAD
OUT_CAP = 1.6    # 도형 텍스트 크기 상한: 도형 밖 텍스트 중앙값 × OUT_CAP


def _shape_factor(p):
    """도형 외접 bbox 대비 텍스트 가용 내접 사각형 비율. 미지원 도형은 None."""
    if isinstance(p, (FancyBboxPatch, Rectangle)):
        return 1.0
    if isinstance(p, Ellipse):          # Circle 포함
        return 0.707
    if isinstance(p, RegularPolygon):
        return 0.5 if getattr(p, 'numvertices', 4) < 6 else 0.7
    if isinstance(p, Polygon):
        return 0.5 if len(p.get_xy()) <= 5 else 0.7
    return None


def _median(vals):
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def _autofit(fig):
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    except Exception:
        return
    for ax in fig.axes:
        shapes = [(p, _shape_factor(p)) for p in ax.patches]
        shapes = [(p, f) for p, f in shapes if f is not None]
        if not shapes:
            continue
        jobs, outside = [], []
        for t in ax.texts:
            if not t.get_text().strip():
                continue
            if t.get_ha() != "center" or t.get_va() != "center":
                outside.append(t.get_fontsize())
                continue
            disp = ax.transData.transform(t.get_position())
            host_bb, host_f, host_area = None, 1.0, None
            for p, f in shapes:
                try:
                    if not p.contains_point(disp):
                        continue
                    bb = p.get_window_extent(renderer)
                except Exception:
                    continue
                area = bb.width * bb.height
                if area <= 0:
                    continue
                if host_area is None or area < host_area:
                    host_bb, host_f, host_area = bb, f, area
            if host_bb is None:
                outside.append(t.get_fontsize())
                continue
            tb = t.get_window_extent(renderer=renderer)
            if tb.width <= 0 or tb.height <= 0:
                continue
            scale = min(host_bb.width * host_f * FILL / tb.width,
                        host_bb.height * host_f * FILL / tb.height)
            fit = max(MIN_PT, min(MAX_PT, t.get_fontsize() * scale))
            jobs.append((t, fit))
        if not jobs:
            continue
        cap = _median([f for _, f in jobs]) * SPREAD
        if outside:
            cap = min(cap, _median(outside) * OUT_CAP)
        for t, fit in jobs:
            t.set_fontsize(max(MIN_PT, min(fit, cap)))


_orig_savefig = matplotlib.figure.Figure.savefig


def _savefig(self, *args, **kwargs):
    _autofit(self)
    return _orig_savefig(self, *args, **kwargs)


matplotlib.figure.Figure.savefig = _savefig
