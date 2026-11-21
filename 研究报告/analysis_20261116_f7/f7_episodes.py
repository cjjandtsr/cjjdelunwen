"""只读：F7 run01 与 P6@u256 的 dev420 / val80 #E2 原迹逐回合特征（1 m 主终点）。
# 2026-11-17：项目仓库整理后，这些原迹改为精简的 *.jsonl.gz（所用字段均保留）；本脚本同时接受 *.jsonl 与 *.jsonl.gz。
用法：python3 -I f7_episodes.py <项目仓库根目录> <输出 episodes.json>
数据：jindu/routea_f7_run01/eval_{dev,val}/<P16..P19>/traces/*.jsonl.gz；
      P6 dev420：jindu/routea_f5_run01/results/eval_dev/full/P6/traces/*.jsonl；P6 val：jindu/routea_p6_u256_e2_val20_run01/full/**/traces/*.jsonl
几何：代码 diffusion_policy_3d/env/collision_geom.py（ObstacleSpec、compute_obstacle_clearance、segment_obstacle_collision）。
1 m 结局：执行路径（逐段连续）到目标中心最近距离 < 1.0 m 或原结局 reached → 成功；否则原结局为碰撞类 → 碰撞；其余 → 超时。
"""
import ast, glob, gzip, json, math, os, sys
import numpy as np
repo, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from diffusion_policy_3d.env.collision_geom import ObstacleSpec, compute_obstacle_clearance, segment_obstacle_collision
F7 = os.path.join(repo, 'jindu/routea_f7_run01')
SRC = {('dev', p): glob.glob(f'{F7}/eval_dev/{p}/traces/*.jsonl.gz') for p in ('P16', 'P17', 'P18', 'P19')}
SRC.update({('val', p): glob.glob(f'{F7}/eval_val/{p}/traces/*.jsonl.gz') for p in ('P16', 'P17', 'P18', 'P19')})
SRC[('dev', 'P6')] = glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_dev/full/P6/traces/*.jsonl*')
SRC[('val', 'P6')] = glob.glob(f'{repo}/jindu/routea_p6_u256_e2_val20_run01/full/**/traces/*.jsonl', recursive=True) or glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_val/full/P6/traces/*.jsonl*')
COLL = {'collision', 'ground_collision', 'ground', 'crash'}
def seg_dist(p, a, b):
    a, b, p = map(np.asarray, (a, b, p)); d = b - a; L = d @ d
    t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))
def cbf(c, dt=.3, w=2.):
    b = np.asarray(c) - .3; v = -((b[1:] - b[:-1]) / dt + (b[1:] + b[:-1]) / 6.)
    return -w * dt * float(np.clip(v, 0, 2).sum())
def hit_name(P, obs):
    for a, b in zip(P[:-1], P[1:]):
        h = segment_obstacle_collision(a, b, obs, .1 + 2e-3)
        if h is not None: return h[1]
    return None
rows = []
for (split, pol), files in sorted(SRC.items()):
    assert files, (split, pol)
    for f in sorted(files):
        op = gzip.open if f.endswith('.gz') else open
        L = [json.loads(l) for l in op(f, 'rt')]
        s, e = L[0], L[-1]; T = [t for t in L if t.get('type') == 'transition']
        task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task'])
        g = np.asarray(task['goal_pos'], float); s0 = np.asarray(task['start_pos'], float); D0 = float(np.linalg.norm(g - s0))
        obs = [ObstacleSpec.from_dict(o) for o in s['geometry']]
        mind, t1 = 1e9, None; tcum = 0.; plen = 0.; seg_v = []; seg_v_near = []; disp = []; cb = []; clear_min = 1e9
        for t in T:
            P = t['executed_path']; n = len(P) - 1; dt = t['executed_time_s'] / max(n, 1)
            c = [compute_obstacle_clearance(*q[:3], obs)[0] for q in P]; clear_min = min(clear_min, min(c))
            if n >= 1 and t['executed_time_s'] > 0: cb.append(cbf(c, dt))
            for k in range(n):
                dd = seg_dist(g, P[k], P[k + 1])
                if dd < 1.0 and t1 is None: t1 = tcum + dt * (k + 1)
                mind = min(mind, dd); L_ = math.dist(P[k], P[k + 1]); plen += L_ if t1 is None else 0
                if dt > 0:
                    seg_v.append(L_ / dt)
                    if min(c[k], c[k + 1]) < 2.5: seg_v_near.append(L_ / dt)
            tcum += t['executed_time_s']; disp.append(math.dist(P[0], P[-1]))
        dr = e['done_reason']
        o = 'S' if (dr == 'reached' or mind < 1.0) else ('C' if dr in COLL else 'T')
        r = dict(split=split, pol=pol, task=s['task_id'], world=s['world_id'], rep=s['repeat'], role=s['role'],
                 init=s['initial_hash'], out=o, dr=dr, n=len(T), D0=D0, goal_z=float(g[2]), mind=mind,
                 prog=1 - min(mind, D0) / D0 if D0 > 0 else 1., t1=t1, plen=plen,
                 v_med=float(np.median(seg_v)) if seg_v else None, v_near_med=float(np.median(seg_v_near)) if seg_v_near else None,
                 stall_frac=float(np.mean(np.asarray(disp) < .15)) if disp else None,
                 stall_last10=float(np.mean(np.asarray(disp[-10:]) < .15)) if disp else None,
                 cbf_sum=float(sum(cb)), cbf_nonzero=float(np.mean(np.asarray(cb) < 0)) if cb else None, clear_min=clear_min,
                 final_pos=T[-1]['executed_path'][-1] if T else None,
                 final_clear=compute_obstacle_clearance(*T[-1]['executed_path'][-1][:3], obs)[0] if T else None)
        if o == 'C':
            k = len(T) - 1; name = hit_name(T[-1]['executed_path'], obs)
            lead = 0
            for j in range(k - 1, -1, -1):
                h = hit_name(T[j]['planned_policy_path'], obs)
                if h is not None and (name is None or h == name): lead += 1
                else: break
            r.update(hit=name, lead=lead)
        rows.append(r)
json.dump(rows, open(out, 'w'))
from collections import Counter
for key in sorted(SRC):
    R = [r for r in rows if (r['split'], r['pol']) == key]
    print(key, len(R), dict(Counter(r['out'] for r in R)))
