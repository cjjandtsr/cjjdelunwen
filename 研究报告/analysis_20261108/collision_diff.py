"""O′ 上本文方法与 BC 的碰撞率配对差（世界聚类 bootstrap 20000，种子 2026102601）。
运行：python3 -I collision_diff.py oprime/rows.json；期望输出 -3.2 -8.3 2.0"""
import json, random, collections, sys
R = json.load(open(sys.argv[1])); idx = {(r['policy'], r['task'], r['rep']): r for r in R}
by = collections.defaultdict(lambda: [0, 0])
for r in R:
    if r['policy'] != 'P6': continue
    d = (r['out'] == 'collision') - (idx[('P0', r['task'], r['rep'])]['out'] == 'collision'); by[r['world']][0] += d; by[r['world']][1] += 1
ws = sorted(by); rng = random.Random(2026102601); v = []
for _ in range(20000):
    a = n = 0
    for _ in ws: x = by[rng.choice(ws)]; a += x[0]; n += x[1]
    v.append(a / n)
v.sort(); print(round(100 * sum(x[0] for x in by.values()) / 995, 1), round(100 * v[500], 1), round(100 * v[19499], 1))
