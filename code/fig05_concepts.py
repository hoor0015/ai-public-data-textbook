# 5주차 1회차 개념도 생성
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


# ---------------------------------------------------------------- 그림 5-1
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
fig.savefig(FIG / "fig05_ecosystem.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 5-2
# 파일 내려받기와 오픈API의 차이
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for ax in axes:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

ax = axes[0]
ax.set_title("(가) 파일 내려받기: 사람이 옮긴다", fontsize=13, pad=12)
box(ax, 0.6, 6.6, 3.6, 2.0, "포털 화면\n(검색·클릭)", fc="#f5f9fd", ec="#2f6fb0")
box(ax, 5.8, 6.6, 3.6, 2.0, "내 컴퓨터\nCSV / XLSX 파일", fc="#fdf9f4", ec="#c77b2f")
box(ax, 3.2, 2.6, 3.6, 2.0, "분석\n(pandas로 읽기)", fc="#f4fbf6", ec="#2f8f4e")
arrow(ax, 4.4, 7.6, 5.6, 7.6)
arrow(ax, 7.6, 6.5, 5.6, 4.7)
ax.text(5.0, 9.3, "내려받기(수동)", ha="center", fontsize=10, color="#555")
ax.text(5.0, 0.9, "받은 순간의 스냅사진: 데이터가 갱신되면 다시 내려받아야 한다",
        ha="center", fontsize=10, color="#333")

ax = axes[1]
ax.set_title("(나) 오픈API: 코드가 가져온다", fontsize=13, pad=12)
box(ax, 0.6, 6.6, 3.6, 2.0, "분석 코드\n(에이전트가 작성)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 5.8, 6.6, 3.6, 2.0, "포털 서버\n(API 창구)", fc="#f5f9fd", ec="#2f6fb0")
box(ax, 3.2, 2.6, 3.6, 2.0, "응답 데이터\n(JSON)", fc="#faf8fc", ec="#7a5fa8")
arrow(ax, 4.4, 7.9, 5.6, 7.9)
arrow(ax, 7.6, 6.5, 5.6, 4.7)
arrow(ax, 3.4, 3.6, 1.6, 6.4, ls="--", color="#999", lw=1.2)
ax.text(5.0, 9.3, "요청(인증키 포함)", ha="center", fontsize=10, color="#555")
ax.text(7.4, 5.4, "응답", ha="center", fontsize=10, color="#555")
ax.text(1.7, 4.9, "코드 재실행 =\n최신 데이터", ha="center", fontsize=9.5, color="#777")
ax.text(5.0, 0.9, "실행할 때마다 자동으로 다시 가져온다: 6주차에서 직접 만든다",
        ha="center", fontsize=10, color="#333")
fig.tight_layout()
fig.savefig(FIG / "fig05_file_vs_api.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig05_*.png'))])
