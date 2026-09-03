# 9주차 2회차(실습) 확장 그림 생성: 그림 9-6, 9-7, 9-8, 9-9
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
mg = pd.read_csv(BASE / "data" / "sigungu_tfr_2013_2023.csv", encoding="utf-8-sig")
df["권역"] = np.where(df["시도"].isin(["서울", "경기", "인천"]), "수도권", "비수도권")
ORDER = ["수도권", "비수도권"]
SRC = "출처: 행정안전부 주민등록인구, 국가데이터처 인구동향조사 (KOSIS)"

# ---------------------------------------------------------------- 그림 9-7
# 수도권·비수도권 분포 비교 박스플롯 (고령인구비율, 합계출산율)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
for ax, col, unit, tag in [(axes[0], "고령인구비율", "%", "(가)"),
                           (axes[1], "합계출산율", "명", "(나)")]:
    sub = df.dropna(subset=[col])
    sns.boxplot(data=sub, x="권역", y=col, hue="권역", order=ORDER, width=0.45,
                palette=["#7fa8d9", "#e0975a"], legend=False, fliersize=4, ax=ax,
                medianprops=dict(color="#c0392b", lw=2))
    for i, g in enumerate(ORDER):
        s = sub.loc[sub["권역"] == g, col]
        ax.text(i, ax.get_ylim()[1] * 0.985 if col == "고령인구비율" else 1.70,
                f"n = {len(s)}\n중앙값 {s.median():.2f}", ha="center", va="top",
                fontsize=9.5, color="#333",
                bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.25"))
    ax.set_title(f"{tag} 권역별 {col} 분포 (2023년)", fontsize=12)
    ax.set_xlabel("")
    ax.set_ylabel(f"{col} ({unit})")
axes[0].set_ylim(5, 50)
axes[1].set_ylim(0.2, 1.8)
fig.text(0.01, -0.02, SRC, fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_box_region.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-9
# 2013→2023 합계출산율 변화: 변화량 히스토그램 + 두 시점 산점도
both = mg.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
both["변화"] = both["합계출산율"] - both["합계출산율_2013"]
r = both["합계출산율_2013"].corr(both["합계출산율"])

fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))

ax = axes[0]
bins = np.arange(-1.2, 0.21, 0.1)
ax.hist(both["변화"], bins=bins, color="#7fa8d9", edgecolor="white")
ax.axvline(0, color="#555", lw=1.2)
med = both["변화"].median()
ax.axvline(med, color="#c0392b", lw=1.8, ls="--", label=f"중앙값 {med:.3f}")
ax.set_title("(가) 합계출산율 변화량의 분포 (2023년 - 2013년)", fontsize=12)
ax.set_xlabel("합계출산율 변화 (명)")
ax.set_ylabel("시군구 수 (개)")
ax.legend(loc="upper left")
ax.annotate(f"0보다 큰 곳(상승) {int((both['변화'] > 0).sum())}곳\n"
            f"0보다 작은 곳(하락) {int((both['변화'] < 0).sum())}곳",
            xy=(0.02, 0.62), xycoords="axes fraction", fontsize=9.5, color="#333",
            bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))

ax = axes[1]
ax.scatter(both["합계출산율_2013"], both["합계출산율"], s=26, alpha=0.6,
           color="#4878a8", edgecolor="white", lw=0.4)
lim = (0.2, 2.5)
ax.plot(lim, lim, color="#888", lw=1.2, ls="--", label="변화 없음 선 (2023년 = 2013년)")
ax.set_xlim(*lim)
ax.set_ylim(*lim)
marks = [("전남 영암군", 2.150, 1.009, (1.75, 0.55)),
         ("경남 거제시", 1.794, 0.717, (1.25, 0.40)),
         ("전남 영광군", 1.609, 1.651, (1.80, 1.85)),
         ("인천 강화군", 0.991, 1.043, (0.35, 1.45))]
for name, x, y, (tx, ty) in marks:
    ax.annotate(name, xy=(x, y), xytext=(tx, ty), fontsize=9.5, color="#333",
                arrowprops=dict(arrowstyle="->", color="#888", lw=0.9))
ax.text(0.03, 0.95, f"상관계수 r = {r:.2f}  (n = {len(both)})",
        transform=ax.transAxes, fontsize=10, va="top",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
ax.set_title("(나) 시군구별 합계출산율: 2013년과 2023년", fontsize=12)
ax.set_xlabel("2013년 합계출산율 (명)")
ax.set_ylabel("2023년 합계출산율 (명)")
ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.86))
fig.text(0.01, -0.02, "출처: 국가데이터처 인구동향조사 (KOSIS). 합계출산율 결측 1곳(경북 군위군) 제외",
         fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_tfr_change.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-6
# 같은 데이터, 세 가지 구간 폭의 히스토그램 (고령인구비율)
aging = df["고령인구비율"]
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=False)
for ax, w, tag in [(axes[0], 1.0, "(가)"), (axes[1], 2.5, "(나)"), (axes[2], 5.0, "(다)")]:
    lo = np.floor(aging.min() / w) * w
    hi = np.ceil(aging.max() / w) * w
    edges = np.arange(lo, hi + w / 2, w)
    cnt, _ = np.histogram(aging, bins=edges)
    ax.hist(aging, bins=edges, color="#7fa8d9", edgecolor="white", lw=0.6)
    ax.axvline(aging.median(), color="#c0392b", lw=1.6, ls="--")
    k = int(cnt.argmax())
    ax.set_title(f"{tag} 구간 폭 {w:g}%포인트 (막대 {len(cnt)}개)", fontsize=12)
    ax.set_xlabel("고령인구비율 (%)")
    ax.set_ylabel("시군구 수 (개)")
    ax.set_xlim(8, 50)
    ax.text(0.97, 0.95, f"가장 높은 막대\n{edges[k]:.1f}-{edges[k + 1]:.1f}% ({cnt[k]}개)",
            transform=ax.transAxes, ha="right", va="top", fontsize=9.5, color="#333",
            bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))
axes[0].text(0.97, 0.62, f"빨간 파선: 중앙값 {aging.median():.2f}%", transform=axes[0].transAxes,
             ha="right", va="top", fontsize=9, color="#c0392b")
fig.text(0.01, -0.02, SRC + ". 229개 시군구", fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_hist_binwidth.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-8
# 수치형 열 전체의 상관 행렬 (규모 변수 블록과 비율·밀도 변수 블록을 나눠 배치)
ORDER_COLS = ["총인구", "생산가능", "고령", "유소년", "출생아수", "면적",
              "인구밀도", "인구증가율", "고령인구비율", "합계출산율"]
LABELS = ["총인구", "생산가능인구", "고령인구", "유소년인구", "출생아수", "면적",
          "인구밀도", "인구증가율", "고령인구비율", "합계출산율"]
corr = df[ORDER_COLS].corr()
fig, ax = plt.subplots(figsize=(8.6, 7.2))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0,
            square=True, linewidths=0.6, linecolor="white", annot_kws={"size": 8.5},
            cbar_kws={"label": "상관계수", "shrink": 0.8},
            xticklabels=LABELS, yticklabels=LABELS, ax=ax)
ax.axhline(6, color="#333", lw=2)
ax.axvline(6, color="#333", lw=2)
ax.text(3.0, -0.45, "규모 변수 (사람 수·넓이)", ha="center", fontsize=10.5, color="#333")
ax.text(8.0, -0.45, "비율·밀도 변수", ha="center", fontsize=10.5, color="#333")
ax.set_title("시군구 수치 변수 10개의 상관 행렬 (2023년)", fontsize=13, pad=32)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9.5)
plt.setp(ax.get_yticklabels(), rotation=0, fontsize=9.5)
fig.text(0.01, -0.01, SRC + ". 결측이 있는 쌍은 그 쌍에서만 제외",
         fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_corr_matrix.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("그림 9-6, 9-7, 9-8, 9-9 저장 완료")
print(f"검증용 수치: 변화 중앙값 {med:.3f}, 2013-2023 r = {r:.3f}, n = {len(both)}")
print(f"상관 행렬 최대: 총인구-생산가능 {corr.loc['총인구', '생산가능']:.3f}, "
      f"인구밀도-합계출산율 {corr.loc['인구밀도', '합계출산율']:.3f}")
