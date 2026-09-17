# 9주차 2회차(실습) 본문 수치 계산: 시도별 관측치 수, 수도권·비수도권 분포 요약,
# 합계출산율·인구증가율 분포, 2013→2023 합계출산율 변화, 면적-합계출산율 답사와 극단값,
# 그림 규격 막대그래프, 새 대화 독립 검산용 값 (대괄호 번호 뒤의 절 번호는 본문 기준)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")
mg = pd.read_csv(BASE / "data" / "sigungu_tfr_2013_2023.csv", encoding="utf-8-sig")
inc = pd.read_csv(BASE / "data" / "income_dist.csv", encoding="utf-8-sig")

print("=" * 60)
print("[1] 2.1 히스토그램·산점도·시계열 검증용 기준값")
print("=" * 60)
a = df["고령인구비율"]
print(f"시군구 수 = {len(df)}, 고령인구비율 평균 = {a.mean():.2f}, 중앙값 = {a.median():.2f}, "
      f"최소 = {a.min():.2f} ({df.loc[a.idxmin(), '시도']} {df.loc[a.idxmin(), '시군구']}), "
      f"최대 = {a.max():.2f} ({df.loc[a.idxmax(), '시도']} {df.loc[a.idxmax(), '시군구']})")
print(f"히스토그램 구간 2.5%포인트 기준 최빈 구간: ", end="")
bins = np.arange(10, 47.5, 2.5)
cnt, edges = np.histogram(a, bins=bins)
k = cnt.argmax()
print(f"{edges[k]:.1f}-{edges[k+1]:.1f}% ({cnt[k]}개)")
sub = df.dropna(subset=["합계출산율"])
r = sub["고령인구비율"].corr(sub["합계출산율"])
print(f"산점도 점 수 = {len(sub)}, r = {r:.3f}")
print(f"결측 시군구: {df.loc[df['합계출산율'].isna(), ['시도', '시군구']].values.tolist()}")
print(f"지니계수 첫해 {inc['연도'].iloc[0]} = {inc['지니계수'].iloc[0]:.3f}, "
      f"마지막 해 {inc['연도'].iloc[-1]} = {inc['지니계수'].iloc[-1]:.3f}, "
      f"최소 = {inc['지니계수'].min():.3f}, 최대 = {inc['지니계수'].max():.3f}")

print()
print("[1-2] 시도별 관측치 수와 고령인구비율 중앙값 (중앙값 오름차순)")
tab = (df.groupby("시도")["고령인구비율"]
         .agg(시군구수="count", 중앙값="median", 최소="min", 최대="max")
         .sort_values("중앙값"))
print(tab.round(2).to_string())
print(f"시군구 수 합계 = {tab['시군구수'].sum()}")

print()
print("=" * 60)
print("[2] 2.3 수도권 vs 비수도권 분포 요약 (박스플롯 검증용)")
print("=" * 60)
df["권역"] = np.where(df["시도"].isin(["서울", "경기", "인천"]), "수도권", "비수도권")
for col in ["고령인구비율", "합계출산율"]:
    print(f"--- {col}")
    for g in ["수도권", "비수도권"]:
        s = df.loc[df["권역"] == g, col].dropna()
        q1, med, q3 = s.quantile([0.25, 0.5, 0.75])
        i_min, i_max = s.idxmin(), s.idxmax()
        print(f"{g}: n={len(s)}, 최소={s.min():.3f}({df.loc[i_min,'시도']} {df.loc[i_min,'시군구']}), "
              f"Q1={q1:.3f}, 중앙값={med:.3f}, Q3={q3:.3f}, "
              f"최대={s.max():.3f}({df.loc[i_max,'시도']} {df.loc[i_max,'시군구']}), 평균={s.mean():.3f}")
# 겹침 확인: 비수도권 중앙값보다 고령인구비율이 높은 수도권 시군구
med_non = df.loc[df["권역"] == "비수도권", "고령인구비율"].median()
over = df[(df["권역"] == "수도권") & (df["고령인구비율"] > med_non)]
print(f"비수도권 중앙값({med_non:.2f}%)보다 높은 수도권 시군구 {len(over)}곳: "
      + ", ".join(f"{r_.시도} {r_.시군구}({r_.고령인구비율:.1f})" for r_ in over.itertuples()))
min_non = df.loc[df["권역"] == "비수도권", "고령인구비율"].min()
under = df[(df["권역"] == "비수도권") & (df["고령인구비율"] < df.loc[df['권역']=='수도권','고령인구비율'].median())]
print(f"수도권 중앙값보다 낮은 비수도권 시군구 {len(under)}곳 (예: "
      + ", ".join(f"{r_.시도} {r_.시군구}({r_.고령인구비율:.1f})" for r_ in under.sort_values('고령인구비율').head(5).itertuples()) + ")")

print()
print("=" * 60)
print("[3] 2.5 합계출산율 2013→2023 변화 (병합 파일)")
print("=" * 60)
print(f"병합 파일 행 수 = {len(mg)}, 2013 결측 = {mg['합계출산율_2013'].isna().sum()}, "
      f"2023 결측 = {mg['합계출산율'].isna().sum()}")
both = mg.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
both["변화"] = both["합계출산율"] - both["합계출산율_2013"]
print(f"두 해 모두 있는 시군구 = {len(both)}")
print(f"2013 평균 = {both['합계출산율_2013'].mean():.3f}, 2023 평균 = {both['합계출산율'].mean():.3f}")
print(f"변화 평균 = {both['변화'].mean():.3f}, 중앙값 = {both['변화'].median():.3f}, "
      f"최소 = {both['변화'].min():.3f}, 최대 = {both['변화'].max():.3f}")
print(f"하락 {int((both['변화'] < 0).sum())}곳, 상승 {int((both['변화'] > 0).sum())}곳, "
      f"변화 없음 {int((both['변화'] == 0).sum())}곳")
print(f"2013 vs 2023 상관계수 r = {both['합계출산율_2013'].corr(both['합계출산율']):.3f}")
cols = ["시도", "시군구", "합계출산율_2013", "합계출산율", "변화"]
print("-- 하락 폭 상위 5")
print(both.sort_values("변화").head(5)[cols].round(3).to_string(index=False))
print("-- 상승(또는 하락 폭 최소) 상위 5")
print(both.sort_values("변화", ascending=False).head(5)[cols].round(3).to_string(index=False))
print("-- 표본 검산용 3곳")
for sido, sgg in [("강원", "강릉시"), ("전남", "영광군"), ("부산", "중구")]:
    row = both[(both["시도"] == sido) & (both["시군구"] == sgg)].iloc[0]
    print(f"{sido} {sgg}: 2013={row['합계출산율_2013']:.3f}, 2023={row['합계출산율']:.3f}, 변화={row['변화']:.3f}")
# 부호 뒤집기 실수 시 보고될 값
print(f"부호를 거꾸로(2013-2023) 계산하면: 평균 {(-both['변화']).mean():+.3f}, "
      f"'상승' {int((both['변화'] < 0).sum())}곳으로 보고됨")
# 히스토그램 구간
bins2 = np.arange(-0.8, 0.45, 0.1)
cnt2, edges2 = np.histogram(both["변화"], bins=bins2)
k2 = cnt2.argmax()
print(f"변화량 히스토그램(폭 0.1) 최빈 구간: {edges2[k2]:.1f}-{edges2[k2+1]:.1f} ({cnt2[k2]}개)")
print(f"-0.2 이하 하락 {int((both['변화'] <= -0.2).sum())}곳, -0.4 이하 하락 {int((both['변화'] <= -0.4).sum())}곳")
sejong = mg[mg["시도"] == "세종"][cols[:4]]
print("세종 행:", sejong.to_dict("records"))
cheongju = mg[mg["시군구"] == "청주시"][cols[:4]]
print("청주 행:", cheongju.to_dict("records"))

print()
print("=" * 60)
print("[4] 2.10 새 대화 독립 검산용 값 셋")
print("=" * 60)
print(f"(1) 고령인구비율-합계출산율 상관계수 r = {r:.3f} (n = {len(sub)})")
cap = df[df["권역"] == "수도권"]["고령인구비율"].median()
non = df[df["권역"] == "비수도권"]["고령인구비율"].median()
print(f"(2) 고령인구비율 중앙값: 수도권 {cap:.2f}, 비수도권 {non:.2f}")
worst = both.sort_values("변화").iloc[0]
print(f"(3) 2013→2023 하락 폭 최대: {worst['시도']} {worst['시군구']} {worst['변화']:.3f} "
      f"({worst['합계출산율_2013']:.3f} → {worst['합계출산율']:.3f})")

print()
print("=" * 60)
print("[5] 2.11 선택 심화·과제 9-D 기준값")
print("=" * 60)
s2 = df[["인구증가율", "고령인구비율"]].dropna()
print(f"인구증가율-고령인구비율 상관계수 r = {s2['인구증가율'].corr(s2['고령인구비율']):.3f} (n = {len(s2)})")
print(f"2013년 합계출산율-변화량 상관계수 r = {both['합계출산율_2013'].corr(both['변화']):.3f} (n = {len(both)})")

print()
print("=" * 60)
print("[6] 2.2 합계출산율·인구증가율의 분포 (다섯 숫자 요약과 구간 폭)")
print("=" * 60)
for col, w in [("합계출산율", 0.05), ("인구증가율", 0.5)]:
    s6 = df[col].dropna()
    q1, med6, q3 = s6.quantile([0.25, 0.5, 0.75])
    i_min, i_max = s6.idxmin(), s6.idxmax()
    print(f"{col}: n = {len(s6)}, 결측 {int(df[col].isna().sum())}곳, "
          f"최소 {s6.min():.3f}({df.loc[i_min,'시도']} {df.loc[i_min,'시군구']}), "
          f"Q1 {q1:.3f}, 중앙값 {med6:.3f}, Q3 {q3:.3f}, "
          f"최대 {s6.max():.3f}({df.loc[i_max,'시도']} {df.loc[i_max,'시군구']}), "
          f"평균 {s6.mean():.3f}")
    lo = np.floor(s6.min() / w) * w
    hi = np.ceil(s6.max() / w) * w
    edges6 = np.arange(lo, hi + w / 2, w)
    cnt6, _ = np.histogram(s6, bins=edges6)
    k6 = int(cnt6.argmax())
    print(f"   구간 폭 {w:g} 기준 막대 {len(cnt6)}개, 가장 높은 막대 "
          f"{edges6[k6]:.2f}-{edges6[k6+1]:.2f} ({cnt6[k6]}개), 높이 합계 {int(cnt6.sum())}")
tfr = df["합계출산율"].dropna()
print(f"합계출산율 1.0명 이상 {int((tfr >= 1.0).sum())}곳, 0.7명 미만 {int((tfr < 0.7).sum())}곳")
g = df["인구증가율"]
print(f"인구증가율 양수 {int((g > 0).sum())}곳, 음수 {int((g < 0).sum())}곳, 0 {int((g == 0).sum())}곳")
print(f"인구증가율 단순 평균 {g.mean():.3f}, 총인구 가중 평균 "
      f"{np.average(g, weights=df['총인구']):.3f} (의미 없는 평균을 잡는 장면용)")

print()
print("=" * 60)
print("[7] 2.4 수치형 열 전체의 상관 행렬")
print("=" * 60)
NUMCOLS = ["총인구", "생산가능", "고령", "유소년", "출생아수",
           "면적", "인구밀도", "인구증가율", "고령인구비율", "합계출산율"]
print(df[NUMCOLS].corr().round(2).to_string())
pairs = []
for i in range(len(NUMCOLS)):
    for j in range(i + 1, len(NUMCOLS)):
        s3 = df[[NUMCOLS[i], NUMCOLS[j]]].dropna()
        pairs.append((abs(s3[NUMCOLS[i]].corr(s3[NUMCOLS[j]])),
                      s3[NUMCOLS[i]].corr(s3[NUMCOLS[j]]), NUMCOLS[i], NUMCOLS[j], len(s3)))
pairs.sort(reverse=True)
print("-- 절댓값 상위 6쌍 (규모 변수끼리가 상위를 독차지한다)")
for _, rv, x, y, n in pairs[:6]:
    print(f"   {x} - {y}: r = {rv:+.3f} (n = {n})")
SCALE = {"총인구", "생산가능", "고령", "유소년", "출생아수", "면적"}
print("-- 규모 변수끼리를 뺀 상위 5쌍")
shown = 0
for _, rv, x, y, n in pairs:
    if x in SCALE and y in SCALE:
        continue
    print(f"   {x} - {y}: r = {rv:+.3f} (n = {n})")
    shown += 1
    if shown == 5:
        break
d2 = df.assign(로그인구밀도=np.log10(df["인구밀도"]))
for col in ["고령인구비율", "합계출산율"]:
    s4 = d2[["로그인구밀도", col]].dropna()
    print(f"로그 인구밀도 - {col}: r = {s4['로그인구밀도'].corr(s4[col]):+.3f} (n = {len(s4)})")

print()
print("=" * 60)
print("[8] 2.6 면적-합계출산율 답사와 극단값 목록")
print("=" * 60)
print(f"면적-합계출산율 r = {sub['면적'].corr(sub['합계출산율']):.3f}, "
      f"로그 면적 r = {np.log10(sub['면적']).corr(sub['합계출산율']):.3f} (n = {len(sub)})")
print(f"면적 500km2 이상 {int((sub['면적'] >= 500).sum())}곳 가운데 합계출산율 1.0명 이상 "
      f"{int(((sub['면적'] >= 500) & (sub['합계출산율'] >= 1.0)).sum())}곳, "
      f"면적 100km2 미만 {int((sub['면적'] < 100).sum())}곳 가운데 "
      f"{int(((sub['면적'] < 100) & (sub['합계출산율'] >= 1.0)).sum())}곳")
print("-- 면적 최대·최소 시군구")
print(sub.nlargest(3, "면적")[["시도", "시군구", "면적", "합계출산율"]].round(3).to_string(index=False))
print(sub.nsmallest(3, "면적")[["시도", "시군구", "면적", "합계출산율"]].round(3).to_string(index=False))
print("-- 극단값 목록 (표 9-4)")
for col in ["고령인구비율", "합계출산율", "인구밀도", "면적"]:
    s8 = df[col].dropna()
    i_min, i_max = s8.idxmin(), s8.idxmax()
    print(f"{col}: 최소 {s8.min():,.3f} ({df.loc[i_min,'시도']} {df.loc[i_min,'시군구']}), "
          f"최대 {s8.max():,.3f} ({df.loc[i_max,'시도']} {df.loc[i_max,'시군구']})")
print(f"원본 행 수 {len(df)} (극단값을 다루어도 이 값은 변하지 않아야 한다)")

print()
print("=" * 60)
print("[8-2] 2.8 그림 규격대로 그리는 권역별 평균 합계출산율 막대그래프")
print("=" * 60)
for gname in ["수도권", "비수도권"]:
    s9 = df.loc[df["권역"] == gname, "합계출산율"].dropna()
    print(f"{gname}: n = {len(s9)}, 평균 {s9.mean():.3f}")
cap_m = df.loc[df["권역"] == "수도권", "합계출산율"].mean()
non_m = df.loc[df["권역"] == "비수도권", "합계출산율"].mean()
print(f"두 막대 길이의 비 = {non_m / cap_m:.3f}배 (세로축을 0에서 시작했을 때)")

print()
print("=" * 60)
print("[9] 2.9 그림 재현: 같은 코드를 두 번 실행하면 같은 파일이 나오는가")
print("=" * 60)
print("실측(matplotlib 3.10.8, 2026-09): 난수를 쓰지 않는 그림은 두 번 저장한 PNG의")
print("MD5 값이 같았다. 흔들기(jitter)에 난수를 쓰면 씨앗을 고정하지 않는 한 매번 달랐고,")
print("씨앗을 42로 고정하면 다시 같아졌다. PNG 안에는 matplotlib 버전 문자열이 들어가므로")
print("도구 버전이 바뀌면 그림이 같아 보여도 파일은 달라질 수 있다.")
