# 2주차 1회차 개념도 생성
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
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


# ---------------------------------------------------------------- 그림 2-1
# 다음 단어 예측
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis("off")
box(ax, 0.5, 4.6, 6.6, 1.6, "입력: \"대한민국의 수도는\"", fc="#fdf9f4", ec="#c77b2f", fontsize=12)
box(ax, 8.4, 4.6, 3.1, 1.6, "언어모델", fc="#f5f9fd", ec="#2f6fb0", fontsize=12, weight="bold")
arrow(ax, 7.2, 5.4, 8.3, 5.4)
cands = [("서울", 0.92), ("부산", 0.03), ("인천", 0.02), ("...", 0.03)]
ax.text(2.2, 3.6, "다음에 올 말의 확률", fontsize=11, color="#333")
for i, (w, p) in enumerate(cands):
    y = 2.7 - i * 0.62
    ax.text(1.2, y, w, fontsize=11, ha="left", va="center")
    ax.add_patch(FancyBboxPatch((2.6, y - 0.18), 6.0 * p, 0.36, boxstyle="round,pad=0.02",
                                fc="#5b6ee1", ec="none"))
    ax.text(2.75 + 6.0 * p, y, f"{p:.2f}", fontsize=10, va="center", color="#333")
arrow(ax, 9.9, 4.5, 6.0, 3.3, color="#5b6ee1")
ax.text(9.2, 0.7, "가장 그럴듯한 말을 골라 잇는다:\n\"대한민국의 수도는 서울…\"",
        ha="center", fontsize=11,
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig02_next_token.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 2-2
# 맥락창
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.5)
ax.axis("off")
ax.add_patch(FancyBboxPatch((0.6, 1.6), 10.8, 3.4, boxstyle="round,pad=0.1",
                            fc="#f7f7fc", ec="#5b6ee1", lw=1.8))
ax.text(6.0, 5.6, "맥락창: 에이전트가 \"지금\" 볼 수 있는 것의 전부", fontsize=13,
        ha="center", fontweight="bold")
items = ["대화 내용\n(질문과 답)", "열어 본 파일\n(데이터·문서)", "실행 결과\n(코드 출력·오류)", "규칙 파일\n(CLAUDE.md)"]
for i, t in enumerate(items):
    box(ax, 1.1 + i * 2.6, 2.3, 2.2, 1.8, t, fc="white", ec="#2f6fb0", fontsize=10)
ax.text(6.0, 0.7, "맥락창 밖에 있는 것(안 열어 본 파일, 지난주 대화)은 아무리 중요해도 에이전트에게 보이지 않는다.",
        ha="center", fontsize=11, color="#333")
fig.savefig(FIG / "fig02_context_window.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 2-3
# 에이전트 루프
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.set_xlim(0, 12)
ax.set_ylim(0, 9)
ax.axis("off")
box(ax, 4.3, 7.2, 3.4, 1.3, "사용자의 목표 지시", fc="#fdf9f4", ec="#c77b2f")
box(ax, 1.0, 4.4, 3.0, 1.6, "① 계획\n다음에 할 일을\n정한다", fc="#f5f9fd", ec="#2f6fb0")
box(ax, 4.6, 4.4, 3.0, 1.6, "② 행동\n도구를 하나\n사용한다", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 8.2, 4.4, 3.0, 1.6, "③ 관찰\n결과를 보고\n판단한다", fc="#faf8fc", ec="#7a5fa8")
box(ax, 4.3, 0.9, 3.4, 1.4, "목표 달성 → 보고", fc="#f7f7fc", ec="#5b6ee1")
arrow(ax, 6.0, 7.1, 3.2, 6.2)
arrow(ax, 4.1, 5.2, 4.5, 5.2)
arrow(ax, 7.7, 5.2, 8.1, 5.2)
arrow(ax, 9.7, 4.3, 3.0, 3.0, ls="--")
ax.text(4.2, 2.75, "아직 멀었으면 ①로 돌아가 반복", fontsize=10, color="#555", ha="center")
arrow(ax, 9.7, 4.3, 7.4, 2.0, color="#5b6ee1")
fig.savefig(FIG / "fig02_agent_loop.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 2-4
# 도구 상자
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis("off")
box(ax, 4.3, 5.2, 3.4, 1.4, "에이전트", fc="#f5f9fd", ec="#2f6fb0", fontsize=12, weight="bold")
tools = [
    ("파일 읽기·쓰기", "데이터를 열고\n보고서를 저장"),
    ("터미널 실행", "파이썬 코드를\n돌리고 결과 확인"),
    ("웹 검색·열람", "포털·문서를\n찾아 읽기"),
    ("사용자 질문", "모호하면\n되물어 확인"),
]
for i, (t1, t2) in enumerate(tools):
    x = 0.6 + i * 2.9
    box(ax, x, 1.9, 2.5, 1.9, f"{t1}\n{t2}", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
    arrow(ax, 6.0, 5.1, x + 1.25, 4.0, color="#2f8f4e")
ax.text(6.0, 0.7, "도구 하나하나는 단순하다. 힘은 \"어떤 도구를 언제 쓸지\" 에이전트가 스스로 고르는 데서 나온다.",
        ha="center", fontsize=11, color="#333")
fig.savefig(FIG / "fig02_tools.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig02_*.png'))])
