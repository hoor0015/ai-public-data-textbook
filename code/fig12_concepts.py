# 12주차 1회차 개념도 생성
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


# ---------------------------------------------------------------- 그림 12-1
# 그라운딩 유무 비교: 기억에서 답하기 vs 문서에서 답하기
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))
for ax in axes:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

ax = axes[0]
ax.set_title("(가) 그라운딩 없음: 기억에서 답한다", fontsize=13, pad=12)
box(ax, 0.5, 7.6, 4.2, 1.7, "질문\n\"공공데이터법의\n제공 원칙은?\"", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 5.6, 7.6, 4.0, 1.7, "모델의 기억\n(학습데이터의 패턴)", fc="#eeeeee", ec="#888888", fontsize=10)
arrow(ax, 4.8, 8.45, 5.5, 8.45)
box(ax, 2.6, 4.2, 5.2, 1.9, "답변\n그럴듯한 요약\n(조문 번호가 틀려도 모른다)", fc="white", ec="#c0392b", fontsize=10)
arrow(ax, 7.4, 7.5, 6.0, 6.2, color="#888888")
ax.text(5.0, 2.4, "근거 확인 불가. 환각이 섞여도\n답변만 보고는 가려낼 수 없다.",
        ha="center", fontsize=10.5, color="#c0392b")

ax = axes[1]
ax.set_title("(나) 그라운딩 있음: 문서에서 답한다", fontsize=13, pad=12)
box(ax, 0.4, 7.6, 3.6, 1.7, "질문 + 문서\n\"이 법률 파일에서\n찾아 답해 줘\"", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 5.8, 7.6, 3.8, 1.7, "문서 읽기\n(법률 전문이\n맥락창에 들어간다)", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
arrow(ax, 4.2, 8.45, 5.7, 8.45)
box(ax, 2.4, 4.2, 5.6, 2.1, "답변 + 인용\n\"제17조 제1항에 따라 ...\"\n(근거 조문을 함께 제시)", fc="white", ec="#2f8f4e", fontsize=10)
arrow(ax, 7.6, 7.5, 6.2, 6.4, color="#2f8f4e")
ax.text(5.1, 2.4, "인용된 조문을 원문과 대조하면\n답이 맞는지 사람이 검증할 수 있다.",
        ha="center", fontsize=10.5, color="#1e6b3a")
fig.tight_layout()
fig.savefig(FIG / "fig12_grounding.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 12-2
# RAG의 세 단계: 검색, 증강, 생성
fig, ax = plt.subplots(figsize=(12.5, 5.6))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")

box(ax, 0.4, 5.6, 2.8, 2.0, "질문\n\"주차장 사용료\n감면 규정은?\"", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 4.2, 5.4, 3.0, 2.4, "① 검색\n서고에서 질문과\n관련된 조각을\n찾아낸다", fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
box(ax, 8.0, 5.6, 2.6, 2.0, "② 증강\n질문 + 찾은 조각을\n함께 모델에 전달", fc="#faf8fc", ec="#7a5fa8", fontsize=10)
box(ax, 11.2, 5.5, 2.5, 2.2, "③ 생성\n답변 + 인용\n(어느 문서\n어느 부분인지)", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
arrow(ax, 3.3, 6.6, 4.1, 6.6)
arrow(ax, 7.3, 6.6, 7.9, 6.6)
arrow(ax, 10.7, 6.6, 11.1, 6.6)

# 아래: 문서 저장소(서고)
box(ax, 3.6, 1.2, 4.2, 2.6, "", fc="white", ec="#2f6fb0")
ax.text(5.7, 3.35, "문서 저장소 (서고)", ha="center", fontsize=10.5, fontweight="bold", color="#2f6fb0")
for i, t in enumerate(["조례집", "지침서", "매뉴얼", "회의록"]):
    box(ax, 3.85 + i * 0.95, 1.55, 0.85, 1.3, t, fc="#f5f9fd", ec="#9db8d2", fontsize=8.5)
ax.text(5.7, 0.6, "수백·수천 건: 맥락창(책상)에 다 올릴 수 없다", ha="center", fontsize=9.5, color="#555")
arrow(ax, 5.7, 3.9, 5.5, 5.3, color="#2f6fb0")
arrow(ax, 5.9, 5.3, 6.1, 3.95, color="#2f6fb0", ls="--")
ax.text(6.9, 4.6, "관련 조각만\n추출", ha="center", fontsize=9, color="#2f6fb0")

ax.text(10.6, 2.4, "서고 전체를 읽지 않는다.\n질문마다 관련 조각만 찾아\n책상(맥락창)에 올린다.",
        ha="center", fontsize=10.5, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig12_rag.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 12-3
# 근거의 삼각대: 문서(그라운딩), 데이터(MCP), 절차(Skill)
fig, ax = plt.subplots(figsize=(11.5, 5.8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")

box(ax, 4.0, 6.5, 6.0, 1.9, "보고서의 주장\n\"고령화가 빠르므로 대응이 필요하다\"",
    fc="white", ec="#c0392b", fontsize=11, weight="bold")

legs = [
    (0.7, "문서 근거", "#2f6fb0", "#f5f9fd", "법령·지침의 조문 인용\n(그라운딩, 12주차)\n검증: 원문과 대조"),
    (5.15, "데이터 근거", "#2f8f4e", "#f4fbf6", "통계 수치와 출처\n(kosis MCP, 6주차)\n검증: 포털 화면과 대조"),
    (9.6, "절차 근거", "#7a5fa8", "#faf8fc", "만든 과정의 기록\n(Skill·수집기록, 5-6주차)\n검증: 같은 절차로 재현"),
]
for x, title, ec, fc, body in legs:
    ax.text(x + 1.85, 3.85, title, ha="center", fontsize=11.5, fontweight="bold", color=ec)
    box(ax, x, 1.0, 3.7, 2.5, body, fc=fc, ec=ec, fontsize=9.5)
    ax.plot([7.0, x + 1.85], [6.5, 3.6], color="#999", lw=1.4)

ax.text(12.4, 7.4, "다리 하나가 빠지면\n주장은 기울어진다",
        ha="center", fontsize=10, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))
fig.savefig(FIG / "fig12_triangle.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig12_*.png'))])
