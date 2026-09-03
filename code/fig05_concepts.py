# 5주차 1회차 개념도 생성 (Skill 심화: 세 방향, 스킬 폴더와 점진적 공개, 호출 주체 제어)
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
# 스킬이 자라는 세 방향: 인자, 참조 파일, 스크립트
fig, ax = plt.subplots(figsize=(12.5, 6.4))
ax.set_xlim(0, 14.5)
ax.set_ylim(0, 9.4)
ax.axis("off")

box(ax, 0.4, 3.2, 3.2, 3.0,
    "csv-profile v1 (4주차)\n\nSKILL.md 한 장\n머리말 + 절차\n인자는 \\$ARGUMENTS 하나",
    fc="#f5f9fd", ec="#2f6fb0", fontsize=10)

rows = [
    (6.6, "① 인자\n(서식의 빈칸)",
     "입력이 매번 달라진다\n파일이 바뀌고, 간단·상세\n보고서 모드 요청이 갈린다",
     "머리말 arguments: [file, mode]\n본문에서 \\$file, \\$mode로 받는다\n하나의 스킬을 여러 입력에"),
    (3.7, "② 참조 파일\n(별첨)",
     "기준표·양식이 길어진다\n품질 경고 기준, 보고서 양식이\nSKILL.md를 수백 줄로 불린다",
     "reference.md, examples.md로 분리\nSKILL.md에서 링크만 건다\n필요할 때만 읽힌다 (점진적 공개)"),
    (0.8, "③ 스크립트\n(계산기)",
     "계산이 매번 조금씩 다르다\n에이전트가 코드를 새로 쓰므로\n반올림·결측 처리가 흔들린다",
     "scripts/profile.py 고정 코드\n\\${CLAUDE_SKILL_DIR}/scripts/…를 실행\n같은 입력이면 같은 숫자"),
]
for y, tag, prob, sol in rows:
    box(ax, 4.5, y, 1.9, 2.0, tag, fc="#faf8fc", ec="#7a5fa8", fontsize=10, weight="bold")
    box(ax, 6.7, y, 3.5, 2.0, prob, fc="#fdf9f4", ec="#c77b2f", fontsize=9)
    box(ax, 10.5, y, 3.7, 2.0, sol, fc="#f4fbf6", ec="#2f8f4e", fontsize=9)
    arrow(ax, 3.7, 4.7, 4.4, y + 1.0)
    arrow(ax, 10.25, y + 1.0, 10.45, y + 1.0, lw=1.2)

ax.text(8.45, 8.95, "부딪히는 문제", ha="center", fontsize=10.5, color="#8a4f14", fontweight="bold")
ax.text(12.35, 8.95, "스킬에 다는 것", ha="center", fontsize=10.5, color="#1f6b38", fontweight="bold")
ax.text(5.45, 8.95, "자라는 방향", ha="center", fontsize=10.5, color="#4a3a68", fontweight="bold")
fig.savefig(FIG / "fig05_skill_growth.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 5-2
# 스킬 폴더 해부와 점진적 공개
fig, ax = plt.subplots(figsize=(12.5, 6.8))
ax.set_xlim(0, 14.5)
ax.set_ylim(0, 9.6)
ax.axis("off")

# 왼쪽: 폴더 구조
ax.add_patch(FancyBboxPatch((0.4, 0.5), 5.6, 8.6, boxstyle="round,pad=0.08",
                            fc="white", ec="#7a5fa8", lw=1.4))
ax.text(0.7, 8.75, ".claude/skills/csv-profile/", ha="left", va="center",
        fontsize=11, fontweight="bold", color="#4a3a68")

ax.add_patch(FancyBboxPatch((0.8, 4.9), 4.8, 3.4, boxstyle="round,pad=0.06",
                            fc="#fbfbfd", ec="#2f6fb0", lw=1.2, ls="--"))
ax.text(1.0, 8.05, "SKILL.md (500줄 이하)", ha="left", va="center", fontsize=10.5,
        fontweight="bold", color="#2f6fb0")
box(ax, 1.1, 6.55, 4.2, 1.2, "머리말: name, description,\narguments, allowed-tools",
    fc="#f5f9fd", ec="#2f6fb0", fontsize=9)
box(ax, 1.1, 5.1, 4.2, 1.2, "본문: 절차와 규칙\n(참조 파일·스크립트로 링크)",
    fc="#f5f9fd", ec="#2f6fb0", fontsize=9)
box(ax, 0.8, 3.2, 2.3, 1.3, "reference.md\n품질 경고 기준표", fc="#faf8fc", ec="#7a5fa8", fontsize=9)
box(ax, 3.3, 3.2, 2.3, 1.3, "examples.md\n보고서 양식 예시", fc="#faf8fc", ec="#7a5fa8", fontsize=9)
box(ax, 0.8, 1.2, 4.8, 1.5, "scripts/profile.py\n고정 계산 코드 (3주차 uv 환경에서 실행)",
    fc="#fdf9f4", ec="#c77b2f", fontsize=9)

# 오른쪽: 점진적 공개 4단계
stages = [
    (7.45, "평소\n이름과 설명만 목록에 있다\n(머리말)", "#f5f9fd", "#2f6fb0"),
    (5.4, "호출 시\nSKILL.md 본문이 맥락창에 로드된다", "#f4fbf6", "#2f8f4e"),
    (3.35, "필요할 때\n절차가 가리키는 참조 파일을 읽는다", "#faf8fc", "#7a5fa8"),
    (1.3, "실행 시\n스크립트를 실행하고 출력만 받는다", "#fdf9f4", "#c77b2f"),
]
for y, text, fc, ec in stages:
    box(ax, 7.6, y, 5.2, 1.5, text, fc=fc, ec=ec, fontsize=9.5)
for y1, y2 in ((7.45, 6.9), (5.4, 4.85), (3.35, 2.8)):
    arrow(ax, 10.2, y1, 10.2, y2)

# 왼쪽 파일 -> 오른쪽 단계 (점선)
arrow(ax, 5.35, 7.15, 7.5, 8.2, color="#2f6fb0", ls="--", lw=1.2)
arrow(ax, 5.35, 5.7, 7.5, 6.15, color="#2f8f4e", ls="--", lw=1.2)
arrow(ax, 5.65, 3.85, 7.5, 4.1, color="#7a5fa8", ls="--", lw=1.2)
arrow(ax, 5.65, 1.95, 7.5, 2.05, color="#c77b2f", ls="--", lw=1.2)

ax.annotate("", xy=(13.6, 1.2), xytext=(13.6, 9.0),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.6))
ax.text(13.85, 5.1, "아래로 갈수록\n맥락창에 들어가는\n시점이 늦다", fontsize=9.5,
        color="#555", va="center", ha="left")
ax.text(10.2, 9.25, "점진적 공개 (progressive disclosure)", ha="center", fontsize=11,
        fontweight="bold", color="#333")
fig.savefig(FIG / "fig05_skill_folder.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 5-3
# 호출 주체 제어: 사용자 축 x 에이전트 축
fig, ax = plt.subplots(figsize=(11.5, 7.2))
ax.set_xlim(0, 12.6)
ax.set_ylim(0, 8.4)
ax.axis("off")

cells = [
    (2.9, 4.2, "기본 (설정 없음)\n\n사용자도, 에이전트도 부른다\n예: csv-profile\n(언제 실행해도 무해한 진단)",
     "#f4fbf6", "#2f8f4e"),
    (7.6, 4.2, "disable-model-invocation: true\n\n사용자만 부른다\n설명이 에이전트 맥락에 실리지 않는다\n예: 제출 폴더 정리 (시점은 사람이)",
     "#fdf9f4", "#c77b2f"),
    (2.9, 1.0, "user-invocable: false\n\n에이전트만 부른다\n/ 메뉴에 보이지 않는다\n예: 행정구역 명칭 규약 (배경지식)",
     "#f5f9fd", "#2f6fb0"),
    (7.6, 1.0, "꺼진 스킬\n\n둘 다 부르지 못한다\nsettings.json의 skillOverrides로\n비활성화한 상태",
     "#f4f4f4", "#888888"),
]
for x, y, text, fc, ec in cells:
    box(ax, x, y, 4.4, 2.8, text, fc=fc, ec=ec, fontsize=9.5)

ax.text(7.6, 7.85, "에이전트가 요청을 보고 스스로 부른다", ha="center", fontsize=11.5,
        fontweight="bold", color="#333")
ax.text(5.1, 7.3, "예", ha="center", fontsize=11, color="#333")
ax.text(9.8, 7.3, "아니오", ha="center", fontsize=11, color="#333")
ax.text(0.55, 4.0, "사용자가 /이름으로 부른다", rotation=90, ha="center", va="center",
        fontsize=11.5, fontweight="bold", color="#333")
ax.text(1.9, 5.6, "예", ha="center", va="center", fontsize=11, color="#333")
ax.text(1.9, 2.4, "아니오", ha="center", va="center", fontsize=11, color="#333")
ax.plot([2.6, 12.2], [3.9, 3.9], color="#d9d9e3", lw=1)
ax.plot([7.35, 7.35], [0.8, 7.1], color="#d9d9e3", lw=1)
fig.savefig(FIG / "fig05_invocation_control.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig05_*.png'))])
