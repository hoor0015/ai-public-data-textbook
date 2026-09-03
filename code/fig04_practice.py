# 4주차 2회차 개념도: 스킬의 테스트와 개선 순환 (그림 4-5),
#                      하나의 스킬과 세 데이터의 보고서 (그림 4-4)
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


# ----------------------------------------------------------------------
# 그림 4-4. 하나의 스킬과 세 데이터: 무엇이 같고 무엇이 다른가
# 세 파일의 행·열 수는 code/ch04_practice.py로 계산한 실제 값이다.
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12.6, 6.4))
ax.set_xlim(0, 14.2)
ax.set_ylim(0, 8.2)
ax.axis("off")

DW, DH = 3.3, 1.25
data_boxes = [
    (6.15, "sigungu_2023.csv\n229행 12열, 결측 2열"),
    (4.15, "income_dist.csv\n13행 3열, 식별자 열 있음"),
    (2.15, "sigungu_tfr_2013.csv\n264행 3열, 결측 없음"),
]
for y, t in data_boxes:
    box(ax, 0.3, y, DW, DH, t, fc="#f5f9fd", ec="#2f6fb0")

SX, SY, SW, SH = 4.9, 3.15, 3.6, 3.3
box(ax, SX, SY, SW, SH,
    "csv-profile\nSKILL.md 한 장\n절차 8단계\n산출물 형식 6절",
    fc="#f4fbf6", ec="#2f8f4e", weight="bold")

RW, RH = 4.5, 1.25
rep_boxes = [
    (6.15, "프로파일_sigungu_2023.md\n열 정보 12행, 확인 필요 1건"),
    (4.15, "프로파일_income_dist.md\n열 정보 3행, 수치형 요약 2열"),
    (2.15, "프로파일_sigungu_tfr_2013.md\n열 정보 3행, 확인 필요 1건"),
]
for y, t in rep_boxes:
    box(ax, 9.4, y, RW, RH, t, fc="#fdf9f4", ec="#c77b2f")

for y, _ in data_boxes:
    arrow(ax, 0.3 + DW + 0.05, y + DH / 2, SX - 0.05, SY + SH / 2, color="#777")
for y, _ in rep_boxes:
    arrow(ax, SX + SW + 0.05, SY + SH / 2, 9.4 - 0.05, y + RH / 2, color="#777")

ax.text(1.95, 7.75, "입력: 세 데이터", ha="center", fontsize=11, color="#2f6fb0")
ax.text(6.7, 7.75, "절차: 하나의 스킬", ha="center", fontsize=11, color="#2f8f4e")
ax.text(11.65, 7.75, "산출: 세 보고서", ha="center", fontsize=11, color="#a0561a")

ax.text(7.1, 0.95,
        "같은 것은 절 제목 여섯 개와 표의 열 구성이고, 다른 것은 표의 행 수와 값이다.\n"
        "형식이 같아야 세 보고서를 나란히 놓고 비교할 수 있다.",
        ha="center", va="center", fontsize=10.5, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.45"))

fig.savefig(FIG / "fig04_three_reports.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig04_three_reports.png")
