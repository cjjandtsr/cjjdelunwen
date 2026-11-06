"""G12 直线飞行参考（只读）。Claude，2026-11-04。

对每个评价集的每个任务，沿起点→终点直线飞行，用项目的首次事件合同
（diffusion_policy_3d/env/reward_v2_support/first_event.py::locate_first_event，机体半径 0.1 m，
目标球 0.5 m，地面 0.2 m，terminate_at_space_limits=False，与共享评价入口一致）判定先到达还是先碰撞。
直线飞行是确定的，同一任务的 5 次重复结局相同，所以按任务计，再乘重复数换算为回合。
不含动力学、不含时间上限（最长直线距离见输出，均远小于 60 次决策 × 1.2 s 内 1 m/s 可飞的 72 m）。

运行：python3 -I g12_straight_line.py <项目仓库根> <out_dir> name=bank.json[:strata.json] [...]
类别取冻结分类文件（dev/val：F5 的 dev_strata.json、val_strata.json；test12：analysis_20261103/test12_strata.json；
扩展集：bank 自带 category，已由 C4 复核）。直线是否穿过障碍另用同一 segment 判定给出（blocked_full_segment）。
输出：g12_tasks.csv（逐任务）、g12_summary.csv（按集合 × 类别）
"""
import csv, json, math, os, sys, collections
root, out = sys.argv[1:3]
banks = [a.split('=', 1) for a in sys.argv[3:]]
code = os.path.join(root, 'Improved-3D-Diffusion-Policy')
sys.path.insert(0, code); sys.path.insert(0, os.path.join(code, 'scripts'))
from diffusion_policy_3d.env.collision_geom import segment_obstacle_collision
from diffusion_policy_3d.env.collision_geom import ObstacleSpec
from diffusion_policy_3d.env.reward_v2_support.first_event import locate_first_event
FIELDS = ('name', 'shape', 'x', 'y', 'z', 'yaw', 'radius', 'height', 'size_x', 'size_y', 'size_z')
CAT = {'zero': 'Sparse', 'low': 'Moderate', 'high': 'Dense'}
os.makedirs(out, exist_ok=True)
rows = []
for name, spec in banks:
    path, _, sp = spec.partition(':')
    b = json.load(open(path))
    frozen = {t['task_id']: t['labels']['w1'] for t in json.load(open(sp))['tasks']} if sp else {t['task_id']: t['category'] for t in b['tasks']}
    for t in b['tasks']:
        p, w = t['payload'], t['world_id']
        geo = b['worlds'][w]['geometry']
        obs = [ObstacleSpec(**{k: o[k] for k in FIELDS}) for o in geo]
        s, g = p['start_pos'], p['goal_pos']
        ev = locate_first_event([s, g], g, obs, 0.1, float(p['z_range'][1]), terminate_at_space_limits=False)
        rows.append(dict(split=name, task_id=t['task_id'], world=w, role=t['role'], cat=CAT[frozen[t['task_id']]],
                         repeats=len(b['episodes']) // len(b['tasks']), distance_m=round(math.dist(s, g), 4),
                         outcome='reached' if ev is not None and ev.kind == 'reached' else (ev.kind if ev else 'none'),
                         blocked_full_segment=segment_obstacle_collision(s, g, obs, 0.1) is not None))
with open(os.path.join(out, 'g12_tasks.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
summ = []
for name, _ in banks:
    for cat in ('Sparse', 'Moderate', 'Dense', 'All'):
        rs = [r for r in rows if r['split'] == name and (cat == 'All' or r['cat'] == cat)]
        if not rs: continue
        c = collections.Counter(r['outcome'] for r in rs); rep = rs[0]['repeats']
        summ.append(dict(split=name, category=cat, tasks=len(rs), episodes=len(rs) * rep,
                         reached_tasks=c['reached'], collision_tasks=c['collision'], other_tasks=len(rs) - c['reached'] - c['collision'],
                         reached_episodes=c['reached'] * rep, arrival_pct=f"{100 * c['reached'] / len(rs):.1f}",
                         max_distance_m=max(r['distance_m'] for r in rs),
                         blocked_but_reached=sum(r['blocked_full_segment'] and r['outcome'] == 'reached' for r in rs)))
with open(os.path.join(out, 'g12_summary.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(summ[0])); wr.writeheader(); wr.writerows(summ)
for x in summ: print(x)
