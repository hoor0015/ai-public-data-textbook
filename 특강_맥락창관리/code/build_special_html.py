# -*- coding: utf-8 -*-
"""특강(이론과 실습을 한 장에 담은 단일 문서) Markdown을 교재 웹페이지와 같은 서식의 HTML로 빌드한다.
출력: 특강_맥락창관리/특강.html (figures/ 상대경로 유지). 사이드바에는 이 문서의 절 목록이 들어간다.
CSS는 본 교재 code/build_html.py의 CSS를 그대로 가져온다.
실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
"""
import re
from datetime import date
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SPECIAL = HERE.parent
ROOT = SPECIAL.parent
BOOK_TITLE = "AI 기반 공공데이터 분석"

src = (ROOT / "code" / "build_html.py").read_text(encoding="utf-8")
CSS = re.search(r'CSS = """(.*?)"""', src, flags=re.S).group(1)


def convert(md_text):
    html = markdown.markdown(md_text, extensions=["extra", "sane_lists"])
    used, heads = set(), []

    def add_id(m):
        inner = m.group(1)
        title = re.sub(r"<[^>]+>", "", inner).strip()
        s = re.sub(r"[^0-9A-Za-z가-힣\- ]", "", title).strip().replace(" ", "-") or "sec"
        key, i = s, 2
        while key in used:
            key = f"{s}-{i}"
            i += 1
        used.add(key)
        heads.append((title, key))
        return f'<h2 id="{key}">{inner}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", add_id, html, flags=re.S)
    html = re.sub(r"<li>\[ \]\s*", '<li style="list-style:none; margin-left:-18px;">'
                                    '<input type="checkbox"> ', html)
    return html, heads


mds = sorted(SPECIAL.glob("특강_*.md"))
assert len(mds) == 1, mds
md = mds[0]
text = md.read_text(encoding="utf-8")
title = re.sub(r"^#\s*", "", text.splitlines()[0].strip())
body, heads = convert(text)
out_name = "특강.html"

nav = [f'<h1><a href="{out_name}">{title}</a></h1><ul>',
       f'<li class="part">{BOOK_TITLE} · 특강</li>']
for t, hid in heads:
    cls = "chap" if re.match(r"^(1부|2부)\.", t) or not re.match(r"^\d\.\d", t) else "sec"
    tag = ""
    if t.startswith("1부."):
        tag = '<span class="tag t1">이론</span>'
    elif t.startswith("2부."):
        tag = '<span class="tag t2">실습</span>'
    nav.append(f'<li class="{cls}"><a href="{out_name}#{hid}">{tag}{t}</a></li>')
nav.append("</ul>")
nav_html = "\n".join(nav)

body = body.replace("</h1>", f'</h1>\n<p class="moddate">최종 수정: {date.today().isoformat()}</p>', 1)
page = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - {BOOK_TITLE}</title>
<style>{CSS}</style>
<script>try{{if(localStorage.getItem('textbook-nav')==='closed')document.documentElement.classList.add('nav-collapsed')}}catch(e){{}}</script></head>
<body>
<button class="nav-show" type="button" title="목차 펼치기">☰ 목차</button>
<nav class="sidebar"><button class="nav-hide" type="button" title="목차 접기">◀ 접기</button>{nav_html}</nav>
<main>{body}</main>
<script>
(function(){{var h=document.documentElement;
function set(c){{h.classList.toggle('nav-collapsed',c);try{{localStorage.setItem('textbook-nav',c?'closed':'open')}}catch(e){{}}}}
document.querySelector('.nav-hide').onclick=function(){{set(true)}};
document.querySelector('.nav-show').onclick=function(){{set(false)}};}})();
</script>
</body></html>"""
(SPECIAL / out_name).write_text(page, encoding="utf-8")
print("built", out_name, "sections", len(heads))
