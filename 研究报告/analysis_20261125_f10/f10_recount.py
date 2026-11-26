"""只读：F10 系统评价的独立复算（dev420、val20）。只需 numpy。

用法：python3 -I f10_recount.py <F10 原迹根> <复用原迹根> <collision_geom.py 所在目录>
  F10 原迹根：项目仓库分支 f10-pack/run01-20261125（提交 1f1eb05）jindu/f10_run01_20261125/packs/<臂>_traces.tar.zst
             逐个解包到 <根>/<臂>/（臂：P6_g1_dev、P6_g1_val、BC_g1_dev、BC_g1_val），并按 traces_manifest.sha256 核对
  复用原迹根：项目仓库 main 的 jindu/ 目录，内含
             routea_p6_u256_e2_dev420_run01/full/P6、routea_f5_run01/results/eval_dev/full/bc、
             routea_f5_run01/results/eval_val/full/{P6,bc}
  collision_geom.py：项目仓库 main 的 Improved-3D-Diffusion-Policy/diffusion_policy_3d/env/
口径：1 m 结局——原迹 done_reason 为 reached，或连续执行路径（逐段线段）到目标的最近距离 < 1 m，记成功；
  否则 done_reason 为 collision/ground_collision 记碰撞，其余记超时。执行路径在碰撞处截断，所以"最近距离 < 1 m"
  只可能发生在碰撞之前。被挡：起点—目标直线上几何净空最小值 < 0.3 m（与 11-20 分析相同）。
"""
import ast, collections, glob, json, os, sys
import numpy as np

F10, REUSE, CG = sys.argv[1:4]
sys.path.insert(0, CG)
from collision_geom import ObstacleSpec, compute_obstacle_clearance

ARMS = {
    ('dev', 'P6'): os.path.join(REUSE, 'routea_p6_u256_e2_dev420_run01/full/P6/traces'),
    ('dev', 'P6_g1'): os.path.join(F10, 'P6_g1_dev/traces'),
    ('dev', 'BC'): os.path.join(REUSE, 'routea_f5_run01/results/eval_dev/full/bc/traces'),
    ('dev', 'BC_g1'): os.path.join(F10, 'BC_g1_dev/traces'),
    ('val', 'P6'): os.path.join(REUSE, 'routea_f5_run01/results/eval_val/full/P6/traces'),
    ('val', 'P6_g1'): os.path.join(F10, 'P6_g1_val/traces'),
    ('val', 'BC'): os.path.join(REUSE, 'routea_f5_run01/results/eval_val/full/bc/traces'),
    ('val', 'BC_g1'): os.path.join(F10, 'BC_g1_val/traces'),
}


def segd(p, a, b):
    d = b - a; L = d @ d; t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1))
    return float(np.linalg.norm(a + t * d - p))


_blocked_cache = {}


def episode(f):
    L = [json.loads(l) for l in open(f) if l.strip()]
    if L[-1].get('type') != 'episode_end': raise SystemExit('incomplete trace ' + f)
    h = L[0]; task = h['task'] if isinstance(h['task'], dict) else ast.literal_eval(h['task'])
    s, g = np.array(task['start_pos'], float), np.array(task['goal_pos'], float)
    T = [t for t in L if t.get('type') == 'transition']
    P = [np.array(T[0]['executed_path'][0], float)]
    for t in T:
        for q in t['executed_path'][1:]: P.append(np.array(q, float))
    P = np.array(P)
    mind = min(segd(g, P[k], P[k + 1]) for k in range(len(P) - 1))
    dr = L[-1]['done_reason']
    out = 'S' if (dr == 'reached' or mind < 1) else ('C' if dr in ('collision', 'ground_collision') else 'T')
    key = (h['task_id'], h['initial_hash'])
    if key not in _blocked_cache:
        obs = [ObstacleSpec.from_dict(o) for o in h['geometry']]
        D = np.linalg.norm(g - s); e = (g - s) / D
        _blocked_cache[key] = min(compute_obstacle_clearance(*(s + u * e), obs)[0]
                                  for u in np.linspace(0, D, int(D / .05) + 2)) < .3
    pm = [t.get('probe_metrics') or {} for t in T]
    trig = sum(1 for m in pm if (m.get('triggered_denoise_steps') or m.get('triggered')))
    fin = float(np.linalg.norm(P[-1] - g))
    return dict(task=h['task_id'], rep=h['repeat'], out=out, blocked=_blocked_cache[key], goal_z=float(g[2]),
                role=h.get('role'), dec=len(T), trig=trig, mind=mind, final_goal=fin)


R = {}
for (split, arm), d in ARMS.items():
    fs = sorted(glob.glob(os.path.join(d, '*.jsonl')))
    eps = [episode(f) for f in fs]
    R[(split, arm)] = {(e['task'], e['rep']): e for e in eps}
    c = collections.Counter(e['out'] for e in eps)
    print('%s %-6s 条件 %d  到达 %d 碰撞 %d 超时 %d' % (split, arm, len(eps), c['S'], c['C'], c['T']))


def paired(split, a, b):
    A, B = R[(split, a)], R[(split, b)]
    assert set(A) == set(B), 'condition sets differ'
    tr = collections.Counter((A[k]['out'], B[k]['out']) for k in A)
    gain = sum(v for (x, y), v in tr.items() if x != 'S' and y == 'S')
    loss = sum(v for (x, y), v in tr.items() if x == 'S' and y != 'S')
    return tr, gain, loss


print('== 配对转移（行：前者结局 → 后者结局）')
for split in ('dev', 'val'):
    for a, b in (('P6', 'P6_g1'), ('BC', 'BC_g1'), ('BC_g1', 'P6_g1')):
        tr, gain, loss = paired(split, a, b)
        print('%s %s → %s：新增到达 %d，流失到达 %d；转移 %s' % (split, a, b, gain, loss,
              {'%s→%s' % k: v for k, v in sorted(tr.items()) if k[0] != k[1]}))

print('== 分层（dev420）：被挡 / 可通行；目标高度 ≤3 m / >3 m')
for arm in ('P6', 'P6_g1', 'BC', 'BC_g1'):
    E = list(R[('dev', arm)].values())
    def cnt(sel):
        c = collections.Counter(e['out'] for e in E if sel(e)); n = sum(c.values())
        return '%d/%d/%d（n=%d）' % (c['S'], c['C'], c['T'], n)
    print('%-6s 被挡 %s  可通行 %s  目标≤3m %s  目标>3m %s' % (arm, cnt(lambda e: e['blocked']), cnt(lambda e: not e['blocked']),
          cnt(lambda e: e['goal_z'] <= 3), cnt(lambda e: e['goal_z'] > 3)))
print('== 被挡任务层面（dev420，每任务 5 次中 ≥3 次到达的任务数）')
for arm in ('P6', 'P6_g1', 'BC', 'BC_g1'):
    by = collections.defaultdict(list)
    for e in R[('dev', arm)].values():
        if e['blocked']: by[e['task']].append(e['out'] == 'S')
    print('%-6s 被挡任务 %d 个，≥3/5 的 %d 个' % (arm, len(by), sum(1 for v in by.values() if sum(v) >= 3)))
print('== 超时的形态（dev420）：结束时离目标距离')
for arm in ('P6', 'P6_g1', 'BC', 'BC_g1'):
    d = np.array([e['final_goal'] for e in R[('dev', arm)].values() if e['out'] == 'T'])
    if len(d): print('%-6s 超时 %d：结束离目标中位 %.2f m，<3 m 的 %d 个' % (arm, len(d), np.median(d), int((d < 3).sum())))
print('== 按任务角色（dev420，到达/碰撞/超时）')
roles = sorted({e['role'] for e in R[('dev', 'P6')].values()})
for role in roles:
    row = []
    for arm in ('P6', 'P6_g1', 'BC', 'BC_g1'):
        c = collections.Counter(e['out'] for e in R[('dev', arm)].values() if e['role'] == role)
        row.append('%s %d/%d/%d' % (arm, c['S'], c['C'], c['T']))
    print(role, ' | '.join(row))

print('== 预先登记判据（F10 方案 v1_0 第五节；工程阈值）')
s0 = collections.Counter(e['out'] for e in R[('dev', 'P6')].values())
s1 = collections.Counter(e['out'] for e in R[('dev', 'P6_g1')].values())
s4 = collections.Counter(e['out'] for e in R[('dev', 'BC_g1')].values())
_, gain, loss = paired('dev', 'P6', 'P6_g1')
q1 = (s0['C'] - s1['C'] >= 15) and (s1['S'] >= s0['S']) and (loss <= 5)
print('Q1：碰撞减少 %d（≥15），到达 %d → %d（不减少），流失 %d（≤5）→ %s' % (s0['C'] - s1['C'], s0['S'], s1['S'], loss, '满足' if q1 else '不满足'))
q2 = s1['S'] - s4['S'] >= 15
print('Q2：P6_g1 − BC_g1 到达差 %d（≥15）→ %s' % (s1['S'] - s4['S'], '满足' if q2 else '不满足'))
