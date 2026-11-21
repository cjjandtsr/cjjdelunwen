"""只读：论文 186 任务上各规划器的执行速度与 1 m 结局（同一任务银行 d34c10d6…）。
用法：python3 -I paper186_planner_speed.py <名称=traces目录> ...
速度 = 执行路径每段长度/段时长，回合取中位；1 m 结局口径同 onset_side_switch.py（不需几何）。"""
import ast, glob, json, os, sys, collections
import numpy as np
def seg(p, a, b):
    d = b - a; L = d @ d; t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))
for arg in sys.argv[1:]:
    name, d = arg.split('=', 1); V = []; C = collections.Counter(); tasks = set()
    for f in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
        L = [json.loads(l) for l in open(f) if l.strip()]
        if L[-1].get('type') != 'episode_end': C['未完成'] += 1; continue
        h = L[0]; task = h['task'] if isinstance(h['task'], dict) else ast.literal_eval(h['task']); g = np.array(task['goal_pos'], float)
        tasks.add(h['task_id']); P = []; v = []
        for t in (x for x in L if x.get('type') == 'transition'):
            ep = np.array(t['executed_path'], float); dt = t['executed_time_s'] / (len(ep) - 1)
            v += list(np.linalg.norm(np.diff(ep, axis=0), axis=1) / dt); P += list(ep)
        P = np.array(P); mind = min(seg(g, P[k], P[k + 1]) for k in range(len(P) - 1))
        dr = L[-1]['done_reason']; C['S' if (dr == 'reached' or mind < 1) else ('C' if dr in ('collision', 'ground_collision') else 'T')] += 1
        V.append(np.median(v))
    V = np.array(V)
    print(f'{name}: 回合 {len(V)}（任务 {len(tasks)}），结局 {dict(C)}，回合中位速度 m/s 中位 {np.median(V):.2f} [{np.percentile(V,25):.2f}, {np.percentile(V,75):.2f}]')
