# 13주차 1회차 개념도 생성
# 실행: cd "$HOME/default-uv-env" && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
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


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 13-1
# 단일 에이전트 vs 서브에이전트 분업
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4))
for ax in axes:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

ax = axes[0]
ax.set_title("(가) 혼자 일하는 에이전트: 맥락창 하나에 전부 쌓인다", fontsize=12.5, pad=12)
box(ax, 3.1, 7.9, 3.8, 1.5, "사용자 지시", fc="#fdf9f4", ec="#c77b2f")
box(ax, 1.6, 1.0, 6.8, 6.0, "", fc="#f5f9fd", ec="#2f6fb0")
ax.text(5.0, 6.5, "에이전트의 맥락창(책상 하나)", ha="center", fontsize=11, fontweight="bold")
for i, t in enumerate(["정제 로그 전체", "분석 코드와 출력 전체", "그림 코드와 시행착오", "보고서 초안"]):
    box(ax, 2.1, 5.0 - i * 1.05, 5.8, 0.8, t, fc="white", ec="#9bb8d4", fontsize=9.5)
arrow(ax, 5.0, 7.8, 5.0, 7.2)
ax.text(5.0, 0.35, "긴 작업일수록 책상이 서류로 덮여 앞 내용이 밀려난다",
        ha="center", fontsize=10.5, color="#a04747")

ax = axes[1]
ax.set_title("(나) 서브에이전트 분업: 각자 자기 책상에서 일한다", fontsize=12.5, pad=12)
box(ax, 3.1, 7.9, 3.8, 1.5, "본 에이전트\n(팀장)", fc="#f5f9fd", ec="#2f6fb0", weight="bold")
subs = [("정제 담당", 0.4), ("분석 담당", 3.7), ("시각화 담당", 7.0)]
for t, xx in subs:
    box(ax, xx, 3.6, 2.6, 1.9, t + "\n독립된 맥락창", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
    arrow(ax, 5.0, 7.8, xx + 1.3, 5.7, color="#2f8f4e")
    arrow(ax, xx + 1.3, 3.5, 5.0, 2.2, color="#7a5fa8")
box(ax, 3.2, 0.9, 3.6, 1.3, "요약 결과만 보고", fc="#faf8fc", ec="#7a5fa8", fontsize=10)
ax.text(5.0, 0.35, "본 에이전트의 책상에는 각 담당의 요약만 올라온다",
        ha="center", fontsize=10.5, color="#2f6fb0")
fig.tight_layout()
fig.savefig(FIG / "fig13_single_vs_subagents.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 13-2
# 파이프라인 5단계와 검문소
fig, ax = plt.subplots(figsize=(12.5, 4.6))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis("off")
stages = [
    ("수집", "원자료 CSV\n(6주차)", "#f5f9fd", "#2f6fb0"),
    ("정제·병합", "분석용 데이터\n(7주차)", "#f4fbf6", "#2f8f4e"),
    ("분석", "통계 결과표\n(10주차)", "#faf8fc", "#7a5fa8"),
    ("시각화", "그림 파일\n(9주차)", "#fdf9f4", "#c77b2f"),
    ("보고", "요약 보고서\n(14주차로)", "#f7f7fc", "#5b6ee1"),
]
for i, (t1, t2, fc, ec) in enumerate(stages):
    x = 0.4 + i * 2.75
    box(ax, x, 4.6, 2.2, 1.7, t1, fc=fc, ec=ec, fontsize=12, weight="bold")
    box(ax, x, 2.6, 2.2, 1.5, t2, fc="white", ec=ec, fontsize=9.5)
    if i < 4:
        arrow(ax, x + 2.3, 5.45, x + 2.65, 5.45)
        # 검문소 표시
        cx = x + 2.475
        ax.plot([cx], [6.7], marker="v", color="#a04747", markersize=9)
        ax.text(cx, 7.2, f"검문소 {i + 1}", ha="center", fontsize=9.5,
                color="#a04747", fontweight="bold")
checks = [
    "행 수·표본 대조", "병합 손실·요약통계 확인", "수치 재검산·과잉해석 점검", "그림-수치 대조",
]
for i, c in enumerate(checks):
    cx = 0.4 + i * 2.75 + 2.475
    ax.text(cx, 1.7, c, ha="center", fontsize=8.8, color="#a04747")
ax.text(7.0, 0.5, "화살표 위의 붉은 표시가 사람이 멈춰서 확인하는 검문소다. 단계 산출물은 모두 파일로 남긴다.",
        ha="center", fontsize=10.5, color="#333")
fig.savefig(FIG / "fig13_pipeline_checkpoints.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 13-3
# MCP 개념도
fig, ax = plt.subplots(figsize=(11, 5.0))
ax.set_xlim(0, 13)
ax.set_ylim(0, 8)
ax.axis("off")
box(ax, 0.5, 3.0, 3.0, 2.2, "에이전트\n(Claude Code)", fc="#f5f9fd", ec="#2f6fb0", weight="bold")
box(ax, 4.6, 3.2, 2.6, 1.8, "MCP\n(공통 규격)", fc="#f4fbf6", ec="#2f8f4e", weight="bold")
arrow(ax, 3.6, 4.1, 4.5, 4.1)
arrow(ax, 4.5, 3.7, 3.6, 3.7)
ext = [
    ("데이터베이스", 6.6), ("업무 시스템\n(일정·문서)", 4.45), ("통계 포털 등\n외부 서비스", 2.3),
]
for t, yy in ext:
    box(ax, 9.3, yy - 0.75, 3.2, 1.5, t, fc="#fdf9f4", ec="#c77b2f", fontsize=10)
    arrow(ax, 7.3, 4.1, 9.2, yy, color="#2f8f4e")
ax.text(4.4, 0.7, "MCP가 없으면 시스템마다 연결 방식을 따로 만들어야 한다.\n"
                  "MCP는 콘센트 규격처럼, 규격만 맞으면 어떤 기기든 꽂아 쓸 수 있게 한다.",
        ha="center", fontsize=10.5, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig13_mcp.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob("fig13_*.png"))])
