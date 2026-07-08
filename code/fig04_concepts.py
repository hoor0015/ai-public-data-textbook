# 4주차 1회차 개념도 생성
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


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 4-1
# 터미널과 셸: 에이전트의 작업대
fig, ax = plt.subplots(figsize=(11, 5.4))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

box(ax, 0.5, 6.6, 2.9, 1.7, "사람\n(직접 타이핑)", fc="#fdf9f4", ec="#c77b2f")
box(ax, 0.5, 4.0, 2.9, 1.7, "에이전트\n(스스로 입력)", fc="#fdf9f4", ec="#c77b2f", weight="bold")
box(ax, 4.6, 5.2, 2.7, 1.9, "터미널\n(창구)\n문자를 주고받는 창", fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
box(ax, 8.3, 5.2, 2.7, 1.9, "셸\n(통역사)\n명령을 해석·전달", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
box(ax, 8.3, 1.2, 2.7, 1.9, "컴퓨터\n(운영체제)\n파일·프로그램 실행", fc="#faf8fc", ec="#7a5fa8", fontsize=10)

arrow(ax, 3.5, 7.2, 4.7, 6.6)
arrow(ax, 3.5, 4.9, 4.7, 5.6)
arrow(ax, 7.4, 6.4, 8.2, 6.4)
arrow(ax, 9.7, 5.1, 9.7, 3.3, color="#2f8f4e")
arrow(ax, 10.4, 3.3, 10.4, 5.1, color="#7a5fa8")
arrow(ax, 8.2, 5.7, 7.4, 5.7, color="#7a5fa8")
ax.text(5.4, 7.6, "명령 (예: uv run main.py)", fontsize=10, color="#555", ha="center")
ax.text(11.6, 4.2, "실행 결과", fontsize=10, color="#7a5fa8", ha="center")
ax.text(7.8, 4.7, "결과 문자", fontsize=10, color="#7a5fa8", ha="center")
ax.text(6.0, 0.9, "터미널은 대화 창구, 셸은 그 안의 통역사다.\n사람이 치든 에이전트가 치든, 명령은 같은 길을 지나 컴퓨터에 닿는다.",
        ha="center", fontsize=11, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig04_terminal_shell.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 4-2
# 가상환경: 프로젝트마다 독립된 도구상자
fig, axes = plt.subplots(1, 2, figsize=(12, 5.0))
for a in axes:
    a.set_xlim(0, 10)
    a.set_ylim(0, 10)
    a.axis("off")

ax = axes[0]
ax.set_title("(가) 컴퓨터 전체에 하나만 설치하면", fontsize=13, pad=12)
ax.add_patch(FancyBboxPatch((0.6, 4.6), 8.8, 3.6, boxstyle="round,pad=0.1",
                            fc="#fdf9f4", ec="#c77b2f", lw=1.8))
ax.text(5.0, 7.6, "컴퓨터 공용 선반 (설치 자리는 하나)", fontsize=11, ha="center", fontweight="bold")
box(ax, 1.4, 5.2, 3.2, 1.5, "pandas 구버전?", fc="white", ec="#c77b2f", fontsize=10)
box(ax, 5.4, 5.2, 3.2, 1.5, "pandas 신버전?", fc="white", ec="#c77b2f", fontsize=10)
box(ax, 0.8, 0.9, 3.6, 1.6, "작년 과제 프로젝트\n(구버전이어야 작동)", fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
box(ax, 5.6, 0.9, 3.6, 1.6, "이번 학기 프로젝트\n(신버전이 필요)", fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
arrow(ax, 2.6, 2.7, 3.0, 5.0, color="#c77b2f")
arrow(ax, 7.4, 2.7, 7.0, 5.0, color="#c77b2f")
ax.text(5.0, 3.6, "충돌!", fontsize=13, ha="center", color="#c0392b", fontweight="bold")

ax = axes[1]
ax.set_title("(나) 가상환경: 프로젝트마다 도구상자", fontsize=13, pad=12)
ax.add_patch(FancyBboxPatch((0.5, 3.4), 4.2, 4.8, boxstyle="round,pad=0.1",
                            fc="#f4fbf6", ec="#2f8f4e", lw=1.8))
ax.text(2.6, 7.5, "작년 과제 폴더", fontsize=11, ha="center", fontweight="bold")
box(ax, 1.0, 5.4, 3.2, 1.3, ".venv 도구상자\npandas 구버전", fc="white", ec="#2f8f4e", fontsize=9.5)
box(ax, 1.0, 3.8, 3.2, 1.3, "코드·데이터", fc="white", ec="#2f8f4e", fontsize=9.5)
ax.add_patch(FancyBboxPatch((5.3, 3.4), 4.2, 4.8, boxstyle="round,pad=0.1",
                            fc="#f4fbf6", ec="#2f8f4e", lw=1.8))
ax.text(7.4, 7.5, "이번 학기 폴더", fontsize=11, ha="center", fontweight="bold")
box(ax, 5.8, 5.4, 3.2, 1.3, ".venv 도구상자\npandas 신버전", fc="white", ec="#2f8f4e", fontsize=9.5)
box(ax, 5.8, 3.8, 3.2, 1.3, "코드·데이터", fc="white", ec="#2f8f4e", fontsize=9.5)
ax.text(5.0, 1.6, "서로 건드리지 않는다.\n한쪽을 바꿔도 다른 쪽은 그대로 작동한다.",
        ha="center", fontsize=11, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.tight_layout()
fig.savefig(FIG / "fig04_venv.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 4-3
# 분석 프로젝트 폴더 구조 (트리형)
fig, ax = plt.subplots(figsize=(11, 7.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 12.4)
ax.axis("off")

box(ax, 0.5, 10.9, 5.0, 1.2, "공공데이터분석/  (작업 폴더)", fc="#f7f7fc", ec="#5b6ee1",
    fontsize=12, weight="bold")

items = [
    ("data/", "원본 데이터 보관 (sigungu_2023.csv)", "#f5f9fd", "#2f6fb0", "1주차에 만듦"),
    ("산출물/", "표·그림·보고서 (에이전트가 저장)", "#f5f9fd", "#2f6fb0", "1주차에 만듦"),
    ("메모/", "관찰일지·기록", "#f5f9fd", "#2f6fb0", "1주차에 만듦"),
    ("CLAUDE.md", "에이전트 규칙 (폴더의 사용설명서)", "#faf8fc", "#7a5fa8", "3주차에 만듦"),
    ("pyproject.toml", "프로젝트 정보와 패키지 목록", "#f4fbf6", "#2f8f4e", "4주차: uv가 만듦"),
    ("uv.lock", "패키지의 정확한 버전 기록 (재현의 열쇠)", "#f4fbf6", "#2f8f4e", "4주차: uv가 만듦"),
    (".venv/", "가상환경 도구상자 (직접 안 건드림)", "#f4fbf6", "#2f8f4e", "4주차: uv가 만듦"),
    ("main.py", "분석 코드 (에이전트가 작성)", "#f4fbf6", "#2f8f4e", "4주차부터"),
]
spine_x = 1.1
for i, (name, desc, fc, ec, when) in enumerate(items):
    y = 9.6 - i * 1.25
    ax.plot([spine_x, spine_x + 0.5], [y + 0.45, y + 0.45], color="#999", lw=1.2)
    box(ax, spine_x + 0.5, y, 3.0, 0.9, name, fc=fc, ec=ec, fontsize=10.5, weight="bold")
    ax.text(spine_x + 3.75, y + 0.45, desc, fontsize=10, va="center", ha="left", color="#333")
    ax.text(10.4, y + 0.45, when, fontsize=9.5, va="center", ha="left", color="#777")
ax.plot([spine_x, spine_x], [10.9, 9.6 - 7 * 1.25 + 0.45], color="#999", lw=1.2)

ax.text(10.4, 11.5, "파랑 = 내가 관리\n초록 = uv·에이전트가 관리\n보라 = 에이전트 규칙",
        fontsize=10, color="#333", ha="left", va="center",
        bbox=dict(fc="white", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig04_folder.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig04_*.png'))])
