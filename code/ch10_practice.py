# 10주차 실습(10-2) 확장 수치 계산: 가정 확인, 차이의 크기, 회귀 진단, 독립 검산, 통제변수 회귀
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
# 본문의 모든 새 수치는 이 스크립트의 출력에서 가져온다. scipy와 numpy만 사용한다(statsmodels는 교차검증 용도).
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data" / "sigungu_2023.csv"
df = pd.read_csv(DATA, encoding="utf-8-sig")

capital = ["서울", "경기", "인천"]
df["권역"] = np.where(df["시도"].isin(capital), "수도권", "비수도권")
g_cap = df.loc[df["권역"] == "수도권", "고령인구비율"]
g_non = df.loc[df["권역"] == "비수도권", "고령인구비율"]


def line(title):
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)


# ------------------------------------------------------------------ [1] 분석 전 가정 확인
line("[1] 분석 전 가정 확인: 두 집단의 분포 모양과 흩어짐 (고령인구비율)")
rows = []
for name, g in [("수도권", g_cap), ("비수도권", g_non)]:
    q1, q3 = g.quantile(0.25), g.quantile(0.75)
    sw_stat, sw_p = stats.shapiro(g)
    rows.append(dict(집단=name, n=len(g), 평균=g.mean(), 표준편차=g.std(ddof=1), 분산=g.var(ddof=1),
                     최소=g.min(), Q1=q1, 중앙값=g.median(), Q3=q3, 최대=g.max(),
                     왜도=stats.skew(g, bias=False), 샤피로p=sw_p))
tab = pd.DataFrame(rows).set_index("집단")
pd.set_option("display.width", 200)
print(tab.round(3).T)
var_ratio = g_non.var(ddof=1) / g_cap.var(ddof=1)
sd_ratio = g_non.std(ddof=1) / g_cap.std(ddof=1)
print(f"분산 비(비수도권/수도권) = {var_ratio:.2f}, 표준편차 비 = {sd_ratio:.2f}")
lev_stat, lev_p = stats.levene(g_cap, g_non, center="median")
print(f"Levene 등분산 검정: 통계량 = {lev_stat:.2f}, p = {lev_p:.2e}")
# 등분산 가정 t검정(Student)과 Welch의 대비
t_s, p_s = stats.ttest_ind(g_non, g_cap, equal_var=True)
t_w, p_w = stats.ttest_ind(g_non, g_cap, equal_var=False)
print(f"Student t(등분산 가정) = {t_s:.2f} (p = {p_s:.2e}) / Welch t = {t_w:.2f} (p = {p_w:.2e})")
# 30% 초과 시군구 수(분포 모양 서술용)
print(f"고령인구비율 30% 초과: 수도권 {(g_cap > 30).sum()}개, 비수도권 {(g_non > 30).sum()}개")
print(f"고령인구비율 15% 미만: 수도권 {(g_cap < 15).sum()}개, 비수도권 {(g_non < 15).sum()}개")
print(f"비수도권 40% 초과: {(g_non > 40).sum()}개 -> "
      f"{', '.join(df.loc[(df['권역']=='비수도권') & (df['고령인구비율']>40), '시도'] + ' ' + df.loc[(df['권역']=='비수도권') & (df['고령인구비율']>40), '시군구'])}")

# ------------------------------------------------------------------ [2] 차이의 크기: 신뢰구간과 효과 크기
line("[2] 차이의 크기: 평균 차이의 95% 신뢰구간과 효과 크기 (고령인구비율)")


def welch_ci(a, b, alpha=0.05):
    """b - a 의 평균 차이, Welch 표준오차, 자유도, 95% 신뢰구간"""
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va / na + vb / nb)
    dfw = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    diff = b.mean() - a.mean()
    tcrit = stats.t.ppf(1 - alpha / 2, dfw)
    return diff, se, dfw, diff - tcrit * se, diff + tcrit * se, tcrit


def cohen_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return (b.mean() - a.mean()) / sp, sp


diff, se, dfw, lo, hi, tcrit = welch_ci(g_cap, g_non)
d, sp = cohen_d(g_cap, g_non)
print(f"평균 차이(비수도권 - 수도권) = {diff:.2f} %포인트")
print(f"표준오차(Welch) = {se:.3f}, 자유도 = {dfw:.1f}, t임계값 = {tcrit:.3f}")
print(f"95% 신뢰구간 = [{lo:.2f}, {hi:.2f}] %포인트 (폭 {hi-lo:.2f})")
print(f"합동 표준편차 = {sp:.2f}, Cohen d = {d:.2f}")
# scipy 내장 신뢰구간으로 교차검증
res = stats.ttest_ind(g_non, g_cap, equal_var=False)
ci = res.confidence_interval(0.95)
print(f"scipy 교차검증: t = {res.statistic:.2f}, df = {res.df:.1f}, CI = [{ci.low:.2f}, {ci.high:.2f}]")

print()
print("참고: 합계출산율의 같은 계산")
t_cap = df.loc[df["권역"] == "수도권", "합계출산율"].dropna()
t_non = df.loc[df["권역"] == "비수도권", "합계출산율"].dropna()
diff2, se2, dfw2, lo2, hi2, _ = welch_ci(t_cap, t_non)
d2, sp2 = cohen_d(t_cap, t_non)
res2 = stats.ttest_ind(t_non, t_cap, equal_var=False)
print(f"n = {len(t_cap)} / {len(t_non)}, 평균 {t_cap.mean():.3f} / {t_non.mean():.3f}, 차이 = {diff2:.3f}명, "
      f"95% CI = [{lo2:.3f}, {hi2:.3f}], t = {res2.statistic:.2f}, 합동SD = {sp2:.3f}, Cohen d = {d2:.2f}")

# ------------------------------------------------------------------ [3] 회귀 진단: 잔차와 한 점의 힘
line("[3] 단순회귀 진단: 잔차 요약, 영향력 큰 점, 빼고 다시 돌리기")
sub = df.dropna(subset=["고령인구비율", "합계출산율"]).reset_index(drop=True)
x, y = sub["고령인구비율"].to_numpy(), sub["합계출산율"].to_numpy()
reg = stats.linregress(x, y)
print(f"n = {len(sub)}, 절편 = {reg.intercept:.4f}, 기울기 = {reg.slope:.5f} (SE {reg.stderr:.5f}), "
      f"p = {reg.pvalue:.2e}, R제곱 = {reg.rvalue**2:.4f}")
pred = reg.intercept + reg.slope * x
resid = y - pred
sub["예측값"], sub["잔차"] = pred, resid
print(f"잔차 평균 = {resid.mean():.2e}, 잔차 표준편차 = {resid.std(ddof=2):.3f}, "
      f"최소 = {resid.min():.3f}, 최대 = {resid.max():.3f}")
print(f"잔차 절댓값이 0.3 넘는 시군구 수 = {(np.abs(resid) > 0.3).sum()}개, 0.2 넘는 수 = {(np.abs(resid) > 0.2).sum()}개")
print(f"y 표준편차 = {y.std(ddof=1):.3f} (잔차 표준편차와 비교)")
top = sub.reindex(sub["잔차"].abs().sort_values(ascending=False).index).head(6)
print("잔차 절댓값 상위 6개:")
print(top[["시도", "시군구", "고령인구비율", "합계출산율", "예측값", "잔차"]].round(3).to_string(index=False))

# 잔차를 예측값 구간별로 요약(패턴 확인)
bins = pd.cut(sub["고령인구비율"], [0, 15, 20, 25, 30, 35, 50])
print("고령인구비율 구간별 잔차 평균(0 근처면 직선이 대체로 적절):")
print(sub.groupby(bins, observed=True)["잔차"].agg(["count", "mean", "std"]).round(3))

# 한 점씩 빼고 기울기 재계산(leave-one-out)
loo = []
for i in range(len(sub)):
    m = np.ones(len(sub), dtype=bool)
    m[i] = False
    r_i = stats.linregress(x[m], y[m])
    loo.append(dict(시도=sub.loc[i, "시도"], 시군구=sub.loc[i, "시군구"], 고령인구비율=x[i], 합계출산율=y[i],
                    기울기=r_i.slope, 변화=r_i.slope - reg.slope, R제곱=r_i.rvalue ** 2))
loo = pd.DataFrame(loo)
loo["변화율%"] = loo["변화"] / reg.slope * 100
top_loo = loo.reindex(loo["변화"].abs().sort_values(ascending=False).index).head(6)
print("한 점을 뺐을 때 기울기 변화가 큰 시군구 상위 6개:")
print(top_loo.round(5).to_string(index=False))

# statsmodels로 Cook's distance 교차검증
try:
    import statsmodels.api as sm
    X = sm.add_constant(x)
    ols = sm.OLS(y, X).fit()
    cooks = ols.get_influence().cooks_distance[0]
    idx = np.argsort(cooks)[::-1][:5]
    print("statsmodels Cook 거리 상위 5개:")
    for i in idx:
        print(f"  {sub.loc[i, '시도']} {sub.loc[i, '시군구']}: D = {cooks[i]:.4f}")
except Exception as e:  # noqa: BLE001
    print("statsmodels 교차검증 생략:", e)

# 가장 영향력 큰 점을 빼고 다시 돌리기 + 영광군(출산율 최대)을 빼고 다시 돌리기
for label, cond in [("영향력 1위 시군구 제외", None), ("전남 영광군 제외", (sub["시도"] == "전남") & (sub["시군구"] == "영광군")),
                    ("부산 중구 제외", (sub["시도"] == "부산") & (sub["시군구"] == "중구"))]:
    if cond is None:
        name = top_loo.iloc[0]
        cond = (sub["시도"] == name["시도"]) & (sub["시군구"] == name["시군구"])
        label = f"영향력 1위({name['시도']} {name['시군구']}) 제외"
    m = ~cond.to_numpy()
    r_m = stats.linregress(x[m], y[m])
    print(f"{label}: n = {m.sum()}, 기울기 = {r_m.slope:.5f} (원래 {reg.slope:.5f}, "
          f"변화 {(r_m.slope-reg.slope)/reg.slope*100:+.1f}%), 절편 = {r_m.intercept:.4f}, "
          f"R제곱 = {r_m.rvalue**2:.4f} (원래 {reg.rvalue**2:.4f}), p = {r_m.pvalue:.2e}")

# 잔차 상위 3개를 한꺼번에 뺐을 때
top3 = top.head(3)
m3 = ~sub.index.isin(top3.index)
r_3 = stats.linregress(x[m3], y[m3])
print(f"잔차 상위 3개({', '.join(top3['시군구'])}) 제외: n = {m3.sum()}, 기울기 = {r_3.slope:.5f} "
      f"({(r_3.slope-reg.slope)/reg.slope*100:+.1f}%), R제곱 = {r_3.rvalue**2:.4f}")

# ------------------------------------------------------------------ [4] 독립 검산용 값 (다른 경로로 계산)
line("[4] 새 대화 독립 검산용: 원자료에서 다른 경로로 다시 계산")
cap_rows = df[df["시도"].isin(capital)]
print(f"수도권 행 수(시도 isin) = {len(cap_rows)}, 고령인구비율 합계 = {cap_rows['고령인구비율'].sum():.4f}, "
      f"합계/개수 = {cap_rows['고령인구비율'].sum()/len(cap_rows):.4f}")
print(f"수도권 시도별 개수: {cap_rows['시도'].value_counts().to_dict()}")
# 가중 평균(고령 인구 합 / 총인구 합)과 단순 평균의 차이: 다른 정의라는 점 확인용
w_cap = cap_rows["고령"].sum() / cap_rows["총인구"].sum() * 100
non_rows = df[~df["시도"].isin(capital)]
w_non = non_rows["고령"].sum() / non_rows["총인구"].sum() * 100
print(f"참고(다른 정의): 인구 가중 고령인구비율 수도권 {w_cap:.2f}%, 비수도권 {w_non:.2f}% (단순 평균과 다름)")
# 기울기를 공식으로: 공분산 / 분산
cov = np.cov(x, y, ddof=1)[0, 1]
print(f"기울기 = 공분산/분산 = {cov:.5f} / {x.var(ddof=1):.4f} = {cov/x.var(ddof=1):.5f}")
print(f"numpy polyfit 기울기 = {np.polyfit(x, y, 1)[0]:.5f}")
print(f"합계출산율 결측 = {df['합계출산율'].isna().sum()}개, 사용 관측치 = {len(sub)}")
print(f"전체 합계출산율 평균(228) = {sub['합계출산율'].mean():.4f}, 중앙값 = {sub['합계출산율'].median():.3f}")
print(f"고령인구비율 25%일 때 예측 = {reg.intercept + reg.slope*25:.4f}")

# ------------------------------------------------------------------ [5] 선택 심화: 통제변수 하나 넣기
line("[5] 선택 심화: 통제변수를 넣은 회귀 (numpy로 계산, statsmodels로 교차검증)")


def ols_numpy(X, y, names):
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    n, k = X.shape
    sigma2 = res @ res / (n - k)
    cov_b = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov_b))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), n - k)
    r2 = 1 - (res @ res) / ((y - y.mean()) @ (y - y.mean()))
    out = pd.DataFrame(dict(계수=beta, 표준오차=se, t=t, p=p), index=["절편"] + names)
    return out, r2, n


sub["수도권"] = (sub["권역"] == "수도권").astype(int)
for names in (["고령인구비율", "수도권"], ["고령인구비율", "인구증가율"], ["고령인구비율", "수도권", "인구증가율"]):
    out, r2, n = ols_numpy(sub[names].to_numpy(dtype=float), y, names)
    print(f"모형: 합계출산율 ~ {' + '.join(names)}  (n = {n}, R제곱 = {r2:.4f})")
    print(out.round(5).to_string())
    print()

try:
    import statsmodels.formula.api as smf
    m1 = smf.ols("합계출산율 ~ 고령인구비율 + 수도권", data=sub).fit()
    print("statsmodels 교차검증(고령인구비율 + 수도권): ",
          {k: round(v, 5) for k, v in m1.params.items()}, "R2 =", round(m1.rsquared, 4), "n =", int(m1.nobs))
except Exception as e:  # noqa: BLE001
    print("statsmodels 교차검증 생략:", e)

print()
print(f"인구증가율과 고령인구비율의 상관 = {stats.pearsonr(sub['고령인구비율'], sub['인구증가율'])[0]:.3f}")
print(f"인구증가율과 합계출산율의 상관 = {stats.pearsonr(sub['인구증가율'], sub['합계출산율'])[0]:.3f}")
print(f"수도권 안에서만 회귀: n = {(sub['수도권']==1).sum()}, "
      f"기울기 = {stats.linregress(sub.loc[sub['수도권']==1,'고령인구비율'], sub.loc[sub['수도권']==1,'합계출산율']).slope:.5f}")
print(f"비수도권 안에서만 회귀: n = {(sub['수도권']==0).sum()}, "
      f"기울기 = {stats.linregress(sub.loc[sub['수도권']==0,'고령인구비율'], sub.loc[sub['수도권']==0,'합계출산율']).slope:.5f}")

# ------------------------------------------------------------------ [6] 잔차 패턴 서술용 보조 값
line("[6] 보조: 고령인구비율 15% 이하 시군구의 잔차 (직선이 낮게 예측하는 구간)")
young = sub[sub["고령인구비율"] <= 15].sort_values("고령인구비율")
print(young[["시도", "시군구", "고령인구비율", "합계출산율", "예측값", "잔차"]].round(3).to_string(index=False))
print(f"15% 이하 {len(young)}개 중 잔차가 양수인 곳 = {(young['잔차'] > 0).sum()}개")

# ------------------------------------------------------------------ [7] 같은 절차를 다른 변수로 반복
line("[7] 같은 집단 비교를 다른 변수로 반복 (2.4절)")
df["유소년인구비율"] = df["유소년"] / df["총인구"] * 100
rows7 = []
for var in ["고령인구비율", "합계출산율", "인구증가율", "유소년인구비율"]:
    a = df.loc[df["권역"] == "수도권", var].dropna()
    b = df.loc[df["권역"] == "비수도권", var].dropna()
    diff_v, se_v, dfv, lo_v, hi_v, _ = welch_ci(a, b)
    d_v, sp_v = cohen_d(a, b)
    r_v = stats.ttest_ind(b, a, equal_var=False)
    rows7.append(dict(변수=var, n수도권=len(a), n비수도권=len(b), 평균수도권=a.mean(), 평균비수도권=b.mean(),
                      SD수도권=a.std(ddof=1), SD비수도권=b.std(ddof=1), 차이=diff_v,
                      CI하한=lo_v, CI상한=hi_v, t=r_v.statistic, p=r_v.pvalue, 합동SD=sp_v, d=d_v))
tab7 = pd.DataFrame(rows7).set_index("변수")
print(tab7.round(4).T.to_string())
print("p값(지수 표기):", {k: f"{v:.3e}" for k, v in tab7["p"].items()})
print("결측 개수:", {c: int(df[c].isna().sum()) for c in
                 ["고령인구비율", "합계출산율", "인구증가율", "유소년인구비율"]})
print()
print("인구증가율 분포 참고: 전체 평균 %.3f, 0보다 큰 시군구 %d개 / 229개"
      % (df["인구증가율"].mean(), (df["인구증가율"] > 0).sum()))
print("인구증가율이 양수인 곳의 권역 구성:",
      df.loc[df["인구증가율"] > 0, "권역"].value_counts().to_dict())
print("유소년인구비율 최대/최소: %.2f%% (%s), %.2f%% (%s)"
      % (df["유소년인구비율"].max(), df.loc[df["유소년인구비율"].idxmax(), "시군구"],
         df["유소년인구비율"].min(), df.loc[df["유소년인구비율"].idxmin(), "시군구"]))
print("권역별 인구증가율 양수 비율: 수도권 %d/%d (%.1f%%), 비수도권 %d/%d (%.1f%%)"
      % ((df.loc[df["권역"] == "수도권", "인구증가율"] > 0).sum(), (df["권역"] == "수도권").sum(),
         (df.loc[df["권역"] == "수도권", "인구증가율"] > 0).mean() * 100,
         (df.loc[df["권역"] == "비수도권", "인구증가율"] > 0).sum(), (df["권역"] == "비수도권").sum(),
         (df.loc[df["권역"] == "비수도권", "인구증가율"] > 0).mean() * 100))
gn = df[df["시군구"] == "강릉시"].iloc[0]
print("파생변수 손 검산(강릉시): 유소년 %.0f / 총인구 %.0f x 100 = %.4f%%"
      % (gn["유소년"], gn["총인구"], gn["유소년"] / gn["총인구"] * 100))

# ------------------------------------------------------------------ [8] 표본 크기의 효과
line("[8] 표본 크기의 효과: 229개 전체와 무작위 50개 (2.5절)")


def compare_group(frame, var):
    a = frame.loc[frame["권역"] == "수도권", var].dropna()
    b = frame.loc[frame["권역"] == "비수도권", var].dropna()
    if len(a) < 2 or len(b) < 2:
        return None
    diff_v, se_v, dfv, lo_v, hi_v, _ = welch_ci(a, b)
    r_v = stats.ttest_ind(b, a, equal_var=False)
    d_v, _ = cohen_d(a, b)
    return dict(n수도권=len(a), n비수도권=len(b), 차이=diff_v, 표준오차=se_v, 자유도=dfv,
                CI하한=lo_v, CI상한=hi_v, CI폭=hi_v - lo_v, t=r_v.statistic, p=r_v.pvalue, d=d_v)


full = compare_group(df, "고령인구비율")
print("전체 229개:", {k: round(v, 4) for k, v in full.items()})
print("  p값(지수 표기) = %.3e" % full["p"])
rng = np.random.default_rng(2023)
samp = df.sample(n=50, random_state=2023)
s50 = compare_group(samp, "고령인구비율")
print("무작위 50개(시드 2023):", {k: round(v, 4) for k, v in s50.items()}, "p = %.5f" % s50["p"])
print("  표본 50개의 시도 구성:", samp["시도"].value_counts().to_dict())
samp2 = df.sample(n=20, random_state=2023)
s20 = compare_group(samp2, "고령인구비율")
print("무작위 20개(시드 2023):", {k: round(v, 4) for k, v in s20.items()}, "p = %.5f" % s20["p"])
# 같은 크기의 표본을 여러 번 뽑았을 때의 분포
for n_s in (50, 20):
    ps, widths, diffs, sig = [], [], [], 0
    for seed in range(500):
        r = compare_group(df.sample(n=n_s, random_state=seed), "고령인구비율")
        if r is None:
            continue
        ps.append(r["p"])
        widths.append(r["CI폭"])
        diffs.append(r["차이"])
        sig += r["p"] < 0.05
    ps = np.array(ps)
    print(f"표본 {n_s}개를 500번 반복: p < 0.05 비율 = {sig/len(ps)*100:.1f}%, "
          f"p값 중앙값 = {np.median(ps):.2e}, 신뢰구간 폭 중앙값 = {np.median(widths):.2f}%포인트, "
          f"평균 차이 중앙값 = {np.median(diffs):.2f}, 최소 = {np.min(diffs):.2f}, 최대 = {np.max(diffs):.2f}")
# 합계출산율은 표본 50개에서 어떻게 되나
s50_tfr = compare_group(df.sample(n=50, random_state=2023), "합계출산율")
print("무작위 50개(시드 2023) 합계출산율:", {k: round(v, 4) for k, v in s50_tfr.items()})
# 시드 재현성: 같은 시드로 두 번 뽑으면 같은 표본인가
again = df.sample(n=50, random_state=2023)
print("시드 2023 재현성(두 번 뽑은 표본이 같은가):",
      bool(samp.index.equals(again.index)), "/ 다른 시드(7)와 같은가:",
      bool(samp.index.equals(df.sample(n=50, random_state=7).index)))
# 유의하지 않게 나온 20개 표본의 예 하나
for seed in range(500):
    r20 = compare_group(df.sample(n=20, random_state=seed), "고령인구비율")
    if r20 and r20["p"] > 0.05:
        print(f"20개 표본에서 유의하지 않게 나온 첫 시드 = {seed}:",
              {k: round(v, 4) for k, v in r20.items()})
        break

# ------------------------------------------------------------------ [9] 독립 검산 보조: 절편 공식
line("[9] 독립 검산 보조: 절편을 평균으로 다시 만들기 (2.10절)")
xbar, ybar = x.mean(), y.mean()
print(f"고령인구비율 평균(228개) = {xbar:.4f}, 합계출산율 평균(228개) = {ybar:.4f}")
print(f"절편 = ybar - 기울기 x xbar = {ybar:.4f} - {reg.slope:.5f} x {xbar:.4f} = {ybar - reg.slope * xbar:.4f}")
print(f"linregress 절편 = {reg.intercept:.4f}")
print(f"상관계수 r = {reg.rvalue:.4f}, r 제곱 = {reg.rvalue**2:.4f}")
print(f"기울기 = r x (y표준편차 / x표준편차) = {reg.rvalue:.4f} x ({y.std(ddof=1):.4f} / {x.std(ddof=1):.4f}) "
      f"= {reg.rvalue * y.std(ddof=1) / x.std(ddof=1):.5f}")

# ------------------------------------------------------------------ [10] 설명변수를 하나씩 더하기 + 표준화 계수
line("[10] 설명변수를 하나씩 더한 회귀와 표준화 계수 (2.12절)")
models = [["고령인구비율"], ["고령인구비율", "수도권"], ["고령인구비율", "수도권", "인구증가율"]]
for names in models:
    out, r2, n = ols_numpy(sub[names].to_numpy(dtype=float), y, names)
    std = {nm: out.loc[nm, "계수"] * sub[nm].std(ddof=1) / y.std(ddof=1) for nm in names}
    print(f"모형 {names} : n = {n}, R제곱 = {r2:.4f}, 조정R제곱 = "
          f"{1 - (1 - r2) * (n - 1) / (n - len(names) - 1):.4f}")
    print(out.round(5).to_string())
    print("  표준화 계수:", {k: round(v, 3) for k, v in std.items()})
    print()
print("변수별 표준편차:",
      {c: round(sub[c].std(ddof=1), 4) for c in ["고령인구비율", "수도권", "인구증가율", "합계출산율"]})

# ------------------------------------------------------------------ [11] 화면 출력 예시(본문 코드 블록용 실제 출력)
line("[11] 본문 코드 블록에 실을 실제 출력")
print("scipy shapiro(수도권):", stats.shapiro(g_cap))
print("scipy shapiro(비수도권):", stats.shapiro(g_non))
print("scipy levene:", stats.levene(g_cap, g_non, center="median"))
print("scipy ttest_ind(Welch):", stats.ttest_ind(g_non, g_cap, equal_var=False))
print("scipy linregress:", stats.linregress(x, y))
_tc = stats.t.ppf(0.975, len(x) - 2)
print(f"기울기의 95% 신뢰구간 = {reg.slope:.5f} +- {_tc:.4f} x {reg.stderr:.5f} = "
      f"[{reg.slope - _tc * reg.stderr:.5f}, {reg.slope + _tc * reg.stderr:.5f}] (자유도 {len(x) - 2})")
try:
    import statsmodels.api as sm2
    X1 = sm2.add_constant(x)
    fit1 = sm2.OLS(y, X1).fit()
    print("--- statsmodels 단순회귀 계수표 ---")
    print(fit1.summary().tables[1])
    print(f"R-squared = {fit1.rsquared:.3f}, Adj = {fit1.rsquared_adj:.3f}, "
          f"F = {fit1.fvalue:.2f}, Prob(F) = {fit1.f_pvalue:.3e}, n = {int(fit1.nobs)}")
    import statsmodels.formula.api as smf2
    fit2 = smf2.ols("합계출산율 ~ 고령인구비율 + 수도권", data=sub).fit()
    print("--- statsmodels 통제 회귀 계수표 ---")
    print(fit2.summary().tables[1])
    print(f"R-squared = {fit2.rsquared:.3f}, Adj = {fit2.rsquared_adj:.3f}, n = {int(fit2.nobs)}")
except Exception as e:  # noqa: BLE001
    print("statsmodels 출력 생략:", e)
