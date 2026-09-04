# 5주차 1회차 개념도 생성 (남이 만든 스킬 가져다 쓰기)
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

BLUE, BLUE_F = "#2f6fb0", "#f5f9fd"
GREEN, GREEN_F = "#2f8f4e", "#f4fbf6"
ORANGE, ORANGE_F = "#c77b2f", "#fdf9f4"
PURPLE, PURPLE_F = "#7a5fa8", "#faf8fc"
NAVY, NAVY_F = "#5b6ee1", "#f7f7fc"
GRAY = "#555"


def box(ax, x, y, w, h, text="", fc="white", ec=BLUE, fontsize=11,
        weight="normal", lw=1.4, ls="-", color="black"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=lw, linestyle=ls))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fontsize, fontweight=weight, color=color)


def arrow(ax, x1, y1, x2, y2, color=GRAY, style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw,
                                 linestyle=ls))


# ---------------------------------------------------------------- 그림 5-1
# GitHub 저장소 -> 마켓플레이스 -> 플러그인 -> 스킬, 그리고 내 컴퓨터의 자리
fig, ax = plt.subplots(figsize=(13.2, 6.4))
ax.set_xlim(0, 15)
ax.set_ylim(0, 10)
ax.axis("off")

# 왼쪽: GitHub 저장소
box(ax, 0.3, 1.0, 5.7, 8.0, fc="#fbfbfd", ec=GRAY, lw=1.2, ls="--")
ax.text(3.15, 8.55, "GitHub 저장소", ha="center", fontsize=12.5, fontweight="bold")
ax.text(3.15, 8.15, "github.com/chrisryugj/kordoc", ha="center",
        fontsize=9.5, color=GRAY)

box(ax, 0.7, 6.55, 4.9, 1.3, fc=NAVY_F, ec=NAVY)
ax.text(3.15, 7.48, "마켓플레이스 파일", ha="center", fontsize=11, fontweight="bold")
ax.text(3.15, 7.10, ".claude-plugin/marketplace.json", ha="center",
        fontsize=8.8, color=GRAY)
ax.text(3.15, 6.75, "이 저장소가 내놓는 꾸러미의 목록", ha="center",
        fontsize=9.2, color="#333")

box(ax, 0.7, 1.5, 4.9, 4.6, fc=PURPLE_F, ec=PURPLE)
ax.text(3.15, 5.62, "플러그인 kordoc (꾸러미)", ha="center",
        fontsize=11.5, fontweight="bold", color="#4a3a68")
ax.text(3.15, 5.22, "버전 4.12.0 / 라이선스 MIT", ha="center", fontsize=9, color=GRAY)

box(ax, 1.15, 2.95, 4.0, 1.9, fc=GREEN_F, ec=GREEN)
ax.text(3.15, 4.42, "스킬 kordoc", ha="center", fontsize=11, fontweight="bold")
ax.text(3.15, 4.05, "skills/kordoc/SKILL.md", ha="center", fontsize=8.8, color=GRAY)
ax.text(3.15, 3.58, "4주차에 직접 만든 파일과", ha="center", fontsize=9.2, color="#333")
ax.text(3.15, 3.24, "같은 구조 (머리말 + 절차)", ha="center", fontsize=9.2, color="#333")

ax.text(3.15, 2.15, "한 꾸러미에 스킬이 여러 개일 수도 있다", ha="center",
        fontsize=9, color=GRAY, style="italic")

# 오른쪽: 내 컴퓨터
box(ax, 9.0, 1.0, 5.7, 8.0, fc="#fbfbfd", ec=GRAY, lw=1.2, ls="--")
ax.text(11.85, 8.55, "내 컴퓨터", ha="center", fontsize=12.5, fontweight="bold")
ax.text(11.85, 8.15, "설치는 사본을 내려받는 일이다", ha="center",
        fontsize=9.5, color=GRAY)

box(ax, 9.4, 4.5, 4.9, 3.35, fc=PURPLE_F, ec=PURPLE)
ax.text(11.85, 7.55, "홈 폴더 아래의 설치 자리", ha="center",
        fontsize=11, fontweight="bold", color="#4a3a68")
ax.text(11.85, 7.15, ".claude/plugins/cache/", ha="center", fontsize=8.8, color=GRAY)
ax.text(11.85, 6.82, "kordoc / kordoc / 4.12.0", ha="center", fontsize=8.8, color=GRAY)
ax.text(11.85, 6.44, "(마켓플레이스 / 플러그인 / 버전)", ha="center",
        fontsize=8.5, color=GRAY, style="italic")
box(ax, 9.9, 4.85, 3.9, 1.25, fc=GREEN_F, ec=GREEN)
ax.text(11.85, 5.72, "SKILL.md 사본", ha="center", fontsize=10.5, fontweight="bold")
ax.text(11.85, 5.30, "경로에 버전이 들어 있으므로", ha="center", fontsize=8.8, color="#333")
ax.text(11.85, 5.00, "내 원본이 아니라 특정 판의 사본이다", ha="center",
        fontsize=8.8, color="#333")

box(ax, 9.4, 1.5, 4.9, 2.35, fc=BLUE_F, ec=BLUE)
ax.text(11.85, 3.50, "대화창에서 부른다", ha="center", fontsize=11, fontweight="bold")
ax.text(11.85, 3.05, "/kordoc:kordoc", ha="center", fontsize=10.5, color="#1a4e80")
ax.text(11.85, 2.62, "(플러그인 이름 : 스킬 이름)", ha="center", fontsize=8.8, color=GRAY)
ax.text(11.85, 2.15, "이름을 부르지 않아도 요청이 설명과", ha="center",
        fontsize=9, color="#333")
ax.text(11.85, 1.82, "맞으면 에이전트가 스스로 쓴다", ha="center", fontsize=9, color="#333")

# 가운데 화살표 두 개
arrow(ax, 6.1, 7.2, 8.9, 7.2, color=NAVY)
ax.text(7.5, 7.75, "1단계. 목록을 등록한다", ha="center", fontsize=9.5,
        fontweight="bold", color="#3a4aa8")
ax.text(7.5, 6.82, "/plugin marketplace add", ha="center", fontsize=8.3, color=GRAY)
ax.text(7.5, 6.52, "chrisryugj/kordoc", ha="center", fontsize=8.3, color=GRAY)

arrow(ax, 6.1, 3.9, 8.9, 3.9, color=PURPLE)
ax.text(7.5, 4.45, "2단계. 꾸러미를 내려받는다", ha="center", fontsize=9.5,
        fontweight="bold", color="#4a3a68")
ax.text(7.5, 3.52, "/plugin install", ha="center", fontsize=8.3, color=GRAY)
ax.text(7.5, 3.22, "kordoc@kordoc", ha="center", fontsize=8.3, color=GRAY)
ax.text(7.5, 2.80, "(플러그인 @ 마켓플레이스)", ha="center", fontsize=8, color=GRAY,
        style="italic")

ax.text(7.5, 0.45, "저장소 한 곳에 목록과 꾸러미와 스킬이 층으로 들어 있고, 명령 두 줄이 그 층을 내 컴퓨터로 옮긴다",
        ha="center", fontsize=10, color="#333",
        bbox=dict(fc=NAVY_F, ec="#d9d9e3", boxstyle="round,pad=0.4"))
fig.savefig(FIG / "fig05_marketplace.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 5-2
# 설치 전에 확인할 네 가지
fig, ax = plt.subplots(figsize=(12.4, 7.0))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

ax.text(7.0, 9.35, "설치 전에 확인할 네 가지", ha="center", fontsize=14,
        fontweight="bold")
ax.text(7.0, 8.85, "설치는 파일을 내려받는 일이 아니라, 남이 쓴 절차와 코드를 내 컴퓨터에서 돌리기로 하는 결정이다",
        ha="center", fontsize=10, color=GRAY)

cards = [
    (0.4, 4.9, BLUE, BLUE_F, "1. 누가 만들었나",
     ["저장소 주인, 최근 갱신 날짜,", "남긴 문서와 이슈, 버전 번호"],
     "kordoc: chrisryugj, 4.12.0판"),
    (7.2, 4.9, GREEN, GREEN_F, "2. 무엇을 하는가",
     ["README와 SKILL.md의 머리말을", "읽고 기능의 범위를 파악한다"],
     "kordoc: 공문서를 Markdown으로"),
    (0.4, 1.3, ORANGE, ORANGE_F, "3. 어떤 도구를 부르나",
     ["절차 안에서 터미널 명령을 실행하는가,", "바깥 프로그램을 내려받는가"],
     "kordoc: npx로 변환기를 부른다"),
    (7.2, 1.3, PURPLE, PURPLE_F, "4. 라이선스는 무엇인가",
     ["써도 되는가, 고쳐도 되는가,", "출처를 어떻게 밝히는가"],
     "kordoc: MIT"),
]
for x, y, ec, fc, title, lines, ex in cards:
    box(ax, x, y, 6.4, 3.1, fc=fc, ec=ec)
    ax.text(x + 3.2, y + 2.35, title, ha="center", fontsize=12.5,
            fontweight="bold", color=ec)
    ax.text(x + 3.2, y + 1.65, lines[0], ha="center", fontsize=10, color="#333")
    ax.text(x + 3.2, y + 1.25, lines[1], ha="center", fontsize=10, color="#333")
    ax.text(x + 3.2, y + 0.5, ex, ha="center", fontsize=9.5, color=GRAY,
            bbox=dict(fc="white", ec="#e0e0e6", boxstyle="round,pad=0.3"))

ax.text(7.0, 0.5, "네 칸의 답을 채우지 못했다면 아직 설치할 때가 아니다",
        ha="center", fontsize=11, color="#333",
        bbox=dict(fc=ORANGE_F, ec=ORANGE, boxstyle="round,pad=0.45"))
fig.savefig(FIG / "fig05_before_install.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 5-3
# 가져다 쓸 것인가, 만들 것인가
fig, ax = plt.subplots(figsize=(12.4, 7.6))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

box(ax, 0.6, 8.6, 6.0, 1.0, fc=NAVY_F, ec=NAVY)
ax.text(3.6, 8.98, "반복되는 절차 하나가 생겼다", ha="center", fontsize=12.5,
        fontweight="bold")

qs = [
    (6.55, "질문 1. 같은 일을 하는 공개 스킬이 이미 있는가", "없다"),
    (4.65, "질문 2. 설치 전 네 가지 점검을 통과하는가", "아니다"),
    (2.75, "질문 3. 우리 기관의 기준과 판단이 절차에 들어가는가", "그렇다"),
]
for y, q, no in qs:
    box(ax, 0.6, y, 6.0, 1.25, fc="white", ec=BLUE)
    ax.text(3.6, y + 0.52, q, ha="center", fontsize=11.5)

outs = [
    (6.55, GREEN, GREEN_F, "직접 만든다", "4주차의 방식으로 SKILL.md를 쓴다"),
    (4.65, ORANGE, ORANGE_F, "설치하지 않는다", "다른 스킬을 찾거나 직접 만든다"),
    (2.75, PURPLE, PURPLE_F, "가져다 쓰고 얹는다",
     "변환은 공개 스킬에, 우리 서식과 판단은 내 스킬에"),
]
for y, ec, fc, t1, t2 in outs:
    box(ax, 8.4, y, 5.0, 1.25, fc=fc, ec=ec)
    ax.text(10.9, y + 0.82, t1, ha="center", fontsize=11.5, fontweight="bold",
            color=ec)
    ax.text(10.9, y + 0.38, t2, ha="center", fontsize=8.8, color="#333")

box(ax, 0.6, 0.5, 6.0, 1.25, fc=BLUE_F, ec=BLUE)
ax.text(3.6, 1.28, "가져다 쓴다", ha="center", fontsize=12, fontweight="bold",
        color=BLUE)
ax.text(3.6, 0.82, "설치하고, 결과는 사람이 원문과 대조한다", ha="center",
        fontsize=9.5, color="#333")

arrow(ax, 3.6, 8.55, 3.6, 7.9)
arrow(ax, 3.6, 6.5, 3.6, 5.98)
arrow(ax, 3.6, 4.6, 3.6, 4.08)
arrow(ax, 3.6, 2.7, 3.6, 1.85)
for y, no in [(6.55, "없다"), (4.65, "아니다"), (2.75, "그렇다")]:
    arrow(ax, 6.65, y + 0.62, 8.3, y + 0.62)
    ax.text(7.45, y + 0.85, no, ha="center", fontsize=9.5, color=GRAY)
for y, yes in [(6.55, "있다"), (4.65, "그렇다"), (2.75, "아니다")]:
    ax.text(3.78, y - 0.5, yes, ha="left", fontsize=9.5, color=GRAY)

ax.text(10.9, 1.12, "판단은 한 번으로 끝나지 않는다.\n공개 스킬이 새로 나오거나 만든 이가 손을 놓으면\n같은 질문을 다시 던진다.",
        ha="center", fontsize=10, color="#333",
        bbox=dict(fc="#fbfbfd", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig05_make_or_take.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob("fig05_*.png"))])
