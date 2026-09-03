# 3주차 2회차(실습) 본문 수치 계산
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
# 본문의 요약통계·최댓값·최솟값·결측 관련 수치는 모두 이 스크립트의 출력에서 가져온다.
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
CSV = BASE / "data" / "sigungu_2023.csv"

df = pd.read_csv(CSV, encoding="utf-8-sig")

print("== (1) 행과 열의 개수 ==")
print(df.shape)

print("\n== (2) 열 이름과 자료형 ==")
print(df.dtypes)

cols = ["총인구", "고령인구비율", "합계출산율"]
print("\n== (3) 세 열의 요약통계 (describe 원문) ==")
print(df[cols].describe())

print("\n== (3') 세 열의 요약통계 (소수 3자리 반올림) ==")
print(df[cols].describe().round(3))

print("\n== (4) 총인구 최대·최소 시군구 ==")
for label, idx in (("최대", df["총인구"].idxmax()), ("최소", df["총인구"].idxmin())):
    r = df.loc[idx]
    print(f"{label}: {r['시도']} {r['시군구']} {int(r['총인구']):,}명  (데이터 {idx + 1}번째 행, 파일 {idx + 2}번째 줄)")

print("\n== (5) 고령인구비율·합계출산율 최대·최소 ==")
for c in ("고령인구비율", "합계출산율"):
    s = df[c]
    for label, idx in (("최대", s.idxmax()), ("최소", s.idxmin())):
        r = df.loc[idx]
        print(f"{c} {label}: {r['시도']} {r['시군구']} {r[c]:.3f}  (파일 {idx + 2}번째 줄)")

print("\n== (6) 결측 ==")
print(df.isnull().sum()[df.isnull().sum() > 0])
miss = df[df["합계출산율"].isnull()]
print(miss[["시도", "시군구", "총인구", "합계출산율", "출생아수"]])
print("결측 행의 파일 줄 번호:", [int(i) + 2 for i in miss.index])

print("\n== (7) 합계출산율 평균: 결측 제외 개수와 값 ==")
s = df["합계출산율"]
print(f"개수(결측 제외) = {s.count()}, 평균 = {s.mean():.6f}, 중앙값 = {s.median():.3f}")
print(f"참고: 결측을 0으로 잘못 채우면 평균 = {s.fillna(0).mean():.6f} (229개)")

print("\n== (8) 총인구 합계(전국) ==")
print(f"{int(df['총인구'].sum()):,}")

print("\n== (9) 산출물 CSV 형태(요약통계표를 저장했을 때의 모습) ==")
print(df[cols].describe().round(3).to_csv())

print("\n== (10) sigungu_tfr_2013.csv (과제용 참고) ==")
d13 = pd.read_csv(BASE / "data" / "sigungu_tfr_2013.csv", encoding="utf-8-sig")
print(d13.shape, list(d13.columns), "결측:", int(d13.isnull().sum().sum()))

print("\n== (11) 총인구 상위 10개 시군구 (그림 3-4의 자료) ==")
top10 = df.nlargest(10, "총인구")[["시도", "시군구", "총인구"]]
for rank, (idx, r) in enumerate(top10.iterrows(), start=1):
    print(f"{rank:2d}. {r['시도']} {r['시군구']} {int(r['총인구']):,}명  (파일 {idx + 2}번째 줄)")

print("\n== (12) 상위 10개의 인구 합계와 전국 대비 비중 ==")
total = df["총인구"].sum()
s10 = top10["총인구"].sum()
print(f"상위 10개 합 = {int(s10):,}명 / 전국 합 = {int(total):,}명 / 비중 = {s10 / total * 100:.1f}%")
print(f"상위 10개는 시군구 개수로는 전체 {len(df)}개의 {10 / len(df) * 100:.1f}%")

print("\n== (13) 열 이름 오타로 나는 오류 메시지 원문 (KeyError) ==")
try:
    df["총인구수"].mean()
except KeyError as e:
    print(f"{type(e).__name__}: {e}")

print("\n== (14) 잘못된 인코딩으로 읽을 때의 오류 메시지 원문 (UnicodeDecodeError) ==")
try:
    pd.read_csv(CSV, encoding="euc-kr")
except UnicodeDecodeError as e:
    print(f"{type(e).__name__}: {e}")

print("\n== (15) 없는 파일을 읽을 때의 오류 메시지 원문 (FileNotFoundError) ==")
try:
    pd.read_csv(BASE / "data" / "sigungu_2024.csv")
except FileNotFoundError as e:
    print(f"{type(e).__name__}: {e}")

print("\n== (16) 고령인구비율 상위 5개 시군구 (2.12 규칙 시험용) ==")
top5 = df.nlargest(5, "고령인구비율")[["시도", "시군구", "고령인구비율", "총인구"]]
for rank, (idx, r) in enumerate(top5.iterrows(), start=1):
    print(f"{rank}. {r['시도']} {r['시군구']} {r['고령인구비율']:.2f}%  "
          f"(총인구 {int(r['총인구']):,}명, 파일 {idx + 2}번째 줄)")

print("\n== (17) 상위 10개 1위와 10위의 인구 배수 ==")
print(f"{top10['총인구'].iloc[0] / top10['총인구'].iloc[-1]:.2f}배")
