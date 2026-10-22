# 13주차 1차시(통합 장) 실습 그림: 그림 13-3 (검증 지점 4에서 대조할 그림의 기준 모습)
# 입력: data/sigungu_mcp_2023.csv, data/sigungu_mcp_tfr_2013.csv (9주차 MCP 수집 파일)
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 <이 파일 경로>
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

d2023 = pd.read_csv(BASE / "data" / "sigungu_mcp_2023.csv", encoding="utf-8-sig")
d2013 = pd.read_csv(BASE / "data" / "sigungu_mcp_tfr_2013.csv", encoding="utf-8-sig")
# ch13_practice.py와 같은 대응표: 옛 표기 연결 (청주시 2013년 값은 통합 전 옛 청주시 값)
for (s0, g0), (s1, g1) in {("인천", "남구(변동전)"): ("인천", "미추홀구"),
                           ("경북", "군위군(변동전)"): ("대구", "군위군"),
                           ("충북", "청주시(변동전)"): ("충북", "청주시")}.items():
    m = (d2013["시도"] == s0) & (d2013["시군구"] == g0)
    d2013.loc[m, ["시도", "시군구"]] = [s1, g1]
merged = d2023.merge(d2013, on=["시도", "시군구"], how="left", validate="one_to_one")
sub = merged.dropna(subset=["고령인구비율", "합계출산율"])
reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])

COL = {"수도권": "#c77b2f", "비수도권": "#4878a8"}
MK = {"수도권": "s", "비수도권": "o"}

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))

ax = axes[0]
for name in ["비수도권", "수도권"]:
    g = sub[sub["수도권"] == name]
    ax.scatter(g["고령인구비율"], g["합계출산율"], s=26, alpha=0.65, marker=MK[name],
               color=COL[name], edgecolor="white", lw=0.4, label=f"{name} ({len(g)}곳)")
xs = pd.Series([sub["고령인구비율"].min(), sub["고령인구비율"].max()])
ax.plot(xs, reg.intercept + reg.slope * xs, color="#a04747", lw=2, label="회귀선 (229곳 전체)")
y25 = reg.intercept + reg.slope * 25
ax.plot([25, 25], [0, y25], ls="--", color="#777", lw=1)
ax.plot([0, 25], [y25, y25], ls="--", color="#777", lw=1)
ax.annotate(f"고령인구비율 25%일 때\n회귀선 높이 {y25:.3f}명", xy=(25, y25), xytext=(30, 0.4),
            fontsize=9.5, arrowprops=dict(arrowstyle="->", color="#555"))
ax.set_xlim(8, 48)
ax.set_ylim(0.2, 1.8)
ax.set_title(f"(가) 고령인구비율과 합계출산율 (2023년, n = {len(sub)})", fontsize=12)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.legend(loc="upper left", fontsize=9)
ax.text(0.97, 0.95, f"기울기 {reg.slope:.5f}\nR제곱 {reg.rvalue ** 2:.3f}",
        transform=ax.transAxes, fontsize=10, va="top", ha="right",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))

ax = axes[1]
both = merged.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
both["변화"] = both["합계출산율"] - both["합계출산율_2013"]
for name in ["비수도권", "수도권"]:
    g = both[both["수도권"] == name]
    ax.scatter(g["합계출산율_2013"], g["합계출산율"], s=24, alpha=0.6, marker=MK[name],
               color=COL[name], edgecolor="white", lw=0.4, label=f"{name} ({len(g)}곳)")
ax.plot([0.3, 2.4], [0.3, 2.4], color="#777", lw=1, ls="--", label="변화 없음 (45도 선)")
up = both[both["변화"] > 0]
ax.scatter(up["합계출산율_2013"], up["합계출산율"], s=70, facecolor="none",
           edgecolor="black", lw=1.0, zorder=3, label=f"2023년이 높은 곳 ({len(up)}곳)")
offsets = {"의성군": (8, 4), "김제시": (8, -14), "영광군": (8, -10), "강화군": (8, -10)}
for _, r in up.iterrows():
    ax.annotate(f"{r['시도']} {r['시군구']}", (r["합계출산율_2013"], r["합계출산율"]),
                xytext=offsets.get(r["시군구"], (6, -10)), textcoords="offset points",
                fontsize=8.5)
ax.set_xlim(0.3, 2.4)
ax.set_ylim(0.3, 2.4)
ax.set_title(f"(나) 2013년 대비 2023년 합계출산율 ({len(both)}곳)", fontsize=12)
ax.set_xlabel("2013년 합계출산율 (명)")
ax.set_ylabel("2023년 합계출산율 (명)")
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "fig13_practice_checkpoint4.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved: fig13_practice_checkpoint4.png", len(sub), len(both), len(up), f"{y25:.3f}")
