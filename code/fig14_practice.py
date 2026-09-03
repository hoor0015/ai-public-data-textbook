# 14주차 2회차(실습) 그림 생성: 그림 14-4(근거 사슬 개념도), 그림 14-5(2013년 대비 2023년 출산율 변화)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 14-4
# 근거 사슬: 원자료 -> 결과 파일 -> 본문 문장 -> 요약·제언. 작성은 오른쪽으로, 대조는 왼쪽으로.
fig, ax = plt.subplots(figsize=(11.5, 5.4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.6)
ax.axis("off")

chain = [
    (0.4, "원자료\ndata/sigungu_2023.csv", "수도권 66개 시군구의\n합계출산율 값", "#c77b2f", "#fdf9f4"),
    (3.9, "결과 파일\noutput/analysis.md", "수도권 평균 0.690\n비수도권 평균 0.877", "#2f6fb0", "#f5f9fd"),
    (7.4, "본문 문장\nreport.md 3장 발견", "수도권 평균(0.690)은\n비수도권(0.877)보다 낮았다", "#2f8f4e", "#f4fbf6"),
    (10.9, "요약·제언\nreport.md 요약, 4장", "제언 1: 대도시 양육 여건\n(근거: 발견 3.2)", "#7a5fa8", "#faf8fc"),
]
for x, title, example, ec, fc in chain:
    box(ax, x, 4.3, 2.8, 1.7, title, fc=fc, ec=ec, fontsize=10.5, weight="bold")
    box(ax, x, 2.2, 2.8, 1.5, example, fc="white", ec=ec, fontsize=9.5)
    arrow(ax, x + 1.4, 4.2, x + 1.4, 3.8, color=ec, lw=1.2)

for x in (3.2, 6.7, 10.2):
    arrow(ax, x + 0.05, 5.5, x + 0.65, 5.5, color="#333", lw=1.8)
# 대조 방향: 오른쪽 끝(요약·제언)에서 왼쪽 끝(원자료)까지 한 번에 거슬러 가는 긴 점선 화살표
arrow(ax, 13.6, 1.5, 0.5, 1.5, color="#b03a2e", lw=1.8, ls="--")
for x, _, _, ec, _ in chain:
    arrow(ax, x + 1.4, 2.1, x + 1.4, 1.6, color=ec, lw=1.0, style="-")

ax.text(7.0, 6.6, "작성 방향: 원자료의 값이 결과 파일을 거쳐 문장과 제언으로 옮겨진다",
        ha="center", fontsize=11, color="#333")
ax.text(7.0, 0.5, "대조 방향: 제언과 문장의 숫자를 결과 파일이 아니라 원자료까지 거슬러 올라가 다시 계산한다",
        ha="center", fontsize=11, color="#b03a2e")
ax.text(7.0, 7.9, "근거 사슬: 보고서의 모든 문장은 파일 하나까지 되짚어 갈 수 있어야 한다",
        ha="center", fontsize=13)
fig.tight_layout()
fig.savefig(FIG / "fig14_evidence_chain.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 14-5
# 2013년 대비 2023년 시군구 합계출산율: 대각선 아래가 하락
m = pd.read_csv(BASE / "data" / "sigungu_tfr_2013_2023.csv", encoding="utf-8-sig")
m = m.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
m["권역"] = np.where(m["시도"].isin(["서울", "경기", "인천"]), "수도권", "비수도권")
m["변화"] = m["합계출산율"] - m["합계출산율_2013"]
n_up = int((m["변화"] > 0).sum())
n_down = int((m["변화"] < 0).sum())

fig, ax = plt.subplots(figsize=(8.2, 7))
lim = (0.2, 2.5)
ax.plot(lim, lim, color="#888", lw=1.2, ls="--", zorder=1)
ax.text(2.02, 2.12, "변화 없음 (대각선)", fontsize=9.5, color="#666", rotation=45,
        rotation_mode="anchor", ha="left", va="bottom")
for name, mk, col in [("비수도권", "o", "#2f6fb0"), ("수도권", "^", "#c77b2f")]:
    g = m[m["권역"] == name]
    ax.scatter(g["합계출산율_2013"], g["합계출산율"], marker=mk, s=34, alpha=0.7,
               color=col, edgecolor="white", lw=0.5, label=f"{name} ({len(g)}개)", zorder=2)

# 상승한 4곳에 이름표
up = m[m["변화"] > 0].sort_values("합계출산율_2013")
# 이름표는 모두 대각선 위쪽의 빈 영역(왼쪽 위)에 둔다
offsets = [(-0.55, 0.12), (-0.65, 0.20), (-0.75, 0.42), (-0.70, 0.38)]
for (_, row), (dx, dy) in zip(up.iterrows(), offsets):
    ax.annotate(f"{row['시도']} {row['시군구']}\n{row['합계출산율_2013']:.3f} → {row['합계출산율']:.3f}",
                (row["합계출산율_2013"], row["합계출산율"]),
                xytext=(row["합계출산율_2013"] + dx, row["합계출산율"] + dy),
                fontsize=8.5, color="#333",
                arrowprops=dict(arrowstyle="-", color="#999", lw=0.8))

ax.text(0.03, 0.97, f"대각선 아래(하락) {n_down}개, 위(상승) {n_up}개, 두 해 모두 값이 있는 {len(m)}개 시군구",
        transform=ax.transAxes, fontsize=9.5, va="top",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
ax.set_xlim(lim)
ax.set_ylim(lim)
ax.set_xlabel("2013년 합계출산율 (명)")
ax.set_ylabel("2023년 합계출산율 (명)")
ax.set_title("시군구 합계출산율: 2013년 대비 2023년", fontsize=12.5)
ax.legend(loc="lower right", fontsize=9.5, frameon=True)
ax.set_aspect("equal")
fig.tight_layout()
fig.savefig(FIG / "fig14_change_2013_2023.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob("fig14_*.png"))])
print(f"하락 {n_down}개, 상승 {n_up}개, n={len(m)}")
