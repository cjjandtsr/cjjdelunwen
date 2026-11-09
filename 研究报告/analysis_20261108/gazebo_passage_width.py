"""每个 Gazebo 任务的"可通过最大余量"（只用障碍几何，与飞行结果无关）。
定义：在飞行空间内（水平为障碍区域与起终点外扩 3 m，高度 z∈[ZMIN, ZMAX]），所有从起点到目标的路径中，路径上到障碍表面最小距离的最大值 r*。
r* < 机体半径 即物理上无法无接触通过。计算：0.1 m 体素化障碍，欧氏距离变换得到每个体素到障碍的距离（地面 z=0 也算障碍），
对 r 由大到小（步长 0.025 m）检验 {d > r} 中起点与目标是否连通（26 邻域），首个连通的 r 即 r*。体素化误差约 ±0.05 m。
运行：python3 -I gazebo_passage_width.py <gazebo_rows.json> <输出 csv> <ZMIN> <ZMAX> <运动学 traces 目录 ...>"""
import json, sys, glob, math, csv
import numpy as np
from scipy import ndimage
ROWS, OUT, ZMIN, ZMAX, *TR = sys.argv[1:]; ZMIN, ZMAX = float(ZMIN), float(ZMAX)
H = 0.1
geo, task = {}, {}
for D in TR:
    for fn in glob.glob(f'{D}/*.jsonl'):
        s = json.loads(open(fn).readline()); geo.setdefault(s['world_id'], s['geometry']); task.setdefault(s['task_id'], s['task'])
rows = json.load(open(ROWS)); tasks = sorted({(r['task'], r['world'], r['cat']) for r in rows})
res = []
for t, w, cat in tasks:
    T = next(v for k, v in task.items() if k.startswith(t)); O = geo[w]; s0, g = T['start_pos'], T['goal_pos']
    xs = [s0[0], g[0]] + [o['x'] - 8 for o in O] + [o['x'] + 8 for o in O]; ys = [s0[1], g[1]] + [o['y'] - 8 for o in O] + [o['y'] + 8 for o in O]
    x0, x1 = min(s0[0], g[0], min(o['x'] for o in O)) - 3, max(s0[0], g[0], max(o['x'] for o in O)) + 3
    y0, y1 = min(s0[1], g[1], min(o['y'] for o in O)) - 3, max(s0[1], g[1], max(o['y'] for o in O)) + 3
    X = np.arange(x0, x1, H); Y = np.arange(y0, y1, H); Z = np.arange(0, ZMAX + H, H)
    gx, gy, gz = np.meshgrid(X, Y, Z, indexing='ij'); occ = gz <= 0.0 + 1e-9
    for o in O:
        dx, dy, dz = gx - o['x'], gy - o['y'], gz - o['z']
        if o['shape'] == 'cylinder': m = (dx ** 2 + dy ** 2 <= o['radius'] ** 2) & (np.abs(dz) <= o['height'] / 2)
        else:
            c, s_ = math.cos(-o['yaw']), math.sin(-o['yaw']); lx, ly = c * dx - s_ * dy, s_ * dx + c * dy
            m = (np.abs(lx) <= o['size_x'] / 2) & (np.abs(ly) <= o['size_y'] / 2) & (np.abs(dz) <= o['size_z'] / 2)
        occ |= m
    dist = ndimage.distance_transform_edt(~occ, sampling=H)
    dist[:, :, Z < ZMIN] = 0
    ij = lambda p: (int(round((p[0] - x0) / H)), int(round((p[1] - y0) / H)), int(round((min(max(p[2], ZMIN), ZMAX) - 0) / H)))
    a, b = ij(s0), ij(g); rstar = None
    for r in np.arange(1.5, 0.0, -0.025):
        lab, _ = ndimage.label(dist > r, structure=np.ones((3, 3, 3)))
        if lab[a] and lab[a] == lab[b]: rstar = round(float(r), 3); break
    res.append(dict(task=t[:12], world=w.replace('routeA_rl_v1__', ''), cat=cat, r_star=rstar, d_start=round(float(dist[a]), 2), d_goal=round(float(dist[b]), 2)))
    print(res[-1], flush=True)
with open(OUT, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(res[0])); wr.writeheader(); wr.writerows(res)
