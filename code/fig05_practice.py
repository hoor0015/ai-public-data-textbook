# 5주차 2회차 개념도 생성 (그림 5-4: 공문서 -> kordoc 스킬 -> Markdown -> 데이터)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", lw=1.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.8, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=17, color=color, lw=lw, linestyle=ls))


fig, ax = plt.subplots(figsize=(12.4, 5.6))
ax.set_xlim(0, 14)
ax.set_ylim(0.95, 7)
ax.axis("off")

BW, BH, BY = 2.4, 1.7, 4.1
xs = [0.25, 3.95, 7.65, 11.35]
MID = BY + BH / 2

box(ax, xs[0], BY, BW, BH, "공문서 파일\nhwpx / hwp / pdf", fc="#f4f4f7", ec="#777")
box(ax, xs[1], BY, BW, BH, "kordoc 스킬\nSKILL.md의 절차", fc="#f4fbf6", ec="#2f8f4e")
box(ax, xs[2], BY, BW, BH, "Markdown 문서\n제목 + 문단 + 표", fc="#f5f9fd", ec="#2f6fb0")
box(ax, xs[3], BY, BW, BH, "CSV + pandas\n계산과 그림", fc="#f5f9fd", ec="#2f6fb0")

gaps = ["설치한 스킬이\n나선다 (2.4)", "npx로 변환\n도구 실행", "표를 CSV로\n옮긴다 (2.5)"]
for i, lab in enumerate(gaps):
    arrow(ax, xs[i] + BW + 0.05, MID, xs[i + 1] - 0.05, MID)
    ax.text((xs[i] + BW + xs[i + 1]) / 2, MID + 0.22, lab,
            ha="center", va="bottom", fontsize=9, color="#444")

notes = [
    "사람이 읽으려고 만든 문서.\n서식 안에 글자가 갇혀 있다",
    "GitHub에서 설치한 스킬.\n4주차 SKILL.md와 같은 구조",
    "글자만 남은 문서.\n표는 파이프 표로 나온다",
    "행과 열이 된 표.\n3주차 uv 환경에서 읽는다",
]
for x, note in zip(xs, notes):
    ax.text(x + BW / 2, BY - 0.22, note, ha="center", va="top", fontsize=9.5, color="#555")

box(ax, 0.25, 1.2, 13.5, 1.0, "사람의 검증: 변환된 Markdown과 CSV를 원문 공문서와 대조한다 (2.7)",
    fc="#fdf9f4", ec="#c77b2f")
for x in (xs[0], xs[2], xs[3]):
    arrow(ax, x + BW / 2, 2.25, x + BW / 2, BY - 1.15, color="#c77b2f", lw=1.5, ls=(0, (5, 3)))

ax.text(0.25, 6.65, "그림 5-4. 공문서가 데이터가 되기까지", fontsize=13, fontweight="bold", color="#222")
ax.text(0.25, 6.25, "오른쪽으로 한 칸씩 갈수록 다루기 쉬운 형태가 되고, 그만큼 원문에서 멀어진다.",
        fontsize=10, color="#555")

fig.tight_layout()
fig.savefig(FIG / "fig05_kordoc_flow.png", dpi=150, bbox_inches="tight")
print("saved:", FIG / "fig05_kordoc_flow.png")
