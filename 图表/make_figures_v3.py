"""论文数据图（v3，英文标签，配色见《论文配图总体方案v3》§2.3）。只读数据，不改数据。

用法（仓库根目录）：
    python 图表/make_figures_v3.py --check          # 检查数据是否齐全，说明各图会用哪种版本
    python 图表/make_figures_v3.py                  # 生成全部数据图
    python 图表/make_figures_v3.py --only 5 7 S2    # 只生成部分
    python 图表/render_figures_v3.py                # 先渲染图4与图形摘要的三维画面（需 Blender/bpy）

输出：图表/v3/<name>.pdf（矢量，字体嵌入）与 .png（600 dpi）。

图号与内容：
  3c  图3(c) 一次评价回合中连续4个决策周期的重规划俯视图（插入PPT第3页下部）
  4   图4 场景类型与局部点云（三维渲染；没有渲染图时退化为真实几何俯视图）
  5   图5 不同障碍条件下的安全到达率（--ci both 时同时输出带/不带任务聚类bootstrap区间两版）
  6   图6 碰撞率—到达率
  7   图7 受阻任务行为指标（raincloud）
  8   图8 首段推进与闭环续飞（逐状态数据到位后(a)自动改为配对点图）
  S1  训练过程；S2 配对终点矩阵；S3 LoRA缩放
  D   类别轨迹占据密度图（全部路径到位前用205个案例回合出预览，文件名带 _preview）
  GA  图形摘要
EGO 结果（图表/data/b3_ego_records.json）到位后，图5、图6自动加入 EGO。
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fig_data as D  # noqa: E402

OUT = HERE / "v3"
RENDER = OUT / "render"
MM = 1 / 25.4

C = dict(bc="#3B6FB6", rl="#E07B39", ego="#4D4D4D", arr="#2A9D8F", col="#8E2C3A", to="#C9C9C9",
         traj="#1A7F72", goal="#E9B32A", obs="#A9B3C1", obs_f="#E6E8EC", ink="#222222", grey="#6B6B6B",
         grid="#E6E6E6", blocked="#8E2C3A", clear="#8C939D")
POL = {D.BC: "BC", D.RL: "Post-trained", D.EG: "EGO-Planner"}
PCOL = {D.BC: C["bc"], D.RL: C["rl"], D.EG: C["ego"]}


# ---------------- 风格 ----------------
def setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for f in glob.glob(os.path.join(os.environ.get("PAPER_FONT_DIR", "/projects/sandbox/work/fonts"), "**", "*.ttf"),
                       recursive=True):
        font_manager.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": ["Arial", "Liberation Sans", "DejaVu Sans"], "font.size": 7,
        "axes.titlesize": 7, "axes.labelsize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
        "legend.fontsize": 6.5, "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": C["ink"], "axes.labelcolor": C["ink"], "xtick.color": C["ink"], "ytick.color": C["ink"],
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": C["grid"], "grid.linewidth": 0.3,
        "axes.axisbelow": True, "legend.frameon": False, "mathtext.fontset": "stix",
        "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
        "hatch.linewidth": 0.5, "hatch.color": "white",
    })
    return plt


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=600)
    print("saved", OUT / name)


def plabel(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=8, fontweight="bold", ha="right" if x < 0 else "left",
            va="bottom")


# ---------------- 几何 ----------------
def draw_obstacles(ax, meta, fc=C["obs_f"], ec=C["obs"]):
    from matplotlib.patches import Circle, Polygon
    for g in meta["geometry"]:
        if g["shape"] == "box":
            hx, hy, c, s = g["size_x"] / 2, g["size_y"] / 2, np.cos(g["yaw"]), np.sin(g["yaw"])
            P = [(g["x"] + c * a * hx - s * b * hy, g["y"] + s * a * hx + c * b * hy) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            ax.add_patch(Polygon(P, closed=True, fc=fc, ec=ec, lw=0.5))
        else:
            ax.add_patch(Circle((g["x"], g["y"]), g["radius"], fc=fc, ec=ec, lw=0.5))


def goal_marker(ax, g, r=0.5):
    from matplotlib.patches import Circle
    ax.add_patch(Circle((g[0], g[1]), r, fc=C["goal"], ec="#9C7410", lw=0.5, zorder=6))


def start_marker(ax, s, yaw, size=0.9):
    from matplotlib.patches import Polygon
    c, sn = np.cos(yaw), np.sin(yaw)
    P = np.array([[1.0, 0], [-0.6, 0.55], [-0.35, 0], [-0.6, -0.55]]) * size
    P = P @ np.array([[c, sn], [-sn, c]]) + np.asarray(s[:2])
    ax.add_patch(Polygon(P, closed=True, fc="#213354", ec="none", zorder=7))


# =====================================================================
def pick_cycles(cs, meta, k=4, min_move=0.8, near=3.0):
    """自动选连续 k 个决策周期：每周期执行位移不小于 min_move、附近（near 米内）有障碍，
    按"执行方向总转角 + 相邻周期规划尾段改写量"打分取最大，使重规划在图上看得出来。"""
    obs = np.array([[g["x"], g["y"]] for g in meta["geometry"]])
    rad = np.array([g["radius"] if g["shape"] != "box" else 0.5 * min(g["size_x"], g["size_y"]) for g in meta["geometry"]])
    best, arg = -1.0, None
    for i in range(len(cs) - k + 1):
        w = cs[i:i + k]
        disp = [np.subtract(c["executed_path"][-1], c["executed_path"][0])[:2] for c in w]
        if min(np.linalg.norm(d) for d in disp) < min_move:
            continue
        P = np.vstack([np.array(c["planned_policy_path"])[:, :2] for c in w])
        if np.min(np.linalg.norm(P[:, None] - obs[None], axis=2) - rad[None]) > near:
            continue
        ang = [np.arctan2(d[1], d[0]) for d in disp]
        turn = sum(abs((b - a + np.pi) % (2 * np.pi) - np.pi) for a, b in zip(ang[:-1], ang[1:]))
        rew = sum(np.linalg.norm(np.subtract(a["planned_policy_path"][-1], b["planned_policy_path"][4]))
                  for a, b in zip(w[:-1], w[1:]))
        score = turn * 2.0 + rew
        if score > best:
            best, arg = score, i
    if arg is None:
        return pick_cycles(cs, meta, k, min_move, near * 2) if near < 20 else list(range(k))
    return list(range(arg, arg + k))


def fig3c(plt, task=30, policy=D.RL, repeat=1, cycles=None):
    meta = D.task_meta(task)
    cs = D.case(task, policy, repeat)["cycles"]
    cycles = cycles or pick_cycles(cs, meta)
    sel = [cs[k] for k in cycles]
    fig, ax = plt.subplots(figsize=(190 * MM, 55 * MM))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.16)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    draw_obstacles(ax, meta)
    route = np.array([cs[0]["pre"]] + [q for c in cs for q in c["executed_path"][1:]])
    ax.plot(route[:, 0], route[:, 1], color="#BFC4CB", lw=0.7, zorder=2)  # 整个回合路线作背景
    P = np.vstack([np.array(c["planned_policy_path"])[:, :2] for c in sel])
    n = len(sel)
    for i, c in enumerate(sel):
        a = 0.35 + 0.65 * (i + 1) / n
        pp = np.array(c["planned_policy_path"])
        ex = np.array(c["executed_path"])
        ax.plot(pp[4:, 0], pp[4:, 1], ls=(0, (2.2, 1.6)), lw=1.0, color=C["traj"], alpha=a, zorder=4)
        ax.plot(ex[:, 0], ex[:, 1], lw=1.8, color=C["traj"], alpha=a, solid_capstyle="round", zorder=5)
        ax.plot(*ex[0, :2], "o", ms=3.4, mfc="white", mec=C["traj"], mew=0.9, zorder=6)
        lab = "$t$" if i == 0 else f"$t+{i}$"
        d = ex[-1, :2] - ex[0, :2]; nrm = np.array([-d[1], d[0]]) / max(1e-6, np.linalg.norm(d))
        ax.annotate(lab, ex[0, :2], xytext=tuple(nrm * 9), textcoords="offset points", ha="center", va="center",
                    fontsize=7, color=C["traj"])
    m = 2.0
    xl = [P[:, 0].min() - m, P[:, 0].max() + m]
    yl = [P[:, 1].min() - m, P[:, 1].max() + m]
    if cycles[0] == 0:
        start_marker(ax, meta["start"], meta["start_yaw"], 0.35)
    gx, gy = meta["goal"][:2]
    if xl[0] - 3 < gx < xl[1] + 3 and yl[0] - 3 < gy < yl[1] + 3:
        goal_marker(ax, meta["goal"])
        xl = [min(xl[0], gx - 1), max(xl[1], gx + 1)]; yl = [min(yl[0], gy - 1), max(yl[1], gy + 1)]
    # 按坐标轴宽高比扩展视野，避免大片空白
    fig.canvas.draw()
    bb = ax.get_position(); ar = (bb.width * fig.get_figwidth()) / (bb.height * fig.get_figheight())
    w, h = xl[1] - xl[0], yl[1] - yl[0]
    if w / h < ar:
        c = sum(xl) / 2; xl = [c - h * ar / 2, c + h * ar / 2]
    else:
        c = sum(yl) / 2; yl = [c - w / ar / 2, c + w / ar / 2]
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect("equal", adjustable="box")
    x0, y0 = xl[1] - 2.6, yl[0] + 0.4
    ax.plot([x0, x0 + 2], [y0, y0], color=C["ink"], lw=1.2, solid_capstyle="butt")
    ax.text(x0 + 1, y0 + 0.2, "2 m", ha="center", va="bottom", fontsize=6.5)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=C["traj"], lw=1.8, label="executed H4"),
         Line2D([], [], color=C["traj"], lw=1.0, ls=(0, (2.2, 1.6)), label="planned but not executed (rest of H8)"),
         Line2D([], [], marker="o", ls="", ms=3.4, mfc="white", mec=C["traj"], label="decision point (replan)"),
         Line2D([], [], color="#BFC4CB", lw=0.7, label="rest of the episode"),
         __import__("matplotlib.patches", fromlist=["Patch"]).Patch(fc=C["obs_f"], ec=C["obs"], lw=0.5, label="obstacle")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=5, handlelength=2.0, columnspacing=1.0)
    print(f"[图3(c)] 任务{task} {POL.get(policy, policy)} 第{repeat}次重复，决策周期 {cycles}")
    save(fig, "figure_03c_replanning"); plt.close(fig)


# =====================================================================
FIG4_TASKS = dict(a=12, b=30, c=55, d=7)
FIG4_TITLES = dict(a="(a) Bottleneck corridor", b="(b) U-trap", c="(c) S-turn, multiple obstacles",
                   d="(d) Low density: front offset", e="(e) Local point cloud (body frame)")


def fig4(plt):
    from PIL import Image
    fig = plt.figure(figsize=(190 * MM, 62 * MM))
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 1, 1.3], wspace=0.06, left=0.005, right=0.995, top=0.90, bottom=0.12)
    used_render = True
    for i, k in enumerate("abcde"):
        ax = fig.add_subplot(gs[0, i]); ax.axis("off")
        ax.set_title(FIG4_TITLES[k], loc="left", fontsize=7, pad=2)
        png = RENDER / f"fig4_{k}.png"
        if png.exists():
            im = Image.open(png); ax.imshow(im); W, H = im.size
            an = json.loads(png.with_suffix(".anchors.json").read_text())
            if "bar0" in an:
                (x0, y0), (x1, y1) = an["bar0"], an["bar1"]
                ax.text((x0 + x1) / 2 * W, max(y0, y1) * H + 0.03 * H, "2 m", ha="center", va="top", fontsize=6.5)
            if k == "e":
                for key, lab in (("x_tip", "$x_b$"), ("y_tip", "$y_b$"), ("z_tip", "$z_b$")):
                    x, y = an[key]; ax.text(x * W, y * H, lab, fontsize=7, ha="center", va="center")
        else:
            used_render = False
            if k == "e":
                fig4e_fallback(ax)
            else:
                fig4_topview(ax, FIG4_TASKS[k])
    # 图例
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle
    h = [Line2D([], [], marker=(3, 0, -90), ls="", ms=5, mfc="#213354", mec="none", label="start (UAV, enlarged)"),
         Line2D([], [], marker="o", ls="", ms=5, mfc=C["goal"], mec="#9C7410", label="goal sphere (r = 0.5 m)"),
         Line2D([], [], color=C["blocked"], lw=1.2, ls=(0, (3, 2)), label="straight line blocked"),
         Line2D([], [], color=C["clear"], lw=1.2, ls=(0, (3, 2)), label="straight line clear")]
    fig.legend(handles=h, loc="lower center", ncol=4, bbox_to_anchor=(0.42, 0.0), handlelength=2.4, columnspacing=1.6)
    if not used_render:
        print("[图4] 未找到全部渲染图（图表/v3/render/fig4_*.png），缺失面板用真实几何俯视图代替；运行 render_figures_v3.py 可生成渲染。")
    save(fig, "figure_04_scenes"); plt.close(fig)


def fig4_topview(ax, task):
    meta = D.task_meta(task)
    ax.set_aspect("equal")
    draw_obstacles(ax, meta, fc=C["obs"], ec="#7D8796")
    s, g = meta["start"], meta["goal"]
    ax.plot([s[0], g[0]], [s[1], g[1]], ls=(0, (3, 2)), lw=1.0, color=C["blocked"] if meta["line_blocked"] else C["clear"])
    start_marker(ax, s, meta["start_yaw"], 1.2); goal_marker(ax, g)
    ax.autoscale_view(); ax.margins(0.05)


def fig4e_fallback(ax):
    sys.path.insert(0, str(HERE / "render"))
    import scene_data as sd
    meta = D.task_meta(FIG4_TASKS["c"])
    pts, *_ = sd.synth_point_cloud(meta, np.array(meta["start"]), meta["start_yaw"])
    yaw = meta["start_yaw"]; c, s = np.cos(-yaw), np.sin(-yaw)
    B = (pts - meta["start"]) @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]).T
    ax.scatter(B[:, 0], B[:, 1], c=B[:, 2], s=0.4, cmap="viridis", vmin=B[:, 2].min() - 0.3 * np.ptp(B[:, 2]))
    ax.set_aspect("equal")


# =====================================================================
ORIG_G = [("dense_blocked", "Dense\nblocked"), ("utrap_blocked", "U-trap\nblocked"),
          ("dense_unblocked", "Dense\nunblocked"), ("low_density", "Low\ndensity")]
NEW_G = [("dense_blocked", "Dense\nblocked"), ("dense_unblocked", "Dense\nunblocked"), ("low_density", "Low\ndensity")]


def group_stats():
    """返回 {('orig'|'new', group, policy): (rate, lo, hi, n, coll_rate)}。"""
    out = {}
    R = D.records((D.BC, D.RL, D.EG))
    og = D.original_groups(R)
    for g, _ in ORIG_G + [("dense", ""), ("all", "")]:
        for p in (D.EG, D.BC, D.RL):
            xs = og[g].get(p, [])
            if xs:
                lo, hi = D.cluster_bootstrap(D.per_task_counts(xs))
                out[("orig", g, p)] = (D.rate(xs), lo, hi, len(xs), D.rate(xs, "collision"))
    T = D.new_tasks()
    for g, _ in NEW_G + [("dense", ""), ("all", "")]:
        ts = [t for t in T if g in D.new_group_keys(t)]
        for p in (D.EG, D.BC, D.RL):
            k = {D.BC: "bc", D.RL: "rl", D.EG: "ego"}[p]
            if not ts or not all(k in t["counts"] for t in ts):
                continue
            per = [(t["counts"][k][0], sum(t["counts"][k])) for t in ts]
            n = sum(b for _, b in per)
            lo, hi = D.cluster_bootstrap(per)
            out[("new", g, p)] = (100 * sum(a for a, _ in per) / n, lo, hi, n,
                                  100 * sum(t["counts"][k][1] for t in ts) / n)
    return out


def fig5(plt, ci="both"):
    S = group_stats()
    has_ego = any(k[2] == D.EG for k in S)
    pols = ([D.EG] if has_ego else []) + [D.BC, D.RL]
    for with_ci in ([True, False] if ci == "both" else [ci == "bootstrap"]):
        fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 68 * MM), gridspec_kw=dict(width_ratios=[4, 3], wspace=0.12),
                                sharey=True)
        w = 0.26
        for ax, setk, groups, lab in ((axs[0], "orig", ORIG_G, "(a)"), (axs[1], "new", NEW_G, "(b)")):
            x = np.arange(len(groups))
            off = (np.arange(len(pols)) - (len(pols) - 1) / 2) * w
            for j, p in enumerate(pols):
                vals = [S.get((setk, g, p)) for g, _ in groups]
                v = np.array([s[0] if s else np.nan for s in vals])
                kw = dict(color=PCOL[p], edgecolor="white", lw=0.4)
                if p == D.EG:
                    kw.update(hatch="////")
                bars = ax.bar(x + off[j], v, w * 0.96, label=POL[p], **kw)
                if with_ci:
                    lo = np.array([s[1] if s else np.nan for s in vals]); hi = np.array([s[2] if s else np.nan for s in vals])
                    ax.errorbar(x + off[j], v, yerr=[v - lo, hi - v], fmt="none", ecolor=C["ink"], elinewidth=0.6, capsize=1.6,
                                capthick=0.6)
                    top = hi
                else:
                    top = v
                for xx, vv, tt in zip(x + off[j], v, top):
                    if np.isfinite(vv):
                        ax.text(xx, tt + 1.2, f"{vv:.1f}", ha="center", va="bottom", fontsize=5.8,
                                rotation=90 if with_ci else 0)
            ns = [S[(setk, g, D.BC)][3] for g, _ in groups]
            ax.set_xticks(x, [f"{l}\nn = {n}" for (_, l), n in zip(groups, ns)])
            ax.tick_params(axis="x", length=0)
            ax.set_ylim(0, 92 if with_ci else 62)
            ax.text(0.0, 1.0, "Original tasks" if setk == "orig" else "New tasks", transform=ax.transAxes, fontsize=7,
                    va="bottom", ha="left")
            plabel(ax, lab, x=-0.01 if setk == "orig" else -0.02)
        axs[0].set_ylabel("Safe arrival rate (%)")
        axs[0].legend(loc="upper right", ncol=len(pols), bbox_to_anchor=(1.0, 1.02), handlelength=1.2, columnspacing=1.0)
        name = "figure_05_arrival_by_category" + ("" if with_ci else "_noCI")
        save(fig, name); plt.close(fig)
    if not has_ego:
        print("[图5] 未找到 EGO 结果（图表/data/b3_ego_records.json），只画 BC 与后训练两组柱。")
    if ci in ("both", "bootstrap"):
        print("[图5] 误差线：以任务为重采样单位的 bootstrap 95% 区间（4000次，种子20261031）。")


def fig6(plt):
    S = group_stats()
    # (集合, 分组, 标签, 标签偏移pt, 对齐)；偏移按当前数据手调，数据变化后如有重叠再调
    sets = [("orig", "dense_blocked", "Dense blocked", (6, 0), "left"),
            ("orig", "dense_unblocked", "Dense unblocked", (6, 3), "left"),
            ("orig", "low_density", "Low density", (-6, -6), "right"),
            ("new", "dense", "New: dense", (6, -4), "left"),
            ("new", "low_density", "New: low density", (6, 0), "left")]
    fig, ax = plt.subplots(figsize=(90 * MM, 85 * MM))
    ax.grid(True, axis="both")
    # 左上角极浅渐变
    gx, gy = np.meshgrid(np.linspace(0, 1, 200), np.linspace(0, 1, 200))
    z = np.clip(1 - np.hypot(gx, 1 - gy) / 0.9, 0, 1) ** 1.6
    from matplotlib.colors import LinearSegmentedColormap
    cm = LinearSegmentedColormap.from_list("g", ["#FFFFFF00", "#2A9D8F33"])
    ax.imshow(z, extent=(0, 80, -2, 60), origin="lower", cmap=cm, aspect="auto", zorder=0)
    ax.text(2, 56.5, "safer & more arrivals", fontsize=6.5, color=C["arr"], ha="left", va="top")

    def ms(n):
        return 6 + n * 0.12
    for setk, g, lab, offs, ha in sets:
        b, r = S.get((setk, g, D.BC)), S.get((setk, g, D.RL))
        if not b or not r:
            continue
        filled = setk == "orig"
        ax.annotate("", xy=(r[4], r[0]), xytext=(b[4], b[0]),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color=C["grey"], shrinkA=2.5, shrinkB=3, mutation_scale=7))
        for s_, p in ((b, D.BC), (r, D.RL)):
            ax.scatter(s_[4], s_[0], s=ms(s_[3]), marker="o", facecolor=PCOL[p] if filled else "white",
                       edgecolor=PCOL[p], lw=1.0, zorder=5)
        e = S.get((setk, g, D.EG))
        if e:
            ax.scatter(e[4], e[0], s=ms(e[3]), marker="D", facecolor=C["ego"] if filled else "white",
                       edgecolor=C["ego"], lw=1.0, zorder=5)
        ax.annotate(lab, (r[4], r[0]), xytext=offs, textcoords="offset points", fontsize=6.2, va="center", ha=ha)
    ax.set_xlim(0, 80); ax.set_ylim(-2, 60)
    ax.set_xlabel("Collision rate (%)"); ax.set_ylabel("Safe arrival rate (%)")
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", ms=4.5, mfc=C["bc"], mec=C["bc"], label="BC"),
         Line2D([], [], marker="o", ls="", ms=4.5, mfc=C["rl"], mec=C["rl"], label="Post-trained")]
    if any(k[2] == D.EG for k in S):
        h.append(Line2D([], [], marker="D", ls="", ms=4, mfc=C["ego"], mec=C["ego"], label="EGO-Planner"))
    h += [Line2D([], [], marker="o", ls="", ms=4.5, mfc=C["grey"], mec=C["grey"], label="original tasks"),
          Line2D([], [], marker="o", ls="", ms=4.5, mfc="white", mec=C["grey"], label="new tasks")]
    for n in (100, 300):
        h.append(ax.scatter([], [], s=ms(n), facecolor="none", edgecolor=C["grey"], lw=0.8, label=f"n = {n}"))
    ax.legend(handles=h, loc="upper right", ncol=2, handletextpad=0.4, columnspacing=0.8, labelspacing=0.5)
    save(fig, "figure_06_collision_vs_arrival"); plt.close(fig)


# =====================================================================
def raincloud(ax, data, pos, color, half=0.17):
    data = np.asarray(data, float)
    # 高斯核密度（Scott带宽，numpy实现，不依赖scipy）；只在数据范围内画，不外推
    sd = data.std(ddof=1) if len(data) > 1 else 0.0
    if sd > 0:
        bw = sd * len(data) ** (-1 / 5)
        ys = np.linspace(data.min(), data.max(), 200)
        d = np.exp(-0.5 * ((ys[:, None] - data[None, :]) / bw) ** 2).sum(1)
        d = d / d.max() * half
        ax.fill_betweenx(ys, pos - d, pos, color=color, alpha=0.35, lw=0)
        ax.plot(pos - d, ys, color=color, lw=0.6)
    q1, med, q3 = np.percentile(data, [25, 50, 75])
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((pos - 0.025, q1), 0.05, q3 - q1, fc="white", ec=color, lw=0.7, zorder=4))
    ax.plot([pos - 0.025, pos + 0.025], [med, med], color=C["ink"], lw=0.9, zorder=5)
    rng = np.random.default_rng(0)
    ax.scatter(pos + 0.05 + rng.random(len(data)) * 0.09, data, s=1.2, color=color, alpha=0.35, lw=0, zorder=3)


def fig7(plt):
    R = D.records()
    fams = D.DENSE
    sel = {(f, p): [r for r in R if r["policy"] == p and r["family"] == f and r["blocked"]] for f in fams for p in (D.BC, D.RL)}
    fig, axs = plt.subplots(1, 3, figsize=(190 * MM, 62 * MM), gridspec_kw=dict(width_ratios=[1.2, 1.2, 0.9], wspace=0.32))
    for ax, key, ylab, lab in ((axs[0], "max_cross_track_m", "Max. lateral deviation (m)", "(a)"),
                               (axs[1], "normalized_best_gain", "Best progress (fraction of $D_0$)", "(b)")):
        for i, f in enumerate(fams):
            for j, p in enumerate((D.BC, D.RL)):
                raincloud(ax, [x[key] for x in sel[(f, p)]], i + (j - 0.5) * 0.42, PCOL[p])
        ax.set_xticks(range(3), [f"{D.FAM_EN[f]}\nn = {len(sel[(f, D.BC)])}" for f in fams]); ax.tick_params(axis="x", length=0)
        ax.set_xlim(-0.6, 2.6); ax.set_ylabel(ylab); plabel(ax, lab)
    ax = axs[2]; w = 0.34; x = np.arange(3)
    for j, p in enumerate((D.BC, D.RL)):
        v = [100 * sum(r["crossed_goal_plane"] for r in sel[(f, p)]) / len(sel[(f, p)]) for f in fams]
        b = ax.bar(x + (j - 0.5) * w, v, w * 0.95, color=PCOL[p], label=POL[p])
        for bb, vv in zip(b, v):
            ax.text(bb.get_x() + bb.get_width() / 2, vv + 0.6, f"{vv:.1f}", ha="center", va="bottom", fontsize=5.8)
    ax.set_xticks(x, [D.FAM_EN[f] for f in fams]); ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Episodes crossing the goal plane (%)"); ax.set_ylim(0, 32); plabel(ax, "(c)")
    ax.legend(loc="upper left", handlelength=1.2)
    save(fig, "figure_07_behavior_metrics"); plt.close(fig)


# =====================================================================
def fig8(plt):
    s = D.SAME_STATE
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 62 * MM), gridspec_kw=dict(width_ratios=[1.0, 1.25], wspace=0.45))
    ax = axs[0]
    if D.P3S.exists():
        S = D.first_step_by_state()
        S = sorted(S, key=lambda r: r["rl_mean_progress_m"] - r["bc_mean_progress_m"])
        ys = np.arange(len(S))
        for y, r in zip(ys, S):
            ax.plot([r["bc_mean_progress_m"], r["rl_mean_progress_m"]], [y, y], color="#BBBBBB", lw=0.6, zorder=1)
        ax.scatter([r["bc_mean_progress_m"] for r in S], ys, s=9, color=C["bc"], zorder=3, label="BC", lw=0)
        ax.scatter([r["rl_mean_progress_m"] for r in S], ys, s=9, color=C["rl"], zorder=3, label="Post-trained", lw=0)
        yt = len(S) + 1.2
        ax.plot([s["mean_progress"]["bc"], s["mean_progress"]["rl"]], [yt, yt], color="#888888", lw=0.9)
        ax.scatter([s["mean_progress"]["bc"]], [yt], s=22, color=C["bc"], zorder=3, lw=0)
        ax.scatter([s["mean_progress"]["rl"]], [yt], s=22, color=C["rl"], zorder=3, lw=0)
        ax.set_yticks(list(ys) + [yt], [""] * len(S) + ["all states"]); ax.tick_params(axis="y", length=0)
        ax.axvline(0, color=C["grey"], lw=0.5)
        ax.set_xlabel("First-step goal progress (m)"); ax.grid(True, axis="x"); ax.grid(False, axis="y")
        ax.text(0.0, 1.02, "rows: 24 intermediate states, sorted by difference", transform=ax.transAxes, ha="left",
                va="bottom", fontsize=6, color=C["grey"])
        ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.07), ncol=2, handletextpad=0.2, columnspacing=1.0)
    else:
        labs = ["BC", "Post-trained"]
        v = [s["mean_progress"]["bc"], s["mean_progress"]["rl"]]
        b = ax.bar(labs, v, 0.55, color=[C["bc"], C["rl"]])
        for bb, vv, k in zip(b, v, ("bc", "rl")):
            p, n = s["positive"][k]
            ax.text(bb.get_x() + bb.get_width() / 2, vv + 0.012, f"{vv:.3f} m\n{100 * p / n:.1f}% positive",
                    ha="center", va="bottom", fontsize=6)
        ax.set_ylim(0, 0.8); ax.set_ylabel("Mean first-step goal progress (m)")
        ax.text(0.5, -0.2, "1200 open-loop samples per policy (24 states × 50)", transform=ax.transAxes, ha="center",
                fontsize=6, color=C["grey"])
        print("[图8] 未找到逐状态数据（图表/data/p3_first_step_by_state.json），(a)使用汇总柱图。")
    plabel(ax, "(a)")
    ax = axs[1]
    groups = [("positive", "first step positive"), ("non_positive", "first step not positive")]
    left = np.zeros(2)
    for i, (oc, lab, col) in enumerate((("reached", "arrival", C["arr"]), ("collision", "collision", C["col"]),
                                         ("time_limit", "timeout", C["to"]))):
        vals = np.array([100 * s["rl_cont"][g][i] / sum(s["rl_cont"][g]) for g, _ in groups])
        ax.barh([0, 1], vals, left=left, color=col, height=0.55, label=lab, edgecolor="white", lw=0.5)
        for y, (l, v) in enumerate(zip(left, vals)):
            if v >= 6:
                ax.text(l + v / 2, y, f"{v:.0f}%", ha="center", va="center", fontsize=6.2,
                        color="white" if oc != "time_limit" else C["ink"])
        left += vals
    ax.set_yticks([0, 1], [f"{lab}\n(n = {sum(s['rl_cont'][g])})" for g, lab in groups]); ax.invert_yaxis()
    ax.tick_params(axis="y", length=0); ax.set_xlim(0, 100); ax.grid(True, axis="x"); ax.grid(False, axis="y")
    ax.set_xlabel("Closed-loop outcome of post-trained continuations (%)")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.0, columnspacing=1.0)
    plabel(ax, "(b)", y=1.08)
    save(fig, "figure_08_first_step_vs_closed_loop"); plt.close(fig)


# =====================================================================
def figS1(plt, ckpt=32, w=16):
    u, tot, arr, col, ret = D.training_curve()

    def roll(num, den):
        k = np.ones(w)
        n = np.convolve(num, k)[:len(num)]; d = np.convolve(den, k)[:len(den)]
        return 100 * n / np.where(d > 0, d, np.nan)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(140 * MM, 80 * MM), sharex=True, gridspec_kw=dict(hspace=0.15))
    raw_a, raw_c = 100 * arr / np.where(tot > 0, tot, np.nan), 100 * col / np.where(tot > 0, tot, np.nan)
    a1.plot(u, raw_a, color=C["arr"], lw=0.4, alpha=0.3); a1.plot(u, raw_c, color=C["col"], lw=0.4, alpha=0.3)
    a1.plot(u, roll(arr, tot), color=C["arr"], lw=1.0, label="arrival")
    a1.plot(u, roll(col, tot), color=C["col"], lw=1.0, ls=(0, (4, 1.5)), label="collision")
    a1.set_ylabel("Training episodes (%)"); a1.legend(loc="upper right", ncol=2)
    r = np.where(np.isfinite(ret), ret, 0)
    a2.plot(u, ret, color=C["rl"], lw=0.4, alpha=0.3)
    a2.plot(u, np.convolve(r, np.ones(w))[:len(r)] / np.convolve(np.isfinite(ret), np.ones(w))[:len(r)], color=C["rl"], lw=1.0)
    a2.set_ylabel("Mean episode return"); a2.set_xlabel("Outer update")
    for ax in (a1, a2):
        ax.axvline(ckpt, color=C["ink"], ls=":", lw=0.8)
    a1.text(ckpt + 4, a1.get_ylim()[1] * 0.92, "checkpoint used", fontsize=6.5, va="top")
    a1.text(0.0, 1.02, f"{w}-update moving average; faint lines: per-update values", transform=a1.transAxes,
            fontsize=6, color=C["grey"], va="bottom")
    plabel(a1, "(a)"); plabel(a2, "(b)")
    save(fig, "figure_S1_training_curve"); plt.close(fig)


def figS2(plt):
    M = D.paired_matrix()
    names = ["arrival", "collision", "timeout"]
    fig, ax = plt.subplots(figsize=(90 * MM, 78 * MM))
    ax.grid(False)
    ax.imshow(M, cmap="Blues", vmin=0, vmax=M.max() * 1.25)
    from matplotlib.patches import Rectangle
    for i in range(3):
        for j in range(3):
            pct = 100 * M[i, j] / M[i].sum()
            dark = M[i, j] > M.max() * 0.6
            ax.text(j, i - 0.08, f"{M[i, j]}", ha="center", va="center", fontsize=8, color="white" if dark else C["ink"])
            ax.text(j, i + 0.22, f"{pct:.0f}% of row", ha="center", va="center", fontsize=5.8,
                    color="white" if dark else C["grey"])
            if j == 0 and i > 0:
                ax.add_patch(Rectangle((j - 0.47, i - 0.47), 0.94, 0.94, fc="none", ec=C["arr"], lw=1.4))
            if i == 0 and j > 0:
                ax.add_patch(Rectangle((j - 0.47, i - 0.47), 0.94, 0.94, fc="none", ec=C["col"], lw=1.4))
    ax.set_xticks(range(3), names); ax.set_yticks(range(3), names)
    ax.set_xlabel("Post-trained outcome"); ax.set_ylabel("BC outcome")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    ax.text(0, 1.03, f"paired episodes, n = {M.sum()}; green frame: gained, red frame: lost", transform=ax.transAxes,
            fontsize=6, color=C["grey"], va="bottom")
    save(fig, "figure_S2_paired_matrix"); plt.close(fig)


def figS3(plt):
    d = D.lora_scale()
    keys = sorted(d["scales"], key=float)
    s = [float(k) for k in keys]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(140 * MM, 60 * MM), gridspec_kw=dict(wspace=0.35))
    for oc, lab, col, mk in (("reached", "arrival", C["arr"], "o"), ("collision", "collision", C["col"], "s"),
                             ("time_limit", "timeout", "#9A9A9A", "^")):
        v = [100 * d["scales"][k]["done_reason"][oc] / d["scales"][k]["episodes"] for k in keys]
        a1.plot(s, v, marker=mk, ms=3.5, lw=1.0, color=col, label=lab)
        a1.annotate(lab, (s[-1], v[-1]), xytext=(4, 0), textcoords="offset points", fontsize=6.2, va="center", color=col)
    a1.set_xticks(s); a1.set_xlim(-0.08, 1.25); a1.set_xlabel("LoRA scale $s$"); a1.set_ylabel("Episodes (%)")
    a1.text(0, 1.02, f"all original tasks, n = {d['scales'][keys[0]]['episodes']} per scale", transform=a1.transAxes,
            fontsize=6, color=C["grey"], va="bottom")
    plabel(a1, "(a)")
    for f, mk, ls in zip(D.DENSE, ("o", "s", "^"), ("-", (0, (4, 1.5)), (0, (1.5, 1.2)))):
        v = [100 * d["scales"][k]["by_family"][f]["success_rate"] for k in keys]
        a2.plot(s, v, marker=mk, ms=3.5, lw=1.0, ls=ls, color=C["arr"], label=D.FAM_EN[f])
        a2.annotate(D.FAM_EN[f], (s[-1], v[-1]), xytext=(4, 0), textcoords="offset points", fontsize=6.2, va="center")
    a2.set_xticks(s); a2.set_xlim(-0.08, 1.3); a2.set_xlabel("LoRA scale $s$"); a2.set_ylabel("Safe arrival rate (%)")
    nf = d["scales"][keys[0]]["by_family"][D.DENSE[0]]["episodes"]
    a2.text(0, 1.02, f"dense families, n = {nf} per family and scale", transform=a2.transAxes, fontsize=6,
            color=C["grey"], va="bottom")
    plabel(a2, "(b)")
    save(fig, "figure_S3_lora_scale"); plt.close(fig)


# =====================================================================
def occupancy(paths, bins=(100, 100), xr=(-0.5, 1.5), yr=(-1.0, 1.0)):
    H = np.zeros(bins[::-1])
    for start, goal, P in paths:
        u = np.asarray(goal[:2]) - np.asarray(start[:2]); Dn = np.linalg.norm(u); u /= Dn
        nrm = np.array([-u[1], u[0]])
        Q = (P[:, :2] - start[:2]) / Dn
        X, Y = Q @ u, Q @ nrm
        ix = np.floor((X - xr[0]) / (xr[1] - xr[0]) * bins[0]).astype(int)
        iy = np.floor((Y - yr[0]) / (yr[1] - yr[0]) * bins[1]).astype(int)
        ok = (ix >= 0) & (ix < bins[0]) & (iy >= 0) & (iy < bins[1])
        cells = set(zip(iy[ok], ix[ok]))
        for c in cells:
            H[c] += 1
    return H / max(1, len(paths)) * 100


def figD(plt):
    full = D.PATHS.exists()
    P = D.all_paths() if full else D.case_paths()
    sel = {}
    for p in (D.BC, D.RL):
        L = []
        for pol, task, rep, path in P:
            if pol != p:
                continue
            m = D.task_meta(task)
            if m["family"] in D.DENSE and m["line_blocked"]:
                L.append((np.array(m["start"]), np.array(m["goal"]), path))
        sel[p] = L
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 70 * MM), gridspec_kw=dict(wspace=0.08))
    xr, yr = (-0.5, 1.5), (-1.0, 1.0)
    Hs = {p: occupancy(sel[p], xr=xr, yr=yr) for p in sel}
    nz = np.concatenate([h[h > 0] for h in Hs.values()])
    vmax = float(np.percentile(nz, 98)) if len(nz) else 1.0  # 起点附近所有回合都经过，不让它压缩色阶
    import matplotlib
    cmap = matplotlib.colormaps["GnBu"].copy(); cmap.set_under("white")
    for ax, p, lab in ((axs[0], D.BC, "(a)"), (axs[1], D.RL, "(b)")):
        ax.grid(False)
        im = ax.imshow(Hs[p], origin="lower", extent=(*xr, *yr), cmap=cmap, vmin=1e-9, vmax=vmax, aspect="equal")
        ax.plot(0, 0, marker=(3, 0, -90), ms=6, color="#213354"); ax.plot(1, 0, "o", ms=6, mfc=C["goal"], mec="#9C7410")
        ax.plot([0, 1], [0, 0], ls=(0, (3, 2)), lw=0.7, color=C["blocked"])
        ax.set_xlabel("Along start–goal line (fraction of $D_0$)")
        ax.text(0.02, 0.97, f"{POL[p]}, n = {len(sel[p])} episodes", transform=ax.transAxes, va="top", fontsize=6.5)
        plabel(ax, lab)
    axs[0].set_ylabel("Lateral offset (fraction of $D_0$)"); axs[1].set_yticklabels([])
    cb = fig.colorbar(im, ax=axs, fraction=0.025, pad=0.01, extend="max"); cb.set_label("Episodes visiting the cell (%)"); cb.outline.set_linewidth(0.4)
    name = "figure_D_occupancy_dense_blocked" + ("" if full else "_preview")
    save(fig, name); plt.close(fig)
    if not full:
        print(f"[密度图] 未找到全部路径（图表/data/v3_executed_paths.json），用案例回合预览：BC {len(sel[D.BC])}、后训练 {len(sel[D.RL])} 个回合。")


# =====================================================================
def figGA(plt):
    from PIL import Image
    S = group_stats()
    d_b, d_r = S[("orig", "dense", D.BC)][0], S[("orig", "dense", D.RL)][0]
    u_b, u_r = S[("orig", "utrap_blocked", D.BC)][0], S[("orig", "utrap_blocked", D.RL)][0]
    fig = plt.figure(figsize=(1328 / 250, 531 / 250))
    ax = fig.add_axes([0.0, 0.0, 0.46, 1.0]); ax.axis("off")
    png = RENDER / "ga_scene.png"
    if png.exists():
        im = Image.open(png); ax.imshow(im); W, H = im.size
        an = json.loads(png.with_suffix(".anchors.json").read_text())
        (x0, y0), (x1, y1) = an["bar0"], an["bar1"]
        ax.text((x0 + x1) / 2 * W, max(y0, y1) * H + 0.03 * H, "2 m", ha="center", va="top", fontsize=6.5)
    else:
        fig4_topview(ax, FIG4_TASKS["b"])
        c = D.case(FIG4_TASKS["b"], D.RL, 1)
        pts = np.array([c["cycles"][0]["pre"]] + [p for cy in c["cycles"] for p in cy["executed_path"][1:]])
        ax.plot(pts[:, 0], pts[:, 1], color=C["rl"], lw=1.4)
        print("[图形摘要] 未找到 ga_scene.png，用俯视图代替；运行 render_figures_v3.py 可生成渲染。")
    tx = fig.add_axes([0.48, 0.0, 0.52, 1.0]); tx.axis("off")
    tx.text(0.0, 0.88, "Point-cloud diffusion policy\n+ DPPO post-training (LoRA only)", fontsize=9, fontweight="bold",
            va="top", linespacing=1.25)
    tx.text(0.0, 0.56, "Safe arrival, BC → post-trained", fontsize=7, color=C["grey"], va="center")
    for y, lab, a, b in ((0.38, "Dense obstacles", d_b, d_r), (0.16, "U-trap, initially blocked", u_b, u_r)):
        tx.text(0.0, y, lab, fontsize=8, va="center")
        tx.text(0.58, y, f"{a:.1f}%", fontsize=10, color=C["bc"], va="center", fontweight="bold")
        tx.text(0.75, y, "→", fontsize=10, color=C["grey"], va="center")
        tx.text(0.82, y, f"{b:.1f}%", fontsize=10, color=C["rl"], va="center", fontweight="bold")
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "graphical_abstract.png", dpi=500, bbox_inches=None)
    fig.savefig(OUT / "graphical_abstract.pdf", bbox_inches=None)
    print("saved", OUT / "graphical_abstract", f"(dense {d_b:.1f}→{d_r:.1f}, U-trap blocked {u_b:.1f}→{u_r:.1f})")
    plt.close(fig)


# =====================================================================
def check():
    av = D.available()
    print("== 已有数据 ==")
    for p in (D.REC, D.TREND, D.CURVE, D.P2, D.P3, D.B1):
        print(f"  {'OK ' if p.exists() else '缺失'} {os.path.relpath(p, D.ROOT)}")
    print("== 待回传数据 ==")
    for k, p, use in (("EGO", D.EGO, "图5、图6加入EGO"), ("P3S", D.P3S, "图8(a)改为逐状态配对点图"),
                      ("PATHS", D.PATHS, "占据密度图用全部回合")):
        print(f"  {'已到位' if av[k] else '未到位'} {os.path.relpath(p, D.ROOT)} —— {use}")
    print("== 渲染 ==")
    for k in "abcde":
        print(f"  {'OK ' if (RENDER / f'fig4_{k}.png').exists() else '缺失'} 图4({k}) 渲染")
    print(f"  {'OK ' if (RENDER / 'ga_scene.png').exists() else '缺失'} 图形摘要渲染")
    if av["EGO"]:
        e = D.ego_records()
        print(f"  EGO 记录 {len(e)} 条：原任务 {sum(r['task_set'] == 'original' for r in e)}，新任务 {sum(r['task_set'] == 'new' for r in e)}")


JOBS = {"3c": fig3c, "4": fig4, "5": fig5, "6": fig6, "7": fig7, "8": fig8, "S1": figS1, "S2": figS2, "S3": figS3,
        "D": figD, "GA": figGA}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None, help="如 5 7 S2；可选：" + " ".join(JOBS))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--ci", choices=["both", "bootstrap", "none"], default="both", help="图5误差线")
    ap.add_argument("--fig3c", nargs="*", type=int, default=None, metavar="N",
                    help="图3(c)：任务号 重复号 周期1 周期2 …（默认任务30、后训练第1次重复、自动选4个周期）")
    a = ap.parse_args()
    if a.check:
        check(); return
    plt = setup()
    for k in (a.only or JOBS):
        if k == "5":
            fig5(plt, a.ci)
        elif k == "3c" and a.fig3c:
            fig3c(plt, task=a.fig3c[0], repeat=a.fig3c[1], cycles=a.fig3c[2:] or None)
        else:
            JOBS[k](plt)


if __name__ == "__main__":
    main()
