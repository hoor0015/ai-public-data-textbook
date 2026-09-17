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
button.nav-hide, button.nav-show { cursor:pointer; font:inherit; font-size:.8rem; line-height:1;
  border:1px solid #d5d9de; border-radius:4px; background:#fff; color:#57606a; padding:5px 9px; }
button.nav-hide:hover, button.nav-show:hover { border-color:var(--accent); color:var(--accent); }
button.nav-hide { position:absolute; top:10px; right:10px; }
button.nav-show { display:none; position:fixed; top:10px; left:10px; z-index:20; }
nav.sidebar h1 { padding-right:66px; }
html.nav-collapsed nav.sidebar { display:none; }
html.nav-collapsed button.nav-show { display:inline-block; }
html.nav-collapsed main { margin-left:auto; margin-right:auto; }
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


def add_target_ids(html):
    """그림(<img alt="그림 N-x. …">)과 표 캡션(<strong>표 N-x. …)에 링크 목적지 id를 붙이고
    {"그림 N-x": id, "표 N-x": id}를 돌려준다."""
    found = {}

    def fig(m):
        key = f"그림 {m.group(2)}-{m.group(3)}"
        if key in found:
            return m.group(0)
        found[key] = f"fig-{m.group(2)}-{m.group(3)}"
        return f'<img id="{found[key]}" {m.group(1)}'

    def tbl(m):
        key = f"표 {m.group(1)}-{m.group(2)}"
        if key in found:
            return m.group(0)
        found[key] = f"tbl-{m.group(1)}-{m.group(2)}"
        return f'<p id="{found[key]}"><strong>표 {m.group(1)}-{m.group(2)}.'

    html = re.sub(r'<img ((?:[^>]*? )?alt="그림 (\d+)-(\d+)\.)', fig, html)
    html = re.sub(r"<p><strong>표 (\d+)-(\d+)\.", tbl, html)
    return html, found


# 상호참조 자동 링크: "N주차 M회차 X.Y", "M회차 X.Y", "N주차 실습", "N주차", 같은 주의 "X.Y(절)",
# 다른 쪽에 있는 "그림 N-x"·"표 N-x"를 링크로 바꾼다. 절 번호 1.x는 1회차, 2.x는 2회차다.
_UNIT = r"개|배|명|점|건|회|번|세|위|년|만|억|천|조|시간|분(?!석)|초|원|km|kg|cm|m|\s?퍼센트|\s?%|p"
_SEC = rf"[12]\.\d{{1,2}}(?![\d.%])(?!{_UNIT})"
_LIST = rf"{_SEC}절?(?:(?:,\s*|\s*·\s*|[과와]\s+){_SEC}절?)*"
XREF = re.compile(
    rf"(?<![\d\-·])(?:(?P<w>\d{{1,2}})주차(?:\s*(?P<s>[12])회차|\s*(?P<k>실습|이론))?"
    rf"|(?P<s2>[12])회차)(?P<mid>의?\s*)(?P<l>{_LIST})?"
    rf"|(?<![\d.\-])(?<!\d, )(?<!\d[와과] )(?<!폭을 )(?P<l2>{_LIST})(?!\s*/)"
    rf"|(?P<ft>(?:그림|표) \d+-\d+)(?!\d)")
SKIP_TAGS = {"a", "code", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style"}


def autolink(html, ch, secmap, targets, pages, log):
    """태그 밖 본문에서 XREF를 찾아 링크로 바꾼다. 링크·코드·제목·지시문 박스 안은 건드리지 않는다."""
    week, cur = ch["week"], ch["out"]

    def sec_links(text, w):
        def one(m):
            num = m.group(0).rstrip("절")
            hit = secmap.get((w, num))
            if not hit:
                return m.group(0)
            return f'<a href="{hit[0]}#{hit[1]}">{m.group(0)}</a>'
        return re.sub(rf"{_SEC}절?", one, text)

    def repl(m):
        if m.group("ft"):
            hit = targets.get(m.group("ft"))
            if not hit or hit[0] == cur:
                return m.group(0)
            return f'<a href="{hit[0]}#{hit[1]}">{m.group(0)}</a>'
        if m.group("l2"):
            out = sec_links(m.group("l2"), week)
            if out != m.group("l2"):
                log.append((cur, m.string[max(0, m.start() - 25):m.end() + 12].replace("\n", " ")))
            return out
        w = int(m.group("w")) if m.group("w") else week
        secs = m.group("l") or ""
        head = m.group(0)[:len(m.group(0)) - len(secs) - len(m.group("mid"))]
        sess = m.group("s") or m.group("s2") or {"이론": "1", "실습": "2"}.get(m.group("k"))
        if not sess and secs:
            sess = secs[0]
        if sess:
            href = pages.get((w, int(sess)))
        else:
            href = f"index.html#week-{w}" if (w, 1) in pages and w != week else None
        if href and href != cur:
            head = f'<a href="{href}">{head}</a>'
        return head + m.group("mid") + sec_links(secs, w)

    out, skip, box = [], 0, 0
    for tok in re.split(r"(<[^>]+>)", html):
        if tok.startswith("<"):
            name = re.match(r"</?\s*([a-zA-Z0-9]+)", tok)
            name = name.group(1).lower() if name else ""
            if name in SKIP_TAGS:
                skip += -1 if tok.startswith("</") else 1
            elif name == "div":
                if box:
                    box += -1 if tok.startswith("</") else 1
                elif "#2f8f4e" in tok:          # 지시문 박스
                    box = 1
            out.append(tok)
        elif skip > 0 or box > 0:
            out.append(tok)
        else:
            out.append(XREF.sub(repl, tok))
    return "".join(out)


REPO_URL = "https://github.com/hoor0015/ai-public-data-textbook"


def link_data(html):
    """본문의 <code>data/파일</code>을 GitHub 저장소의 그 파일로 연결한다.
    저장소에 올라가 있는(git이 추적하는) 파일만 링크하므로 학생이 실습에서 만드는 파일은 그대로 둔다."""
    from urllib.parse import quote
    try:
        out = subprocess.run(["git", "-C", ROOT, "-c", "core.quotepath=false", "ls-files", "data"],
                             capture_output=True, text=True, encoding="utf-8").stdout
    except OSError:
        return html
    tracked = set(out.split("\n"))

    def repl(m):
        path = m.group(1)
        if path in tracked:
            url = f"{REPO_URL}/blob/main/{quote(path)}"
        elif path.endswith("/") and any(x.startswith(path) for x in tracked):
            url = f"{REPO_URL}/tree/main/{quote(path.rstrip('/'))}"
        else:
            return m.group(0)
        return f'<a href="{url}" target="_blank" rel="noopener">{m.group(0)}</a>'

    return re.sub(r"<code>(data/[^<]*)</code>", repl, html)


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
<style>{CSS}</style>
<script>try{{if(localStorage.getItem('textbook-nav')==='closed')document.documentElement.classList.add('nav-collapsed')}}catch(e){{}}</script></head>
<body>
<button class="nav-show" type="button" title="목차 펼치기">☰ 목차</button>
<nav class="sidebar"><button class="nav-hide" type="button" title="목차 접기">◀ 접기</button>{nav_html}</nav>
<main>{body_html}{pager}</main>
<script>
(function(){{var h=document.documentElement;
function set(c){{h.classList.toggle('nav-collapsed',c);try{{localStorage.setItem('textbook-nav',c?'closed':'open')}}catch(e){{}}}}
document.querySelector('.nav-hide').onclick=function(){{set(true)}};
document.querySelector('.nav-show').onclick=function(){{set(false)}};}})();
</script>
</body></html>"""


chapters = find_chapters()
assert len(chapters) == 26, f"장 수가 26이 아님: {len(chapters)}"

# 1) 변환
tocs, bodies = {}, {}
for ch in chapters:
    text = open(ch["md"], encoding="utf-8").read()
    html, heads = convert(text)
    tocs[ch["out"]], bodies[ch["out"]] = heads, html

# 1-1) 상호참조 자동 링크
secmap, targets, pages, xref_log = {}, {}, {}, []
for ch in chapters:
    pages[(ch["week"], ch["sess"])] = ch["out"]
    for t, hid in tocs[ch["out"]]:
        m = re.match(r"([12]\.\d{1,2}) ", t)
        if m:
            secmap[(ch["week"], m.group(1))] = (ch["out"], hid)
    bodies[ch["out"]], found = add_target_ids(bodies[ch["out"]])
    for key, tid in found.items():
        targets.setdefault(key, (ch["out"], tid))
for ch in chapters:
    bodies[ch["out"]] = autolink(bodies[ch["out"]], ch, secmap, targets, pages, xref_log)
    bodies[ch["out"]] = link_data(bodies[ch["out"]])
if os.environ.get("XREF_REPORT"):      # 접두어 없는 절 번호("2.6에서")의 링크 목록. 수치 오인 점검용
    for cur, ctx in xref_log:
        print(f"[xref] {cur}: {ctx}")

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
    toc_html.append(f'<ul id="week-{val}">')
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
