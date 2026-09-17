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
print("\n=== 2.3 실험 1: 헐거운 지시에 에이전트가 고르는 갈래 ===")
filled = d2023.copy()
filled["합계출산율"] = filled["합계출산율"].fillna(0)
cols = ["시도", "시군구", "합계출산율"]
print("[(가) 결측을 0으로 채우고 뽑은 하위 5]")
print(filled.nsmallest(5, "합계출산율")[cols].to_string(index=False))
print("[(나)(다) 결측을 제외하고 뽑은 하위 5 (정답)]")
print(d2023.nsmallest(5, "합계출산율")[cols].to_string(index=False))
print("값이 있는 시군구 수:", int(d2023["합계출산율"].count()), "/ 전체 행:", len(d2023))
print("원본:", stats(d2023["합계출산율"]))
print("0 대치:", stats(filled["합계출산율"]))

print("\n[평균 대치가 만들어 내는 값: 1회차 1.2의 평균 대치 위험]")
mean_val = d2023["합계출산율"].mean()
gw = d2023[d2023["시군구"] == "군위군"].iloc[0]
print("전국 평균 합계출산율(228곳):", round(mean_val, 3))
print("군위군: 총인구", int(gw["총인구"]), "/ 고령인구비율", round(gw["고령인구비율"], 1),
      "/ 고령인구비율 전국 순위(높은 순):", int(d2023["고령인구비율"].rank(ascending=False)[gw.name]))
print("평균으로 채운 뒤 표준편차:", round(d2023["합계출산율"].fillna(mean_val).std(), 4),
      "/ 보존했을 때:", round(d2023["합계출산율"].std(), 4))

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

# ------------------------------------------------------------------ 2.2 자료형 규칙의 근거
print("\n=== 2.2 자료형: 실수형으로 읽힌 열을 정수로 바꿔도 합계가 같은가 ===")
print("[자료형 전후] 총인구:", d2023["총인구"].dtype, "->", d2023["총인구"].astype("int64").dtype,
      "/ 출생아수:", d2023["출생아수"].dtype, "->", d2023["출생아수"].astype("Int64").dtype)
print("2023 총인구 합계:", int(d2023["총인구"].sum()), "/ 정수 변환 후 합계:", int(d2023["총인구"].astype("int64").sum()))

print("\n=== 2.6 병합이 2023년 값을 건드리지 않았는가 (원본 vs 병합 파일) ===")
print(pd.DataFrame({"2023 원본": stats(d2023["합계출산율"]),
                    "병합 파일": stats(merged["합계출산율"])}).T.to_string())

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

# ------------------------------------------------------------------ 2.5 시도 단위 정제와 병합
print("\n=== 2.5 grdp_sido.csv 진단 ===")
grdp = pd.read_csv(os.path.join(DATA, "grdp_sido.csv"), encoding="utf-8-sig")
print("행", len(grdp), "/ 열", grdp.shape[1], "/ 첫 열 이름:", repr(grdp.columns[0]))
print("열 이름 전체:", list(grdp.columns))
print("결측 칸:", int(grdp.isna().sum().sum()), "/ 전체 칸:", grdp.size)
na_cells = [(grdp.iloc[r, 0], grdp.columns[c]) for r in range(len(grdp)) for c in range(1, grdp.shape[1])
            if pd.isna(grdp.iloc[r, c])]
print("결측 위치(시도, 연도):", na_cells)
year_cols = [c for c in grdp.columns if c.isdigit()]
print("연도 열:", year_cols[0], "-", year_cols[-1], f"({len(year_cols)}개)")
g23 = grdp[[grdp.columns[0], "2023"]].copy()
print("2023년 최댓값:", g23.loc[g23["2023"].idxmax()].to_dict(),
      "/ 최솟값:", g23.loc[g23["2023"].idxmin()].to_dict())
s_grdp, s_sgg = set(grdp[grdp.columns[0]]), set(d2023["시도"])
print("시도 표기가 그대로 일치하는 것:", len(s_grdp & s_sgg), "건")
print("grdp 표기 17개:", sorted(s_grdp))
print("긴 형으로 바꾸면:", len(grdp) * len(year_cols), "행 3열")

print("\n[틀리는 장면: 앞 두 글자 규칙으로 표기를 맞추면]")
naive = grdp.copy()
naive["시도"] = naive[grdp.columns[0]].str[:2]
dup = naive["시도"].duplicated(keep=False)
print("앞 두 글자 결과 중복 키:", sorted(naive.loc[dup, "시도"].unique()),
      f"({int(dup.sum())}행이 {naive.loc[dup, '시도'].nunique()}개 이름으로)")
print("시군구 파일의 시도와 안 맞는 표기:", sorted(set(naive["시도"]) - s_sgg))
print("짝을 못 찾는 시군구 파일 쪽 시도:", sorted(s_sgg - set(naive["시도"])))

print("\n[대응표를 쓴 본 병합]")
SIDO_MAP = {"강원특별자치도": "강원", "경기도": "경기", "경상남도": "경남", "경상북도": "경북",
            "광주광역시": "광주", "대구광역시": "대구", "대전광역시": "대전", "부산광역시": "부산",
            "서울특별시": "서울", "세종특별자치시": "세종", "울산광역시": "울산", "인천광역시": "인천",
            "전라남도": "전남", "전북특별자치도": "전북", "제주특별자치도": "제주",
            "충청남도": "충남", "충청북도": "충북"}
g23 = g23.rename(columns={grdp.columns[0]: "원래표기", "2023": "1인당지역내총생산"})
g23["시도"] = g23["원래표기"].map(SIDO_MAP)
print("대응표로 바뀐 표기 중 시군구 파일과 안 맞는 것:", sorted(set(g23["시도"]) - s_sgg))
sido_agg = (d2023.groupby("시도")
            .agg(시군구수=("시군구", "size"), 합계출산율평균=("합계출산율", "mean"),
                 출산율값개수=("합계출산율", "count"), 총인구=("총인구", "sum"))
            .reset_index())
sido = sido_agg.merge(g23[["시도", "1인당지역내총생산"]], on="시도", how="left", validate="one_to_one")
print("병합 결과 행 수:", len(sido), "/ GRDP가 안 붙은 시도:", int(sido["1인당지역내총생산"].isna().sum()))
sido["합계출산율평균"] = sido["합계출산율평균"].round(3)
sido["1인당지역내총생산"] = sido["1인당지역내총생산"].astype(int)
print(sido.sort_values("1인당지역내총생산", ascending=False).to_string(index=False))
print("출산율 평균이 229곳이 아닌 228곳으로 계산된 시도:",
      sido.loc[sido["시군구수"] != sido["출산율값개수"], ["시도", "시군구수", "출산율값개수"]].to_dict("records"))
print("시군구 수 합계:", int(sido["시군구수"].sum()), "/ 총인구 합계:", int(sido["총인구"].sum()))

# ------------------------------------------------------------------ 2.9 데이터 사전
print("\n=== 2.9 최종 산출물의 열 목록 ===")
final = pd.read_csv(os.path.join(DATA, "sigungu_tfr_2013_2023.csv"), encoding="utf-8-sig")
print("행", len(final), "열", final.shape[1])
info = pd.DataFrame({"자료형": final.dtypes.astype(str),
                     "결측": final.isna().sum(),
                     "최소": final.min(numeric_only=False),
                     "최대": final.max(numeric_only=False)})
print(info.to_string())
