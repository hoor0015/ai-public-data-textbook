# -*- coding: utf-8 -*-
"""26개 장 Markdown을 Kwangwoon University 강의 교재 웹사이트(HTML)로 빌드.
통계학입문책 code/build_html.py를 계승, 4부·13주 구조로 확장.
출력: 교재 루트의 index.html, w01-1.html - w13-2.html
(figures/ 상대경로가 그대로 작동하도록 루트에 출력)
실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<교재>/code/build_html.py"
"""
import os
import re
import glob
import subprocess
from datetime import date

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_TITLE = "AI 기반 공공데이터 분석"
BOOK_SUBTITLE = "VSCode와 Claude Code로 배우는 공공데이터 분석"

PARTS = [
    ("1부. 에이전트와 도구", [1, 2, 3, 4, 5]),
    ("2부. 공공데이터의 수집과 정리", [6, 7]),
    ("3부. 분석과 해석", [9, 10, 11, 12]),
    ("4부. 종합과 확장", [13, 14]),
]

EXAMS = {8: "중간고사", 15: "기말고사"}


def display_units():
    """부 제목·시험 주차·콘텐츠 주차를 화면 순서대로 나열."""
    emitted = set()
    for part_title, weeks in PARTS:
        for ex in sorted(EXAMS):
            if ex not in emitted and ex < weeks[0]:
                emitted.add(ex)
                yield ("exam", ex)
        yield ("part", part_title)
        for w in weeks:
            for ex in sorted(EXAMS):
                if ex not in emitted and ex < w:
                    emitted.add(ex)
                    yield ("exam", ex)
            yield ("week", w)
    for ex in sorted(EXAMS):
        if ex not in emitted:
            yield ("exam", ex)


CSS = """
:root { --accent:#2f6fb0; --sidebar-w:320px; }
* { box-sizing:border-box; }
body { margin:0; font-family:'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif;
       color:#1f2328; line-height:1.75; background:#fff; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
nav.sidebar { position:fixed; top:0; left:0; bottom:0; width:var(--sidebar-w);
  overflow-y:auto; background:#f7f8fa; border-right:1px solid #e3e6ea; padding:22px 18px; }
nav.sidebar h1 { font-size:1.02rem; line-height:1.45; margin:0 0 14px;
  padding-bottom:12px; border-bottom:2px solid var(--accent); }
nav.sidebar h1 a { color:#1f2328; }
nav.sidebar ul { list-style:none; margin:0; padding:0; }
nav.sidebar li.part { margin-top:14px; font-weight:700; font-size:.92rem; color:#57606a; }
nav.sidebar li.chap { margin:4px 0 0 6px; font-size:.88rem; font-weight:600; }
nav.sidebar li.sec { margin:2px 0 2px 20px; font-size:.83rem; font-weight:400; }
nav.sidebar li.cur > a { color:#a33; }
nav.sidebar .tag { display:inline-block; font-size:.72rem; font-weight:700; border-radius:3px;
  padding:0 5px; margin-right:5px; vertical-align:1px; }
nav.sidebar .t1 { background:#e7eefc; color:#2f6fb0; }
nav.sidebar .t2 { background:#e6f4ea; color:#2f8f4e; }
main { margin-left:var(--sidebar-w); padding:36px 48px 80px; max-width:880px; }
main h1 { font-size:1.7rem; border-bottom:3px solid var(--accent); padding-bottom:10px; }
main h2 { font-size:1.32rem; margin-top:2.4em; border-bottom:1px solid #e3e6ea; padding-bottom:6px; }
main h3 { font-size:1.12rem; margin-top:1.8em; }
main h4 { font-size:1.0rem; margin-top:1.5em; }
main img { max-width:100%; display:block; margin:20px auto; border:1px solid #eceef0; border-radius:4px; }
main table { border-collapse:collapse; margin:18px 0; font-size:.92rem; }
main th, main td { border:1px solid #d5d9de; padding:6px 12px; }
main th { background:#f0f3f6; }
main code { background:#f2f3f5; padding:1px 5px; border-radius:3px; font-size:.9em; }
main pre { background:#f6f8fa; border:1px solid #e3e6ea; border-radius:6px;
  padding:14px 16px; overflow-x:auto; line-height:1.5; }
p.moddate { color:#7a828a; font-size:.85rem; margin:-6px 0 22px; }
span.moddate-inline { color:#8a929a; font-size:.8rem; font-weight:400; margin-left:6px; }
div.update-notice { border:1px solid #d9d9e3; border-left:5px solid #5b6ee1; background:#f7f7fc;
  padding:12px 16px; margin:18px 0; border-radius:4px; font-size:.95rem; }
main pre code { background:none; padding:0; }
main blockquote { margin:18px 0; padding:8px 18px; border-left:4px solid #c8ccd2;
  background:#fafbfc; color:#4b5563; }
main input[type=checkbox] { margin-right:6px; }
nav.sidebar li.exam { margin-top:12px; margin-left:6px; font-size:.88rem;
  font-weight:700; color:#a33; }
.toc-exam { margin-top:24px; font-size:1.05rem; font-weight:700; color:#a33; }
.pager { display:flex; justify-content:space-between; margin-top:56px;
  padding-top:18px; border-top:1px solid #e3e6ea; font-size:.95rem; }
.pager a { max-width:46%; }
.toc-part { margin-top:26px; font-size:1.1rem; }
@media (max-width: 900px) {
  nav.sidebar { position:static; width:auto; border-right:none; border-bottom:1px solid #e3e6ea; }
  main { margin-left:0; padding:24px 20px 60px; }
}
"""


def mod_date(md_path):
    """장 md 파일의 최종 수정일(YYYY-MM-DD).
    커밋되지 않은 변경이 있으면 오늘(빌드일), 아니면 마지막 커밋일. git이 없으면 파일 mtime."""
    rel = os.path.relpath(md_path, ROOT)
    try:
        dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", rel],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            return date.today().isoformat()
        out = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%cs", "--", rel],
                             capture_output=True, text=True).stdout.strip()
        if out:
            return out
    except OSError:
        pass
    return date.fromtimestamp(os.path.getmtime(md_path)).isoformat()


def find_chapters():
    """NN-S_*.md 파일을 (주차, 회차) 순으로 수집하고 h1 제목을 뽑는다."""
    chapters = []
    for path in sorted(glob.glob(os.path.join(ROOT, "[0-9][0-9]-[12]_*.md"))):
        name = os.path.basename(path)
        m = re.match(r"^(\d{2})-([12])_", name)
        if not m:
            continue
        week, sess = int(m.group(1)), int(m.group(2))
        first = open(path, encoding="utf-8").readline().strip()
        title = re.sub(r"^#\s*", "", first)                      # "N주차 N회차. 제목"
        short = re.sub(r"^\d+주차 \d회차\.\s*", "", title)        # "제목"
        chapters.append({
            "week": week, "sess": sess, "md": path,
            "out": f"w{week:02d}-{sess}.html",
            "title": title, "short": short, "date": mod_date(path),
        })
    return chapters


def slugify(text, used):
    s = re.sub(r"[^0-9A-Za-z가-힣\- ]", "", text).strip().replace(" ", "-")
    base = s or "sec"
    key, i = base, 2
    while key in used:
        key = f"{base}-{i}"
        i += 1
    used.add(key)
    return key


def convert(md_text):
    """md -> html. h2에 id를 붙이고 (제목, id) 목록을 돌려준다."""
    html = markdown.markdown(md_text, extensions=["extra", "sane_lists"])
    used, heads = set(), []

    def add_id(m):
        inner = m.group(1)
        title = re.sub(r"<[^>]+>", "", inner).strip()
        hid = slugify(title, used)
        heads.append((title, hid))
        return f'<h2 id="{hid}">{inner}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", add_id, html, flags=re.S)
    # 체크리스트: "- [ ] 항목" -> 체크박스
    html = re.sub(r"<li>\[ \]\s*", '<li style="list-style:none; margin-left:-18px;">'
                                    '<input type="checkbox"> ', html)
    return html, heads


def sidebar(chapters, tocs, current):
    by_week = {}
    for ch in chapters:
        by_week.setdefault(ch["week"], []).append(ch)
    items = [f'<h1><a href="index.html">{BOOK_TITLE}</a></h1><ul>']
    for kind_, val in display_units():
        if kind_ == "part":
            items.append(f'<li class="part">{val}</li>')
            continue
        if kind_ == "exam":
            items.append(f'<li class="exam">{val}주차 · {EXAMS[val]}</li>')
            continue
        for ch in by_week.get(val, []):
            tag = ('<span class="tag t1">이론</span>' if ch["sess"] == 1
                   else '<span class="tag t2">실습</span>')
            cur = ' cur' if ch["out"] == current else ''
            items.append(f'<li class="chap{cur}"><a href="{ch["out"]}">'
                         f'{tag}{ch["week"]}주차 {ch["short"]}</a></li>')
            if ch["out"] == current:
                for t, hid in tocs[ch["out"]]:
                    items.append(f'<li class="sec"><a href="{ch["out"]}#{hid}">{t}</a></li>')
    items.append("</ul>")
    return "\n".join(items)


def page(title, body_html, nav_html, prev_l, next_l):
    pager = '<div class="pager"><span>{}</span><span>{}</span></div>'.format(
        f'<a href="{prev_l[0]}">← {prev_l[1]}</a>' if prev_l else "",
        f'<a href="{next_l[0]}">{next_l[1]} →</a>' if next_l else "")
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - {BOOK_TITLE}</title>
<style>{CSS}</style></head>
<body>
<nav class="sidebar">{nav_html}</nav>
<main>{body_html}{pager}</main>
</body></html>"""


chapters = find_chapters()
assert len(chapters) == 26, f"장 수가 26이 아님: {len(chapters)}"

# 1) 변환
tocs, bodies = {}, {}
for ch in chapters:
    text = open(ch["md"], encoding="utf-8").read()
    html, heads = convert(text)
    tocs[ch["out"]], bodies[ch["out"]] = heads, html

# 2) 장 페이지
for i, ch in enumerate(chapters):
    prev_l = ((chapters[i - 1]["out"], chapters[i - 1]["title"]) if i > 0
              else ("index.html", "목차"))
    next_l = ((chapters[i + 1]["out"], chapters[i + 1]["title"])
              if i < len(chapters) - 1 else None)
    body = bodies[ch["out"]].replace(
        "</h1>",
        f'</h1>\n<p class="moddate">최종 수정: {ch["date"]} · '
        '이 교재는 학기 중에도 계속 업데이트됩니다</p>', 1)
    out = page(ch["title"], body,
               sidebar(chapters, tocs, ch["out"]), prev_l, next_l)
    open(os.path.join(ROOT, ch["out"]), "w", encoding="utf-8").write(out)
print(f"built {len(chapters)} chapter pages")

# 3) index
toc_html = [
    f"<h1>{BOOK_TITLE}</h1>",
    f"<p><strong>{BOOK_SUBTITLE}.</strong> "
    "AI 에이전트를 활용해 한국 공공데이터를 분석하는 학부 수준의 강의 교재입니다. "
    "13개 주차가 각각 이론(1회차)과 실습(2회차)으로 나뉘며, "
    "학생의 역할은 코딩이 아니라 에이전트에 대한 지시, 결과의 검증, 정책적 해석입니다. "
    "모든 그림과 수치는 실제 공공데이터(KOSIS, 공공데이터포털 등)에서 코드로 생성했습니다.</p>",
    "<p>광운대학교 행정학과 조교수 김경동(kdkim@kw.ac.kr)</p>",
    '<div class="update-notice"><strong>업데이트 안내</strong><br>'
    "이 교재는 완성 후 멈춘 책이 아니라 학기 중에도 계속 업데이트되는 살아 있는 문서입니다. "
    "각 장 제목 아래와 아래 목차의 날짜가 그 장의 최종 수정일이니, "
    "수업 전에 자신이 읽은 판이 최신인지 확인해 주세요.</div>",
]
by_week = {}
for ch in chapters:
    by_week.setdefault(ch["week"], []).append(ch)
for kind_, val in display_units():
    if kind_ == "part":
        toc_html.append(f'<h2 class="toc-part">{val}</h2>')
        continue
    if kind_ == "exam":
        toc_html.append(f'<p class="toc-exam">{val}주차 · {EXAMS[val]}</p>')
        continue
    toc_html.append("<ul>")
    for ch in by_week.get(val, []):
        kind = "이론" if ch["sess"] == 1 else "실습"
        label = f'{ch["week"]}주차 {ch["sess"]}회차 ({kind}) · {ch["short"]}' 
        toc_html.append(
            f'<li style="margin-top:10px"><strong><a href="{ch["out"]}">'
            f'{label}</a></strong>'
            f'<span class="moddate-inline">{ch["date"]} 수정</span><ul>')
        for t, hid in tocs[ch["out"]]:
            toc_html.append(f'<li><a href="{ch["out"]}#{hid}">{t}</a></li>')
        toc_html.append("</ul></li>")
    toc_html.append("</ul>")
out = page("목차", "\n".join(toc_html), sidebar(chapters, tocs, None),
           None, (chapters[0]["out"], chapters[0]["title"]))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
print("built index.html")
