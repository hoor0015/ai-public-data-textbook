# 5주차 2회차 개념도 생성 (그림 5-4: csv-profile 스킬 폴더의 v1 → v2 변화와 로드 시점)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

figfit.MAX_PT = 13.0  # 짧은 문구 상자의 글씨 과대 방지

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=10, weight="normal", lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


fig, ax = plt.subplots(figsize=(12, 6.6))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

# ---- 왼쪽: v1 (4주차)
ax.text(2.6, 9.45, "v1 (4주차)", ha="center", fontsize=12, fontweight="bold", color="#333")
ax.text(2.6, 8.95, ".claude/skills/csv-profile/", ha="center", fontsize=10, color="#555", family="monospace")
ax.add_patch(FancyBboxPatch((0.5, 3.2), 4.2, 5.4, boxstyle="round,pad=0.06",
                            fc="#fafafa", ec="#bbbbbb", lw=1.2, ls="--"))
box(ax, 0.9, 4.0, 3.4, 4.1,
    "SKILL.md\n\n설명\n인자 자리($ARGUMENTS)\n절차 7단계\n품질 경고 기준\n산출물 양식\n규칙",
    fc="#f4fbf6", ec="#2f8f4e")
ax.text(2.6, 3.55, "파일 하나에 전부. 계산은 매번 즉흥 코드", ha="center", fontsize=9, color="#555")

# ---- 가운데 화살표
arrow(ax, 4.9, 6.0, 5.9, 6.0, lw=2.0)
ax.text(5.4, 6.45, "인자 설계\n참조 분리\n스크립트", ha="center", va="bottom", fontsize=9.5, color="#333")

# ---- 오른쪽: v2 (5주차)
ax.text(9.9, 9.45, "v2 (5주차)", ha="center", fontsize=12, fontweight="bold", color="#333")
ax.text(9.9, 8.95, ".claude/skills/csv-profile/", ha="center", fontsize=10, color="#555", family="monospace")
ax.add_patch(FancyBboxPatch((6.1, 3.2), 7.6, 5.4, boxstyle="round,pad=0.06",
                            fc="#fafafa", ec="#bbbbbb", lw=1.2, ls="--"))
box(ax, 6.4, 4.9, 2.2, 3.2, "SKILL.md\n\n설명·인자\n절차·규칙\n(짧게)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 8.9, 4.9, 2.2, 3.2, "reference.md\n\n품질 경고 기준표\n산출물 양식\n확인 필요 지침", fc="#f5f9fd", ec="#2f6fb0")
box(ax, 11.4, 4.9, 2.0, 3.2, "scripts/\nprofile.py\n\n계산 코드\n(고정)", fc="#fdf9f4", ec="#c77b2f")
ax.text(7.5, 4.45, "설명: 항상 목록에\n본문: 호출할 때 로드", ha="center", va="top", fontsize=8.8, color="#555")
ax.text(10.0, 4.45, "절차가 그 단계에\n이르렀을 때만 읽힘", ha="center", va="top", fontsize=8.8, color="#555")
ax.text(12.4, 4.45, "실행만 되고 코드는\n맥락창에 안 실림", ha="center", va="top", fontsize=8.8, color="#555")

# ---- 아래: 스킬 라이브러리
ax.add_patch(FancyBboxPatch((0.5, 0.35), 13.2, 2.3, boxstyle="round,pad=0.06",
                            fc="white", ec="#7a5fa8", lw=1.3))
ax.text(7.1, 2.12, "스킬 라이브러리 (2.5절-2.8절)", ha="center", va="bottom", fontsize=11,
        fontweight="bold", color="#4a3a68")
box(ax, 0.9, 0.6, 3.9, 1.35, "csv-profile\n범용. 개인 폴더로 승격\n(자동 호출 허용)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 5.15, 0.6, 3.9, 1.35, "submit-pack\n프로젝트 전용. 사람만 호출\n(disable-model-invocation)", fc="#fdf9f4", ec="#c77b2f")
box(ax, 9.4, 0.6, 3.9, 1.35, "check-report\n격리 실행(context: fork)\n독립 검산", fc="#faf8fc", ec="#7a5fa8")

fig.savefig(FIG / "fig05_skill_v2.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved:", FIG / "fig05_skill_v2.png")
