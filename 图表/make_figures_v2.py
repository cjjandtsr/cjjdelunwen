"""论文v2全部配图生成脚本（正文图1—8、补充图S1—S2）。

用法（在仓库根目录运行）：
    python 图表/make_figures_v2.py              # 生成全部图
    python 图表/make_figures_v2.py --only 5 7    # 只生成图5、图7
    python 图表/make_figures_v2.py --data-only   # 不画图，只打印各图使用的数值（无需matplotlib）

依赖：Python>=3.8，numpy，matplotlib>=3.5。输出到 图表/v2/，每图PDF（矢量）+PNG（600dpi）。
数据来源与用途见《论文实验数据清单_v1.md》；风格与设计说明见《图表/论文配图设计与生成说明_v2.md》。
本脚本只读原始数据，不修改任何数据文件。
"""
import argparse
import csv
import json
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '图表' / 'v2'
REC = ROOT / '2026-10-15_v3_全策略原轨迹分析' / '2026-10-15_v3_全策略原轨迹分析数据.json'
CURVE = ROOT / '2026-10-15_v3_全策略原轨迹分析' / 'fresh203_training_curve_384.csv'
P2 = ROOT / '图表' / 'P2_results.json'
P3 = ROOT / '图表' / 'P3_data_tables.md'
CLOUD = ROOT / '图表' / '参考图核对' / 'project_cloud_0.png'

BC, RL = 'bc', 'rl_2f3f9914db78_u32'
DENSE = {'cul_de_sac_trap': 'U形陷阱', 'bottleneck_corridor': '瓶颈通道', 's_turn_multi_obstacle': 'S形多障碍'}

# ---------------- 全文统一风格 ----------------
C = dict(bc='#3B6FB6', rl='#E07B39', arr='#2E9E5B', col='#C8423B', to='#9A9A9A',
         ink='#262626', grid='#E5E5E5', box='#F3F4F6', edge='#5B6573', lora='#E07B39',
         frozen='#DCE3EE', obs='#E8F1E4', train='#FBF0E6')
W1, W2 = 8.5 / 2.54, 17.0 / 2.54  # 单栏/双栏宽度（英寸）


# ---------------- 数据 ----------------
def load_records():
    d = json.loads(REC.read_text(encoding='utf-8'))
    return [r for r in d['records'] if r['policy'] in (BC, RL)]


def rate(xs, key='outcome', val='reached'):
    return 100.0 * sum(x[key] == val for x in xs) / len(xs) if xs else float('nan')


def original_groups(R):
    """原任务分组 -> {组名: {policy: [records]}}"""
    g = defaultdict(lambda: defaultdict(list))
    for r in R:
        dense = r['family'] in DENSE
        keys = []
        if dense and r['blocked']:
            keys.append('密集·受阻')
        if r['family'] == 'cul_de_sac_trap' and r['blocked']:
            keys.append('U形·受阻')
        if dense and not r['blocked']:
            keys.append('密集·未受阻')
        if not dense:
            keys.append('低密度')
        keys.append('全部')
        for k in keys:
            g[k][r['policy']].append(r)
    return g


def new_task_groups():
    """解析P3附表的新任务24项；返回 {组名: {'bc':[a,c,t], 'rl':[a,c,t], 'n':回合数}}"""
    t = P3.read_text(encoding='utf-8')
    rows = re.findall(r'\| (\d+) \| \w+ \| (\S+) \| (True|False) \| (True|False) \| (\d)/(\d)/(\d) \| (\d)/(\d)/(\d) \|', t)
    assert len(rows) == 24, len(rows)
    g = defaultdict(lambda: {'bc': [0, 0, 0], 'rl': [0, 0, 0], 'n': 0})
    for r in rows:
        world, blocked = r[1], r[2] == 'True'
        dense = any(k in world for k in DENSE)
        keys = ['全部']
        if dense:
            keys += ['密集', '密集·受阻' if blocked else '密集·未受阻']
        else:
            keys.append('低密度')
        for k in keys:
            g[k]['n'] += 5
            for i in range(3):
                g[k]['bc'][i] += int(r[4 + i])
                g[k]['rl'][i] += int(r[7 + i])
    return g


# 中间状态汇总值（来源：研究报告/2026-10-21_论文P3与有限任务评价独立验收数据.json 及其验收报告）
SAME_STATE = dict(mean_progress={'bc': 0.355, 'rl': 0.593},
                  positive={'bc': (851, 1200), 'rl': (1000, 1200)},
                  rl_cont={'首段正推进': (36, 12, 52), '首段非正推进': (5, 0, 15)},
                  arrivals={'bc': 46, 'rl': 41})


def data_summary():
    R = load_records()
    og, ng = original_groups(R), new_task_groups()
    print('== 图5/图6 原任务（到达%/碰撞%） ==')
    for k in ['密集·受阻', 'U形·受阻', '密集·未受阻', '低密度', '全部']:
        for p in (BC, RL):
            xs = og[k][p]
            print(f'  {k:6s} {p[:6]:6s} n={len(xs):3d} 到达 {rate(xs):5.1f} 碰撞 {rate(xs, val="collision"):5.1f}')
    print('== 图5/图6 新任务 ==')
    for k in ['密集·受阻', '密集·未受阻', '密集', '低密度', '全部']:
        v = ng[k]
        print(f'  {k:6s} n={v["n"]:3d} BC 到达 {100*v["bc"][0]/v["n"]:5.1f} 碰撞 {100*v["bc"][1]/v["n"]:5.1f} | '
              f'后训练 到达 {100*v["rl"][0]/v["n"]:5.1f} 碰撞 {100*v["rl"][1]/v["n"]:5.1f}')
    print('== 图7 行为指标（受阻，中位数） ==')
    for f, name in DENSE.items():
        for p in (BC, RL):
            xs = [r for r in R if r['policy'] == p and r['family'] == f and r['blocked']]
            print(f'  {name} {p[:6]} n={len(xs)} 侧偏 {st.median(x["max_cross_track_m"] for x in xs):.2f} '
                  f'进展 {st.median(x["normalized_best_gain"] for x in xs):.2f} 越过 {rate(xs, "crossed_goal_plane", True):.1f}%')
    print('== 图8 ==', SAME_STATE)


# ---------------- 绘图通用 ----------------
def setup_mpl():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Noto Sans CJK SC', 'Source Han Sans SC', 'Microsoft YaHei', 'SimHei',
                            'PingFang SC', 'WenQuanYi Micro Hei', 'Arial Unicode MS', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'mathtext.fontset': 'stix',
        'font.size': 8, 'axes.titlesize': 9, 'axes.labelsize': 8, 'legend.fontsize': 7,
        'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.linewidth': 0.6,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': C['ink'],
        'axes.grid': True, 'grid.color': C['grid'], 'grid.linewidth': 0.5, 'axes.axisbelow': True,
        'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.03,
    })
    return plt


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=600)
    print('saved', OUT / name)


def panel(ax, s):
    ax.set_title(s, loc='left', fontweight='bold', fontsize=9)


def bar_labels(ax, bars, fmt='{:.1f}'):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.8, fmt.format(h), ha='center', va='bottom', fontsize=6)


def box(ax, x, y, w, h, text, fc=None, ec=None, ls='-', fs=7, bold=False, r=0.02):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                                fc=fc or C['box'], ec=ec or C['edge'], lw=0.8, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs,
            fontweight='bold' if bold else 'normal', color=C['ink'], linespacing=1.3)


def arrow(ax, p, q, color=None, ls='-', lw=0.9, rad=0.0, text=None, toff=(0, 0.02)):
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=7, lw=lw, ls=ls,
                                 color=color or C['edge'], connectionstyle=f'arc3,rad={rad}'))
    if text:
        ax.text((p[0] + q[0]) / 2 + toff[0], (p[1] + q[1]) / 2 + toff[1], text, ha='center', fontsize=6, color=color or C['edge'])


def blank(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')


# ---------------- 图1 方法总体框架 ----------------
def fig1(plt):
    fig, ax = plt.subplots(figsize=(W2, W2 * 0.52)); blank(ax)
    # 导航闭环
    ax.add_patch(plt.Rectangle((0.005, 0.47), 0.99, 0.52, fc='white', ec=C['edge'], lw=0.6))
    ax.text(0.015, 0.955, '导航闭环（训练与评价共用）', fontsize=8, fontweight='bold', va='top')
    if CLOUD.exists():
        img = plt.imread(str(CLOUD))
        iax = fig.add_axes([0.02, 0.58, 0.15, 0.25]); iax.imshow(img); iax.axis('off')
    box(ax, 0.02, 0.52, 0.15, 0.05, '局部点云 3×4096×3\n状态 3×9、目标', fc=C['obs'], fs=6)
    box(ax, 0.22, 0.60, 0.15, 0.22, 'PointNet编码器\n→128维/帧\n\n状态MLP\n→64维/帧\n（冻结）', fc=C['frozen'], fs=6.5)
    box(ax, 0.42, 0.60, 0.17, 0.22, '条件向量 576维\n＋扩散时间步\n↓ FiLM\n条件一维U-Net\nDDIM 10步去噪', fs=6.5)
    box(ax, 0.64, 0.60, 0.15, 0.22, '轨迹 H16（16×11）\n取规划窗口 H8\n执行前缀 H4\n（4×0.3s）', fs=6.5)
    box(ax, 0.84, 0.60, 0.14, 0.22, '运动学仿真环境\n碰撞/到达判定\n合成新点云', fc=C['obs'], fs=6.5)
    for a, b in [(0.17, 0.22), (0.37, 0.42), (0.59, 0.64), (0.79, 0.84)]:
        arrow(ax, (a, 0.71), (b, 0.71))
    arrow(ax, (0.91, 0.60), (0.10, 0.575), rad=-0.12, text='每0.3s更新观测，每1.2s重新规划', toff=(0, -0.085))
    # 训练
    ax.add_patch(plt.Rectangle((0.005, 0.01), 0.99, 0.43, fc='white', ec=C['edge'], lw=0.6, ls='--'))
    ax.text(0.015, 0.415, '两阶段训练（评价时移除）', fontsize=8, fontweight='bold', va='top')
    box(ax, 0.02, 0.06, 0.25, 0.27, '① 示范预训练\nEGO示范 988回合\n$\\mathcal{L}_{BC}+\\lambda_{geo}\\mathcal{L}_{geo}$\n更新完整策略', fs=6.5)
    box(ax, 0.33, 0.20, 0.13, 0.12, '奖励 $r_t$\n进展/风险/终止', fc=C['train'], fs=6.5)
    box(ax, 0.50, 0.20, 0.13, 0.12, '价值网络\n$V_\\phi(c_t,\\beta_t)$', fc=C['train'], fs=6.5)
    box(ax, 0.67, 0.20, 0.13, 0.12, 'GAE优势\n去噪折扣', fc=C['train'], fs=6.5)
    box(ax, 0.84, 0.20, 0.14, 0.12, 'PPO截断代理\n仅更新LoRA', fc=C['train'], ec=C['lora'], fs=6.5)
    box(ax, 0.50, 0.04, 0.13, 0.10, '价值回归 $\\mathcal{L}_V$', fc=C['train'], fs=6.5)
    ax.text(0.33, 0.37, '② 交互后训练（DPPO）', fontsize=7, fontweight='bold')
    for a, b in [(0.46, 0.50), (0.63, 0.67), (0.80, 0.84)]:
        arrow(ax, (a, 0.26), (b, 0.26))
    arrow(ax, (0.565, 0.20), (0.565, 0.14), color=C['rl'], ls='--')
    arrow(ax, (0.91, 0.32), (0.51, 0.60), color=C['rl'], ls='--', rad=0.15, text='梯度', toff=(0.12, 0.0))
    arrow(ax, (0.145, 0.33), (0.29, 0.60), color=C['bc'], ls='--', rad=-0.1)
    arrow(ax, (0.88, 0.60), (0.395, 0.32), color=C['edge'], ls=':', rad=0.25)
    save(fig, 'figure_01_method_v2'); plt.close(fig)


# ---------------- 图2 网络结构 ----------------
def fig2(plt):
    fig, ax = plt.subplots(figsize=(W2, W2 * 0.40)); blank(ax)
    box(ax, 0.00, 0.62, 0.11, 0.26, '点云\n3帧×4096×3\n（机体系XYZ）', fc=C['obs'], fs=6)
    box(ax, 0.00, 0.14, 0.11, 0.26, '状态\n3帧×9\n位置/目标/偏航', fc=C['obs'], fs=6)
    box(ax, 0.15, 0.58, 0.16, 0.34, '多阶段PointNet\n逐点Conv1d 3→128\n4阶段：局部⊕全局最大池化\n512→128，最大池化\n输出 128/帧', fc=C['frozen'], fs=5.8)
    box(ax, 0.15, 0.12, 0.16, 0.30, '状态MLP\nLinear 9→64→64\nReLU\n输出 64/帧', fc=C['frozen'], fs=5.8)
    ax.text(0.23, 0.02, '编码器冻结（后训练）', ha='center', fontsize=6, color=C['edge'])
    box(ax, 0.35, 0.40, 0.11, 0.22, '拼接\n192/帧×3帧\n条件 $c_t$\n576', fs=6.2)
    box(ax, 0.35, 0.10, 0.11, 0.20, '扩散步 $k$\n正弦编码\nMLP→128', fs=6.2)
    box(ax, 0.50, 0.25, 0.08, 0.30, 'FiLM\n704→\n(γ, β)\n每残差块', fs=6.2)
    # U-Net
    xs = [0.62, 0.69, 0.76, 0.83, 0.90]
    hs = [0.52, 0.40, 0.30, 0.40, 0.52]
    labs = ['256\n@16', '512\n@8', '1024\n@4\n中间层', '512\n@8', '256\n@16']
    for x, h, l in zip(xs, hs, labs):
        box(ax, x, 0.50 - h / 2, 0.055, h, l, fc='white', ec=C['lora'], ls='--', fs=5.8)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow(ax, (a + 0.055, 0.50), (b, 0.50))
    ax.annotate('', xy=(0.90, 0.80), xytext=(0.69, 0.72), arrowprops=dict(arrowstyle='-|>', lw=0.6, ls=':', color=C['edge'], connectionstyle='arc3,rad=-0.3'))
    ax.text(0.795, 0.86, '跳跃连接', fontsize=6, ha='center', color=C['edge'])
    ax.text(0.76, 0.12, '条件一维U-Net（卷积核5，GroupNorm 8，Mish）\n橙色虚线：后训练加入LoRA的层（14个线性层＋33个卷积层，秩8）', ha='center', fontsize=5.8, color=C['ink'])
    box(ax, 0.965, 0.38, 0.035, 0.24, '16\n×\n11', fc=C['obs'], fs=6)
    arrow(ax, (0.11, 0.75), (0.15, 0.75)); arrow(ax, (0.11, 0.27), (0.15, 0.27))
    arrow(ax, (0.31, 0.72), (0.35, 0.56)); arrow(ax, (0.31, 0.27), (0.35, 0.46))
    arrow(ax, (0.46, 0.51), (0.50, 0.45)); arrow(ax, (0.46, 0.20), (0.50, 0.33))
    arrow(ax, (0.58, 0.40), (0.62, 0.40), color=C['rl'])
    arrow(ax, (0.955, 0.50), (0.965, 0.50))
    save(fig, 'figure_02_network'); plt.close(fig)


# ---------------- 图3 两层决策与滚动执行 ----------------
def fig3(plt):
    fig, ax = plt.subplots(figsize=(W2, W2 * 0.42)); blank(ax)
    # 外层
    ax.text(0.0, 0.96, '(a) 外层：环境决策', fontsize=8, fontweight='bold', va='top')
    for i, t in enumerate(['$t$', '$t+1$', '$t+2$']):
        x = 0.06 + i * 0.32
        box(ax, x, 0.76, 0.12, 0.10, f'观测 $o_{{{t[1:-1]}}}$', fc=C['obs'], fs=6.5)
        box(ax, x + 0.15, 0.76, 0.12, 0.10, f'轨迹 → 奖励 $r_{{{t[1:-1]}}}$', fs=6.5)
        arrow(ax, (x + 0.12, 0.81), (x + 0.15, 0.81))
        if i < 2:
            arrow(ax, (x + 0.27, 0.81), (x + 0.32, 0.81), text='执行H4', toff=(0, 0.025))
    # 时间轴与序列索引
    ax.text(0.0, 0.66, '(b) 一次决策的轨迹序列与执行时序', fontsize=8, fontweight='bold', va='top')
    x0, cw = 0.06, 0.055
    for h in range(16):
        fc = '#D9D9D9' if h < 2 else (C['rl'] if h < 6 else ('#F5C9A8' if h < 10 else 'white'))
        ax.add_patch(plt.Rectangle((x0 + h * cw, 0.44), cw * 0.94, 0.08, fc=fc, ec=C['edge'], lw=0.5))
        ax.text(x0 + h * cw + cw * 0.47, 0.48, str(h), ha='center', va='center', fontsize=5.5)
    for lab, a, b, y in [('H16 完整预测', 0, 16, 0.57), ('H8 规划窗口（风险评价）', 2, 10, 0.37), ('H4 执行前缀', 2, 6, 0.30)]:
        ax.annotate('', xy=(x0 + a * cw, y), xytext=(x0 + b * cw - 0.003, y), arrowprops=dict(arrowstyle='|-|', lw=0.6, color=C['ink']))
        ax.text(x0 + (a + b) / 2 * cw, y + 0.012, lab, ha='center', va='bottom', fontsize=6)
    for k in range(5):
        xx = x0 + (2 + k) * cw
        ax.plot([xx, xx], [0.24, 0.28], color=C['bc'], lw=0.8)
    ax.text(x0 + 4 * cw, 0.205, '每段0.3s后更新观测；4段（1.2s）后重新规划', ha='center', fontsize=6, color=C['bc'])
    ax.text(x0 + 16.2 * cw, 0.48, '0—1 对齐元素（不执行）\n2—5 本周期执行\n6—9 仅计规划风险\n10—15 不参与当前周期', fontsize=5.8, va='center')
    # 内层
    ax.text(0.0, 0.15, '(c) 内层：去噪过程', fontsize=8, fontweight='bold', va='top')
    ks = ['$Z^{10}\\sim\\mathcal{N}(0,I)$', '$Z^{9}$', '…', '$Z^{1}$', '$Z^{0}$（轨迹）']
    for i, k in enumerate(ks):
        x = 0.06 + i * 0.17
        box(ax, x, 0.01, 0.11, 0.08, k, fc='white', fs=6.5)
        if i < 4:
            arrow(ax, (x + 0.11, 0.05), (x + 0.17, 0.05), text='高斯转移' if i == 0 else None, toff=(0, 0.02))
    ax.text(0.92, 0.05, '每步对数概率可解析计算\n→ 策略梯度更新', fontsize=6, va='center')
    save(fig, 'figure_03_two_layer_receding'); plt.close(fig)


# ---------------- 图4 场景示意 ----------------
def fig4(plt):
    import numpy as np
    from matplotlib.patches import Circle, Rectangle
    fig, axs = plt.subplots(1, 5, figsize=(W2, W2 * 0.24), gridspec_kw=dict(width_ratios=[1, 1, 1, 1, 1.25]))
    S, G = (0.0, 0.0), (16.0, 0.0)

    def base(ax, title, blocked):
        ax.set_aspect('equal'); ax.set_xlim(-2, 18); ax.set_ylim(-10, 10); ax.axis('off'); panel(ax, title)
        ax.plot(*S, 's', color=C['ink'], ms=4); ax.plot(*G, '*', color=C['rl'], ms=7)
        ax.plot([S[0], G[0]], [S[1], G[1]], ls='--', lw=0.8, color=C['col'] if blocked else C['arr'])

    def cyl(ax, x, y, r):
        ax.add_patch(Circle((x, y), r, fc='#B8C2CE', ec=C['edge'], lw=0.4))

    def boxp(ax, x, y, w, h):
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc='#B8C2CE', ec=C['edge'], lw=0.4))

    rng = np.random.default_rng(0)
    a = axs[0]; base(a, '(a) 瓶颈通道', True)
    for i in range(10):
        cyl(a, 5 + i * 0.6, 1.0 + max(0, 5 - i) * 0.9, 0.35); cyl(a, 5 + i * 0.6, -1.0 - max(0, 5 - i) * 0.9, 0.35)
    cyl(a, 9.5, 0.0, 0.5)
    a = axs[1]; base(a, '(b) U形陷阱', True)
    boxp(a, 11, 0, 0.6, 7); boxp(a, 8.5, 3.2, 5, 0.6); boxp(a, 8.5, -3.2, 5, 0.6)
    a = axs[2]; base(a, '(c) S形多障碍', True)
    for i in range(7):
        cyl(a, 4, -5 + i * 1.1, 0.4); cyl(a, 9, 5 - i * 1.1, 0.4); cyl(a, 13, -4 + i * 1.0, 0.35)
    a = axs[3]; base(a, '(d) 低密度：前方偏置障碍', False)
    cyl(a, 8, 2.2, 1.3)
    a = axs[4]
    if CLOUD.exists():
        a.imshow(plt.imread(str(CLOUD))); a.axis('off')
    else:
        a.axis('off')
    panel(a, '(e) 机体系局部点云')
    save(fig, 'figure_04_scenes'); plt.close(fig)


# ---------------- 图5 分层到达率 ----------------
def fig5(plt, R):
    import numpy as np
    og, ng = original_groups(R), new_task_groups()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, W2 * 0.34), gridspec_kw=dict(width_ratios=[4, 3]))
    w = 0.36
    ok = ['密集·受阻', 'U形·受阻', '密集·未受阻', '低密度']
    olab = ['密集\n受阻', 'U形陷阱\n受阻', '密集\n未受阻', '低密度\n专项']
    x = np.arange(len(ok))
    b1 = a1.bar(x - w / 2, [rate(og[k][BC]) for k in ok], w, color=C['bc'], label='BC策略')
    b2 = a1.bar(x + w / 2, [rate(og[k][RL]) for k in ok], w, color=C['rl'], label='后训练策略')
    bar_labels(a1, b1); bar_labels(a1, b2)
    a1.set_xticks(x, olab); a1.set_ylabel('安全到达率（%）'); a1.set_ylim(0, 60); panel(a1, '(a) 原任务')
    a1.legend(loc='upper left', ncol=2)
    nk = ['密集·受阻', '密集·未受阻', '低密度']
    nlab = ['密集\n受阻', '密集\n未受阻', '低密度\n专项']
    x = np.arange(len(nk))
    v = [ng[k] for k in nk]
    b1 = a2.bar(x - w / 2, [100 * g['bc'][0] / g['n'] for g in v], w, color=C['bc'])
    b2 = a2.bar(x + w / 2, [100 * g['rl'][0] / g['n'] for g in v], w, color=C['rl'])
    bar_labels(a2, b1); bar_labels(a2, b2)
    a2.set_xticks(x, nlab); a2.set_ylim(0, 60); panel(a2, '(b) 新任务')
    fig.tight_layout(); save(fig, 'figure_05_arrival_by_category'); plt.close(fig)


# ---------------- 图6 碰撞率—到达率 ----------------
def fig6(plt, R):
    og, ng = original_groups(R), new_task_groups()
    pts = []
    for k, lab in [('密集·受阻', '原·密集受阻'), ('密集·未受阻', '原·密集未受阻'), ('低密度', '原·低密度')]:
        pts.append((lab, rate(og[k][BC], val='collision'), rate(og[k][BC]), rate(og[k][RL], val='collision'), rate(og[k][RL]), 'o'))
    for k, lab in [('密集', '新·密集'), ('低密度', '新·低密度')]:
        g = ng[k]; n = g['n']
        pts.append((lab, 100 * g['bc'][1] / n, 100 * g['bc'][0] / n, 100 * g['rl'][1] / n, 100 * g['rl'][0] / n, 's'))
    fig, ax = plt.subplots(figsize=(W1, W1 * 0.85))
    for lab, c0, a0, c1, a1_, m in pts:
        ax.annotate('', xy=(c1, a1_), xytext=(c0, a0), arrowprops=dict(arrowstyle='-|>', lw=0.9, color=C['edge']))
        ax.plot(c0, a0, m, color=C['bc'], ms=5); ax.plot(c1, a1_, m, color=C['rl'], ms=5)
        ax.text(c1 + 1.2, a1_ + 0.8, lab, fontsize=6)
    ax.plot([], [], 'o', color=C['bc'], label='BC策略'); ax.plot([], [], 'o', color=C['rl'], label='后训练策略')
    ax.plot([], [], 'o', color='gray', label='原任务'); ax.plot([], [], 's', color='gray', label='新任务')
    ax.set_xlabel('碰撞率（%）'); ax.set_ylabel('安全到达率（%）'); ax.set_xlim(0, 80); ax.set_ylim(-2, 55)
    ax.legend(loc='upper right', ncol=2)
    ax.text(2, 51, '← 更安全、更高到达', fontsize=6, color=C['arr'])
    save(fig, 'figure_06_collision_vs_arrival'); plt.close(fig)


# ---------------- 图7 行为指标分布 ----------------
def fig7(plt, R):
    import numpy as np
    fams = list(DENSE)
    sel = {(f, p): [r for r in R if r['policy'] == p and r['family'] == f and r['blocked']] for f in fams for p in (BC, RL)}
    fig, axs = plt.subplots(1, 3, figsize=(W2, W2 * 0.30))
    for ax, key, ylab, title in [(axs[0], 'max_cross_track_m', '最大侧向偏离（m）', '(a) 侧向偏离'),
                                 (axs[1], 'normalized_best_gain', '最优进展（比例）', '(b) 最优进展')]:
        for i, f in enumerate(fams):
            for j, p in enumerate((BC, RL)):
                data = [x[key] for x in sel[(f, p)]]
                bp = ax.boxplot(data, positions=[i + (j - 0.5) * 0.36], widths=0.3, patch_artist=True, showfliers=False,
                                medianprops=dict(color=C['ink'], lw=1.0), whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6))
                bp['boxes'][0].set(facecolor=C['bc'] if p == BC else C['rl'], alpha=0.85, lw=0.6)
        ax.set_xticks(range(3), [DENSE[f] for f in fams]); ax.set_ylabel(ylab); panel(ax, title)
    ax = axs[2]; w = 0.36; x = np.arange(3)
    b1 = ax.bar(x - w / 2, [rate(sel[(f, BC)], 'crossed_goal_plane', True) for f in fams], w, color=C['bc'], label='BC策略')
    b2 = ax.bar(x + w / 2, [rate(sel[(f, RL)], 'crossed_goal_plane', True) for f in fams], w, color=C['rl'], label='后训练策略')
    bar_labels(ax, b1); bar_labels(ax, b2)
    ax.set_xticks(x, [DENSE[f] for f in fams]); ax.set_ylabel('回合比例（%）'); ax.set_ylim(0, 30); panel(ax, '(c) 越过目标横截面')
    ax.legend(loc='upper left')
    fig.tight_layout(); save(fig, 'figure_07_behavior_metrics'); plt.close(fig)


# ---------------- 图8 首段推进与闭环结果 ----------------
def fig8(plt):
    s = SAME_STATE
    fig, axs = plt.subplots(1, 3, figsize=(W2, W2 * 0.28), gridspec_kw=dict(width_ratios=[1, 1, 1.6]))
    labs = ['BC策略', '后训练策略']; cols = [C['bc'], C['rl']]
    b = axs[0].bar(labs, [s['mean_progress']['bc'], s['mean_progress']['rl']], color=cols, width=0.55)
    for r in b:
        axs[0].text(r.get_x() + r.get_width() / 2, r.get_height() + 0.01, f'{r.get_height():.3f}', ha='center', fontsize=6)
    axs[0].set_ylabel('首段平均目标推进（m）'); axs[0].set_ylim(0, 0.75); panel(axs[0], '(a) 开环首段推进')
    pr = [100 * s['positive'][k][0] / s['positive'][k][1] for k in ('bc', 'rl')]
    b = axs[1].bar(labs, pr, color=cols, width=0.55); bar_labels(axs[1], b)
    axs[1].set_ylabel('正推进样本比例（%）'); axs[1].set_ylim(0, 100); panel(axs[1], '(b) 正推进比例')
    ax = axs[2]; groups = list(s['rl_cont']); left = [0, 0]
    for i, (name, col) in enumerate([('到达', C['arr']), ('碰撞', C['col']), ('超时', C['to'])]):
        vals = [100 * s['rl_cont'][g][i] / sum(s['rl_cont'][g]) for g in groups]
        ax.barh(groups, vals, left=left, color=col, label=name, height=0.5)
        for y, (l, v) in enumerate(zip(left, vals)):
            if v >= 8:
                ax.text(l + v / 2, y, f'{v:.0f}', ha='center', va='center', fontsize=6, color='white')
        left = [l + v for l, v in zip(left, vals)]
    ax.set_yticks(range(2), [f'{g}\n（n={sum(s["rl_cont"][g])}）' for g in groups])
    ax.set_xlabel('后训练策略续飞终点构成（%）'); ax.set_xlim(0, 100); ax.grid(axis='y', visible=False)
    ax.legend(ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.22)); panel(ax, '(c) 首段推进与闭环终点')
    fig.tight_layout(); save(fig, 'figure_08_first_step_vs_closed_loop'); plt.close(fig)


# ---------------- 补充图 ----------------
def figS1(plt):
    rows = list(csv.DictReader(CURVE.open(encoding='utf-8')))
    keys = ['reached', 'collision', 'time_limit', 'collection_boundary', 'altitude_exceed', 'ground_crash', 'out_of_bounds']
    u = [int(r['update']) for r in rows]
    tot = [sum(int(r['done_reason_' + k] or 0) for k in keys) for r in rows]
    arr = [int(r['done_reason_reached'] or 0) for r in rows]
    col = [int(r['done_reason_collision'] or 0) for r in rows]
    ret = [float(r['return_mean']) if r['return_mean'] else float('nan') for r in rows]

    def roll(num, den, w=16):
        out = []
        for i in range(len(num)):
            a = max(0, i - w + 1); d = sum(den[a:i + 1]); out.append(100 * sum(num[a:i + 1]) / d if d else float('nan'))
        return out
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, W2 * 0.30))
    a1.plot(u, roll(arr, tot), color=C['arr'], label='到达'); a1.plot(u, roll(col, tot), color=C['col'], label='碰撞')
    a1.axvline(32, color=C['ink'], ls=':', lw=0.8); a1.text(34, 45, '所用检查点（第32轮）', fontsize=6)
    a1.set_xlabel('外层更新轮数'); a1.set_ylabel('训练回合比例（%，16轮滑动）'); a1.legend(); panel(a1, '(a) 训练采集回合终点')
    a2.plot(u, ret, color=C['grid'], lw=0.6); a2.plot(u, roll([r if r == r else 0 for r in ret], [1] * len(ret)), color=C['rl'])
    a2.axvline(32, color=C['ink'], ls=':', lw=0.8); a2.set_xlabel('外层更新轮数'); a2.set_ylabel('平均回合回报'); panel(a2, '(b) 平均回报')
    fig.tight_layout(); save(fig, 'figure_S1_training_curve'); plt.close(fig)


def figS2(plt):
    d = json.loads(P2.read_text(encoding='utf-8'))
    M = d['paired_terminal_matrix']
    zh = ['到达', '碰撞', '超时']
    assert M['rows_bc'] == M['columns_rl'] == ['reached', 'collision', 'time_limit']
    mat = M['counts']
    fig, ax = plt.subplots(figsize=(W1, W1 * 0.8))
    ax.imshow(mat, cmap='Greys', vmin=0, vmax=max(max(r) for r in mat) * 1.3); ax.grid(False)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, mat[i][j], ha='center', va='center', fontsize=8,
                    color=C['arr'] if (j == 0 and i != 0) else (C['col'] if (i == 0 and j != 0) else C['ink']))
    ax.set_xticks(range(3), zh); ax.set_yticks(range(3), zh); ax.set_xlabel('后训练策略终点'); ax.set_ylabel('BC策略终点')
    save(fig, 'figure_S2_paired_matrix'); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*', default=None, help='如 1 2 5 S1')
    ap.add_argument('--data-only', action='store_true')
    a = ap.parse_args()
    if a.data_only:
        data_summary(); return
    plt = setup_mpl(); R = load_records()
    jobs = {'1': lambda: fig1(plt), '2': lambda: fig2(plt), '3': lambda: fig3(plt), '4': lambda: fig4(plt),
            '5': lambda: fig5(plt, R), '6': lambda: fig6(plt, R), '7': lambda: fig7(plt, R), '8': lambda: fig8(plt),
            'S1': lambda: figS1(plt), 'S2': lambda: figS2(plt)}
    for k in (a.only or jobs):
        jobs[k]()


if __name__ == '__main__':
    main()
