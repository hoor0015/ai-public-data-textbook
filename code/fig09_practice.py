# 9주차 2회차(실습) 그림 생성: 그래프 다듬기 전과 후
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

df = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")
inc = pd.read_csv(BASE / "data" / "income_dist.csv", encoding="utf-8-sig")
sub = df.dropna(subset=["합계출산율"])
r = sub["고령인구비율"].corr(sub["합계출산율"])

# ---------------------------------------------------------------- 그림 9-10
# 그래프 다듬기 전과 후
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))

ax = axes[0]
ax.grid(False)
ax.scatter(sub["고령인구비율"], sub["합계출산율"], s=18)
ax.set_title("(가) 다듬기 전", fontsize=12, color="#888")

ax = axes[1]
ax.scatter(sub["고령인구비율"], sub["합계출산율"],
           s=28, alpha=0.6, color="#4878a8", edgecolor="white", lw=0.4)
ax.set_title("(나) 다듬기 후: 고령인구비율과 합계출산율 (2023년)",
             fontsize=12)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.text(0.03, 0.95, f"상관계수 r = {r:.2f}  (n = {len(sub)})",
        transform=ax.transAxes, fontsize=10, va="top",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
fig.tight_layout()
fig.savefig(FIG / "fig09_polish.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved: fig09_polish.png")
