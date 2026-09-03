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

# ---------------------------------------------------------------- 그림 3-4
# 같은 대화의 재검산 vs 새 대화의 독립 검산
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4))
for ax in axes:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

ax = axes[0]
ax.set_title("(가) 같은 대화에서 재검산", fontsize=13, pad=12)
box(ax, 0.6, 2.9, 8.8, 5.9, "", fc="#fdf9f4", ec="#c77b2f")
ax.text(5.0, 8.25, "맥락창 (결과를 만든 대화)", ha="center", fontsize=11, fontweight="bold", color="#8a5a1f")
for i, t in enumerate(["내가 세운 계획", "내가 쓴 코드", "내 결론: 표 완성"]):
    box(ax, 1.2, 6.3 - i * 1.35, 3.6, 1.1, t, fc="white", ec="#c77b2f", fontsize=9.5)
box(ax, 5.6, 4.1, 3.2, 2.4, "검증 지시\n→ 재검산", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
arrow(ax, 4.9, 5.3, 5.5, 5.3, color="#c77b2f", ls="--")
ax.text(5.0, 1.6, "자기 기억을 참조하며 검산한다.\n처음의 착각이 이어질 수 있다.", ha="center", fontsize=10, color="#8a5a1f")

ax = axes[1]
ax.set_title("(나) 새 대화에서 독립 검산", fontsize=13, pad=12)
box(ax, 0.6, 2.9, 8.8, 5.9, "", fc="#f5f9fd", ec="#2f6fb0")
ax.text(5.0, 8.25, "맥락창 (새 대화: 빈 책상)", ha="center", fontsize=11, fontweight="bold", color="#2f6fb0")
for i, t in enumerate(["원본 파일", "결과 표"]):
    box(ax, 1.2, 6.0 - i * 1.5, 3.6, 1.2, t, fc="white", ec="#2f6fb0", fontsize=9.5)
box(ax, 5.6, 4.1, 3.2, 2.4, "검산 지시\n→ 처음부터\n다시 계산", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
arrow(ax, 4.9, 5.3, 5.5, 5.3, color="#2f6fb0")
ax.text(5.0, 1.6, "만든 사람의 믿음을 물려받지 않은\n감사관이 된다.", ha="center", fontsize=10, color="#1f4e7a")
fig.tight_layout()
fig.savefig(FIG / "fig03_independent_check.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 3-5
# 3주차 실습 2.5절의 흐름
fig, ax = plt.subplots(figsize=(12.5, 5.4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
box(ax, 0.4, 3.6, 2.8, 2.2, "실험 B의 표\n상위·하위 5개\n시군구", fc="#fdf9f4", ec="#c77b2f", fontsize=10)
box(ax, 4.2, 6.0, 3.4, 2.0, "1단계 검증 지시\n(같은 대화에서 이어서)", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
box(ax, 4.2, 1.4, 3.4, 2.0, "2단계 독립 검산\n(새 대화: 원본 + 표만)", fc="#f5f9fd", ec="#2f6fb0", fontsize=10)
box(ax, 8.4, 6.0, 2.6, 2.0, "검증 보고 1\n값·재계산값\n행 번호·일치", fc="white", ec="#2f8f4e", fontsize=9.5)
box(ax, 8.4, 1.4, 2.6, 2.0, "검증 보고 2\n값·재계산값\n행 번호·일치", fc="white", ec="#2f6fb0", fontsize=9.5)
box(ax, 11.4, 3.4, 2.5, 2.6, "사람의 확인\n참값 대조\n'일치' 칸 2개\n직접 확인", fc="#fdf9f4", ec="#c77b2f", fontsize=9.5)
arrow(ax, 3.3, 5.3, 4.1, 6.8)
arrow(ax, 3.3, 4.1, 4.1, 2.6)
arrow(ax, 7.7, 7.0, 8.3, 7.0)
arrow(ax, 7.7, 2.4, 8.3, 2.4)
arrow(ax, 11.1, 6.6, 11.5, 5.4)
arrow(ax, 11.1, 2.8, 11.5, 4.0)
ax.text(5.9, 4.6, "오류 심기 실험: 0.320 → 0.302로 고쳐 다시 검산", ha="center", fontsize=9.5, color="#555",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.3"))
ax.text(7.0, 0.5, "사람이 볼 양은 열 칸에서 두 칸으로 줄지만, 마지막 확인은 남는다",
        ha="center", fontsize=10.5, color="#555")
fig.savefig(FIG / "fig03_verify_flow.png", dpi=150, bbox_inches="tight")
plt.close(fig)


print("saved:", [p.name for p in sorted(FIG.glob('fig03_*.png'))])
