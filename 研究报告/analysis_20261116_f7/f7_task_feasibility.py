"""只读：dev420 各任务的几何可通过性（用评价原迹回合头中的障碍几何，不用于任何训练或调参）。
用法：python3 -I f7_task_feasibility.py <项目仓库根目录> <输出 task_feas.json>
方法：在 z_range 内、起终点包围盒外扩 4 m 的范围建 0.1 m 体素栅格，障碍（box 含 yaw、cylinder）按实体栅格化；
  欧氏距离变换得每个体素到最近障碍体素的距离 c（m，栅格近似，误差约 ±0.07 m）。
  瓶颈净空 c* = 起点与目标仍连通（26 邻接）的最大阈值（二分，精度 0.01 m）。
  绕行比 = 在 c ≥ 0.3 m 的自由空间中，0.25 m 栅格 26 邻接 Dijkstra 最短路长 / 起终点直线距离（不连通记 None）。
  直线净空 = 起终点直线上逐 0.05 m 采样的最小 c。"""
import ast, glob, json, math, os, sys
# 2026-11-17：项目仓库整理后，这些原迹改为精简的 *.jsonl.gz（所用字段均保留）；本脚本同时接受 *.jsonl 与 *.jsonl.gz。
import gzip as _gz
_topen = lambda f: _gz.open(f, 'rt') if f.endswith('.gz') else open(f)
import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
repo, out = sys.argv[1], sys.argv[2]
tasks = {}
for f in glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_dev/full/P6/traces/*.jsonl*'):
    s = json.loads(_topen(f).readline())
    task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task'])
    tasks.setdefault(s['task_id'], (task, s['geometry'], s['role'], s['world_id']))
def raster(geom, lo, res, shape):
    X = lo[0] + res * (np.arange(shape[0]) + .5); Y = lo[1] + res * (np.arange(shape[1]) + .5); Z = lo[2] + res * (np.arange(shape[2]) + .5)
    occ = np.zeros(shape, bool); XX, YY = np.meshgrid(X, Y, indexing='ij')
    for o in geom:
        if o['shape'] == 'cylinder':
            m2 = (XX - o['x']) ** 2 + (YY - o['y']) ** 2 <= o['radius'] ** 2; h = o['height']
        elif o['shape'] == 'box':
            c, s_ = math.cos(o['yaw']), math.sin(o['yaw']); dx, dy = XX - o['x'], YY - o['y']
            u, v = c * dx + s_ * dy, -s_ * dx + c * dy
            m2 = (abs(u) <= o['size_x'] / 2) & (abs(v) <= o['size_y'] / 2); h = o['size_z']
        else: raise ValueError(o['shape'])
        z0, z1 = o['z'] - h / 2, o['z'] + h / 2; mz = (Z >= z0) & (Z <= z1)
        if mz.any() and m2.any(): occ[np.ix_(m2.any(1), m2.any(0), mz)] |= (m2[np.ix_(m2.any(1), m2.any(0))][:, :, None])
    return occ
res_out = {}
for tid, (task, geom, role, world) in sorted(tasks.items()):
    s0, g = np.array(task['start_pos']), np.array(task['goal_pos']); zr = task['z_range']; res = .1
    lo = np.minimum(s0, g) - 4; hi = np.maximum(s0, g) + 4; lo[2], hi[2] = zr[0], zr[1]
    shape = tuple(int(math.ceil((hi[i] - lo[i]) / res)) for i in range(3))
    occ = raster(geom, lo, res, shape)
    c = ndimage.distance_transform_edt(~occ) * res - res / 2
    idx = lambda p: tuple(int(np.clip((p[i] - lo[i]) // res, 0, shape[i] - 1)) for i in range(3))
    si, gi = idx(s0), idx(g); st = np.ones((3, 3, 3), bool)
    def conn(th):
        if c[si] < th or c[gi] < th: return False
        lab, _ = ndimage.label(c >= th, structure=st); return lab[si] == lab[gi] and lab[si] != 0
    a, b = 0., float(min(c[si], c[gi]))
    if not conn(a + 1e-9): cstar = None
    else:
        while b - a > .01:
            m = (a + b) / 2; a, b = (m, b) if conn(m) else (a, m)
        cstar = a
    line = [c[idx(s0 + t * (g - s0))] for t in np.linspace(0, 1, int(np.linalg.norm(g - s0) / .05) + 2)]
    # 绕行比：0.25 m 粗栅格
    k = 2.5; cs = ndimage.zoom(c, 1 / k, order=0) if False else c[::3, ::3, ::3][:, :, :]; rc = res * 3
    free = cs >= .3; n = free.size; ids = -np.ones(free.shape, int); ids[free] = np.arange(free.sum())
    rows, cols, w = [], [], []
    for d in [(i, j, l) for i in (-1, 0, 1) for j in (-1, 0, 1) for l in (-1, 0, 1) if (i, j, l) > (0, 0, 0)]:
        sl1 = tuple(slice(max(0, -x), cs.shape[q] - max(0, x)) for q, x in enumerate(d))
        sl2 = tuple(slice(max(0, x), cs.shape[q] - max(0, -x)) for q, x in enumerate(d))
        A, B = ids[sl1], ids[sl2]; m = (A >= 0) & (B >= 0)
        rows += [A[m]]; cols += [B[m]]; w += [np.full(m.sum(), rc * math.sqrt(sum(x * x for x in d)))]
    detour = None
    if free.sum():
        G = coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(free.sum(),) * 2).tocsr()
        ci = lambda p: tuple(int(np.clip((p[i] - lo[i]) // rc, 0, cs.shape[i] - 1)) for i in range(3))
        a_, b_ = ids[ci(s0)], ids[ci(g)]
        if a_ >= 0 and b_ >= 0:
            dist = dijkstra(G, directed=False, indices=a_)[b_]
            if np.isfinite(dist): detour = float(dist / np.linalg.norm(g - s0))
    res_out[tid] = dict(role=role, world=world, cstar=cstar, line_min=float(min(line)), detour=detour, D0=float(np.linalg.norm(g - s0)))
    print(tid[-60:], role, 'c*=%s' % (None if cstar is None else round(cstar, 2)), 'line=%.2f' % min(line), 'detour=%s' % (None if detour is None else round(detour, 2)), flush=True)
json.dump(res_out, open(out, 'w'), indent=1)
