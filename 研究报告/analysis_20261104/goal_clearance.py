"""目标点周围的障碍间隙（只读）。Claude，2026-11-04。用于任务E 触发半径的几何依据。
运行：python3 -I goal_clearance.py <项目仓库根> name=bank.json[:strata.json] ...
输出：每集 × 类别：目标点到最近障碍表面距离（compute_obstacle_clearance，check_3d=True）的最小值、分位数、<2.1 m 与 <1.1 m 的任务数；目标高度最小值。"""
import json, os, sys, collections
root = sys.argv[1]; code = os.path.join(root, 'Improved-3D-Diffusion-Policy'); sys.path.insert(0, code)
from diffusion_policy_3d.env.collision_geom import ObstacleSpec, compute_obstacle_clearance
F = ('name', 'shape', 'x', 'y', 'z', 'yaw', 'radius', 'height', 'size_x', 'size_y', 'size_z')
CAT = {'zero': 'Sparse', 'low': 'Moderate', 'high': 'Dense'}
for a in sys.argv[2:]:
    name, spec = a.split('=', 1); path, _, sp = spec.partition(':'); b = json.load(open(path))
    lab = {t['task_id']: t['labels']['w1'] for t in json.load(open(sp))['tasks']} if sp else {t['task_id']: t['category'] for t in b['tasks']}
    by = collections.defaultdict(list); gz = []
    for t in b['tasks']:
        g = t['payload']['goal_pos']; gz.append(g[2])
        obs = [ObstacleSpec(**{k: o[k] for k in F}) for o in b['worlds'][t['world_id']]['geometry']]
        c = compute_obstacle_clearance(g[0], g[1], g[2], obs, True)[0] if obs else float('inf')
        by[CAT[lab[t['task_id']]]].append(c); by['All'].append(c)
    for k in ('Sparse', 'Moderate', 'Dense', 'All'):
        v = sorted(by[k]); n = len(v)
        print(f"{name:7s} {k:8s} n={n:3d} min={v[0]:.2f} p10={v[n//10]:.2f} median={v[n//2]:.2f} <2.1m={sum(x<2.1 for x in v)} <1.1m={sum(x<1.1 for x in v)}")
    print(f"{name:7s} goal z min={min(gz):.2f}")
