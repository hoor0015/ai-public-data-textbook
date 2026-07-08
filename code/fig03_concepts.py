# 3주차 1회차 개념도 생성
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
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


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 3-1
# 좋은 지시의 다섯 요소
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

elems = [
    ("역할", "누구의 입장에서\n일하는가", "\"구청 인구정책팀의\n분석 보조로서\"", "#c77b2f", "#fdf9f4"),
    ("맥락", "어떤 재료와 배경이\n있는가", "\"data 폴더의\nsigungu_2023.csv를\n바탕으로\"", "#2f6fb0", "#f5f9fd"),
    ("과제", "무엇을 해야\n하는가", "\"합계출산율 상위·하위\n5개 시군구를 찾아\"", "#2f8f4e", "#f4fbf6"),
    ("제약", "무엇을 지키고\n피해야 하는가", "\"파일에 있는 값만 쓰고\n추측하지 말 것\"", "#b03a3a", "#fdf5f5"),
    ("산출물", "결과가 어떤 모습\n이어야 하는가", "\"마크다운 표와\n세 문장 요약으로\"", "#7a5fa8", "#faf8fc"),
]
for i, (t, desc, ex, ec, fc) in enumerate(elems):
    x = 0.4 + i * 2.56
    box(ax, x, 6.4, 2.2, 1.5, t, fc=fc, ec=ec, fontsize=13, weight="bold")
    box(ax, x, 4.2, 2.2, 1.8, desc, fc="white", ec=ec, fontsize=9.5)
    box(ax, x, 1.5, 2.2, 2.3, ex, fc=fc, ec=ec, fontsize=9)
    arrow(ax, x + 1.1, 6.3, x + 1.1, 6.15, color=ec)
    arrow(ax, x + 1.1, 4.1, x + 1.1, 3.95, color=ec)
ax.text(6.5, 8.6, "좋은 지시 = 다섯 요소가 한 지시문 안에 함께 들어 있는 것", ha="center",
        fontsize=13, fontweight="bold")
ax.text(6.5, 0.5, "다섯 요소를 이으면 그대로 하나의 완성된 지시문이 된다. 모든 지시에 다섯 개가 전부 필요한 것은 아니다.",
        ha="center", fontsize=10.5, color="#333")
fig.savefig(FIG / "fig03_five_elements.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 3-2
# 나쁜 지시(발산) vs 좋은 지시(수렴)
fig, axes = plt.subplots(1, 2, figsize=(12, 5.0))
for ax in axes:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

ax = axes[0]
ax.set_title("(가) 나쁜 지시: 해석이 갈라진다", fontsize=13, pad=12)
box(ax, 2.4, 7.8, 5.2, 1.5, "\"인구 데이터 분석해 줘\"", fc="#fdf5f5", ec="#b03a3a", fontsize=11)
interps = [
    ("어느 파일을?\n(data 폴더엔 여러 개)", 0.3),
    ("무슨 분석을?\n(요약? 비교? 그림?)", 3.7),
    ("어떤 형태로?\n(표? 보고서? 코드?)", 7.1),
]
for t, x in interps:
    box(ax, x, 4.2, 2.6, 1.9, t, fc="white", ec="#b03a3a", fontsize=9.5)
    arrow(ax, 5.0, 7.7, x + 1.3, 6.2, color="#b03a3a", ls="--")
box(ax, 2.4, 0.9, 5.2, 1.6, "결과가 복불복이 된다\n(내 의도와 다를 수 있음)", fc="#fdf5f5", ec="#b03a3a", fontsize=10)
for t, x in interps:
    arrow(ax, x + 1.3, 4.1, 5.0, 2.6, color="#b03a3a", ls="--")

ax = axes[1]
ax.set_title("(나) 좋은 지시: 해석이 모인다", fontsize=13, pad=12)
box(ax, 1.2, 7.2, 7.6, 2.1,
    "\"data 폴더의 sigungu_2023.csv에서\n합계출산율 상위·하위 5개 시군구를\n마크다운 표로 정리해 줘\"",
    fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
box(ax, 2.8, 4.0, 4.4, 1.7, "파일·과제·형식이\n하나로 정해진다", fc="white", ec="#2f8f4e", fontsize=10)
arrow(ax, 5.0, 7.1, 5.0, 5.8, color="#2f8f4e")
box(ax, 2.4, 0.9, 5.2, 1.6, "누가 몇 번을 시켜도\n의도한 결과에 가깝다", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
arrow(ax, 5.0, 3.9, 5.0, 2.6, color="#2f8f4e")
fig.tight_layout()
fig.savefig(FIG / "fig03_bad_vs_good.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 3-3
# 계획 모드의 흐름
fig, ax = plt.subplots(figsize=(11, 5.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 8.5)
ax.axis("off")

box(ax, 0.4, 5.6, 3.0, 1.9, "사용자\n복잡한 과제를\n계획 모드로 지시", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 4.3, 5.6, 3.6, 1.9, "에이전트\n파일을 읽고 조사만 한다\n(수정·실행은 하지 않음)", fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
box(ax, 8.9, 5.6, 3.4, 1.9, "계획서 제시\n\"1단계 ... 2단계 ...\n이렇게 진행할까요?\"", fc="#faf8fc", ec="#7a5fa8", fontsize=10)
box(ax, 8.9, 1.2, 3.4, 1.9, "사용자 검토\n단계가 빠졌나?\n순서가 맞나?", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 3.3, 1.2, 3.6, 1.9, "승인 후 실행\n에이전트가 계획대로\n작업을 시작한다", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)

arrow(ax, 3.5, 6.55, 4.2, 6.55)
arrow(ax, 8.0, 6.55, 8.8, 6.55)
arrow(ax, 10.6, 5.5, 10.6, 3.3)
arrow(ax, 8.8, 2.15, 7.1, 2.15)
arrow(ax, 8.9, 3.0, 6.4, 5.5, color="#b03a3a", ls="--")
ax.text(5.6, 3.8, "계획을 고쳐 달라고\n되돌려 보낼 수 있다", fontsize=9.5, color="#b03a3a", ha="center")
ax.text(6.5, 0.4, "실행 전에 사람이 계획을 검토하는 관문이 생긴다. 잘못된 방향이면 파일이 바뀌기 전에 잡는다.",
        ha="center", fontsize=10.5, color="#333")
fig.savefig(FIG / "fig03_plan_mode.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig03_*.png'))])
