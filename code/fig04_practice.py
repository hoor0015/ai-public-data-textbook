# 4주차 2회차 개념도: 스킬의 테스트와 개선 순환 (그림 4-4)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


fig, ax = plt.subplots(figsize=(12.5, 6.2))
ax.set_xlim(-0.3, 14.4)
ax.set_ylim(0, 8.6)
ax.axis("off")

W, H, Y = 2.4, 2.0, 5.4
xs = [0.4, 3.2, 6.0, 8.8, 11.6]
steps = [
    ("SKILL.md 작성\n절차와 형식을\n손으로 적는다", "#f5f9fd", "#2f6fb0"),
    ("테스트 1\n직접 호출\n/csv-profile 파일", "#f4fbf6", "#2f8f4e"),
    ("테스트 2\n자동 호출\n(새 대화, 이름 없이)", "#f4fbf6", "#2f8f4e"),
    ("테스트 3\n경계 입력\n(다른 구조의 파일)", "#f4fbf6", "#2f8f4e"),
    ("독립 검산\n(새 대화에서 보고서\n수치를 재계산)", "#f4fbf6", "#2f8f4e"),
]
checks = [
    "2.2절: 기준은 사람이 정한다",
    "형식 5개 절, 행 수·결측 대조",
    "description이 요청과 맞는가",
    "스킬이 놓치는 것 찾기",
    "보고서 값과 대조표 일치",
]
for x, (t, fc, ec), c in zip(xs, steps, checks):
    box(ax, x, Y, W, H, t, fc=fc, ec=ec)
    ax.text(x + W / 2, Y - 0.35, c, ha="center", va="top", fontsize=9, color="#555")
for i in range(len(xs) - 1):
    arrow(ax, xs[i] + W + 0.05, Y + H / 2, xs[i + 1] - 0.05, Y + H / 2)

# 아래: 개선 상자
BX, BY, BW, BH = 3.2, 1.0, 10.8, 1.9
box(ax, BX, BY, BW, BH,
    "발견한 문제를 SKILL.md에 반영하고 개선 내역을 기록한다\n"
    "개선 1: description에 실제 쓰는 표현 추가 / 개선 2: 행·열 수 대조 출력 추가\n"
    "개선 3: 식별자 열은 요약에서 제외 / 개선 4: 하이픈으로 적힌 결측도 결측으로 센다",
    fc="#fdf9f4", ec="#c77b2f")
for x in xs[1:]:
    arrow(ax, x + W / 2, Y - 0.75, x + W / 2, BY + BH + 0.05, color="#c77b2f", ls="--")

# 되돌아가는 화살표 (개선 상자 왼쪽 -> 왼쪽 여백을 돌아 v1 상자 왼쪽 옆으로)
LX = 0.05
ax.plot([BX - 0.05, LX, LX], [BY + BH / 2, BY + BH / 2, Y + H / 2], color="#c77b2f", lw=1.6)
arrow(ax, LX, Y + H / 2, xs[0] - 0.05, Y + H / 2, color="#c77b2f")
ax.text(LX + 0.2, (BY + BH + Y) / 2 - 0.6, "고친 스킬로\n다시 테스트", ha="left", va="center",
        fontsize=9.5, color="#a0561a")

ax.text(7.2, 8.25, "스킬은 만든 뒤 여러 번 시험하고 한 번 더 검산한다. 틀리는 장면이 곧 다음 수정 줄이 된다",
        ha="center", fontsize=11, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.4"))

fig.savefig(FIG / "fig04_skill_test_loop.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig04_skill_test_loop.png")


