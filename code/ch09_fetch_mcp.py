"""9주차 공통 데이터 수집: kosis MCP 서버를 직접 호출해 시군구 데이터셋을 만든다.

학생이 9주차 2차시 2.1-2.2에서 kosis MCP(kosis_get_data)로 받는 것과 같은 요청을 MCP 서버(HTTP)에
보내고, 응답 표를 그대로 CSV로 저장한 뒤(data/raw_mcp/), 학생이 에이전트에게 시키는 것과 같은 규칙으로
정제·결합해 data/sigungu_mcp_2023.csv를 만든다. 교재 9-14주차의 모든 수치는 이 파일에서 계산한다.

MCP 응답의 특징(교재 본문에서 그대로 다룬다):
  - 지역은 이름만 오고 코드는 오지 않는다. 시도 행 뒤에 그 시도의 시군구 행이 이어지므로 시도 열은
    "시도 행을 만나면 그 뒤 행에 채운다"는 규칙으로 만든다(동명 구 구분: 중구·남구·북구·서구·동구).
  - e-지방지표 표(DT_1YL20651E, DT_1YL20631, DT_1YL20621)는 시군구 단위만 있고 일반구(수원시 장안구 등)가
    없다. 합계출산율 표(DT_1B81A23)와 면적 표(DT_MLTM_2300)에는 일반구가 섞여 있으므로 e-지방지표의
    (시도, 시군구) 목록과 안쪽 결합(inner join)해 걷어 낸다.
  - 표마다 이름 표기가 다르다: "통합청주시"/"청주시", "통합창원시"/"창원시", "제주 제주시"/"제주시",
    "수원시(계)"/"수원시", 면적 표의 시도는 약칭("서울", "경기", "전북특별자치도"는 "전북")이다.

실행:
  VIRTUAL_ENV= uv run --project ~/default-uv-env --with requests python -X utf8 code/ch09_fetch_mcp.py
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd
import requests

URL = "https://kosismcp2026.vercel.app/api/mcp"
HEAD = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_mcp"
RAW.mkdir(exist_ok=True)
OUT = ROOT / "data" / "sigungu_mcp_2023.csv"
OUT_TFR13 = ROOT / "data" / "sigungu_mcp_tfr_2013.csv"

# (라벨, 통계표 설명, kosis_get_data 인자)
CALLS = [
    ("주민등록인구", "주민등록인구(시도/시/군/구) 행정안전부", {"orgId": "101", "tblId": "DT_1YL20651E", "itmId": "ALL", "objL1": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("고령인구비율", "고령인구비율(시도/시/군/구) e-지방지표", {"orgId": "101", "tblId": "DT_1YL20631", "itmId": "T10", "objL1": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("인구증가율", "인구증가율(시도/시/군/구) e-지방지표", {"orgId": "101", "tblId": "DT_1YL20621", "itmId": "ALL", "objL1": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("합계출산율", "시군구/출생아수 합계출산율 인구동향조사", {"orgId": "101", "tblId": "DT_1B81A23", "itmId": "ALL", "objL1": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("면적", "행정구역별·지목별 국토이용현황_시군구 지적통계(국토교통부)", {"orgId": "116", "tblId": "DT_MLTM_2300", "itmId": "13103874596T1", "objL1": "ALL", "objL2": "ALL", "objL3": "13102874596C.0001", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    # 부양비 표는 항목 6개 x 구분 2개 x 지역 329개라 한 번에 받으면 응답이 잘린다. 구분 01(총인구)로 한정하고 항목을 하나씩 받는다
    ("부양비_유소년부양비", "주요 인구지표 시군구 인구총조사: 유소년부양비", {"orgId": "101", "tblId": "DT_1IN2030", "itmId": "T2", "objL1": "01", "objL2": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("부양비_노년부양비", "주요 인구지표 시군구 인구총조사: 노년부양비", {"orgId": "101", "tblId": "DT_1IN2030", "itmId": "T3", "objL1": "01", "objL2": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("부양비_노령화지수", "주요 인구지표 시군구 인구총조사: 노령화지수", {"orgId": "101", "tblId": "DT_1IN2030", "itmId": "T4", "objL1": "01", "objL2": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("부양비_중위연령", "주요 인구지표 시군구 인구총조사: 중위연령", {"orgId": "101", "tblId": "DT_1IN2030", "itmId": "T5", "objL1": "01", "objL2": "ALL", "prdSe": "Y", "startPrdDe": "2023", "endPrdDe": "2023"}),
    ("합계출산율2013", "시군구/출생아수 합계출산율 인구동향조사 (2013)", {"orgId": "101", "tblId": "DT_1B81A23", "itmId": "T2", "objL1": "ALL", "prdSe": "Y", "startPrdDe": "2013", "endPrdDe": "2013"}),
]

SIDO_FULL = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시",
             "세종특별자치시", "경기도", "강원특별자치도", "강원도", "충청북도", "충청남도", "전북특별자치도",
             "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"]
SIDO_SHORT = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
              "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종",
              "경기도": "경기", "강원특별자치도": "강원", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
              "전북특별자치도": "전북", "전라북도": "전북", "전라남도": "전남", "경상북도": "경북",
              "경상남도": "경남", "제주특별자치도": "제주"}
RENAME = {"통합청주시": "청주시", "통합창원시": "창원시", "제주 제주시": "제주시", "제주 서귀포시": "서귀포시"}


def rpc(payload, tries=3):
    for i in range(tries):
        try:
            r = requests.post(URL, headers=HEAD, json=payload, timeout=240)
            r.raise_for_status()
            break
        except requests.exceptions.RequestException as e:  # 서버가 느릴 때 같은 요청을 다시 보낸다
            if i == tries - 1:
                raise
            print(f"  재시도 {i + 1}: {type(e).__name__}")
    for line in r.content.decode("utf-8").splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return None


def mcp_call(name, args):
    rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "textbook", "version": "0"}}})
    res = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": args}})
    return "\n".join(c["text"] for c in res["result"]["content"] if c.get("type") == "text")


def parse_table(text):
    rows, header = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if len(cells) == len(header):
            rows.append(cells)
    return pd.DataFrame(rows, columns=header)


def fetch_all():
    frames = {}
    for label, _desc, args in CALLS:
        path = RAW / f"mcp_{label}_{args['tblId']}_{args['startPrdDe']}.csv"
        if path.exists() and "--refresh" not in sys.argv:
            frames[label] = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
            print(f"{label}: 저장된 응답 사용 ({len(frames[label])}행)")
            continue
        text = mcp_call("kosis_get_data", args)
        if "잘렸습니다" in text:
            raise SystemExit(f"{label}: 응답이 잘렸다. 조건을 나눠 조회할 것")
        df = parse_table(text)
        m = re.search(r"\((\d+)건\)", text)
        print(f"{label}: 응답 {m.group(1) if m else '?'}건, 표 {len(df)}행 -> {path.name}")
        df.to_csv(path, index=False, encoding="utf-8-sig")
        (RAW / f"mcp_{label}_응답원문.md").write_text(text, encoding="utf-8")
        frames[label] = df
    return frames


def fill_sido(df, name_col="분류1"):
    """시도 행을 만나면 그 뒤 행의 시도 열에 채운다. 시도 행 자체와 전국 행은 뺀다."""
    out, cur = [], None
    for _, row in df.iterrows():
        name = row[name_col]
        if name == "전국":
            continue
        if name in SIDO_FULL:
            cur = SIDO_SHORT[name]
            if name == "세종특별자치시":  # 세종은 시도이면서 유일한 시군구
                out.append({"시도": "세종", "시군구": "세종특별자치시", **row.drop(name_col).to_dict()})
            continue
        if name == "세종시":
            continue
        out.append({"시도": cur, "시군구": RENAME.get(name, name), **row.drop(name_col).to_dict()})
    return pd.DataFrame(out)


def build(frames):
    # 1) 주민등록인구: 항목 계만
    pop = frames["주민등록인구"]
    pop = fill_sido(pop[pop["항목"] == "계"])
    pop = pop.rename(columns={"값": "총인구"})[["시도", "시군구", "총인구"]]
    # 2) 고령인구비율
    old = fill_sido(frames["고령인구비율"]).rename(columns={"값": "고령인구비율"})[["시도", "시군구", "고령인구비율"]]
    # 3) 인구증가율: 항목 중 인구증가율 행만
    grw = frames["인구증가율"]
    grw = fill_sido(grw[grw["항목"].str.startswith("인구증가율")]).rename(columns={"값": "인구증가율"})[["시도", "시군구", "인구증가율"]]
    # 4) 합계출산율·출생아수 (일반구 포함, 뒤의 안쪽 결합으로 걷어 낸다)
    tfr = frames["합계출산율"]
    tfr = fill_sido(tfr).pivot_table(index=["시도", "시군구"], columns="항목", values="값", aggfunc="first").reset_index()
    tfr = tfr.rename(columns={"합계출산율": "합계출산율", "출생아수": "출생아수"})
    # 5) 면적: 분류1(시도 약칭) + 분류2(시군구). "수원시(계)" -> 수원시, 일반구는 결합에서 빠진다
    area = frames["면적"].copy()
    area = area[(area["분류1"] != "전국") & (area["분류2"] != "합계")]
    area["시군구"] = area["분류2"].str.replace(r"\(계\)$", "", regex=True)
    # 시도 합계 행("서울 | 서울") 제거. 세종은 "세종특별자치시 | 세종특별자치시" 한 행이 곧 시군구 값이므로 남긴다
    area = area[(area["시군구"] != area["분류1"]) | (area["분류1"] == "세종특별자치시")]
    area["시도"] = area["분류1"].map(lambda s: SIDO_SHORT.get(s, s))
    area.loc[area["시도"] == "세종", "시군구"] = "세종특별자치시"  # "세종특별자치시 | 세종특별자치시" 행
    area["면적"] = pd.to_numeric(area["값"], errors="coerce") / 1_000_000  # m² -> km²
    area = area[["시도", "시군구", "면적"]].drop_duplicates(["시도", "시군구"])
    # 6) 부양비·노령화지수·중위연령 (항목별로 받은 네 표를 합친다. 지역 열 이름은 응답에 따라 분류1 또는 분류2)
    parts = []
    for label in ["부양비_유소년부양비", "부양비_노년부양비", "부양비_노령화지수", "부양비_중위연령"]:
        d = frames[label].copy()
        reg = "분류2" if "분류2" in d.columns else "분류1"
        d = fill_sido(d[[reg, "값"]], name_col=reg).rename(columns={"값": label.split("_")[1]})
        parts.append(d)
    dep = parts[0]
    for d in parts[1:]:
        dep = dep.merge(d, on=["시도", "시군구"], how="outer")

    # 주민등록인구와 고령인구비율은 2023년 시군구 229개가 같다. 인구증가율은 2023년 7월 경북에서 대구로 편입된
    # 군위군의 증가율 행이 없으므로(당해년은 대구, 전년은 경북에 있음) 왼쪽 결합으로 결측을 남긴다
    df = pop.merge(old, on=["시도", "시군구"], how="inner").merge(grw, on=["시도", "시군구"], how="left")
    n_core = len(df)
    df = df.merge(tfr, on=["시도", "시군구"], how="left").merge(area, on=["시도", "시군구"], how="left")
    df = df.merge(dep, on=["시도", "시군구"], how="left")
    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["인구밀도"] = df["총인구"] / df["면적"]
    df["수도권"] = df["시도"].isin(["서울", "인천", "경기"]).map({True: "수도권", False: "비수도권"})
    df = df[["시도", "시군구", "총인구", "면적", "인구밀도", "인구증가율", "고령인구비율", "유소년부양비",
             "노년부양비", "노령화지수", "중위연령", "합계출산율", "출생아수", "수도권"]]
    print(f"결합: e-지방지표 공통 {n_core}행 -> 최종 {len(df)}행, 결측: "
          + ", ".join(f"{c} {int(df[c].isna().sum())}" for c in df.columns if df[c].isna().any()) )
    return df


def build_tfr13(frames):
    t = fill_sido(frames["합계출산율2013"]).rename(columns={"값": "합계출산율_2013"})
    t["합계출산율_2013"] = pd.to_numeric(t["합계출산율_2013"], errors="coerce")
    return t[["시도", "시군구", "합계출산율_2013"]]


if __name__ == "__main__":
    frames = fetch_all()
    df = build(frames)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"저장 {OUT.relative_to(ROOT)} ({len(df)}행 x {df.shape[1]}열)")
    t13 = build_tfr13(frames)
    t13.to_csv(OUT_TFR13, index=False, encoding="utf-8-sig")
    print(f"저장 {OUT_TFR13.relative_to(ROOT)} ({len(t13)}행)")
