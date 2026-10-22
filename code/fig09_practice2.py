# 9주차 2차시(실습) 확장 그림 생성 (data/sigungu_mcp_2023.csv): 그림 9-19(합계출산율·인구증가율 분포), 9-7, 9-8, 9-9
# 실행: VIRTUAL_ENV= uv run --project ~/default-uv-env python -X utf8 code/fig09_practice2.py
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

df = pd.read_csv(BASE / "data" / "sigungu_mcp_2023.csv", encoding="utf-8-sig")
t13 = pd.read_csv(BASE / "data" / "sigungu_mcp_tfr_2013.csv", encoding="utf-8-sig")
# 9주차 2차시 2.7의 대응표: 2013년 표의 (변동전) 세 행을 2023년 행정구역 이름으로 맞춘다
MAP13 = {("인천", "남구(변동전)"): ("인천", "미추홀구"),
         ("경북", "군위군(변동전)"): ("대구", "군위군"),
         ("충북", "청주시(변동전)"): ("충북", "청주시")}
for (s0, g0), (s1, g1) in MAP13.items():
    t13.loc[(t13["시도"] == s0) & (t13["시군구"] == g0), ["시도", "시군구"]] = [s1, g1]
mg = df[["시도", "시군구", "합계출산율"]].merge(t13, on=["시도", "시군구"], how="left",
                                         validate="one_to_one")
df["권역"] = df["수도권"]
ORDER = ["수도권", "비수도권"]
SRC = "출처: kosis MCP로 수집한 KOSIS 통계표 6개를 결합한 시군구 데이터 (2023년)"

# ---------------------------------------------------------------- 그림 9-20
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
        ax.text(i, ax.get_ylim()[1] * 0.985 if col == "고령인구비율" else 1.93,
                f"n = {len(s)}\n중앙값 {s.median():.2f}", ha="center", va="top",
                fontsize=9.5, color="#333",
                bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.25"))
    ax.set_title(f"{tag} 권역별 {col} 분포 (2023년)", fontsize=12)
    ax.set_xlabel("")
    ax.set_ylabel(f"{col} ({unit})")
axes[0].set_ylim(5, 50)
axes[1].set_ylim(0.2, 1.95)
fig.text(0.01, -0.02, SRC, fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_box_region.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-22
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
fig.text(0.01, -0.02, "출처: 국가데이터처 인구동향조사 시군구 합계출산율 2013·2023년 (kosis MCP). 2013년 값은 대응표로 이름을 맞춘 229곳",
         fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_tfr_change.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-19
# 11주차가 이어 쓰는 두 변수의 분포: 합계출산율, 인구증가율
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
for ax, col, unit, w, tag in [(axes[0], "합계출산율", "명", 0.05, "(가)"),
                              (axes[1], "인구증가율", "%", 0.5, "(나)")]:
    s = df[col].dropna()
    lo = np.floor(s.min() / w) * w
    hi = np.ceil(s.max() / w) * w
    edges = np.arange(lo, hi + w / 2, w)
    ax.hist(s, bins=edges, color="#7fa8d9", edgecolor="white", lw=0.6)
    ax.axvline(s.median(), color="#c0392b", lw=1.6, ls="--",
               label=f"중앙값 {s.median():.2f}{unit}")
    if col == "인구증가율":
        ax.axvline(0, color="#444", lw=1.4, ls=":", label="변화 없음 (0)")
    ax.set_title(f"{tag} {col}의 분포 (2023년, 구간 폭 {w:g}{unit})", fontsize=12)
    ax.set_xlabel(f"{col} ({unit})")
    ax.set_ylabel("시군구 수 (개)")
    ax.legend(fontsize=9, loc="upper right")
    ax.text(0.98, 0.72, f"n = {len(s)}", transform=ax.transAxes,
            ha="right", va="top", fontsize=9.5, color="#333")
fig.text(0.01, -0.02, SRC + ". 인구증가율은 결측 1곳(대구 군위군)을 제외한 228곳",
         fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_hist_tfr_growth.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 9-21
# 수치형 열 전체의 상관 행렬 (규모 변수, 연령 구조 변수, 나머지 세 묶음으로 나눠 배치)
ORDER_COLS = ["총인구", "출생아수", "면적",
              "고령인구비율", "노년부양비", "노령화지수", "중위연령", "유소년부양비",
              "인구밀도", "인구증가율", "합계출산율"]
LABELS = ORDER_COLS
corr = df[ORDER_COLS].corr()
fig, ax = plt.subplots(figsize=(9.2, 7.8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0,
            square=True, linewidths=0.6, linecolor="white", annot_kws={"size": 8.5},
            cbar_kws={"label": "상관계수", "shrink": 0.8},
            xticklabels=LABELS, yticklabels=LABELS, ax=ax)
for k in (3, 8):
    ax.axhline(k, color="#333", lw=2)
    ax.axvline(k, color="#333", lw=2)
ax.text(1.5, -0.45, "규모 변수", ha="center", fontsize=10.5, color="#333")
ax.text(5.5, -0.45, "연령 구조 변수", ha="center", fontsize=10.5, color="#333")
ax.text(9.5, -0.45, "밀도·증가율·출산율", ha="center", fontsize=10.5, color="#333")
ax.set_title("시군구 수치 변수 11개의 상관 행렬 (2023년)", fontsize=13, pad=32)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9.5)
plt.setp(ax.get_yticklabels(), rotation=0, fontsize=9.5)
fig.text(0.01, -0.01, SRC + ". 결측이 있는 쌍은 그 쌍에서만 제외",
         fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_corr_matrix.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("그림 9-19, 9-7, 9-8, 9-9 저장 완료")
print(f"검증용 수치: 변화 중앙값 {med:.3f}, 2013-2023 r = {r:.3f}, n = {len(both)}")
print(f"상관 행렬: 고령인구비율-노년부양비 {corr.loc['고령인구비율', '노년부양비']:.3f}, "
      f"인구밀도-합계출산율 {corr.loc['인구밀도', '합계출산율']:.3f}")
