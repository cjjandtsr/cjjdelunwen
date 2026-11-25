"""只读：P6 + g1（#E4）在 dev420 上剩余碰撞的形态。只需 numpy 与项目的 collision_geom.py。

用法：python3 -I f10_residual_collisions.py <P6_g1_dev 原迹目录> <collision_geom.py 所在目录>
  原迹：项目仓库分支 f10-pack/run01-20261125（提交 1f1eb05）packs/P6_g1_dev_traces.tar.zst 解包后的 traces/
口径：只看 1 m 口径下的碰撞回合（碰撞前未进入目标 1 m）。"规划净空"为该决策 planned_policy_path 各点到几何障碍的
  最小净空（负值表示规划穿入障碍）。触发 = probe_metrics.triggered_denoise_steps 非空。
"""
import ast, collections, glob, json, sys
import numpy as np
D, CG = sys.argv[1:3]
sys.path.insert(0, CG)
from collision_geom import ObstacleSpec, compute_obstacle_clearance
clr = lambda p, obs: compute_obstacle_clearance(*p, obs)[0]


def segd(p, a, b):
    d = b - a; L = d @ d; t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t*d - p))


rows = []
for f in sorted(glob.glob(D + '/*.jsonl')):
    L = [json.loads(l) for l in open(f)]
    if L[-1]['done_reason'] not in ('collision', 'ground_collision'): continue
    h = L[0]; task = h['task'] if isinstance(h['task'], dict) else ast.literal_eval(h['task'])
    s, g = np.array(task['start_pos'], float), np.array(task['goal_pos'], float)
    obs = [ObstacleSpec.from_dict(o) for o in h['geometry']]
    T = [t for t in L if t.get('type') == 'transition']; n = len(T)
    P = np.array([T[0]['executed_path'][0]] + [q for t in T for q in t['executed_path'][1:]], float)
    if min(segd(g, P[i], P[i+1]) for i in range(len(P)-1)) < 1: continue
    Dd = np.linalg.norm(g - s); e = (g - s)/Dd
    blocked = min(clr(s + u*e, obs) for u in np.linspace(0, Dd, int(Dd/.05) + 2)) < .3
    trig = [bool(t['probe_metrics']['triggered_denoise_steps']) for t in T]
    seq = []
    for i in range(max(0, n-10), n):
        pm = T[i]['probe_metrics']
        seq.append((n-1-i, bool(pm['triggered_denoise_steps']), pm['delta_exec'],
                    min(clr(np.array(q, float), obs) for q in T[i]['planned_policy_path']), pm['cloud_points']))
    v = [np.linalg.norm(np.array(t['executed_path'][-1]) - np.array(t['executed_path'][0]))/max(t['executed_time_s'], 1e-6) for t in T[-4:]]
    rows.append(dict(task=h['task_id'], role=h['role'], blocked=blocked, trig_any=any(trig),
                     first_trig=next((i for i, x in enumerate(trig) if x), None), n=n, seq=seq,
                     z=float(P[-1][2]), speed=float(np.mean(v))))

print('1 m 口径碰撞回合 %d，其中被挡任务 %d，涉及任务 %d 个；角色 %s' % (len(rows), sum(r['blocked'] for r in rows),
      len({r['task'] for r in rows}), dict(collections.Counter(r['role'] for r in rows))))
print('回合中触发过引导 %d；碰撞决策触发 %d；碰撞决策机载点云为空 %d' % (sum(r['trig_any'] for r in rows),
      sum(r['seq'][-1][1] for r in rows), sum(r['seq'][-1][4] == 0 for r in rows)))
lead = [r['n']-1-r['first_trig'] for r in rows if r['first_trig'] is not None]
print('首次触发到碰撞相隔决策数：中位 %.1f，四分位 %s' % (np.median(lead), np.percentile(lead, [25, 75]).tolist()))
de = [x[2] for r in rows for x in r['seq'] if x[1]]
print('最后 10 个决策中触发时的执行段修正量：中位 %.3f m，p90 %.3f m' % (np.median(de), np.percentile(de, 90)))
print('最后 5 个决策的触发比例 %.2f' % np.mean([x[1] for r in rows for x in r['seq'][-5:]]))
for b in range(8):
    c = np.array([x[3] for r in rows for x in r['seq'] if x[0] == b])
    print('碰撞前第 %d 个决策：规划净空中位 %.2f m，规划穿入障碍的比例 %.2f' % (b, np.median(c), np.mean(c < 0)))
print('碰撞点高度中位 %.2f m（>3 m 的 %d 个）；碰撞前 4 个决策平均速度中位 %.2f m/s' % (
      np.median([r['z'] for r in rows]), sum(r['z'] > 3 for r in rows), np.median([r['speed'] for r in rows])))
