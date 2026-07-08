# 7주차 그림: 병합 진단 결과 다이어그램 (실제 병합 결과 수치 기반)
# 수치 출처: code/ch07_merge.py 실행 결과 (both 228, left_only 1, right_only 36)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
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


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw))


fig, ax = plt.subplots(figsize=(11.5, 6.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 10)
ax.axis("off")

# 왼쪽: 두 원본 데이터
box(ax, 0.4, 6.6, 3.3, 2.2, "sigungu_2023.csv\n229행\n(2023년 기준 시군구)",
    fc="#f5f9fd", ec="#2f6fb0", weight="bold")
box(ax, 0.4, 1.2, 3.3, 2.2, "sigungu_tfr_2013.csv\n264행\n(2013년 기준, 일반구 포함)",
    fc="#fdf9f4", ec="#c77b2f", weight="bold")

# 가운데: 병합
box(ax, 4.8, 3.9, 3.0, 2.2, "병합\n키 = (시도, 시군구)", fc="#f7f7fc", ec="#5b6ee1",
    weight="bold")
arrow(ax, 3.8, 7.3, 5.4, 6.2, color="#2f6fb0")
arrow(ax, 3.8, 2.7, 5.4, 3.8, color="#c77b2f")

# 오른쪽: 세 갈래 결과
box(ax, 9.0, 7.2, 3.6, 1.8, "양쪽 일치 228곳\n(both)", fc="#f4fbf6", ec="#2f8f4e",
    weight="bold")
box(ax, 9.0, 4.4, 3.6, 1.8, "2023년에만 1곳\n인천 미추홀구\n(2013년엔 '남구')",
    fc="#fdf4f4", ec="#c0392b", fontsize=10)
box(ax, 9.0, 1.0, 3.6, 2.4,
    "2013년에만 36곳\n일반구 33 (분당구 등)\n청원군 (2014년 통합 소멸)\n세종시 (표기 중복)",
    fc="#fdf4f4", ec="#c0392b", fontsize=10)
arrow(ax, 7.9, 5.6, 8.9, 8.0, color="#2f8f4e")
arrow(ax, 7.9, 5.0, 8.9, 5.3, color="#c0392b")
arrow(ax, 7.9, 4.4, 8.9, 2.4, color="#c0392b")

ax.text(6.3, 1.4, "이름이 안 맞는 이유는 오타가 아니라\n10년 사이의 행정구역 개편과\n집계 단위의 차이다.",
        ha="center", fontsize=10.5, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))

fig.savefig(FIG / "fig07_merge_diagram.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig07_merge_diagram.png")
