"""图1版式线框（规划用，不是成品）。按190 mm成品宽度、7 pt字号绘制，检查信息层级、阅读顺序和箭头走向。

python 图表/figure_01_layout_wireframe.py  ->  图表/_preview/figure_01_layout_wireframe.{png,pdf}
"""
import glob
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle  # noqa: E402

for f in glob.glob(os.path.join(os.environ.get("PAPER_FONT_DIR", "/projects/sandbox/work/fonts"), "**", "*.ttf"), recursive=True):
    font_manager.fontManager.addfont(f)
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans", "DejaVu Sans"], "font.size": 7,
                     "pdf.fonttype": 42, "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans",
                     "mathtext.it": "Liberation Sans:italic"})

W, H = 190, 104                       # mm
BLUE, ORANGE, GREY = "#3B6FB6", "#E07B39", "#8C939D"
FROZEN, INK, TEAL, GOLD = "#DDE2E8", "#222222", "#1A7F72", "#E9B32A"
PANEL = "#F5F6F8"

fig = plt.figure(figsize=(W / 25.4, H / 25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def box(x, y, w, h, fc="white", ec=GREY, lw=0.5, ls="-", r=1.2, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def txt(x, y, s, size=7, w="normal", c=INK, ha="center", va="center", **k):
    ax.text(x, y, s, fontsize=size, fontweight=w, color=c, ha=ha, va=va, zorder=5, **k)


def arrow(pts, c=INK, lw=0.75, ls="-", head=True):
    """折线箭头：只用水平/竖直段；实心闭合箭头，约为线宽的60%比例。"""
    for i in range(len(pts) - 1):
        last = i == len(pts) - 2
        style = "-|>,head_length=1.6,head_width=0.9" if (head and last) else "-"
        ax.add_patch(FancyArrowPatch(pts[i], pts[i + 1], arrowstyle=style, color=c, lw=lw, ls=ls,
                                     shrinkA=0, shrinkB=0.6 if last else 0, mutation_scale=lw * 2.4, zorder=4,
                                     joinstyle="miter", capstyle="butt"))


def placeholder(x, y, w, h, label):
    ax.add_patch(Rectangle((x, y), w, h, fc="#EEF1F4", ec="#B9C0C9", lw=0.4, ls=(0, (2, 1.5)), zorder=2))
    txt(x + w / 2, y + h / 2, label, size=6, c="#6B7380", linespacing=1.1)


def policy_icon(x, y, mode):
    """同一个策略图标在三处重复出现，只改变高亮部分（Stage 1 全部更新 / Stage 2 只更新LoRA）。"""
    w1, w2, w3, h = 11, 13, 6, 9
    enc_fc = "#D5E2F3" if mode == "bc" else FROZEN
    unet_fc = "#D5E2F3" if mode == "bc" else FROZEN
    enc_ec = BLUE if mode == "bc" else GREY
    box(x, y, w1, h, fc=enc_fc, ec=enc_ec, r=0.8)
    txt(x + w1 / 2, y + h / 2, "Encoders", size=6)
    box(x + w1 + 1, y, w2, h, fc=unet_fc, ec=enc_ec, r=0.8)
    txt(x + w1 + 1 + w2 / 2, y + h / 2, "1D U-Net", size=6)
    if mode == "rl":
        box(x + w1 + w2 + 2, y, w3, h, fc="#F8DCC6", ec=ORANGE, r=0.8, lw=0.75)
        txt(x + w1 + w2 + 2 + w3 / 2, y + h / 2, "LoRA", size=5.5, rotation=90)
    return x + w1 + w2 + 2 + (w3 if mode == "rl" else 0)


# ---------------- (a) Stage 1 ----------------
box(1, 54, 52, 49, fc=PANEL, ec="none", r=2)
txt(3, 100, "(a) Stage 1: BC pre-training", size=8, w="bold", ha="left")
placeholder(4, 72, 16, 16, "EGO-Planner\ndemos\n988 ep.")
arrow([(21, 80), (27, 80)], c=GREY)
xe = policy_icon(27.5, 75.5, "bc")
txt(40, 88.5, r"Policy $\pi_\theta$", size=7)
box(25, 58, 26, 8, fc="white", ec=BLUE, lw=0.6)
txt(38, 62, r"$\mathcal{L}_{\rm BC}+\lambda_{\rm geo}\mathcal{L}_{\rm geo}$", size=7)
arrow([(38, 66), (38, 75)], c=BLUE, lw=1.4)
txt(39.5, 70.5, "all parameters", size=6, c=BLUE, ha="left")

# ---------------- (b) Stage 2 闭环 ----------------
box(56, 54, 133, 49, fc=PANEL, ec="none", r=2)
txt(58, 100, "(b) Stage 2: DPPO post-training in the closed loop", size=8, w="bold", ha="left")
placeholder(60, 63, 26, 26, "Environment\n(kinematic sim.)\nreal render /\npoint-cloud shot")
arrow([(87, 80), (98, 80)], c=INK)
txt(92.5, 82.5, r"$o_\tau$", size=7)
xe = policy_icon(98.5, 75.5, "rl")
txt(114, 88.5, r"Policy $\pi_\theta$ (encoders, $W_0$ frozen)", size=6.5)
arrow([(xe + 0.5, 80), (xe + 9, 80)], c=INK)
txt(xe + 5, 82.5, "H4", size=7)
# 回环线：走面板上沿，不穿过任何模块
arrow([(xe + 9, 80), (xe + 9, 94), (73, 94), (73, 89.6)], c=INK)
txt((xe + 9 + 73) / 2, 95.8, r"execute H4 (4 $\times$ 0.3 s), observe, replan", size=6.5)
# 仅训练时存在的部分：虚线框
box(147, 57, 40, 33, fc="white", ec=ORANGE, lw=0.5, ls=(0, (3, 2)))
txt(167, 87.3, "training only", size=6, c=ORANGE)
box(150, 76, 15, 7, ec=GREY); txt(157.5, 79.5, r"reward $r_t$", size=6.5)
box(168, 76, 16, 7, ec=GREY); txt(176, 79.5, r"critic $V_\phi$", size=6.5)
box(150, 61, 34, 8, ec=ORANGE, lw=0.6); txt(167, 65, r"GAE $\hat A_t$  →  clipped PPO", size=6.5)
arrow([(157.5, 76), (157.5, 69.2)], c=GREY, lw=0.6)
arrow([(176, 76), (176, 69.2)], c=GREY, lw=0.6)
arrow([(xe + 9, 80), (xe + 9, 79.5), (150, 79.5)], c=GREY, lw=0.6, ls=(0, (2, 1.5)))
arrow([(150, 65), (xe - 3, 65), (xe - 3, 75.3)], c=ORANGE, lw=1.4)
txt(130, 63, "LoRA only", size=6, c=ORANGE)
txt(60, 57.5, "Evaluation runs the same loop without the training-only part.", size=6, c="#555B63", ha="left",
    style="italic")

# ---------------- (c) 一次决策 ----------------
box(1, 1, 188, 50, fc=PANEL, ec="none", r=2)
txt(3, 48, r"(c) One decision cycle $t$", size=8, w="bold", ha="left")
placeholder(5, 14, 28, 26, "local point clouds\n3 frames, 4096 pts\n(real render)")
box(5, 6, 28, 6, ec=GREY); txt(19, 9, r"state $s_\tau\in\mathbb{R}^9$", size=6.5)
arrow([(34, 25), (42, 25)])
box(42, 18, 16, 14, fc=FROZEN, ec=GREY, r=0.8); txt(50, 25, "PointNet\n+ state MLP", size=6.5, linespacing=1.1)
arrow([(58.5, 25), (66, 25)]); txt(62.2, 27.5, r"$c_t$", size=7)
for i, lab in enumerate([r"$Z_t^{K}$", r"$Z_t^{k}$", r"$Z_t^{0}$"]):
    x0 = 66 + i * 25
    placeholder(x0, 15, 20, 20, ["noise", "partially\ndenoised", "trajectory"][i])
    txt(x0 + 10, 12.5, lab, size=7)
    if i < 2:
        arrow([(x0 + 20.5, 25), (x0 + 24.5, 25)], c=TEAL)
txt(103.5, 40, r"conditional 1D U-Net, DDIM $\times$ 10 (details: Fig. 2, Fig. 3)", size=6.5)
arrow([(136.5, 25), (144, 25)])
placeholder(144, 13, 41, 24, "H16 → H8 window\nH4 solid (executed)\nH8 tail dashed")
txt(164.5, 9.5, "executed prefix H4, then replan", size=6.5)
# 放大关系：不画跨面板斜线（会穿过其他模块），在策略图标下方用短括线和文字指向(c)
ax.plot([98.5, 98.5, xe, xe], [74.2, 73.2, 73.2, 74.2], color="#9AA3AE", lw=0.5, zorder=3)
txt((98.5 + xe) / 2, 71.3, "one decision: see (c)", size=6, c="#6B7380")

out = Path(__file__).resolve().parent / "_preview"; out.mkdir(exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(out / f"figure_01_layout_wireframe.{ext}", dpi=400)
print("saved", out / "figure_01_layout_wireframe.png")
