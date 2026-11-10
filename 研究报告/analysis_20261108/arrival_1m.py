"""1 m 目标邻域到达（重新计分，只读）。判据：执行路径在任何碰撞之前首次进入目标 1 m 范围。
评价为确定性采样，到达半径只影响回合在何时终止，因此首次进入 1 m 之前的路径与原评价完全相同；
重新计分等价于以 1 m 半径重新评价，无需重跑。记录字段 nearest_goal_distance_m 为连续执行路径到目标的最小距离
（已用 P15 扩展集 300 条执行记录逐段复算核对，最大差 4.6e-7 m）。碰撞回合的路径止于碰撞点，故 nearest<1 即"碰撞前已进入 1 m"。
运行：python3 -I arrival_1m.py <oprime/rows.json> <OUT>；输出 arrival_1m_main.csv、arrival_1m_pairs.csv"""
import json, sys, os, csv, random, collections
R = json.load(open(sys.argv[1])); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
ok = lambda r: r['out'] == 'reached' or r['near'] < 1.0
P = ['P0', 'P2', 'P3', 'P4', 'P6', 'P14', 'P15']; D = ['总体', '稀疏', '适中', '密集']
idx = {(r['policy'], r['task'], r['rep']): r for r in R}
def boot(items):
    by = collections.defaultdict(lambda: [0, 0])
    for w, a in items: by[w][0] += a; by[w][1] += 1
    ws = sorted(by); rng = random.Random(2026102601); v = []
    for _ in range(20000):
        s = n = 0
        for _ in ws: x = by[rng.choice(ws)]; s += x[0]; n += x[1]
        v.append(s / n)
    v.sort(); return f'[{100*v[500]:.1f}, {100*v[19499]:.1f}]'
with open(f'{OUT}/arrival_1m_main.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['策略', '难度', '回合', '0.5m到达', '1m到达', '其中原超时', '其中原碰撞（碰撞前已入1m）', '1m到达率%', '区间'])
    for p in P:
        for d in D:
            rs = [r for r in R if r['policy'] == p and (d == '总体' or r['cat'] == d)]
            k = sum(map(ok, rs))
            w.writerow([p, d, len(rs), sum(r['out'] == 'reached' for r in rs), k,
                        sum(r['out'] == 'time_limit' and r['near'] < 1 for r in rs), sum(r['out'] == 'collision' and r['near'] < 1 for r in rs),
                        f'{100*k/len(rs):.1f}', boot([(r['world'], ok(r)) for r in rs])])
with open(f'{OUT}/arrival_1m_pairs.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['比较', '难度', '回合', '差值pp', '区间'])
    for a, b in [('P6', 'P0'), ('P2', 'P0'), ('P6', 'P2'), ('P6', 'P4'), ('P6', 'P3'), ('P15', 'P0'), ('P15', 'P14')]:
        for d in D:
            rs = [r for r in R if r['policy'] == a and (d == '总体' or r['cat'] == d)]
            it = [(r['world'], ok(r) - ok(idx[(b, r['task'], r['rep'])])) for r in rs]
            w.writerow([f'{a}-{b}', d, len(rs), f'{100*sum(x for _, x in it)/len(rs):+.1f}', boot(it)])
print(open(f'{OUT}/arrival_1m_main.csv').read()); print(open(f'{OUT}/arrival_1m_pairs.csv').read())
