# -*- coding: utf-8 -*-
# 5주차 2회차 실습 보강분 수치 계산 스크립트
# (1) 2.3절 재현성 실험표: 결측 처리 방식 세 가지가 내는 값, 스크립트 3회 실행의 동일성
# (2) 2.3절 스크립트 깨뜨리기: 시끄러운 실패(예외)와 조용한 실패(문턱 변경)
# (3) 2.6절 오류 심기 세 유형: 값 삭제, 열 이름 변경, 천 단위 쉼표
# 사본은 모두 code/ch05_out/ 에만 만든다. data/ 의 원본은 건드리지 않는다.
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch05_practice import profile  # noqa: E402  (2.3절 profile.py 원형)

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "ch05_out"
OUT.mkdir(exist_ok=True)
os.chdir(ROOT)

sig = Path("data/sigungu_2023.csv")
inc = Path("data/income_dist.csv")
df = pd.read_csv(sig, encoding="utf-8-sig")


def show(title, text):
    print(f"===== {title} =====")
    print(text)
    print()


# ---------------------------------------------------------------- (1) 재현성
print("== 표: 결측 처리 방식에 따라 갈리는 값 (sigungu_2023.csv) ==")
dropped = df.dropna()
filled = df.fillna(0)
rows = [
    ("열마다 결측 제외 (스크립트)", len(df), f"{df['총인구'].mean():,.1f}",
     f"{df['합계출산율'].mean():.3f} ({df['합계출산율'].count()}개)",
     f"{df['고령인구비율'].mean():.3f}"),
    ("dropna()로 행 삭제", len(dropped), f"{dropped['총인구'].mean():,.1f}",
     f"{dropped['합계출산율'].mean():.3f} ({dropped['합계출산율'].count()}개)",
     f"{dropped['고령인구비율'].mean():.3f}"),
    ("fillna(0)으로 0 채움", len(filled), f"{filled['총인구'].mean():,.1f}",
     f"{filled['합계출산율'].mean():.3f} ({filled['합계출산율'].count()}개)",
     f"{filled['고령인구비율'].mean():.3f}"),
]
for r in rows:
    print(" | ".join(str(v) for v in r))
print(f"dropna와 결측 제외의 총인구 평균 차이: "
      f"{dropped['총인구'].mean() - df['총인구'].mean():,.1f}")
print()

runs = [profile(sig, "간단") for _ in range(3)]
print("== 스크립트 3회 실행 ==")
print("세 번 모두 동일:", runs[0] == runs[1] == runs[2], "/ 출력 문자 수:", len(runs[0]))
runs_d = [profile(sig, "상세") for _ in range(3)]
print("상세 모드 3회 모두 동일:", runs_d[0] == runs_d[1] == runs_d[2],
      "/ 출력 문자 수:", len(runs_d[0]))
print()

# ---------------------------------------------------------------- (2) 스크립트 깨뜨리기
broken_py = OUT / "profile_broken.py"
broken_py.write_text(
    "import sys\n"
    "from pathlib import Path\n"
    "import pandas as pd\n"
    "sys.stdout.reconfigure(encoding='utf-8')\n"
    "path = Path(sys.argv[1])\n"
    "df = pdd.read_csv(path, encoding='utf-8-sig')\n"   # pd 오타
    "print(len(df))\n",
    encoding="utf-8")
p = subprocess.run([sys.executable, str(broken_py), str(sig)],
                   capture_output=True, text=True, encoding="utf-8")
show("시끄러운 실패 (이름 오타 pdd)", p.stderr.strip())


def profile_threshold(path, mode, threshold):
    """경고 문턱만 바꾼 profile(). 조용한 실패를 보이기 위한 변형."""
    d = pd.read_csv(path, encoding="utf-8-sig")
    warns = [f"- 결측 비율 {threshold}% 이상: {c} ({r:.1f}%)"
             for c, r in (d.isna().mean() * 100).items() if r >= threshold]
    return warns or ["- (해당 없음)"]


bpath = OUT / "income_dist_결측실험.csv"
if not bpath.exists():
    b = pd.read_csv(inc, encoding="utf-8-sig")
    b.loc[b["연도"].isin([2013, 2015, 2017, 2019, 2021]), "지니계수"] = pd.NA
    b.to_csv(bpath, index=False, encoding="utf-8-sig")
show("조용한 실패 (문턱 30 -> 60)",
     "문턱 30: " + "; ".join(profile_threshold(bpath, "간단", 30)) + "\n"
     + "문턱 60: " + "; ".join(profile_threshold(bpath, "간단", 60)))

# ---------------------------------------------------------------- (3) 오류 심기 세 유형
# 유형 B: 열 이름 변경 (합계출산율 -> 출산율)
b_path = OUT / "sigungu_열이름실험.csv"
df.rename(columns={"합계출산율": "출산율"}).to_csv(b_path, index=False, encoding="utf-8-sig")
txt_b = profile(b_path, "간단")
show("유형 B 열 이름 변경 (간단)", txt_b)

# 유형 C: 천 단위 쉼표 (총인구를 문자열로)
c_path = OUT / "sigungu_쉼표실험.csv"
dc = df.copy()
dc["총인구"] = dc["총인구"].map(lambda v: f"{v:,.0f}")
dc.to_csv(c_path, index=False, encoding="utf-8-sig")
dcc = pd.read_csv(c_path, encoding="utf-8-sig")
print("쉼표 사본을 다시 읽은 총인구 자료형:", dcc["총인구"].dtype,
      "/ 첫 값:", repr(dcc["총인구"].iloc[0]))
txt_c = profile(c_path, "상세")
show("유형 C 천 단위 쉼표 (상세)", txt_c)
print("상세 표에 총인구가 있는가:", "| 총인구 |" in txt_c.split("## 3.")[1].split("## 4.")[0])
print("쉼표 사본의 수치형 열 수:", dcc.select_dtypes("number").shape[1],
      "/ 원본의 수치형 열 수:", df.select_dtypes("number").shape[1])
