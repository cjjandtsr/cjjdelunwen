"""只读：dev420 上"碰撞核心"（P6、P16—P19 五个策略中 ≥4 个碰撞的条件）的构成，及 BC 在这些条件上的结局。
用法：python3 -I f7_collision_core.py <项目仓库根目录> <episodes.json>
BC 原迹：jindu/routea_f5_run01/results/eval_dev/full/bc/traces/*.jsonl（1 m 判定同 f7_episodes.py）"""
import glob, json, math, sys, collections, re
# 2026-11-17：项目仓库整理后，这些原迹改为精简的 *.jsonl.gz（所用字段均保留）；本脚本同时接受 *.jsonl 与 *.jsonl.gz。
import gzip as _gz
_topen = lambda f: _gz.open(f, 'rt') if f.endswith('.gz') else open(f)
import numpy as np
repo, ep = sys.argv[1], sys.argv[2]
R = json.load(open(ep)); dev = collections.defaultdict(dict)
for r in R:
    if r['split'] == 'dev': dev[r['pol']][(r['task'], r['rep'])] = r
def seg_dist(p, a, b):
    a, b, p = map(np.asarray, (a, b, p)); d = b - a; L = d @ d
    t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))
bc = {}
for f in glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_dev/full/bc/traces/*.jsonl*'):
    L = [json.loads(l) for l in _topen(f)]; s, e = L[0], L[-1]; T = [t for t in L if t.get('type') == 'transition']
    import ast; task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task']); g = task['goal_pos']
    mind = min((seg_dist(g, P[k], P[k + 1]) for t in T for P in [t['executed_path']] for k in range(len(P) - 1)), default=1e9)
    bc[(s['task_id'], s['repeat'])] = 'S' if (e['done_reason'] == 'reached' or mind < 1) else ('C' if e['done_reason'] in ('collision', 'ground_collision') else 'T')
pols = ['P6', 'P16', 'P17', 'P18', 'P19']; ks = list(dev['P6'])
core = [k for k in ks if sum(dev[p][k]['out'] == 'C' for p in pols) >= 4]
print('碰撞核心条件 %d 个（5 个策略中 ≥4 个碰撞）；每个策略的碰撞中落在核心内的比例：' % len(core),
      {p: '%d/%d' % (sum(dev[p][k]['out'] == 'C' for k in core), sum(r['out'] == 'C' for r in dev[p].values())) for p in pols})
print('BC 在核心条件上的结局：', dict(collections.Counter(bc[k] for k in core)), '；BC 全部 dev420：', dict(collections.Counter(bc.values())))
fam = lambda w: re.sub(r'^routeA_rl_v1__[a-z_]+__rl_train__', '', w).rsplit('__', 1)[0]
print('核心条件的场景类型：', collections.Counter(fam(dev['P6'][k]['world']) for k in core).most_common())
print('全部条件的场景类型：', collections.Counter(fam(dev['P6'][k]['world']) for k in ks).most_common())
print('核心条件的角色：', dict(collections.Counter(dev['P6'][k]['role'] for k in core)))
print('核心条件的世界数 %d，任务数 %d' % (len({dev['P6'][k]['world'] for k in core}), len({k[0] for k in core})))
C = [dev[p][k] for p in pols for k in core]
print('核心碰撞：撞前进度中位 %.2f，D0 中位 %.1f m，碰撞时决策数中位 %d' % (np.median([c['prog'] for c in C]), np.median([c['D0'] for c in C]), np.median([c['n'] for c in C])))
