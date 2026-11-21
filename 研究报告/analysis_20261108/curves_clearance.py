"""训练曲线（16 轮一块的采集到达率、近似 KL 中位数）与安全余量汇总（只读）。
运行：python3 -I curves_clearance.py <training_curves.csv> <clearance.csv> <rows.json> <OUT>
到达率 = Σreached / Σcompleted_episodes；安全余量 = 每回合执行路径到障碍表面的最小距离（已减机体半径前的原始值，按导出列 clearance_m）。"""
import csv, sys, json, collections, statistics, os
cur, clr, rowsf, OUT = sys.argv[1:5]; os.makedirs(OUT, exist_ok=True)
R = list(csv.DictReader(open(cur)))
print('policies', collections.Counter(r['policy'] for r in R))
blk = collections.defaultdict(lambda: [0, 0, []])
for r in R:
    u = int(r['update']); b = (r['policy'], (u - 1) // 16)
    blk[b][0] += int(r['reached']); blk[b][1] += int(r['completed_episodes']); blk[b][2].append(float(r['approx_kl_mean']))
with open(f'{OUT}/curve_blocks.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['策略', '轮', '采集到达率%', 'KL中位数'])
    for (p, b), (a, n, kl) in sorted(blk.items()):
        w.writerow([p, f'u{16*b+1}-{16*b+16}', f'{100*a/n:.1f}', f'{statistics.median(kl):.2e}'])
C = list(csv.DictReader(open(clr)))
cat = {(r['task'], r['rep']): r['cat'] for r in json.load(open(rowsf)) if r['policy'] == 'P0'}
with open(f'{OUT}/clearance.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['策略', '类别', '回合', '到达回合安全余量中位数m', '全部未碰撞回合安全余量中位数m'])
    for p in sorted({r['policy'] for r in C}):
        for c in [None, '稀疏', '适中', '密集']:
            rs = [r for r in C if r['policy'] == p and (c is None or cat[(r['task_id'], int(r['repeat']))] == c)]
            a = [float(r['clearance_m']) for r in rs if r['done_reason'] == 'reached']
            nc = [float(r['clearance_m']) for r in rs if r['done_reason'] != 'collision']
            w.writerow([p, c or '总体', len(rs), f'{statistics.median(a):.3f}', f'{statistics.median(nc):.3f}'])
print(open(f'{OUT}/curve_blocks.csv').read()); print(open(f'{OUT}/clearance.csv').read())
