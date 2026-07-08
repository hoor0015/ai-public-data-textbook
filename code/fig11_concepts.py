# 11주차 1회차 개념도 생성
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
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


# ---------------------------------------------------------------- 그림 11-1
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
fig.savefig(FIG / "fig11_grounding.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 11-2
# 일회성 지시, Skill, CLAUDE.md의 3층 구조
fig, ax = plt.subplots(figsize=(11, 5.8))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

layers = [
    (6.3, "일회성 지시 (대화창)", "이번 한 번만 필요한 요청",
     "\"이 표를 오름차순으로 다시 정렬해 줘\"", "#fdf9f4", "#c77b2f"),
    (3.5, "Skill (.claude/skills/이름/SKILL.md)", "부르면 실행되는 절차. 필요할 때만 본문이 로드된다",
     "\"/csv-profile data/민원.csv\" 또는 관련 요청 시 자동 사용", "#f4fbf6", "#2f8f4e"),
    (0.7, "CLAUDE.md (프로젝트 규칙)", "항상 적용되는 규칙. 매 대화에 자동으로 로드된다",
     "\"표의 숫자는 천 단위 쉼표\", \"그림은 figures 폴더에 저장\"", "#f5f9fd", "#2f6fb0"),
]
for y, t1, t2, ex, fc, ec in layers:
    box(ax, 0.6, y, 7.6, 2.2, "", fc=fc, ec=ec)
    ax.text(4.4, y + 1.72, t1, ha="center", fontsize=12, fontweight="bold")
    ax.text(4.4, y + 1.12, t2, ha="center", fontsize=10, color="#333")
    ax.text(4.4, y + 0.48, "예: " + ex, ha="center", fontsize=9.5, color="#555")

ax.annotate("", xy=(9.2, 8.4), xytext=(9.2, 0.8),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.6))
ax.text(9.55, 4.6, "위로 갈수록\n일회적·즉흥적", fontsize=10.5, color="#555", va="center")
ax.text(11.5, 4.6, "아래로 갈수록\n반복적·영구적", fontsize=10.5, color="#555", va="center")
ax.annotate("", xy=(11.2, 0.8), xytext=(11.2, 8.4),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.6))
ax.text(4.4, 8.75, "같은 지시를 세 번째 쓰고 있다면 아래층으로 내릴 때다",
        ha="center", fontsize=11, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.4"))
fig.savefig(FIG / "fig11_three_layers.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 11-3
# Skill 작동 흐름
fig, ax = plt.subplots(figsize=(12, 5.4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")

box(ax, 0.4, 5.6, 3.2, 2.4, "평소\n\nSkill의 이름과 설명만\n목록으로 알고 있다\n(본문은 안 읽은 상태)",
    fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
box(ax, 5.2, 6.9, 3.6, 1.5, "호출 방법 1\n사용자가 /skill-name 입력", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 5.2, 4.9, 3.6, 1.5, "호출 방법 2\n요청이 설명과 맞으면\n에이전트가 스스로 사용", fc="#fdf9f4", ec="#c77b2f", fontsize=9.5)
box(ax, 10.2, 5.6, 3.4, 2.4, "실행\n\nSKILL.md 본문이\n맥락창에 로드되고\n적힌 절차대로 작업",
    fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
arrow(ax, 3.7, 7.2, 5.1, 7.55)
arrow(ax, 3.7, 6.2, 5.1, 5.75)
arrow(ax, 8.9, 7.55, 10.1, 7.2)
arrow(ax, 8.9, 5.75, 10.1, 6.2)

box(ax, 2.2, 1.0, 9.6, 2.6, "", fc="white", ec="#7a5fa8")
ax.text(7.0, 3.1, "SKILL.md의 두 부분", ha="center", fontsize=11, fontweight="bold", color="#4a3a68")
ax.text(4.6, 1.95, "머리말(frontmatter)\nname: 이름\ndescription: 언제 쓰는 스킬인지", ha="center",
        fontsize=9.5, color="#333")
ax.text(9.6, 1.95, "본문(markdown)\n에이전트가 따를 절차를\n단계별로 적은 지시문", ha="center",
        fontsize=9.5, color="#333")
ax.plot([7.0, 7.0], [1.2, 2.8], color="#d9d9e3", lw=1)
arrow(ax, 11.9, 5.5, 8.4, 3.75, color="#7a5fa8", ls="--")
fig.savefig(FIG / "fig11_skill_flow.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig11_*.png'))])
