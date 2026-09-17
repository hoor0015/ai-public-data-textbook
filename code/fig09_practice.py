# 9주차 2회차(실습) 그림 생성: 그림 9-10 (그림 규격 여섯 줄의 자리)
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
SRC = "출처: 행정안전부 주민등록인구, 국가데이터처 인구동향조사 (KOSIS)"

# ---------------------------------------------------------------- 그림 9-10
# 그림 규격 여섯 줄이 그림의 어디에 놓이는가 (권역별 평균 합계출산율 막대그래프)
df["권역"] = np.where(df["시도"].isin(["서울", "경기", "인천"]), "수도권", "비수도권")
means, counts = [], []
for g in ["수도권", "비수도권"]:
    s = df.loc[df["권역"] == g, "합계출산율"].dropna()
    means.append(s.mean())
    counts.append(len(s))

fig, ax = plt.subplots(figsize=(7.6, 5.2))
colors = ["#7fa8d9", "#e0975a"]
for i, (g, m, c) in enumerate(zip(["수도권", "비수도권"], means, counts)):
    ax.bar(i, m, width=0.5, color=colors[i], edgecolor="white",
           label=f"{g} (시군구 {c}곳)")
    ax.text(i, m + 0.02, f"{m:.3f}명", ha="center", va="bottom", fontsize=11)
ax.set_xticks([0, 1])
ax.set_xticklabels(["수도권", "비수도권"])
ax.set_ylim(0, 1.05)
ax.set_title("(1) 수도권과 비수도권의 평균 합계출산율 (2023년)", fontsize=13)
ax.set_xlabel("(2) 권역")
ax.set_ylabel("(3) 합계출산율 (명)")
ax.legend(title="(4) 범례", fontsize=9.5, title_fontsize=9.5, loc="upper left")
ax.annotate("(6) 막대그래프의 세로축은\n0에서 시작한다",
            xy=(0.0, 0.0), xycoords="axes fraction",
            xytext=(0.30, 0.22), textcoords="axes fraction",
            fontsize=10.5, color="#c0392b", ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.3))
fig.text(0.01, -0.02,
         "(5) " + SRC + ". 합계출산율이 결측인 1곳(경북 군위군)은 제외",
         fontsize=8.5, color="#666", ha="left")
fig.tight_layout()
fig.savefig(FIG / "fig09_bar_region_spec.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved: fig09_bar_region_spec.png")
print(f"수도권 {counts[0]}곳 평균 {means[0]:.3f}, 비수도권 {counts[1]}곳 평균 {means[1]:.3f}, "
      f"길이 비 {means[1] / means[0]:.3f}배")
