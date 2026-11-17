"""只读：任务几何（f7_task_feasibility.py 输出）与五个策略（P6、P16—P19）及 BC 的 dev420 1 m 结局的关系。
用法：python3 -I f7_feas_vs_outcome.py <task_feas.json> <episodes.json> <项目仓库根目录>"""
import json, sys, collections, glob, ast
import numpy as np
F = json.load(open(sys.argv[1])); E = json.load(open(sys.argv[2])); repo = sys.argv[3]
pols = ['P6', 'P16', 'P17', 'P18', 'P19']
agg = collections.defaultdict(lambda: collections.Counter())
for r in E:
    if r['split'] == 'dev' and r['pol'] in pols: agg[r['task']][r['out']] += 1
def bucket(f):
    if f['line_min'] >= .3: return 'A 直线可通过（直线净空 ≥0.3 m）'
    return 'B 直线被挡，绕行比 ≤1.10' if (f['detour'] or 9) <= 1.10 else 'C 直线被挡，绕行比 >1.10'
B = collections.defaultdict(lambda: collections.Counter()); nt = collections.Counter()
for t, f in F.items(): B[bucket(f)].update(agg[t]); nt[bucket(f)] += 1
print('按几何分组（五个策略合计，每任务 5 次 × 5 策略）：')
for k in sorted(B):
    c = B[k]; n = sum(c.values()); print('  %s：任务 %d，成功 %.0f%%，碰撞 %.0f%%，超时 %.0f%%' % (k, nt[k], 100 * c['S'] / n, 100 * c['C'] / n, 100 * c['T'] / n))
print('所有任务均存在净空 ≥0.3 m 的连通路线：', all(f['detour'] is not None for f in F.values()),
      '；瓶颈净空 c* 最小值 %.2f m；绕行比最大 %.2f' % (min(f['cstar'] for f in F.values()), max(f['detour'] for f in F.values())))
blk = [t for t, f in F.items() if f['line_min'] < .3]
print('直线被挡的任务 %d 个：五策略碰撞率 %.0f%%；直线可通过的任务碰撞率 %.0f%%' % (len(blk),
      100 * sum(agg[t]['C'] for t in blk) / sum(sum(agg[t].values()) for t in blk),
      100 * sum(agg[t]['C'] for t in F if t not in blk) / sum(sum(agg[t].values()) for t in F if t not in blk)))
by = collections.defaultdict(list)
for t in blk: by[t.split('__rl_train__')[1].rsplit('__', 3)[0]].append(agg[t]['C'] / sum(agg[t].values()))
print('直线被挡任务按场景的碰撞率：', {k: '%d 任务 %.0f%%' % (len(v), 100 * np.mean(v)) for k, v in sorted(by.items())})
# BC 同口径（读 F5 的 bc 原迹，1 m 判定同 f7_episodes.py）
def seg_dist(p, a, b):
    a, b, p = map(np.asarray, (a, b, p)); d = b - a; L = d @ d
    t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))
bcB = collections.defaultdict(collections.Counter)
for f in glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_dev/full/bc/traces/*.jsonl'):
    L = [json.loads(l) for l in open(f)]; s, e = L[0], L[-1]; T = [t for t in L if t.get('type') == 'transition']
    task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task']); g = task['goal_pos']
    mind = min((seg_dist(g, P[k], P[k + 1]) for t in T for P in [t['executed_path']] for k in range(len(P) - 1)), default=1e9)
    o = 'S' if (e['done_reason'] == 'reached' or mind < 1) else ('C' if e['done_reason'] in ('collision', 'ground_collision') else 'T')
    bcB[bucket(F[s['task_id']])][o] += 1
print('BC 按同一几何分组：')
for k in sorted(bcB):
    c = bcB[k]; n = sum(c.values()); print('  %s：成功 %.0f%%，碰撞 %.0f%%，超时 %.0f%%（%d 回合）' % (k, 100 * c['S'] / n, 100 * c['C'] / n, 100 * c['T'] / n, n))
