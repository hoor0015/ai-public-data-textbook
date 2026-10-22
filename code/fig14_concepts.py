# 14주차 1차시(통합 장) 개념도 생성: 그림 14-1(보고서 세 층), 그림 14-2(근거 사슬),
# 그림 14-3(verifier의 삼중 대조와 사람의 2차 확인)
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 code/fig14_concepts.py
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

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


# ---------------------------------------------------------------- 그림 14-1
# 보고서의 세 층: 한 쪽 요약 - 본문 - 부록
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

layers = [
    (4.4, 7.4, 6.0, 2.2, "한 쪽 요약\n(결론과 제언)", "#fdf9f4", "#c77b2f"),
    (3.3, 8.5, 3.4, 2.2, "본문\n배경 · 데이터와 방법 · 발견 · 제언", "#f5f9fd", "#2f6fb0"),
    (2.2, 9.6, 0.8, 2.2, "부록\n상세 표 · 코드 · 데이터 출처 · AI 활용 내역", "#f4fbf6", "#2f8f4e"),
]
for bl, br, yb, h, label, fc, ec in layers:
    top_indent = 0.55
    ax.add_patch(Polygon([(bl, yb), (br, yb), (br - top_indent, yb + h), (bl + top_indent, yb + h)],
                         closed=True, fc=fc, ec=ec, lw=1.6))
    ax.text((bl + br) / 2, yb + h / 2, label, ha="center", va="center", fontsize=11)

readers = [
    (7.2, "의사결정자: 이것만 읽는다", "#c77b2f"),
    (4.5, "담당자: 근거를 따라 읽는다", "#2f6fb0"),
    (1.9, "검증하는 사람: 필요할 때 찾아본다", "#2f8f4e"),
]
for y, text, color in readers:
    ax.text(9.9, y, text, fontsize=10.5, color=color, va="center")

ax.text(1.6, 4.5, "위로 갈수록\n짧아지고\n결론에 가깝다", fontsize=10.5, color="#555",
        ha="center", va="center")
arrow(ax, 0.6, 2.6, 0.6, 6.3, color="#999")
ax.set_title("보고서의 세 층: 층마다 읽는 사람이 다르다", fontsize=13, pad=10)
fig.tight_layout()
fig.savefig(FIG / "fig14_report_pyramid.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 14-2
# 근거 경로: 원자료 -> 결과 파일 -> 본문 문장 -> 요약·제언 (수치는 code/ch14_practice.py 출력)
fig, ax = plt.subplots(figsize=(11.5, 5.4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.6)
ax.axis("off")

chain = [
    (0.4, "원자료\ndata/sigungu_mcp_2023.csv", "229개 시군구의\n고령인구비율 값", "#c77b2f", "#fdf9f4"),
    (3.9, "결과 파일\n산출물/파이프라인/", "수도권 평균 18.58%\n비수도권 평균 27.82%", "#2f6fb0", "#f5f9fd"),
    (7.4, "본문 문장\nreport.md 발견", "비수도권의 고령인구비율이\n9.24%포인트 높았다", "#2f8f4e", "#f4fbf6"),
    (10.9, "요약·제언\nreport.md 요약, 제언", "제언 1의 근거:\n발견 1", "#7a5fa8", "#faf8fc"),
]
for x, title, example, ec, fc in chain:
    box(ax, x, 4.3, 2.8, 1.7, title, fc=fc, ec=ec, fontsize=10.5, weight="bold")
    box(ax, x, 2.2, 2.8, 1.5, example, fc="white", ec=ec, fontsize=9.5)
    arrow(ax, x + 1.4, 4.2, x + 1.4, 3.8, color=ec, lw=1.2)

for x in (3.2, 6.7, 10.2):
    arrow(ax, x + 0.05, 5.5, x + 0.65, 5.5, color="#333", lw=1.8)
arrow(ax, 13.6, 1.5, 0.5, 1.5, color="#b03a2e", lw=1.8, ls="--")
for x, _, _, ec, _ in chain:
    arrow(ax, x + 1.4, 2.1, x + 1.4, 1.6, color=ec, lw=1.0, style="-")

ax.text(7.0, 6.6, "작성 방향: 원자료의 값이 결과 파일을 거쳐 문장과 제언으로 옮겨진다",
        ha="center", fontsize=11, color="#333")
ax.text(7.0, 0.5, "대조 방향: 문장과 제언의 숫자를 결과 파일이 아니라 원자료까지 거슬러 올라가 다시 계산한다",
        ha="center", fontsize=11, color="#b03a2e")
ax.text(7.0, 7.9, "근거 경로: 보고서의 모든 문장은 파일 하나까지 되짚어 갈 수 있어야 한다",
        ha="center", fontsize=13)
fig.tight_layout()
fig.savefig(FIG / "fig14_evidence_chain.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 14-3
# verifier 서브에이전트의 삼중 대조와 사람의 2차 확인
fig, ax = plt.subplots(figsize=(13, 6.6))
ax.set_xlim(0, 15.6)
ax.set_ylim(0, 10)
ax.axis("off")

# 왼쪽: 보고서 초안
box(ax, 0.3, 4.1, 2.5, 1.9, "보고서 초안\nreport.md", fc="#f7f7fc", ec="#5b6ee1", weight="bold")

# 가운데: verifier
box(ax, 3.6, 7.7, 5.6, 1.3, "verifier 서브에이전트\n보고서와 원본만 받아 별도 맥락창에서 대조",
    fc="#eef1fb", ec="#5b6ee1", weight="bold")
rows = [
    (5.6, "대조 1 · 숫자\n원자료에서 다시 계산", "data/sigungu_mcp_2023.csv\ndata/sigungu_mcp_tfr_2013.csv", "#c77b2f", "#fdf9f4"),
    (3.6, "대조 2 · 인용\n원문에서 다시 찾기", "수집기록, 근거 메모의\n원문 파일", "#2f8f4e", "#f4fbf6"),
    (1.6, "대조 3 · 그림\n주장과 그림 목록 정리", "그림 파일(PNG)\n제목 · 축 · 연도", "#7a5fa8", "#faf8fc"),
]
for y, check, src, ec, fc in rows:
    box(ax, 3.6, y, 2.7, 1.4, check, fc=fc, ec=ec)
    box(ax, 6.6, y, 2.6, 1.4, src, fc="white", ec=ec)
    arrow(ax, 6.55, y + 0.7, 6.4, y + 0.7, color=ec, style="-")
    arrow(ax, 2.9, 5.05, 3.5, y + 0.7, color="#5b6ee1", lw=1.2)
    arrow(ax, 9.3, y + 0.7, 9.9, 5.05, color=ec, lw=1.2)

# 대조표
box(ax, 10.0, 4.2, 2.1, 1.7, "대조표\ncheck_report.md", fc="white", ec="#333", weight="bold")
arrow(ax, 12.2, 5.05, 12.7, 5.05, color="#333")

# 사람의 2차 확인
box(ax, 12.8, 3.95, 2.6, 2.2, "사람의 2차 확인\n불일치 · 확인 불가 행 판정\n재계산이 원자료에서 왔는가\n그림이 주장을 보여 주는가",
    fc="#fdf2f0", ec="#b03a2e", weight="bold")

# 수정 화살표: 사람 -> 보고서
arrow(ax, 14.1, 3.85, 14.1, 0.5, color="#b03a2e", style="-", lw=1.6, ls="--")
arrow(ax, 14.1, 0.5, 1.55, 0.5, color="#b03a2e", style="-", lw=1.6, ls="--")
arrow(ax, 1.55, 0.5, 1.55, 4.0, color="#b03a2e", lw=1.6, ls="--")
ax.text(7.8, 0.75, "판정에 따라 보고서를 고친다", ha="center", fontsize=10.5, color="#b03a2e")

ax.set_title("삼중 대조: 대조는 verifier에게 맡기고 판정은 사람이 한다", fontsize=13, pad=10)
fig.tight_layout()
fig.savefig(FIG / "fig14_verifier_triple.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved: fig14_report_pyramid.png, fig14_evidence_chain.png, fig14_verifier_triple.png")
