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

v3 (2026-09-05): 진단 추가. figfit이 조용히 아무 일도 하지 않는 두 상황을 스스로 알린다.
  두 상황 모두 실제로 겪었고, 그림을 눈으로 보기 전에는 알아채기 어려웠다.
  (1) 도형 안 글씨의 `va`가 'center'가 아니어서 전부 지나친 경우.
      `ax.text(cx, cy, "제목", ha="center")`처럼 `va`를 빠뜨리면 기본값이 'baseline'이라
      figfit이 손대지 못한다. 상자마다 제목 줄과 설명 줄을 따로 그릴 때 흔히 생긴다.
      → 상자 라벨은 상자당 하나의 글씨로 합치고 `va="center"`를 준다.
  (2) 도형이 글씨에 비해 지나치게 커서, 조화 상한에 걸린 글씨가 도형을 채우지 못하는 경우.
      figfit은 도형을 채우도록 키우지만 상한을 넘겨 키우지는 않으므로, 도형이 크면 빈 채로 남는다.
      → 도형 높이를 글씨에 맞게 줄이거나, 도형 밖 작은 글씨를 키워 상한을 올린다.

조정 변수(모듈 속성으로 덮어쓰기 가능):
  MIN_PT/MAX_PT 글자 크기 범위, FILL 도형 채움 비율,
  SPREAD 도형 간 상한 배수, OUT_CAP 도형 밖 중앙값 대비 상한 배수,
  WARN 진단 경고 출력 여부, REPORT 그림마다 적용 결과 요약 출력 여부.
  환경변수 FIGFIT_QUIET=1 로 경고를 끄고, FIGFIT_REPORT=1 로 요약을 켠다.
"""
import os
import sys

import matplotlib.figure
from matplotlib.patches import (FancyBboxPatch, Rectangle, Ellipse,
                                RegularPolygon, Polygon)

MIN_PT = 9.0     # 최소 글자 크기 (pt)
MAX_PT = 26.0    # 최대 글자 크기 (pt)
FILL = 0.84      # 도형 가용 영역을 채우는 비율 (모서리 패딩 감안)
SPREAD = 1.15    # 도형 텍스트 크기 상한: 도형 텍스트 중앙값 × SPREAD
OUT_CAP = 1.6    # 도형 텍스트 크기 상한: 도형 밖 텍스트 중앙값 × OUT_CAP

WARN = os.environ.get("FIGFIT_QUIET", "") not in ("1", "true", "True")
REPORT = os.environ.get("FIGFIT_REPORT", "") in ("1", "true", "True")
# "도형이 글씨보다 크다"는 판정. 세로가 많이 비었더라도 가로가 거의 찼다면
# 글씨는 그 도형에서 최대로 커진 것이므로 알리지 않는다(여백이 의도로 읽힌다).
# 가로도 헐겁고 세로도 많이 빈 도형이 절반 이상일 때만 알린다.
LOOSE_H = 0.30        # 세로 채움이 이 값 미만이고
LOOSE_W = 0.55        # 가로 채움도 이 값 미만이면 헐겁다고 본다
LOOSE_SHARE = 0.5     # 그런 도형이 이 비율 이상이면 알린다


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


def _short(text, n=30):
    t = " / ".join(text.split("\n"))
    return t if len(t) <= n else t[:n - 1] + "…"


def _autofit(fig):
    """도형 안 글씨 크기를 맞추고, 진단에 쓸 통계를 돌려준다."""
    stat = {"fitted": 0, "skipped": [], "loose": 0, "sizes": [], "fills": []}
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    except Exception:
        return stat
    for ax in fig.axes:
        shapes = [(p, _shape_factor(p)) for p in ax.patches]
        shapes = [(p, f) for p, f in shapes if f is not None]
        if not shapes:
            continue

        # 막대그래프·히스토그램의 막대는 개념도 도형이 아니다. 진단에서만 제외한다
        # (막대 안에 찍힌 값 라벨을 "상자 라벨"로 오해해 경고하지 않도록).
        bar_ids = set()
        for c in getattr(ax, "containers", []):
            for p in getattr(c, "patches", []) or []:
                bar_ids.add(id(p))

        def _host(t):
            """글씨의 위치를 품는 가장 작은 도형의 bbox와 내접 비율, 그리고 그 도형."""
            disp = ax.transData.transform(t.get_position())
            bb_best, f_best, area_best, p_best = None, 1.0, None, None
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
                if area_best is None or area < area_best:
                    bb_best, f_best, area_best, p_best = bb, f, area, p
            return bb_best, f_best, p_best

        jobs, outside = [], []
        for t in ax.texts:
            if not t.get_text().strip():
                continue
            if t.get_ha() != "center" or t.get_va() != "center":
                outside.append(t.get_fontsize())
                # 크기 조화용 계산은 그대로 두고, 진단용으로만 도형 안인지 본다.
                try:
                    bb_d, _, p_d = _host(t)
                    if bb_d is not None and id(p_d) not in bar_ids:
                        stat["skipped"].append(t.get_text())
                except Exception:
                    pass
                continue
            host_bb, host_f, host_p = _host(t)
            if host_bb is None:
                outside.append(t.get_fontsize())
                continue
            tb = t.get_window_extent(renderer=renderer)
            if tb.width <= 0 or tb.height <= 0:
                continue
            scale = min(host_bb.width * host_f * FILL / tb.width,
                        host_bb.height * host_f * FILL / tb.height)
            fit = max(MIN_PT, min(MAX_PT, t.get_fontsize() * scale))
            jobs.append((t, fit, host_bb, host_f, tb, t.get_fontsize(), host_p))
        if not jobs:
            continue
        cap = _median([j[1] for j in jobs]) * SPREAD
        if outside:
            cap = min(cap, _median(outside) * OUT_CAP)
        for t, fit, host_bb, host_f, tb, base, host_p in jobs:
            final = max(MIN_PT, min(fit, cap))
            t.set_fontsize(final)
            stat["fitted"] += 1
            stat["sizes"].append(final)
            if id(host_p) in bar_ids:
                continue
            # 최종 크기에서의 채움 비율(근사): 글씨 bbox는 크기에 비례해 늘어나고,
            # 쓸 수 있는 자리는 도형 bbox의 host_f배다(원·다각형은 1보다 작다).
            k = final / base if base else 1.0
            aw, ah = host_bb.width * host_f, host_bb.height * host_f
            if aw > 0 and ah > 0:
                fw, fh = tb.width * k / aw, tb.height * k / ah
                stat["fills"].append(min(fw, fh))
                if fh < LOOSE_H and fw < LOOSE_W:
                    stat["loose"] += 1
    return stat


def _diagnose(stat, fname):
    """조용히 아무 일도 하지 않은 경우를 알린다. 그림 생성은 절대 방해하지 않는다."""
    try:
        name = os.path.basename(str(fname)) if fname else "(그림)"
        if stat["fitted"] == 0:
            if stat["skipped"] and WARN:
                sample = ", ".join('"%s"' % _short(s) for s in stat["skipped"][:3])
                print("[figfit] %s: 도형 안 글씨 %d개가 크기 조정에서 빠졌습니다. "
                      "ha/va가 모두 'center'여야 합니다 (va 기본값은 'baseline'). "
                      "상자 라벨이라면 상자마다 하나의 글씨로 합치세요. 예: %s"
                      % (name, len(stat["skipped"]), sample), file=sys.stderr)
            return
        if (WARN and stat["loose"] >= 2
                and stat["loose"] >= stat["fitted"] * LOOSE_SHARE):
            print("[figfit] %s: 도형 %d개(전체 %d개)가 글씨에 비해 큽니다. "
                  "가로·세로 어느 쪽도 차지 않아 도형이 비어 보입니다. "
                  "도형 높이를 줄이거나 도형 밖 작은 글씨를 키우세요."
                  % (name, stat["loose"], stat["fitted"]), file=sys.stderr)
        if REPORT:
            lo, hi = min(stat["sizes"]), max(stat["sizes"])
            fill = min(stat["fills"]) if stat["fills"] else float("nan")
            print("[figfit] %s: 맞춘 글씨 %d개 %.1f-%.1fpt, 최소 채움 %.0f%%, "
                  "헐거운 도형 %d개, 지나친 도형 안 글씨 %d개"
                  % (name, stat["fitted"], lo, hi, fill * 100,
                     stat["loose"], len(stat["skipped"])), file=sys.stderr)
    except Exception:
        pass


_orig_savefig = matplotlib.figure.Figure.savefig


def _savefig(self, *args, **kwargs):
    stat = _autofit(self)
    _diagnose(stat, args[0] if args else kwargs.get("fname"))
    return _orig_savefig(self, *args, **kwargs)


matplotlib.figure.Figure.savefig = _savefig
