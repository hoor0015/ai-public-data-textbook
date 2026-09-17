# 11주차 2회차 실습 확장 단계의 계산 코드
# 데이터: data/minwon_cases_2021.csv (공정거래위원회 소비자 민원 상담 사례 567건),
#         data/minwon_sample30.csv (교차검증 표본 30건, ch10_text.py가 시드 10으로 추출)
# 실행: cd "$HOME/default-uv-env" && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
#
# 이 파일이 계산하는 것 (본문의 절 번호)
#   2.2-2.3 불용어 1차/2차 실행의 최빈 단어 대조, 토큰화 예시
#   2.5     상위 단어의 세 가지 셈법(토큰 빈도, 문자열 등장, 포함 문서 수)과 유형별 분포
#   2.6     토큰 빈도 상위 15개의 문서 빈도·순위 이동·건당 평균, 문자열 기준과의 차이
#   2.7     규칙 분류에서 "인터넷" 키워드가 끌어온 건수, 정보 부족 사례 수
#   2.8     규칙 분류 vs 에이전트 직접 분류(기준표를 주고 1회)의 집계,
#           표본 30건 안의 정보 부족 사례(근거구절을 채울 수 없는 건)
#   2.9     유형별 상위 10개 단어와 유형 간 겹치는 단어
#   2.11    키워드 규칙 개정(인터넷 제거, 택배 추가) 전후의 건수와 유형 이동,
#           시드를 바꿔 새로 뽑은 표본 30건의 구성
#   2.12    기계적 경계 후보 신호(약한 근거, 경합, 정보부족)와 검증 우선순위 상위 20건,
#           표본 30건에서 그 표시와 실제 불일치가 겹치는 정도
#   2.13    유형별 대표 민원(유형 중심 벡터와 코사인 유사도가 가장 높은 문서)
# 전처리 규칙과 키워드 규칙은 ch10_text.py와 동일하다.

import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "minwon_cases_2021.csv"
SAMPLE = BASE / "data" / "minwon_sample30.csv"

# ---------------------------------------------------------------- 전처리 규칙
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
# 1차 실행: 처음부터 넣어 둔 기본 불용어
STOP_1 = {
    "저는", "제가", "저의", "저희", "우리", "그런데", "그리고", "그러나",
    "하지만", "그래서", "또한", "및", "등", "때문", "경우", "정도", "관련",
    "여부", "이후", "당시", "현재", "다시", "함께", "가장", "매우", "일부",
    "모두", "다른", "어떤", "무엇", "어떻게", "생각", "내용", "사실",
    "하나", "지금", "동안", "상태", "상황", "문제", "가능", "필요",
}
# 2차 실행: 1차 결과의 최빈 단어를 눈으로 보고 추가한 것 (서술어 조각, 단위, 지시어)
STOP_2 = STOP_1 | {
    "받을", "받은", "받고", "받아", "않아", "않고", "있을", "있을까",
    "할까", "원을", "만원", "개월", "이었", "되었", "됩니", "합니",
    "이런", "그런", "저런", "어떠한",
}


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


# ---------------------------------------------------------------- 데이터 읽기
df = pd.read_csv(DATA, on_bad_lines="skip")
df.columns = ["사건번호", "제목", "내용", "답변"]
df = df.dropna(subset=["제목", "내용"]).reset_index(drop=True)
docs = (df["제목"] + " " + df["내용"]).tolist()
print(f"민원 사례 수: {len(df)}건, 사건번호 고유값 {df['사건번호'].nunique()}개")


def word_freq(stopwords):
    cv = CountVectorizer(analyzer=make_tokenizer(stopwords))
    dtm = cv.fit_transform(docs)
    freq = pd.Series(dtm.sum(axis=0).A1, index=cv.get_feature_names_out())
    return freq.sort_values(ascending=False), dtm.shape


# 2.2 토큰화 예시 (본문에 싣는 한 문장. 첫 민원 내용에서 그대로 가져온 문장이다)
SENT = ("보험 회사는 과거 간경화로 치료 받은 사실이 있었는데도 보험을 청약할 때 "
        "고지하지 않았으므로 고지의무 위반이라며 사망 보험금을 제외한 "
        "암진단 급여금(1천만원)과 이미 납입한 보험료만 환급해 주었습니다.")
print("\n[2.2 토큰화 예시]")
print("원문:", SENT)
print("1차 토큰:", " / ".join(make_tokenizer(STOP_1)(SENT)))
print("2차 토큰:", " / ".join(make_tokenizer(STOP_2)(SENT)))


# ---------------------------------------------------------------- 2.2-2.3 불용어 반복
freq1, shape1 = word_freq(STOP_1)
freq2, shape2 = word_freq(STOP_2)
print(f"\n[1차 실행] 행렬 {shape1[0]}행 x {shape1[1]}열")
print(freq1.head(20).to_string())
print(f"\n[2차 실행] 행렬 {shape2[0]}행 x {shape2[1]}열")
print(freq2.head(20).to_string())
compare = pd.DataFrame({
    "1차 단어": freq1.head(10).index, "1차 횟수": freq1.head(10).values,
    "2차 단어": freq2.head(10).index, "2차 횟수": freq2.head(10).values,
})
print("\n[상위 10개 대조표]")
print(compare.to_string(index=False))
add = STOP_2 - STOP_1
cv1 = CountVectorizer(analyzer=make_tokenizer(STOP_1))
cv1.fit(docs)
vocab1 = set(cv1.get_feature_names_out())
print(f"추가 불용어 {len(add)}개 중 1차 어휘에 없던 것:",
      sorted(w for w in add if w not in vocab1))

# ------------------------------------------------- 2.6 토큰 빈도와 문서 빈도
cv2 = CountVectorizer(analyzer=make_tokenizer(STOP_2))
dtm2 = cv2.fit_transform(docs)
vocab2 = cv2.get_feature_names_out()
tokfreq = pd.Series(np.asarray(dtm2.sum(axis=0)).ravel(), index=vocab2).sort_values(ascending=False)
docfreq = pd.Series(np.asarray((dtm2 > 0).sum(axis=0)).ravel(), index=vocab2)
rank_tok = {w: i + 1 for i, w in enumerate(tokfreq.index)}
rank_doc = {w: i + 1 for i, w in enumerate(docfreq.sort_values(ascending=False).index)}
rows6 = [(w, int(tokfreq[w]), rank_tok[w], int(docfreq[w]),
          round(docfreq[w] / len(docs) * 100, 1), rank_doc[w],
          rank_tok[w] - rank_doc[w], round(tokfreq[w] / docfreq[w], 2))
         for w in tokfreq.head(15).index]
print("\n[2.6 토큰 빈도 상위 15개의 문서 빈도]")
print(pd.DataFrame(rows6, columns=["단어", "토큰빈도", "빈도순위", "문서수", "문서비율",
                                   "문서순위", "순위이동", "건당평균"]).to_string(index=False))
# 표 11-5(문자열 기준 포함 문서 수)와 표 11-6(토큰 기준 문서 빈도)의 차이
col = list(vocab2).index("환급")
tok_docs = set(np.where(np.asarray(dtm2[:, col].todense()).ravel() > 0)[0])
str_docs = {i for i, d in enumerate(docs) if "환급" in d}
gap = Counter()
tk2 = make_tokenizer(STOP_2)
for i in sorted(str_docs - tok_docs):
    for w in tk2(docs[i]):
        if "환급" in w:
            gap[w] += 1
print(f"'환급' 문자열 포함 {len(str_docs)}건, 토큰 포함 {len(tok_docs)}건, "
      f"차이 {len(str_docs - tok_docs)}건. 그 문서들의 환급 관련 토큰: {gap.most_common(10)}")
yogu = docfreq[[w for w in vocab2 if w.startswith("요구")]].sort_values(ascending=False)
print(f"'요구' 문자열 포함 {sum(1 for d in docs if '요구' in d)}건, "
      f"토큰별 문서 수: {yogu.head(5).to_dict()}")

# ---------------------------------------------------------------- 2.5 세 가지 셈법
print("\n[상위 5개 단어 + '요구'의 세 가지 셈법]")
rows = []
for w in list(freq2.head(5).index) + ["요구"]:
    s_cnt = sum(d.count(w) for d in docs)          # 문자열 등장 횟수
    d_cnt = sum(1 for d in docs if w in d)         # 포함 문서 수
    rows.append((w, int(freq2[w]), s_cnt, d_cnt, round(d_cnt / len(docs) * 100, 1)))
methods = pd.DataFrame(rows, columns=["단어", "토큰 빈도", "문자열 등장", "포함 문서", "문서 비율(%)"])
print(methods.to_string(index=False))
print("포함 문서 수 기준 순위:", ", ".join(methods.sort_values("포함 문서", ascending=False)["단어"]))

# ---------------------------------------------------------------- 규칙 분류 (ch10_text.py와 동일)
RULES = [
    ("의료", r"^\s*\[[^\]]*(과|한방|검진|진료|의학)\]|오진|의료진|수술|진료"),
    ("보험", r"보험"),
    ("통신·인터넷", r"통신|휴대폰|핸드폰|이동전화|인터넷|요금제"),
    ("여행·운송", r"여행|항공|숙박|호텔|콘도|펜션"),
    ("자동차", r"자동차|중고차|차량|정비"),
]


def classify(title, content, rules=RULES):
    text = f"{title} {content}"
    if re.search(rules[0][1], title):
        return "의료"
    for label, pat in rules:
        if re.search(pat, text):
            return label
    return "기타"


df["유형_규칙"] = [classify(t, c) for t, c in zip(df["제목"], df["내용"])]
print("\n[규칙 분류 건수]")
print(df["유형_규칙"].value_counts().to_string())

# 환급 포함 문서의 유형별 비율 (2.5 "주요 불만" 단정 검증)
full = df["제목"] + " " + df["내용"]
has_hwan = full.str.contains("환급")
ratio = (df[has_hwan]["유형_규칙"].value_counts() / df["유형_규칙"].value_counts() * 100).round(1)
print(f"\n'환급' 포함 문서 {int(has_hwan.sum())}건, 유형별 포함 비율(%):")
print(ratio.sort_values(ascending=False).to_string())

# ---------------------------------------------------------------- 2.7 기준표 설계 근거
tel = df[df["유형_규칙"] == "통신·인터넷"]
tel_text = tel["제목"] + " " + tel["내용"]
only_internet = tel_text.apply(
    lambda s: bool(re.search("인터넷", s)) and not re.search(r"통신|휴대폰|핸드폰|이동전화|요금제", s))
service = tel_text.apply(lambda s: bool(re.search(
    r"초고속|인터넷\s*서비스|인터넷\s*요금|인터넷\s*가입|인터넷\s*약정|인터넷\s*해지|인터넷\s*설치|인터넷\s*회선", s)))
print(f"\n통신·인터넷 규칙 {len(tel)}건 중 '인터넷' 한 단어로만 걸린 건 {int(only_internet.sum())}건, "
      f"그중 통신 서비스 표현(초고속, 인터넷 요금·가입·약정 등)이 있는 건 {int((only_internet & service).sum())}건")
RULES_NO_INTERNET = [(l, p.replace("|인터넷", "")) if l == "통신·인터넷" else (l, p) for l, p in RULES]
df["유형_규칙_인터넷제외"] = [classify(t, c, RULES_NO_INTERNET) for t, c in zip(df["제목"], df["내용"])]
print("'인터넷' 키워드를 뺀 규칙의 건수:", df["유형_규칙_인터넷제외"].value_counts().to_dict())
short = df[df["내용"].str.strip().isin(["첨부파일 참조"]) | (df["내용"].str.strip() == df["제목"].str.strip())]
print(f"내용이 '첨부파일 참조'이거나 제목과 같은 정보 부족 사례 {len(short)}건, "
      f"그중 규칙 분류가 기타로 보낸 건 {(short['유형_규칙'] == '기타').sum()}건")
print(f"'택배' 포함 문서 {int(full.str.contains('택배').sum())}건")

# ---------------------------------------------------------------- 2.9 유형별 상위 10개 단어
LABELS = ["의료", "보험", "통신·인터넷", "여행·운송", "자동차", "기타"]
per_type = {}
for label in LABELS:
    idx = df.index[df["유형_규칙"] == label]
    cvt = CountVectorizer(analyzer=make_tokenizer(STOP_2))
    mt = cvt.fit_transform([docs[i] for i in idx])
    per_type[label] = pd.Series(np.asarray(mt.sum(axis=0)).ravel(),
                                index=cvt.get_feature_names_out()).sort_values(ascending=False)
print("\n[2.9 유형별 상위 10개 단어 (유형 안에서만 센 토큰 빈도)]")
print(pd.DataFrame({f"{l} ({int((df['유형_규칙'] == l).sum())}건)":
                    [f"{w} {int(v)}" for w, v in per_type[l].head(10).items()]
                    for l in ["의료", "보험", "통신·인터넷", "기타"]}).to_string())
for a, b in [("의료", "보험"), ("통신·인터넷", "기타")]:
    both = sorted(set(per_type[a].head(10).index) & set(per_type[b].head(10).index))
    print(f"{a} 상위10 과 {b} 상위10 의 겹치는 단어 {len(both)}개: {both}")
overall10 = set(freq2.head(10).index)
for label in LABELS:
    print(f"  {label}: 상위10 중 전체 상위10과 겹치는 단어 "
          f"{len(set(per_type[label].head(10).index) & overall10)}개")

# ---------------------------------------------------------------- 2.8 규칙 vs 에이전트 직접 분류
# 에이전트 직접 분류는 저자가 Claude Code에게 눈가림 표본(유형_규칙 열을 뺀 30건)과
# 2.7의 분류 기준표를 함께 주고 새 대화에서 한 번 실행한 결과를 옮겨 적은 것이다.
# 근거 열에는 적용한 기준표 규칙과 민원 내용 본문에서 그대로 옮긴 구절을 적게 했고,
# 비고는 경계 / 정보부족 / 해당없음 세 가지다.
AGENT = {
    1000509527: "보험", 1000506058: "의료", 1000509134: "보험", 1000514847: "보험",
    1002909748: "기타", 1000909776: "의료", 1000926143: "기타", 1001359846: "기타",
    1001360312: "기타", 1001360120: "기타", 1001518580: "기타", 1001911777: "보험",
    1001912410: "의료", 1001901173: "자동차", 1001899140: "기타", 1001905113: "기타",
    1001902733: "기타", 1001908313: "기타", 1001904880: "기타", 1002061755: "여행·운송",
    1002543997: "기타", 1003097124: "기타", 1003088380: "통신·인터넷", 1003087655: "기타",
    1003096476: "기타", 1003098459: "여행·운송", 1003097896: "기타", 1003093891: "기타",
    1003102174: "기타", 1003059458: "의료",
}
FLAG_B = {  # 기준표 실행의 비고. 적지 않은 건은 "해당없음"
    1000509134: "경계", 1000514847: "경계", 1002909748: "경계", 1001359846: "경계",
    1001518580: "경계", 1002061755: "경계", 1002543997: "경계", 1003093891: "경계",
    1001904880: "정보부족", 1003059458: "정보부족",
}

sample = pd.read_csv(SAMPLE)
assert set(sample["사건번호"]) == set(AGENT), "표본 30건의 사건번호와 에이전트 결과의 사건번호가 다르다"
assert set(df.sample(30, random_state=10)["사건번호"]) == set(sample["사건번호"]), "시드 10 재추출 불일치"
sample["에이전트"] = sample["사건번호"].map(AGENT)
sample["비고(기준표)"] = sample["사건번호"].map(FLAG_B).fillna("해당없음")
sample["일치"] = np.where(sample["유형_규칙"] == sample["에이전트"], "일치", "불일치")
print("\n[표본 30건: 규칙 vs 에이전트]")
print(f"일치 {(sample['일치'] == '일치').sum()}건 / 30건 "
      f"({(sample['일치'] == '일치').mean() * 100:.0f}%)")
print("  에이전트 분류의 유형 분포:", sample["에이전트"].value_counts().to_dict())
print("  기준표 실행의 비고:", sample["비고(기준표)"].value_counts().to_dict())
print("\n교차표 (행: 규칙, 열: 에이전트)")
print(pd.crosstab(sample["유형_규칙"], sample["에이전트"]).to_string())
print("\n불일치 건:")
print(sample.loc[sample["일치"] == "불일치", ["사건번호", "유형_규칙", "에이전트", "제목"]].to_string(index=False))
# 근거구절을 채울 수 없는 건: 내용이 "첨부파일 참조"이거나 제목과 같은 건
thin_sample = sample[sample["사건번호"].isin(short["사건번호"])]
print(f"\n표본 30건 중 근거구절을 내용에서 뽑을 수 없는 건 {len(thin_sample)}건 "
      f"(제대로 실행되면 인용확인 열의 '내용 없음'이 이만큼 나와야 한다):")
for _, r in thin_sample.iterrows():
    src = df.loc[df["사건번호"] == r["사건번호"]].iloc[0]
    print(f"  {r['사건번호']} | {src['제목']} | 내용: {src['내용'].strip()[:40]}")

# ---------------------------------------------------------------- 2.11 규칙 개정 실험
# 기준표에 덧붙인 경계 규칙 세 줄을 키워드 규칙에 반영한 것.
#   (1) 통신·인터넷에서 "인터넷"을 빼고 통신 서비스 표현만 남긴다
#   (2) 여행·운송에 "택배"를 넣고 통신·인터넷보다 먼저 적용한다
#   (3) 정보부족 표시는 규칙이 아니라 비고로 다루므로 여기서는 건드리지 않는다
RULES_REV = [
    ("의료", r"^\s*\[[^\]]*(과|한방|검진|진료|의학)\]|오진|의료진|수술|진료"),
    ("보험", r"보험"),
    ("여행·운송", r"여행|항공|숙박|호텔|콘도|펜션|택배"),
    ("통신·인터넷", r"통신|휴대폰|핸드폰|이동전화|요금제|초고속인터넷|인터넷\s*요금|인터넷\s*약정"),
    ("자동차", r"자동차|중고차|차량|정비"),
]
df["유형_개정"] = [classify(t, c, RULES_REV) for t, c in zip(df["제목"], df["내용"])]
print("\n[2.11 규칙 개정 전후]")
print(pd.DataFrame({"개정 전": df["유형_규칙"].value_counts(),
                    "개정 후": df["유형_개정"].value_counts()}).loc[LABELS].to_string())
print("유형이 바뀐 민원:", int((df["유형_규칙"] != df["유형_개정"]).sum()), "건")
print(pd.crosstab(df["유형_규칙"], df["유형_개정"]).to_string())
sample["규칙_개정"] = sample["사건번호"].map(dict(zip(df["사건번호"], df["유형_개정"])))
# 2.10에서 원문을 읽은 불일치 5건이 개정 규칙에서 어떻게 되었는지 (점수가 아니라 진단)
print("\n2.10에서 읽은 불일치 5건의 개정 후 유형:")
print(sample.loc[sample["일치"] == "불일치",
                 ["사건번호", "유형_규칙", "규칙_개정", "에이전트", "제목"]].to_string(index=False))
# 개정이 새로 만든 오류: 택배가 지나가듯 나와 여행·운송으로 옮겨 간 건
moved = df[(df["유형_규칙"] != df["유형_개정"]) & (df["유형_개정"] == "여행·운송")]
print(f"\n여행·운송으로 옮겨 간 {len(moved)}건의 제목:")
for t in moved["제목"]:
    print("  -", t[:60])
# 개정 뒤에도 남은 오류: "통신판매"의 통신에 걸린 전자상거래 분쟁
tel_rev = df[df["유형_개정"] == "통신·인터넷"]
tel_rev_text = tel_rev["제목"] + " " + tel_rev["내용"]
still = ~tel_rev_text.str.contains(r"휴대폰|핸드폰|이동전화|요금제|초고속인터넷|인터넷\s*요금|"
                                   r"인터넷\s*약정|통신사|통신서비스|통신요금|통화")
print(f"\n개정 후 통신·인터넷 {len(tel_rev)}건 중 통신 서비스 표현 없이 "
      f"'통신판매' 등으로만 걸린 건 {int(still.sum())}건:")
for t in tel_rev.loc[still.values, "제목"]:
    print("  -", t[:60])

# ------------------------------------------- 2.11 시드를 바꿔 새로 뽑은 표본 30건
# 고칠 때 본 표본에서 잰 성과는 증거가 약하다. 개정 규칙은 보지 않았던 표본에서 확인한다.
NEW_SEED = 23
new30 = df.sample(30, random_state=NEW_SEED).sort_index()
print(f"\n[2.11 새 표본 30건 (시드 {NEW_SEED})]")
print("첫 표본(시드 10)과 겹치는 건:",
      len(set(new30["사건번호"]) & set(sample["사건번호"])), "건")
print("개정 규칙의 유형 분포:", new30["유형_개정"].value_counts().to_dict())
moved_new = new30[new30["유형_규칙"] != new30["유형_개정"]]
print(f"이 표본에서 개정으로 유형이 바뀐 건 {len(moved_new)}건:")
print(moved_new[["사건번호", "유형_규칙", "유형_개정", "제목"]].to_string(index=False))

# ------------------------------------- 2.12 기계적 경계 후보와 검증 우선순위 목록
# 규칙 분류 하나만 돌리고도 "먼저 읽을 건"을 고를 수 있는가. 세 가지 기계적 신호를 쓴다.
#   s1 약한 근거: 유형을 결정한 키워드가 제목+내용 전체에서 한 번만 나왔다
#                (제목의 [진료과] 표시로 걸린 건은 구조적 표시이므로 제외)
#   s2 경합    : 둘 이상 유형의 키워드에 동시에 걸렸다
#   s3 정보부족 : 내용이 "첨부파일 참조"이거나 제목과 같다
MED_TAG = r"^\s*\[[^\]]*(과|한방|검진|진료|의학)\]"


def decide(title, content, rules=RULES):
    """규칙이 배정한 유형, 그 근거 키워드의 등장 횟수, [진료과] 표시로 걸렸는지."""
    text = f"{title} {content}"
    if re.search(rules[0][1], title):
        return "의료", len(re.findall(rules[0][1], text)), bool(re.search(MED_TAG, title))
    for label, pat in rules:
        if re.search(pat, text):
            return label, len(re.findall(pat, text)), False
    return "기타", 0, False


def hit_count(title, content, rules=RULES):
    """이 민원이 몇 개 유형의 키워드에 걸리는지."""
    text = f"{title} {content}"
    got = {"의료"} if re.search(rules[0][1], title) else set()
    for label, pat in rules:
        if re.search(pat, text):
            got.add(label)
    return len(got)


dec = [decide(t, c) for t, c in zip(df["제목"], df["내용"])]
df["근거횟수"] = [d[1] for d in dec]
df["진료과표시"] = [d[2] for d in dec]
df["걸린유형수"] = [hit_count(t, c) for t, c in zip(df["제목"], df["내용"])]
df["약한근거"] = (df["유형_규칙"] != "기타") & (df["근거횟수"] <= 1) & (~df["진료과표시"])
df["경합"] = df["걸린유형수"] >= 2
df["정보부족"] = df["사건번호"].isin(short["사건번호"])
df["우선순위점수"] = df[["약한근거", "경합", "정보부족"]].sum(axis=1)
assert (df["유형_규칙"] == [d[0] for d in dec]).all(), "decide()와 classify()의 배정이 다르다"

print("\n[2.12 기계적 경계 후보 신호]")
print(f"약한 근거 {int(df['약한근거'].sum())}건, 경합 {int(df['경합'].sum())}건, "
      f"정보부족 {int(df['정보부족'].sum())}건")
print("점수 분포:", df["우선순위점수"].value_counts().sort_index().to_dict())
n_cand = int((df["우선순위점수"] >= 1).sum())
print(f"하나라도 해당하는 경계 후보 {n_cand}건 ({n_cand / len(df) * 100:.1f}%)")
print("약한 근거로 표시된 건의 유형 분포:",
      df[df["약한근거"]]["유형_규칙"].value_counts().to_dict())

top20 = df.sort_values(["우선순위점수", "약한근거", "정보부족", "사건번호"],
                       ascending=[False, False, False, True]).head(20)
print("\n검증 우선순위 상위 20건")
for i, (_, r) in enumerate(top20.iterrows(), 1):
    sig = ",".join(n for n in ["약한근거", "경합", "정보부족"] if r[n])
    print(f"{i:2d} {r['사건번호']} 점수{r['우선순위점수']} [{sig}] "
          f"규칙={r['유형_규칙']} 근거{r['근거횟수']}회 | {r['제목'][:40]}")
print("상위 20건의 규칙 유형 분포:", top20["유형_규칙"].value_counts().to_dict())

# 이 표시가 쓸모 있는지를 표본 30건의 실제 불일치로 확인한다 (표 11-12)
flag = df.set_index("사건번호")[["약한근거", "경합", "정보부족", "우선순위점수"]]
sm = sample.join(flag, on="사건번호")
sm["후보"] = sm["우선순위점수"] >= 1
print("\n[표 11-12] 기계적 표시와 실제 불일치 (표본 30건, 개정 전 규칙 기준)")
rows12 = []
for name in ["약한근거", "경합", "정보부족"]:
    sub = sm[sm[name]]
    rows12.append((name, len(sub), int((sub["일치"] == "불일치").sum())))
for name, mask in [("하나라도 해당(후보)", sm["후보"]), ("해당 없음", ~sm["후보"])]:
    sub = sm[mask]
    rows12.append((name, len(sub), int((sub["일치"] == "불일치").sum())))
t12 = pd.DataFrame(rows12, columns=["신호", "해당 건수", "불일치"])
t12["불일치 비율(%)"] = (t12["불일치"] / t12["해당 건수"] * 100).round(1)
print(t12.to_string(index=False))
print("\n에이전트가 붙인 비고와 기계적 후보 표시의 교차:")
print(pd.crosstab(sm["비고(기준표)"], sm["후보"]).to_string())
print("\n새 표본 30건의 경계 후보:", int((new30["사건번호"].map(
    df.set_index("사건번호")["우선순위점수"]) >= 1).sum()), "건")

# ---------------------------------------------------------------- 2.13 유형별 대표 민원
tv = TfidfVectorizer(analyzer=make_tokenizer(STOP_2))
X = tv.fit_transform(docs)
print("\n[유형별 대표 민원: 유형 중심 벡터와 코사인 유사도가 가장 높은 문서]")
for label in ["의료", "보험", "통신·인터넷", "여행·운송", "자동차", "기타"]:
    idx = df.index[df["유형_규칙"] == label]
    centroid = np.asarray(X[idx].mean(axis=0))
    sims = cosine_similarity(X[idx], centroid).ravel()
    best = idx[sims.argmax()]
    print(f"{label} ({len(idx)}건): 유사도 {sims.max():.2f}  #{df.loc[best, '사건번호']}  {df.loc[best, '제목']}")
