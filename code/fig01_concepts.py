# 1주차 1회차 개념도 생성
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


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 1-1
# 챗봇과 에이전트의 차이
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
for ax in axes:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

ax = axes[0]
ax.set_title("(가) 챗봇: 한 번 묻고 한 번 답한다", fontsize=13, pad=12)
box(ax, 0.6, 6.2, 3.4, 2.2, "사용자\n질문 한 개", fc="#fdf9f4", ec="#c77b2f")
box(ax, 6.0, 6.2, 3.4, 2.2, "챗봇\n답변 한 개", fc="#f5f9fd", ec="#2f6fb0")
arrow(ax, 4.2, 7.6, 5.8, 7.6)
arrow(ax, 5.8, 6.8, 4.2, 6.8)
ax.text(5.0, 8.3, "질문", ha="center", fontsize=10, color="#555")
ax.text(5.0, 6.0, "답변", ha="center", fontsize=10, color="#555")
ax.text(5.0, 3.4, "대화가 곧 결과의 전부다.\n파일도, 실행도, 확인도 없다.",
        ha="center", fontsize=11, color="#333")

ax = axes[1]
ax.set_title("(나) 에이전트: 목표를 받아 일을 끝낸다", fontsize=13, pad=12)
box(ax, 0.4, 7.4, 3.0, 1.8, "사용자\n목표 지시", fc="#fdf9f4", ec="#c77b2f")
box(ax, 5.8, 7.4, 3.8, 1.8, "에이전트", fc="#f5f9fd", ec="#2f6fb0", weight="bold")
arrow(ax, 3.6, 8.3, 5.6, 8.3)
for i, (label, xx) in enumerate([("파일 읽기", 0.7), ("코드 실행", 4.0), ("웹 검색", 7.3)]):
    box(ax, xx, 4.2, 2.6, 1.4, label, fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
    arrow(ax, 7.7, 7.3, xx + 1.3, 5.8, color="#2f8f4e")
box(ax, 3.2, 1.2, 4.4, 1.6, "완성된 산출물\n(표·그림·보고서)", fc="#faf8fc", ec="#7a5fa8")
arrow(ax, 5.3, 4.0, 5.4, 3.0, color="#7a5fa8")
fig.tight_layout()
fig.savefig(FIG / "fig01_chatbot_vs_agent.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 1-2
# 분석가의 새 역할: 지시-검증-해석
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis("off")
box(ax, 0.6, 5.6, 3.2, 1.7, "① 지시\n무엇을 어떻게 할지\n명확히 말한다", fc="#fdf9f4", ec="#c77b2f")
box(ax, 8.2, 5.6, 3.2, 1.7, "② 검증\n결과가 맞는지\n직접 확인한다", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 4.4, 0.8, 3.2, 1.7, "③ 해석\n숫자를 정책의 말로\n옮긴다", fc="#faf8fc", ec="#7a5fa8")
box(ax, 4.4, 5.6, 3.2, 1.7, "에이전트 실행\n(코드 작성·실행·수정)", fc="#f5f9fd", ec="#2f6fb0")
arrow(ax, 3.9, 6.45, 4.3, 6.45)
arrow(ax, 7.7, 6.45, 8.1, 6.45)
arrow(ax, 9.8, 5.5, 6.6, 2.6)
arrow(ax, 4.3, 1.9, 1.8, 5.4, ls="--")
ax.text(2.4, 3.3, "다음 분석 지시로\n(반복)", fontsize=10, color="#555", ha="center")
ax.text(6.0, 4.2, "학생(분석가)이 하는 일은 ①②③,\n에이전트가 하는 일은 가운데 상자다.",
        ha="center", fontsize=11, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig01_analyst_role.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 1-3
# 교재 4부 로드맵
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 6)
ax.axis("off")
parts = [
    ("1부 (1-4주)\n에이전트와 도구", "에이전트 이해\n지시 설계\n환경 구축", "#f5f9fd", "#2f6fb0"),
    ("2부 (5-7주)\n수집과 정리", "공공데이터 생태계\nAPI 수집\n정제·병합", "#f4fbf6", "#2f8f4e"),
    ("3부 (8-11주)\n분석과 해석", "EDA·시각화\n통계 진단\n텍스트·그라운딩", "#faf8fc", "#7a5fa8"),
    ("4부 (12-13주)\n종합과 확장", "파이프라인\n종합 보고서", "#fdf9f4", "#c77b2f"),
]
for i, (t1, t2, fc, ec) in enumerate(parts):
    x = 0.4 + i * 3.2
    box(ax, x, 3.2, 2.7, 2.0, t1, fc=fc, ec=ec, fontsize=11, weight="bold")
    box(ax, x, 0.6, 2.7, 2.2, t2, fc="white", ec=ec, fontsize=10)
    if i < 3:
        arrow(ax, x + 2.8, 4.2, x + 3.1, 4.2)
fig.savefig(FIG / "fig01_roadmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig01_*.png'))])
