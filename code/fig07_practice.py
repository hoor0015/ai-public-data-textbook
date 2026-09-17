# 7주차 실습 그림 7-4: 넓은 형과 긴 형 (data/grdp_sido.csv의 실제 구조)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

g = pd.read_csv(BASE / "data" / "grdp_sido.csv", encoding="utf-8-sig")
YEARS = [c for c in g.columns if c.isdigit()]
NROW, NYEAR = len(g), len(YEARS)

HEAD = "#2f6fb0"
ACCENT = "#c77b2f"
LINE = "#b9c2cc"
TXT = "#222222"


def draw_table(ax, headers, rows, col_w, title, note, head_color):
    """선과 글씨만으로 표의 모양을 그린다 (도형 없음, 글씨 크기 균일)."""
    x0 = 0.0
    xs = [x0]
    for w in col_w:
        xs.append(xs[-1] + w)
    total = xs[-1]
    n = len(rows) + 1
    row_h = 1.0
    for i in range(n + 1):                       # 가로줄
        y = -i * row_h
        ax.plot([0, total], [y, y], color=LINE, linewidth=0.9, zorder=1)
    for x in xs:                                 # 세로줄
        ax.plot([x, x], [0, -n * row_h], color=LINE, linewidth=0.9, zorder=1)
    ax.add_patch(plt.Rectangle((0, -row_h), total, row_h, facecolor=head_color,
                               alpha=0.13, edgecolor="none", zorder=0))
    for j, h in enumerate(headers):              # 머리글
        ax.text((xs[j] + xs[j + 1]) / 2, -row_h / 2, h, ha="center", va="center",
                fontsize=10.5, color=head_color, fontweight="bold", zorder=2)
    for i, row in enumerate(rows):               # 본문
        for j, cell in enumerate(row):
            ax.text((xs[j] + xs[j + 1]) / 2, -(i + 1.5) * row_h, cell, ha="center", va="center",
                    fontsize=10, color=TXT, zorder=2)
    ax.set_title(title, fontsize=12, pad=14)
    ax.text(total / 2, -(n + 0.75) * row_h, note, ha="center", va="center",
            fontsize=10, color=head_color)
    ax.set_xlim(-0.35, total + 0.35)
    ax.set_ylim(-(n + 1.6) * row_h, 0.55)
    ax.axis("off")


fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), gridspec_kw={"width_ratios": [1.28, 1]})

# (가) 넓은 형: 파일에 저장된 그대로
wide_rows = []
for name in ["강원특별자치도", "경기도", "울산광역시"]:
    r = g[g[g.columns[0]] == name].iloc[0]
    wide_rows.append([name, f"{int(r['2010']):,}", "…", f"{int(r['2023']):,}"])
wide_rows.append(["…", "…", "…", "…"])
draw_table(axes[0],
           [g.columns[0], "2010", "…", "2023"],
           wide_rows, [3.0, 1.5, 0.8, 1.5],
           f"(가) 넓은 형: 파일에 저장된 모양 ({NROW}행 {NYEAR}개 연도 열)",
           "연도가 열 제목 속에 숨어 있다", HEAD)

# (나) 긴 형: 연도를 열 하나로 편 모양
long_rows = []
for name in ["강원특별자치도", "강원특별자치도", "경기도"]:
    r = g[g[g.columns[0]] == name].iloc[0]
    yr = "2010" if len(long_rows) != 1 else "2023"
    long_rows.append([name, yr, f"{int(r[yr]):,}"])
long_rows.append(["…", "…", "…"])
draw_table(axes[1],
           ["시도", "연도", "1인당 지역내총생산"],
           long_rows, [3.0, 1.2, 2.6],
           f"(나) 긴 형: 연도를 열 하나로 편 모양 ({NROW * NYEAR}행 3열)",
           "한 행이 한 시도의 한 해", ACCENT)

fig.suptitle("같은 자료의 두 가지 모양 (data/grdp_sido.csv, 단위 천원)", fontsize=13, y=1.0)
fig.text(0.5, -0.02, "출처: 국가데이터처 지역소득, KOSIS 시도별 1인당 지역내총생산(DT_1C96)",
         ha="center", fontsize=9, color="#666666")
fig.tight_layout()
fig.savefig(FIG / "fig07_wide_long.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig07_wide_long.png")
