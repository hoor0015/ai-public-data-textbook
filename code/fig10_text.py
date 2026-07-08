# 10주차 데이터 그림: 소비자 민원 상담 사례 코퍼스 (실제 데이터)
# 그림 10-2 핵심어 빈도, 그림 10-3 유형별 TF-IDF 특징어, 그림 10-4 유형 문서 간 유사도
# 데이터: 공정거래위원회_소비자 민원학습데이터 모범상담 사례_20211227 (공공데이터포털 15098335)
# 실행: cd "$HOME/default-uv-env" && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

# ---- 전처리 규칙 (ch10_text.py와 동일) ----------------------------------
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
STOPWORDS = {
    "저는", "제가", "저의", "저희", "우리", "그런데", "그리고", "그러나",
    "하지만", "그래서", "또한", "및", "등", "때문", "경우", "정도", "관련",
    "여부", "이후", "당시", "현재", "다시", "함께", "가장", "매우", "일부",
    "모두", "다른", "어떤", "무엇", "어떻게", "생각", "내용", "사실",
    "하나", "지금", "동안", "상태", "상황", "문제", "가능", "필요",
    "받을", "받은", "받고", "받아", "않아", "않고", "있을", "있을까",
    "할까", "원을", "만원", "개월", "이었", "되었", "됩니", "합니",
    "이런", "그런", "저런", "어떠한",
}


def tokenize(text):
    text = re.sub(r"[^가-힣\s]", " ", str(text))
    tokens = []
    for w in text.split():
        for j in JOSA:
            if w.endswith(j) and len(w) - len(j) >= 2:
                w = w[: -len(j)]
                break
        if len(w) < 2 or w in STOPWORDS or PREDICATE.search(w):
            continue
        tokens.append(w)
    return tokens


RULES = [
    ("의료", r"^\s*\[[^\]]*(과|한방|검진|진료|의학)\]|오진|의료진|수술|진료"),
    ("보험", r"보험"),
    ("통신·인터넷", r"통신|휴대폰|핸드폰|이동전화|인터넷|요금제"),
    ("여행·운송", r"여행|항공|숙박|호텔|콘도|펜션"),
    ("자동차", r"자동차|중고차|차량|정비"),
]


def classify(title, content):
    text = f"{title} {content}"
    if re.search(RULES[0][1], title):
        return "의료"
    for label, pat in RULES:
        if re.search(pat, text):
            return label
    return "기타"


# ---- 데이터 ---------------------------------------------------------------
df = pd.read_csv(BASE / "data" / "minwon_cases_2021.csv", on_bad_lines="skip")
df.columns = ["사건번호", "제목", "내용", "답변"]
df = df.dropna(subset=["제목", "내용"]).reset_index(drop=True)
docs = (df["제목"] + " " + df["내용"]).tolist()
df["유형_규칙"] = [classify(t, c) for t, c in zip(df["제목"], df["내용"])]

# ---------------------------------------------------------------- 그림 10-2
# 핵심어 빈도 상위 20개 막대그래프
cv = CountVectorizer(analyzer=tokenize)
dtm = cv.fit_transform(docs)
freq = pd.Series(dtm.sum(axis=0).A1, index=cv.get_feature_names_out())
top20 = freq.sort_values(ascending=False).head(20)

fig, ax = plt.subplots(figsize=(8.5, 6.5))
sns.barplot(x=top20.values, y=top20.index, color="#5b8ac4", ax=ax)
ax.set_xlabel("등장 횟수 (전체 567건 합계)")
ax.set_ylabel("")
ax.set_title("소비자 민원 상담 사례의 핵심어 상위 20개", fontsize=13)
for i, v in enumerate(top20.values):
    ax.text(v + 2, i, str(v), va="center", fontsize=9, color="#333")
sns.despine(left=True)
fig.tight_layout()
fig.savefig(FIG / "fig10_freq.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 10-3
# 유형별 TF-IDF 특징어 (6개 유형 문서)
grouped = df.groupby("유형_규칙")["내용"].apply(lambda s: " ".join(s.astype(str)))
order = ["의료", "보험", "통신·인터넷", "여행·운송", "자동차", "기타"]
grouped = grouped.reindex(order)
tv = TfidfVectorizer(analyzer=tokenize)
tfidf = tv.fit_transform(grouped.tolist())
terms = tv.get_feature_names_out()

n_docs = df["유형_규칙"].value_counts()
fig, axes = plt.subplots(2, 3, figsize=(11.5, 6.5))
palette = ["#5b8ac4", "#c47f5b", "#6aa56a", "#9a7fb8", "#b8697a", "#8a8a8a"]
for i, (label, ax) in enumerate(zip(order, axes.ravel())):
    row = pd.Series(tfidf[i].toarray().ravel(), index=terms)
    top = row.sort_values(ascending=False).head(5)[::-1]
    ax.barh(top.index, top.values, color=palette[i])
    ax.set_title(f"{label} ({n_docs[label]}건)", fontsize=11)
    ax.set_xlabel("TF-IDF" if i >= 3 else "")
    ax.tick_params(labelsize=10)
fig.suptitle("민원 유형별 TF-IDF 상위 특징어 5개 (유형별로 이어 붙인 문서 기준)",
             fontsize=13, y=1.00)
fig.tight_layout()
fig.savefig(FIG / "fig10_tfidf.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 10-4
# 유형 문서 간 코사인 유사도 히트맵
sim = cosine_similarity(tfidf)
fig, ax = plt.subplots(figsize=(7.2, 5.8))
sns.heatmap(pd.DataFrame(sim, index=order, columns=order),
            annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=1,
            cbar_kws={"label": "코사인 유사도"}, ax=ax)
ax.set_title("민원 유형 문서 간 코사인 유사도", fontsize=13)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
plt.setp(ax.get_yticklabels(), rotation=0)
fig.tight_layout()
fig.savefig(FIG / "fig10_similarity.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob("fig10_*.png"))])
