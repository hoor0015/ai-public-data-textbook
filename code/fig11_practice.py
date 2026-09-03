# 11주차 2회차 실습 그림 (실제 데이터)
# 그림 11-5 불용어 1차/2차 실행의 최빈 단어 대조, 그림 11-6 상위 단어의 세 가지 셈법,
# 그림 11-7 토큰 빈도 순위와 문서 빈도 순위, 그림 11-8 키워드 규칙 개정 전후
# 데이터: data/minwon_cases_2021.csv (공정거래위원회 소비자 민원 상담 사례 567건)
# 실행: cd "$HOME/default-uv-env" && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

from sklearn.feature_extraction.text import CountVectorizer  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

# ---- 전처리 규칙 (ch11_practice.py, ch10_text.py와 동일) ---------------------
JOSA = sorted(
    ["으로부터", "에서부터", "에게서", "으로써", "으로는", "으로도", "이라고",
     "라고", "에서는", "에서도", "까지", "부터", "에서", "에게", "한테", "으로",
     "이라", "라는", "이나", "하고", "와의", "과의", "은", "는", "이", "가",
     "을", "를", "에", "의", "도", "와", "과", "로", "만", "요"],
    key=len, reverse=True,
)
PREDICATE = re.compile(
    r"(습니다|입니다|합니다|니다|세요|어요|아요|해요|한다|았다|었다|였다|"
    r"하여|해서|하고|하는|하던|되어|되는|하지|되지|있는|없는|같은|위해|"
    r"대한|따라|통해|관한|드립니다|바랍니다|는지|은지|다고|다는|는데)$"
)
STOP_1 = {
    "저는", "제가", "저의", "저희", "우리", "그런데", "그리고", "그러나",
    "하지만", "그래서", "또한", "및", "등", "때문", "경우", "정도", "관련",
    "여부", "이후", "당시", "현재", "다시", "함께", "가장", "매우", "일부",
    "모두", "다른", "어떤", "무엇", "어떻게", "생각", "내용", "사실",
    "하나", "지금", "동안", "상태", "상황", "문제", "가능", "필요",
}
ADDED = {
    "받을", "받은", "받고", "받아", "않아", "않고", "있을", "있을까",
    "할까", "원을", "만원", "개월", "이었", "되었", "됩니", "합니",
    "이런", "그런", "저런", "어떠한",
}
STOP_2 = STOP_1 | ADDED


def make_tokenizer(stopwords):
    def tokenize(text):
        text = re.sub(r"[^가-힣\s]", " ", str(text))
        tokens = []
        for w in text.split():
            for j in JOSA:
                if w.endswith(j) and len(w) - len(j) >= 2:
                    w = w[: -len(j)]
                    break
            if len(w) < 2 or w in stopwords or PREDICATE.search(w):
                continue
            tokens.append(w)
        return tokens
    return tokenize


df = pd.read_csv(BASE / "data" / "minwon_cases_2021.csv", on_bad_lines="skip")
df.columns = ["사건번호", "제목", "내용", "답변"]
df = df.dropna(subset=["제목", "내용"]).reset_index(drop=True)
docs = (df["제목"] + " " + df["내용"]).tolist()


def word_freq(stopwords):
    cv = CountVectorizer(analyzer=make_tokenizer(stopwords))
    dtm = cv.fit_transform(docs)
    freq = pd.Series(dtm.sum(axis=0).A1, index=cv.get_feature_names_out())
    return freq.sort_values(ascending=False)


freq1 = word_freq(STOP_1)
freq2 = word_freq(STOP_2)

# ---------------------------------------------------------------- 그림 11-5
# 불용어 1차 실행과 2차 실행의 최빈 단어 상위 15개. 1차에서 불용어로 추가된 토큰은 회색
N = 15
fig, axes = plt.subplots(1, 2, figsize=(11, 6), sharex=True)
for ax, freq, title in zip(axes, [freq1, freq2],
                           ["1차 실행 (기본 불용어만)", "2차 실행 (동사 조각·단위 추가 제거)"]):
    top = freq.head(N)[::-1]
    colors = ["#b0b0b0" if w in ADDED else "#5b8ac4" for w in top.index]
    ax.barh(top.index, top.values, color=colors)
    for i, v in enumerate(top.values):
        ax.text(v + 2, i, str(v), va="center", fontsize=9, color="#333")
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("등장 횟수 (토큰 빈도, 567건 합계)")
    ax.tick_params(axis="y", labelsize=10)
axes[0].text(0.98, 0.02, "회색: 2차에서 불용어로 추가한 토큰", transform=axes[0].transAxes,
             ha="right", va="bottom", fontsize=9, color="#555")
fig.suptitle("불용어 사전을 한 번 다듬기 전후의 최빈 단어 상위 15개", fontsize=13)
sns.despine(left=True)
fig.tight_layout()
fig.savefig(FIG / "fig11_stopword_iter.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 11-6
# 상위 5개 단어와 '요구'의 세 가지 셈법: 토큰 빈도, 문자열 등장 횟수, 포함 문서 수
words = list(freq2.head(5).index) + ["요구"]
token = [int(freq2[w]) for w in words]
string = [sum(d.count(w) for d in docs) for w in words]
docn = [sum(1 for d in docs if w in d) for w in words]

x = np.arange(len(words))
width = 0.27
fig, ax = plt.subplots(figsize=(9.5, 5.5))
bars = [
    ax.bar(x - width, token, width, label="토큰 빈도 (전처리 후 세기)", color="#5b8ac4"),
    ax.bar(x, string, width, label="문자열 등장 횟수 (원문에서 글자 검색)", color="#c47f5b"),
    ax.bar(x + width, docn, width, label="포함 문서 수 (그 단어가 든 민원 건수)", color="#6aa56a"),
]
for group in bars:
    for b in group:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 4, str(int(b.get_height())),
                ha="center", va="bottom", fontsize=8.5, color="#333")
ax.set_xticks(x)
ax.set_xticklabels(words, fontsize=11)
ax.set_ylabel("횟수 또는 건수")
ax.set_ylim(0, max(string) * 1.15)
ax.set_title("같은 단어, 세 가지 셈법: 토큰 빈도 상위 5개 단어와 '요구'", fontsize=13)
ax.legend(loc="upper right", fontsize=9, frameon=False)
sns.despine()
fig.tight_layout()
fig.savefig(FIG / "fig11_count_methods.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 11-7
# 토큰 빈도 상위 15개 단어가 문서 빈도(그 토큰이 든 민원 건수)로는 몇 위인지 잇는 그림
cv2 = CountVectorizer(analyzer=make_tokenizer(STOP_2))
dtm2 = cv2.fit_transform(docs)
vocab2 = cv2.get_feature_names_out()
tokfreq = pd.Series(np.asarray(dtm2.sum(axis=0)).ravel(), index=vocab2).sort_values(ascending=False)
docfreq = pd.Series(np.asarray((dtm2 > 0).sum(axis=0)).ravel(), index=vocab2)
rank_tok = {w: i + 1 for i, w in enumerate(tokfreq.index)}
rank_doc = {w: i + 1 for i, w in enumerate(docfreq.sort_values(ascending=False).index)}
top15 = list(tokfreq.head(15).index)

fig, ax = plt.subplots(figsize=(8.5, 7.5))
for w in top15:
    r1, r2 = rank_tok[w], rank_doc[w]
    color = "#c47f5b" if r2 > r1 else ("#5b8ac4" if r2 < r1 else "#999999")
    ax.plot([0, 1], [r1, r2], color=color, lw=1.8, marker="o", ms=5, alpha=0.9)
    ax.text(-0.04, r1, f"{w} {int(tokfreq[w])}회", ha="right", va="center", fontsize=10)
    ax.text(1.04, r2, f"{w} {int(docfreq[w])}건", ha="left", va="center", fontsize=10)
ax.set_xlim(-0.55, 1.55)
ax.set_ylim(28.5, 0.2)
ax.set_yticks([1, 5, 10, 15, 20, 25])
ax.set_yticklabels(["1위", "5위", "10위", "15위", "20위", "25위"], fontsize=9)
ax.set_xticks([0, 1])
ax.set_xticklabels(["토큰 빈도 순위", "문서 빈도 순위"], fontsize=12)
ax.grid(axis="x", visible=False)
ax.set_title("같은 단어의 두 순위: 토큰 빈도 상위 15개가 문서 빈도로는 몇 위인가", fontsize=13)
ax.text(0.5, 27.6, "주황: 문서 빈도 순위가 내려간 단어   파랑: 올라간 단어",
        ha="center", va="center", fontsize=9.5, color="#555")
sns.despine(left=True, bottom=True)
fig.tight_layout()
fig.savefig(FIG / "fig11_freq_vs_docfreq.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 11-8
# 키워드 규칙 개정 전후: 567건의 유형별 건수와 표본 30건의 일치 건수
RULES = [
    ("의료", r"^\s*\[[^\]]*(과|한방|검진|진료|의학)\]|오진|의료진|수술|진료"),
    ("보험", r"보험"),
    ("통신·인터넷", r"통신|휴대폰|핸드폰|이동전화|인터넷|요금제"),
    ("여행·운송", r"여행|항공|숙박|호텔|콘도|펜션"),
    ("자동차", r"자동차|중고차|차량|정비"),
]
RULES_REV = [
    ("의료", r"^\s*\[[^\]]*(과|한방|검진|진료|의학)\]|오진|의료진|수술|진료"),
    ("보험", r"보험"),
    ("여행·운송", r"여행|항공|숙박|호텔|콘도|펜션|택배"),
    ("통신·인터넷", r"통신|휴대폰|핸드폰|이동전화|요금제|초고속인터넷|인터넷\s*요금|인터넷\s*약정"),
    ("자동차", r"자동차|중고차|차량|정비"),
]


def classify(title, content, rules):
    text = f"{title} {content}"
    if re.search(rules[0][1], title):
        return "의료"
    for label, pat in rules:
        if re.search(pat, text):
            return label
    return "기타"


before = pd.Series([classify(t, c, RULES) for t, c in zip(df["제목"], df["내용"])])
after = pd.Series([classify(t, c, RULES_REV) for t, c in zip(df["제목"], df["내용"])])
labels = ["의료", "보험", "통신·인터넷", "여행·운송", "자동차", "기타"]
b = [int((before == l).sum()) for l in labels]
a = [int((after == l).sum()) for l in labels]

fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [2.1, 1]})
y = np.arange(len(labels))
h = 0.36
axes[0].barh(y + h / 2, b, h, label="개정 전", color="#b8c6d9")
axes[0].barh(y - h / 2, a, h, label="개정 후", color="#5b8ac4")
for i, (vb, va) in enumerate(zip(b, a)):
    axes[0].text(vb + 4, i + h / 2, str(vb), va="center", fontsize=9, color="#555")
    axes[0].text(va + 4, i - h / 2, str(va), va="center", fontsize=9, color="#333")
axes[0].set_yticks(y)
axes[0].set_yticklabels(labels, fontsize=11)
axes[0].invert_yaxis()
axes[0].set_xlabel("민원 건수 (전체 567건)")
axes[0].set_title("규칙 개정 전후의 유형별 건수", fontsize=12)
axes[0].legend(loc="upper right", fontsize=9, frameon=False)

match = [25, 29]
miss = [5, 1]
x = np.arange(2)
axes[1].bar(x, match, 0.5, label="규칙과 에이전트 일치", color="#6aa56a")
axes[1].bar(x, miss, 0.5, bottom=match, label="불일치", color="#c47f5b")
for i, (m, s) in enumerate(zip(match, miss)):
    axes[1].text(i, m / 2, f"{m}건", ha="center", va="center", fontsize=11, color="white")
    axes[1].text(i, m + s + 0.7, f"불일치 {s}건", ha="center", va="bottom", fontsize=9.5, color="#333")
axes[1].set_xticks(x)
axes[1].set_xticklabels(["개정 전", "개정 후"], fontsize=11)
axes[1].set_ylim(0, 41)
axes[1].set_ylabel("표본 30건")
axes[1].set_title("표본 30건의 일치 건수", fontsize=12)
axes[1].legend(loc="upper center", fontsize=8.5, frameon=False, ncol=1, handlelength=1.2)
sns.despine()
fig.suptitle("키워드 규칙을 기준표에 맞춰 고치면 무엇이 달라지는가", fontsize=13)
fig.tight_layout()
fig.savefig(FIG / "fig11_rule_revision.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob("fig11_*.png"))])
