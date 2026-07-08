# 9주차 개념도 생성 (표본추출, 상관과 인과)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401

from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)

rng = np.random.default_rng(9)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 9-1
# 모집단과 표본, 그리고 추론
fig, ax = plt.subplots(figsize=(11, 5.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis("off")

# 모집단 (큰 타원 + 많은 점)
pop = Ellipse((2.9, 3.6), 4.6, 4.6, fc="#f5f9fd", ec="#2f6fb0", lw=1.6)
ax.add_patch(pop)
px = rng.uniform(1.1, 4.7, 90)
py = rng.uniform(1.9, 5.3, 90)
inside = ((px - 2.9) / 2.1) ** 2 + ((py - 3.6) / 2.1) ** 2 < 1
ax.scatter(px[inside], py[inside], s=14, color="#2f6fb0", alpha=0.55, zorder=3)
ax.text(2.9, 6.35, "모집단(population)\n알고 싶은 전체", ha="center", fontsize=12,
        fontweight="bold", color="#2f6fb0")

# 표본 (작은 원 + 적은 점)
sam = Circle((9.3, 3.6), 1.55, fc="#f4fbf6", ec="#2f8f4e", lw=1.6)
ax.add_patch(sam)
sx = rng.uniform(8.1, 10.5, 30)
sy = rng.uniform(2.4, 4.8, 30)
inside_s = (sx - 9.3) ** 2 + (sy - 3.6) ** 2 < 1.3 ** 2
ax.scatter(sx[inside_s], sy[inside_s], s=14, color="#2f8f4e", alpha=0.8, zorder=3)
ax.text(9.3, 5.75, "표본(sample)\n실제로 관찰한 일부", ha="center", fontsize=12,
        fontweight="bold", color="#2f8f4e")

arrow(ax, 5.4, 4.3, 7.6, 4.3, color="#2f8f4e", lw=2)
ax.text(6.5, 4.75, "표본추출\n(무작위로 뽑는다)", ha="center", fontsize=10.5, color="#2f8f4e")
arrow(ax, 7.6, 2.9, 5.4, 2.9, color="#c77b2f", lw=2, ls="--")
ax.text(6.5, 2.0, "추론(inference)\n표본에서 본 것으로 전체를 짐작한다\n짐작에는 늘 불확실성이 따른다",
        ha="center", fontsize=10.5, color="#c77b2f")
fig.savefig(FIG / "fig09_population_sample.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-4
# 상관은 인과가 아니다: 교란요인 삼각형
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis("off")

box(ax, 4.1, 6.1, 3.8, 1.5, "교란요인 Z\n청년층의 유출", fc="#fdf9f4", ec="#c77b2f",
    fontsize=12, weight="bold")
box(ax, 0.7, 1.9, 3.6, 1.5, "X\n고령인구비율 상승", fc="#f5f9fd", ec="#2f6fb0", fontsize=12)
box(ax, 7.7, 1.9, 3.6, 1.5, "Y\n합계출산율의 지역차", fc="#f4fbf6", ec="#2f8f4e", fontsize=12)

arrow(ax, 4.6, 5.9, 2.9, 3.7, color="#c77b2f", lw=2)
arrow(ax, 7.4, 5.9, 9.1, 3.7, color="#c77b2f", lw=2)
ax.text(2.6, 5.0, "젊은 사람이 떠나면\n노인 비중이 커진다", ha="center", fontsize=10, color="#8a5a1e")
ax.text(9.5, 5.0, "떠난 곳과 남은 곳의\n인구 구성이 달라진다", ha="center", fontsize=10, color="#1e6b38")

arrow(ax, 4.5, 2.65, 7.5, 2.65, color="#999", lw=2, ls="--", style="<|-|>")
ax.text(6.0, 3.05, "겉보기 상관 (r = 0.39)", ha="center", fontsize=11, color="#555")
ax.text(6.0, 0.6, "X와 Y가 함께 움직이는 것은 Z가 둘 모두를 움직이기 때문일 수 있다.\n이때 X가 Y의 원인이라고 말하면 틀린다.",
        ha="center", fontsize=11, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig09_confounder.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig09_*.png'))])
