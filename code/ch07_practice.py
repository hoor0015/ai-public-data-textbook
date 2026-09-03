# -*- coding: utf-8 -*-
"""7주차 2회차 실습 장(07-2)에 쓰는 수치를 data/의 원자료에서 직접 계산한다.

실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "code/ch07_practice.py"
"파일 줄 번호"는 VSCode에서 CSV를 열었을 때의 줄 번호다 (열 이름 줄이 1번째 줄, 첫 데이터가 2번째 줄).
절 번호는 07-2 장의 단계 번호를 따른다.
"""
import os

import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_rows", 300)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(root, "data")
d2023 = pd.read_csv(os.path.join(DATA, "sigungu_2023.csv"), encoding="utf-8-sig")
d2013 = pd.read_csv(os.path.join(DATA, "sigungu_tfr_2013.csv"), encoding="utf-8-sig")
d2023["파일줄번호"] = d2023.index + 2
d2013["파일줄번호"] = d2013.index + 2
KEY = ["시도", "시군구"]


def stats(s):
    s = pd.Series(s)
    return {"n": int(s.count()), "평균": round(s.mean(), 3), "중앙값": round(s.median(), 3),
            "표준편차": round(s.std(), 3), "최소": round(s.min(), 3), "최대": round(s.max(), 3)}


# ------------------------------------------------------------------ 2.1 진단
print("=== 2.1 구조 ===")
print("2023:", d2023.shape[0], "행", d2023.shape[1] - 1, "열 /", "2013:", d2013.shape[0], "행", d2013.shape[1] - 1, "열")
print("\n[2023 열별 자료형]")
print(d2023.drop(columns="파일줄번호").dtypes.to_string())
print("\n[2013 열별 자료형]")
print(d2013.drop(columns="파일줄번호").dtypes.to_string())
print("\n[값은 모두 정수인데 실수(float64)로 저장된 열]")
for c in d2023.select_dtypes("number").columns:
    if c == "파일줄번호":
        continue
    v = d2023[c].dropna()
    if (v == v.round()).all() and d2023[c].dtype == "float64":
        print(" ", c, "예:", v.iloc[0])
print("\n[2023 결측 위치]")
na_rows = d2023[d2023.isna().any(axis=1)]
print(na_rows[["시도", "시군구", "합계출산율", "출생아수", "파일줄번호"]].to_string(index=False))
print("pandas 인덱스(0부터):", list(na_rows.index))
print("2013 결측 합계:", int(d2013.drop(columns="파일줄번호").isna().sum().sum()))
print("\n[시도 표기 집합 비교]")
s23, s13 = set(d2023["시도"]), set(d2013["시도"])
print("2023 시도 수:", len(s23), "/ 2013 시도 수:", len(s13), "/ 차이:", s23 ^ s13)
print("\n[앞뒤 공백·중복 키 검사]")
for name, df in (("2023", d2023), ("2013", d2013)):
    ws = sum(int((df[c] != df[c].str.strip()).sum()) for c in KEY)
    dup = df.duplicated(KEY, keep=False).sum()
    print(f"  {name}: 공백 이상 {ws}건, (시도,시군구) 중복 {dup}건")
print("[2013 세종 행]")
print(d2013[d2013["시도"] == "세종"].to_string(index=False))
print("\n[2023 숫자 열 최소·최대]")
desc = d2023.drop(columns="파일줄번호").describe().T[["min", "max"]]
print(desc.to_string())

# ------------------------------------------------------------------ 2.3 결측 실험과 이상치
print("\n=== 2.3 실험: 결측을 0으로 채웠을 때 ===")
filled = d2023.copy()
filled["합계출산율"] = filled["합계출산율"].fillna(0)
cols = ["시도", "시군구", "합계출산율"]
print("[0 대치 기준 하위 5]")
print(filled.nsmallest(5, "합계출산율")[cols].to_string(index=False))
print("[원본 기준 하위 5]")
print(d2023.nsmallest(5, "합계출산율")[cols].to_string(index=False))
print("원본:", stats(d2023["합계출산율"]))
print("0 대치:", stats(filled["합계출산율"]))

print("\n=== 2.3 이상치: 박스플롯(IQR 1.5배) 규칙 ===")
outlier_idx = set()
for col in ("합계출산율", "인구증가율"):
    s = d2023[col]
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (s < lo) | (s > hi)
    outlier_idx |= set(d2023.index[mask])
    print(f"[{col}] Q1={q1:.3f} Q3={q3:.3f} 수염 하한={lo:.3f} 상한={hi:.3f} 이상치 {int(mask.sum())}곳 (전국 평균 {s.mean():.3f})")
    out = d2023.loc[mask, ["시도", "시군구", col, "파일줄번호"]].copy()
    out["평균과의 차이"] = (out[col] - s.mean()).round(3)
    print(out.sort_values(col, ascending=False).to_string(index=False))

print("\n=== 2.3 틀리는 장면: 이상치 행을 삭제했을 때 ===")
kept = d2023.drop(index=sorted(outlier_idx))
print("삭제된 행:", len(outlier_idx), "/ 남은 행:", len(kept))
print("삭제된 시군구:", ", ".join(f"{r.시도} {r.시군구}" for r in d2023.loc[sorted(outlier_idx)].itertuples()))
print("삭제 후 합계출산율:", stats(kept["합계출산율"]))
print("삭제 후 인구증가율:", stats(kept["인구증가율"]), "/ 원본:", stats(d2023["인구증가율"]))

# ------------------------------------------------------------------ 2.4 병합
print("\n=== 2.4 진단 병합 (outer, indicator) ===")
diag = d2023.drop(columns="파일줄번호").merge(d2013, on=KEY, how="outer", indicator=True)
print("outer 병합 행 수:", len(diag))
print(diag["_merge"].value_counts().to_string())
print("[2023년에만 있는 행 (left_only)]")
print(diag.loc[diag["_merge"] == "left_only", KEY].to_string(index=False))
ro = diag.loc[diag["_merge"] == "right_only", KEY + ["합계출산율_2013", "파일줄번호"]].copy()
ro["파일줄번호"] = ro["파일줄번호"].astype(int)
# 2013 파일은 일반구를 "장안구"처럼 시 이름 없이 수록한다. 일반구가 아닌 3건(인천 남구, 세종 세종시, 충북 청원군)을
# 제외한 나머지가 일반구다.
not_gu = ((ro["시도"] == "인천") & (ro["시군구"] == "남구")) | (ro["시군구"].isin(["세종시", "청원군"]))
is_gu = ~not_gu
print(f"[2013년에만 있는 행 (right_only) {len(ro)}건: 일반구 {int(is_gu.sum())}건 + 그 외 {int((~is_gu).sum())}건]")
print(ro[~is_gu].to_string(index=False))
print("[일반구 33건의 시도별 수]")
print(ro[is_gu]["시도"].value_counts().sort_index().to_string())
print("[일반구 전체 목록 (파일 표기 그대로)]")
print(", ".join(f"{r.시도} {r.시군구}" for r in ro[is_gu].itertuples()))

print("\n=== 2.4 본 병합: 이름 대응표 적용 전후 ===")
before = d2023.drop(columns="파일줄번호").merge(d2013.drop(columns="파일줄번호"), on=KEY, how="left", validate="one_to_one")
d2013_fix = d2013.drop(columns="파일줄번호").copy()
mask = (d2013_fix["시도"] == "인천") & (d2013_fix["시군구"] == "남구")
print("2013 인천 남구 행:", d2013.loc[mask.values, ["시도", "시군구", "합계출산율_2013", "파일줄번호"]].to_dict("records"))
d2013_fix.loc[mask, "시군구"] = "미추홀구"
merged = d2023.drop(columns="파일줄번호").merge(d2013_fix, on=KEY, how="left", validate="one_to_one")
print("대응표 적용 전: 행", len(before), "/ 2013 값 없는 곳", int(before["합계출산율_2013"].isna().sum()),
      before.loc[before["합계출산율_2013"].isna(), KEY].values.tolist())
print("대응표 적용 후: 행", len(merged), "/ 2013 값 없는 곳", int(merged["합계출산율_2013"].isna().sum()))
print("시군구 이름만 키로 잡았을 때 행 수 (이름 수정 전 2013 파일, left):",
      len(d2023.drop(columns="파일줄번호").merge(d2013.drop(columns="파일줄번호"), on="시군구", how="left")),
      "/ (수정 후, left):", len(d2023.drop(columns="파일줄번호").merge(d2013_fix, on="시군구", how="left")))
saved = pd.read_csv(os.path.join(DATA, "sigungu_tfr_2013_2023.csv"), encoding="utf-8-sig")
print("저장된 병합 파일과 동일:", saved.shape == merged.shape and
      np.allclose(saved["합계출산율_2013"], merged["합계출산율_2013"], equal_nan=True))

# ------------------------------------------------------------------ 2.5 정제 전후 비교
print("\n=== 2.5 합계출산율(2023) 요약통계: 경로별 ===")
paths = {"원본(결측 보존)": d2023["합계출산율"], "결측 0 대치": filled["합계출산율"],
         "이상치 삭제": kept["합계출산율"], "최종 정제(병합 후)": merged["합계출산율"]}
print(pd.DataFrame({k: stats(v) for k, v in paths.items()}).T.to_string())
print("\n[합계출산율_2013: 병합 전(264행) vs 병합 후(229행)]")
print(pd.DataFrame({"2013 원본(264행)": stats(d2013["합계출산율_2013"]),
                    "병합 후(229행)": stats(merged["합계출산율_2013"]),
                    "제외된 일반구 33행": stats(ro[is_gu]["합계출산율_2013"])}).T.to_string())
print("\n[자료형 전후] 총인구:", d2023["총인구"].dtype, "->", d2023["총인구"].astype("int64").dtype,
      "/ 출생아수:", d2023["출생아수"].dtype, "->", d2023["출생아수"].astype("Int64").dtype)
print("2023 총인구 합계:", int(d2023["총인구"].sum()), "/ 정수 변환 후 합계:", int(d2023["총인구"].astype("int64").sum()))

# ------------------------------------------------------------------ 2.6 표본 대조
print("\n=== 2.6 표본 대조 ===")
samples = [("서울", "종로구"), ("인천", "미추홀구"), ("강원", "고성군"), ("경남", "고성군")]
for sido, sgg in samples:
    r = merged[(merged["시도"] == sido) & (merged["시군구"] == sgg)].iloc[0]
    o23 = d2023[(d2023["시도"] == sido) & (d2023["시군구"] == sgg)].iloc[0]
    name13 = "남구" if sgg == "미추홀구" else sgg
    o13 = d2013[(d2013["시도"] == sido) & (d2013["시군구"] == name13)].iloc[0]
    print(f"  {sido} {sgg}: 병합 2013={r['합계출산율_2013']} 2023={r['합계출산율']} | "
          f"원본 2013={o13['합계출산율_2013']}(줄 {o13['파일줄번호']}) 원본 2023={o23['합계출산율']}(줄 {o23['파일줄번호']})")

# ------------------------------------------------------------------ 2.7 독립 검산용 수치
print("\n=== 2.7 2013 대비 2023 변화 ===")
merged["변화"] = merged["합계출산율"] - merged["합계출산율_2013"]
print("오른 곳:", int((merged["변화"] > 0).sum()), "/ 내린 곳:", int((merged["변화"] < 0).sum()),
      "/ 같은 곳:", int((merged["변화"] == 0).sum()), "/ 비교 불가:", int(merged["변화"].isna().sum()))
cols = ["시도", "시군구", "합계출산율_2013", "합계출산율", "변화"]
print("[변화 상위 5]")
print(merged.nlargest(5, "변화")[cols].round(3).to_string(index=False))
print("[변화 하위 5 (가장 많이 내린 곳)]")
print(merged.nsmallest(5, "변화")[cols].round(3).to_string(index=False))
print("2013 평균(229곳):", round(merged["합계출산율_2013"].mean(), 3),
      "/ 2023 평균(228곳):", round(merged["합계출산율"].mean(), 3),
      "/ 변화 평균(228곳):", round(merged["변화"].mean(), 3),
      "/ 변화 중앙값:", round(merged["변화"].median(), 3))
print("[청주시]")
print(merged[merged["시군구"] == "청주시"][cols].round(3).to_string(index=False))
print("[군위군]")
print(merged[merged["시군구"] == "군위군"][cols].to_string(index=False))
print("2013 값이 2023 값보다 높은 곳 중 하락폭 0.5 이상:", int((merged["변화"] <= -0.5).sum()))

# ------------------------------------------------------------------ 2.3 이상치: 두 기준 비교
print("\n=== 2.3 이상치 기준 비교: 분포 기준(박스플롯) vs 절대 기준(분석자가 정한 상식 범위) ===")
ABS_RULE = {"합계출산율": (0.5, 1.3), "인구증가율": (-3.0, 5.0)}
dist_sets, abs_sets = {}, {}
for col, (lo_a, hi_a) in ABS_RULE.items():
    s = d2023[col]
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo_d, hi_d = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    dm, am = (s < lo_d) | (s > hi_d), (s < lo_a) | (s > hi_a)
    dist_sets[col], abs_sets[col] = set(d2023.index[dm]), set(d2023.index[am])
    print(f"[{col}] 분포 기준({lo_d:.3f} 미만 / {hi_d:.3f} 초과): {int(dm.sum())}곳"
          f" | 절대 기준({lo_a} 미만 / {hi_a} 초과): {int(am.sum())}곳"
          f" | 두 기준 모두: {len(dist_sets[col] & abs_sets[col])}곳")
    for label, idx in (("  분포 기준에만", dist_sets[col] - abs_sets[col]),
                       ("  절대 기준에만", abs_sets[col] - dist_sets[col])):
        sub = d2023.loc[sorted(idx), ["시도", "시군구", col]].sort_values(col, ascending=False)
        print(f"{label} 걸린 {len(idx)}곳:",
              ", ".join(f"{a} {b} {c}" for a, b, c in sub.itertuples(index=False, name=None)))
dist_all = dist_sets["합계출산율"] | dist_sets["인구증가율"]
abs_all = abs_sets["합계출산율"] | abs_sets["인구증가율"]
print("두 열 합집합: 분포 기준", len(dist_all), "곳 / 절대 기준", len(abs_all), "곳 / 겹치는 곳",
      len(dist_all & abs_all), "곳 / 어느 한쪽에라도 걸린 곳", len(dist_all | abs_all), "곳")

# ------------------------------------------------------------------ 2.5 결측 처리 세(네) 방식
print("\n=== 2.5 결측 처리 방식별 비교 (합계출산율 2023) ===")
mean_val = d2023["합계출산율"].mean()
by_mean = d2023["합계출산율"].fillna(mean_val)
dropped = d2023.dropna(subset=["합계출산율"])
ways = {"① 표시만 (보존)": d2023["합계출산율"], "② 행 제외 (dropna)": dropped["합계출산율"],
        "③ 평균 대치": by_mean, "④ 0 대치": filled["합계출산율"]}
print(pd.DataFrame({k: stats(v) for k, v in ways.items()}).T.to_string())
print("대치에 쓴 평균값:", round(mean_val, 3))
gw = d2023[d2023["시군구"] == "군위군"].iloc[0]
print("군위군: 총인구", int(gw["총인구"]), "/ 고령인구비율", round(gw["고령인구비율"], 1),
      "/ 고령인구비율 전국 순위(높은 순):", int(d2023["고령인구비율"].rank(ascending=False)[gw.name]))
rank_zero = int((filled["합계출산율"] < 0).sum() + 1)
rank_mean = int((by_mean < mean_val).sum() + 1)
print("군위군의 합계출산율 순위(낮은 순, 229곳 기준): 0 대치", rank_zero, "위 / 평균 대치", rank_mean, "위")
print("전국 총인구 합계: 보존", int(d2023["총인구"].sum()), "/ 행 제외", int(dropped["총인구"].sum()),
      "/ 차이", int(d2023["총인구"].sum() - dropped["총인구"].sum()))
print("행 제외 시 행 수:", len(dropped), "/ 사라지는 시군구:", gw["시도"], gw["시군구"])

# ------------------------------------------------------------------ 2.9 오류 심기 ①: 천 단위 쉼표
print("\n=== 2.9 실험 3: 총인구에 천 단위 쉼표를 넣은 사본 ===")
comma = d2023.drop(columns="파일줄번호").copy()
comma["총인구"] = comma["총인구"].map(lambda v: f"{int(v):,}")
print("사본의 총인구 자료형:", comma["총인구"].dtype, "/ 첫 값:", repr(comma["총인구"].iloc[0]))
try:
    print("평균 계산:", comma["총인구"].mean())
except Exception as e:
    print("평균 계산 오류:", type(e).__name__, "-", str(e)[:90])
concat = comma["총인구"].sum()
print("sum()의 결과 길이:", len(concat), "글자 / 앞 40글자:", concat[:40])
print("[문자로 정렬한 인구 상위 5]")
print(comma.sort_values("총인구", ascending=False).head(5)[["시도", "시군구", "총인구"]].to_string(index=False))
print("[숫자로 정렬한 인구 상위 5 (정답)]")
print(d2023.nlargest(5, "총인구")[["시도", "시군구", "총인구"]].assign(
    총인구=lambda x: x["총인구"].map(lambda v: f"{int(v):,}")).to_string(index=False))
fixed = comma["총인구"].str.replace(",", "", regex=False).astype("int64")
print("쉼표 제거 후 자료형:", fixed.dtype, "/ 합계:", int(fixed.sum()),
      "/ 원본 합계와 같은가:", int(fixed.sum()) == int(d2023["총인구"].sum()))

# ------------------------------------------------------------------ 2.9 오류 심기 ②: 병합 키의 공백
print("\n=== 2.9 실험 4: 병합 키에 공백 한 칸이 붙은 사본 ===")
space = d2013_fix.copy()                      # 미추홀구 이름은 이미 맞춰 둔 상태
gg = space["시도"] == "경기"
space.loc[gg, "시군구"] = space.loc[gg, "시군구"] + " "
print("공백이 붙은 2013 파일 행 수:", int(gg.sum()), "(모두 시도가 경기)")
print("눈으로 보이는 표기:", [repr(v) for v in space.loc[gg, "시군구"].head(3)])
bad = d2023.drop(columns="파일줄번호").merge(space, on=KEY, how="left", validate="one_to_one")
print("병합 결과 행 수:", len(bad), "(기준 데이터와 같으므로 행 수 검증은 통과한다)")
print("합계출산율_2013이 비어 있는 곳:", int(bad["합계출산율_2013"].isna().sum()), "곳")
print("비어 있는 곳의 시도 분포:")
print(bad.loc[bad["합계출산율_2013"].isna(), "시도"].value_counts().to_string())
print("2023 파일의 경기 시군구 수:", int((d2023["시도"] == "경기").sum()))
print("진단 지시로 잡는 법 - 키 열의 앞뒤 공백 검사:",
      int((space["시군구"] != space["시군구"].str.strip()).sum()), "건")
space_fixed = space.copy()
for c in KEY:
    space_fixed[c] = space_fixed[c].str.strip()
good = d2023.drop(columns="파일줄번호").merge(space_fixed, on=KEY, how="left", validate="one_to_one")
print("공백 제거 후 다시 병합 - 행:", len(good), "/ 값이 비어 있는 곳:",
      int(good["합계출산율_2013"].isna().sum()), "곳")

# ------------------------------------------------------------------ 2.10 데이터 사전
print("\n=== 2.10 최종 산출물의 열 목록 ===")
final = pd.read_csv(os.path.join(DATA, "sigungu_tfr_2013_2023.csv"), encoding="utf-8-sig")
print("행", len(final), "열", final.shape[1])
info = pd.DataFrame({"자료형": final.dtypes.astype(str),
                     "결측": final.isna().sum(),
                     "최소": final.min(numeric_only=False),
                     "최대": final.max(numeric_only=False)})
print(info.to_string())
