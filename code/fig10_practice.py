# 10주차 2회차(실습) 그림 생성: 그림 10-5(분석 전 가정 확인), 그림 10-6(시도별 평균과 신뢰구간),
# 그림 10-7(잔차 그림과 한 점의 힘). 번호는 본문 등장 순서를 따른다.
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

df = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")
capital = ["서울", "경기", "인천"]
df["권역"] = np.where(df["시도"].isin(capital), "수도권", "비수도권")
order = ["수도권", "비수도권"]
pal = {"수도권": "#2f6fb0", "비수도권": "#c77b2f"}

# ---------------------------------------------------------------- 그림 10-5
# 분석 전 가정 확인: 두 집단의 고령인구비율 분포 모양과 흩어짐
bins = np.arange(10, 48, 2)
fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.4), sharex=True)
for ax, g in zip(axes, order):
    v = df.loc[df["권역"] == g, "고령인구비율"]
    ax.hist(v, bins=bins, color=pal[g], alpha=0.7, edgecolor="white")
    m, sd, med = v.mean(), v.std(ddof=1), v.median()
    ax.axvline(m, color="black", lw=1.6, ls="-")
    ax.axvline(med, color="black", lw=1.2, ls="--")
    ax.axvspan(m - sd, m + sd, color="gray", alpha=0.12)
    ax.text(0.98, 0.92,
            f"{g} (n = {len(v)})\n평균 {m:.1f}%  중앙값 {med:.1f}%\n표준편차 {sd:.1f}%포인트",
            transform=ax.transAxes, ha="right", va="top", fontsize=10.5,
            bbox=dict(fc="white", ec="#d9d9e3", boxstyle="round,pad=0.4"))
    ax.set_ylabel("시군구 수")
axes[0].set_title("수도권과 비수도권 시군구의 고령인구비율 분포 모양 (2023)", fontsize=13)
axes[1].set_xlabel("고령인구비율 (%)")
axes[0].text(0.02, 0.92, "실선 = 평균, 점선 = 중앙값\n회색 띠 = 평균 ± 1표준편차",
             transform=axes[0].transAxes, fontsize=9.5, va="top", color="#444")
fig.tight_layout()
fig.savefig(FIG / "fig10_assumption.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 10-7
# 잔차 그림과 한 점의 힘 (본문 2.7절)
sub = df.dropna(subset=["고령인구비율", "합계출산율"]).reset_index(drop=True)
x, y = sub["고령인구비율"].to_numpy(), sub["합계출산율"].to_numpy()
reg = stats.linregress(x, y)
sub["잔차"] = y - (reg.intercept + reg.slope * x)

fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))

# (가) 잔차 그림
ax = axes[0]
for g in order:
    d = sub[sub["권역"] == g]
    ax.scatter(d["고령인구비율"], d["잔차"], s=24, alpha=0.6, color=pal[g], label=g,
               edgecolor="white", linewidth=0.4)
ax.axhline(0, color="#c0392b", lw=1.8)
# 구간별 잔차 평균
cuts = pd.cut(sub["고령인구비율"], [0, 15, 20, 25, 30, 35, 50])
bm = sub.groupby(cuts, observed=True).agg(x=("고령인구비율", "mean"), r=("잔차", "mean"))
ax.plot(bm["x"], bm["r"], marker="s", color="black", lw=1.2, ms=6, label="구간별 잔차 평균")
labels = {("전남", "영광군"): (6, 4), ("부산", "중구"): (6, -14), ("강원", "인제군"): (6, 4)}
for (sido, sgg), off in labels.items():
    r = sub[(sub["시도"] == sido) & (sub["시군구"] == sgg)].iloc[0]
    ax.annotate(f"{sido} {sgg} ({r['잔차']:+.2f})", (r["고령인구비율"], r["잔차"]),
                xytext=off, textcoords="offset points", fontsize=9.5)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("잔차 = 실제 출산율 - 예측 출산율 (명)")
ax.set_title("(가) 잔차 그림: 직선이 빗나간 정도", fontsize=12)
ax.set_ylim(-0.72, 0.88)
ax.legend(loc="lower left", fontsize=9)

# (나) 한 점을 뺐을 때 회귀선의 변화
ax = axes[1]
ax.scatter(x, y, s=20, alpha=0.4, color="#888", edgecolor="white", linewidth=0.4)
tgt = sub[(sub["시도"] == "경북") & (sub["시군구"] == "의성군")].iloc[0]
ax.scatter(tgt["고령인구비율"], tgt["합계출산율"], s=110, color="#c0392b", edgecolor="black",
           zorder=5, label="경북 의성군 (고령인구비율 최고)")
m = ~((sub["시도"] == "경북") & (sub["시군구"] == "의성군")).to_numpy()
reg2 = stats.linregress(x[m], y[m])
xs = np.linspace(x.min(), x.max(), 100)
ax.plot(xs, reg.intercept + reg.slope * xs, color="#c0392b", lw=2.4,
        label=f"전체 228개: 기울기 {reg.slope:.5f}")
ax.plot(xs, reg2.intercept + reg2.slope * xs, color="#2f6fb0", lw=2.2, ls="--",
        label=f"의성군 제외 227개: 기울기 {reg2.slope:.5f}")
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.set_title("(나) 한 점을 빼면 회귀선이 얼마나 움직이나", fontsize=12)
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "fig10_residuals.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 10-6
# 시도별 고령인구비율 평균과 95% 신뢰구간 (본문 2.5절)
rows = []
for sido, v in df.groupby("시도")["고령인구비율"]:
    n, m = len(v), v.mean()
    if n < 2:
        rows.append(dict(시도=sido, n=n, 평균=m, 하한=np.nan, 상한=np.nan))
        continue
    se = v.std(ddof=1) / np.sqrt(n)
    tc = stats.t.ppf(0.975, n - 1)
    rows.append(dict(시도=sido, n=n, 평균=m, 하한=m - tc * se, 상한=m + tc * se))
sido_ci = pd.DataFrame(rows).sort_values("평균").reset_index(drop=True)
nation = df["고령인구비율"].mean()
XLO, XHI = 8.0, 42.0

fig, ax = plt.subplots(figsize=(9.0, 6.6))
ax.axvline(nation, color="#7a5fa8", lw=1.4, ls="--", zorder=1)
ax.text(nation + 0.4, -0.75, f"전국 229개 시군구 평균 {nation:.1f}%",
        color="#7a5fa8", fontsize=9.5, va="center")
for i, r in sido_ci.iterrows():
    c = pal["수도권"] if r["시도"] in capital else pal["비수도권"]
    if np.isnan(r["하한"]):
        ax.plot([r["평균"]], [i], marker="o", ms=7, color=c, mfc="white", mew=1.8, zorder=4)
        ax.annotate("시군구가 1개여서 구간을 만들 수 없다", (r["평균"], i), xytext=(10, 0),
                    textcoords="offset points", va="center", fontsize=9.5, color="#555")
        continue
    ax.plot([r["하한"], r["상한"]], [i, i], color=c, lw=2.6, solid_capstyle="butt", zorder=2)
    for xv in (r["하한"], r["상한"]):
        if XLO < xv < XHI:
            ax.plot([xv, xv], [i - 0.22, i + 0.22], color=c, lw=1.6, zorder=3)
    ax.plot([r["평균"]], [i], marker="o", ms=6.5, color=c, zorder=4)
jeju = sido_ci[sido_ci["시도"] == "제주"].iloc[0]
ax.text(XHI - 0.5, sido_ci[sido_ci["시도"] == "제주"].index[0] + 0.52,
        f"제주의 구간은 {jeju['하한']:.1f}%에서 {jeju['상한']:.1f}%까지다",
        fontsize=9.5, color="#c0392b", ha="right", va="center",
        bbox=dict(fc="white", ec="none", pad=1.5))
ax.set_yticks(range(len(sido_ci)))
ax.set_yticklabels([f"{r['시도']} ({int(r['n'])}개)" for _, r in sido_ci.iterrows()])
ax.invert_yaxis()
ax.set_xlim(XLO, XHI)
ax.set_ylim(len(sido_ci) - 0.3, -1.3)
ax.set_xlabel("고령인구비율 (%)")
ax.set_title("시도별 고령인구비율 평균과 95% 신뢰구간 (2023, 시군구 단위)", fontsize=13)
ax.text(0.015, 0.03, "점 = 시도 안 시군구의 평균, 가로 막대 = 95% 신뢰구간\n"
                     "파랑 = 수도권, 주황 = 비수도권, 괄호 안 = 그 시도의 시군구 수",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=9.5,
        bbox=dict(fc="white", ec="#d9d9e3", boxstyle="round,pad=0.4"))
fig.tight_layout()
fig.savefig(FIG / "fig10_sido_ci.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"그림 10-6 보조 수치: 전국 평균 {nation:.4f}, 시도 수 {len(sido_ci)}, "
      f"구간 없는 시도 {sido_ci.loc[sido_ci['하한'].isna(), '시도'].tolist()}")

print("saved:", [p.name for p in sorted(FIG.glob("fig10_*.png"))])
