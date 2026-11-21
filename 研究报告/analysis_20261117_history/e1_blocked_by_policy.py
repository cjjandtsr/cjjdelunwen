"""只读：#E1 dev420（A2 回传）上 BC、P2@u128、P4@u256（分叉不加保持项）、P6@u256（加保持项）在直线被挡 / 可通过任务上的 1 m 结局。
用法：python3 -I e1_blocked_by_policy.py <A2 evaluation_dev/full 目录> <blocked_tasks_dev420.json> [F5 eval_dev/full 目录（可选，#E2 的 bc、P6 对照）]
策略目录：bc、rl_391a6656a0f7_u128 = P2@u128、rl_910559bb5de2_u256 = P4@u256（A2 的 C 臂）、rl_d987235a0cbb_u256 = P6@u256（A2 的 T 臂）。
同一 (task, repeat) 有多个 attempt 时，取含 episode_end 的最后一个。1 m 结局：执行路径逐段到目标中心最近距离 < 1 m 或原结局 reached → 成功；原结局为碰撞类 → 碰撞；其余 → 超时。
原迹可为 .jsonl 或 .jsonl.gz。"""
import ast, glob, gzip, json, os, sys, collections
import numpy as np
full, blkf = sys.argv[1], sys.argv[2]; BLK = set(json.load(open(blkf)))
def seg(p, a, b):
    a, b, p = map(np.asarray, (a, b, p)); d = b - a; L = d @ d
    t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))
def load(d):
    out = {}
    for f in sorted(glob.glob(os.path.join(d, 'traces', '*.jsonl*'))):
        op = gzip.open if f.endswith('.gz') else open
        L = [json.loads(l) for l in op(f, 'rt') if l.strip()]
        if L[-1].get('type') != 'episode_end': continue
        s = L[0]; task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task']); g = task['goal_pos']
        T = [t for t in L if t.get('type') == 'transition']
        mind = min((seg(g, P[k], P[k + 1]) for t in T for P in [t['executed_path']] for k in range(len(P) - 1)), default=1e9)
        dr = L[-1]['done_reason']
        out[(s['task_id'], s['repeat'])] = 'S' if (dr == 'reached' or mind < 1) else ('C' if dr in ('collision', 'ground_collision') else 'T')
    return out
names = [('BC', 'bc'), ('P2@u128', 'rl_391a6656a0f7_u128'), ('P4@u256 不加保持项', 'rl_910559bb5de2_u256'), ('P6@u256 加保持项', 'rl_d987235a0cbb_u256')]
R = {n: load(os.path.join(full, d)) for n, d in names}
if len(sys.argv) > 3:
    R['BC #E2'] = load(os.path.join(sys.argv[3], 'bc')); R['P6 #E2'] = load(os.path.join(sys.argv[3], 'P6'))
keys = set.intersection(*[set(v) for v in R.values()]); print('共同条件', len(keys), '；被挡条件', sum(k[0] in BLK for k in keys))
for n, v in R.items():
    for grp, sel in (('直线被挡', lambda k: k[0] in BLK), ('直线可通过', lambda k: k[0] not in BLK)):
        c = collections.Counter(v[k] for k in keys if sel(k)); m = sum(c.values())
        print('%-18s %s：到达 %3d / 碰撞 %3d / 超时 %3d（共 %d）' % (n, grp, c['S'], c['C'], c['T'], m))
print('配对（直线被挡条件）：')
for a, b in (('P2@u128', 'P4@u256 不加保持项'), ('P2@u128', 'P6@u256 加保持项'), ('P6@u256 加保持项', 'P4@u256 不加保持项')):
    K = [k for k in keys if k[0] in BLK]; m = collections.Counter((R[a][k], R[b][k]) for k in K)
    print('  %s → %s：' % (a, b), dict(sorted(m.items())))
tb = collections.defaultdict(lambda: collections.Counter())
for n, v in R.items():
    for k in keys:
        if k[0] in BLK and v[k] == 'S': tb[n][k[0]] += 1
print('被挡任务中至少成功一次的任务数（共 %d 个任务）：' % len({k[0] for k in keys if k[0] in BLK}), {n: len(tb[n]) for n in R})
# 各被挡任务：哪些策略成功过（5 次重复中的成功次数）
allt = sorted({k[0] for k in keys if k[0] in BLK}); union = [t for t in allt if any(tb[n][t] for n in R)]
print('任一策略成功过的被挡任务：%d / %d；从未有策略成功的：%d' % (len(union), len(allt), len(allt) - len(union)))
for t in union: print('   %-60s' % t.split('__rl_train__')[1][:58], ' '.join('%s=%d' % (n.split('@')[0].split(' ')[0] + ('E2' if 'E2' in n else ''), tb[n][t]) for n in R))
