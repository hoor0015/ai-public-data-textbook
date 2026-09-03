# 7주차 실습 그림 7-4: 정제 경로에 따라 같은 데이터의 분포가 어떻게 달라지는가 (sigungu_2023.csv 실제 데이터)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

d = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")


def iqr_mask(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)


out_idx = d.index[iqr_mask(d["합계출산율"]) | iqr_mask(d["인구증가율"])]
kept = d.drop(index=out_idx)                       # "이상치를 정리해 줘"의 결과: 26행 삭제
filled = d["합계출산율"].fillna(0)                   # "결측을 0으로 채워 줘"의 결과

rng = np.random.default_rng(7)
BOX = dict(medianprops=dict(color="black", linewidth=1.6), boxprops=dict(color="black"),
           whiskerprops=dict(color="black"), capprops=dict(color="black"))
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})

# (가) 합계출산율: 세 경로
ax = axes[0]
paths = [("원본 (결측 보존)", d["합계출산율"].dropna()),
         ("결측을 0으로 대치", filled),
         ("이상치 행 삭제", kept["합계출산율"].dropna())]
colors = ["#2f6fb0", "#c0392b", "#c77b2f"]
for i, (label, s) in enumerate(paths):
    y = i + rng.uniform(-0.18, 0.18, len(s))
    ax.scatter(s, y, s=12, color=colors[i], alpha=0.45, linewidths=0)
    ax.boxplot(s, positions=[i], vert=False, widths=0.5, showfliers=False, **BOX)
    ax.text(1.72, i - 0.36, f"n = {len(s)}, 평균 {s.mean():.3f}, 최소 {s.min():.3f}, 최대 {s.max():.3f}",
            fontsize=9, ha="right", va="center", color="#333333")
ax.set_yticks(range(3))
ax.set_yticklabels([p[0] for p in paths], fontsize=10)
ax.set_xlim(-0.05, 1.75)
ax.set_xlabel("합계출산율 (명)")
ax.set_title("(가) 같은 데이터, 세 가지 정제 경로: 합계출산율", fontsize=12)
ax.annotate("군위군 0.000\n(존재하지 않는 값)", xy=(0.0, 1), xytext=(0.1, 1.42), fontsize=9, color="#c0392b",
            arrowprops=dict(arrowstyle="->", color="#c0392b"))
ax.annotate("영광군 1.651과 부산 중구 0.320이\n있던 자리가 비어 있다", xy=(1.62, 2.05), xytext=(0.95, 2.62),
            fontsize=9, color="#c77b2f", arrowprops=dict(arrowstyle="->", color="#c77b2f"))
ax.set_ylim(2.95, -0.7)

# (나) 인구증가율: 원본 vs 이상치 삭제
ax = axes[1]
paths2 = [("원본", d["인구증가율"]), ("이상치 행 삭제", kept["인구증가율"])]
colors2 = ["#2f6fb0", "#c77b2f"]
for i, (label, s) in enumerate(paths2):
    y = i + rng.uniform(-0.18, 0.18, len(s))
    ax.scatter(s, y, s=12, color=colors2[i], alpha=0.45, linewidths=0)
    ax.boxplot(s, positions=[i], vert=False, widths=0.5, showfliers=False, **BOX)
    ax.text(-3.8, i - 0.36, f"n = {len(s)}, 평균 {s.mean():.2f}, 최대 {s.max():.2f}",
            fontsize=9, ha="left", va="center", color="#333333")
ax.set_yticks(range(2))
ax.set_yticklabels([p[0] for p in paths2], fontsize=10)
ax.set_xlim(-4, 12)
ax.set_xlabel("인구증가율 (%)")
ax.set_title("(나) 인구증가율: 이상치 삭제가 지우는 것", fontsize=12)
ax.annotate("대구 중구 11.05, 양주시 10.10 등\n14곳이 사라짐", xy=(11.05, 0.08), xytext=(5.0, 1.55), fontsize=9,
            color="#c77b2f", arrowprops=dict(arrowstyle="->", color="#c77b2f"))
ax.set_ylim(1.95, -0.7)

fig.tight_layout()
fig.savefig(FIG / "fig07_cleaning_paths.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig07_cleaning_paths.png")

# ---------------------------------------------------------------------------
# 그림 7-5: 결측 한 칸을 네 가지 방식으로 다루면 무엇이 달라지는가
s = d["합계출산율"]
mean_val = s.mean()
ways = [("표시만 (보존)", s.dropna(), None),
        ("행 제외", d.dropna(subset=["합계출산율"])["합계출산율"], None),
        ("평균으로 대치", s.fillna(mean_val), mean_val),
        ("0으로 대치", s.fillna(0), 0.0)]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.3, 1]})

ax = axes[0]
rng2 = np.random.default_rng(75)
for i, (label, v, gw) in enumerate(ways):
    y = i + rng2.uniform(-0.16, 0.16, len(v))
    ax.scatter(v, y, s=11, color="#2f6fb0", alpha=0.35, linewidths=0)
    ax.boxplot(v, positions=[i], vert=False, widths=0.46, showfliers=False, **BOX)
    if gw is None:
        ax.text(0.02, i - 0.34, "군위군: 데이터에 값이 없음", fontsize=9, color="#666666", va="center")
    else:
        ax.scatter([gw], [i], s=70, facecolor="#c0392b", edgecolor="black", zorder=5, linewidths=0.8)
        ax.text(gw + 0.03, i - 0.34, f"군위군: {gw:.3f}로 기록됨", fontsize=9, color="#c0392b", va="center")
    ax.text(1.73, i + 0.3, f"n = {len(v)}, 평균 {v.mean():.3f}, 표준편차 {v.std():.4f}",
            fontsize=9, ha="right", va="center", color="#333333")
ax.set_yticks(range(4))
ax.set_yticklabels([w[0] for w in ways], fontsize=10)
ax.set_xlim(-0.08, 1.78)
ax.set_ylim(3.95, -0.75)
ax.set_xlabel("합계출산율 (명)")
ax.set_title("(가) 결측 한 칸을 다루는 네 가지 방식", fontsize=12)

ax = axes[1]
lows = []
for label, v, gw in ways:
    frame = d.assign(값=s if gw is None else s.fillna(gw))
    if label == "행 제외":
        frame = frame.dropna(subset=["합계출산율"])
    frame = frame.dropna(subset=["값"]).nsmallest(1, "값").iloc[0]
    lows.append((label, f"{frame['시도']} {frame['시군구']}", float(frame["값"])))
names = [w[0] for w in ways]
vals = [x[2] for x in lows]
bars = ax.barh(range(4), vals, color=["#7f8c8d", "#7f8c8d", "#7f8c8d", "#c0392b"], height=0.5)
for i, (label, who, val) in enumerate(lows):
    ax.text(val + 0.012, i, f"{who}  {val:.3f}", va="center", fontsize=10,
            color="#c0392b" if i == 3 else "#333333")
ax.set_yticks(range(4))
ax.set_yticklabels(names, fontsize=10)
ax.set_ylim(3.6, -0.6)
ax.set_xlim(0, 0.52)
ax.set_xlabel("합계출산율 (명)")
ax.set_title("(나) 각 방식이 내놓는 '전국 최저 시군구'", fontsize=12)

fig.tight_layout()
fig.savefig(FIG / "fig07_missing_ways.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig07_missing_ways.png")
