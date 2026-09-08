# -*- coding: utf-8 -*-
# 특강 맥락창 개념도: 머리 그림(figures/head_brain_src.png)의 뇌 구역을 찾아 색과 글씨를 얹는다
# 산출: figS_context_head.png (머리 안에 무엇이 있나)
#       figS_compact_clear.png (compact와 clear의 차이)
#       figS_orchestrator_heads.png (본 에이전트와 서브에이전트)
#       figS_agent_features.png (머리로 보는 에이전트 기능 네 가지)
#       figS_more_features.png (되감기·훅·옆에서 묻기·자동 메모리)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from scipy import ndimage

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (이 그림에는 상자가 없어 사실상 무동작. 집필지침 준수용)

from matplotlib.patches import FancyArrowPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
SRC = FIG / "head_brain_src.png"

# ---------------------------------------------------------------- 원본 그림에서 뇌 구역 찾기
gray = np.array(Image.open(SRC).convert("L"))
H, W = gray.shape
ink = gray <= 128                      # 검은 선
labels, n = ndimage.label(~ink)        # 흰 영역의 연결 성분
objs = ndimage.find_objects(labels)
areas = ndimage.sum(~ink, labels, range(1, n + 1))
lobes = {}
for i, (sz, sl) in enumerate(zip(areas, objs), start=1):
    if sz < 300 or sz > 100000:        # 잡티와 바깥 배경 제외
        continue
    cy, cx = ndimage.center_of_mass(labels == i)
    lobes[i] = (float(cx), float(cy), int(sz))
assert len(lobes) == 7, f"뇌 구역이 7개가 아님: {len(lobes)}"


def pick(pred):
    cands = [k for k, (cx, cy, sz) in lobes.items() if pred(cx, cy, sz)]
    assert len(cands) == 1, cands
    return cands[0]


L_CENTER = pick(lambda cx, cy, sz: sz > 30000)                       # 큰 가운데 타원
L_TOP = pick(lambda cx, cy, sz: cy < 170 and cx > 300)                # 위쪽 띠
L_RIGHT = pick(lambda cx, cy, sz: cx > 500 and cy < 340)              # 오른쪽
L_TOPLEFT = pick(lambda cx, cy, sz: cx < 250 and cy < 210)            # 왼쪽 위(이마)
L_BOTTOM = pick(lambda cx, cy, sz: 300 < cx < 420 and cy > 360)       # 아래 가운데
L_LEFTLOW = pick(lambda cx, cy, sz: cx < 250 and cy > 240)            # 왼쪽 아래(작은 것)
L_BOTRIGHT = pick(lambda cx, cy, sz: cx > 450 and cy > 400)           # 오른쪽 아래(작은 원)

# 글씨 위치 미세 조정 (픽셀). 굽은 구역은 무게중심이 좁은 쪽에 놓이므로 넓은 쪽으로 옮긴다
NUDGE = {L_TOPLEFT: (-8, 14), L_TOP: (-30, 4), L_RIGHT: (6, 8), L_LEFTLOW: (-2, -4),
         L_BOTTOM: (-6, 0), L_BOTRIGHT: (0, 0), L_CENTER: (0, 0)}

# 선 그림을 RGBA로 (검은 선만 불투명)
line_rgba = np.zeros((H, W, 4), dtype=float)
line_rgba[..., 3] = ink.astype(float)

# 교재 팔레트 (연한 채움색)
BLUE, GREEN, ORANGE, PURPLE, INDIGO = "#c9dcf2", "#cfe9d6", "#f6ddc0", "#e2d7ee", "#d9dcf6"
GREY, WHITE = "#e9e9e9", "#ffffff"


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def overlay(colors):
    """{구역 label: hex} -> RGBA 배열"""
    arr = np.zeros((H, W, 4), dtype=float)
    for lab, col in colors.items():
        m = labels == lab
        arr[m, :3] = hex2rgb(col)
        arr[m, 3] = 1.0
    return arr


def draw_head(ax, colors, texts, x0=0, y0=0, scale=1.0, crop=None):
    """ax 데이터 좌표 (x0, y0)에 머리를 scale 배율로 그린다. 좌표계는 픽셀(위가 0).\n    crop: 원본의 이 행 아래(목 부분)는 그리지 않는다."""
    ext = (x0, x0 + W * scale, y0 + H * scale, y0)   # imshow extent: (left, right, bottom, top)
    lines = line_rgba.copy()
    if crop is not None:
        lines[crop:, :, 3] = 0
    ax.imshow(overlay(colors), extent=ext, interpolation="nearest", zorder=1)
    ax.imshow(lines, extent=ext, interpolation="bilinear", zorder=2)
    for lab, (txt, kw) in texts.items():
        cx, cy, _ = lobes[lab]
        dx, dy = NUDGE.get(lab, (0, 0))
        ax.text(x0 + (cx + dx) * scale, y0 + (cy + dy) * scale, txt,
                ha="center", va="center", linespacing=1.15, zorder=3, **kw)


def setup(ax, x_max=W, y_max=H, pad=12):
    ax.set_xlim(-pad, x_max + pad)
    ax.set_ylim(y_max + pad, -pad)
    ax.set_aspect("equal")
    ax.axis("off")


FIXED_COLORS = {L_TOPLEFT: BLUE, L_LEFTLOW: INDIGO, L_BOTRIGHT: INDIGO}

# ---------------------------------------------------------------- 그림 A: 머리 안에 무엇이 있나
fig, ax = plt.subplots(figsize=(8.2, 8.6))
setup(ax, y_max=640)   # 목 아랫부분은 잘라 여백을 줄인다
T = dict(fontsize=12, color="#1f2328")
TB = dict(fontsize=12, color="#1f2328", fontweight="bold")
TS = dict(fontsize=11, color="#1f2328")
colors_full = {**FIXED_COLORS, L_CENTER: ORANGE, L_TOP: GREEN, L_RIGHT: GREEN, L_BOTTOM: PURPLE}
texts_full = {
    L_TOPLEFT: ("CLAUDE.md\n규칙 파일", TB),
    L_LEFTLOW: ("기본\n지침", TS),
    L_BOTRIGHT: ("도구\n목록", TS),
    L_CENTER: ("대화 내용\n지시와 답이\n계속 쌓인다", T),
    L_TOP: ("열어 본 파일", T),
    L_RIGHT: ("실행\n결과", T),
    L_BOTTOM: ("오류와\n재시도", T),
}
draw_head(ax, colors_full, texts_full)
ax.set_title("맥락창은 에이전트의 머리 안이다", fontsize=14, fontweight="bold", pad=10)
ax.text(W / 2 + 20, 615,
        "파랑: 대화를 시작할 때마다 자동으로 들어오는 것\n"
        "주황·초록·보라: 일을 하는 동안 쌓이는 것. 대화가 길수록 늘어난다",
        ha="center", va="center", fontsize=11, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "figS_context_head.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 B: compact vs clear
fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.4))
for ax in axes:
    setup(ax, y_max=640)
T = dict(fontsize=11, color="#1f2328")
TB = dict(fontsize=11, color="#1f2328", fontweight="bold")
TS = dict(fontsize=10, color="#1f2328")
F = dict(fontsize=9.5, color="#8a8a8a")

colors_compact = {**FIXED_COLORS, L_CENTER: ORANGE, L_TOP: GREY, L_RIGHT: GREY, L_BOTTOM: GREY}
texts_compact = {
    L_TOPLEFT: ("CLAUDE.md\n규칙 파일", TB),
    L_LEFTLOW: ("기본\n지침", TS),
    L_BOTRIGHT: ("도구\n목록", TS),
    L_CENTER: ("요약만 남는다\n기준, 파일 경로,\n지금까지의 결론", T),
    L_TOP: ("(요약에 흡수)", F),
    L_RIGHT: ("(요약에\n흡수)", dict(fontsize=9, color="#8a8a8a")),
    L_BOTTOM: ("(버려진다)", F),
}
draw_head(axes[0], colors_compact, texts_compact)
axes[0].set_title("(가) /compact: 요약만 남기고 줄인다", fontsize=13, pad=8)

colors_clear = {**FIXED_COLORS, L_CENTER: WHITE, L_TOP: WHITE, L_RIGHT: WHITE, L_BOTTOM: WHITE}
texts_clear = {
    L_TOPLEFT: ("CLAUDE.md\n규칙 파일", TB),
    L_LEFTLOW: ("기본\n지침", TS),
    L_BOTRIGHT: ("도구\n목록", TS),
    L_CENTER: ("(비어 있음)", F),
    L_TOP: ("(비어 있음)", F),
    L_RIGHT: ("(비어\n있음)", F),
    L_BOTTOM: ("(비어 있음)", F),
}
draw_head(axes[1], colors_clear, texts_clear)
axes[1].set_title("(나) /clear 또는 새 대화: 다 비운다", fontsize=13, pad=8)

fig.text(0.5, 0.06,
         "두 경우 모두 파란 구역(CLAUDE.md, 기본 지침, 도구 목록)은 남는다. 파일에 적힌 규칙은 대화가 지워져도 다시 읽히기 때문이다.",
         ha="center", fontsize=11, color="#333")
fig.savefig(FIG / "figS_compact_clear.png", dpi=150, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------- 그림 C: 오케스트레이터와 서브에이전트
fig, ax = plt.subplots(figsize=(12.5, 8.0))
setup(ax, x_max=1600, y_max=1080, pad=0)
T = dict(fontsize=10.5, color="#1f2328")
TB = dict(fontsize=10.5, color="#1f2328", fontweight="bold")
TS = dict(fontsize=9.5, color="#1f2328")
F = dict(fontsize=9, color="#8a8a8a")

MAIN_Y = 100
colors_main = {**FIXED_COLORS, L_CENTER: ORANGE, L_TOP: GREEN, L_RIGHT: GREEN, L_BOTTOM: WHITE}
texts_main = {
    L_TOPLEFT: ("CLAUDE.md\n규칙 파일", TB),
    L_LEFTLOW: ("기본\n지침", TS),
    L_BOTRIGHT: ("도구\n목록", TS),
    L_CENTER: ("나의 지시와\n전체 계획", T),
    L_TOP: ("팀원 보고 요약", T),
    L_RIGHT: ("팀원\n보고\n요약", T),
    L_BOTTOM: ("(로그는\n안 온다)", F),
}
draw_head(ax, colors_main, texts_main, x0=0, y0=MAIN_Y, scale=1.0)
ax.text(W / 2, MAIN_Y + 760, "본 에이전트 (오케스트레이터)\n일을 나누어 주고 요약만 받는다",
        ha="center", va="top", fontsize=12, fontweight="bold")

s = 0.5
sub_x = 1060
subs = [("정제 담당", "정제 로그\n수백 줄"), ("분석 담당", "코드와\n출력"),
        ("검증 담당 (verifier)", "원자료\n대조 계산")]
ST = dict(fontsize=9, color="#1f2328")
STB = dict(fontsize=7.5, color="#1f2328", fontweight="bold")
ys = [20, 345, 670]
ybs = [250, 330, 410]          # 본 에이전트 쪽 화살표 출발 높이
for (name, log), y, yb in zip(subs, ys, ybs):
    colors_sub = {**FIXED_COLORS, L_CENTER: PURPLE, L_TOP: PURPLE, L_RIGHT: PURPLE, L_BOTTOM: PURPLE}
    texts_sub = {L_TOPLEFT: ("CLAUDE.md", STB), L_CENTER: (log, ST)}
    draw_head(ax, colors_sub, texts_sub, x0=sub_x, y0=y, scale=s, crop=640)
    ax.text(sub_x + W * s + 10, y + 140, name, ha="left", va="center",
            fontsize=11, fontweight="bold")
    ax.add_patch(FancyArrowPatch((612, yb - 14), (sub_x + 12, y + 128), arrowstyle="-|>",
                                 mutation_scale=16, color="#2f6fb0", lw=1.6))
    ax.add_patch(FancyArrowPatch((sub_x + 12, y + 162), (612, yb + 18), arrowstyle="-|>",
                                 mutation_scale=16, color="#c77b2f", lw=1.6, linestyle="--"))
ax.text(780, 120, "작업 지시서\n기준과 파일 경로를 적어 보낸다", ha="center", va="center",
        fontsize=10, color="#2f6fb0",
        bbox=dict(fc="white", ec="#2f6fb0", boxstyle="round,pad=0.4"))
ax.text(760, 720, "요약 보고\n한 장짜리 결과만 돌아온다", ha="center", va="center",
        fontsize=10, color="#c77b2f",
        bbox=dict(fc="white", ec="#c77b2f", boxstyle="round,pad=0.4"))
ax.text(sub_x + W * s / 2 + 90, 1040,
        "서브에이전트: 각자 자기 머리(맥락창)를 따로 가진다.\n"
        "시행착오는 자기 머리 안에 남고, 요약만 본 에이전트로 간다.",
        ha="center", va="center", fontsize=10.5, color="#333")
fig.savefig(FIG / "figS_orchestrator_heads.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 D: 머리로 보는 에이전트 기능 네 가지
fig, axes = plt.subplots(2, 2, figsize=(12.5, 7.6))
for ax in axes.flat:
    setup(ax, x_max=1000, y_max=580, pad=0)
S = 0.42
HW, HH = W * S, 640 * S           # 머리 하나의 폭·높이(목 자름)
CT = dict(fontsize=9, color="#1f2328")
MAIN = {**FIXED_COLORS, L_CENTER: ORANGE, L_TOP: GREEN, L_RIGHT: GREEN, L_BOTTOM: PURPLE}
SUB = {**FIXED_COLORS, L_CENTER: PURPLE, L_TOP: PURPLE, L_RIGHT: PURPLE, L_BOTTOM: PURPLE}


def head(ax, x, y, colors, center_txt, kw=CT):
    draw_head(ax, colors, {L_CENTER: (center_txt, kw)}, x0=x, y0=y, scale=S, crop=640)


def label(ax, x, y, txt, **kw):
    opts = dict(ha="center", va="center", fontsize=10.5, color="#333")
    opts.update(kw)
    ax.text(x, y, txt, **opts)


def arrow2(ax, p, q, color, ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, color=color,
                                 lw=1.5, linestyle=ls, connectionstyle=f"arc3,rad={rad}"))


# (가) 위임: 서브에이전트
ax = axes[0, 0]
head(ax, 40, 70, MAIN, "나의 일")
head(ax, 640, 70, SUB, "맡은 일")
arrow2(ax, (40 + HW - 10, 70 + 120), (640 + 20, 70 + 120), "#2f6fb0")
arrow2(ax, (640 + 20, 70 + 170), (40 + HW - 10, 70 + 170), "#c77b2f", ls="--")
label(ax, 470, 165, "지시서", color="#2f6fb0")
label(ax, 470, 265, "요약 보고", color="#c77b2f")
label(ax, 40 + HW / 2, 70 + HH + 22, "본 에이전트", fontweight="bold")
label(ax, 640 + HW / 2, 70 + HH + 22, "서브에이전트", fontweight="bold")
ax.set_title("(가) 위임: 서브에이전트에게 맡긴다", fontsize=12, pad=6)
label(ax, 500, 440, "새 머리에서 일하고 요약 하나만 돌려준다.\n끝난 뒤 이어서 물으려면 메시지를 보낸다.")

# (나) 갈라내기: 브랜치
ax = axes[0, 1]
head(ax, 40, 70, MAIN, "지금의\n대화")
head(ax, 640, 70, MAIN, "지금의\n대화")
arrow2(ax, (40 + HW - 10, 70 + 140), (640 + 20, 70 + 140), "#7a5fa8")
label(ax, 470, 185, "그대로 복사", color="#7a5fa8")
label(ax, 40 + HW / 2, 70 + HH + 22, "원래 대화", fontweight="bold")
label(ax, 640 + HW / 2, 70 + HH + 22, "갈라낸 대화", fontweight="bold")
ax.set_title("(나) 갈라내기: 대화를 복사해 두 갈래로", fontsize=12, pad=6)
label(ax, 500, 440, "같은 내용으로 시작하는 머리가 하나 더 생긴다.\n한쪽에서 시험해 보고 다른 쪽은 그대로 둔다.")

# (다) 팀: 서로 메시지를 주고받는다
ax = axes[1, 0]
TY, AY, BY = 80, 0, 315
head(ax, 20, TY, MAIN, "팀장")
head(ax, 600, AY, SUB, "팀원 A")
head(ax, 600, BY, SUB, "팀원 B")
G = "#2f8f4e"
arrow2(ax, (20 + HW - 10, TY + 110), (600 + 20, AY + 130), G)      # 팀장 -> A
arrow2(ax, (600 + 20, AY + 165), (20 + HW - 10, TY + 145), G)      # A -> 팀장
arrow2(ax, (20 + HW - 10, TY + 190), (600 + 20, BY + 130), G)      # 팀장 -> B
arrow2(ax, (600 + 20, BY + 165), (20 + HW - 10, TY + 225), G)      # B -> 팀장
arrow2(ax, (600 + 140, AY + HH + 4), (600 + 140, BY + 24), G)      # A -> B
arrow2(ax, (600 + 175, BY + 24), (600 + 175, AY + HH + 4), G)      # B -> A
label(ax, 430, 150, "메시지", color=G)
label(ax, 430, 400, "메시지", color=G)
label(ax, 20 + HW / 2, TY + HH + 22, "팀장", fontweight="bold")
label(ax, 600 + HW + 12, AY + 140, "팀원 A", fontweight="bold", ha="left")
label(ax, 600 + HW + 12, BY + 140, "팀원 B", fontweight="bold", ha="left")
ax.set_title("(다) 팀: 머리 여러 개가 메시지를 주고받는다", fontsize=12, pad=6)
label(ax, 250, 500, "받은 메시지는 받는 쪽 머리에 들어간다.\n할 일 목록을 함께 보며 스스로 조율한다.\n(실험 기능. 설정으로 켜야 쓸 수 있다)", fontsize=10)

# (라) 다시 열기: 보관된 대화를 되살린다
ax = axes[1, 1]
ax.text(190, 210, "보관된 대화들\n\n어제의 정제 작업\n오늘 오전의 설치 작업\n방금 /clear로 닫은 대화",
        ha="center", va="center", fontsize=10, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#5b6ee1", boxstyle="round,pad=0.8"))
head(ax, 600, 70, MAIN, "되살린\n대화")
arrow2(ax, (335, 210), (600 + 20, 70 + 150), "#5b6ee1")
label(ax, 470, 160, "다시 열기", color="#5b6ee1")
label(ax, 600 + HW / 2, 70 + HH + 22, "되살린 대화", fontweight="bold")
ax.set_title("(라) 다시 열기: 닫은 대화를 그 머리째 되살린다", fontsize=12, pad=6)
label(ax, 500, 440, "/clear나 새 대화로 비운 대화는 지워지지 않고 보관된다.\n대화 기록에서 고르면 그때의 머리로 돌아간다.")

fig.subplots_adjust(hspace=0.15, wspace=0.05)
fig.savefig(FIG / "figS_agent_features.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 E: 머리로 보는 확장 기능 네 가지 더
fig, axes = plt.subplots(2, 2, figsize=(12.5, 7.6))
for ax in axes.flat:
    setup(ax, x_max=1000, y_max=580, pad=0)


def docbox(ax, x, y, txt, ec="#57606a", fc="white", fs=10):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, color="#1f2328",
            bbox=dict(fc=fc, ec=ec, boxstyle="round,pad=0.6", lw=1.4))


# (가) 되감기: 대화와 파일을 따로 되돌린다
ax = axes[0, 0]
head(ax, 40, 30, MAIN, "지금의\n대화")
docbox(ax, 640, 140, "파일\n(에이전트가 고친 것)", ec="#2f8f4e", fc="#f4fbf6")
# 시점 표시줄
ax.plot([120, 900], [370, 370], color="#8a8a8a", lw=1.5)
for i, x in enumerate([150, 330, 510, 690]):
    ax.plot(x, 370, "o", color="#8a8a8a", ms=6)
    ax.text(x, 398, f"지시 {i + 1}", ha="center", va="center", fontsize=9, color="#555")
ax.plot(870, 370, "o", color="#a33", ms=7)
ax.text(870, 398, "지금", ha="center", va="center", fontsize=9, color="#a33")
arrow2(ax, (860, 335), (345, 335), "#a33", ls="--")
ax.text(600, 310, "이 시점으로 되돌린다", ha="center", va="center", fontsize=10, color="#a33")
ax.set_title("(가) 되감기: 대화와 파일을 따로 되돌린다", fontsize=12, pad=6)
label(ax, 500, 490, "메시지 위의 되감기 단추에서 고른다.\n① 대화만 갈라내기 (파일은 그대로)  ② 파일만 되돌리기 (대화는 그대로)\n③ 둘 다. 명령으로 바꾼 파일은 되돌리지 못한다.", fontsize=10)

# (나) 훅: 머리 밖의 문지기
ax = axes[0, 1]
head(ax, 40, 60, MAIN, "파일을\n고치자")
docbox(ax, 500, 190, "문지기 (훅)\n정해 둔 순간에\n자동으로 실행", ec="#c77b2f", fc="#fdf9f4")
docbox(ax, 840, 190, "파일 수정", ec="#2f8f4e", fc="#f4fbf6")
arrow2(ax, (40 + HW - 10, 190), (400, 190), "#2f6fb0")
arrow2(ax, (600, 190), (770, 190), "#2f6fb0")
ax.text(690, 150, "통과", ha="center", va="center", fontsize=9.5, color="#2f8f4e")
arrow2(ax, (500, 245), (500, 330), "#a33")
ax.text(500, 360, "규칙에 어긋나면 막거나 알린다", ha="center", va="center", fontsize=9.5, color="#a33")
ax.set_title("(나) 훅: 머리 밖의 문지기", fontsize=12, pad=6)
label(ax, 500, 470, "에이전트의 판단을 거치지 않고 설정대로 움직인다.\n\"data 폴더의 파일은 고칠 수 없다\"처럼 규칙을 강제할 때 쓴다.", fontsize=10)

# (다) 옆에서 묻기: /btw
ax = axes[1, 0]
head(ax, 40, 60, MAIN, "지금의\n대화")
docbox(ax, 640, 160, "옆 질문 (/btw)\n\"지금까지 뭘 했지?\"\n\"이 오류가 무슨 뜻이지?\"", ec="#7a5fa8", fc="#faf8fc")
arrow2(ax, (320, 150), (480, 150), "#7a5fa8", ls="--")
ax.text(400, 118, "대화를 본다", ha="center", va="center", fontsize=9.5, color="#7a5fa8")
arrow2(ax, (480, 235), (320, 235), "#a33", ls="--")
ax.text(400, 235, "X", ha="center", va="center", fontsize=13, color="#a33", fontweight="bold",
        bbox=dict(fc="white", ec="none", pad=1))
ax.text(400, 272, "대화에 남지 않는다", ha="center", va="center", fontsize=9.5, color="#a33")
ax.set_title("(다) 옆에서 묻기: 머리에 넣지 않고 묻는다", fontsize=12, pad=6)
label(ax, 500, 470, "답은 옆 창에 뜨고 맥락창을 차지하지 않는다.\n파일 읽기나 명령 실행은 못 한다. 궁금한 것만 묻는 용도다.", fontsize=10)

# (라) 머리 밖의 기록 두 가지: CLAUDE.md와 자동 메모리
ax = axes[1, 1]
head(ax, 600, 60, MAIN, "새 대화")
docbox(ax, 200, 110, "CLAUDE.md\n내가 쓰는 규칙", ec="#2f6fb0", fc="#f5f9fd")
docbox(ax, 200, 290, "자동 메모리\n에이전트가 스스로\n적는 수첩", ec="#5b6ee1", fc="#f7f7fc")
arrow2(ax, (330, 110), (600 + 30, 150), "#2f6fb0")
arrow2(ax, (330, 290), (600 + 30, 200), "#5b6ee1")
ax.text(470, 105, "시작할 때 읽힌다", ha="center", va="center", fontsize=9.5, color="#2f6fb0")
ax.set_title("(라) 머리 밖의 기록 두 가지", fontsize=12, pad=6)
label(ax, 500, 470, "규칙은 내가 CLAUDE.md에 쓰고, 에이전트는 배운 것을 자동 메모리에 적는다.\n둘 다 대화가 지워져도 남으며 /memory에서 볼 수 있다.", fontsize=10)

fig.subplots_adjust(hspace=0.15, wspace=0.05)
fig.savefig(FIG / "figS_more_features.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved 5 figures in", FIG)
