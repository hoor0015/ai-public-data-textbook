# 6주차 1회차 개념도 생성 (API 요청-응답 구조, 파일 다운로드 vs API 수집)
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
import koreanize_matplotlib  # noqa: E402,F401

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, color=color, lw=lw, linestyle=ls))


# ---------------------------------------------------------------- 그림 6-1
# API 요청-응답 구조: 요청 URL의 해부와 JSON 응답
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

# 위: 요청하는 쪽과 받는 쪽
box(ax, 0.5, 7.6, 3.4, 1.8, "내 컴퓨터\n(파이썬 스크립트)", fc="#fdf9f4", ec="#c77b2f", weight="bold")
box(ax, 10.1, 7.6, 3.4, 1.8, "KOSIS 서버", fc="#f5f9fd", ec="#2f6fb0", weight="bold")
arrow(ax, 4.1, 8.9, 9.9, 8.9)
ax.text(7.0, 9.3, "요청: 주소 하나에 모든 주문 내용을 담는다", ha="center", fontsize=10.5, color="#555")
arrow(ax, 9.9, 7.9, 4.1, 7.9, color="#2f8f4e")
ax.text(7.0, 7.3, "응답: JSON (약속된 형식의 데이터)", ha="center", fontsize=10.5, color="#2f8f4e")

# 가운데: 요청 URL의 세 부분
ax.text(0.6, 6.3, "요청 URL의 세 부분", fontsize=11.5, fontweight="bold", color="#333")
box(ax, 0.5, 4.4, 4.1, 1.5,
    "엔드포인트 (가게 주소)\nkosis.kr/openapi/Param/\nstatisticsParameterData.do",
    fc="#f5f9fd", ec="#2f6fb0", fontsize=9.5)
box(ax, 4.95, 4.4, 4.1, 1.5,
    "파라미터 (주문 내용)\ntblId=DT_1B040A3\nstartPrdDe=2023, format=json",
    fc="#f4fbf6", ec="#2f8f4e", fontsize=9.5)
box(ax, 9.4, 4.4, 4.1, 1.5,
    "인증키 (회원증)\napiKey=발급받은키",
    fc="#fdf9f4", ec="#c77b2f", fontsize=9.5)
ax.text(4.78, 5.15, "+", ha="center", va="center", fontsize=15, color="#555")
ax.text(9.22, 5.15, "+", ha="center", va="center", fontsize=15, color="#555")

# 아래: 응답 JSON 조각
box(ax, 2.2, 0.5, 9.6, 3.0,
    '응답 JSON의 레코드 한 개 (실제 응답에서 발췌)\n'
    '{ "TBL_NM": "행정구역(시군구)별 성별 인구수",\n'
    '  "C1_NM": "서울특별시",  "ITM_NM": "총인구수",\n'
    '  "PRD_DE": "2023",  "DT": "9386034",  "UNIT_NM": "명" }',
    fc="#faf8fc", ec="#7a5fa8", fontsize=10)
arrow(ax, 7.0, 4.2, 7.0, 3.7, color="#7a5fa8")
fig.savefig(FIG / "fig06_api_request.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 6-2
# 파일 내려받기 vs API 수집
fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
for ax in axes:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

ax = axes[0]
ax.set_title("(가) 파일 내려받기: 손이 일한다", fontsize=13, pad=12)
box(ax, 3.0, 8.0, 4.0, 1.4, "사람", fc="#fdf9f4", ec="#c77b2f", weight="bold")
box(ax, 3.0, 5.6, 4.0, 1.4, "포털 화면에서\n검색·클릭·조건 설정", fc="white", ec="#c77b2f", fontsize=10)
box(ax, 3.0, 3.2, 4.0, 1.4, "다운로드 버튼 클릭", fc="white", ec="#c77b2f", fontsize=10)
box(ax, 3.0, 0.8, 4.0, 1.4, "파일 저장\n(어떻게 받았는지 기록 없음)", fc="#f7f7fc", ec="#5b6ee1", fontsize=10)
arrow(ax, 5.0, 7.9, 5.0, 7.15)
arrow(ax, 5.0, 5.5, 5.0, 4.75)
arrow(ax, 5.0, 3.1, 5.0, 2.35)
ax.text(8.6, 5.0, "갱신되면\n처음부터\n다시 반복", ha="center", fontsize=10, color="#c0392b")

ax = axes[1]
ax.set_title("(나) API 수집: 스크립트가 일한다", fontsize=13, pad=12)
box(ax, 3.0, 8.0, 4.0, 1.4, "수집 스크립트\n(에이전트가 작성)", fc="#f5f9fd", ec="#2f6fb0", weight="bold", fontsize=10)
box(ax, 3.0, 5.6, 4.0, 1.4, "API 요청\n(조건이 코드에 적혀 있음)", fc="white", ec="#2f6fb0", fontsize=10)
box(ax, 3.0, 3.2, 4.0, 1.4, "JSON 응답 수신", fc="white", ec="#2f6fb0", fontsize=10)
box(ax, 3.0, 0.8, 4.0, 1.4, "CSV 저장\n(스크립트 = 수집 기록)", fc="#f4fbf6", ec="#2f8f4e", fontsize=10)
arrow(ax, 5.0, 7.9, 5.0, 7.15)
arrow(ax, 5.0, 5.5, 5.0, 4.75)
arrow(ax, 5.0, 3.1, 5.0, 2.35)
ax.text(8.6, 5.0, "갱신되면\n스크립트를\n다시 실행", ha="center", fontsize=10, color="#2f8f4e")
fig.tight_layout()
fig.savefig(FIG / "fig06_file_vs_api.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob('fig06_*.png'))])
