# 5주차 2회차 개념도 생성 (그림 5-5: 오류 심기 세 유형이 어느 검증 층에서 잡히는가)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

figfit.MAX_PT = 12.0

from matplotlib.patches import FancyBboxPatch  # noqa: E402

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)

GREEN = ("#f4fbf6", "#2f8f4e")
ORANGE = ("#fdf9f4", "#c77b2f")
BLUE = ("#f5f9fd", "#2f6fb0")

cols = ["스크립트의 자동 경고\n(4절)", "에이전트의 판단\n(4절과 5절)", "사람의 눈\n(보고서와 파일)"]
rows = [
    ("유형 A  값 삭제\n지니계수 5칸 비움",
     [("잡힘", GREEN), ("잡힘", GREEN), ("잡힘", GREEN)]),
    ("유형 B  열 이름 변경\n합계출산율을 출산율로",
     [("놓침", ORANGE), ("고친 뒤 잡힘", BLUE), ("잡힘", GREEN)]),
    ("유형 C  천 단위 쉼표\n총인구가 문자로",
     [("놓침", ORANGE), ("고친 뒤 잡힘", BLUE), ("잡힘", GREEN)]),
]

fig, ax = plt.subplots(figsize=(11, 6.2))
ax.set_xlim(0, 12.6)
ax.set_ylim(0, 8.2)
ax.axis("off")

X0, CW, GAP = 4.0, 2.6, 0.25
Y0, RH, RGAP = 5.0, 1.35, 0.3

for j, c in enumerate(cols):
    ax.text(X0 + j * (CW + GAP) + CW / 2, 7.15, c, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="#333")

for i, (label, cells) in enumerate(rows):
    y = Y0 - i * (RH + RGAP)
    ax.text(3.6, y + RH / 2, label, ha="right", va="center", fontsize=10, color="#333")
    for j, (text, (fc, ec)) in enumerate(cells):
        x = X0 + j * (CW + GAP)
        ax.add_patch(FancyBboxPatch((x, y), CW, RH, boxstyle="round,pad=0.05",
                                    fc=fc, ec=ec, lw=1.5))
        ax.text(x + CW / 2, y + RH / 2, text, ha="center", va="center", fontsize=11)

ax.plot([X0 - 0.2, X0 - 0.2], [Y0 - 2 * (RH + RGAP) - 0.2, 6.8],
        color="#bbbbbb", lw=1.0)
ax.plot([X0 - 0.35, 12.3], [6.75, 6.75], color="#bbbbbb", lw=1.0)

ax.text(6.3, 0.95, "왼쪽 두 층은 미리 정해 둔 것만 잡고, 오른쪽 층은 세 유형 모두에 통한다.",
        ha="center", va="center", fontsize=10.5, color="#4a3a68")
ax.text(6.3, 0.35,
        "잡힘: 고치기 전에도 잡았다   /   고친 뒤 잡힘: 절차와 기준표를 손본 다음에 잡았다   /   놓침: 끝내 못 잡았다",
        ha="center", va="center", fontsize=9.2, color="#666")

fig.savefig(FIG / "fig05_error_layers.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved:", FIG / "fig05_error_layers.png")
