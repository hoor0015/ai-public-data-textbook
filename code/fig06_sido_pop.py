# 6주차 확인 그림: 시도별 주민등록 총인구 (2023)
# 데이터 출처: KOSIS, 행정안전부 주민등록인구현황
#   통계표 DT_1B040A3 (행정구역(시군구)별 성별 인구수), 항목 T20(총인구수), 2023년
#   2026-08-12에 kosis MCP로 수집한 실제 값. 17개 시도 합계 = 51,325,329 (전국 값과 일치 확인)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)

sido = [
    ("경기도", 13630821), ("서울특별시", 9386034), ("부산광역시", 3293362),
    ("경상남도", 3251158), ("인천광역시", 2997410), ("경상북도", 2554324),
    ("대구광역시", 2374960), ("충청남도", 2130119), ("전라남도", 1804217),
    ("전북특별자치도", 1754757), ("충청북도", 1593469), ("강원특별자치도", 1527807),
    ("대전광역시", 1442216), ("광주광역시", 1419237), ("울산광역시", 1103661),
    ("제주특별자치도", 675252), ("세종특별자치시", 386525),
]
names = [s[0] for s in sido][::-1]
vals = [s[1] / 10000 for s in sido][::-1]  # 만 명 단위

fig, ax = plt.subplots(figsize=(9, 6.5))
bars = ax.barh(names, vals, color="#7fa8d0", edgecolor="#2f6fb0", height=0.62)
for b, v in zip(bars, vals):
    ax.text(b.get_width() + 10, b.get_y() + b.get_height() / 2,
            f"{v:,.0f}", va="center", fontsize=9, color="#333")
ax.set_xlabel("주민등록 총인구 (만 명, 2023)")
ax.set_xlim(0, 1550)
ax.set_title("시도별 주민등록 총인구 (2023): MCP 수집 결과 확인용", fontsize=13)
sns.despine(left=True)
fig.tight_layout()
fig.savefig(FIG / "fig06_sido_pop.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig06_sido_pop.png")
