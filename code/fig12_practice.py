# 12주차 2회차(실습) 그림 생성
#   그림 12-4 fig12_cite_check.png    인용 검증표의 세 열과 세 가지 판정
#   그림 12-5 fig12_evidence_skill.png evidence-memo 스킬의 구성과 실행 흐름
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


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 12-4
figfit.SPREAD = 1.0          # 표 모양이므로 칸 사이 글씨 크기를 고르게 맞춘다
fig, ax = plt.subplots(figsize=(12.6, 6.6))
ax.set_xlim(0, 12.6)
ax.set_ylim(0.2, 7.2)
ax.axis("off")

XS = [0.2, 3.6, 6.6, 10.0]          # 열 왼쪽 좌표
WS = [3.2, 2.8, 3.2, 2.4]           # 열 너비
HEAD = ["답변의 주장", "에이전트가 적은\n근거 위치", "내가 원문에서\n확인한 결과", "판정"]
ROWS = [
    ["영리 목적을 이유로\n제한할 수 없다", "공공데이터법.txt\n제3조 제4항",
     "그 자리에 같은 문장이\n글자까지 그대로 있다", "일치"],
    ["공공데이터란\n이러이러한 자료다", "공공데이터법.txt\n제2조 제3호",
     "정의는 제2조 제2호에\n있다. 호 번호가 다르다", "위치 어긋남"],
    ["별도의 승인 절차를\n거쳐야 한다", "(근거 표시 없음)",
     "이 문장을 원문에서\n찾지 못했다", "원문에 없음"],
]
VERDICT_FC = ["#f4fbf6", "#fdf9f4", "#fbf1f0"]
VERDICT_EC = ["#2f8f4e", "#c77b2f", "#c0392b"]

y_head, h_head = 5.20, 0.95
for x, w, t in zip(XS, WS, HEAD):
    box(ax, x, y_head, w, h_head, t, fc="#f7f7fc", ec="#5b6ee1", weight="bold")

for i, row in enumerate(ROWS):
    y = 3.95 - i * 1.15
    for j, (x, w, t) in enumerate(zip(XS, WS, row)):
        if j == 3:
            box(ax, x, y, w, 0.95, t, fc=VERDICT_FC[i], ec=VERDICT_EC[i], weight="bold")
        elif j == 2:
            box(ax, x, y, w, 0.95, t, fc="#eeeeee", ec="#888888")
        else:
            box(ax, x, y, w, 0.95, t, fc="#f5f9fd", ec="#2f6fb0")

# 열의 주체 표시 (표 위쪽)
ax.annotate("", xy=(6.4, 6.42), xytext=(0.2, 6.42),
            arrowprops=dict(arrowstyle="-", color="#2f6fb0", lw=1.2))
ax.text(3.3, 6.52, "에이전트가 적는 두 열", ha="center", va="bottom",
        fontsize=11, color="#2f6fb0")
ax.annotate("", xy=(12.4, 6.42), xytext=(6.6, 6.42),
            arrowprops=dict(arrowstyle="-", color="#666666", lw=1.2))
ax.text(9.5, 6.52, "사람만 쓸 수 있는 두 열", ha="center", va="bottom",
        fontsize=11, color="#666666")

ax.text(6.3, 0.72,
        "판정이 '일치'가 아닌 줄이 하나라도 있으면 그 줄을 근거로 재지시한다. "
        "'원문에 없음'은 그 주장을 메모에서 빼는 사유가 된다.",
        ha="center", va="center", fontsize=11, color="#333",
        bbox=dict(fc="#fdf9f4", ec="#ecd9c6", boxstyle="round,pad=0.5"))

fig.savefig(FIG / "fig12_cite_check.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved:", FIG / "fig12_cite_check.png")


# ---------------------------------------------------------------- 그림 12-5
figfit.SPREAD = 1.15         # 기본값으로 되돌린다
fig, ax = plt.subplots(figsize=(13, 5.6))
ax.set_xlim(0, 14)
ax.set_ylim(1.9, 9)
ax.axis("off")

# 호출과 SKILL.md
box(ax, 0.3, 6.3, 3.0, 1.9,
    "호출 (인자 세 개. 질문은 따옴표로)\n/evidence-memo data/laws 인구감소\n"
    '"우리나라 인구는 감소 추세인가"',
    fc="#fdf9f4", ec="#c77b2f")
box(ax, 4.0, 6.4, 3.0, 1.7, "SKILL.md\n절차 10단계\n(\\$docs, \\$topic, \\$question)",
    fc="#f5f9fd", ec="#2f6fb0", weight="bold")
arrow(ax, 3.3, 7.25, 4.0, 7.25)

# 보조 파일 (필요할 때만 읽힘)
box(ax, 3.4, 3.4, 2.1, 1.7, "reference.md\n근거 표기 규칙\n(필요할 때만 읽힘)",
    fc="#faf8fc", ec="#7a5fa8")
box(ax, 5.7, 3.4, 2.3, 1.7, "scripts/cite_check.py\n인용을 원문에서\n다시 찾아 대조",
    fc="#faf8fc", ec="#7a5fa8")
arrow(ax, 5.0, 6.3, 4.6, 5.1, color="#7a5fa8", ls="--")
arrow(ax, 6.0, 6.3, 6.6, 5.1, color="#7a5fa8")

# 근거의 원천
box(ax, 8.0, 7.35, 2.6, 1.35, "data/laws/ 파일 읽기\n(문서 근거)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 8.0, 5.45, 2.6, 1.35, "kosis MCP로 통계 조회\n(데이터 근거)", fc="#f4fbf6", ec="#2f8f4e")
arrow(ax, 7.0, 7.5, 8.0, 8.0)
arrow(ax, 7.0, 7.0, 8.0, 6.1)

# 산출물
box(ax, 11.2, 6.0, 2.5, 2.3, "reports/\n근거메모_인구감소.md\n일곱 절 고정 양식",
    fc="white", ec="#c0392b")
arrow(ax, 10.6, 8.0, 11.2, 7.5)
arrow(ax, 10.6, 6.1, 11.2, 6.7)
arrow(ax, 8.0, 4.25, 11.3, 6.0, color="#7a5fa8", ls="--")
ax.text(9.9, 4.55, "검산 결과를\n7절에 붙임", ha="center", fontsize=9, color="#7a5fa8")

# 사람의 확인
box(ax, 10.6, 2.5, 3.0, 1.6, "사람의 확인 (마지막 겹)\n인용 1건을 원문과 대조\n수치 1건을 포털과 대조",
    fc="#eeeeee", ec="#888888")
arrow(ax, 12.45, 6.0, 12.1, 4.1, color="#888888")

# 범례
ax.text(1.75, 4.25,
        "삼각대가 한 스킬 안에 있다\n문서 근거: data/laws 읽기\n데이터 근거: kosis MCP\n"
        "절차 근거: SKILL.md, reference.md,\nscripts, 7절의 검산 기록",
        ha="center", va="center", fontsize=9.8, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))

fig.savefig(FIG / "fig12_evidence_skill.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved:", FIG / "fig12_evidence_skill.png")
