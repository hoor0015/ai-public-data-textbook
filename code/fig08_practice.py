# 8주차 2회차(실습) 그림 생성: 그림 8-6, 8-7
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

df = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")
inc = pd.read_csv(BASE / "data" / "income_dist.csv", encoding="utf-8-sig")
sub = df.dropna(subset=["합계출산율"])
r = sub["고령인구비율"].corr(sub["합계출산율"])

# ---------------------------------------------------------------- 그림 8-6
# 그래프 다듬기 전과 후
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))

ax = axes[0]
ax.grid(False)
ax.scatter(sub["고령인구비율"], sub["합계출산율"], s=18)
ax.set_title("(가) 다듬기 전", fontsize=12, color="#888")

ax = axes[1]
ax.scatter(sub["고령인구비율"], sub["합계출산율"],
           s=28, alpha=0.6, color="#4878a8", edgecolor="white", lw=0.4)
ax.set_title("(나) 다듬기 후: 고령인구비율과 합계출산율 (2023년)",
             fontsize=12)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.text(0.03, 0.95, f"상관계수 r = {r:.2f}  (n = {len(sub)})",
        transform=ax.transAxes, fontsize=10, va="top",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
fig.tight_layout()
fig.savefig(FIG / "fig08_polish.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 8-7
# 왜곡된 시계열 그래프와 고친 그래프
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))

ax = axes[0]
ax.plot(inc["연도"], inc["지니계수"], marker="o", color="#c0392b", lw=2.6)
ax.set_ylim(0.320, 0.390)
ax.set_xticks([2011, 2015, 2019, 2023])
ax.set_title("(가) 왜곡: 축을 좁게 잘라 급락처럼 보이게", fontsize=12)
ax.set_xlabel("연도")
ax.set_ylabel("지니계수")

ax = axes[1]
ax.plot(inc["연도"], inc["지니계수"], marker="o", color="#2f6fb0", lw=2)
ax.set_ylim(0, 0.45)
ax.set_xticks([2011, 2015, 2019, 2023])
ax.set_title("(나) 고침: 축 범위를 넓혀 변화의 크기를 맥락에", fontsize=12)
ax.set_xlabel("연도")
ax.set_ylabel("지니계수")
ax.annotate("0.387", xy=(2011, 0.387), xytext=(2011.2, 0.30),
            fontsize=9.5, ha="left", color="#2f6fb0",
            arrowprops=dict(arrowstyle="->", color="#888", lw=0.8))
ax.annotate("0.323", xy=(2023, 0.323), xytext=(2021.0, 0.22),
            fontsize=9.5, ha="left", color="#2f6fb0",
            arrowprops=dict(arrowstyle="->", color="#888", lw=0.8))

fig.suptitle("같은 지니계수 시계열, 두 가지 인상 (2011-2023년)",
             fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(FIG / "fig08_distort_fix.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("그림 8-6, 8-7 저장 완료")
