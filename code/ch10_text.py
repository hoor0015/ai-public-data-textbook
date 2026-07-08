# 10주차 텍스트 분석: 소비자 민원 상담 사례 코퍼스
# 데이터: 공정거래위원회_소비자 민원학습데이터 모범상담 사례_20211227
#         (공공데이터포털 www.data.go.kr/data/15098335/fileData.do, 로그인 없이 내려받음)
# 실행: cd "$HOME/default-uv-env" && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
#
# 한국어 형태소 분석기 없이, 간단한 규칙(조사 떼기 + 불용어 제거)만으로
# 토큰화한다. 완벽하지 않지만 방법의 원리를 배우기에는 충분하다.

import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "minwon_cases_2021.csv"

# ---------------------------------------------------------------- 1. 데이터 읽기
# 원본 CSV에는 형식이 어긋난 행이 3건 있다(현실 데이터의 흔한 모습, 7주차 참조).
# 열이 더 많은 1건은 건너뛰고, 답변 열이 빠진 2건은 제목·내용이 있어 그대로 쓴다.
df = pd.read_csv(DATA, on_bad_lines="skip")
df.columns = ["사건번호", "제목", "내용", "답변"]
df = df.dropna(subset=["제목", "내용"]).reset_index(drop=True)
print(f"민원 사례 수: {len(df)}건")
print(f"내용 길이(글자): 최소 {df['내용'].str.len().min()}, "
      f"중앙값 {df['내용'].str.len().median():.0f}, 최대 {df['내용'].str.len().max()}")

# ---------------------------------------------------------------- 2. 간단한 토큰화
# (1) 한글이 아닌 글자는 공백으로 바꾸고 공백으로 자른다
# (2) 단어 끝의 흔한 조사를 뗀다 (긴 조사부터 시도)
# (3) 두 글자 미만, 불용어, 서술어 꼴(-습니다 등)은 버린다
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
    # 첫 실행 후 최빈 단어를 눈으로 확인하고 추가한 것들 (서술어 조각, 단위)
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


# ---------------------------------------------------------------- 3. 문서-단어 행렬과 최빈 단어
docs = (df["제목"] + " " + df["내용"]).tolist()
cv = CountVectorizer(analyzer=tokenize)
dtm = cv.fit_transform(docs)
print(f"\n문서-단어 행렬: {dtm.shape[0]}행(문서) x {dtm.shape[1]}열(단어)")

freq = pd.Series(dtm.sum(axis=0).A1, index=cv.get_feature_names_out())
print("\n[전체 최빈 단어 20개]")
print(freq.sort_values(ascending=False).head(20).to_string())

# ---------------------------------------------------------------- 4. 규칙(키워드) 분류
# 우선순위: 의료 -> 보험 -> 통신·인터넷 -> 여행·운송 -> 자동차 -> 기타
RULES = [
    ("의료", r"^\s*\[[^\]]*(과|한방|검진|진료|의학)\]|오진|의료진|수술|진료"),
    ("보험", r"보험"),
    ("통신·인터넷", r"통신|휴대폰|핸드폰|이동전화|인터넷|요금제"),
    ("여행·운송", r"여행|항공|숙박|호텔|콘도|펜션"),
    ("자동차", r"자동차|중고차|차량|정비"),
]


def classify(title, content):
    text = f"{title} {content}"
    if re.search(RULES[0][1], title):        # 의료는 제목의 [진료과] 표시 우선
        return "의료"
    for label, pat in RULES:
        if re.search(pat, text):
            return label
    return "기타"


df["유형_규칙"] = [classify(t, c) for t, c in zip(df["제목"], df["내용"])]
print("\n[규칙 분류 결과]")
print(df["유형_규칙"].value_counts().to_string())

# ---------------------------------------------------------------- 5. 유형별 특징어 (TF-IDF)
# 유형별로 문서를 이어 붙여 "유형 문서" 6편을 만들고 TF-IDF를 계산한다
grouped = df.groupby("유형_규칙")["내용"].apply(lambda s: " ".join(s.astype(str)))
tv = TfidfVectorizer(analyzer=tokenize)
tfidf = tv.fit_transform(grouped.tolist())
terms = tv.get_feature_names_out()
print("\n[유형별 TF-IDF 상위 특징어 5개]")
for i, label in enumerate(grouped.index):
    row = pd.Series(tfidf[i].toarray().ravel(), index=terms)
    top = row.sort_values(ascending=False).head(5)
    print(f"{label}: {', '.join(top.index)}")

# ---------------------------------------------------------------- 6. 유형 문서 간 코사인 유사도
# 유형별로 이어 붙인 문서 6편이 서로 얼마나 닮았는지 잰다
sim = cosine_similarity(tfidf)
print("\n[유형 문서 간 코사인 유사도]")
print(pd.DataFrame(sim, index=grouped.index, columns=grouped.index).round(2).to_string())

# ---------------------------------------------------------------- 7. 교차검증용 표본 추출
# 에이전트 직접 분류와 규칙 분류를 비교할 표본 30건 (재현 가능하도록 시드 고정)
sample30 = df.sample(30, random_state=10).sort_index()
out = BASE / "data" / "minwon_sample30.csv"
sample30[["사건번호", "제목", "내용", "유형_규칙"]].to_csv(out, index=False, encoding="utf-8-sig")
print(f"\n교차검증 표본 30건 저장: {out.name}")
print(sample30["유형_규칙"].value_counts().to_string())
