# -*- coding: utf-8 -*-
# 5주차 2회차 실습 수치 계산 스크립트
# (1) profile(): 교재 2.3절의 .claude/skills/csv-profile/scripts/profile.py 와 같은 코드.
#     실습 장 본문의 출력 예시는 이 함수의 실제 출력이다.
# (2) 즉흥 코드의 결측 처리 차이(2.3절 틀리는 장면), 오류 심기 사본(2.6절),
#     독립 검산 대조표(2.8절)의 수치를 계산한다.
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "ch05_out"
OUT.mkdir(exist_ok=True)


# ---------------------------------------------------------------- (1) profile.py 원형
def md_table(df):
    """DataFrame을 마크다운 표 문자열로 바꾼다 (외부 패키지 없이)."""
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row.tolist()) + " |")
    return "\n".join(lines)


def profile(path, mode="간단"):
    """CSV 프로파일링 보고서(1-4절)를 문자열로 돌려준다. 5절(확인 필요)은 에이전트 몫."""
    path = Path(path)
    df = pd.read_csv(path, encoding="utf-8-sig")
    out = [f"# 데이터 프로파일링: {path.name} ({mode} 모드)", "",
           "## 1. 기본 정보", f"- 원본 파일: {path.as_posix()}",
           f"- 행 수: {len(df)}, 열 수: {df.shape[1]}", "", "## 2. 열 정보"]
    info = pd.DataFrame({"열 이름": df.columns, "자료형": df.dtypes.astype(str).values,
                         "결측 개수": df.isna().sum().values,
                         "결측 비율(%)": (df.isna().mean() * 100).round(1).values,
                         "고유값 수": df.nunique().values})
    out += [md_table(info), "", "## 3. 수치형 요약"]
    if mode == "상세":
        num = df.select_dtypes("number")
        summ = num.agg(["count", "mean", "std", "min", "median", "max"]).T.round(3)
        summ.columns = ["개수", "평균", "표준편차", "최솟값", "중앙값", "최댓값"]
        summ["개수"] = summ["개수"].astype(int)
        summ.insert(0, "열 이름", summ.index)
        out.append(md_table(summ))
    else:
        out.append("(간단 모드에서는 생략. 상세 모드로 다시 실행하면 표가 붙는다)")
    out += ["", "## 4. 품질 경고"]
    warns = [f"- 결측 비율 30% 이상: {c} ({r:.1f}%)"
             for c, r in (df.isna().mean() * 100).items() if r >= 30]
    warns += [f"- 값이 하나뿐인 열: {c}" for c in df.columns if df[c].nunique(dropna=False) == 1]
    if df.duplicated().sum():
        warns.append(f"- 중복 행: {df.duplicated().sum()}행")
    rows = df[df.isna().any(axis=1)]
    if len(rows):
        key_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])][:2] or [df.columns[0]]
        names = [" ".join(str(v) for v in r) for r in rows[key_cols].head(5).values.tolist()]
        warns.append(f"- 결측이 있는 행 {len(rows)}개 (처음 5개까지): " + ", ".join(names))
    out += (warns or ["- 없음"]) + ["", "## 5. 확인 필요 (사람 검토용)", "(에이전트가 reference.md의 지침에 따라 작성)"]
    return "\n".join(out)


def save(name, text):
    (OUT / name).write_text(text, encoding="utf-8")
    print(f"===== {name} =====")
    print(text)
    print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import os
    os.chdir(ROOT)  # 학생의 프로젝트 폴더에서 실행할 때와 같은 상대 경로가 찍히도록
    sig = Path("data/sigungu_2023.csv")
    inc = Path("data/income_dist.csv")

    # 2.1·2.3: csv-profile v2 출력 예시 (간단/상세)
    save("sigungu_간단.md", profile(sig, "간단"))
    save("sigungu_상세.md", profile(sig, "상세"))
    save("income_간단.md", profile(inc, "간단"))
    save("income_상세.md", profile(inc, "상세"))

    # 2.3 재현성: 같은 파일에 두 번 실행해 글자 단위로 같은지
    a, b = profile(sig, "간단"), profile(sig, "간단")
    print("두 번 실행 결과 동일:", a == b, "/ 문자 수:", len(a))
    print()

    # 2.3 틀리는 장면: 즉흥 코드의 결측 처리 차이
    df = pd.read_csv(sig, encoding="utf-8-sig")
    print("== 결측 처리 방식에 따른 평균 차이 ==")
    print(f"합계출산율 평균 (결측 제외, n={df['합계출산율'].count()}): {df['합계출산율'].mean():.4f}")
    print(f"합계출산율 평균 (결측을 0으로 채움, n=229): {df['합계출산율'].fillna(0).mean():.4f}")
    dropped = df.dropna()
    print(f"dropna() 후 행 수: {len(dropped)}")
    print(f"총인구 평균 (229행): {df['총인구'].mean():,.1f}")
    print(f"총인구 평균 (dropna 후 228행): {dropped['총인구'].mean():,.1f}")
    print(f"고령인구비율 평균 (229행): {df['고령인구비율'].mean():.3f}")
    print(f"고령인구비율 평균 (dropna 후 228행): {dropped['고령인구비율'].mean():.3f}")
    gunwi = df[df["시군구"] == "군위군"].iloc[0]
    print(f"군위군 총인구: {gunwi['총인구']:,.0f}, 고령인구비율: {gunwi['고령인구비율']:.3f}")
    print()

    # 2.6 income_dist.csv 기본 사실
    di = pd.read_csv(inc, encoding="utf-8-sig")
    print("== income_dist.csv ==")
    print(f"행 수 {len(di)}, 열 수 {di.shape[1]}, 열 이름 {list(di.columns)}")
    print(f"연도 범위 {di['연도'].min()}-{di['연도'].max()}")
    print(f"지니계수 최댓값 {di['지니계수'].max()} ({di.loc[di['지니계수'].idxmax(), '연도']}), "
          f"최솟값 {di['지니계수'].min()} ({di.loc[di['지니계수'].idxmin(), '연도']}), "
          f"평균 {di['지니계수'].mean():.4f}, 중앙값 {di['지니계수'].median():.4f}")
    print(f"소득5분위배율 최댓값 {di['소득5분위배율'].max()}, 최솟값 {di['소득5분위배율'].min()}, "
          f"평균 {di['소득5분위배율'].mean():.4f}")
    print()

    # 2.6 오류 심기: 지니계수 5칸(2013, 2015, 2017, 2019, 2021년)을 지운 사본
    broken = di.copy()
    broken.loc[broken["연도"].isin([2013, 2015, 2017, 2019, 2021]), "지니계수"] = pd.NA
    bpath = Path("code/ch05_out/income_dist_결측실험.csv")  # 교재 data 폴더는 건드리지 않는다
    broken.to_csv(bpath, index=False, encoding="utf-8-sig")
    save("income_결측실험_간단.md", profile(bpath, "간단"))
    bb = pd.read_csv(bpath, encoding="utf-8-sig")
    print(f"결측실험 사본: 행 수 {len(bb)}, 지니계수 결측 {bb['지니계수'].isna().sum()}개 "
          f"({bb['지니계수'].isna().mean()*100:.1f}%), 결측 제외 평균 {bb['지니계수'].mean():.4f}")
    # 틀리는 장면 대비: 행을 지운 사본(값 대신 행 삭제)
    wrong = di[~di["연도"].isin([2013, 2015, 2017, 2019, 2021])]
    print(f"행을 지운 잘못된 사본: 행 수 {len(wrong)}, 지니계수 결측 {wrong['지니계수'].isna().sum()}개")
    print()

    # 2.8 독립 검산 대조표 수치
    print("== check-report 대조표 수치 (sigungu_2023.csv) ==")
    print(f"행 수 {len(df)}")
    print(f"합계출산율 평균 {df['합계출산율'].mean():.3f} (n={df['합계출산율'].count()}), "
          f"중앙값 {df['합계출산율'].median():.3f}")
    imax, imin = df["총인구"].idxmax(), df["총인구"].idxmin()
    print(f"총인구 최대 {df.loc[imax, '시도']} {df.loc[imax, '시군구']} {df.loc[imax, '총인구']:,.0f}")
    print(f"총인구 최소 {df.loc[imin, '시도']} {df.loc[imin, '시군구']} {df.loc[imin, '총인구']:,.0f}")
    print(f"고령인구비율 최대 {df.loc[df['고령인구비율'].idxmax(), '시군구']} {df['고령인구비율'].max():.1f}")
    print(f"결측 행: {df[df.isna().any(axis=1)][['시도', '시군구']].values.tolist()}")
    print(f"열별 고유값 수: {df.nunique().to_dict()}")
