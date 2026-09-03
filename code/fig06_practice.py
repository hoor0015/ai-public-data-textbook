# 6주차 2회차(실습) 그림 생성: 그림 6-4 전국 주민등록 총인구 추이(2019-2023)와 전년 대비 증감
# 데이터 출처: KOSIS, 행정안전부 주민등록인구현황
#   통계표 DT_1B040A3 (행정구역(시군구)별 성별 인구수), 항목 총인구수, 전국, 2019-2023년
#   kosis MCP로 수집한 실제 값 (12주차 2.3의 근거 메모와 같은 값)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)

# 전국 주민등록 총인구 (명), 2019-2023
korea = pd.DataFrame({
    "연도": [2019, 2020, 2021, 2022, 2023],
    "총인구": [51849861, 51829023, 51638809, 51439038, 51325329],
})
korea["전년대비증감"] = korea["총인구"].diff()

# ------------------------------------------------ 본문에 쓴 수치 계산 (2.6 손 검산 정답)
print("연도별 전년 대비 증감 (명):")
for _, r in korea.iterrows():
    d = "" if pd.isna(r["전년대비증감"]) else f"{int(r['전년대비증감']):+,}"
    print(f"  {int(r['연도'])}: {int(r['총인구']):,}  {d}")
total = korea["총인구"].iloc[-1] - korea["총인구"].iloc[0]
pct = total / korea["총인구"].iloc[0] * 100
print(f"2019→2023 누적 증감: {total:+,} 명 ({pct:+.2f}%)")
print("증감 합계 = 누적 증감 확인:",
      int(korea["전년대비증감"].dropna().sum()) == int(total))

# ------------------------------------------------ 2.7 csv-profile 대조용: 17개 시도 총인구 요약
sido = pd.Series({
    "경기도": 13630821, "서울특별시": 9386034, "부산광역시": 3293362,
    "경상남도": 3251158, "인천광역시": 2997410, "경상북도": 2554324,
    "대구광역시": 2374960, "충청남도": 2130119, "전라남도": 1804217,
    "전북특별자치도": 1754757, "충청북도": 1593469, "강원특별자치도": 1527807,
    "대전광역시": 1442216, "광주광역시": 1419237, "울산광역시": 1103661,
    "제주특별자치도": 675252, "세종특별자치시": 386525,
})
print("\n17개 시도 총인구 요약 (2023):")
print(f"  합계 {sido.sum():,}  평균 {sido.mean():,.1f}  중앙값 {sido.median():,.0f}")
print(f"  표준편차(pandas 기본, n-1) {sido.std():,.1f}")
print(f"  최소 {sido.idxmin()} {sido.min():,}  최대 {sido.idxmax()} {sido.max():,}")

# ------------------------------------------------ 그림 6-4
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

ax = axes[0]
y = korea["총인구"] / 10000
ax.plot(korea["연도"], y, marker="o", color="#2f6fb0", lw=2)
for x, v, raw in zip(korea["연도"], y, korea["총인구"]):
    ax.annotate(f"{raw:,}", (x, v), textcoords="offset points", xytext=(0, 9),
                ha="center", fontsize=9, color="#333")
ax.set_xticks(korea["연도"])
ax.set_ylim(5100, 5210)
ax.set_xlabel("연도")
ax.set_ylabel("주민등록 총인구 (만 명)")
ax.set_title("(가) 전국 주민등록 총인구 (2019-2023)", fontsize=12)

ax = axes[1]
ch = korea.dropna(subset=["전년대비증감"])
vals = ch["전년대비증감"] / 10000
bars = ax.bar(ch["연도"], vals, color="#d98c5f", edgecolor="#c77b2f", width=0.6)
for b, v, raw in zip(bars, vals, ch["전년대비증감"]):
    ax.text(b.get_x() + b.get_width() / 2, v - 0.6, f"{int(raw):+,}",
            ha="center", va="top", fontsize=9, color="#333")
ax.axhline(0, color="#555", lw=0.8)
ax.set_xticks(ch["연도"])
ax.set_ylim(-24, 3)
ax.set_xlabel("연도")
ax.set_ylabel("전년 대비 증감 (만 명)")
ax.set_title("(나) 전년 대비 증감: 네 해 모두 감소", fontsize=12)

fig.tight_layout()
fig.savefig(FIG / "fig06_korea_trend.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nsaved: fig06_korea_trend.png")
