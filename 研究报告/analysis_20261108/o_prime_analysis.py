"""O′（test12 ∪ 扩展集 v2，995 回合/策略）论文线主分析（只读）。
运行：python3 -I o_prime_analysis.py <G3包目录> <C5包目录> <G17包目录> <P3包目录> <增量包目录> <P15包目录> <extv2_tasks.json> <OUT>
  G3：eval_test_{bc,P2,P4,P6}_package.json、banks/test12.json；C5：{bc,P2,P4,P6}_episode_package.json；
  G17：test_P14_package.json、ext_P14_package.json；P3：test_P3_package.json、ext_P3_package.json；
  增量：{bc,P2,P3,P4,P6,P14}.json（455）；P15：test/P15.json、ext/P15.json（240+755）。
统计：世界聚类 bootstrap，20000 次，种子 2026102601（与 C5、G3 分析相同实现）。
输出：main.csv（评价集×类别×策略）、pairs.csv（配对差、新增/流失）、timeouts.csv、behavior.csv、checks.txt"""
import json, os, sys, csv, random, collections, statistics, math
G3, C5, G17, P3D, ADD, P15D, TASKS, OUT = sys.argv[1:9]
os.makedirs(OUT, exist_ok=True)
B, SEED = 20000, 2026102601
POL = ['P0', 'P2', 'P3', 'P4', 'P6', 'P14', 'P15']
src = {
 'P0': {'test': f'{G3}/eval_test_bc_package.json', 'r02': f'{C5}/bc_episode_package.json', 'add': f'{ADD}/bc.json'},
 'P2': {'test': f'{G3}/eval_test_P2_package.json', 'r02': f'{C5}/P2_episode_package.json', 'add': f'{ADD}/P2.json'},
 'P4': {'test': f'{G3}/eval_test_P4_package.json', 'r02': f'{C5}/P4_episode_package.json', 'add': f'{ADD}/P4.json'},
 'P6': {'test': f'{G3}/eval_test_P6_package.json', 'r02': f'{C5}/P6_episode_package.json', 'add': f'{ADD}/P6.json'},
 'P3': {'test': f'{P3D}/test_P3_package.json', 'r02': f'{P3D}/ext_P3_package.json', 'add': f'{ADD}/P3.json'},
 'P14': {'test': f'{G17}/test_P14_package.json', 'r02': f'{G17}/ext_P14_package.json', 'add': f'{ADD}/P14.json'},
}
checks = []
D0 = {}
for t in json.load(open(f'{G3}/banks/test12.json'))['tasks']:
    D0[t['task_id']] = math.dist(t['payload']['start_pos'], t['payload']['goal_pos'])
for t in json.load(open(TASKS)): D0[t['task_id']] = t['D0']
CAT = {'zero': '稀疏', 'low': '适中', 'high': '密集'}
rows = []
def add(p, part, rs):
    for r in rs:
        rows.append(dict(policy=p, part=part, task=r['task_id'], rep=r['repeat'], world=r['world_id'], cat=CAT[r['category']],
                         out=r['done_reason'], near=r['nearest_goal_distance_m'], tm=r['trajectory_metrics'], t=r['physical_time_s'],
                         init=r.get('initial_hash')))
for p, d in src.items():
    for part, f in d.items():
        rs = json.load(open(f))['records']; add(p, part, rs)
        checks.append(f'{p} {part} {len(rs)}')
p15t = json.load(open(f'{P15D}/test/P15.json'))['records']; p15e = json.load(open(f'{P15D}/ext/P15.json'))['records']
addkeys = {(r['task'], r['rep']) for r in rows if r['policy'] == 'P0' and r['part'] == 'add'}
add('P15', 'test', p15t)
add('P15', 'r02', [r for r in p15e if (r['task_id'], r['repeat']) not in addkeys])
add('P15', 'add', [r for r in p15e if (r['task_id'], r['repeat']) in addkeys])
# 一致性检查：每策略 995，条件集合与初态相同
keyset = {p: {(r['part'], r['task'], r['rep']) for r in rows if r['policy'] == p} for p in POL}
init = {p: {(r['task'], r['rep']): r['init'] for r in rows if r['policy'] == p} for p in POL}
for p in POL:
    n = collections.Counter(r['part'] for r in rows if r['policy'] == p)
    checks.append(f'{p} 回合 {dict(n)} 合计 {sum(n.values())} 条件集=P0:{keyset[p] == keyset["P0"]} 初态一致:{sum(init[p][k] == init["P0"][k] for k in init["P0"])}/995')
    assert sum(n.values()) == 995 and keyset[p] == keyset['P0']
catk = {(r['task'], r['rep']): r['cat'] for r in rows if r['policy'] == 'P0'}
for p in POL: assert all(catk[(r['task'], r['rep'])] == r['cat'] for r in rows if r['policy'] == p)
idx = {(r['policy'], r['task'], r['rep']): r for r in rows}
SETS = {'训练外I(test12)': {'test'}, '训练外II(扩展v2)': {'r02', 'add'}, 'O′': {'test', 'r02', 'add'}, '新增': {'add'}, '原O': {'test', 'r02'}}
def sel(p, s, c=None): return [r for r in rows if r['policy'] == p and r['part'] in SETS[s] and (c is None or r['cat'] == c)]
def boot_w(items):  # items: list of (world, a, n)；统计量 sum(a)/sum(n)
    by = collections.defaultdict(lambda: [0.0, 0]); 
    for w, a, n in items: by[w][0] += a; by[w][1] += n
    ws = sorted(by)
    if len(ws) < 5: return None
    rng = random.Random(SEED); vals = []
    for _ in range(B):
        sa = sn = 0
        for _ in ws:
            v = by[rng.choice(ws)]; sa += v[0]; sn += v[1]
        vals.append(sa / sn)
    vals.sort(); return vals[int(.025 * B)], vals[int(.975 * B) - 1]
fmt = lambda ci: 'n/a' if ci is None else f'[{100*ci[0]:.1f}, {100*ci[1]:.1f}]'
eff = lambda r: D0[r['task']] / r['tm']['path_length_m']
med = lambda v: round(statistics.median(v), 3) if v else ''
with open(f'{OUT}/main.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['评价集', '类别', '策略', '回合', '世界', '到达', '碰撞', '超时', '到达率%', '区间', '路径效率中位数'])
    for s in ['O′', '训练外I(test12)', '训练外II(扩展v2)', '新增']:
        for c in [None, '稀疏', '适中', '密集']:
            for p in POL:
                rs = sel(p, s, c)
                if not rs: continue
                k = collections.Counter(r['out'] for r in rs)
                ci = boot_w([(r['world'], r['out'] == 'reached', 1) for r in rs])
                w.writerow([s, c or '总体', p, len(rs), len({r['world'] for r in rs}), k['reached'], k['collision'], k['time_limit'],
                            f"{100*k['reached']/len(rs):.1f}", fmt(ci), med([eff(r) for r in rs if r['out'] == 'reached'])])
CMP = [('P6', 'P0'), ('P15', 'P0'), ('P2', 'P0'), ('P14', 'P0'), ('P4', 'P0'), ('P3', 'P0'), ('P6', 'P2'), ('P6', 'P4'), ('P6', 'P3'),
       ('P4', 'P2'), ('P3', 'P2'), ('P15', 'P14'), ('P15', 'P6'), ('P14', 'P2')]
with open(f'{OUT}/pairs.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['评价集', '类别', '比较', '回合', '差值pp', '区间', '新增', '流失'])
    for s in ['O′', '训练外I(test12)', '训练外II(扩展v2)', '新增']:
        for c in [None, '稀疏', '适中', '密集']:
            for a, b in CMP:
                rs = sel(a, s, c)
                if not rs: continue
                it = [(r['world'], (r['out'] == 'reached') - (idx[(b, r['task'], r['rep'])]['out'] == 'reached'), 1) for r in rs]
                gain = sum(1 for _, d, _ in it if d == 1); loss = sum(1 for _, d, _ in it if d == -1)
                w.writerow([s, c or '总体', f'{a}-{b}', len(rs), f'{100*(gain-loss)/len(rs):+.1f}', fmt(boot_w(it)), gain, loss])
with open(f'{OUT}/timeouts.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['评价集', '策略', '超时', '<1m', '1-2m', '>2m', '中位数m'])
    for s in ['O′', '新增']:
        for p in POL:
            d = [r['near'] for r in sel(p, s) if r['out'] == 'time_limit']
            w.writerow([s, p, len(d), sum(x < 1 for x in d), sum(1 <= x < 2 for x in d), sum(x >= 2 for x in d), med(d)])
with open(f'{OUT}/behavior.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['评价集', '类别', '策略', '到达回合', '路径效率', '最大横向偏离m', '高度范围m', '回退m', '飞行时间s'])
    for s in ['O′']:
        for c in [None, '稀疏', '适中', '密集']:
            for p in POL:
                rs = [r for r in sel(p, s, c) if r['out'] == 'reached']
                w.writerow([s, c or '总体', p, len(rs), med([eff(r) for r in rs]), med([r['tm']['max_cross_track_m'] for r in rs]),
                            med([r['tm']['z_span_m'] for r in rs]), med([r['tm']['backtrack_m'] for r in rs]), med([r['t'] for r in rs])])
json.dump([{k: v for k, v in r.items() if k != 'tm'} for r in rows], open(f'{OUT}/rows.json', 'w'))
open(f'{OUT}/checks.txt', 'w').write('\n'.join(checks) + '\n')
print('\n'.join(checks)); print('done')
