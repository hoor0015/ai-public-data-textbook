# 7주차 그림: 이상치 판단 예시 (박스플롯, sigungu_2023.csv 실제 데이터)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

d = pd.read_csv(BASE / "data" / "sigungu_2023.csv")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

# (가) 합계출산율 박스플롯
ax = axes[0]
sns.boxplot(x=d["합계출산율"].dropna(), ax=ax, color="#9ec3e0", width=0.35,
            flierprops=dict(marker="o", markerfacecolor="#c0392b",
                            markeredgecolor="#c0392b", markersize=5))
ax.set_title("(가) 합계출산율 (228개 시군구, 2023년)", fontsize=12)
ax.set_xlabel("합계출산율 (명)")
for sido, sgg, dy in [("전남", "영광군", 0.22), ("부산", "중구", 0.22)]:
    v = d.loc[(d["시도"] == sido) & (d["시군구"] == sgg), "합계출산율"].iloc[0]
    ax.annotate(f"{sido} {sgg} {v}", xy=(v, 0), xytext=(v - 0.12, -0.33),
                fontsize=10, color="#c0392b",
                arrowprops=dict(arrowstyle="->", color="#c0392b"))

# (나) 인구증가율 박스플롯
ax = axes[1]
sns.boxplot(x=d["인구증가율"], ax=ax, color="#b7dcc2", width=0.35,
            flierprops=dict(marker="o", markerfacecolor="#c0392b",
                            markeredgecolor="#c0392b", markersize=5))
ax.set_title("(나) 인구증가율 (229개 시군구, 2023년, %)", fontsize=12)
ax.set_xlabel("인구증가율 (%)")
for sido, sgg, tx, ty in [("대구", "중구", 8.6, -0.33), ("경기", "양주시", 6.4, 0.30)]:
    v = d.loc[(d["시도"] == sido) & (d["시군구"] == sgg), "인구증가율"].iloc[0]
    ax.annotate(f"{sido} {sgg} +{v}%", xy=(v, 0), xytext=(tx, ty),
                fontsize=10, color="#c0392b",
                arrowprops=dict(arrowstyle="->", color="#c0392b"))

for ax in axes:
    ax.set_ylim(-0.55, 0.55)
    ax.set_yticks([])

fig.suptitle("상자 밖의 점은 '지워야 할 값'이 아니라 '조사해야 할 값'이다",
             fontsize=12, y=1.02)
fig.tight_layout()
fig.savefig(FIG / "fig07_outlier.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig07_outlier.png")
