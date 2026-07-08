# 9주차 데이터 그림 생성 (집단 비교 박스플롯, 산점도와 회귀선)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

df = pd.read_csv(BASE / "data" / "sigungu_2023.csv")
capital = ["서울", "경기", "인천"]
df["권역"] = np.where(df["시도"].isin(capital), "수도권", "비수도권")
order = ["수도권", "비수도권"]
pal = {"수도권": "#2f6fb0", "비수도권": "#c77b2f"}

# ---------------------------------------------------------------- 그림 9-2
# 수도권 vs 비수도권 고령인구비율 분포 비교
fig, ax = plt.subplots(figsize=(8.5, 5.5))
sns.boxplot(data=df, x="권역", y="고령인구비율", order=order, palette=pal,
            width=0.45, fliersize=0, boxprops=dict(alpha=0.55), ax=ax)
sns.stripplot(data=df, x="권역", y="고령인구비율", order=order, palette=pal,
              size=3.5, alpha=0.55, jitter=0.12, ax=ax)
for i, g in enumerate(order):
    m = df.loc[df["권역"] == g, "고령인구비율"].mean()
    ax.scatter(i, m, marker="D", s=70, color="white", edgecolor="black", zorder=5)
    ax.annotate(f"평균 {m:.1f}%", (i, m), xytext=(i + 0.27, m - 0.4), fontsize=11,
                fontweight="bold")
ax.set_ylabel("고령인구비율 (%)")
ax.set_xlabel("")
ax.set_title("수도권과 비수도권 시군구의 고령인구비율 분포 (2023)", fontsize=13)
fig.tight_layout()
fig.savefig(FIG / "fig09_group_compare.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-3
# 고령인구비율과 합계출산율: 산점도 + 회귀선
sub = df.dropna(subset=["고령인구비율", "합계출산율"])
reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])

fig, ax = plt.subplots(figsize=(8.5, 5.8))
for g in order:
    d = sub[sub["권역"] == g]
    ax.scatter(d["고령인구비율"], d["합계출산율"], s=26, alpha=0.65,
               color=pal[g], label=g, edgecolor="white", linewidth=0.4)
xs = np.linspace(sub["고령인구비율"].min(), sub["고령인구비율"].max(), 100)
ax.plot(xs, reg.intercept + reg.slope * xs, color="#c0392b", lw=2.4, label="회귀선")
ax.text(0.03, 0.95,
        f"합계출산율 = {reg.intercept:.3f} + {reg.slope:.4f} x 고령인구비율\n"
        f"상관계수 r = {reg.rvalue:.2f},  R제곱 = {reg.rvalue**2:.2f}",
        transform=ax.transAxes, fontsize=11, va="top",
        bbox=dict(fc="white", ec="#d9d9e3", boxstyle="round,pad=0.4"))
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.set_title("시군구의 고령인구비율과 합계출산율 (2023, 228개)", fontsize=13)
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "fig09_scatter_reg.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig09_*.png'))])
