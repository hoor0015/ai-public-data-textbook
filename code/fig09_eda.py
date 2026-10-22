# 9주차 1차시(이론) 그림 생성: 그림 9-1부터 9-18까지 (본문 등장 순서)
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 code/fig09_eda.py
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import gaussian_kde

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)
RAW = BASE / "data" / "raw_mcp"

df = pd.read_csv(BASE / "data" / "sigungu_mcp_2023.csv", encoding="utf-8-sig")
inc = pd.read_csv(BASE / "data" / "income_dist.csv", encoding="utf-8-sig")

SIDO = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기",
        "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
FULL = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
        "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
        "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기",
        "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남",
        "전북특별자치도": "전북", "전라남도": "전남", "경상북도": "경북",
        "경상남도": "경남", "제주특별자치도": "제주", "전국": "전국"}
C_CAP, C_NON = "#2f6fb0", "#e0975a"      # 수도권, 비수도권
df["권역"] = np.where(df["시도"].isin(["서울", "경기", "인천"]), "수도권", "비수도권")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def sido_rows(path, item=None):
    """kosis 원 응답 CSV에서 전국·시도 행만 뽑아 {약칭: 값}으로 돌려준다."""
    raw = pd.read_csv(path, encoding="utf-8-sig")
    if item is not None:
        raw = raw[raw["항목"] == item]
    raw = raw[raw["분류1"].isin(FULL)].drop_duplicates("분류1")
    return {FULL[k]: float(v) for k, v in zip(raw["분류1"], raw["값"])}


# ================================================================ 1.2
# ---------------------------------------------------------------- 그림 9-1
# 고령인구비율 히스토그램
fig, ax = plt.subplots(figsize=(8, 5))
bins = np.arange(10, 47.5, 2.5)
ax.hist(df["고령인구비율"], bins=bins, color="#7fa8d9", edgecolor="white")
mean_v = df["고령인구비율"].mean()
med_v = df["고령인구비율"].median()
ax.axvline(med_v, color="#c0392b", lw=1.8, ls="--",
           label=f"중앙값 {med_v:.1f}%")
ax.axvline(mean_v, color="#2c3e50", lw=1.8, ls=":",
           label=f"평균 {mean_v:.1f}%")
ax.set_title("시군구 고령인구비율의 분포 (2023년, 229개 시군구)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("시군구 수 (개)")
ax.legend()
ax.annotate("오른쪽으로 길게 뻗은 꼬리:\n고령화가 극심한 농촌 군 지역",
            xy=(41, 6), xytext=(33.5, 22),
            arrowprops=dict(arrowstyle="->", color="#555"),
            fontsize=10, color="#333")
save(fig, "fig09_hist_aging.png")

# ---------------------------------------------------------------- 그림 9-2
# 밀도 그림: (가) 히스토그램 위의 밀도 곡선 (나) 권역별 밀도 곡선 겹치기
age = df["고령인구비율"]
xs_d = np.linspace(0, 55, 551)
kde_all = gaussian_kde(age)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
ax = axes[0]
ax.hist(age, bins=bins, density=True, color="#c9daf0", edgecolor="white",
        label="히스토그램 (막대 넓이의 합 = 1)")
ax.plot(xs_d, kde_all(xs_d), color="#2c3e50", lw=2, label="밀도 곡선")
ax.axvline(age.min(), color="#888", lw=1, ls=":")
ax.text(age.min() - 1.2, 0.012, f"실제 최솟값\n{age.min():.1f}%", ha="right",
        fontsize=9, color="#555")
ax.set_xlim(0, 55)
ax.set_title("(가) 히스토그램과 밀도 곡선", fontsize=12)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("밀도")
ax.legend(fontsize=9, loc="upper right")
ax = axes[1]
peaks = {}
for g, c in [("수도권", C_CAP), ("비수도권", C_NON)]:
    s = df.loc[df["권역"] == g, "고령인구비율"]
    k = gaussian_kde(s)
    y = k(xs_d)
    peaks[g] = xs_d[y.argmax()]
    ax.plot(xs_d, y, color=c, lw=2, label=f"{g} (n = {len(s)})")
    ax.fill_between(xs_d, y, color=c, alpha=0.15)
ax.set_xlim(0, 55)
ax.set_title("(나) 수도권과 비수도권의 밀도 곡선 겹치기", fontsize=12)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("밀도")
ax.legend(fontsize=9.5)
fig.suptitle("시군구 고령인구비율의 밀도 그림 (2023년)", fontsize=13, y=1.02)
save(fig, "fig09_density_aging.png")
# 밀도 곡선이 0.001 이상인 가장 왼쪽 x (자료 밖으로 번진 정도 확인용)
kde_left = xs_d[(kde_all(xs_d) >= 0.001).argmax()]

# ---------------------------------------------------------------- 그림 9-3
# 누적분포 그림 (경험적 누적분포)
sv = np.sort(age.values)
cum = np.arange(1, len(sv) + 1) / len(sv)
share20 = (age <= 20).mean()
share30 = (age <= 30).mean()
q90 = age.quantile(0.9)
fig, ax = plt.subplots(figsize=(8, 5))
ax.step(sv, cum, where="post", color="#2f6fb0", lw=2)
ax.axhline(0.5, color="#c0392b", lw=1, ls="--")
ax.axvline(med_v, color="#c0392b", lw=1, ls="--")
ax.text(med_v + 0.4, 0.06, f"중앙값 {med_v:.1f}%\n(세로 0.5)", fontsize=9.5,
        color="#c0392b")
for x0, sh in [(20, share20), (30, share30)]:
    ax.plot([x0, x0], [0, sh], color="#555", lw=1, ls=":")
    ax.plot([8, x0], [sh, sh], color="#555", lw=1, ls=":")
    ax.text(8.3, sh + 0.015, f"{x0}% 이하: {sh * 100:.1f}%", fontsize=9.5,
            color="#333")
ax.set_xlim(8, 48)
ax.set_ylim(0, 1.02)
ax.set_title("시군구 고령인구비율의 누적분포 (2023년, 229개 시군구)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("그 값 이하인 시군구의 비율")
save(fig, "fig09_ecdf_aging.png")

# ---------------------------------------------------------------- 그림 9-4
# 막대그래프: 시도별 시군구 수 (많은 순)
cnt = df["시도"].value_counts()
fig, ax = plt.subplots(figsize=(9, 4.8))
bars = ax.bar(cnt.index, cnt.values, color="#7fa8d9", width=0.65)
for b, v in zip(bars, cnt.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.4, str(v), ha="center",
            fontsize=9.5)
ax.set_ylim(0, cnt.max() + 4)
ax.set_title("시도별 시군구 수 (2023년, 합계 229개)", fontsize=13)
ax.set_xlabel("시도")
ax.set_ylabel("시군구 수 (개)")
save(fig, "fig09_bar_sido_count.png")

# ---------------------------------------------------------------- 그림 9-5
# 시도별 고령인구비율 박스플롯 (중앙값 오름차순)
order = (df.groupby("시도")["고령인구비율"].median()
           .sort_values().index.tolist())
fig, ax = plt.subplots(figsize=(8, 7))
sns.boxplot(data=df, y="시도", x="고령인구비율", order=order,
            color="#a8c4e0", width=0.6, fliersize=4, ax=ax,
            medianprops=dict(color="#c0392b", lw=2))
ax.set_title("시도별 고령인구비율 분포 (2023년)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("")
save(fig, "fig09_box_sido.png")

# ---------------------------------------------------------------- 그림 9-6
# 바이올린 그림과 스트립 그림 (시군구가 15개 이상인 시도 중 6곳)
six = ["서울", "경기", "강원", "경북", "전남", "경남"]
d6 = df[df["시도"].isin(six)]
order6 = d6.groupby("시도")["고령인구비율"].median().sort_values().index.tolist()
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
ax = axes[0]
sns.violinplot(data=d6, x="시도", y="고령인구비율", order=order6,
               color="#a8c4e0", inner="quartile", cut=0, ax=ax)
ax.set_title("(가) 바이올린 그림", fontsize=12)
ax.set_xlabel("")
ax.set_ylabel("고령인구비율 (%)")
ax = axes[1]
sns.boxplot(data=d6, x="시도", y="고령인구비율", order=order6,
            color="#e8eef6", width=0.55, fliersize=0, ax=ax,
            medianprops=dict(color="#c0392b", lw=2))
sns.stripplot(data=d6, x="시도", y="고령인구비율", order=order6,
              color="#2f6fb0", size=4.5, jitter=0.18, alpha=0.8, ax=ax)
ax.set_title("(나) 박스플롯 위에 시군구를 점으로 찍은 스트립 그림", fontsize=12)
ax.set_xlabel("")
ax.set_ylabel("")
for i, s in enumerate(order6):
    n = int((d6["시도"] == s).sum())
    axes[0].text(i, 49, f"n={n}", ha="center", fontsize=9, color="#555")
    axes[1].text(i, 49, f"n={n}", ha="center", fontsize=9, color="#555")
axes[0].set_ylim(8, 51)
fig.suptitle("같은 여섯 시도의 고령인구비율을 두 방식으로 (2023년)",
             fontsize=13, y=1.02)
save(fig, "fig09_violin_strip.png")

# ---------------------------------------------------------------- 그림 9-7
# 점 그림: 시도별 고령인구비율 (시도 값과 시군구 단순 평균)
aging_sido = sido_rows(RAW / "mcp_고령인구비율_DT_1YL20631_2023.csv")
sgg_mean = df.groupby("시도")["고령인구비율"].mean()
dot = pd.DataFrame({"시도값": pd.Series(aging_sido), "단순평균": sgg_mean})
dot = dot.loc[SIDO].sort_values("시도값")
fig, ax = plt.subplots(figsize=(8, 6.5))
yy = np.arange(len(dot))
ax.hlines(yy, 0, dot["시도값"], color="#ddd", lw=1)
ax.scatter(dot["시도값"], yy, s=55, color="#2f6fb0", zorder=3,
           label="시도 전체의 고령인구비율 (같은 통계표의 시도 행)")
ax.scatter(dot["단순평균"], yy, s=55, facecolor="white", edgecolor="#c0392b",
           lw=1.6, zorder=3, label="소속 시군구 값의 단순 평균")
ax.set_yticks(yy)
ax.set_yticklabels(dot.index)
ax.set_xlim(0, 40)
ax.set_title("시도별 고령인구비율: 시도 값 순으로 정렬 (2023년)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.legend(loc="lower right", fontsize=9.5)
save(fig, "fig09_dot_sido.png")

# ---------------------------------------------------------------- 그림 9-8
# 막대 위 오차막대: 권역별 평균 ± 표준편차
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
eb = {}
for ax, var, unit in [(axes[0], "고령인구비율", "%"), (axes[1], "합계출산율", "명")]:
    st = (df.groupby("권역")[var].agg(["mean", "std", "count"])
            .loc[["수도권", "비수도권"]])
    eb[var] = st
    ax.bar([0, 1], st["mean"], color=["#7fa8d9", C_NON], width=0.5)
    ax.errorbar([0, 1], st["mean"], yerr=st["std"], fmt="none",
                ecolor="#2c3e50", capsize=8, lw=1.6)
    for i, (m, s, n) in enumerate(zip(st["mean"], st["std"], st["count"])):
        ax.text(i + 0.29, m, f"평균 {m:.2f}\n표준편차 {s:.2f}\nn = {n}",
                fontsize=9, va="center")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["수도권", "비수도권"])
    ax.set_xlim(-0.5, 1.95)
    ax.set_ylim(0, (st["mean"] + st["std"]).max() * 1.15)
    ax.set_ylabel(f"{var} ({unit})")
axes[0].set_title("(가) 고령인구비율", fontsize=12)
axes[1].set_title("(나) 합계출산율", fontsize=12)
fig.suptitle("권역별 시군구 평균과 표준편차 오차막대 (2023년)", fontsize=13, y=1.02)
save(fig, "fig09_errorbar_region.png")

# ================================================================ 1.3
# ---------------------------------------------------------------- 그림 9-9
# 산점도: 고령인구비율 vs 합계출산율
sub = df.dropna(subset=["합계출산율"])
r = sub["고령인구비율"].corr(sub["합계출산율"])
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(sub["고령인구비율"], sub["합계출산율"],
           s=28, alpha=0.6, color="#4878a8", edgecolor="white", lw=0.4)
coef = np.polyfit(sub["고령인구비율"], sub["합계출산율"], 1)
xs = np.linspace(sub["고령인구비율"].min(), sub["고령인구비율"].max(), 50)
ax.plot(xs, np.polyval(coef, xs), color="#c0392b", lw=1.6, ls="--",
        label="추세선")


def _pt(sido, sgg):
    row = sub[(sub["시도"] == sido) & (sub["시군구"] == sgg)].iloc[0]
    return row["고령인구비율"], row["합계출산율"]


marks = [("전남 영광군", *_pt("전남", "영광군"), (23.5, 1.62)),
         ("경북 의성군", *_pt("경북", "의성군"), (40.5, 1.55)),
         ("부산 중구", *_pt("부산", "중구"), (32.5, 0.34)),
         ("경기 화성시", *_pt("경기", "화성시"), (11.2, 1.08))]
for name, x, y, (tx, ty) in marks:
    ax.annotate(name, xy=(x, y), xytext=(tx, ty), fontsize=9.5,
                color="#333",
                arrowprops=dict(arrowstyle="->", color="#888", lw=0.9))
ax.text(0.03, 0.95, f"상관계수 r = {r:.2f}  (n = {len(sub)})",
        transform=ax.transAxes, fontsize=10.5, va="top",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
ax.set_title("고령인구비율과 합계출산율의 관계 (2023년)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.legend(loc="lower right")
save(fig, "fig09_scatter_aging_tfr.png")

# ---------------------------------------------------------------- 그림 9-10
# 로그 축 산점도: 인구밀도 vs 고령인구비율
r_lin = df["인구밀도"].corr(df["고령인구비율"])
r_log = np.log10(df["인구밀도"]).corr(df["고령인구비율"])
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, logx, title, rr in [(axes[0], False, "(가) 보통 축", r_lin),
                            (axes[1], True, "(나) 가로축을 로그 눈금으로", r_log)]:
    ax.scatter(df["인구밀도"], df["고령인구비율"], s=22, alpha=0.6,
               color="#4878a8", edgecolor="white", lw=0.4)
    if logx:
        ax.set_xscale("log")
        ax.set_xticks([10, 100, 1000, 10000])
        ax.set_xticklabels(["10", "100", "1,000", "10,000"])
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("인구밀도 (명/km²)")
    ax.text(0.97, 0.95, f"r = {rr:.2f}", transform=ax.transAxes, ha="right",
            va="top", fontsize=10.5,
            bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
axes[0].set_ylabel("고령인구비율 (%)")
fig.suptitle("인구밀도와 고령인구비율 (2023년, 229개 시군구)", fontsize=13, y=1.02)
save(fig, "fig09_log_scatter.png")

# ---------------------------------------------------------------- 그림 9-11
# 집단별 색을 입힌 산점도
fig, ax = plt.subplots(figsize=(8, 5.5))
r_grp = {}
for g, c, mk in [("비수도권", C_NON, "o"), ("수도권", C_CAP, "s")]:
    s = sub[sub["권역"] == g]
    r_grp[g] = (s["고령인구비율"].corr(s["합계출산율"]), len(s))
    ax.scatter(s["고령인구비율"], s["합계출산율"], s=28, alpha=0.7, color=c,
               marker=mk, edgecolor="white", lw=0.4,
               label=f"{g} (n = {len(s)}, r = {r_grp[g][0]:.2f})")
ax.set_title("권역별로 색을 나눈 산점도: 고령인구비율과 합계출산율 (2023년)",
             fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.legend(loc="lower right")
save(fig, "fig09_scatter_region.png")

# ---------------------------------------------------------------- 그림 9-12
# 소다중: 시도별 패널 (세종 제외 16개)
sm_list = [s for s in SIDO if s != "세종"]
fig, axes = plt.subplots(4, 4, figsize=(11, 10), sharex=True, sharey=True)
r_sido = {}
for ax, s in zip(axes.flat, sm_list):
    ax.scatter(sub["고령인구비율"], sub["합계출산율"], s=8, color="#d5d5d5",
               lw=0)
    ss = sub[sub["시도"] == s]
    ax.scatter(ss["고령인구비율"], ss["합계출산율"], s=18,
               color=C_CAP if s in ("서울", "경기", "인천") else C_NON,
               edgecolor="white", lw=0.3)
    r_sido[s] = (ss["고령인구비율"].corr(ss["합계출산율"]), len(ss))
    ax.set_title(f"{s} (n = {len(ss)})", fontsize=11)
for ax in axes[-1]:
    ax.set_xlabel("고령인구비율 (%)")
for ax in axes[:, 0]:
    ax.set_ylabel("합계출산율 (명)")
fig.suptitle("시도별 소다중 산점도: 회색은 전국 229개, 색 점은 그 시도 (2023년)",
             fontsize=13, y=1.0)
save(fig, "fig09_small_multiples.png")

# ---------------------------------------------------------------- 그림 9-13
# 산점도 행렬 (짝 그림)
pv = df[["고령인구비율", "합계출산율", "인구증가율", "인구밀도", "권역"]].copy()
pv["인구밀도(로그)"] = np.log10(pv["인구밀도"])
pv = pv.drop(columns="인구밀도").dropna()
pvars = ["고령인구비율", "합계출산율", "인구증가율", "인구밀도(로그)"]
g = sns.pairplot(pv, vars=pvars, hue="권역", hue_order=["비수도권", "수도권"],
                 palette={"수도권": C_CAP, "비수도권": C_NON},
                 diag_kind="hist", corner=True, height=2.3,
                 plot_kws=dict(s=14, alpha=0.6, edgecolor="white", lw=0.3),
                 diag_kws=dict(element="step", alpha=0.35))
g.figure.suptitle("네 변수의 산점도 행렬 (2023년, 인구밀도는 상용로그 값)",
                  fontsize=13, y=1.02)
g.figure.savefig(FIG / "fig09_pairplot.png", dpi=150, bbox_inches="tight")
plt.close(g.figure)
n_pair = len(pv)

# ---------------------------------------------------------------- 그림 9-14
# 상관 히트맵 (여섯 변수)
hv = df[["고령인구비율", "중위연령", "유소년부양비", "합계출산율", "인구증가율"]].copy()
hv.insert(0, "인구밀도(로그)", np.log10(df["인구밀도"]))
cm = hv.corr()
mask = np.triu(np.ones_like(cm, dtype=bool), k=1)
fig, ax = plt.subplots(figsize=(7.6, 6.2))
sns.heatmap(cm, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1,
            vmax=1, square=True, linewidths=0.6,
            cbar_kws=dict(shrink=0.75, label="상관계수 r"),
            annot_kws=dict(fontsize=10), ax=ax)
ax.set_title("여섯 변수의 상관 히트맵 (2023년, 229개 시군구)", fontsize=13)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
plt.setp(ax.get_yticklabels(), rotation=0)
save(fig, "fig09_corr_heatmap.png")

# ================================================================ 1.4
# ---------------------------------------------------------------- 그림 9-15
# 지니계수 시계열
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(inc["연도"], inc["지니계수"], marker="o", color="#2f6fb0", lw=2)
ax.set_ylim(0.30, 0.40)
ax.set_xticks(inc["연도"])
ax.set_title("지니계수 추이 (2011-2023년, 처분가능소득 기준)", fontsize=13)
ax.set_xlabel("연도")
ax.set_ylabel("지니계수")
first, last = inc["지니계수"].iloc[0], inc["지니계수"].iloc[-1]
ax.annotate(f"{first:.3f}", xy=(2011, first), xytext=(2011, first + 0.006),
            fontsize=10, ha="center", color="#2f6fb0")
ax.annotate(f"{last:.3f}", xy=(2023, last), xytext=(2023, last + 0.006),
            fontsize=10, ha="center", color="#2f6fb0")
save(fig, "fig09_line_gini.png")

# ---------------------------------------------------------------- 그림 9-16
# 두 시점: 기울기 그림과 덤벨 그림 (시도 합계출산율 2013, 2023)
t13 = sido_rows(RAW / "mcp_합계출산율2013_DT_1B81A23_2013.csv")
t23 = sido_rows(RAW / "mcp_합계출산율_DT_1B81A23_2023.csv", item="합계출산율")
tt = pd.DataFrame({"2013": pd.Series(t13), "2023": pd.Series(t23)}).loc[SIDO]
tt["변화"] = tt["2023"] - tt["2013"]
hl = {"전남": "#2c3e50", "충남": "#c0392b", "강원": "#2f8f4e", "서울": C_CAP}
fig, axes = plt.subplots(1, 2, figsize=(11.5, 6),
                         gridspec_kw=dict(width_ratios=[1, 1.25]))
ax = axes[0]
for s, row in tt.iterrows():
    c = hl.get(s, "#c8c8c8")
    lw = 2.2 if s in hl else 1.1
    ax.plot([0, 1], [row["2013"], row["2023"]], color=c, lw=lw, marker="o",
            ms=4, zorder=3 if s in hl else 2)
    if s in hl:
        ax.text(-0.04, row["2013"], f"{s} {row['2013']:.2f}", ha="right",
                va="center", fontsize=9.5, color=c)
        ax.text(1.04, row["2023"], f"{row['2023']:.2f} {s}", ha="left",
                va="center", fontsize=9.5, color=c)
ax.set_xlim(-0.45, 1.45)
ax.set_xticks([0, 1])
ax.set_xticklabels(["2013년", "2023년"])
ax.set_ylim(0.45, 1.6)
ax.set_ylabel("합계출산율 (명)")
ax.set_title("(가) 기울기 그림 (색은 네 시도만)", fontsize=12)
ax = axes[1]
td = tt.sort_values("2023")
yy = np.arange(len(td))
ax.hlines(yy, td["2023"], td["2013"], color="#bbb", lw=2)
ax.scatter(td["2013"], yy, s=50, facecolor="white", edgecolor="#2c3e50",
           lw=1.5, zorder=3, label="2013년")
ax.scatter(td["2023"], yy, s=50, color="#c0392b", zorder=3, label="2023년")
ax.set_yticks(yy)
ax.set_yticklabels(td.index)
ax.set_xlim(0.4, 1.65)
ax.set_xlabel("합계출산율 (명)")
ax.set_title("(나) 덤벨 그림 (2023년 값 순)", fontsize=12)
ax.legend(loc="lower right")
fig.suptitle("시도별 합계출산율의 2013년과 2023년", fontsize=13, y=1.01)
save(fig, "fig09_slope_dumbbell.png")

# ---------------------------------------------------------------- 그림 9-17
# 변화 산점도: 가로 2013년, 세로 2023년, 대각선 = 변화 없음
r_tt = tt["2013"].corr(tt["2023"])
fig, ax = plt.subplots(figsize=(7.2, 6.4))
lim = (0.4, 1.65)
ax.plot(lim, lim, color="#999", lw=1.2, ls="--")
ax.text(1.18, 1.25, "변화 없음 (2013년 = 2023년)", rotation=45, fontsize=9.5,
        color="#777", ha="center", va="center")
ax.scatter(tt["2013"], tt["2023"], s=45, color="#2f6fb0", edgecolor="white",
           lw=0.5, zorder=3)
off = {"충북": (6, 3), "경북": (-28, -4), "충남": (6, 2), "제주": (6, -7),
       "울산": (2, -13), "경남": (-6, -14), "전북": (-6, -14), "대구": (-26, 2),
       "광주": (-4, 6), "인천": (5, -10), "대전": (-26, 2), "경기": (5, -10),
       "세종": (-26, 4), "전남": (6, 2)}
for s, row in tt.iterrows():
    ax.annotate(s, (row["2013"], row["2023"]), xytext=off.get(s, (5, 4)),
                textcoords="offset points", fontsize=9, color="#333")
ax.set_xlim(*lim)
ax.set_ylim(*lim)
ax.set_aspect("equal")
ax.set_title("변화 산점도: 시도별 합계출산율 (17개 시도)", fontsize=13)
ax.set_xlabel("2013년 합계출산율 (명)")
ax.set_ylabel("2023년 합계출산율 (명)")
save(fig, "fig09_change_scatter.png")

# ================================================================ 1.5
# ---------------------------------------------------------------- 그림 9-18
# 정직한 그래프 vs 축 자른 왜곡 그래프 (막대)
cap = df["시도"].isin(["서울", "경기", "인천"])
v_cap = df.loc[cap, "합계출산율"].mean()
v_non = df.loc[cap.eq(False), "합계출산율"].mean()
labels = ["수도권", "비수도권"]
values = [v_cap, v_non]
colors = ["#7fa8d9", "#e0975a"]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
for ax, title, ylim in [(axes[0], "(가) 정직한 그래프: 세로축이 0에서 시작", (0, 1.0)),
                        (axes[1], "(나) 왜곡된 그래프: 세로축을 0.65에서 자름", (0.65, 0.90))]:
    bars = ax.bar(labels, values, color=colors, width=0.55)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=12)
    ax.set_ylabel("합계출산율 (명)")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2,
                min(v, ylim[1]) - (ylim[1] - ylim[0]) * 0.06,
                f"{v:.2f}", ha="center", fontsize=11,
                color="white", fontweight="bold")
fig.suptitle("같은 데이터, 다른 인상: 시군구 평균 합계출산율 (2023년)",
             fontsize=13, y=1.02)
save(fig, "fig09_axis_trunc.png")

# ================================================================ 출력
print("그림 9-1부터 9-18 저장 완료")
print(f"[9-1] 평균 {mean_v:.2f}, 중앙값 {med_v:.2f}, 최솟값 {age.min()}, "
      f"최댓값 {age.max()}")
print(f"[9-2] 밀도 0.001 이상 시작 x = {kde_left:.1f}, 권역별 봉우리 위치 "
      + ", ".join(f"{k} {v:.1f}" for k, v in peaks.items()))
print(f"[9-3] 20% 이하 {share20:.3f} ({(age <= 20).sum()}곳), "
      f"30% 이하 {share30:.3f} ({(age <= 30).sum()}곳), 90분위수 {q90:.2f}, "
      f"25분위 {age.quantile(.25):.2f}, 75분위 {age.quantile(.75):.2f}")
print("[9-4] 시도별 시군구 수:", {k: int(v) for k, v in cnt.items()})
for s in order6:
    v6 = d6.loc[d6["시도"] == s, "고령인구비율"]
    print(f"[9-6] {s}: n={len(v6)}, 중앙값 {v6.median():.2f}, "
          f"최소 {v6.min()}, 최대 {v6.max()}, 25분위 {v6.quantile(.25):.2f}, "
          f"75분위 {v6.quantile(.75):.2f}")
print("[9-7] 시도 값과 시군구 단순평균:")
print(dot.assign(차이=dot["단순평균"] - dot["시도값"]).round(2).to_string())
print(f"전국 고령인구비율 {aging_sido.get('전국')}")
print("[9-8] 권역별 평균·표준편차·n:")
for k, v in eb.items():
    print(k)
    print(v.round(3).to_string())
print(f"[9-9] r = {r:.3f}, n = {len(sub)}")
print(f"[9-10] r(보통) = {r_lin:.3f}, r(로그) = {r_log:.3f}, 밀도 최소 "
      f"{df['인구밀도'].min():.1f}, 최대 {df['인구밀도'].max():.1f}, "
      f"1,000 미만 {(df['인구밀도'] < 1000).sum()}곳")
print("[9-11] 권역별 r, n:", {k: (round(v[0], 3), v[1]) for k, v in r_grp.items()})
print("[9-12] 시도별 r, n:", {k: (round(v[0], 2), v[1]) for k, v in r_sido.items()})
print(f"[9-13] 산점도 행렬 n = {n_pair}")
print(pv[pvars].corr().round(2).to_string())
print("[9-14] 상관 행렬:")
print(cm.round(2).to_string())
print("[9-16] 시도 합계출산율:")
print(tt.round(3).to_string())
print(f"전국 2013 {t13.get('전국')}, 2023 {t23.get('전국')}")
print(f"[9-17] 2013-2023 시도 상관 r = {r_tt:.3f}")
print(f"[9-18] 수도권 {v_cap:.3f}, 비수도권 {v_non:.3f}")

# ---------------------------------------------------------------- 본문 보조 수치
gn = df[df["시도"] == "경남"].sort_values("고령인구비율")
print("[9-6 보조] 경남 25% 미만:", gn.loc[gn["고령인구비율"] < 25, ["시군구", "고령인구비율"]].values.tolist())
print("[9-6 보조] 경남 30% 이상:", int((gn["고령인구비율"] >= 30).sum()), "곳,",
      "25-30%:", gn.loc[gn["고령인구비율"].between(25, 30, inclusive="left"), ["시군구", "고령인구비율"]].values.tolist())
gg = df[df["시도"] == "경기"]
print("[9-6 보조] 경기 24% 이상:", gg.loc[gg["고령인구비율"] >= 24, ["시군구", "고령인구비율"]].values.tolist())
se = df[df["시도"] == "서울"]
print(f"[9-12 보조] 서울 고령 {se['고령인구비율'].min()}-{se['고령인구비율'].max()}, "
      f"합계출산율 {se['합계출산율'].min()}-{se['합계출산율'].max()}")
print("[9-12 보조] 인천:", df.loc[df["시도"] == "인천", ["시군구", "고령인구비율", "합계출산율"]].values.tolist())
print("[9-13 보조] 인구증가율 상위:", df.nlargest(3, "인구증가율")[["시도", "시군구", "인구증가율"]].values.tolist())
A, P = df["면적"].sum(), df["총인구"].sum()
for th in (30, 35):
    m = df["고령인구비율"] >= th
    print(f"[지도 보조] 고령 {th}% 이상 {int(m.sum())}곳: 면적 {df.loc[m, '면적'].sum() / A * 100:.1f}%, "
          f"인구 {df.loc[m, '총인구'].sum() / P * 100:.1f}%")
print(f"[지도 보조] 서울 면적 {se['면적'].sum():.1f}km² (전국의 {se['면적'].sum() / A * 100:.1f}%), "
      f"인구 {se['총인구'].sum():,} (전국의 {se['총인구'].sum() / P * 100:.1f}%)")
print("[지도 보조] 면적 최대:", df.nlargest(1, "면적")[["시도", "시군구", "면적", "총인구"]].values.tolist())
print("[9-10 보조] 인구밀도 1,000 초과이면서 고령 25% 이상:",
      df.loc[(df["인구밀도"] > 1000) & (df["고령인구비율"] >= 25), ["시도", "시군구", "고령인구비율"]].values.tolist())
