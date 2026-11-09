"""路径效率（1 m 主终点，任务书 D10；表 3、表 4）。
定义：成功回合（碰撞前进入目标 1 m）上，D0 / (L + d_entry)。D0 为起点到目标的直线距离；L 为执行路径（各决策 executed_path 折线首尾相接）
从起点到首次进入 1 m 的长度（在线段上插值求进入点）；d_entry 为进入点到目标的距离（= 1 m）。按方法与难度取中位数。
运行：python3 -I path_eff_1m.py <rows.json> <输出目录> <traces 目录 ...>
每个 traces 目录下为 *.jsonl；策略名 bc 记为 P0。只统计 rows.json 中 O′ 的 (策略, 任务, 重复)；
校验：由轨迹算出的最小目标距离 < 1 m 与 rows.json 的 near < 1 逐条一致，每个策略 995 条齐全且不重复。"""
import json, sys, glob, math, os, csv, collections, statistics
rows_p, OUT, *DIRS = sys.argv[1:]; os.makedirs(OUT, exist_ok=True)
R = json.load(open(rows_p)); POL = ['P0', 'P2', 'P3', 'P4', 'P6']
want = {(r['policy'], r['task'], int(r['rep'])): r for r in R if r['policy'] in POL}
got = {}
def seg_entry(a, b, g, r=1.0):
    """线段 a→b 上首次距离 g ≤ r 的参数 s∈[0,1]；无则 None。"""
    d = [b[i] - a[i] for i in range(3)]; f = [a[i] - g[i] for i in range(3)]
    A = sum(x * x for x in d); B = 2 * sum(d[i] * f[i] for i in range(3)); C = sum(x * x for x in f) - r * r
    if C <= 0: return 0.0
    if A == 0: return None
    disc = B * B - 4 * A * C
    if disc < 0: return None
    s = (-B - math.sqrt(disc)) / (2 * A)
    return s if 0 <= s <= 1 else None
for D in DIRS:
    for fn in glob.glob(f'{D}/*.jsonl'):
        L = [json.loads(l) for l in open(fn)]
        st, end = L[0], L[-1]; pol = 'P0' if st['policy'] == 'bc' else st['policy']
        key = (pol, st['task_id'], int(st['repeat']))
        if key not in want: continue
        assert key not in got, key
        g = st['task']['goal_pos']; s0 = st['task']['start_pos']
        pts = []
        for t in L[1:-1]:
            if t.get('type') != 'transition': continue
            p = t['executed_path'] if isinstance(t['executed_path'], list) else json.loads(t['executed_path'])
            pts += p if not pts else (p[1:] if p[0] == pts[-1] else p)
        mind = min(math.dist(p, g) for p in pts); Lsum = 0.0; eff = None
        for a, b in zip(pts, pts[1:]):
            s = seg_entry(a, b, g)
            if s is not None:
                e = [a[i] + s * (b[i] - a[i]) for i in range(3)]
                Lsum += math.dist(a, e); eff = math.dist(s0, g) / (Lsum + math.dist(e, g)); break
            Lsum += math.dist(a, b)
        if eff is None and math.dist(pts[0], g) <= 1.0: eff = 1.0
        got[key] = dict(eff=eff, mind=mind, d0=math.dist(s0, g), start_gap=math.dist(pts[0], s0), end=end.get('done_reason'))
miss = set(want) - set(got); assert not miss, (len(miss), list(miss)[:3])
bad = [k for k in want if (got[k]['mind'] < 1.0) != (want[k]['near'] < 1.0 or want[k]['out'] == 'reached')]
gap = max(v['start_gap'] for v in got.values())
DIFF = ['总体', '稀疏', '适中', '密集']
with open(f'{OUT}/path_eff_1m.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['策略', '难度', '成功回合', '路径效率中位数', '四分位下', '四分位上'])
    for p in POL:
        for d in DIFF:
            v = sorted(got[k]['eff'] for k, r in want.items() if k[0] == p and got[k]['eff'] is not None and (d == '总体' or r['cat'] == d))
            q = statistics.quantiles(v, n=4)
            w.writerow([p, d, len(v), f'{statistics.median(v):.3f}', f'{q[0]:.3f}', f'{q[2]:.3f}'])
json.dump(dict(per_policy={p: sum(1 for k in got if k[0] == p) for p in POL}, success_mismatch=len(bad), mismatch_examples=bad[:5], max_start_gap_m=gap),
          open(f'{OUT}/checks.json', 'w'), ensure_ascii=False, indent=1)
print(open(f'{OUT}/path_eff_1m.csv').read()); print(open(f'{OUT}/checks.json').read())
