# 14주차 1차시(통합 장) 데이터 그림: 그림 14-4(2013년 대비 2023년 시군구 합계출산율)
# 공통 데이터(9주차 kosis MCP 수집 파일)에서 계산한다. 결합 규칙은 code/ch14_practice.py와 같다.
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 code/fig14_practice.py
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

d23 = pd.read_csv(BASE / "data" / "sigungu_mcp_2023.csv", encoding="utf-8-sig")
d13 = pd.read_csv(BASE / "data" / "sigungu_mcp_tfr_2013.csv", encoding="utf-8-sig")
rename = {("인천", "남구(변동전)"): ("인천", "미추홀구"),
          ("충북", "청주시(변동전)"): ("충북", "청주시"),
          ("경북", "군위군(변동전)"): ("대구", "군위군")}
for (s0, g0), (s1, g1) in rename.items():
    mask = (d13["시도"] == s0) & (d13["시군구"] == g0)
    d13.loc[mask, ["시도", "시군구"]] = [s1, g1]
m = d23.merge(d13, on=["시도", "시군구"], how="left", validate="one_to_one")
m = m.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
m["변화"] = m["합계출산율"] - m["합계출산율_2013"]
n_up = int((m["변화"] > 0).sum())
n_down = int((m["변화"] < 0).sum())

fig, ax = plt.subplots(figsize=(8.2, 7))
lim = (0.2, 2.5)
ax.plot(lim, lim, color="#888", lw=1.2, ls="--", zorder=1)
ax.text(2.02, 2.12, "변화 없음 (대각선)", fontsize=9.5, color="#666", rotation=45,
        rotation_mode="anchor", ha="left", va="bottom")
for name, mk, col in [("비수도권", "o", "#2f6fb0"), ("수도권", "^", "#c77b2f")]:
    g = m[m["수도권"] == name]
    ax.scatter(g["합계출산율_2013"], g["합계출산율"], marker=mk, s=34, alpha=0.7,
               color=col, edgecolor="white", lw=0.5, label=f"{name} ({len(g)}개)", zorder=2)

up = m[m["변화"] > 0].sort_values("합계출산율_2013")
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

print(f"saved: fig14_change_2013_2023.png / 하락 {n_down}개, 상승 {n_up}개, n={len(m)}")
