# 5주차 1회차 본문 수치 계산 (스크립트 유무에 따라 달라질 수 있는 계산의 예)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data" / "sigungu_2023.csv"
df = pd.read_csv(DATA)

n = len(df)
miss = df["합계출산율"].isna().sum()
print(f"행 수: {n}, 합계출산율 결측: {miss}")
print(f"결측 비율(소수 둘째 자리): {miss / n * 100:.2f}%")
print(f"결측 비율(소수 첫째 자리): {miss / n * 100:.1f}%")

tfr = df["합계출산율"]
print(f"합계출산율 평균(결측 제외, {tfr.notna().sum()}개): {tfr.mean():.3f}")
print(f"합계출산율 평균(결측을 0으로 채움, {n}개): {tfr.fillna(0).mean():.3f}")
print(f"합계출산율 중앙값(결측 제외): {tfr.median():.3f}")
print(f"합계출산율 중앙값(결측을 0으로 채움): {tfr.fillna(0).median():.3f}")

print(f"시도 고유값 수: {df['시도'].nunique()}")
print(f"시군구 고유값 수(결측 제외 기본값): {df['시군구'].nunique()}")
print(f"중복 행 수: {df.duplicated().sum()}")
