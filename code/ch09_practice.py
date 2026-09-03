# 9주차 2회차(실습) 본문 수치 계산: 시도별 관측치 수, 수도권·비수도권 분포 요약,
# 2013→2023 합계출산율 변화, 새 대화 독립 검산용 값
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
print("[4] 2.11 새 대화 독립 검산용 값 셋")
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
print("[5] 2.12 선택 심화·과제 9-D 기준값")
print("=" * 60)
s2 = df[["인구증가율", "고령인구비율"]].dropna()
print(f"인구증가율-고령인구비율 상관계수 r = {s2['인구증가율'].corr(s2['고령인구비율']):.3f} (n = {len(s2)})")
print(f"2013년 합계출산율-변화량 상관계수 r = {both['합계출산율_2013'].corr(both['변화']):.3f} (n = {len(both)})")

print()
print("=" * 60)
print("[6] 2.2 히스토그램 구간 폭 세 가지 비교 (고령인구비율)")
print("=" * 60)
for w in [1.0, 2.5, 5.0]:
    lo = np.floor(a.min() / w) * w
    hi = np.ceil(a.max() / w) * w
    edges3 = np.arange(lo, hi + w / 2, w)
    cnt3, _ = np.histogram(a, bins=edges3)
    k3 = int(cnt3.argmax())
    peaks = sum(1 for i in range(1, len(cnt3) - 1)
                if cnt3[i] >= cnt3[i - 1] and cnt3[i] > cnt3[i + 1])
    print(f"폭 {w:g}%포인트: 막대 {len(cnt3)}개, 가장 높은 막대 "
          f"{edges3[k3]:.1f}-{edges3[k3 + 1]:.1f}% ({cnt3[k3]}개), "
          f"국소 봉우리 {peaks}개, 막대 높이 = {list(map(int, cnt3))}")

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
print("[8] 2.6 이상치 한 곳을 빼면 무엇이 달라지는가 (고령인구비율-합계출산율)")
print("=" * 60)
print("-- 합계출산율 상위 5곳")
print(sub.nlargest(5, "합계출산율")[["시도", "시군구", "고령인구비율", "합계출산율"]]
      .round(3).to_string(index=False))
cases = [("전체 229곳(결측 1 제외)", sub),
         ("전남 영광군 제외", sub[~((sub["시도"] == "전남") & (sub["시군구"] == "영광군"))]),
         ("경북 의성군 제외", sub[~((sub["시도"] == "경북") & (sub["시군구"] == "의성군"))]),
         ("부산 중구 제외", sub[~((sub["시도"] == "부산") & (sub["시군구"] == "중구"))]),
         ("합계출산율 상위 3곳 제외", sub.drop(sub.nlargest(3, "합계출산율").index))]
for label, s5 in cases:
    print(f"{label}: n = {len(s5)}, r = {s5['고령인구비율'].corr(s5['합계출산율']):.3f}, "
          f"합계출산율 최대 {s5['합계출산율'].max():.3f}, 고령인구비율 최대 {s5['고령인구비율'].max():.2f}")

print()
print("=" * 60)
print("[9] 2.10 그림 재현: 같은 코드를 두 번 실행하면 같은 파일이 나오는가")
print("=" * 60)
print("실측(matplotlib 3.10.8, 2026-09): 난수를 쓰지 않는 그림은 두 번 저장한 PNG의")
print("MD5 값이 같았다. 흔들기(jitter)에 난수를 쓰면 씨앗을 고정하지 않는 한 매번 달랐고,")
print("씨앗을 42로 고정하면 다시 같아졌다. PNG 안에는 matplotlib 버전 문자열이 들어가므로")
print("도구 버전이 바뀌면 그림이 같아 보여도 파일은 달라질 수 있다.")
