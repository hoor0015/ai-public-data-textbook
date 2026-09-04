# 6주차 2회차(실습) 그림 생성: 그림 6-5 kosis-collect 스킬의 절차와 검증 손잡이
# 개념도이므로 데이터 없이 도형으로 그린다. 상자 글씨는 figfit이 자동으로 맞춘다.
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

# 상자 글씨 크기가 서로 비슷해지도록 여섯 단계의 문구 길이를 비슷하게 맞춰 두었다.

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=15, color=color, lw=lw, linestyle=ls))


fig, ax = plt.subplots(figsize=(11.5, 7.6))
ax.set_xlim(0, 14)
ax.set_ylim(0, 11.2)
ax.axis("off")

BX, BW, BH = 1.0, 5.2, 0.92
PITCH = 1.32

# 스킬을 부르며 조건을 문장으로 일러 주는 한 줄
box(ax, BX, 9.72, BW, 1.02,
    "/kosis-collect + 통계표 DT_1B040A3, 2019-2023년, 전국",
    fc="#f4fbf6", ec="#2f8f4e", weight="bold")
ax.text(BX + BW + 0.35, 10.23, "바뀌는 조건은 말로 일러 준다",
        ha="left", va="center", fontsize=10.5, color="#2f8f4e")

steps = [
    "1. 구조 확인: 항목 · 분류 · 수록 기간 · 단위",
    "2. 건수 기준 세우기: 몇 건이 와야 하는가",
    "3. 조회: 항목 하나, 지역 수준, 시작과 끝 시점",
    "4. 건수 확인: 받은 건수를 기준과 비교한다",
    "5. 저장: CSV (숫자는 숫자로, utf-8-sig)",
    "6. 수집기록: 조건 · 출처 · 검증 칸을 양식대로",
]
ys = [9.72 - PITCH * (i + 1) for i in range(len(steps))]
for i, (t, y) in enumerate(zip(steps, ys)):
    box(ax, BX, y, BW, BH, t, fontsize=10)
    y_from = 9.72 if i == 0 else ys[i - 1]
    arrow(ax, BX + BW / 2, y_from, BX + BW / 2, y + BH)

# 절차 묶음 표시
ax.plot([BX - 0.28, BX - 0.28], [ys[-1], ys[0] + BH], color="#2f6fb0", lw=1.4)
ax.text(BX - 0.5, (ys[-1] + ys[0] + BH) / 2, "SKILL.md의 절차",
        ha="center", va="center", rotation=90, fontsize=10.5, color="#2f6fb0")

# 검증 손잡이 주석 (절차 2 · 4 · 6에 붙는다)
notes = [
    (1, "조회 전에 적어 두는 성공 기준\n(전국 1개 지역 x 5개 연도 = 5건)"),
    (3, "기준과 다르면 값을 보여 주기 전에\n원인부터 보고하고 멈춘다"),
    (5, "검증 내용 칸은 비워 둔다.\n채우는 것은 사람의 일이다"),
]
for idx, note in notes:
    y = ys[idx] + BH / 2
    ax.text(7.35, y, note, ha="left", va="center", fontsize=10, color="#8a5a1f",
            bbox=dict(fc="#fdf9f4", ec="#c77b2f", boxstyle="round,pad=0.42"))
    arrow(ax, BX + BW + 0.05, y, 7.25, y, color="#c77b2f", ls="--", lw=1.2)

ax.text(7.0, 0.55,
        "바뀌는 것(통계표 ID, 기간, 지역 수준)은 부를 때 말로 일러 주고,\n"
        "바뀌지 않는 것(건수 기준, 건수 확인, 기록)은 절차에 고정한다.",
        ha="center", va="center", fontsize=10.5, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))

fig.savefig(FIG / "fig06_skill.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig06_skill.png")
