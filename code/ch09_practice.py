# 9주차 본문 수치 계산 (공통 데이터 data/sigungu_mcp_2023.csv, data/sigungu_mcp_tfr_2013.csv)
# [0] 2.1-2.2 수집·결합 점검, [T] 1차시 본문 수치, [1]-[9] 2차시 2.3 이후 본문 수치
# (대괄호 번호 뒤의 절 번호는 9주차 2차시 본문 기준)
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 code/ch09_practice.py
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw_mcp"
df = pd.read_csv(BASE / "data" / "sigungu_mcp_2023.csv", encoding="utf-8-sig")
t13 = pd.read_csv(BASE / "data" / "sigungu_mcp_tfr_2013.csv", encoding="utf-8-sig")
inc = pd.read_csv(BASE / "data" / "income_dist.csv", encoding="utf-8-sig")


def name(i, d=df):
    return f"{d.loc[i, '시도']} {d.loc[i, '시군구']}"


def head(title):
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)


head("[0] 2.1-2.2 수집 응답과 결합 결과")
for f in sorted(RAW.glob("mcp_*.csv")):
    d = pd.read_csv(f, encoding="utf-8-sig", dtype=str)
    print(f"{f.name}: {len(d)}행, 열 {list(d.columns)}")
print(f"결합 결과: {df.shape[0]}행 x {df.shape[1]}열, 열 = {list(df.columns)}")
na = df.isna().sum()
print("결측:", {c: int(v) for c, v in na.items() if v > 0},
      df.loc[df["인구증가율"].isna(), ["시도", "시군구"]].values.tolist())
print("시도별 시군구 수:", df["시도"].value_counts().to_dict())
dup = df["시군구"].value_counts()
print("이름이 둘 이상인 시군구:", dup[dup > 1].to_dict())
pop = pd.read_csv(RAW / "mcp_주민등록인구_DT_1YL20651E_2023.csv", encoding="utf-8-sig", dtype=str)
print(f"주민등록인구 응답의 '계' 행 {int((pop['항목'] == '계').sum())}개 = 전국 1 + 시도 17 + 시군구 228"
      f" (세종은 시도 행 하나)")
tfr = pd.read_csv(RAW / "mcp_합계출산율_DT_1B81A23_2023.csv", encoding="utf-8-sig", dtype=str)
print(f"합계출산율 응답 지역 {tfr['분류1'].nunique()}개")
area = pd.read_csv(RAW / "mcp_면적_DT_MLTM_2300_2023.csv", encoding="utf-8-sig", dtype=str)
print(f"면적 응답 '(계)'로 끝나는 행: {area['분류2'].str.endswith('(계)').sum()}개")
for sgg in ["세종특별자치시", "군위군", "청주시", "창원시", "제주시"]:
    print(df[df["시군구"] == sgg][["시도", "시군구", "총인구", "면적", "인구증가율", "합계출산율"]]
          .to_string(index=False, header=False))
print("이름이 같은 구:", df[df["시군구"].isin(["중구", "동구"])][["시도", "시군구", "총인구"]]
      .values.tolist())

head("[T] 1차시 본문 수치")
a = df["고령인구비율"]
print(f"고령인구비율 평균 {a.mean():.2f}, 중앙값 {a.median():.2f}, 최소 {a.min()} ({name(a.idxmin())}), "
      f"최대 {a.max()} ({name(a.idxmax())})")
bins = np.arange(7.5, 47.6, 2.5)
cnt, edges = np.histogram(a, bins=bins)
k = cnt.argmax()
print(f"구간 폭 2.5 최빈 구간 {edges[k]:.1f}-{edges[k+1]:.1f} ({cnt[k]}곳), 높이 합 {cnt.sum()}")
print(f"고령인구비율 20% 초과 {int((a > 20).sum())}곳 ({(a > 20).mean() * 100:.1f}%)")
r = df["고령인구비율"].corr(df["합계출산율"])
print(f"고령인구비율-합계출산율 r = {r:.3f} (n = {len(df)})")
ld = np.log10(df["인구밀도"])
print(f"인구밀도-고령인구비율 r = {df['인구밀도'].corr(a):.3f}, 로그 인구밀도-고령인구비율 r = {ld.corr(a):.3f}")
dn = df["인구밀도"]
print(f"인구밀도 최소 {dn.min():.1f} ({name(dn.idxmin())}), 최대 {dn.max():.1f} ({name(dn.idxmax())}), "
      f"배수 {dn.max() / dn.min():.0f}, 중앙값 {dn.median():.1f}, 평균 {dn.mean():.1f}, "
      f"100 미만 {int((dn < 100).sum())}, 100-1000 {int(((dn >= 100) & (dn < 1000)).sum())}, "
      f"1000 미만 계 {int((dn < 1000).sum())}")
for sgg in [("부산", "중구"), ("전남", "영광군"), ("경북", "의성군"), ("울산", "북구")]:
    row = df[(df["시도"] == sgg[0]) & (df["시군구"] == sgg[1])].iloc[0]
    print(f"{sgg}: 고령 {row['고령인구비율']}, 합계출산율 {row['합계출산율']}")
i_lo, i_hi = df["합계출산율"].idxmin(), df["합계출산율"].idxmax()
print(f"합계출산율 최저 {name(i_lo)} {df.loc[i_lo, '합계출산율']} (고령 {df.loc[i_lo, '고령인구비율']}), "
      f"최고 {name(i_hi)} {df.loc[i_hi, '합계출산율']} (고령 {df.loc[i_hi, '고령인구비율']})")
seoul_max = df.loc[df["시도"] == "서울", "합계출산율"].max()
print(f"서울 자치구 합계출산율 최댓값 {seoul_max}")
print(f"지니계수 {inc['연도'].iloc[0]} {inc['지니계수'].iloc[0]:.3f} -> "
      f"{inc['연도'].iloc[-1]} {inc['지니계수'].iloc[-1]:.3f}")

head("[1] 2.3 히스토그램·박스플롯·산점도")
print(f"시군구 {len(df)}, 고령인구비율 평균 {a.mean():.2f}, 중앙값 {a.median():.2f}")
tab = (df.groupby("시도")["고령인구비율"]
         .agg(시군구수="count", 중앙값="median", 최소="min", 최대="max",
              Q1=lambda s: s.quantile(.25), Q3=lambda s: s.quantile(.75))
         .sort_values("중앙값"))
tab["IQR"] = tab["Q3"] - tab["Q1"]
print(tab.round(2).to_string())
print(f"시군구 수 합계 {tab['시군구수'].sum()}")
for sido in ["경기", "인천", "경남"]:
    s = df[df["시도"] == sido]
    q1, q3 = s["고령인구비율"].quantile([.25, .75])
    hi = q3 + 1.5 * (q3 - q1)
    out = s[s["고령인구비율"] > hi]
    print(f"{sido} 위쪽 이상치(1.5 IQR) {len(out)}곳: "
          + ", ".join(f"{x.시군구}({x.고령인구비율})" for x in out.itertuples())
          + f" / 최소 {s.loc[s['고령인구비율'].idxmin(), '시군구']}({s['고령인구비율'].min()})"
          + f" 최대 {s.loc[s['고령인구비율'].idxmax(), '시군구']}({s['고령인구비율'].max()})")

head("[2] 2.4 합계출산율·인구증가율 분포")
for col, w in [("합계출산율", 0.05), ("인구증가율", 0.5)]:
    s = df[col].dropna()
    q1, med, q3 = s.quantile([0.25, 0.5, 0.75])
    print(f"{col}: n {len(s)}, 결측 {int(df[col].isna().sum())}, 최소 {s.min():.3f} ({name(s.idxmin())}), "
          f"Q1 {q1:.3f}, 중앙값 {med:.3f}, Q3 {q3:.3f}, 최대 {s.max():.3f} ({name(s.idxmax())}), 평균 {s.mean():.3f}")
    lo, hi = np.floor(s.min() / w) * w, np.ceil(s.max() / w) * w
    e = np.arange(lo, hi + w / 2, w)
    c, _ = np.histogram(s, bins=e)
    k = int(c.argmax())
    print(f"   폭 {w:g}: 막대 {len(c)}개, 최빈 {e[k]:.2f}-{e[k+1]:.2f} ({c[k]}곳), 합 {c.sum()}")
    print("   상위 3:", ", ".join(f"{name(i)} {s[i]}" for i in s.nlargest(3).index))
t = df["합계출산율"]
print(f"합계출산율 1.0 이상 {int((t >= 1.0).sum())}곳")
g = df["인구증가율"].dropna()
print(f"인구증가율 양수 {int((g > 0).sum())}, 음수 {int((g < 0).sum())}, 0 {int((g == 0).sum())}")

head("[3] 2.5 수도권 vs 비수도권")
for col in ["고령인구비율", "합계출산율"]:
    for gname in ["수도권", "비수도권"]:
        s = df.loc[df["수도권"] == gname, col].dropna()
        q1, med, q3 = s.quantile([.25, .5, .75])
        print(f"{col} {gname}: n {len(s)}, 최소 {s.min():.3f} ({name(s.idxmin())}), Q1 {q1:.3f}, "
              f"중앙값 {med:.3f}, Q3 {q3:.3f}, 최대 {s.max():.3f} ({name(s.idxmax())}), 평균 {s.mean():.3f}")
med_non = df.loc[df["수도권"] == "비수도권", "고령인구비율"].median()
over = df[(df["수도권"] == "수도권") & (df["고령인구비율"] > med_non)]
print(f"비수도권 고령 중앙값({med_non})보다 높은 수도권 {len(over)}곳: "
      + ", ".join(f"{x.시도} {x.시군구}({x.고령인구비율})" for x in over.itertuples()))
s = df[df["수도권"] == "수도권"]["고령인구비율"]
q1, q3 = s.quantile([.25, .75])
print(f"수도권 고령 이상치(1.5 IQR 위) {int((s > q3 + 1.5 * (q3 - q1)).sum())}곳")
s = df[df["수도권"] == "수도권"]["합계출산율"]
q1, q3 = s.quantile([.25, .75])
print(f"수도권 합계출산율 이상치 위 {int((s > q3 + 1.5 * (q3 - q1)).sum())}곳")

head("[4] 2.6 상관 행렬")
COLS = ["총인구", "출생아수", "면적", "고령인구비율", "노년부양비", "노령화지수", "중위연령",
        "유소년부양비", "인구밀도", "인구증가율", "합계출산율"]
corr = df[COLS].corr()
print(corr.round(2).to_string())
pairs = []
for i in range(len(COLS)):
    for j in range(i + 1, len(COLS)):
        s = df[[COLS[i], COLS[j]]].dropna()
        rv = s[COLS[i]].corr(s[COLS[j]])
        pairs.append((abs(rv), rv, COLS[i], COLS[j], len(s)))
pairs.sort(reverse=True)
print(f"짝의 수 {len(pairs)}")
print("-- 절댓값 상위 8")
for _, rv, x, y, n in pairs[:8]:
    print(f"   {x} - {y}: {rv:+.3f} (n {n})")
AGE = {"고령인구비율", "노년부양비", "노령화지수", "중위연령", "유소년부양비"}
SCALE = {"총인구", "출생아수", "면적"}
print("-- 같은 묶음(연령 구조끼리, 규모끼리) 짝을 뺀 상위 6")
k = 0
for _, rv, x, y, n in pairs:
    if (x in AGE and y in AGE) or (x in SCALE and y in SCALE):
        continue
    print(f"   {x} - {y}: {rv:+.3f} (n {n})")
    k += 1
    if k == 6:
        break
n_age = sum(1 for p in pairs if p[2] in AGE and p[3] in AGE and p[0] >= 0.8)
print(f"연령 구조 변수끼리 10짝 중 |r|>=0.8: {n_age}")
for col in ["고령인구비율", "합계출산율"]:
    print(f"로그 인구밀도 - {col}: {np.log10(df['인구밀도']).corr(df[col]):+.3f}")
print(f"인구밀도-합계출산율 {df['인구밀도'].corr(df['합계출산율']):+.3f}")
print(f"인구밀도 중앙값 {dn.median():.1f}, 평균 {dn.mean():.1f}, 최대 {dn.max():.1f} ({name(dn.idxmax())})")

head("[5] 2.7 2013 -> 2023 합계출산율 변화 (결합 규칙 적용)")
raw = df[["시도", "시군구", "합계출산율"]].merge(t13, on=["시도", "시군구"], how="outer", indicator=True)
print("결합 전:", raw["_merge"].value_counts().to_dict())
print("2023만:", raw[raw["_merge"] == "left_only"][["시도", "시군구"]].values.tolist())
ro = raw[raw["_merge"] == "right_only"]
print("2013만:", len(ro), "중 (변동전)", int(ro["시군구"].str.contains("변동전").sum()),
      ro[ro["시군구"].str.contains("변동전")][["시도", "시군구"]].values.tolist())
MAP = {("인천", "남구(변동전)"): ("인천", "미추홀구"),
       ("경북", "군위군(변동전)"): ("대구", "군위군"),
       ("충북", "청주시(변동전)"): ("충북", "청주시")}
t2 = t13.copy()
for (s0, g0), (s1, g1) in MAP.items():
    m = (t2["시도"] == s0) & (t2["시군구"] == g0)
    t2.loc[m, ["시도", "시군구"]] = [s1, g1]
both = df[["시도", "시군구", "합계출산율"]].merge(t2, on=["시도", "시군구"], how="left", validate="one_to_one")
print(f"대응표 적용 뒤 {len(both)}행, 2013 결측 {int(both['합계출산율_2013'].isna().sum())}")
both["변화"] = both["합계출산율"] - both["합계출산율_2013"]
v = both["변화"]
print(f"2013 평균 {both['합계출산율_2013'].mean():.3f}, 2023 평균 {both['합계출산율'].mean():.3f}")
print(f"변화 평균 {v.mean():.3f}, 중앙값 {v.median():.3f}, 최소 {v.min():.3f}, 최대 {v.max():.3f}")
print(f"하락 {int((v < 0).sum())}, 상승 {int((v > 0).sum())}, 같음 {int((v == 0).sum())}, "
      f"0.4명 이상 하락 {int((v <= -0.4).sum())}")
print(f"r(2013, 2023) = {both['합계출산율_2013'].corr(both['합계출산율']):.3f}, "
      f"r(2013, 변화) = {both['합계출산율_2013'].corr(v):.3f}")
cols = ["시도", "시군구", "합계출산율_2013", "합계출산율", "변화"]
print(both.sort_values("변화").head(5)[cols].round(3).to_string(index=False))
print(both[v > 0].sort_values("변화", ascending=False)[cols].round(3).to_string(index=False))
for key in [("충북", "청주시"), ("대구", "군위군"), ("인천", "미추홀구"), ("경남", "창원시"), ("강원", "강릉시")]:
    row = both[(both["시도"] == key[0]) & (both["시군구"] == key[1])].iloc[0]
    print(f"{key}: 2013 {row['합계출산율_2013']}, 2023 {row['합계출산율']}, 변화 {row['변화']:.3f}")

head("[6] 2.8 면적-합계출산율, 극단값")
print(f"면적-합계출산율 r {df['면적'].corr(df['합계출산율']):.3f}, 로그 면적 r "
      f"{np.log10(df['면적']).corr(df['합계출산율']):.3f} (n {len(df)})")
ar = df["면적"]
print(f"면적 중앙값 {ar.median():.1f}, 100 미만 {int((ar < 100).sum())}곳 중 1.0명 이상 "
      f"{int(((ar < 100) & (t >= 1)).sum())}, 500 이상 {int((ar >= 500).sum())}곳 중 1.0명 이상 "
      f"{int(((ar >= 500) & (t >= 1)).sum())}")
print(df.nlargest(3, "면적")[["시도", "시군구", "면적", "합계출산율"]].round(3).to_string(index=False))
print(df.nsmallest(3, "면적")[["시도", "시군구", "면적", "합계출산율"]].round(3).to_string(index=False))
for col in ["고령인구비율", "합계출산율", "인구밀도", "면적", "인구증가율"]:
    s = df[col].dropna()
    print(f"{col}: 최소 {s.min():,.3f} ({name(s.idxmin())}), 최대 {s.max():,.3f} ({name(s.idxmax())})")

head("[7] 2.10 그림 규격 막대그래프")
m = df.groupby("수도권")["합계출산율"].agg(["count", "mean"])
print(m.round(3).to_string())
print(f"길이 비 {m.loc['비수도권', 'mean'] / m.loc['수도권', 'mean']:.3f}, "
      f"차이 {m.loc['비수도권', 'mean'] - m.loc['수도권', 'mean']:.3f}")

head("[8] 2.12 eda-pack 시험 실행 기준값")
s2 = df[["인구증가율", "고령인구비율"]].dropna()
print(f"인구증가율-고령인구비율 r = {s2['인구증가율'].corr(s2['고령인구비율']):.3f} (n {len(s2)})")
