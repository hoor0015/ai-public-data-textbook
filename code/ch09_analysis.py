# 9주차 분석 코드: 집단 비교(t검정)와 단순회귀
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data" / "sigungu_2023.csv"
df = pd.read_csv(DATA)

# 수도권(서울·경기·인천) 여부
capital = ["서울", "경기", "인천"]
df["권역"] = np.where(df["시도"].isin(capital), "수도권", "비수도권")

print("=" * 60)
print("[1] 집단 비교: 수도권 vs 비수도권 고령인구비율")
print("=" * 60)
g_cap = df.loc[df["권역"] == "수도권", "고령인구비율"].dropna()
g_non = df.loc[df["권역"] == "비수도권", "고령인구비율"].dropna()
for name, g in [("수도권", g_cap), ("비수도권", g_non)]:
    print(f"{name}: n={len(g)}, 평균={g.mean():.2f}, 표준편차={g.std(ddof=1):.2f}, "
          f"중앙값={g.median():.2f}")
diff = g_non.mean() - g_cap.mean()
print(f"평균 차이(비수도권 - 수도권) = {diff:.2f} %포인트")

# Welch t검정 (등분산을 가정하지 않는 표준적 방법)
t, p = stats.ttest_ind(g_non, g_cap, equal_var=False)
print(f"Welch t검정: t = {t:.2f}, p = {p:.2e}")

print()
print("=" * 60)
print("[2] 참고: 수도권 vs 비수도권 합계출산율")
print("=" * 60)
t_cap = df.loc[df["권역"] == "수도권", "합계출산율"].dropna()
t_non = df.loc[df["권역"] == "비수도권", "합계출산율"].dropna()
for name, g in [("수도권", t_cap), ("비수도권", t_non)]:
    print(f"{name}: n={len(g)}, 평균={g.mean():.3f}, 표준편차={g.std(ddof=1):.3f}")
t2, p2 = stats.ttest_ind(t_non, t_cap, equal_var=False)
print(f"평균 차이 = {t_non.mean() - t_cap.mean():.3f}명")
print(f"Welch t검정: t = {t2:.2f}, p = {p2:.2e}")

print()
print("=" * 60)
print("[3] 상관과 단순회귀: 고령인구비율 -> 합계출산율")
print("=" * 60)
sub = df[["시도", "시군구", "고령인구비율", "합계출산율", "권역"]].dropna()
print(f"사용 관측치: {len(sub)}개 (합계출산율 결측 {df['합계출산율'].isna().sum()}개 제외)")
r, p_r = stats.pearsonr(sub["고령인구비율"], sub["합계출산율"])
print(f"상관계수 r = {r:.3f} (p = {p_r:.2e})")

reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])
print(f"회귀식: 합계출산율 = {reg.intercept:.3f} + {reg.slope:.5f} x 고령인구비율")
print(f"기울기 = {reg.slope:.5f} (10%포인트당 {reg.slope*10:.3f}명)")
print(f"기울기의 p값 = {reg.pvalue:.2e}, R제곱 = {reg.rvalue**2:.3f}")

# 본문 예시용 예측값
for x in [15, 25, 35]:
    print(f"  고령인구비율 {x}%일 때 예측 출산율 = {reg.intercept + reg.slope*x:.3f}명")

print()
print("=" * 60)
print("[4] 참고: 고령인구비율 -> 인구증가율 (교란 서사 확인용)")
print("=" * 60)
sub2 = df[["고령인구비율", "인구증가율"]].dropna()
r2_, p2_ = stats.pearsonr(sub2["고령인구비율"], sub2["인구증가율"])
print(f"상관계수 r = {r2_:.3f} (p = {p2_:.2e})")
