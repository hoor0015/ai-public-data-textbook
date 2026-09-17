# -*- coding: utf-8 -*-
"""5주차 2회차 2.8의 기준 계산: 공익법인 결산서류 공시(표준서식, 별지 제31호서식) 엑셀 묶음을
한 표로 모으고 보고서에 쓸 집계를 낸다. 본문의 수치는 모두 이 스크립트의 출력이다.

입력: data/gongik/<YYYYMM>/*.xls  (또는 첫째 인자로 준 폴더)
출력: 화면 출력. 둘째 인자로 경로를 주면 법인별 표를 CSV로 저장한다.
실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<교재>/code/ch05_gongik.py"
필요 패키지: pandas, xlrd
"""
import os
import sys
import glob
import io
import contextlib
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "gongik")

# (항목 이름, 절 제목, 그 항목의 칸 이름표). 2019년 개정 서식 기준이다.
FIELDS = [
    ("총자산", "2.재무현황", "총자산가액"), ("부채", "2.재무현황", "부채"), ("순자산", "2.재무현황", "순자산"),
    ("수익총계", "4.수익현황", "31총계"), ("기부금", "4.수익현황", "기부금"), ("보조금", "4.수익현황", "보조금"),
    ("비용총계", "5.비용현황", "40총계"), ("사업비용", "5.비용현황", "42소계"),
    ("사업수행비용", "5.비용현황", "사업수행비용"),
]


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def parse(path):
    """서식 한 장에서 법인 한 곳의 값을 뽑는다. 칸의 위치가 아니라 칸의 이름표로 찾는다."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        df = pd.read_excel(path, sheet_name=0, header=None)
    lab = df[0].fillna("").astype(str).str.replace(r"\s", "", regex=True)

    def find(key):
        idx = lab[lab.str.contains(key, regex=False)].index
        return idx[0] if len(idx) else None

    def text(key, col=2):
        r = find(key)
        if r is None or pd.isna(df.iat[r, col]):
            return None
        return str(df.iat[r, col]).strip()

    def value(title, key):
        """절 제목 아래 두 줄의 머리글에서 key가 적힌 칸을 찾고, 총계 행의 그 칸 값을 읽는다."""
        s = find(title)
        if s is None:
            return None
        col = total = None
        for r in range(s + 1, min(s + 7, len(df))):
            if lab[r].startswith("ⓐ") and "총계" in lab[r]:
                total = r
                break
            for c in range(df.shape[1]):
                cell = df.iat[r, c]
                if col is None and pd.notna(cell) and key in "".join(str(cell).split()):
                    col = c
        if col is None or total is None or pd.isna(df.iat[total, col]):
            return None
        return num(df.iat[total, col])

    out = {
        "월": os.path.basename(os.path.dirname(path)),
        "파일": os.path.basename(path),
        "법인명": text("①공익법인등명") or text("1공익법인명", 4),
        "공익사업유형": text("⑬공익사업유형"),
        "설립근거법": text("⑪설립근거법"),
        "고용직원수": num(text("⑰고용직원수")),
    }
    r = find("사업연도")
    out["사업연도시작"] = None
    if r is not None:                    # 시작일은 서식 판에 따라 놓인 칸이 다르다
        for c in range(1, df.shape[1]):
            if pd.notna(df.iat[r, c]):
                out["사업연도시작"] = str(df.iat[r, c]).split(".")[0]
                break
    out["서식"] = "2019개정" if find("2.재무현황") is not None else (
        "2016개정" if find("2.자산보유현황") is not None else "미확인")
    for name, title, key in FIELDS:
        out[name] = value(title, key)
    return out


def main():
    files = sorted(glob.glob(os.path.join(SRC, "*", "*.xls")))
    rows, errors = [], []
    for f in files:
        try:
            rows.append(parse(f))
        except Exception as ex:          # 읽지 못한 파일은 세어서 보고한다
            errors.append((os.path.basename(f), repr(ex)[:100]))
    d = pd.DataFrame(rows)
    if len(sys.argv) > 2:
        d.to_csv(sys.argv[2], index=False, encoding="utf-8-sig")

    print(f"[1] 파일 {len(files)}개, 읽은 것 {len(d)}개, 읽지 못한 것 {len(errors)}개")
    for e in errors[:10]:
        print("   ", e)
    print("\n[2] 월 폴더별 파일 수")
    print(d["월"].value_counts().sort_index().to_string())
    print("\n[2-1] 서식 판별")
    print(d["서식"].value_counts().to_string())
    old = d[d["서식"] != "2019개정"]
    d = d[d["서식"] == "2019개정"].copy()
    print(f"    2019년 개정 서식이 아닌 {len(old)}개는 항목 구성이 달라 아래 집계에서 뺀다 "
          f"(사업연도 시작 연도: {old['사업연도시작'].str[:4].value_counts().to_dict()})")
    print("\n[3] 항목별 빈칸 수")
    print(d.isna().sum().to_string())
    print("\n[4] 사업연도 시작일 분포 (상위 5)")
    print(d["사업연도시작"].value_counts().head(5).to_string())
    print("\n[5] 같은 법인명이 두 번 이상 나오는 경우")
    dup = d["법인명"].value_counts()
    print(f"    법인명 고유값 {dup.size}개, 두 번 이상 {int((dup > 1).sum())}개, 최다 {dup.index[0]} {dup.iloc[0]}회")

    money = ["총자산", "수익총계", "사업비용"]
    print("\n[6] 평균, 중앙값, 합계 (원)")
    for c in money:
        s = d[c].dropna()
        print(f"    {c}: n={len(s)}, 평균 {s.mean():,.0f}, 중앙값 {s.median():,.0f}, 합계 {s.sum():,.0f}, "
              f"0인 곳 {int((s == 0).sum())}, 음수 {int((s < 0).sum())}")
    for c in money:
        print(f"\n[7] {c} 상위 5")
        top = d.nlargest(5, c)[["월", "파일", "법인명", c]]
        for _, r in top.iterrows():
            print(f"    {r[c]:>20,.0f}  {r['법인명']}  ({r['월']}/{r['파일'][:4]})")
    print("\n[8] 상위 집중도")
    for c in money:
        s = d[c].dropna().sort_values(ascending=False)
        print(f"    {c}: 상위 10곳이 합계의 {s.head(10).sum() / s.sum() * 100:.1f}%, 상위 1%({max(1, len(s) // 100)}곳)가 "
              f"{s.head(max(1, len(s) // 100)).sum() / s.sum() * 100:.1f}%")
    print("\n[9] 공익사업유형별 법인 수와 총자산 중앙값")
    g = d.groupby("공익사업유형")["총자산"].agg(["size", "median"]).sort_values("size", ascending=False)
    for k, r in g.head(8).iterrows():
        print(f"    {k}: {int(r['size'])}곳, 총자산 중앙값 {r['median']:,.0f}")
    print("\n[10] 검산: 총자산 = 부채 + 순자산 이 맞지 않는 곳")
    chk = d.dropna(subset=["총자산", "부채", "순자산"])
    bad = chk[(chk["총자산"] - chk["부채"] - chk["순자산"]).abs() > 1]
    print(f"    {len(bad)}곳 / {len(chk)}곳")
    same = bad[(bad["순자산"] == bad["총자산"]) & (bad["부채"] > 0)]
    zero = bad[(bad["순자산"] == 0) & (bad["부채"] == 0)]
    print(f"    그중 순자산을 총자산과 같게 적은 곳 {len(same)}곳, 부채와 순자산을 모두 0으로 둔 곳 {len(zero)}곳")

    print("\n[11] 같은 법인이 여러 번 나오는 까닭: 법인명과 사업연도가 모두 같은 파일")
    key = d.dropna(subset=["법인명"]).groupby(["법인명", "사업연도시작"]).size()
    print(f"    법인명·사업연도 조합 {key.size}개, 그중 두 번 이상 {int((key > 1).sum())}개")
    sams = d[d["법인명"].str.contains("삼성생명공익재단", na=False)][["월", "파일", "사업연도시작", "총자산"]]
    print(sams.to_string(index=False))

    print("\n[12] 국민연금공단 한 곳을 빼면")
    x = d[~d["법인명"].str.contains("국민연금공단", na=False)]
    for c in money:
        s = x[c].dropna()
        print(f"    {c}: 평균 {s.mean():,.0f}, 중앙값 {s.median():,.0f}")

    print("\n[13] 보고서 기준값: 법인마다 가장 최근 사업연도의 공시 하나만 남긴 뒤")
    u = d.sort_values(["법인명", "사업연도시작", "월", "파일"]).drop_duplicates("법인명", keep="last")
    print(f"    법인 {len(u)}곳 (중복 정리 전 {len(d)}개 파일)")
    print("    사업연도 시작 연도:", u["사업연도시작"].str[:4].value_counts().to_dict())
    for c in money:
        s = u[c].dropna()
        print(f"    {c}: n={len(s)}, 평균 {s.mean():,.0f}, 중앙값 {s.median():,.0f}, 합계 {s.sum():,.0f}")
    for c in money:
        print(f"    {c} 상위 5")
        for _, r in u.nlargest(5, c).iterrows():
            print(f"        {r[c]:>20,.0f}  {r['법인명']}  ({r['월']}/{r['파일'][:4]}, 사업연도 {r['사업연도시작'][:4]})")
    s = u["수익총계"].dropna().sort_values(ascending=False)
    print(f"    수익총계 상위 10곳 비중 {s.head(10).sum() / s.sum() * 100:.1f}%, "
          f"평균보다 수익이 큰 법인 {int((s > s.mean()).sum())}곳 ({(s > s.mean()).mean() * 100:.1f}%)")
    chk = u.dropna(subset=["총자산", "부채", "순자산"])
    bad = chk[(chk["총자산"] - chk["부채"] - chk["순자산"]).abs() > 1]
    print(f"    총자산 = 부채 + 순자산이 맞지 않는 곳 {len(bad)}곳 / {len(chk)}곳 ({len(bad) / len(chk) * 100:.1f}%)")
    print(f"    기부금 합계 {u['기부금'].sum():,.0f}, 보조금 합계 {u['보조금'].sum():,.0f}, "
          f"보조금이 수익의 절반을 넘는 법인 {int((u['보조금'] > u['수익총계'] * 0.5).sum())}곳")
    return d


if __name__ == "__main__":
    main()
