# 13주차 2회차(실습) 본문 수치 계산: 파이프라인 검문소 대조표, 틀리는 장면, 재현성 대조
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data"
d2023 = pd.read_csv(DATA / "sigungu_2023.csv", encoding="utf-8-sig")
d2013 = pd.read_csv(DATA / "sigungu_tfr_2013.csv", encoding="utf-8-sig")


def sep(title):
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)


# ---------------------------------------------------------------- 검문소 1
sep("[검문소 1] 수집 확인: 행 수와 열 목록")
print("2023:", d2023.shape, list(d2023.columns))
print("2013:", d2013.shape, list(d2013.columns))
print("2023 결측:", d2023.isna().sum()[lambda s: s > 0].to_dict())
print("2013 결측:", int(d2013.isna().sum().sum()))
print("2013 '남구' 행:", d2013.loc[d2013["시군구"] == "남구", "시도"].tolist())
print("2023 '남구' 행:", d2023.loc[d2023["시군구"] == "남구", "시도"].tolist())

# ---------------------------------------------------------------- 검문소 2
sep("[검문소 2] 진단 병합과 본 병합")
diag = d2023.merge(d2013, on=["시도", "시군구"], how="outer", indicator=True)
print(diag["_merge"].value_counts().to_dict())
print("left_only:", diag.loc[diag["_merge"] == "left_only", ["시도", "시군구"]].values.tolist())

d2013_fix = d2013.copy()
mask = (d2013_fix["시도"] == "인천") & (d2013_fix["시군구"] == "남구")
d2013_fix.loc[mask, "시군구"] = "미추홀구"
merged = d2023.merge(d2013_fix, on=["시도", "시군구"], how="left", validate="one_to_one")
print("본 병합 행 수:", len(merged), "/ 2013 결측:", int(merged["합계출산율_2013"].isna().sum()))

# 표본 대조: 파일 행 번호 = 인덱스 + 2 (1행은 열 이름)
def row_no(df, sido, gu):
    idx = df.index[(df["시도"] == sido) & (df["시군구"] == gu)]
    return int(idx[0]) + 2

for sido, gu in [("서울", "종로구"), ("인천", "미추홀구"), ("강원", "고성군"), ("경남", "고성군")]:
    m = merged[(merged["시도"] == sido) & (merged["시군구"] == gu)].iloc[0]
    src_gu = "남구" if gu == "미추홀구" else gu
    print(f"{sido} {gu}: 2023={m['합계출산율']}, 2013={m['합계출산율_2013']}, "
          f"merged 행 {row_no(merged, sido, gu)}, 2023파일 행 {row_no(d2023, sido, gu)}, "
          f"2013파일 행 {row_no(d2013, sido, src_gu)}")

rng = np.random.default_rng(13)
pick = sorted(rng.choice(len(merged), size=5, replace=False))
print("무작위 5행 (seed 13):")
for i in pick:
    m = merged.iloc[i]
    src_gu = "남구" if m["시군구"] == "미추홀구" else m["시군구"]
    print(f"  merged 행 {i + 2}: {m['시도']} {m['시군구']} 2023={m['합계출산율']} "
          f"2013={m['합계출산율_2013']} (2023파일 행 {row_no(d2023, m['시도'], m['시군구'])}, "
          f"2013파일 행 {row_no(d2013, m['시도'], src_gu)})")

# 정렬 여부: 원본 파일이 시도·시군구 가나다순인가
srt = d2023.sort_values(["시도", "시군구"]).reset_index(drop=True)
print("2023 원본이 시도·시군구 가나다순 정렬인가:", srt.equals(d2023))
print("2023 원본 첫 3행:", d2023[["시도", "시군구"]].head(3).values.tolist())
print("2023 원본 마지막 3행:", d2023[["시도", "시군구"]].tail(3).values.tolist())

# ---------------------------------------------------------------- 검문소 3
sep("[검문소 3] 분석: 대표 수치, 집단 비교, 회귀")
t23 = merged["합계출산율"].dropna()
t13 = merged["합계출산율_2013"]
print(f"2023 합계출산율: n={len(t23)}, 평균={t23.mean():.4f}, 중앙값={t23.median():.3f}, "
      f"최소={t23.min()} 최대={t23.max()}")
print(f"2013 합계출산율(229곳): n={t13.notna().sum()}, 평균={t13.mean():.4f}, "
      f"중앙값={t13.median():.3f}, 최소={t13.min()} 최대={t13.max()}")
print(f"2013 합계출산율(군위군 제외 228곳): 평균={t13[merged['합계출산율'].notna()].mean():.4f}")

capital = ["서울", "경기", "인천"]
merged["권역"] = np.where(merged["시도"].isin(capital), "수도권", "비수도권")
for name in ["수도권", "비수도권"]:
    g = merged.loc[merged["권역"] == name, "합계출산율"].dropna()
    print(f"{name} 2023: n={len(g)}, 평균={g.mean():.4f}")
    g13 = merged.loc[merged["권역"] == name, "합계출산율_2013"]
    print(f"{name} 2013: n={len(g13)}, 평균={g13.mean():.4f}")

sub = merged.dropna(subset=["고령인구비율", "합계출산율"])
reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])
r = sub["고령인구비율"].corr(sub["합계출산율"])
print(f"회귀(n={len(sub)}): 절편={reg.intercept:.4f}, 기울기={reg.slope:.5f}, "
      f"p={reg.pvalue:.2e}, R2={reg.rvalue ** 2:.4f}, r={r:.3f}")
print(f"  고령인구비율 25%일 때 예측 = {reg.intercept + reg.slope * 25:.3f}")
print(f"  고령인구비율 범위: {sub['고령인구비율'].min():.2f} - {sub['고령인구비율'].max():.2f}")
hi = sub.loc[sub["고령인구비율"].idxmax()]
print(f"  고령인구비율 최대: {hi['시도']} {hi['시군구']} {hi['고령인구비율']:.2f}%, 출산율 {hi['합계출산율']}")

# ---------------------------------------------------------------- 검문소 4
sep("[검문소 4] 2013 대비 2023 변화 (그림 대조용)")
both = merged.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
both["변화"] = both["합계출산율"] - both["합계출산율_2013"]
up = both[both["변화"] > 0]
print(f"비교 가능 {len(both)}곳, 오른 곳 {len(up)}곳:", up[["시도", "시군구", "합계출산율_2013", "합계출산율"]].values.tolist())
print(f"내린 곳 {int((both['변화'] < 0).sum())}곳, 같은 곳 {int((both['변화'] == 0).sum())}곳")
print(f"평균 변화 = {both['변화'].mean():.4f}, 중앙값 변화 = {both['변화'].median():.3f}")
lo = both.loc[both["변화"].idxmin()]
print(f"가장 크게 내린 곳: {lo['시도']} {lo['시군구']} {lo['합계출산율_2013']} -> {lo['합계출산율']} ({lo['변화']:.3f})")
print(f"2013 최대: {both.loc[both['합계출산율_2013'].idxmax(), ['시도', '시군구', '합계출산율_2013']].tolist()}")
print(f"2013 최소: {both.loc[both['합계출산율_2013'].idxmin(), ['시도', '시군구', '합계출산율_2013']].tolist()}")
gw = merged[merged["시군구"] == "군위군"].iloc[0]
print(f"군위군: 2013={gw['합계출산율_2013']}, 2023={gw['합계출산율']}, 고령인구비율={gw['고령인구비율']:.2f}")

# ---------------------------------------------------------------- 틀리는 장면 A
sep("[틀리는 장면 A] 정제 담당이 결측 행을 삭제(dropna)해 병합")
d2023_drop = d2023.dropna(subset=["합계출산율"])
merged_drop = d2023_drop.merge(d2013_fix, on=["시도", "시군구"], how="left", validate="one_to_one")
print("merged.csv 행 수:", len(merged_drop), "(사라진 행:",
      d2023.loc[~d2023.index.isin(d2023_drop.index), ["시도", "시군구"]].values.tolist(), ")")
sub_d = merged_drop.dropna(subset=["고령인구비율", "합계출산율"])
reg_d = stats.linregress(sub_d["고령인구비율"], sub_d["합계출산율"])
print(f"회귀(n={len(sub_d)}): 기울기={reg_d.slope:.5f}, R2={reg_d.rvalue ** 2:.4f}  <- 원래와 같은가:",
      np.isclose(reg_d.slope, reg.slope))
print(f"2013 평균(228곳) = {merged_drop['합계출산율_2013'].mean():.4f} vs 229곳 {t13.mean():.4f}")

# ---------------------------------------------------------------- 틀리는 장면 B
sep("[틀리는 장면 B] 정제 담당이 결측을 0으로 채워 병합 (재현 실패의 원인 예)")
d2023_fill = d2023.copy()
d2023_fill["합계출산율"] = d2023_fill["합계출산율"].fillna(0)
merged_fill = d2023_fill.merge(d2013_fix, on=["시도", "시군구"], how="left", validate="one_to_one")
print("merged.csv 행 수:", len(merged_fill))
sub_f = merged_fill.dropna(subset=["고령인구비율", "합계출산율"])
reg_f = stats.linregress(sub_f["고령인구비율"], sub_f["합계출산율"])
print(f"회귀(n={len(sub_f)}): 절편={reg_f.intercept:.4f}, 기울기={reg_f.slope:.5f}, "
      f"p={reg_f.pvalue:.2e}, R2={reg_f.rvalue ** 2:.4f}")
print(f"2023 평균(229곳, 0 포함) = {merged_fill['합계출산율'].mean():.4f} vs 228곳 {t23.mean():.4f}")
print(f"2023 최저: {merged_fill.loc[merged_fill['합계출산율'].idxmin(), ['시도', '시군구', '합계출산율']].tolist()}")
for name in ["수도권", "비수도권"]:
    g = merged_fill.loc[merged_fill["시도"].isin(capital) == (name == "수도권"), "합계출산율"]
    print(f"  {name} 2023 평균(0 포함) = {g.mean():.4f}, n={len(g)}")

# ---------------------------------------------------------------- 재현성 대조
sep("[재현성] 같은 지시로 두 번 만든 merged.csv의 파일 단위 대조 (정렬만 다른 경우)")
run1 = merged.drop(columns=["권역"])
run2 = run1.sort_values(["시도", "시군구"]).reset_index(drop=True)
print("행 수 같음:", len(run1) == len(run2))
print("행 순서까지 같음(파일 단위):", run1.equals(run2))
key = ["시도", "시군구"]
a = run1.set_index(key).sort_index()
b = run2.set_index(key).sort_index()
print("키로 정렬해 맞춘 뒤 값 비교:", a.equals(b))
diff_rows = int((run1[key].values != run2[key].values).any(axis=1).sum())
print(f"정렬만 다른 두 파일에서 같은 행 번호의 시군구가 다른 행 수: {diff_rows} / {len(run1)}")

# ---------------------------------------------------------------- 검문소 3 대조표
sep("[검문소 3 대조표] 분석 산출물 검산에 쓰는 결정적 항목")
cap_t = merged.loc[merged["권역"] == "수도권", "합계출산율"].dropna()
non_t = merged.loc[merged["권역"] == "비수도권", "합계출산율"].dropna()
tt = stats.ttest_ind(non_t, cap_t, equal_var=False)
print(f"수도권 출산율: n={len(cap_t)}, 평균={cap_t.mean():.4f}, 표준편차={cap_t.std(ddof=1):.4f}")
print(f"비수도권 출산율: n={len(non_t)}, 평균={non_t.mean():.4f}, 표준편차={non_t.std(ddof=1):.4f}")
print(f"평균 차이(비수도권-수도권) = {non_t.mean() - cap_t.mean():.4f}, "
      f"Welch t={tt.statistic:.3f}, p={tt.pvalue:.3e}")
print(f"전체 2023 출산율: n={len(t23)}, 평균={t23.mean():.4f}, 중앙값={t23.median():.4f}")
print(f"회귀 재확인: n={len(sub)}, 절편={reg.intercept:.4f}, 기울기={reg.slope:.5f}, "
      f"p={reg.pvalue:.3e}, R2={reg.rvalue ** 2:.4f}")
print(f"결측 제외 개수: 229 - {int(merged['합계출산율'].isna().sum())} = {len(t23)}")

# ---------------------------------------------------------------- 검문소 4 대조표
sep("[검문소 4 대조표] 그림 대조에 쓰는 결정적 항목")
print(f"(가) 산점도 점 개수 = {len(sub)}, "
      f"x 범위 {sub['고령인구비율'].min():.2f} - {sub['고령인구비율'].max():.2f}, "
      f"y 범위 {sub['합계출산율'].min():.3f} - {sub['합계출산율'].max():.3f}")
print(f"(가) 회귀선 높이: 15%={reg.intercept + reg.slope * 15:.3f}, "
      f"25%={reg.intercept + reg.slope * 25:.3f}, 35%={reg.intercept + reg.slope * 35:.3f}")
print(f"(나) 점 개수 = {len(both)}, 45도선 위 {len(up)}곳, 아래 {int((both['변화'] < 0).sum())}곳")
print("(나) 45도선 위 목록:", [f"{r['시도']} {r['시군구']}" for _, r in up.iterrows()])
print(f"(나) x 범위 {both['합계출산율_2013'].min():.3f} - {both['합계출산율_2013'].max():.3f}, "
      f"y 범위 {both['합계출산율'].min():.3f} - {both['합계출산율'].max():.3f}")

# ---------------------------------------------------------------- 오류 시나리오 행렬
sep("[검문소 감도 행렬] 네 가지 오류가 검문소별 지표에 어떻게 나타나는가")


def indicators(mg, label):
    """merged 후보 하나에서 검문소 2/3/4의 결정적 지표를 뽑는다."""
    n_row = len(mg)
    n_na13 = int(mg["합계출산율_2013"].isna().sum())
    n_na23 = int(mg["합계출산율"].isna().sum())
    s = mg.dropna(subset=["고령인구비율", "합계출산율"])
    rg = stats.linregress(s["고령인구비율"], s["합계출산율"])
    b = mg.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
    b["변화"] = b["합계출산율"] - b["합계출산율_2013"]
    out = dict(label=label, rows=n_row, na13=n_na13, na23=n_na23, n=len(s),
               slope=rg.slope, r2=rg.rvalue ** 2, mean23=s["합계출산율"].mean(),
               both=len(b), up=int((b["변화"] > 0).sum()), mean13=b["합계출산율_2013"].mean())
    print(f"{label}: 행 수 {out['rows']}, 2023결측 {out['na23']}, 2013결측 {out['na13']}, "
          f"회귀 n {out['n']}, 기울기 {out['slope']:.5f}, R2 {out['r2']:.4f}, "
          f"2023평균 {out['mean23']:.4f} | 비교가능 {out['both']}곳, 45도선 위 {out['up']}곳, "
          f"2013평균 {out['mean13']:.4f}")
    return out


base = indicators(merged.drop(columns=["권역"]), "정상")

# 시나리오 A: 병합 키에서 시도를 빼고 시군구만으로 병합
try:
    mg_a = d2023.merge(d2013_fix, on="시군구", how="left", validate="one_to_one")
    print("A(시군구만 키): one_to_one 검증 통과")
except Exception as e:
    print("A(시군구만 키): validate 실패 ->", type(e).__name__)
    mg_a = d2023.merge(d2013_fix, on="시군구", how="left")
    mg_a = mg_a.rename(columns={"시도_x": "시도"})
print(f"A 행 수 {len(mg_a)} (정상 229), 중복으로 불어난 행 {len(mg_a) - 229}")
gs = mg_a[mg_a["시군구"] == "고성군"][["시도", "시군구", "합계출산율", "합계출산율_2013"]]
print("A 고성군 행:", gs.values.tolist())
a_ind = indicators(mg_a[["시도", "시군구", "고령인구비율", "합계출산율", "합계출산율_2013"]], "A 시군구만 키")

# 시나리오 B: 결측 행(군위군)을 삭제하고 병합
b_ind = indicators(merged_drop, "B 결측행 삭제")

# 시나리오 C: 결측을 0으로 대치
c_ind = indicators(merged_fill, "C 결측 0 대치")

# 시나리오 D: 미추홀구를 연결하지 않은 병합 (옛 이름 남구를 그대로 둠)
mg_d = d2023.merge(d2013, on=["시도", "시군구"], how="left", validate="one_to_one")
d_ind = indicators(mg_d, "D 미추홀구 미연결")

print()
print("검문소별 감지 여부 (정상값과 다르면 '잡힘')")
head = ["시나리오", "검2 행수", "검2 결측수", "검3 회귀n", "검3 기울기", "검4 비교가능", "검4 45도위"]
print(" | ".join(head))
for x in [a_ind, b_ind, c_ind, d_ind]:
    row = [x["label"],
           "잡힘" if x["rows"] != base["rows"] else "못잡음",
           "잡힘" if (x["na23"], x["na13"]) != (base["na23"], base["na13"]) else "못잡음",
           "잡힘" if x["n"] != base["n"] else "못잡음",
           "잡힘" if abs(x["slope"] - base["slope"]) > 1e-9 else "못잡음",
           "잡힘" if x["both"] != base["both"] else "못잡음",
           "잡힘" if x["up"] != base["up"] else "못잡음"]
    print(" | ".join(row))

# ---------------------------------------------------------------- 실행 시간
sep("[실행 시간] 파이프라인의 계산 자체는 몇 초인가")
import time  # noqa: E402

t0 = time.perf_counter()
a2023 = pd.read_csv(DATA / "sigungu_2023.csv", encoding="utf-8-sig")
a2013 = pd.read_csv(DATA / "sigungu_tfr_2013.csv", encoding="utf-8-sig")
t_read = time.perf_counter() - t0

t0 = time.perf_counter()
a2013.loc[(a2013["시도"] == "인천") & (a2013["시군구"] == "남구"), "시군구"] = "미추홀구"
mg = a2023.merge(a2013, on=["시도", "시군구"], how="left", validate="one_to_one")
mg.to_csv(DATA.parent / "code" / "ch13_out_merged.csv", index=False, encoding="utf-8-sig")
t_merge = time.perf_counter() - t0

t0 = time.perf_counter()
s = mg.dropna(subset=["고령인구비율", "합계출산율"])
r2 = stats.linregress(s["고령인구비율"], s["합계출산율"])
cap = mg.loc[mg["시도"].isin(capital), "합계출산율"].dropna()
non = mg.loc[~mg["시도"].isin(capital), "합계출산율"].dropna()
stats.ttest_ind(non, cap, equal_var=False)
t_stat = time.perf_counter() - t0

t0 = time.perf_counter()
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(s["고령인구비율"], s["합계출산율"], s=20)
xs = pd.Series([s["고령인구비율"].min(), s["고령인구비율"].max()])
ax.plot(xs, r2.intercept + r2.slope * xs)
fig.savefig(DATA.parent / "code" / "ch13_out_fig.png", dpi=150)
plt.close(fig)
t_plot = time.perf_counter() - t0

print(f"읽기 {t_read:.3f}초 / 병합·저장 {t_merge:.3f}초 / 통계 {t_stat:.3f}초 / "
      f"그림 1장 {t_plot:.3f}초")
print(f"합계 {t_read + t_merge + t_stat + t_plot:.3f}초")
(DATA.parent / "code" / "ch13_out_merged.csv").unlink()
(DATA.parent / "code" / "ch13_out_fig.png").unlink()

# ------------------------------------------------- 재현성: 정렬만 다른 두 파일
sep("[재현성] 한쪽을 총인구 내림차순으로 정렬했을 때의 행 번호 어긋남")
r1 = merged.drop(columns=["권역"])
r2 = r1.sort_values("총인구", ascending=False).reset_index(drop=True)
same = int((r1[key].values == r2[key].values).all(axis=1).sum())
print(f"같은 행 번호에 같은 시군구가 오는 행 수: {same} / {len(r1)}")
print("가나다순 첫 3행:", r1[["시도", "시군구"]].head(3).values.tolist())
print("총인구 내림차순 첫 3행:", r2[["시도", "시군구"]].head(3).values.tolist())
print("키로 맞춘 뒤 모든 셀이 같은가:",
      r1.set_index(key).sort_index().equals(r2.set_index(key).sort_index()))
