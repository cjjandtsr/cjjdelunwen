"""只读：直线被挡任务上"从多远开始偏离、走哪一侧、换不换向"，EGO-Planner-Swarm 对 BC、P6@u256（#E2）。
用法：python3 -I onset_side_switch.py <EGO 原迹目录> <P6 #E2 dev420 原迹目录> <BC #E2 dev420 原迹目录> <collision_geom.py 所在目录> <blocked_tasks_dev420.json>
数据：EGO = Codex 前置交接 ego_full_traces_932（论文 186 任务 × 5，common_H4，运动学环境）；
      P6、BC = jindu/routea_f5_run01/results/eval_dev/full/{P6,bc}/traces（dev420，#E2）。两组任务不同，只比较行为分布，不做逐任务配对。
口径（全部为本脚本定义，写在这里）：
  直线 s→g，0.05 m 采样，几何净空 <0.3 m 判"被挡"（与 dev420 分析同口径）；被挡点 b = 沿线第一个净空 <0.3 m 的采样点，u_b 为其沿线坐标。
  执行路径点 p：沿线坐标 u = (p−s)·ê；垂直偏移 r 分解为水平侧向 h（沿 ẑ×ê 方向）与竖直 v。
  偏离起点 = 第一个 r ≥ 0.3 m 且 u < u_b 的点；提前距离 = u_b − u；提前时间 = 首次 u ≥ u_b 的时刻 − 偏离起点时刻（每执行段 0.3 s；未到 u_b 记缺）。
  通过方式 = 首次 u ≥ u_b 时 |h| ≥ |v| 记侧绕（左/右），否则 v>0 记越顶、v<0 记下穿；r <0.3 记"贴线"。
  换向次数 = 从起点到 u 首次 ≥ u_b+0.5 m 为止，|h| > 0.3 m 的点上 h 符号的改变次数。
  1 m 结局：执行路径逐段到目标最近距离 <1 m 或 reached → 到达；碰撞类 → 碰撞；其余 → 超时（与 e1_blocked_by_policy.py 一致）。
"""
import ast, glob, gzip, json, os, sys, collections
import numpy as np
EGO, P6D, BCD, CG, BLKF = sys.argv[1:6]
sys.path.insert(0, CG)
from collision_geom import ObstacleSpec, compute_obstacle_clearance
BLK_DEV = set(json.load(open(BLKF)))

def seg(p, a, b):
    d = b - a; L = d @ d; t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))

def episode(f):
    op = gzip.open if f.endswith('.gz') else open
    L = [json.loads(l) for l in op(f, 'rt') if l.strip()]
    if L[-1].get('type') != 'episode_end': return None
    h = L[0]; task = h['task'] if isinstance(h['task'], dict) else ast.literal_eval(h['task'])
    s, g = np.array(task['start_pos'], float), np.array(task['goal_pos'], float)
    obs = [ObstacleSpec.from_dict(o) for o in h['geometry']]
    T = [t for t in L if t.get('type') == 'transition']
    P = [np.array(T[0]['executed_path'][0], float)]; tm = [0.]
    for t in T:
        ep = t['executed_path']; dt = t['executed_time_s'] / (len(ep) - 1)
        for q in ep[1:]: P.append(np.array(q, float)); tm.append(tm[-1] + dt)
    P = np.array(P); tm = np.array(tm)
    mind = min(seg(g, P[k], P[k + 1]) for k in range(len(P) - 1))
    dr = L[-1]['done_reason']
    out = 'S' if (dr == 'reached' or mind < 1) else ('C' if dr in ('collision', 'ground_collision') else 'T')
    D = np.linalg.norm(g - s); e = (g - s) / D
    n = int(D / .05) + 2; us = np.linspace(0, D, n)
    cl = np.array([compute_obstacle_clearance(*(s + u * e), obs)[0] for u in us])
    blocked = bool(cl.min() < .3)
    r = dict(task=h['task_id'], rep=h['repeat'], out=out, blocked=blocked, D=D)
    if not blocked: return r
    ub = float(us[np.argmax(cl < .3)])
    nh = np.cross(e, [0, 0, 1.]); nh /= np.linalg.norm(nh); nv = np.cross(nh, e)
    Q = P - s; u = Q @ e; hh = Q @ nh; vv = Q @ nv; rr = np.hypot(hh, vv)
    pre = np.where((rr >= .3) & (u < ub))[0]
    reach_b = np.where(u >= ub)[0]
    r.update(ub=ub)
    if len(pre):
        i = int(pre[0]); r['lead_m'] = ub - u[i]
        r['onset_clear'] = compute_obstacle_clearance(*P[i], obs)[0]
        r['lead_s'] = (tm[reach_b[0]] - tm[i]) if len(reach_b) and reach_b[0] > i else np.nan
    else:
        r['lead_m'] = np.nan; r['lead_s'] = np.nan; r['onset_clear'] = np.nan
    # 到 u_b−1 m 时的偏移
    k1 = np.where(u >= ub - 1.0)[0]; r['r_at_m1'] = float(rr[k1[0]]) if len(k1) else np.nan
    if len(reach_b):
        j = reach_b[0]
        if rr[j] < .3: r['pass'] = '贴线'
        elif abs(hh[j]) >= abs(vv[j]): r['pass'] = '侧绕'
        else: r['pass'] = '越顶' if vv[j] > 0 else '下穿'
    else: r['pass'] = '未到被挡点'
    stop = np.where(u >= ub + .5)[0]; stop = stop[0] if len(stop) else len(u)
    sg = np.sign(hh[:stop][np.abs(hh[:stop]) > .3]); r['switch'] = int((np.diff(sg) != 0).sum()) if len(sg) > 1 else 0
    return r

def load(d):
    R = []
    for f in sorted(glob.glob(os.path.join(d, '*.jsonl*'))):
        x = episode(f)
        if x: R.append(x)
    return R

def q(a):
    a = np.array([x for x in a if np.isfinite(x)])
    return '—' if not len(a) else f'{np.median(a):5.2f} [{np.percentile(a,25):.2f}, {np.percentile(a,75):.2f}] n={len(a)}'

SRC = {'EGO（论文186任务）': EGO, 'BC #E2（dev420）': BCD, 'P6@u256 #E2（dev420）': P6D}
ALL = {k: load(v) for k, v in SRC.items()}
dev_b = {r['task'] for r in ALL['P6@u256 #E2（dev420）'] if r['blocked']}
print(f'dev420 几何判被挡任务 {len(dev_b)}，与 blocked_tasks_dev420.json（{len(BLK_DEV)}）交集 {len(dev_b & BLK_DEV)}')
for name, R in ALL.items():
    B = [r for r in R if r['blocked']]
    print(f'\n== {name}：回合 {len(R)}，被挡回合 {len(B)}（任务 {len({r["task"] for r in B})}）')
    for lab, sel in (('全部被挡', lambda r: True), ('到达', lambda r: r['out'] == 'S'), ('碰撞', lambda r: r['out'] == 'C'), ('超时', lambda r: r['out'] == 'T')):
        S = [r for r in B if sel(r)]
        if not S: continue
        noon = sum(not np.isfinite(r['lead_m']) for r in S)
        ge1 = sum(np.isfinite(r['lead_m']) and r['lead_m'] >= 1.0 for r in S)
        pc = collections.Counter(r['pass'] for r in S)
        sw = collections.Counter(min(r['switch'], 3) for r in S)
        print(f'  [{lab} {len(S)}] 提前距离 m 中位[四分位] {q([r["lead_m"] for r in S])}；提前 ≥1 m 的 {ge1}（{100*ge1/len(S):.0f}%）；被挡点前未偏离 {noon}')
        print(f'      提前时间 s {q([r["lead_s"] for r in S])}；偏离起点处几何净空 m {q([r["onset_clear"] for r in S])}；到被挡点前 1 m 时偏移 m {q([r["r_at_m1"] for r in S])}')
        print(f'      通过方式 {dict(pc)}；换向次数(3=≥3) {dict(sorted(sw.items()))}')
json.dump({k: v for k, v in ALL.items()}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'onset_rows.json'), 'w'), ensure_ascii=False, default=float)
