# -*- coding: utf-8 -*-
# 14주차 2회차 실습 예시 수치 계산 스크립트
# 본문의 숫자 대조표(2.3절), 제언-근거 연결표(2.4절), 재현 검증(2.6절)에 쓰인
# 모든 수치는 이 스크립트가 data/ 폴더의 원본에서 직접 계산한 값이다.
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

d23 = pd.read_csv(DATA / "sigungu_2023.csv", encoding="utf-8-sig")
d13 = pd.read_csv(DATA / "sigungu_tfr_2013.csv", encoding="utf-8-sig")
merged = pd.read_csv(DATA / "sigungu_tfr_2013_2023.csv", encoding="utf-8-sig")

print("=" * 60)
print("[1] 원자료 기본 사실")
print("=" * 60)
print("2023년 파일:", d23.shape, "/ 2013년 파일:", d13.shape, "/ 병합 파일:", merged.shape)
tfr = d23["합계출산율"]
print(f"합계출산율 결측 {tfr.isna().sum()}개:",
      d23.loc[tfr.isna(), ["시도", "시군구"]].values.tolist())
print(f"합계출산율 평균(228개) = {tfr.mean():.4f}, 중앙값 = {tfr.median():.3f}")
print(f"최대 = {tfr.max():.3f} ({d23.loc[tfr.idxmax(), '시도']} {d23.loc[tfr.idxmax(), '시군구']}),"
      f" 최소 = {tfr.min():.3f} ({d23.loc[tfr.idxmin(), '시도']} {d23.loc[tfr.idxmin(), '시군구']})")

print()
print("=" * 60)
print("[2] 수도권 vs 비수도권 합계출산율 (2023)")
print("=" * 60)
capital = ["서울", "경기", "인천"]
d23["권역"] = np.where(d23["시도"].isin(capital), "수도권", "비수도권")
g_cap = d23.loc[d23["권역"] == "수도권", "합계출산율"].dropna()
g_non = d23.loc[d23["권역"] == "비수도권", "합계출산율"].dropna()
print(f"수도권: n={len(g_cap)}, 평균={g_cap.mean():.4f}, 중앙값={g_cap.median():.3f}")
print(f"비수도권: n={len(g_non)}, 평균={g_non.mean():.4f}, 중앙값={g_non.median():.3f}")
print(f"차이(비수도권 - 수도권) = {g_non.mean() - g_cap.mean():.4f}명")
print(f"비율(수도권 / 비수도권) = {g_cap.mean() / g_non.mean():.4f}")
t, p = stats.ttest_ind(g_non, g_cap, equal_var=False)
print(f"Welch t = {t:.2f}, p = {p:.2e}")
# 수도권 안의 상위 시군구 (이야기에 불리한 숫자 확인용)
cap_sorted = d23[d23["권역"] == "수도권"].sort_values("합계출산율", ascending=False)
print("수도권 상위 3:", cap_sorted[["시도", "시군구", "합계출산율"]].head(3).values.tolist())
print("수도권에서 비수도권 평균(0.877) 이상인 시군구 수:", int((g_cap >= g_non.mean()).sum()))

print()
print("=" * 60)
print("[3] 상관계수 (2023)")
print("=" * 60)
sub = d23.dropna(subset=["합계출산율"])
for col in ["인구밀도", "고령인구비율"]:
    r, pr = stats.pearsonr(sub[col], sub["합계출산율"])
    print(f"{col} vs 합계출산율: r = {r:.4f} (n={len(sub)}, p = {pr:.2e})")
reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])
print(f"회귀: 절편 {reg.intercept:.4f}, 기울기 {reg.slope:.5f}, R제곱 {reg.rvalue**2:.4f}")

print()
print("=" * 60)
print("[4] 2013년 대비 2023년 변화 (병합 파일, 229행)")
print("=" * 60)
m = merged.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
m["변화"] = m["합계출산율"] - m["합계출산율_2013"]
print(f"두 해 모두 값이 있는 시군구: {len(m)}개")
print(f"2013년 평균 = {m['합계출산율_2013'].mean():.4f}, 2023년 평균(같은 {len(m)}개) = {m['합계출산율'].mean():.4f}")
print(f"평균 변화 = {m['변화'].mean():.4f}명, 중앙값 변화 = {m['변화'].median():.4f}명")
n_up = int((m["변화"] > 0).sum())
n_same = int((m["변화"] == 0).sum())
n_down = int((m["변화"] < 0).sum())
print(f"상승 {n_up}개, 변동 없음 {n_same}개, 하락 {n_down}개 (하락 비율 {n_down / len(m) * 100:.1f}%)")
print("상승한 시군구:", m.loc[m["변화"] > 0, ["시도", "시군구", "합계출산율_2013", "합계출산율"]].values.tolist())
print("하락 폭 상위 3:",
      m.sort_values("변화")[["시도", "시군구", "합계출산율_2013", "합계출산율", "변화"]].head(3).round(3).values.tolist())
print(f"2013년 최고: {m.loc[m['합계출산율_2013'].idxmax(), ['시도', '시군구', '합계출산율_2013']].values.tolist()}")
print(f"2013년 최저: {m.loc[m['합계출산율_2013'].idxmin(), ['시도', '시군구', '합계출산율_2013']].values.tolist()}")
# 권역별 변화
m["권역"] = np.where(m["시도"].isin(capital), "수도권", "비수도권")
for k, g in m.groupby("권역"):
    print(f"{k}: 2013 평균 {g['합계출산율_2013'].mean():.4f} -> 2023 평균 {g['합계출산율'].mean():.4f},"
          f" 변화 {g['변화'].mean():.4f} (n={len(g)})")
# 2013년 1.0 미만 / 2023년 1.0 미만 시군구 수
print(f"합계출산율 1.0 미만 시군구: 2013년 {(m['합계출산율_2013'] < 1.0).sum()}개 -> 2023년 {(m['합계출산율'] < 1.0).sum()}개")

print()
print("=" * 60)
print("[5] 표본 대조용 개별 값 (원자료 행 번호 = 헤더 제외, 1부터)")
print("=" * 60)
for sido, sgg in [("서울", "관악구"), ("전남", "영광군"), ("경북", "울릉군"), ("인천", "미추홀구"), ("부산", "중구")]:
    r23 = d23[(d23["시도"] == sido) & (d23["시군구"] == sgg)]
    r13 = d13[(d13["시도"] == sido) & (d13["시군구"] == sgg)]
    v13 = r13["합계출산율_2013"].iloc[0] if len(r13) else None
    print(f"{sido} {sgg}: 2023 파일 {r23.index[0] + 1}행 합계출산율 {r23['합계출산율'].iloc[0]},"
          f" 총인구 {int(r23['총인구'].iloc[0])}, 2013 파일 값 {v13}")
r13 = d13[(d13["시도"] == "인천") & (d13["시군구"] == "남구")]
print(f"인천 남구(2013 파일 {r13.index[0] + 1}행): {r13['합계출산율_2013'].iloc[0]}")
