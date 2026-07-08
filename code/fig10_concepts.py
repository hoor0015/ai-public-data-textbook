# 10주차 1회차 개념도: 문서-단어 행렬 (가상의 민원 3건 장난감 예시)
# 실행: cd "$HOME/default-uv-env" && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw))


# ---------------------------------------------------------------- 그림 10-1
# 문서-단어 행렬: 가상의 민원 3건 -> 3행 5열 표
fig, ax = plt.subplots(figsize=(11.5, 5.2))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.7)
ax.axis("off")

docs = [
    ('민원 1  "버스 정류장에 쓰레기가\n많으니 치워 주세요"', 5.9),
    ('민원 2  "버스 노선을 늘려\n주세요"', 3.6),
    ('민원 3  "공원의 쓰레기 무단투기를\n단속해 주세요"', 1.3),
]
for text, y in docs:
    box(ax, 0.3, y, 4.4, 1.8, text, fc="#fdf9f4", ec="#c77b2f", fontsize=10)

arrow(ax, 5.0, 4.3, 6.6, 4.3)
ax.text(5.8, 4.9, "토큰화 후\n단어 세기", ha="center", fontsize=10, color="#555")

# 행렬 표: 행 3(문서) x 열 5(단어)
words = ["버스", "정류장", "쓰레기", "노선", "공원"]
counts = [
    [1, 1, 1, 0, 0],
    [1, 0, 0, 1, 0],
    [0, 0, 1, 0, 1],
]
x0, y0, cw, chh = 8.2, 1.3, 1.05, 1.15
# 열 머리글
for j, w in enumerate(words):
    box(ax, x0 + j * cw, y0 + 3 * chh + 0.15, cw - 0.12, 0.9, w,
        fc="#f5f9fd", ec="#2f6fb0", fontsize=10, weight="bold")
# 행 머리글
for i in range(3):
    box(ax, x0 - 1.55, y0 + (2 - i) * chh, 1.35, chh - 0.15, f"민원 {i+1}",
        fc="#fdf9f4", ec="#c77b2f", fontsize=10)
# 값 칸
for i in range(3):
    for j in range(5):
        v = counts[i][j]
        fc = "#e8f1fa" if v > 0 else "white"
        box(ax, x0 + j * cw, y0 + (2 - i) * chh, cw - 0.12, chh - 0.15, str(v),
            fc=fc, ec="#9db8d2", fontsize=12,
            weight="bold" if v > 0 else "normal")

ax.text(x0 + 2.5 * cw, 0.45, "행 = 문서, 열 = 단어, 칸 = 등장 횟수",
        ha="center", fontsize=10, color="#333")
ax.text(x0 + 2.5 * cw, 6.6, "문서-단어 행렬 (3행 x 5열)",
        ha="center", fontsize=12, fontweight="bold")
ax.text(2.5, 8.1, "글 (비정형 데이터)", ha="center", fontsize=12, fontweight="bold")

fig.tight_layout()
fig.savefig(FIG / "fig10_dtm_concept.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig10_dtm_concept.png")
