# -*- coding: utf-8 -*-
"""근거 메모의 문서 인용을 원문 파일에서 다시 찾아 대조한다.

12주차 2회차 evidence-memo 스킬의 scripts/cite_check.py 참고 구현.
실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일>" <근거메모.md> <문서폴더>

메모의 "문서 근거" 절에서 다음 형식의 줄을 찾는다.
    - [파일명 제N조 제M항] 「원문 그대로」
각 인용에 대해 <문서폴더>/<파일명> 을 열어
  (1) 조문 제목 "제N조(" 가 파일에 있는지,
  (2) 인용문이 원문과 글자 단위로 일치하는지 (공백과 줄바꿈만 무시)
를 보고한다. 항 번호(제M항)와 해석의 타당성은 사람이 확인한다.
불일치가 하나라도 있으면 종료 코드 1로 끝난다.
"""
import io
import os
import re
import sys

PAT = re.compile(
    r"^\s*- \[(?P<file>[^\s\]]+)\s+(?P<art>제\d+조[^\]]*)\]\s*「(?P<quote>.+?)」",
    re.M | re.S,
)


def squeeze(s):
    return re.sub(r"\s+", "", s)


def load_doc(path):
    """공백을 뺀 전체 문자열과, 각 글자가 원본 몇 번째 줄인지의 목록을 돌려준다."""
    chars, line_of = [], []
    with io.open(path, encoding="utf-8-sig") as f:
        for n, line in enumerate(f, 1):
            for ch in line:
                if not ch.isspace():
                    chars.append(ch)
                    line_of.append(n)
    return "".join(chars), line_of


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    memo_path, docs = sys.argv[1], sys.argv[2]
    memo = io.open(memo_path, encoding="utf-8-sig").read()
    items = list(PAT.finditer(memo))
    if not items:
        print("인용 줄을 찾지 못했다. '- [파일명 제N조] 「원문」' 형식인지 확인할 것")
        sys.exit(1)
    n_bad = 0
    cache = {}
    for i, m in enumerate(items, 1):
        fname, art, quote = m.group("file"), m.group("art").strip(), m.group("quote")
        path = os.path.join(docs, fname)
        head = f"[{i}] {fname} {art}"
        if not os.path.exists(path):
            print(f"{head} | 파일 없음: {path}")
            n_bad += 1
            continue
        if path not in cache:
            cache[path] = load_doc(path)
        text, line_of = cache[path]
        jo = re.match(r"제\d+조(의\d+)?", art).group(0)
        k = text.find(jo + "(")
        jo_msg = f"조문 있음 ({line_of[k]}번째 줄)" if k >= 0 else "조문 없음"
        j = text.find(squeeze(quote))
        if j >= 0:
            q_msg = f"인용 일치 ({line_of[j]}번째 줄)"
        else:
            q_msg = "인용 불일치: 원문에서 이 문장을 찾을 수 없음"
        if k < 0 or j < 0:
            n_bad += 1
        print(f"{head} | {jo_msg} | {q_msg}")
    print(f"요약: 인용 {len(items)}건 중 일치 {len(items) - n_bad}건, 불일치 {n_bad}건. "
          "항 번호(제○항)와 해석의 타당성은 사람이 확인한다.")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
