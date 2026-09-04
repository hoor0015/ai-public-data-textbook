# 13주차 2회차(실습) 그림 생성: 그림 13-4 (팀 배치도), 그림 13-5 (검문소 4 대조용 그림)
# 실행: cd ~/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

sns.set_style("whitegrid")
import koreanize_matplotlib  # noqa: E402,F401
import figfit  # noqa: E402,F401  (상자 글씨 자동 크기)

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, fc="#f5f9fd", ec="#2f6fb0", fontsize=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color="#555", lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=lw))


# ---------------------------------------------------------------- 그림 13-4
# 파이프라인 명세서의 팀 배치도: 단계, 담당 에이전트, 산출 파일, 검문소
fig, ax = plt.subplots(figsize=(13, 6.2))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

box(ax, 5.2, 8.3, 3.6, 1.3, "본 에이전트 (팀장)\n지시서 전달·요약 수합", fc="#f5f9fd", ec="#2f6fb0", weight="bold")
stages = [
    ("① 수집 확인\n(6주차)", "본 에이전트\n(직접 처리)", "확인 보고\n(행 수·열 목록)", "#f5f9fd", "#2f6fb0"),
    ("② 정제·병합\n(7주차)", "cleaner\n(agents/cleaner.md)", "merged.csv\n정제로그.md", "#f4fbf6", "#2f8f4e"),
    ("③ 분석\n(10주차)", "analyst\n(agents/analyst.md)", "analysis.md\n(결과표)", "#faf8fc", "#7a5fa8"),
    ("④ 시각화\n(9주차)", "plotter\n(agents/plotter.md)", "fig_scatter.png\nfig_change.png", "#fdf9f4", "#c77b2f"),
    ("⑤ 보고\n(14주차로)", "본 에이전트\n(직접 처리)", "report.md\n(한 쪽 요약)", "#f7f7fc", "#5b6ee1"),
]
for i, (t1, who, out, fc, ec) in enumerate(stages):
    x = 0.4 + i * 2.75
    box(ax, x, 5.2, 2.2, 1.5, t1, fc=fc, ec=ec, fontsize=12, weight="bold")
    box(ax, x, 3.9, 2.2, 1.0, "담당: " + who, fc="white", ec=ec, fontsize=10)
    box(ax, x, 2.45, 2.2, 1.2, out, fc="white", ec="#aaa", fontsize=9)
    if i < 4:
        arrow(ax, x + 2.3, 5.95, x + 2.65, 5.95)
        cx = x + 2.475
        ax.plot([cx], [6.95], marker="v", color="#a04747", markersize=9)
        ax.text(cx, 7.25, f"검문소 {i + 1}", ha="center", fontsize=9.5,
                color="#a04747", fontweight="bold")
arrow(ax, 7.0, 8.2, 7.0, 6.8, color="#2f6fb0", lw=1.6)
ax.text(7.25, 7.85, "단계별 지시서를 담당에게 전달하고\n요약 보고만 받는다", ha="left", va="center",
        fontsize=9.5, color="#2f6fb0")
box(ax, 0.4, 0.5, 6.0, 1.2, "verifier (검증 전담): 검문소마다 원자료와 산출 파일만 받아 대조표 작성",
    fc="#f4fbf6", ec="#2f8f4e", fontsize=9.5)
box(ax, 7.6, 0.5, 6.0, 1.2, "사람: 대조표의 결정적 항목과 표본을 파일에서 직접 확인, 통과·반려 결정",
    fc="#fdf9f4", ec="#c77b2f", fontsize=9.5)
ax.text(7.0, 1.95, "단계 사이의 전달은 대화가 아니라 산출물 폴더의 파일로만 한다",
        ha="center", va="center", fontsize=10, color="#333")
fig.savefig(FIG / "fig13_practice_team.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 그림 13-5
# 검문소 4에서 대조할 그림의 기준 모습 (실제 데이터)
d2023 = pd.read_csv(BASE / "data" / "sigungu_2023.csv", encoding="utf-8-sig")
d2013 = pd.read_csv(BASE / "data" / "sigungu_tfr_2013.csv", encoding="utf-8-sig")
d2013.loc[(d2013["시도"] == "인천") & (d2013["시군구"] == "남구"), "시군구"] = "미추홀구"
merged = d2023.merge(d2013, on=["시도", "시군구"], how="left", validate="one_to_one")
sub = merged.dropna(subset=["고령인구비율", "합계출산율"])
reg = stats.linregress(sub["고령인구비율"], sub["합계출산율"])

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))

ax = axes[0]
ax.scatter(sub["고령인구비율"], sub["합계출산율"], s=26, alpha=0.6,
           color="#4878a8", edgecolor="white", lw=0.4)
xs = pd.Series([sub["고령인구비율"].min(), sub["고령인구비율"].max()])
ax.plot(xs, reg.intercept + reg.slope * xs, color="#a04747", lw=2)
y25 = reg.intercept + reg.slope * 25
ax.plot([25, 25], [0, y25], ls="--", color="#777", lw=1)
ax.plot([0, 25], [y25, y25], ls="--", color="#777", lw=1)
ax.annotate(f"고령인구비율 25%일 때\n회귀선 높이 {y25:.3f}명", xy=(25, y25), xytext=(28, 0.42),
            fontsize=9.5, arrowprops=dict(arrowstyle="->", color="#555"))
ax.set_xlim(8, 48)
ax.set_ylim(0.2, 1.8)
ax.set_title(f"(가) 고령인구비율과 합계출산율 (2023년, n = {len(sub)})", fontsize=12)
ax.set_xlabel("고령인구비율 (%)")
ax.set_ylabel("합계출산율 (명)")
ax.text(0.03, 0.95, f"기울기 {reg.slope:.5f}, R제곱 {reg.rvalue ** 2:.3f}",
        transform=ax.transAxes, fontsize=10, va="top",
        bbox=dict(fc="white", ec="#bbb", boxstyle="round,pad=0.3"))

ax = axes[1]
both = merged.dropna(subset=["합계출산율", "합계출산율_2013"]).copy()
both["변화"] = both["합계출산율"] - both["합계출산율_2013"]
up = both[both["변화"] > 0]
down = both[both["변화"] <= 0]
ax.scatter(down["합계출산율_2013"], down["합계출산율"], s=24, alpha=0.55,
           color="#4878a8", edgecolor="white", lw=0.4, label=f"2023년이 낮은 곳 ({len(down)}곳)")
ax.scatter(up["합계출산율_2013"], up["합계출산율"], s=60, color="#c77b2f",
           edgecolor="black", lw=0.6, zorder=3, label=f"2023년이 높은 곳 ({len(up)}곳)")
ax.plot([0.3, 2.4], [0.3, 2.4], color="#777", lw=1, ls="--", label="변화 없음 (45도 선)")
offsets = {"의성군": (8, 4), "김제시": (8, -14), "영광군": (8, -10), "강화군": (8, -10)}
for _, r in up.iterrows():
    ax.annotate(f"{r['시도']} {r['시군구']}", (r["합계출산율_2013"], r["합계출산율"]),
                xytext=offsets.get(r["시군구"], (6, -10)), textcoords="offset points",
                fontsize=8.5)
lo = both.loc[both["변화"].idxmin()]
ax.annotate(f"{lo['시도']} {lo['시군구']}\n{lo['합계출산율_2013']:.3f} → {lo['합계출산율']:.3f}",
            (lo["합계출산율_2013"], lo["합계출산율"]), xytext=(1.85, 0.45), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color="#555"))
ax.set_xlim(0.3, 2.4)
ax.set_ylim(0.3, 2.4)
ax.set_title("(나) 2013년 대비 2023년 합계출산율 (228곳)", fontsize=12)
ax.set_xlabel("2013년 합계출산율 (명)")
ax.set_ylabel("2023년 합계출산율 (명)")
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "fig13_practice_checkpoint4.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob("fig13_practice*.png"))])

# ---------------------------------------------------------------- 그림 13-6
# 검문소 감도 행렬: 네 가지 오류를 어느 검문소의 어떤 지표가 잡아내는가
# 각 칸의 값은 code/ch13_practice.py의 [검문소 감도 행렬] 출력에서 그대로 옮긴 것이다.
from matplotlib.colors import ListedColormap  # noqa: E402

rows = [
    "A. 병합 키에서 시도를 빼고\n시군구만으로 병합 (345행)",
    "B. 결측이 있는 행(군위군)을\n삭제하고 병합 (228행)",
    "C. 결측을 0으로 채우고\n병합 (229행)",
    "D. 미추홀구를 옛 이름\n남구와 잇지 않음 (229행)",
]
cols = [
    "검문소 2\n병합 행 수",
    "검문소 2\n결측 개수",
    "검문소 3\n회귀 관측치 수",
    "검문소 3\n기울기·R제곱",
    "검문소 4\n(나) 비교 가능 곳",
    "검문소 4\n45도선 위 개수",
]
grid = [
    [1, 0, 1, 1, 1, 1],
    [1, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 1, 0],
]

fig, ax = plt.subplots(figsize=(12.2, 5.4))
ax.imshow(grid, cmap=ListedColormap(["#f4f4f6", "#f7e0dd"]), vmin=0, vmax=1, aspect="auto")
for i in range(len(rows)):
    for j in range(len(cols)):
        if grid[i][j]:
            ax.text(j, i, "잡힌다", ha="center", va="center", fontsize=11,
                    color="#a04747", fontweight="bold")
        else:
            ax.text(j, i, "놓친다", ha="center", va="center", fontsize=10.5, color="#888")
ax.set_xticks(range(len(cols)))
ax.set_xticklabels(cols, fontsize=10)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(rows, fontsize=10)
ax.tick_params(length=0)
ax.xaxis.set_ticks_position("top")
for j in range(len(cols) + 1):
    ax.axvline(j - 0.5, color="white", lw=2.5)
for i in range(len(rows) + 1):
    ax.axhline(i - 0.5, color="white", lw=2.5)
for j in (1.5, 3.5):
    ax.axvline(j, color="#999", lw=1.2, ls="--")
ax.grid(False)
ax.set_xlim(-0.5, len(cols) - 0.5)
ax.set_ylim(len(rows) - 0.5, -0.5)
fig.savefig(FIG / "fig13_practice_matrix.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", [p.name for p in sorted(FIG.glob("fig13_practice*.png"))])
