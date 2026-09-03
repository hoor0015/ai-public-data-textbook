# 3주차 2회차(실습) 그림 생성: 그림 3-4 총인구 상위 10개 시군구, 그림 3-5 재현 테스트의 흐름
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

figfit.MAX_PT = 12.5  # 짧은 글씨 상자가 지나치게 커지지 않도록 상한 조정

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=10, weight="normal", ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                fc=fc, ec=ec, lw=1.4, linestyle=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 3-5
# 재현 테스트: 설계도 두 장으로 같은 환경을 다시 짓는다
fig, ax = plt.subplots(figsize=(12, 6.6))
ax.set_xlim(0, 14.4)
ax.set_ylim(0, 9.6)
ax.axis("off")

# 원본 폴더 틀
ax.add_patch(FancyBboxPatch((0.4, 3.3), 4.4, 5.9, boxstyle="round,pad=0.1",
                            fc="#f7f7fc", ec="#5b6ee1", lw=1.8))
ax.text(2.6, 8.75, "원본 폴더: 공공데이터분석/", fontsize=11.5, ha="center", fontweight="bold")
box(ax, 0.9, 7.5, 3.4, 0.8, "pyproject.toml (필요 목록)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 0.9, 6.55, 3.4, 0.8, "uv.lock (정밀 기록)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 0.9, 4.75, 3.4, 1.1, ".venv/ (도구상자)\n복사하지 않는다", fc="#f2f2f2", ec="#999", ls="--")
box(ax, 0.9, 3.7, 3.4, 0.8, "main.py, data/", fc="white", ec="#2f6fb0")

# 사본 폴더 틀
ax.add_patch(FancyBboxPatch((5.6, 3.3), 4.4, 5.9, boxstyle="round,pad=0.1",
                            fc="#f7f7fc", ec="#5b6ee1", lw=1.8))
ax.text(7.8, 8.75, "사본 폴더: 공공데이터분석_사본/", fontsize=11.5, ha="center", fontweight="bold")
box(ax, 6.1, 7.5, 3.4, 0.8, "pyproject.toml (복사)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 6.1, 6.55, 3.4, 0.8, "uv.lock (복사)", fc="#f4fbf6", ec="#2f8f4e")
box(ax, 6.1, 4.75, 3.4, 1.1, ".venv/ (도구상자)\nuv sync가 새로 짓는다", fc="#fdf9f4", ec="#c77b2f")
box(ax, 6.1, 3.7, 3.4, 0.8, "main.py, data/ (복사)", fc="white", ec="#2f6fb0")
arrow(ax, 7.8, 6.5, 7.8, 5.9, color="#c77b2f", lw=2.0)
ax.text(8.05, 6.12, "uv sync", fontsize=10, color="#c77b2f", ha="left", fontweight="bold")

# 복사 화살표
arrow(ax, 4.9, 6.95, 5.5, 6.95, color="#5b6ee1", lw=2.0)
ax.text(5.2, 7.3, "복사", fontsize=10, color="#5b6ee1", ha="center", fontweight="bold")

# 실행 결과
arrow(ax, 2.6, 3.2, 2.6, 2.35)
ax.text(2.95, 2.75, "uv run main.py", fontsize=9.5, color="#555", ha="left")
arrow(ax, 7.8, 3.2, 7.8, 2.35)
ax.text(8.15, 2.75, "uv run main.py", fontsize=9.5, color="#555", ha="left")
box(ax, 0.9, 1.3, 3.4, 0.95, "실행결과_원본.txt", fc="#faf8fc", ec="#7a5fa8", weight="bold")
box(ax, 6.1, 1.3, 3.4, 0.95, "실행결과_사본.txt", fc="#faf8fc", ec="#7a5fa8", weight="bold")
ax.add_patch(FancyArrowPatch((4.4, 1.77), (6.0, 1.77), arrowstyle="<|-|>",
                             mutation_scale=16, color="#7a5fa8", lw=1.8))
ax.text(5.2, 2.05, "같은가?", fontsize=10.5, color="#7a5fa8", ha="center", fontweight="bold")

# 설명 상자
ax.text(12.2, 5.2,
        "설계도 두 장(pyproject.toml, uv.lock)만\n있으면 도구상자(.venv)는 어디서든\n다시 지을 수 있다.\n\n두 출력 파일이 한 글자도 다르지 않으면\n재현에 성공한 것이다.",
        ha="center", va="center", fontsize=10.5, color="#333",
        bbox=dict(fc="#f7f7fc", ec="#d9d9e3", boxstyle="round,pad=0.6"))

fig.savefig(FIG / "fig03_repro_test.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig03_repro_test.png")

# ---------------------------------------------------------------- 그림 3-4
# 총인구 상위 10개 시군구: 실습 2.7에서 학생이 에이전트에게 그리게 하는 첫 그림
# 수치는 data/sigungu_2023.csv에서 직접 계산 (code/ch03_practice.py의 (11)과 같은 값)
import pandas as pd  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")
top10 = df.nlargest(10, "총인구")[["시도", "시군구", "총인구"]]
names = [f"{r['시도']} {r['시군구']}" for _, r in top10.iterrows()][::-1]
vals = [r["총인구"] / 10000 for _, r in top10.iterrows()][::-1]  # 만 명 단위

_kfont = plt.rcParams["font.family"]  # seaborn 스타일이 한글 글꼴을 되돌리지 않도록 보존
sns.set_style("whitegrid")
plt.rcParams["font.family"] = _kfont
fig, ax = plt.subplots(figsize=(9, 5.4))
bars = ax.barh(names, vals, color="#7fa8d0", edgecolor="#2f6fb0", height=0.62)
for b, v in zip(bars, vals):
    ax.text(b.get_width() + 1.2, b.get_y() + b.get_height() / 2,
            f"{v * 10000:,.0f}", va="center", fontsize=9.5, color="#333")
ax.set_xlabel("총인구 (만 명)")
ax.set_xlim(0, 138)
ax.set_title("총인구 상위 10개 시군구 (2023)", fontsize=13, pad=10)
sns.despine(left=True)
fig.tight_layout()
fig.savefig(FIG / "fig03_top10_pop.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig03_top10_pop.png")
print(top10.to_string(index=False))
