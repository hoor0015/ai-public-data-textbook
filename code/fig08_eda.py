# 8주차 1회차(이론) 그림 생성: 그림 8-1부터 8-5까지
# 실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

df = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")
inc = pd.read_csv(BASE / "data" / "income_dist.csv", encoding="utf-8-sig")

# ---------------------------------------------------------------- 그림 8-1
# 고령인구비율 히스토그램
fig, ax = plt.subplots(figsize=(8, 5))
bins = np.arange(10, 47.5, 2.5)
ax.hist(df["고령인구비율"], bins=bins, color="#7fa8d9", edgecolor="white")
mean_v = df["고령인구비율"].mean()
med_v = df["고령인구비율"].median()
ax.axvline(med_v, color="#c0392b", lw=1.8, ls="--",
           label=f"중앙값 {med_v:.1f}%")
ax.axvline(mean_v, color="#2c3e50", lw=1.8, ls=":",
           label=f"평균 {mean_v:.1f}%")
ax.set_title("시군구 고령인구비율의 분포 (2023년, 229개 시군구)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("시군구 수 (개)")
ax.legend()
ax.annotate("오른쪽으로 길게 뻗은 꼬리:\n고령화가 극심한 농촌 군 지역",
            xy=(41, 6), xytext=(33.5, 22),
            arrowprops=dict(arrowstyle="->", color="#555"),
            fontsize=10, color="#333")
fig.tight_layout()
fig.savefig(FIG / "fig08_hist_aging.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 8-2
# 시도별 고령인구비율 박스플롯 (중앙값 오름차순)
order = (df.groupby("시도")["고령인구비율"].median()
           .sort_values().index.tolist())
fig, ax = plt.subplots(figsize=(8, 7))
sns.boxplot(data=df, y="시도", x="고령인구비율", order=order,
            color="#a8c4e0", width=0.6, fliersize=4, ax=ax,
            medianprops=dict(color="#c0392b", lw=2))
ax.set_title("시도별 고령인구비율 분포 (2023년)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(FIG / "fig08_box_sido.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 8-3
# 산점도: 고령인구비율 vs 합계출산율
sub = df.dropna(subset=["합계출산율"])
r = sub["고령인구비율"].corr(sub["합계출산율"])
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(sub["고령인구비율"], sub["합계출산율"],
           s=28, alpha=0.6, color="#4878a8", edgecolor="white", lw=0.4)
coef = np.polyfit(sub["고령인구비율"], sub["합계출산율"], 1)
xs = np.linspace(sub["고령인구비율"].min(), sub["고령인구비율"].max(), 50)
ax.plot(xs, np.polyval(coef, xs), color="#c0392b", lw=1.6, ls="--",
        label="추세선")
marks = [("전남 영광군", 31.19, 1.651, (23.5, 1.62)),
         ("경북 의성군", 45.28, 1.406, (40.5, 1.55)),
         ("부산 중구", 29.90, 0.320, (32.5, 0.34)),
         ("울산 북구", 10.68, 0.930, (11.2, 1.08))]
for name, x, y, (tx, ty) in marks:
    ax.annotate(name, xy=(x, y), xytext=(tx, ty), fontsize=9.5,
                color="#333",
                arrowprops=dict(arrowstyle="->", color="#888", lw=0.9))
ax.text(0.03, 0.95, f"상관계수 r = {r:.2f}  (n = {len(sub)})",
        transform=ax.transAxes, fontsize=10.5, va="top",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
ax.set_title("고령인구비율과 합계출산율의 관계 (2023년)", fontsize=13)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "fig08_scatter_aging_tfr.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 8-4
# 지니계수 시계열
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(inc["연도"], inc["지니계수"], marker="o", color="#2f6fb0", lw=2)
ax.set_ylim(0.30, 0.40)
ax.set_xticks(inc["연도"])
ax.set_title("지니계수 추이 (2011-2023년, 처분가능소득 기준)", fontsize=13)
ax.set_xlabel("연도")
ax.set_ylabel("지니계수")
first, last = inc["지니계수"].iloc[0], inc["지니계수"].iloc[-1]
ax.annotate(f"{first:.3f}", xy=(2011, first), xytext=(2011, first + 0.006),
            fontsize=10, ha="center", color="#2f6fb0")
ax.annotate(f"{last:.3f}", xy=(2023, last), xytext=(2023, last + 0.006),
            fontsize=10, ha="center", color="#2f6fb0")
fig.tight_layout()
fig.savefig(FIG / "fig08_line_gini.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 8-5
# 정직한 그래프 vs 축 자른 왜곡 그래프 (막대)
cap = df["시도"].isin(["서울", "경기", "인천"])
v_cap = df.loc[cap, "합계출산율"].mean()
v_non = df.loc[cap.eq(False), "합계출산율"].mean()
labels = ["수도권", "비수도권"]
values = [v_cap, v_non]
colors = ["#7fa8d9", "#e0975a"]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
for ax, title, ylim in [(axes[0], "(가) 정직한 그래프: 세로축이 0에서 시작", (0, 1.0)),
                        (axes[1], "(나) 왜곡된 그래프: 세로축을 0.65에서 자름", (0.65, 0.90))]:
    bars = ax.bar(labels, values, color=colors, width=0.55)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=12)
    ax.set_ylabel("합계출산율 (명)")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2,
                min(v, ylim[1]) - (ylim[1] - ylim[0]) * 0.06,
                f"{v:.2f}", ha="center", fontsize=11,
                color="white", fontweight="bold")
fig.suptitle("같은 데이터, 다른 인상: 시군구 평균 합계출산율 (2023년)",
             fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(FIG / "fig08_axis_trunc.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("그림 8-1부터 8-5 저장 완료")
print(f"검증용 수치: 평균 {mean_v:.2f}, 중앙값 {med_v:.2f}, r={r:.3f}, "
      f"수도권 {v_cap:.3f}, 비수도권 {v_non:.3f}")
