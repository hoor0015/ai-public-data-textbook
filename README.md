# AI 기반 공공데이터 분석 교재

VSCode + Claude Code 조합으로 AI 에이전트를 활용해 한국 공공데이터를 분석하는 학부 교재. 13개 콘텐츠 주차(중간·기말 제외) × 주당 2회차(1회차 이론, 2회차 실습) = 총 26개 장. 형식은 통계학입문책(QSS 한국 공공데이터판)을 계승한다. 독자는 문과(행정학과) 학부 1학년이며, 학생의 역할은 코딩이 아니라 에이전트에 대한 지시·검증·해석이다.

## 문서

- [목차.md](목차.md): 26개 장의 절 단위 목차 (확정)
- [집필지침.md](집필지침.md): 눈높이, 장 구조, HTML 박스, 그림·데이터, 금칙어 등 집필 기준

## 웹교재 (HTML)

SNU 강의노트 형식의 웹교재로 빌드되어 있으며, GitHub Pages로 게시된다: https://hoor0015.github.io/ai-public-data-textbook/ (main에 푸시하면 자동 재배포). [index.html](index.html)을 브라우저로 열면 4부·13주 목차와 사이드바 내비게이션(이론/실습 태그, 현재 장의 절 목록 펼침)으로 26개 장을 읽을 수 있다. 본문(md)을 고친 뒤 `code/build_html.py`를 실행하면 다시 빌드된다 (index.html + w01-1.html - w13-2.html, 앞뒤 장 이동 링크 포함).

## 진행 현황: 26개 장 전체 완성 (그림 46개, 전 장 검수 통과)

### 1부. 에이전트와 도구 (1-4주)
- [x] 01-1 AI 에이전트 시대의 공공데이터 분석 / 01-2 첫 만남: VSCode와 Claude Code
- [x] 02-1 AI 에이전트의 작동 원리 / 02-2 에이전트가 일하는 모습 관찰하기
- [x] 03-1 에이전트에게 일 시키는 법: 지시 설계 / 03-2 지시문 개선 워크숍
- [x] 04-1 분석 환경 이해하기 / 04-2 에이전트로 분석 환경 구축하기 (uv)

### 2부. 공공데이터의 수집과 정리 (5-7주)
- [x] 05-1 공공데이터 생태계 / 05-2 데이터 찾고 첫 개관하기
- [x] 06-1 오픈API와 자동 수집 / 06-2 에이전트로 API 수집 파이프라인 만들기 (KOSIS 실수집 예시)
- [x] 07-1 데이터 정제 / 07-2 에이전트로 데이터 정제하기 (2013-2023 행정구역 개편 실사례 병합)

### 3부. 분석과 해석 (8-11주)
- [x] 08-1 탐색적 데이터 분석과 시각화 / 08-2 에이전트로 EDA 수행하기
- [x] 09-1 통계로 정책 진단하기 / 09-2 에이전트로 통계 분석하기 (수도권 비교 t검정, 회귀)
- [x] 10-1 텍스트 데이터 분석 / 10-2 에이전트로 민원 텍스트 분석하기 (공정위 민원 567건 실분석)
- [x] 11-1 문서 그라운딩과 작업 자동화 / 11-2 그라운딩과 나만의 Skill 만들기

### 4부. 종합과 확장 (12-13주)
- [x] 12-1 다중 에이전트와 분석 파이프라인 / 12-2 전 과정 파이프라인 구축하기
- [x] 13-1 분석 보고서와 책임 있는 AI 활용 / 13-2 종합 프로젝트: 나의 분석 보고서

## 집필 원칙 (요약)

- 모든 본문 수치는 실제 데이터에서 계산해 검증한 값만 사용. 모든 그림은 `code/`의 스크립트로 재현 가능.
- Claude Code 기능(계획 모드, CLAUDE.md, Skill, 서브에이전트, MCP)과 포털·법령 사실관계는 공식 문서(code.claude.com/docs, law.go.kr 등)로 확인 후 서술.
- 매 실습 장에 "에이전트가 틀리는 장면"과 검증 절차 포함 (예: 결측 fillna(0)으로 군위군이 전국 최저 출산율로 둔갑, 병합 시 미추홀구 조용히 탈락).

## 구성

```
목차.md, 집필지침.md, README.md
index.html, wNN-S.html           웹교재 (빌드 산출물, code/build_html.py)
NN-1_이론_*.md, NN-2_실습_*.md   26개 장 본문 (Markdown 원고)
code/    그림 생성(figNN_*.py)·분석(chNN_*.py)·빌드(build_html.py) 코드
data/    예시 공공데이터
figures/ 본문 삽입 그림 46개 (PNG, dpi=150)
```

## 데이터 출처

| 파일 | 출처 | 사용 장 |
|------|------|------|
| `data/sigungu_2023.csv` | 행안부 주민등록인구(KOSIS DT_110001_A001) + 합계출산율(DT_1B81A23) | 2-9, 12-13 |
| `data/sigungu_tfr_2013.csv` | 시군구 합계출산율 2013 (KOSIS DT_1B81A23) | 7, 12 |
| `data/sigungu_tfr_2013_2023.csv` | 위 두 파일의 병합 산출물 (code/ch07_merge.py 생성) | 7-8 |
| `data/income_dist.csv` | 소득분배지표 (KOSIS DT_1HDALF05) | 8 |
| `data/grdp_sido.csv` | 시도별 1인당 GRDP (KOSIS DT_1C96) | 예비 |
| `data/migration_od_2023.csv` | 시도 간 인구이동 (KOSIS DT_1B26008) | 예비 |
| `data/minwon_cases_2021.csv` | 공정거래위원회 소비자 민원학습데이터 모범상담 사례 (공공데이터포털 15098335) | 10 |
| `data/minwon_sample30.csv` | 위 데이터의 교차검증용 표본 30건 (시드 고정) | 10 |
| 6주차 API 예시 | KOSIS 오픈API DT_1B040A3 실호출 (2023년 행정구역별 인구 870건) | 6 |

## 그림·분석 재현

```bash
cd ~/default-uv-env
PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<교재>/code/fig01_concepts.py"   # 장별 figNN_*.py 동일
PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<교재>/code/ch07_merge.py"      # 7장 병합, ch09/ch10 동일
```

필요 패키지: pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, koreanize-matplotlib, requests.
