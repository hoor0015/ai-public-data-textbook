# 1주차 2회차 실습 개념도 생성: 그림 1-4 VSCode 화면 구성(네 구역)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

figfit.MAX_PT = 14.0  # 작은 제목 상자의 글씨 과대 확대 방지

from matplotlib.patches import FancyBboxPatch, Rectangle

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11,
        weight="normal", lw=1.4, pad=0.06):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={pad}",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


# ---------------------------------------------------------------- 그림 1-4
# VSCode 화면 구성: 탐색기·편집기·터미널·Claude Code 패널
fig, ax = plt.subplots(figsize=(12, 6.8))
ax.set_xlim(0, 12.6)
ax.set_ylim(-1.3, 8.6)
ax.axis("off")

# 창 바깥 테두리와 제목 표시줄 (도형이 아닌 배경이므로 Rectangle 사용)
ax.add_patch(Rectangle((0.2, 0.2), 12.2, 8.0, fc="#ececf1", ec="#9a9aa8", lw=1.2))
ax.add_patch(Rectangle((0.2, 7.5), 12.2, 0.7, fc="#d9d9e3", ec="#9a9aa8", lw=1.2))
ax.text(0.5, 7.85, "VSCode  -  공공데이터분석", ha="left", va="center",
        fontsize=10, color="#333")

# 활동 막대 (왼쪽 세로 띠)
ax.add_patch(Rectangle((0.2, 0.2), 0.75, 7.3, fc="#cfcfdb", ec="none"))
ax.text(0.575, 6.9, "탐색기", ha="center", va="center", fontsize=7.5,
        rotation=90, color="#333")
ax.text(0.575, 5.6, "확장", ha="center", va="center", fontsize=7.5,
        rotation=90, color="#333")
ax.text(0.575, 4.3, "Claude", ha="center", va="center", fontsize=7.5,
        rotation=90, color="#333")

# ① 탐색기
box(ax, 1.05, 0.4, 2.35, 6.95, "", fc="#f5f9fd", ec="#2f6fb0")
box(ax, 1.2, 6.45, 2.05, 0.75, "① 탐색기", fc="white", ec="#2f6fb0", weight="bold")
tree = ("공공데이터분석\n"
        "  data\n"
        "  산출물\n"
        "  메모\n"
        "    내가아는사실.md\n"
        "    우리동네.md\n"
        "  README.md")
ax.text(1.3, 6.15, tree, ha="left", va="top", fontsize=9.5, color="#333")
ax.text(2.225, 0.6, "폴더와 파일의 목록.\n에이전트가 만든 파일이\n실제로 있는지\n여기서 확인한다.",
        ha="center", va="bottom", fontsize=9, color="#333")

# ② 편집기
box(ax, 3.55, 3.55, 5.3, 3.8, "", fc="#faf8fc", ec="#7a5fa8")
box(ax, 3.7, 6.45, 2.2, 0.75, "② 편집기", fc="white", ec="#7a5fa8", weight="bold")
ax.text(3.75, 6.2, "README.md", ha="left", va="top", fontsize=9, color="#555")
ax.text(3.75, 5.75,
        "  ## 메모\n"
        "- 수업 중 관찰과 기록을 남긴다.\n"
        "+ 수업 중 관찰과 기록을 남긴다.\n"
        "+ 계획서는 주차별로 저장한다.",
        ha="left", va="top", fontsize=9, color="#333")
ax.text(6.2, 3.75, "파일을 클릭하면 내용이 열린다.\n에이전트가 파일을 고치면\n이전과 이후가 나란히 비교된다(diff).",
        ha="center", va="bottom", fontsize=9, color="#333")

# ③ 터미널
box(ax, 3.55, 0.4, 5.3, 2.95, "", fc="#fdf9f4", ec="#c77b2f")
box(ax, 3.7, 2.55, 2.2, 0.7, "③ 터미널", fc="white", ec="#c77b2f", weight="bold")
ax.text(3.75, 2.3,
        "> Get-ChildItem\n"
        "  data   산출물   메모   README.md",
        ha="left", va="top", fontsize=9, color="#333")
ax.text(6.2, 0.6, "에이전트가 명령을 실행하는 창.\n학생은 여기 찍힌 출력을 읽기만 한다.",
        ha="center", va="bottom", fontsize=9, color="#333")

# ④ Claude Code 패널
box(ax, 9.0, 0.4, 3.25, 6.95, "", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 9.15, 6.45, 2.95, 0.75, "④ Claude Code 패널", fc="white", ec="#2f8f4e",
    weight="bold")
box(ax, 9.25, 5.35, 2.75, 0.85, "대화 기록 / 새 대화", fc="white", ec="#2f8f4e",
    fontsize=9)
box(ax, 9.25, 3.6, 2.75, 1.5, "도구 사용 기록\n(파일 읽기, 명령 실행,\n파일 쓰기가 순서대로)",
    fc="white", ec="#2f8f4e", fontsize=9)
box(ax, 9.25, 2.35, 2.75, 1.0, "승인 · 거부 버튼", fc="#fdf9f4", ec="#c77b2f",
    fontsize=9)
box(ax, 9.25, 0.65, 2.75, 1.45, "지시 입력창\n(한국어로 지시한다)", fc="white",
    ec="#2f8f4e", fontsize=9)

# 아래 범례: 누가 어느 구역을 쓰는가
ax.text(6.3, -0.55,
        "학생이 주로 쓰는 곳: ④ 패널(지시)  ①(확인)  ②(읽기).   "
        "에이전트가 일하는 곳: ③ 터미널, ② 편집기의 파일.",
        ha="center", va="center", fontsize=10, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.5"))

fig.savefig(FIG / "fig01_vscode_layout.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", FIG / "fig01_vscode_layout.png")

# 2.6절 긴 계산 예시의 정답 확인 (1부터 99까지 홀수의 제곱의 합)
print("odd squares 1-99 sum:", sum(k * k for k in range(1, 100, 2)))
