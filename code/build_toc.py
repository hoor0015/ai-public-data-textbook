"""목차.md의 장 목록 부분을 장 파일(NN-S_*.md)의 h1·h2 제목에서 다시 만든다.

머리말(첫 '---' 앞)과 꼬리(## 장별 공통 형식 이후)는 손으로 쓴 글이므로 그대로 두고, 그 사이의
부·주차·절 목록만 바꿔 쓴다. 실습 장의 마지막 세 절(검증 체크리스트·자주 겪는 문제·혼자서 해 보는 실습)은
한 줄로 합쳐 적는다.
실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 code/build_toc.py
"""
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = [("1부. 에이전트와 도구 (1-5주)", [1, 2, 3, 4, 5]),
         ("2부. 공공데이터의 수집과 정리 (6-7주)", [6, 7]),
         ("3부. 분석과 해석 (9-12주)", [9, 10, 11, 12]),
         ("4부. 종합과 확장 (13-14주)", [13, 14])]
EXAMS = {8: "중간고사", 15: "기말고사"}
TAIL3 = ("검증 체크리스트", "자주 겪는 문제", "혼자서 해 보는 실습")


def chapters():
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "[0-9][0-9]-[12]_*.md"))):
        name = os.path.basename(path)
        m = re.match(r"^(\d{2})-([12])_(이론|실습|특강|통합)_", name)
        if not m:
            continue
        week, sess, kind = int(m.group(1)), int(m.group(2)), m.group(3)
        lines = io.open(path, encoding="utf-8").read().split("\n")
        title = re.sub(r"^#\s*\d+주차 \d차시\.\s*", "", lines[0].strip())
        if kind == "특강":
            title = re.sub(r"^특강\.\s*", "", title)
        secs = [re.sub(r"^##\s*", "", l).strip() for l in lines if re.match(r"^## ", l)]
        secs = [s for s in secs if s not in ("이 장에서 배우는 것", "이 실습에서 하는 것", "준비물")]
        if all(t in secs for t in TAIL3):
            secs = [s for s in secs if s not in TAIL3] + [" / ".join(TAIL3)]
        out[(week, sess)] = (kind, title, secs)
    return out


def render(ch):
    body = []
    for part, weeks in PARTS:
        body.append(f"## {part}\n")
        for w in weeks:
            for s in (1, 2):
                if (w, s) not in ch:
                    continue
                kind, title, secs = ch[(w, s)]
                body.append(f"### {w}주차 {s}차시 ({kind}): {title}")
                body.extend(secs)
                body.append("")
            if w + 1 in EXAMS:
                body.append(f"## {w + 1}주차: {EXAMS[w + 1]}\n")

    body.append("## 15주차: 기말고사\n")
    return "\n".join(body)


if __name__ == "__main__":
    p = os.path.join(ROOT, "목차.md")
    s = io.open(p, encoding="utf-8").read()
    head, rest = s.split("\n---\n", 1)
    _mid, tail = rest.split("\n---\n", 1)
    new = head + "\n---\n\n" + render(chapters()) + "\n---\n" + tail
    io.open(p, "w", encoding="utf-8", newline="").write(new)
    print("목차.md rebuilt:", len(chapters()), "chapters")
