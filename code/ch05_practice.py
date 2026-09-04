# -*- coding: utf-8 -*-
"""5주차 2회차 실습 장(05-2)에 쓰는 수치를 실제로 계산해 확인한다.

실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"

확인 대상
 (1) 2.5절: kordoc이 변환한 Markdown 표(다섯 행)를 CSV로 옮겨 pandas로 읽었을 때의 출력
 (2) 2.5절 틀리는 장면: 한 행을 빠뜨린 사본을 읽으면 무엇이 달라지는가
 (3) 자주 겪는 문제: 천 단위 쉼표를 그대로 둔 사본의 자료형
 (4) 2.7절 검증: 예시 문서의 표 값이 data/sigungu_2023.csv의 상위 5곳과 같은가
산출 파일은 code/ch05_out/ 아래에 만든다 (학생 실습에서는 data/ 아래에 만든다).
"""
import io
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "ch05_out"
OUT.mkdir(exist_ok=True)

# kordoc이 인구현황보고_예시.hwpx를 변환해 만든 Markdown 표의 다섯 행 (원문 그대로)
ROWS = [
    (1, "경기", "수원시", 1190964),
    (2, "경기", "고양시", 1076535),
    (3, "경기", "용인시", 1074971),
    (4, "경남", "창원시", 1021487),
    (5, "경기", "성남시", 922518),
]
HEADER = "순위,시도,시군구,총인구"


def write_csv(path, rows, thousands=False):
    """네 열짜리 CSV를 만든다. thousands=True면 총인구에 천 단위 쉼표를 남기고 따옴표로 묶는다."""
    lines = [HEADER]
    for rank, sido, sgg, pop in rows:
        value = f'"{pop:,}"' if thousands else str(pop)
        lines.append(f"{rank},{sido},{sgg},{value}")
    with io.open(path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- (1) 옳게 옮긴 CSV
good = OUT / "인구상위5.csv"
write_csv(good, ROWS)
print("########## (1) 표를 옮긴 CSV를 pandas로 읽기 ##########")
print("--- 파일 원문 ---")
print(io.open(good, encoding="utf-8-sig").read().rstrip())

df = pd.read_csv(good)
print("\n--- df ---")
print(df.to_string(index=False))
print("\n--- 자료형 ---")
print(df.dtypes.to_string())
print("\n행 수:", len(df), " 열 수:", df.shape[1])
print("총인구 합계:", f"{df['총인구'].sum():,}")
print("총인구 평균:", f"{df['총인구'].mean():,.1f}")
print("1위와 5위의 차이:", f"{df['총인구'].max() - df['총인구'].min():,}")

# ---------------------------------------------------------------- (2) 한 행을 빠뜨린 사본
bad = OUT / "인구상위5_행누락.csv"
write_csv(bad, ROWS[:4])
print("\n\n########## (2) 다섯째 행(성남시)을 빠뜨린 사본 ##########")
bad_df = pd.read_csv(bad)
print(bad_df.to_string(index=False))
print("행 수:", len(bad_df), "(원문 표는 5행)")
print("순위 열의 마지막 값:", int(bad_df["순위"].max()), "(원문 표는 5)")
print("총인구 합계:", f"{bad_df['총인구'].sum():,}")
print("빠진 행이 합계에 미친 차이:", f"{df['총인구'].sum() - bad_df['총인구'].sum():,}")

# ---------------------------------------------------------------- (3) 천 단위 쉼표를 남긴 사본
comma = OUT / "인구상위5_쉼표.csv"
write_csv(comma, ROWS, thousands=True)
print("\n\n########## (3) 천 단위 쉼표를 그대로 둔 사본 ##########")
print("--- 파일 원문 ---")
print(io.open(comma, encoding="utf-8-sig").read().rstrip())
comma_df = pd.read_csv(comma)
print("\n총인구 자료형:", comma_df["총인구"].dtype)
print("합계를 내면:", comma_df["총인구"].sum())
print("(문자열이라 숫자로 더해지지 않고 이어 붙는다)")
fixed = comma_df.copy()
fixed["총인구"] = fixed["총인구"].str.replace(",", "", regex=False).astype("int64")
print("쉼표를 지우고 숫자로 바꾼 뒤 합계:", f"{fixed['총인구'].sum():,}", " 자료형:", fixed["총인구"].dtype)

# ---------------------------------------------------------------- (4) 원본 데이터와 대조
print("\n\n########## (4) data/sigungu_2023.csv의 총인구 상위 5곳과 대조 ##########")
src = pd.read_csv(DATA / "sigungu_2023.csv")
top5 = src.nlargest(5, "총인구")[["시도", "시군구", "총인구"]].reset_index(drop=True)
top5["총인구"] = top5["총인구"].astype("int64")
print(top5.to_string(index=False))
same = [
    (r[1], r[2], r[3]) == (top5.loc[i, "시도"], top5.loc[i, "시군구"], int(top5.loc[i, "총인구"]))
    for i, r in enumerate(ROWS)
]
print("\n다섯 행이 모두 원본 데이터와 같은가:", all(same), same)
print("전체 229개 시군구 총인구 합계 대비 상위 5곳의 비중:",
      f"{df['총인구'].sum() / src['총인구'].sum() * 100:.1f}%")

# 문서의 다섯 곳이 sigungu_2023.csv의 몇 번째 줄에 있는가 (열 이름 줄이 1번째 줄)
print("\n--- 파일 줄 번호 (VSCode에서 연 CSV 기준) ---")
for _, sido, sgg, pop in ROWS:
    hit = src[(src["시도"] == sido) & (src["시군구"] == sgg)]
    for idx, row in hit.iterrows():
        print(f"{sido} {sgg}: {idx + 2}번째 줄, 총인구 {int(row['총인구']):,}")

# 문서 본문 문장에 나오는 합계출산율 세 값
tfr = src["합계출산율"]
hi, lo = src.loc[tfr.idxmax()], src.loc[tfr.idxmin()]
print("\n--- 합계출산율 (문서 본문 문장의 세 값) ---")
print(f"최고: {hi['시도']} {hi['시군구']} {hi['합계출산율']:.3f} ({tfr.idxmax() + 2}번째 줄)")
print(f"최저: {lo['시도']} {lo['시군구']} {lo['합계출산율']:.3f} ({tfr.idxmin() + 2}번째 줄)")
print(f"중앙값: {tfr.median():.3f}   계산에 쓴 값의 개수: {tfr.count()} (전체 {len(src)}행)")
