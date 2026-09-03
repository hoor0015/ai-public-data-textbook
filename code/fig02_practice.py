# -*- coding: utf-8 -*-
# 2주차 2회차 실습 장 그림. 2.2절 실험 C(손잡이를 하나씩 붙이기)의 개념도.
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

figfit.SPREAD = 1.0  # 한 줄짜리 상자의 글씨만 커지지 않도록 크기 차이를 좁힌다

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                fc=fc, ec=ec, lw=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)


def arrow(ax, x1, y1, x2, y2, color="#777", lw=1.3):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, color=color, lw=lw))


# 아래에서 위로 쌓이는 여섯 단계 (0단계가 맨 아래)
rows = [
    ("0단계\n손잡이 없음", "숫자 하나\n\"평균은 0.823입니다\""),
    ("1단계\n근거의 위치", "파일 이름과\n열 이름"),
    ("2단계\n자료에서 직접 계산", "도구 호출 줄과\n계산에 쓴 명령"),
    ("3단계\n없다고 답할 자리", "없는 것은\n없다는 답"),
    ("4단계\n성공 기준", "몇 곳으로 계산했는지\n(228곳)"),
    ("5단계\n이상 상황 보고", "군위군 결측을\n계산보다 먼저 보고"),
]

fig, ax = plt.subplots(figsize=(9.4, 6.4))
ax.set_xlim(0, 10)
ax.set_ylim(-0.1, 7.4)
ax.axis("off")

x_left, w_left = 1.05, 3.0
x_right, w_right = 5.3, 4.0
h = 0.82

for i, (handle, gain) in enumerate(rows):
    y = 0.55 + i * 1.07
    box(ax, x_left, y, w_left, h, handle, fc="#f4fbf6", ec="#2f8f4e")
    box(ax, x_right, y, w_right, h, gain, fc="#f5f9fd", ec="#2f6fb0")
    arrow(ax, x_left + w_left + 0.06, y + h / 2, x_right - 0.06, y + h / 2)

# 왼쪽: 손잡이가 쌓인다
arrow(ax, 0.62, 0.62, 0.62, 6.68, color="#2f8f4e", lw=2.0)
ax.text(x_left + w_left / 2, 0.16, "위로 갈수록 손잡이가 하나씩 쌓인다",
        ha="center", va="center", fontsize=10.5, color="#2f8f4e")

# 오른쪽: 확인 경로가 늘어난다
arrow(ax, 9.72, 0.62, 9.72, 6.68, color="#2f6fb0", lw=2.0)
ax.text(x_right + w_right / 2, 0.16, "위로 갈수록 확인할 수 있는 것이 늘어난다",
        ha="center", va="center", fontsize=10.5, color="#2f6fb0")

ax.text(x_left + w_left / 2, 7.05, "지시문에 더한 한 줄", ha="center",
        va="center", fontsize=12, fontweight="bold")
ax.text(x_right + w_right / 2, 7.05, "답에 새로 생기는 것", ha="center",
        va="center", fontsize=12, fontweight="bold")

fig.tight_layout()
fig.savefig(FIG / "fig02_handles_ladder.png", dpi=150, bbox_inches="tight")
print("저장:", FIG / "fig02_handles_ladder.png")
