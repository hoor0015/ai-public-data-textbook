# -*- coding: utf-8 -*-
# 14주차 1차시(통합 장) 본문 수치 계산 스크립트
# 보고서 초안(1.2), verifier 대조표(1.4), 그림 대조(1.4)에 쓰인 모든 수치는
# 이 스크립트가 공통 데이터(9주차에 kosis MCP로 수집한 파일)에서 직접 계산한 값이다.
#   data/sigungu_mcp_2023.csv      2023년 시군구 229행 x 14열
#   data/sigungu_mcp_tfr_2013.csv  2013년 시군구 합계출산율 263행 (옛 행정구역·일반구 포함)
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 code/ch14_practice.py
from pathlib import Path

import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data"
d23 = pd.read_csv(DATA / "sigungu_mcp_2023.csv", encoding="utf-8-sig")
d13 = pd.read_csv(DATA / "sigungu_mcp_tfr_2013.csv", encoding="utf-8-sig")


def sep(title):
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)


sep("[1] 원자료 기본 사실")
print("2023 파일:", d23.shape, "/ 2013 파일:", d13.shape)
print("2023 결측:", d23.isna().sum()[lambda s: s > 0].to_dict())
print("권역별 시군구 수:", d23["수도권"].value_counts().to_dict())

sep("[2] 수도권 vs 비수도권 고령인구비율 (2023, Welch t검정)")
cap = d23.loc[d23["수도권"] == "수도권", "고령인구비율"]
non = d23.loc[d23["수도권"] == "비수도권", "고령인구비율"]
for name, g in [("수도권", cap), ("비수도권", non)]:
    print(f"{name}: n={len(g)}, 평균={g.mean():.2f}, 표준편차={g.std(ddof=1):.2f}, 중앙값={g.median():.2f}")
print(f"평균 차이(비수도권 - 수도권) = {non.mean() - cap.mean():.2f} %포인트")
t, p = stats.ttest_ind(non, cap, equal_var=False)
print(f"Welch t = {t:.2f}, p = {p:.2e}")

sep("[3] 수도권 vs 비수도권 합계출산율 (2023, 참고)")
tc = d23.loc[d23["수도권"] == "수도권", "합계출산율"]
tn = d23.loc[d23["수도권"] == "비수도권", "합계출산율"]
for name, g in [("수도권", tc), ("비수도권", tn)]:
    print(f"{name}: n={len(g)}, 평균={g.mean():.3f}, 중앙값={g.median():.3f}")
t2, p2 = stats.ttest_ind(tn, tc, equal_var=False)
print(f"평균 차이 = {tn.mean() - tc.mean():.3f}명, Welch t = {t2:.2f}, p = {p2:.2e}")
print(f"전체 평균 = {d23['합계출산율'].mean():.3f}명 (n={d23['합계출산율'].notna().sum()})")
over = d23[(d23["수도권"] == "수도권") & (d23["합계출산율"] >= tn.mean())]
print(f"수도권에서 비수도권 평균({tn.mean():.3f}) 이상인 시군구 {len(over)}개:",
      over.sort_values("합계출산율", ascending=False)[["시도", "시군구", "합계출산율"]].values.tolist())

sep("[4] 고령인구비율 -> 합계출산율 상관과 단순회귀 (2023)")
sub = d23.dropna(subset=["고령인구비율", "합계출산율"])
r, pr = stats.pearsonr(sub["고령인구비율"], sub["합계출산율"])
reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])
print(f"n={len(sub)}, r = {r:.3f} (p = {pr:.2e})")
print(f"회귀식: 합계출산율 = {reg.intercept:.3f} + {reg.slope:.5f} x 고령인구비율")
print(f"기울기 = {reg.slope:.5f} (10%포인트당 {reg.slope * 10:.3f}명), p = {reg.pvalue:.2e}, R제곱 = {reg.rvalue ** 2:.3f}")

sep("[5] 2013년 대비 2023년 합계출산율 변화")
# 2013 파일의 옛 이름을 2023 행정구역에 연결하는 규칙
#   인천 남구(변동전) -> 인천 미추홀구 (2018년 이름 변경)
#   충북 청주시(변동전) -> 충북 청주시 (2014년 청원군 통합 전의 옛 청주시 값)
#   경북 군위군(변동전) -> 대구 군위군 (2023년 7월 대구 편입)
# 나머지 2013 전용 행(일반구 등)은 2023 목록에 없으므로 결합에서 자연히 빠진다.
rename = {("인천", "남구(변동전)"): ("인천", "미추홀구"),
          ("충북", "청주시(변동전)"): ("충북", "청주시"),
          ("경북", "군위군(변동전)"): ("대구", "군위군")}
d13f = d13.copy()
for (s0, g0), (s1, g1) in rename.items():
    mask = (d13f["시도"] == s0) & (d13f["시군구"] == g0)
    d13f.loc[mask, ["시도", "시군구"]] = [s1, g1]
m = d23.merge(d13f, on=["시도", "시군구"], how="left", validate="one_to_one")
print(f"결합 행 수 {len(m)}, 2013 결측 {int(m['합계출산율_2013'].isna().sum())}")
print("2013 파일에서 결합되지 않은 행 수:", len(d13f) - int(m["합계출산율_2013"].notna().sum()))
m = m.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
m["변화"] = m["합계출산율"] - m["합계출산율_2013"]
print(f"두 해 모두 값이 있는 시군구: {len(m)}개")
print(f"2013 평균 = {m['합계출산율_2013'].mean():.3f}, 2023 평균 = {m['합계출산율'].mean():.3f}")
print(f"평균 변화 = {m['변화'].mean():.3f}명, 중앙값 변화 = {m['변화'].median():.3f}명")
n_up, n_same, n_down = int((m["변화"] > 0).sum()), int((m["변화"] == 0).sum()), int((m["변화"] < 0).sum())
print(f"상승 {n_up}개, 변동 없음 {n_same}개, 하락 {n_down}개 (하락 비율 {n_down / len(m) * 100:.1f}%)")
print("상승한 시군구:", m.loc[m["변화"] > 0, ["시도", "시군구", "합계출산율_2013", "합계출산율"]].values.tolist())
print("하락 폭 상위 3:",
      m.sort_values("변화")[["시도", "시군구", "합계출산율_2013", "합계출산율", "변화"]].head(3).round(3).values.tolist())
for k, g in m.groupby("수도권"):
    print(f"{k}: n={len(g)}, 2013 평균 {g['합계출산율_2013'].mean():.3f} -> 2023 평균 {g['합계출산율'].mean():.3f},"
          f" 평균 변화 {g['변화'].mean():.3f}")
print(f"합계출산율 1.0 미만 시군구: 2013년 {(m['합계출산율_2013'] < 1.0).sum()}개 -> 2023년 {(m['합계출산율'] < 1.0).sum()}개")
# 변화와 2013년 수준의 관계 (그림 대조용: 2013년 값이 높았던 곳일수록 많이 내려갔는가)
rc, pc = stats.pearsonr(m["합계출산율_2013"], m["변화"])
print(f"2013년 값과 변화의 상관 r = {rc:.3f} (p = {pc:.2e})")
