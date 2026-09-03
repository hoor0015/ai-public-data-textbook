# -*- coding: utf-8 -*-
"""4주차 2회차 실습 장(04-2)에 쓰는 수치를 data/ 파일에서 직접 계산한다.

실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python code/ch04_practice.py
"파일 줄 번호"는 VSCode에서 CSV를 열었을 때의 줄 번호다 (열 이름 줄이 1번째 줄, 첫 데이터가 2번째 줄).
계산 대상: (1) sigungu_2023.csv 프로파일링 보고서의 표 값, (2) 행·열 수 대조 출력,
(3) income_dist.csv에 같은 절차를 적용했을 때의 표 값(연도 열의 무의미한 평균 포함),
(4) 독립 검산 대조표에 쓰는 값.
"""
import io
import os

import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def raw_lines(path):
    with io.open(path, encoding="utf-8-sig") as f:
        return f.read().splitlines()


def profile(name):
    path = os.path.join(root, "data", name)
    df = pd.read_csv(path)  # 기본 인코딩(utf-8)으로 읽어도 BOM이 열 이름에 남지 않는지 확인
    lines = raw_lines(path)
    print(f"\n==================== {name} ====================")
    print("첫 열 이름 repr:", repr(df.columns[0]))
    print("행 수:", len(df), " 열 수:", df.shape[1])
    print("파일 전체 줄 수(열 이름 줄 포함):", len(lines), " 열 이름 줄의 열 개수:", len(lines[0].split(",")))
    print("[대조] 데이터 줄 수", len(lines) - 1, "vs pandas 행 수", len(df), "->", "일치" if len(lines) - 1 == len(df) else "불일치")
    print("[대조] 열 이름 줄 열 개수", len(lines[0].split(",")), "vs pandas 열 수", df.shape[1], "->",
          "일치" if len(lines[0].split(",")) == df.shape[1] else "불일치")

    print("\n--- 열 정보 표 (자료형, 결측 개수, 결측 비율 %, 고유값 개수) ---")
    info = pd.DataFrame({
        "자료형": df.dtypes.astype(str),
        "결측 개수": df.isnull().sum(),
        "결측 비율(%)": (df.isnull().mean() * 100).round(2),
        "고유값 개수": df.nunique(),
    })
    print(info.to_string())

    print("\n--- 수치형 요약 (평균, 표준편차, 최솟값, 중앙값, 최댓값) ---")
    num = df.select_dtypes("number")
    summ = pd.DataFrame({
        "개수": num.count(),
        "평균": num.mean(),
        "표준편차": num.std(),
        "최솟값": num.min(),
        "중앙값": num.median(),
        "최댓값": num.max(),
    })
    print(summ.to_string(float_format=lambda x: f"{x:,.3f}"))

    print("\n--- 문자형 열 최빈값 ---")
    for c in df.select_dtypes(exclude="number").columns:
        vc = df[c].value_counts()
        print(f"{c}: 최빈값 {vc.index[0]} ({vc.iloc[0]}회), 고유값 {df[c].nunique()}개")

    print("\n--- 품질 경고 ---")
    print("결측 비율 30% 이상 열:", list(info.index[info["결측 비율(%)"] >= 30]))
    print("값이 하나뿐인 열:", list(info.index[info["고유값 개수"] == 1]))
    print("중복 행 수:", int(df.duplicated().sum()))
    return df, lines


df, lines = profile("sigungu_2023.csv")
df["파일줄번호"] = df.index + 2

print("\n--- 2.1 수동 보고서 표에 쓰는 값 ---")
for c in ["총인구", "고령인구비율", "합계출산율"]:
    s = df[c]
    print(f"{c}: 개수 {s.count()}, 최소 {s.min():,.3f}, 최대 {s.max():,.3f}, 평균 {s.mean():,.3f}, 중앙값 {s.median():,.3f}")

print("\n--- 최댓값·최솟값 행과 파일 줄 번호 ---")
cols = ["시도", "시군구", "파일줄번호"]
for c in ["총인구", "고령인구비율", "합계출산율"]:
    mx = df.loc[df[c].idxmax()]
    mn = df.loc[df[c].idxmin()]
    print(f"{c} 최대: {mx['시도']} {mx['시군구']} {mx[c]:,.3f} (줄 {mx['파일줄번호']}) / "
          f"최소: {mn['시도']} {mn['시군구']} {mn[c]:,.3f} (줄 {mn['파일줄번호']})")

print("\n--- 결측 행 ---")
print(df[df["합계출산율"].isna()][["시도", "시군구", "합계출산율", "출생아수", "파일줄번호"]].to_string(index=False))

print("\n--- 2.7 독립 검산 대조표에 쓰는 값 ---")
tfr = df["합계출산율"]
print("합계출산율 평균(결측 제외, 228개):", round(tfr.mean(), 4))
print("합계출산율 합계를 229로 나눈 값(결측을 0으로 채운 경우):", round(tfr.sum() / len(df), 4))
print("합계출산율 중앙값:", round(tfr.median(), 4))
print("총인구 평균:", round(df["총인구"].mean(), 1), " 총인구 합계:", int(df["총인구"].sum()))
print("고령인구비율 평균:", round(df["고령인구비율"].mean(), 3))
print("시도별 시군구 수 상위 3:")
print(df["시도"].value_counts().head(3).to_string())
print("시군구 이름 중복 상위 5:")
print(df["시군구"].value_counts().head(5).to_string())

df2, lines2 = profile("income_dist.csv")
print("\n--- income_dist.csv 파일 줄 번호 ---")
print("2011 행: 줄 2, 2023 행: 줄", len(lines2))
print("연도 평균:", df2["연도"].mean(), " 연도 표준편차:", round(df2["연도"].std(), 3))
print("지니계수 첫해-마지막해:", df2["지니계수"].iloc[0], "->", df2["지니계수"].iloc[-1],
      " 차이:", round(df2["지니계수"].iloc[0] - df2["지니계수"].iloc[-1], 3))
print("소득5분위배율 첫해-마지막해:", df2["소득5분위배율"].iloc[0], "->", df2["소득5분위배율"].iloc[-1])
print("지니계수 최댓값 연도:", int(df2.loc[df2["지니계수"].idxmax(), "연도"]),
      " 최솟값 연도:", int(df2.loc[df2["지니계수"].idxmin(), "연도"]))
print("연도 열을 제외한 수치형 요약:")
print(df2[["지니계수", "소득5분위배율"]].describe().T.to_string(float_format=lambda x: f"{x:.3f}"))

# =====================================================================
# 2.8 세 번째 데이터: sigungu_tfr_2013.csv (세 보고서의 형식 일관성 대조표)
# =====================================================================
df3, lines3 = profile("sigungu_tfr_2013.csv")
df3["파일줄번호"] = df3.index + 2
COL13 = "합계출산율_2013"
print("\n--- sigungu_tfr_2013.csv 값 ---")
print("파일 전체 줄 수:", len(lines3), " 마지막 데이터 줄 번호:", len(lines3))
s13 = df3[COL13]
print(f"{COL13}: 개수 {s13.count()}, 최소 {s13.min():.3f}, 최대 {s13.max():.3f}, "
      f"평균 {s13.mean():.3f}, 중앙값 {s13.median():.3f}, 표준편차 {s13.std():.3f}")
mx13 = df3.loc[s13.idxmax()]
mn13 = df3.loc[s13.idxmin()]
print(f"최대: {mx13['시도']} {mx13['시군구']} {mx13[COL13]} (줄 {mx13['파일줄번호']})")
print(f"최소: {mn13['시도']} {mn13['시군구']} {mn13[COL13]} (줄 {mn13['파일줄번호']})")
print("시도 고유값:", df3["시도"].nunique(), " 시군구 고유값:", df3["시군구"].nunique())
print("결측 열:", list(df3.columns[df3.isnull().sum() > 0]))
print("중복 행 수:", int(df3.duplicated().sum()))
print("2013 평균과 2023 평균(각 파일 안에서만 계산):",
      round(s13.mean(), 3), "/", round(df["합계출산율"].mean(), 3))
print("군위군 2013 행:")
print(df3[df3["시군구"] == "군위군"][["시도", "시군구", COL13, "파일줄번호"]].to_string(index=False))

print("\n--- 세 파일 형식 일관성 대조표에 쓰는 값 ---")
for name, d in [("sigungu_2023.csv", df.drop(columns=["파일줄번호"])),
                ("income_dist.csv", df2),
                ("sigungu_tfr_2013.csv", df3.drop(columns=["파일줄번호"]))]:
    num = d.select_dtypes("number")
    txt = d.select_dtypes(exclude="number")
    miss = [c for c in d.columns if d[c].isnull().sum() > 0]
    print(f"{name}: {len(d)}행 {d.shape[1]}열 / 문자형 {list(txt.columns)} / "
          f"수치형 {list(num.columns)} / 결측 열 {miss} / 중복 행 {int(d.duplicated().sum())}")

# =====================================================================
# 2.9 결측을 "-"로 표기한 사본에서 무슨 일이 벌어지는가
#     (원본은 건드리지 않고 임시 파일에 사본을 만들어 확인한다)
# =====================================================================
import tempfile

print("\n\n########## 2.9 결측을 '-'로 표기한 사본 ##########")
src = os.path.join(root, "data", "sigungu_2023.csv")
orig = pd.read_csv(src)
dash = orig.copy()
for c in ["합계출산율", "출생아수"]:
    dash[c] = dash[c].astype(object).where(orig[c].notna(), "-")
with tempfile.TemporaryDirectory() as td:
    tmp = os.path.join(td, "sigungu_2023_dash.csv")
    dash.to_csv(tmp, index=False, encoding="utf-8")
    with io.open(tmp, encoding="utf-8") as f:
        dlines = f.read().splitlines()
    dd = pd.read_csv(tmp)

print("사본 파일 줄 수:", len(dlines), " pandas 행 수:", len(dd), " 열 수:", dd.shape[1])
print("[대조 절이 출력할 내용] 데이터 줄 수", len(dlines) - 1, "vs 행 수", len(dd), "->",
      "일치" if len(dlines) - 1 == len(dd) else "불일치")
print("군위군 줄(사본):", dlines[72][:200])
info_d = pd.DataFrame({
    "자료형": dd.dtypes.astype(str),
    "결측 개수": dd.isnull().sum(),
    "고유값 개수": dd.nunique(),
})
print(info_d.loc[["시도", "총인구", "고령인구비율", "합계출산율", "출생아수"]].to_string())
print("사본에서 수치형으로 인식된 열:", list(dd.select_dtypes("number").columns))
print("원본에서 수치형으로 인식된 열:", list(orig.select_dtypes("number").columns))
print("사본에서 수치형 요약표에 남는 열 수:", dd.select_dtypes("number").shape[1],
      "/ 원본:", orig.select_dtypes("number").shape[1])
print("사본 합계출산율 고유값:", dd["합계출산율"].nunique(),
      " 원본 합계출산율 고유값:", orig["합계출산율"].nunique())
print("사본에서 '-'의 개수:", int((dd["합계출산율"] == "-").sum()))
print("사본 합계출산율을 숫자로 되돌린 뒤 평균:",
      round(pd.to_numeric(dd["합계출산율"], errors="coerce").mean(), 4),
      " 값 개수:", int(pd.to_numeric(dd["합계출산율"], errors="coerce").count()))
