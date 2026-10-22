# 13주차 1차시(통합 장) 본문 수치 계산: 수도권·비수도권의 고령화와 출산율 파이프라인
# 입력: 9주차에 kosis MCP로 수집·결합한 data/sigungu_mcp_2023.csv, data/sigungu_mcp_tfr_2013.csv
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 <이 파일 경로>
from pathlib import Path

import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data"
d2023 = pd.read_csv(DATA / "sigungu_mcp_2023.csv", encoding="utf-8-sig")
d2013 = pd.read_csv(DATA / "sigungu_mcp_tfr_2013.csv", encoding="utf-8-sig")


def sep(title):
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)


def row_no(df, sido, gu):
    """VSCode 줄 번호(1행은 열 이름)."""
    idx = df.index[(df["시도"] == sido) & (df["시군구"] == gu)]
    return int(idx[0]) + 2


# ---------------------------------------------------------------- 검증 지점 1
sep("[검증 지점 1] 수집 확인: 행 수, 열 목록, 결측")
print("2023:", d2023.shape)
print("  열:", list(d2023.columns))
print("2013:", d2013.shape, list(d2013.columns))
na = d2023.isna().sum()
print("2023 결측:", na[na > 0].to_dict())
print("  결측 행:", d2023.loc[d2023.isna().any(axis=1), ["시도", "시군구"]].values.tolist())
print("2013 결측 칸 수:", int(d2013.isna().sum().sum()))
print("수도권 열 집계:", d2023["수도권"].value_counts().to_dict())
print("수도권 시도:", sorted(d2023.loc[d2023["수도권"] == "수도권", "시도"].unique()))
print("2013 '(변동전)' 행:", d2013.loc[d2013["시군구"].str.contains("변동전"),
                                     ["시도", "시군구", "합계출산율_2013"]].values.tolist())

# ---------------------------------------------------------------- 검증 지점 2
sep("[검증 지점 2] 진단 병합(이름 그대로)")
diag = d2023.merge(d2013, on=["시도", "시군구"], how="outer", indicator=True)
print(diag["_merge"].value_counts().to_dict())
print("2023에만:", diag.loc[diag["_merge"] == "left_only", ["시도", "시군구"]].values.tolist())
ro = diag.loc[diag["_merge"] == "right_only", ["시도", "시군구"]]
print(f"2013에만 {len(ro)}행:", ro.values.tolist())
print("  2013에만 중 '(변동전)' 아닌 행(일반구) 수:", int((~ro["시군구"].str.contains("변동전")).sum()))
not_gu = ["군위군(변동전)", "남구(변동전)", "청원군(변동전)", "청주시(변동전)"]
print("  2013에만 중 일반구 전체(상당구·흥덕구(변동전) 포함):", int((~ro["시군구"].isin(not_gu)).sum()))

sep("[검증 지점 2] 사람이 정한 대응표로 본 병합")
# 대응표: 옛 표기를 연결한다. 청주시의 2013년 값은 2014년 청원군 통합 전 옛 청주시 값이다(7주차와 같은 처리).
fix = d2013.copy()
rename = {("인천", "남구(변동전)"): ("인천", "미추홀구"),
          ("경북", "군위군(변동전)"): ("대구", "군위군"),
          ("충북", "청주시(변동전)"): ("충북", "청주시")}
for (s0, g0), (s1, g1) in rename.items():
    m = (fix["시도"] == s0) & (fix["시군구"] == g0)
    fix.loc[m, ["시도", "시군구"]] = [s1, g1]
merged = d2023.merge(fix, on=["시도", "시군구"], how="left", validate="one_to_one")
print("본 병합:", merged.shape, "/ 2013 값이 빈 행:",
      merged.loc[merged["합계출산율_2013"].isna(), ["시도", "시군구"]].values.tolist())
for sido, gu in [("인천", "미추홀구"), ("대구", "군위군"), ("강원", "고성군"), ("경남", "고성군"),
                 ("충북", "청주시")]:
    r = merged[(merged["시도"] == sido) & (merged["시군구"] == gu)].iloc[0]
    print(f"  {sido} {gu}: 2023={r['합계출산율']}, 2013={r['합계출산율_2013']}, "
          f"merged 행 {row_no(merged, sido, gu)}")
print("  2013 파일 행: 인천 남구(변동전)", row_no(d2013, "인천", "남구(변동전)"),
      "/ 경북 군위군(변동전)", row_no(d2013, "경북", "군위군(변동전)"),
      "/ 충북 청주시(변동전)", row_no(d2013, "충북", "청주시(변동전)"),
      "/ 강원 고성군", row_no(d2013, "강원", "고성군"), "/ 경남 고성군", row_no(d2013, "경남", "고성군"))
print("병합 후 열 수:", merged.shape[1])

# 잘못된 키 예: 시군구만 키
wrong = d2023.merge(fix, on="시군구", how="left")
print("시군구만 키로 병합했을 때 행 수:", len(wrong))

# ---------------------------------------------------------------- 검증 지점 3
sep("[검증 지점 3] 분석: 수도권 vs 비수도권 Welch t검정")
cap = merged["수도권"] == "수도권"
res = {}
for col, digits in [("고령인구비율", 2), ("합계출산율", 3)]:
    a = merged.loc[cap, col].dropna()
    b = merged.loc[~cap, col].dropna()
    t = stats.ttest_ind(b, a, equal_var=False)
    res[col] = (a, b, t)
    print(f"{col}: 수도권 n={len(a)} 평균={a.mean():.{digits + 1}f} | 비수도권 n={len(b)} 평균={b.mean():.{digits + 1}f} | "
          f"차이(비-수)={b.mean() - a.mean():.{digits + 1}f} | Welch t={t.statistic:.2f}, p={t.pvalue:.2e}")

sep("[검증 지점 3] 분석: 고령인구비율 -> 합계출산율 단순회귀")
sub = merged.dropna(subset=["고령인구비율", "합계출산율"])
reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])
print(f"n={len(sub)}, 절편={reg.intercept:.4f}, 기울기={reg.slope:.5f}, p={reg.pvalue:.2e}, "
      f"R2={reg.rvalue ** 2:.4f}, r={reg.rvalue:.3f}")
for x in [15, 25, 35]:
    print(f"  고령인구비율 {x}%일 때 회귀선 높이 = {reg.intercept + reg.slope * x:.3f}")
print(f"  고령인구비율 범위 {sub['고령인구비율'].min()} - {sub['고령인구비율'].max()}, "
      f"합계출산율 범위 {sub['합계출산율'].min()} - {sub['합계출산율'].max()}")
for name, mask in [("수도권", cap), ("비수도권", ~cap)]:
    s = sub[mask.loc[sub.index]]
    rg = stats.linregress(s["고령인구비율"], s["합계출산율"])
    print(f"  {name}만 회귀: n={len(s)}, 기울기={rg.slope:.5f}, R2={rg.rvalue ** 2:.4f}, p={rg.pvalue:.2e}")

sep("[검증 지점 3] 분석: 2013 대비 2023 합계출산율 변화(권역별)")
both = merged.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
both["변화"] = both["합계출산율"] - both["합계출산율_2013"]
print(f"비교 가능 {len(both)}곳")
print(f"전체: 2013 평균={both['합계출산율_2013'].mean():.3f}, 2023 평균={both['합계출산율'].mean():.3f}, "
      f"변화 평균={both['변화'].mean():.3f}")
for name in ["수도권", "비수도권"]:
    g = both[both["수도권"] == name]
    print(f"{name}: n={len(g)}, 2013 평균={g['합계출산율_2013'].mean():.3f}, "
          f"2023 평균={g['합계출산율'].mean():.3f}, 변화 평균={g['변화'].mean():.3f}, "
          f"오른 곳={int((g['변화'] > 0).sum())}")
up = both[both["변화"] > 0]
print(f"오른 곳 {len(up)}곳:", up[["시도", "시군구", "합계출산율_2013", "합계출산율"]].values.tolist())
lo = both.loc[both["변화"].idxmin()]
print(f"가장 크게 내린 곳: {lo['시도']} {lo['시군구']} {lo['합계출산율_2013']} -> {lo['합계출산율']} ({lo['변화']:.3f})")

# ---------------------------------------------------------------- 검증 지점 4
sep("[검증 지점 4] 그림 대조용 결정적 항목")
print(f"(가) 산점도 점 개수 {len(sub)} (수도권 {int(cap.loc[sub.index].sum())}, 비수도권 {int((~cap).loc[sub.index].sum())})")
cs = sub[cap.loc[sub.index]]
print(f"(가) 수도권 점: 고령인구비율 25% 이하 {int((cs['고령인구비율'] <= 25).sum())}곳 / {len(cs)}, "
      f"합계출산율 범위 {cs['합계출산율'].min()} - {cs['합계출산율'].max()}")
print(f"(나) 변화 그림 점 개수 {len(both)}, 45도선 위 {len(up)}곳, 아래 {int((both['변화'] < 0).sum())}곳, "
      f"같음 {int((both['변화'] == 0).sum())}곳")

# ---------------------------------------------------------------- 재현 실행 보고 세 줄
sep("[재현 실행] 보고 세 줄")
print(f"(1) merged.csv: {len(merged)}행, 2013 값이 빈 행 {int(merged['합계출산율_2013'].isna().sum())}")
print(f"(2) 회귀: 관측치 {len(sub)}, 기울기 {reg.slope:.5f}, R제곱 {reg.rvalue ** 2:.3f}")
a, b, t = res["합계출산율"]
print(f"(3) 합계출산율 Welch t = {t.statistic:.2f}, 수도권 평균 {a.mean():.3f}, 비수도권 평균 {b.mean():.3f}")
