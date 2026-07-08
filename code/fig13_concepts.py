# 13주차 개념도 생성
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

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
# 보고서 구조 피라미드: 한 쪽 요약 - 본문 - 부록
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

# 피라미드 세 층 (사다리꼴)
layers = [
    # (아래왼x, 아래오른x, 밑y, 높이, 라벨, fc, ec)
    (4.4, 7.4, 6.0, 2.2, "한 쪽 요약\n(결론과 제언)", "#fdf9f4", "#c77b2f"),
    (3.3, 8.5, 3.4, 2.2, "본문\n배경 · 데이터와 방법 · 발견 · 제언", "#f5f9fd", "#2f6fb0"),
    (2.2, 9.6, 0.8, 2.2, "부록\n상세 표 · 코드 · 데이터 출처 · AI 활용 내역", "#f4fbf6", "#2f8f4e"),
]
for bl, br, yb, h, label, fc, ec in layers:
    top_indent = 0.55
    ax.add_patch(Polygon([(bl, yb), (br, yb), (br - top_indent, yb + h), (bl + top_indent, yb + h)],
                         closed=True, fc=fc, ec=ec, lw=1.6))
    ax.text((bl + br) / 2, yb + h / 2, label, ha="center", va="center", fontsize=11)

# 오른쪽: 읽는 사람과 시간
readers = [
    (7.2, "의사결정자: 이것만 읽는다 (1분)", "#c77b2f"),
    (4.5, "담당자: 근거를 따라 읽는다 (30분)", "#2f6fb0"),
    (1.9, "검증하는 사람: 필요할 때 찾아본다", "#2f8f4e"),
]
for y, text, color in readers:
    ax.text(9.9, y, text, fontsize=10.5, color=color, va="center")

ax.text(1.6, 4.5, "위로 갈수록\n짧아지고\n결론에 가깝다", fontsize=10.5, color="#555",
        ha="center", va="center")
arrow(ax, 0.6, 2.6, 0.6, 6.3, color="#999")
ax.set_title("보고서는 피라미드다: 층마다 읽는 사람이 다르다", fontsize=13, pad=10)
fig.tight_layout()
fig.savefig(FIG / "fig13_report_pyramid.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 13-2
# 삼중 대조: 숫자 - 인용 - 그림
fig, ax = plt.subplots(figsize=(11, 6.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 10)
ax.axis("off")

# 가운데: 보고서 본문
box(ax, 4.5, 4.1, 4.0, 1.9, "보고서 본문의 서술\n(제출 직전의 원고)", fc="#f7f7fc", ec="#5b6ee1",
    fontsize=11.5, weight="bold")

# 대조 1: 숫자 (왼쪽 위)
box(ax, 0.5, 7.6, 3.6, 1.7, "대조 1 · 숫자\n본문의 숫자 =\n데이터에서 다시 계산한 값?", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 0.5, 5.4, 3.6, 1.3, "원본 데이터 (CSV)", fc="white", ec="#c77b2f", fontsize=10)
arrow(ax, 2.3, 7.5, 2.3, 6.9, color="#c77b2f")
arrow(ax, 4.2, 6.3, 5.0, 5.9, color="#c77b2f")

# 대조 2: 인용 (오른쪽 위)
box(ax, 8.9, 7.6, 3.6, 1.7, "대조 2 · 인용\n본문의 인용문 =\n원문의 문장 그대로?", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
box(ax, 8.9, 5.4, 3.6, 1.3, "원문 문서 (법령·보고서)", fc="white", ec="#2f8f4e", fontsize=10)
arrow(ax, 10.7, 7.5, 10.7, 6.9, color="#2f8f4e")
arrow(ax, 8.8, 6.3, 8.0, 5.9, color="#2f8f4e")

# 대조 3: 그림 (아래)
box(ax, 4.7, 0.6, 3.6, 1.7, "대조 3 · 그림\n그림이 보여 주는 것 =\n본문이 말하는 것?", fc="#faf8fc", ec="#7a5fa8", fontsize=10)
box(ax, 9.0, 0.8, 3.4, 1.3, "그림 파일 (PNG)", fc="white", ec="#7a5fa8", fontsize=10)
arrow(ax, 8.9, 1.45, 8.4, 1.45, color="#7a5fa8")
arrow(ax, 6.5, 2.4, 6.5, 4.0, color="#7a5fa8")

ax.text(6.5, 9.4, "세 대조를 모두 통과해야 보고서에 내 이름을 걸 수 있다",
        ha="center", fontsize=12, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.4"))
fig.tight_layout()
fig.savefig(FIG / "fig13_triple_check.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 13-3
# 재현 패키지 구성도
fig, ax = plt.subplots(figsize=(11, 5.8))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

box(ax, 0.5, 3.3, 3.3, 2.2, "재현 패키지\n(제출 폴더 하나)", fc="#f7f7fc", ec="#5b6ee1",
    fontsize=12, weight="bold")

items = [
    (7.2, "data/  원본 데이터 + 출처 기록", "이 숫자는 어디서 왔는가", "#2f6fb0", "#f5f9fd"),
    (5.4, "code/  분석 코드 (pyproject.toml 포함)", "같은 환경에서 다시 돌릴 수 있는가", "#2f8f4e", "#f4fbf6"),
    (3.6, "prompts.md  주요 지시문 기록", "에이전트에게 무엇을 시켰는가", "#c77b2f", "#fdf9f4"),
    (1.8, "report.md + figures/  보고서와 그림", "최종 산출물", "#7a5fa8", "#faf8fc"),
    (0.2, "README.md  재현 순서 안내", "처음 보는 사람이 어디부터 여는가", "#555555", "#f5f5f5"),
]
for y, label, note, ec, fc in items:
    box(ax, 4.9, y, 4.6, 1.3, label, fc=fc, ec=ec, fontsize=10)
    ax.text(9.9, y + 0.65, note, fontsize=9.5, color=ec, va="center")
    arrow(ax, 3.9, 4.4, 4.8, y + 0.65, color=ec, lw=1.2)

ax.text(2.15, 1.4, "검증 기준:\n남이 이 폴더만 받아서\n같은 보고서를 만들 수 있는가",
        ha="center", fontsize=10.5, color="#333",
        bbox=dict(fc="white", ec="#d9d9e3", boxstyle="round,pad=0.4"))
ax.set_title("재현 패키지: 보고서 한 편이 아니라 분석 전체를 제출한다", fontsize=13, pad=10)
fig.tight_layout()
fig.savefig(FIG / "fig13_repro_package.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig13_*.png'))])
