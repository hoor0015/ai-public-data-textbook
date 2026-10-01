# 2주차 실습 2.8절 흐름도(그림 2-14) 개정본.
# 원본은 code/fig02_instruction.py의 마지막 블록이며, 왼쪽 상자의 이름만 바꾼다.
# 2.4가 "나쁜 지시 vs 좋은 지시 비교"에서 "다섯 요소로 지시문 짓기"로 바뀌면서
# "실험 B의 표"라는 이름이 없어졌기 때문이다.
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "code"))
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


fig, ax = plt.subplots(figsize=(12.5, 5.4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
box(ax, 0.4, 3.6, 2.8, 2.2, "2.4의 표\n상위·하위 5개\n시군구", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 4.2, 6.0, 3.4, 2.0, "1단계 검증 지시\n(같은 대화에서 이어서)", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
box(ax, 4.2, 1.4, 3.4, 2.0, "2단계 독립 검산\n(새 대화: 원본 + 표만)", fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
box(ax, 8.4, 6.0, 2.6, 2.0, "검증 보고 1\n값·재계산값\n행 번호·일치", fc="white", ec="#2f8f4e", fontsize=9.5)
box(ax, 8.4, 1.4, 2.6, 2.0, "검증 보고 2\n값·재계산값\n행 번호·일치", fc="white", ec="#2f6fb0", fontsize=9.5)
box(ax, 11.4, 3.4, 2.5, 2.6, "사람의 확인\n참값 대조\n'일치' 칸 2개\n직접 확인", fc="#fdf9f4", ec="#c77b2f", fontsize=9.5)
arrow(ax, 3.3, 5.3, 4.1, 6.8)
arrow(ax, 3.3, 4.1, 4.1, 2.6)
arrow(ax, 7.7, 7.0, 8.3, 7.0)
arrow(ax, 7.7, 2.4, 8.3, 2.4)
arrow(ax, 11.1, 6.6, 11.5, 5.4)
arrow(ax, 11.1, 2.8, 11.5, 4.0)
ax.text(5.9, 4.6, "같은 표를 두 갈래로 검산한다", ha="center", fontsize=9.5, color="#555",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.3"))
ax.text(7.0, 0.5, "사람이 볼 양은 열 칸에서 두 칸으로 줄지만, 마지막 확인은 남는다",
        ha="center", fontsize=10.5, color="#555")
fig.savefig(FIG / "fig02_verify_flow.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", FIG / "fig02_verify_flow.png")
