# 7주차 그림: 열별 결측 현황 (sigungu_2023.csv 실제 데이터)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

d2023 = pd.read_csv(BASE / "data" / "sigungu_2023.csv")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8),
                         gridspec_kw={"width_ratios": [1.15, 1]})

# (가) 열별 결측 개수
ax = axes[0]
na_counts = d2023.isna().sum()
colors = ["#c0392b" if v > 0 else "#9ec3e0" for v in na_counts]
ax.bar(range(len(na_counts)), na_counts.values, color=colors)
ax.set_xticks(range(len(na_counts)))
ax.set_xticklabels(na_counts.index, rotation=45, ha="right", fontsize=9)
ax.set_ylabel("결측 칸 수")
ax.set_yticks([0, 1, 2])
ax.set_ylim(0, 2.2)
ax.set_title("(가) 열별 결측 개수: 229행 12열 중 결측은 2칸", fontsize=12)
for i, v in enumerate(na_counts.values):
    if v > 0:
        ax.text(i, v + 0.06, str(int(v)), ha="center", fontsize=10,
                color="#c0392b", fontweight="bold")

# (나) 결측 위치 지도 (행 x 열, 결측 칸만 붉게)
ax = axes[1]
mat = d2023.isna().to_numpy().astype(float)
ax.imshow(mat, aspect="auto", cmap=plt.cm.colors.ListedColormap(["#eef4fa", "#c0392b"]),
          interpolation="nearest")
ax.set_xticks(range(len(d2023.columns)))
ax.set_xticklabels(d2023.columns, rotation=45, ha="right", fontsize=9)
ax.set_ylabel("행 번호 (시군구)")
ax.set_title("(나) 결측의 위치: 두 칸 모두 71행(경북 군위군)", fontsize=12)
row = int(np.where(mat.any(axis=1))[0][0])
ax.annotate("경북 군위군 (71행)\n합계출산율·출생아수 결측",
            xy=(10, row), xytext=(4.2, 150),
            fontsize=10, color="#c0392b",
            arrowprops=dict(arrowstyle="->", color="#c0392b"))
ax.grid(False)

fig.tight_layout()
fig.savefig(FIG / "fig07_missing.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved: fig07_missing.png")
