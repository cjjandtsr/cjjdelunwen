"""只读：训练采集（P18、P19，随机采样）中直线被挡的回合，到达与碰撞回合的轨迹形状。
用法：python3 -I train_blocked_success_shape.py <项目仓库根目录>
直线被挡 = 回合首个记录位置到目标的直线净空 < 0.3 m（compute_obstacle_clearance，0.05 m 采样）。
侧向偏移 = 轨迹上各决策终点到"起点—目标直线"的垂直距离（分水平、竖直分量）的最大值。
目的：检验"绕行从未被采样到"这一说法。若到达回合有米级偏移，则多决策的闭环随机飞行确实产生过绕行。"""
import glob, gzip, json, os, sys, collections
import numpy as np
repo = sys.argv[1]; sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from diffusion_policy_3d.env.collision_geom import ObstacleSpec, compute_obstacle_clearance
geo = {}
for f in glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P18/traces/*.jsonl.gz'):
    s = json.loads(gzip.open(f, 'rt').readline()); geo.setdefault(s['world_id'], [ObstacleSpec.from_dict(o) for o in s['geometry']])
def line_clear(a, b, obs):
    a, b = np.asarray(a), np.asarray(b); n = int(np.linalg.norm(b - a) / .05) + 2
    return min(compute_obstacle_clearance(*(a + t * (b - a)), obs)[0] for t in np.linspace(0, 1, n))
eps = collections.defaultdict(list)
for P in ('P18', 'P19'):
    for f in sorted(glob.glob(f'{repo}/jindu/routea_f7_run01/train/{P}/metrics_update_*.json.gz')):
        for t in json.load(gzip.open(f))['rollout_audit']['transition_records']:
            eps[(P, t['episode_id'])].append((t['decision_index'], t['world_id'], t['goal_xyz'], t['position_before_xyz'], t['position_after_xyz'], t['terminated'], t['truncated'], t['reward_terms'].get('terminal', 0)))
R = collections.defaultdict(list)
for k, T in eps.items():
    T.sort()
    if not (T[-1][5] or T[-1][6]): continue
    s0, g = np.array(T[0][3]), np.array(T[0][2]); obs = geo[T[0][1]]
    if line_clear(s0, g, obs) >= .3: continue
    o = ('S' if T[-1][7] > 0 else 'C') if T[-1][5] else 'T'
    d = (g - s0) / np.linalg.norm(g - s0); P = np.array([t[4] for t in T]); off = (P - s0) - np.outer((P - s0) @ d, d)
    R[o].append((float(np.linalg.norm(off[:, :2], axis=1).max()), float(off[:, 2].max()), float(np.linalg.norm(g - s0)), T[0][0]))
q = lambda v, p: float(np.percentile(v, p))
for o in 'SCT':
    v = np.array(R[o])
    print('结局 %s：%d 回合；最大水平偏移 中位 %.2f m（25%% %.2f，75%% %.2f）；≥1 m 的比例 %.0f%%，≥2 m %.0f%%；最大向上偏移 中位 %.2f m，≥1 m 的比例 %.0f%%；任一方向偏移 ≥1 m 的比例 %.0f%%；从回合开头（决策 0）起的比例 %.0f%%' % (
        o, len(v), np.median(v[:, 0]), q(v[:, 0], 25), q(v[:, 0], 75), 100 * np.mean(v[:, 0] >= 1), 100 * np.mean(v[:, 0] >= 2), np.median(v[:, 1]), 100 * np.mean(v[:, 1] >= 1), 100 * np.mean((v[:, 0] >= 1) | (v[:, 1] >= 1)), 100 * np.mean(v[:, 3] == 0)))
