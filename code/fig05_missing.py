# 5주차 2회차: sigungu_2023.csv 열별 결측 현황 막대그래프
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

df = pd.read_csv(BASE / "data" / "sigungu_2023.csv")
missing = df.isnull().sum()

fig, ax = plt.subplots(figsize=(9, 4.6))
colors = ["#c77b2f" if v > 0 else "#a8c4de" for v in missing]
bars = ax.bar(missing.index, missing.values, color=colors, edgecolor="#555", lw=0.6)
for bar, v in zip(bars, missing.values):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, str(int(v)),
            ha="center", va="bottom", fontsize=10,
            fontweight="bold" if v > 0 else "normal",
            color="#c77b2f" if v > 0 else "#666")
ax.set_ylim(0, 1.4)
ax.set_yticks([0, 1])
ax.grid(axis="x", visible=False)
ax.set_ylabel("결측 개수 (전체 229행 중)")
ax.set_title("sigungu_2023.csv 열별 결측 현황: 합계출산율과 출생아수에 각 1개", fontsize=13, pad=12)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=10)
sns.despine(left=True)
fig.tight_layout()
fig.savefig(FIG / "fig05_missing.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig05_missing.png / missing =", dict(missing[missing > 0]))
