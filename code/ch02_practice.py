# -*- coding: utf-8 -*-
"""2주차 2회차 실습 장(02-2)에 쓰는 수치를 data/sigungu_2023.csv에서 직접 계산한다.

실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python code/ch02_practice.py
"파일 줄 번호"는 VSCode에서 CSV를 열었을 때의 줄 번호다 (열 이름 줄이 1번째 줄, 첫 데이터가 2번째 줄).
"""
import io
import os

import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(root, "data", "sigungu_2023.csv")

df = pd.read_csv(path, encoding="utf-8-sig")
df["파일줄번호"] = df.index + 2

with io.open(path, encoding="utf-8-sig") as f:
    raw_lines = f.read().splitlines()

print("=== 파일 구조 ===")
print("데이터 행 수:", len(df), " 열 수:", df.shape[1] - 1)
print("파일의 전체 줄 수(열 이름 줄 포함):", len(raw_lines))
print("열 이름:", list(df.columns[:-1]))
print("시도 수:", df["시도"].nunique())
print(df["시도"].value_counts().to_string())

print("\n=== 2.1 총인구 상위 3 / 하위 3 ===")
cols = ["시도", "시군구", "총인구", "파일줄번호"]
print(df.nlargest(3, "총인구")[cols].to_string(index=False))
print(df.nsmallest(3, "총인구")[cols].to_string(index=False))
print("총인구 합계:", int(df["총인구"].sum()))

print("\n=== 2.2 의성군 ===")
cols = ["시도", "시군구", "총인구", "고령인구비율", "합계출산율", "파일줄번호"]
print(df[df["시군구"] == "의성군"][cols].to_string(index=False))
print("의성군 pandas 인덱스(0부터):", int(df.index[df["시군구"] == "의성군"][0]))

print("\n=== 결측 ===")
print(df[df["합계출산율"].isna()][["시도", "시군구", "합계출산율", "출생아수", "파일줄번호"]].to_string(index=False))
print("합계출산율 값 개수:", int(df["합계출산율"].count()))

print("\n=== 2.4 합계출산율 상위 5 / 하위 5 ===")
cols = ["시도", "시군구", "합계출산율", "파일줄번호"]
print(df.nlargest(5, "합계출산율")[cols].to_string(index=False))
print(df.nsmallest(5, "합계출산율")[cols].to_string(index=False))
print("단순평균(228개):", round(df["합계출산율"].mean(), 3), " 중앙값:", round(df["합계출산율"].median(), 3))
w = df.dropna(subset=["합계출산율"])
print("총인구 가중평균:", round((w["합계출산율"] * w["총인구"]).sum() / w["총인구"].sum(), 3))

print("\n=== 2.5 강원 ===")
g = df[df["시도"] == "강원"].sort_values("총인구", ascending=False)
print("강원 시군구 수:", len(g))
print(g[["시군구", "총인구", "고령인구비율", "합계출산율", "파일줄번호"]].to_string(index=False))
print("강원 고령인구비율 최고:", g.loc[g["고령인구비율"].idxmax(), ["시군구", "고령인구비율"]].to_dict())
print("강원 고령인구비율 최저:", g.loc[g["고령인구비율"].idxmin(), ["시군구", "고령인구비율"]].to_dict())
print("강원 합계출산율 최고:", g.loc[g["합계출산율"].idxmax(), ["시군구", "합계출산율"]].to_dict())
print("강원 합계출산율 최저:", g.loc[g["합계출산율"].idxmin(), ["시군구", "합계출산율"]].to_dict())
print("강원 총인구 합계:", int(g["총인구"].sum()))

print("\n=== 2.6 고령인구비율 상위 5 / 하위 5 ===")
cols = ["시도", "시군구", "고령인구비율", "파일줄번호"]
print(df.nlargest(5, "고령인구비율")[cols].to_string(index=False))
print(df.nsmallest(5, "고령인구비율")[cols].to_string(index=False))
print("고령인구비율 평균:", round(df["고령인구비율"].mean(), 2), " 중앙값:", round(df["고령인구비율"].median(), 2))

# ---------------------------------------------------------------
# 확장분 (2026-09-03): 2.2 다섯 손잡이, 2.3 세 번 반복, 2.4 시도별 시군구 수,
# 2.6 맥락창 실습, 2.7 CLAUDE.md 전후, 2.8 오류 심기 실험에 쓰는 값
# ---------------------------------------------------------------
pd.set_option("display.max_rows", 300)

print()
print("=== 2.2 다섯 손잡이 실험: 성공 기준과 이상 상황 ===")
print("전체 행 수:", len(df))
print("합계출산율 값 있는 행:", int(df["합계출산율"].count()))
print("출생아수 값 있는 행:", int(df["출생아수"].count()))
print("결측 행:")
print(df[df["합계출산율"].isna()][["시도", "시군구", "총인구", "합계출산율", "출생아수", "파일줄번호"]].to_string(index=False))
print("총인구 합계(229곳):", int(df["총인구"].sum()))
print("출생아수 합계(228곳):", int(df["출생아수"].sum()))
print("고령인구비율 평균(229곳):", round(df["고령인구비율"].mean(), 2))
print("고령인구비율 중앙값:", round(df["고령인구비율"].median(), 2))

print("\n=== 2.3 세 번 반복 실험에 쓰는 고정값 ===")
for name in ["수원시", "울릉군", "의성군", "영광군", "중구"]:
    sub = df[df["시군구"] == name][["시도", "시군구", "총인구", "고령인구비율", "합계출산율", "파일줄번호"]]
    print(sub.to_string(index=False))

print("\n=== 2.4 세 번째 과제: 시도별 시군구 수 ===")
vc = df["시도"].value_counts().sort_values(ascending=False)
print("시도 수:", df["시도"].nunique())
print(vc.to_string())
print("합계:", int(vc.sum()))
print("\n시도별 첫 줄·마지막 줄 번호:")
g = df.groupby("시도")["파일줄번호"].agg(["min", "max", "count"])
print(g.to_string())
print("\n세종 행:")
print(df[df["시도"] == "세종"][["시도", "시군구", "총인구", "고령인구비율", "합계출산율", "파일줄번호"]].to_string(index=False))

print("\n=== 2.6 맥락창 실습: 인구밀도 ===")
cols = ["시도", "시군구", "인구밀도", "총인구", "면적", "파일줄번호"]
print(df.nlargest(3, "인구밀도")[cols].to_string(index=False))
print(df.nsmallest(3, "인구밀도")[cols].to_string(index=False))
print("인구밀도 중앙값:", round(df["인구밀도"].median(), 1))

print("\n=== 2.6 맥락창 실습: 인구증가율 ===")
cols = ["시도", "시군구", "인구증가율", "총인구", "파일줄번호"]
print(df.nlargest(3, "인구증가율")[cols].to_string(index=False))
print(df.nsmallest(3, "인구증가율")[cols].to_string(index=False))

print("\n=== 2.8 오류 심기 실험: 합계출산율 상위 5 / 하위 5 (재확인) ===")
cols = ["시도", "시군구", "합계출산율", "파일줄번호"]
top5 = df.nlargest(5, "합계출산율")[cols]
bot5 = df.nsmallest(5, "합계출산율")[cols]
print(top5.to_string(index=False))
print(bot5.to_string(index=False))
print("상위 6위(행 빼기 실험에서 밀려 올라오는 곳):")
print(df.nlargest(6, "합계출산율")[cols].tail(1).to_string(index=False))
print("하위 6위:")
print(df.nsmallest(6, "합계출산율")[cols].tail(1).to_string(index=False))

print("\n=== 2.7 CLAUDE.md 규칙 전후 비교에 쓰는 값 ===")
print("합계출산율 단순평균(228곳):", round(df["합계출산율"].mean(), 3))
print("합계출산율 중앙값(228곳):", round(df["합계출산율"].median(), 3))
w = df.dropna(subset=["합계출산율"])
print("총인구 가중평균:", round((w["합계출산율"] * w["총인구"]).sum() / w["총인구"].sum(), 3))
print("출생아수 합 / (해당 시군구 총인구 합) 참고용 확인:", int(w["출생아수"].sum()), int(w["총인구"].sum()))

print("\n=== 강원 재확인 (2.5) ===")
gw = df[df["시도"] == "강원"].sort_values("총인구", ascending=False)
print(gw[["시군구", "총인구", "고령인구비율", "합계출산율", "파일줄번호"]].to_string(index=False))
gun = gw[gw["시군구"].str.endswith("군")]
print("강원 군 지역 수:", len(gun), " 고령인구비율 30% 미만:", len(gun[gun["고령인구비율"] < 30]))
print(gun[gun["고령인구비율"] < 30][["시군구", "고령인구비율", "파일줄번호"]].to_string(index=False))
