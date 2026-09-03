# 10주차 2회차(실습) 그림 생성: 그림 10-5(분석 전 가정 확인), 그림 10-6(표본 크기의 효과),
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
# 표본 크기를 줄이면 결과가 어떻게 흔들리나 (본문 2.5절)
def welch_diff_ci(frame, var="고령인구비율"):
    a = frame.loc[frame["권역"] == "수도권", var].dropna()
    b = frame.loc[frame["권역"] == "비수도권", var].dropna()
    if len(a) < 2 or len(b) < 2:
        return None
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va / na + vb / nb)
    dfw = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    diff = b.mean() - a.mean()
    tc = stats.t.ppf(0.975, dfw)
    return diff, diff - tc * se, diff + tc * se


full_d, full_lo, full_hi = welch_diff_ci(df)
res50 = [welch_diff_ci(df.sample(n=50, random_state=s)) for s in range(500)]
res20 = [welch_diff_ci(df.sample(n=20, random_state=s)) for s in range(500)]
res50 = [r for r in res50 if r]
res20 = [r for r in res20 if r]

fig, axes = plt.subplots(1, 2, figsize=(12, 5.0))

ax = axes[0]
bins2 = np.arange(0, 20.5, 1.0)
ax.hist([r[0] for r in res20], bins=bins2, color="#c77b2f", alpha=0.55,
        edgecolor="white", label="표본 20개 (500번)")
ax.hist([r[0] for r in res50], bins=bins2, color="#2f6fb0", alpha=0.65,
        edgecolor="white", label="표본 50개 (500번)")
ax.axvline(full_d, color="#c0392b", lw=2.2)
ax.annotate(f"전체 229개의 차이 {full_d:.2f}", (full_d, ax.get_ylim()[1] * 0.62),
            xytext=(-8, 0), textcoords="offset points", ha="right", color="#c0392b", fontsize=10.5)
ax.set_xlabel("표본에서 계산한 평균 차이 (%포인트)")
ax.set_ylabel("표본 수 (500번 중)")
ax.set_title("(가) 표본을 다시 뽑을 때마다 달라지는 차이", fontsize=12)
ax.legend(loc="upper right", fontsize=9.5)

ax = axes[1]
show = res50[:30]
for i, (d_i, lo_i, hi_i) in enumerate(show):
    hit = lo_i <= full_d <= hi_i
    ax.plot([lo_i, hi_i], [i, i], color="#2f6fb0" if hit else "#c0392b", lw=2.0,
            solid_capstyle="butt")
    ax.plot([d_i], [i], marker="o", ms=4, color="#2f6fb0" if hit else "#c0392b")
ax.plot([full_lo, full_hi], [-3, -3], color="black", lw=3.6, solid_capstyle="butt")
ax.plot([full_d], [-3], marker="D", ms=6.5, color="black")
ax.axvline(full_d, color="#c0392b", lw=1.4, ls="--")
ax.text(full_d, -4.6, f"전체 229개의 신뢰구간 {full_lo:.2f} - {full_hi:.2f}",
        ha="center", va="top", fontsize=9.5)
ax.set_ylim(-7, 33)
ax.set_yticks([])
ax.set_xlabel("평균 차이의 95% 신뢰구간 (%포인트)")
ax.set_title("(나) 표본 50개로 만든 신뢰구간 30개", fontsize=12)
n_hit = sum(1 for d_i, lo_i, hi_i in res50 if lo_i <= full_d <= hi_i)
ax.text(0.02, 0.98, f"파란 구간은 전체 값 {full_d:.2f}를 담은 것,\n"
                    f"빨간 구간은 담지 못한 것\n"
                    f"(500개 중 {n_hit}개, {n_hit / len(res50) * 100:.1f}%가 담았다)",
        transform=ax.transAxes, fontsize=9.5, va="top",
        bbox=dict(fc="white", ec="#d9d9e3", boxstyle="round,pad=0.4"))
fig.tight_layout()
fig.savefig(FIG / "fig10_samplesize.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"그림 10-6 보조 수치: 전체 차이 {full_d:.4f}, 전체 CI [{full_lo:.4f}, {full_hi:.4f}], "
      f"50개 표본 500개 중 전체 값 포함 {n_hit}개")

print("saved:", [p.name for p in sorted(FIG.glob("fig10_*.png"))])
