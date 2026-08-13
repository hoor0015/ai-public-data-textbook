# 6주차 1회차 개념도 생성 (공공데이터 생태계 지도, MCP 개념도)
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


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 6-1
# 한국 공공데이터 생태계 지도: 포털들을 성격별로 배치
fig, ax = plt.subplots(figsize=(12, 6.4))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

# 맨 위: 분석가의 질문
box(ax, 4.4, 7.6, 4.2, 1.1, "분석가의 질문\n\"이 데이터는 어디에 있을까?\"",
    fc="#fdf9f4", ec="#c77b2f", fontsize=11, weight="bold")

# 가운데: 종합 창구
box(ax, 4.4, 5.2, 4.2, 1.5,
    "공공데이터포털  data.go.kr\n(행정안전부 · 범정부 종합 창구)\n파일데이터 + 오픈API",
    fc="#f5f9fd", ec="#2f6fb0", fontsize=10.5, weight="bold")
arrow(ax, 6.5, 7.5, 6.5, 6.9)

# 아래: 성격별 전문 포털 4묶음
groups = [
    ("통계 전문", "#f4fbf6", "#2f8f4e",
     "KOSIS 국가통계포털\nkosis.kr (국가데이터처)\n인구·고용·물가 등 승인통계",
     "한국은행 ECOS\necos.bok.or.kr\n금리·환율·국민소득"),
    ("재정·기관 정보", "#faf8fc", "#7a5fa8",
     "지방재정365\nlofin365.go.kr\n지자체 예산·재정자립도",
     "ALIO 경영정보 공개\nalio.go.kr\n공공기관 인력·부채"),
    ("법령·행정문서", "#fdf9f4", "#c77b2f",
     "국가법령정보센터\nlaw.go.kr (법제처)\n법령·판례·자치법규",
     "정보공개포털\nopen.go.kr\n정보공개 청구·원문"),
]
x0 = 0.5
for i, (title, fc, ec, top, bottom) in enumerate(groups):
    x = x0 + i * 4.2
    ax.text(x + 1.9, 4.35, title, ha="center", fontsize=11.5,
            fontweight="bold", color=ec)
    box(ax, x, 2.3, 3.8, 1.6, top, fc=fc, ec=ec, fontsize=9.5)
    box(ax, x, 0.4, 3.8, 1.6, bottom, fc=fc, ec=ec, fontsize=9.5)
    arrow(ax, 6.5, 5.1, x + 1.9, 4.7, color="#999", ls="--", lw=1.2)

ax.text(11.2, 6.0, "종합 창구에서 시작하되,\n주제가 분명하면\n전문 포털로 바로 간다",
        ha="center", fontsize=10, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig06_ecosystem.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 6-2
# MCP 개념도: 에이전트와 외부 시스템을 잇는 공통 규격
fig, ax = plt.subplots(figsize=(11, 5.0))
ax.set_xlim(0, 13)
ax.set_ylim(0, 8)
ax.axis("off")
box(ax, 0.5, 3.0, 3.0, 2.2, "에이전트\n(Claude Code)", fc="#f5f9fd", ec="#2f6fb0", weight="bold")
box(ax, 4.6, 3.2, 2.6, 1.8, "MCP\n(공통 규격)", fc="#f4fbf6", ec="#2f8f4e", weight="bold")
arrow(ax, 3.6, 4.1, 4.5, 4.1)
arrow(ax, 4.5, 3.7, 3.6, 3.7)
ext = [
    ("통계 데이터베이스\n(KOSIS 등)", 6.6), ("업무 시스템\n(일정·문서)", 4.45), ("외부 서비스\n(메일·저장소 등)", 2.3),
]
for t, yy in ext:
    box(ax, 9.3, yy - 0.75, 3.2, 1.5, t, fc="#fdf9f4", ec="#c77b2f", fontsize=10)
    arrow(ax, 7.3, 4.1, 9.2, yy, color="#2f8f4e")
ax.text(4.4, 0.7, "MCP가 없으면 시스템마다 연결 방식을 따로 만들어야 한다.\n"
                  "MCP는 콘센트 규격처럼, 규격만 맞으면 어떤 기기든 꽂아 쓸 수 있게 한다.",
        ha="center", fontsize=10.5, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig06_mcp.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig06_*.png'))])
