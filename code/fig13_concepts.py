# 13주차 1차시(통합 장) 개념도 생성: 그림 13-1 (파이프라인과 검증 지점), 그림 13-2 (검증 지점의 1차·2차 확인)
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 <이 파일 경로>
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
# 파이프라인 5단계: 단계, 담당, 산출 파일, 검증 지점
fig, ax = plt.subplots(figsize=(13, 5.6))
ax.set_xlim(0, 14)
ax.set_ylim(0.6, 8.2)
ax.axis("off")
stages = [
    ("① 수집 확인\n(9주차 파일)", "본 에이전트", "확인 보고\n(행 수·열·결측)", "#f5f9fd", "#2f6fb0"),
    ("② 정제·병합\n(7주차)", "cleaner", "merged.csv\n정제로그.md", "#f4fbf6", "#2f8f4e"),
    ("③ 분석\n(11주차)", "analyst", "analysis.md\n(결과표)", "#faf8fc", "#7a5fa8"),
    ("④ 시각화\n(9주차)", "plotter", "fig_scatter.png\nfig_change.png", "#fdf9f4", "#c77b2f"),
    ("⑤ 요약\n(14주차로)", "본 에이전트", "summary.md\n(결과 요약)", "#f7f7fc", "#5b6ee1"),
]
for i, (t1, who, out, fc, ec) in enumerate(stages):
    x = 0.4 + i * 2.75
    box(ax, x, 4.6, 2.2, 1.5, t1, fc=fc, ec=ec, weight="bold")
    box(ax, x, 3.3, 2.2, 0.9, "담당: " + who, fc="white", ec=ec)
    box(ax, x, 1.75, 2.2, 1.2, out, fc="white", ec="#aaa")
    if i < 4:
        arrow(ax, x + 2.3, 5.35, x + 2.65, 5.35)
        cx = x + 2.475
        ax.plot([cx], [6.45], marker="v", color="#a04747", markersize=9)
        ax.text(cx, 6.8, f"검증 지점 {i + 1}", ha="center", fontsize=9.5,
                color="#a04747", fontweight="bold")
checks = ["행 수·열·결측", "행 수·빈 값·대응표", "관측치 수·대표 수치", "점 개수·축·단위"]
for i, c in enumerate(checks):
    cx = 0.4 + i * 2.75 + 2.475
    ax.text(cx, 7.35, c, ha="center", fontsize=8.8, color="#a04747")
ax.text(7.0, 1.0, "단계 사이의 전달은 산출물/파이프라인 폴더의 파일로 하고, 검증 지점에서 사람이 통과·반려를 정한다",
        ha="center", fontsize=10.5, color="#333")
fig.savefig(FIG / "fig13_pipeline_checkpoints.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 13-2
# 검증 지점의 1차 확인(verifier)과 2차 확인(사람)
fig, ax = plt.subplots(figsize=(12.5, 5.6))
ax.set_xlim(0, 14)
ax.set_ylim(1.4, 8.0)
ax.axis("off")
box(ax, 0.3, 3.6, 2.6, 2.2, "② 단계 산출물\nmerged.csv", fc="#f5f9fd", ec="#2f6fb0")
box(ax, 3.6, 2.6, 7.2, 5.2, "", fc="white", ec="#c0392b")
ax.text(7.2, 7.35, "검증 지점 2", ha="center", fontsize=12, fontweight="bold", color="#c0392b")
box(ax, 3.85, 3.3, 3.3, 3.5,
    "1차 확인: verifier\n별도 맥락창\n원자료와 산출물만 받음\n행 수·지정 항목 재계산\n→ 대조표",
    fc="#f4fbf6", ec="#2f8f4e")
box(ax, 7.45, 3.3, 3.2, 3.5,
    "2차 확인: 사람\n대조표의 결정적 항목\n대응표 판단의 근거\n→ 통과 또는 반려",
    fc="#fdf9f4", ec="#c77b2f")
arrow(ax, 3.0, 4.7, 3.75, 5.3)
arrow(ax, 7.2, 5.3, 7.35, 5.3)
box(ax, 11.4, 5.5, 2.2, 1.3, "통과\n→ ③ 분석", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 11.4, 2.8, 2.2, 1.3, "반려\n→ ② 재실행", fc="#fdf9f4", ec="#c0392b")
arrow(ax, 10.7, 6.0, 11.3, 6.1, color="#2f8f4e")
arrow(ax, 10.7, 4.8, 11.3, 3.6, color="#c0392b")
ax.text(7.2, 1.75, "값을 다시 세는 일은 verifier가, 통과·반려의 결정은 사람이 맡는다",
        ha="center", fontsize=10, color="#333")
fig.savefig(FIG / "fig13_verifier_gate.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved: fig13_pipeline_checkpoints.png, fig13_verifier_gate.png")
