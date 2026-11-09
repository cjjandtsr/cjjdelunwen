"""Gazebo 三方法 288 回合按论文主终点（D10：碰撞前进入目标 1 m）重新判定，并给出 0.5 m（补充 S2）结果。
运行：python3 -I gazebo_analysis.py <jindu/gazebo_3method_288_run01> <输出目录> [exclusions.json]
给出 exclusions.json 时，table5_1m.csv、s2_gazebo_05m.csv、pairs.csv、checks.json 按去除后的任务统计，另写 full48_table_1m.csv（全部 48 个任务，补充材料 S4）；gazebo_rows.json 始终为全部 288 回合。
判定：轨迹（odom 系，goal_odom = goal_world − (start_x, start_y, 0)）任一帧到目标 3D 距离 ≤ r 即成功；
碰撞或越界即结束轨迹记录，故"任一帧 ≤ r"等价于"碰撞前进入"。其余：monitor 为 collision/lost 记碰撞（越界单列计数），否则记超时。
难度：tasks.json 的 zero/low/high 即稀疏/适中/密集。区间：按世界聚类自助法，20000 次，seed 2026102601（工程阈值，非显著性检验）。
执行端汇总 summary_1m.json 采用"碰撞优先"，与 D10 不同：9 个回合（UAV-iDP3 4、本文方法 5）先进入 1 m 后碰撞，本脚本记为成功。"""
import csv, json, math, sys, collections, random, os
G, OUT = sys.argv[1:3]; os.makedirs(OUT, exist_ok=True)
EXC = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {'worlds': [], 'tasks': []}
CAT = {'zero': '稀疏', 'low': '适中', 'high': '密集'}; NAME = {'P0': 'UAV-iDP3', 'P6': '本文方法', 'EGO': 'EGO-Planner'}
rows = []
for r in csv.DictReader(open(f'{G}/regrade_1m.csv')):
    d = f"{G}/{r['method']}/{r['task_id'][:12]}_r{r['repeat']}"
    c = json.load(open(d + '/condition.json'))
    s, g = c['start_pos'], c['goal_pos']; go = (g[0] - s[0], g[1] - s[1], g[2])
    m = min(math.dist((float(x['px']), float(x['py']), float(x['pz'])), go) for x in csv.DictReader(open(d + '/result_state.csv')))
    assert abs(m - float(r['min3d_m'])) < 1e-3
    fail = '碰撞' if r['monitor_status'] in ('collision', 'lost') else '超时'
    rows.append(dict(method=r['method'], task=r['task_id'], rep=r['repeat'], world=r['world'], cat=CAT[r['category']],
                     monitor=r['monitor_status'], min3d=round(m, 4),
                     out1m='成功' if m <= 1.0 else fail, out05='成功' if m <= 0.5 else fail))
json.dump(rows, open(f'{OUT}/gazebo_rows.json', 'w'), ensure_ascii=False, indent=0)
ALL = rows
rows = [r for r in ALL if not any(r['world'].endswith(w) for w in EXC['worlds']) and not any(r['task'].startswith(t) for t in EXC['tasks'])]
print('统计用回合', len(rows), '任务', len({r['task'] for r in rows}), '世界', len({r['world'] for r in rows}))
def table(key):
    T = []
    for d in ['总体', '稀疏', '适中', '密集']:
        for m in ['P0', 'P6', 'EGO']:
            rs = [r for r in rows if r['method'] == m and (d == '总体' or r['cat'] == d)]; k = collections.Counter(r[key] for r in rs); n = len(rs)
            T.append([d, NAME[m], n, k['成功'], k['碰撞'], k['超时'], f"{100*k['成功']/n:.1f}", f"{100*k['碰撞']/n:.1f}", f"{100*k['超时']/n:.1f}"])
    return T
H = ['难度', '方法', '回合', '成功', '碰撞', '超时', '成功率%', '碰撞率%', '超时率%']
if EXC['worlds'] or EXC['tasks']:
    kept = rows; rows = ALL
    with open(f'{OUT}/full48_table_1m.csv', 'w', newline='') as f: w = csv.writer(f); w.writerow(H); w.writerows(table('out1m'))
    rows = kept
for key, fn in [('out1m', 'table5_1m.csv'), ('out05', 's2_gazebo_05m.csv')]:
    with open(f'{OUT}/{fn}', 'w', newline='') as f: w = csv.writer(f); w.writerow(H); w.writerows(table(key))
idx = {(r['method'], r['task'], r['rep']): r for r in rows}
def pair(a, b, key, cat='总体'):
    it = [(r['world'], (r[key] == '成功') - (idx[(b, r['task'], r['rep'])][key] == '成功')) for r in rows if r['method'] == a and (cat == '总体' or r['cat'] == cat)]
    by = collections.defaultdict(lambda: [0, 0])
    for w_, x in it: by[w_][0] += x; by[w_][1] += 1
    ws = sorted(by); rng = random.Random(2026102601); v = []
    for _ in range(20000):
        s_ = n = 0
        for _ in ws: x = by[rng.choice(ws)]; s_ += x[0]; n += x[1]
        v.append(s_ / n)
    v.sort(); return [a, b, key, cat, len(it), len(ws), round(100 * sum(x for _, x in it) / len(it), 1), round(100 * v[500], 1), round(100 * v[19499], 1)]
with open(f'{OUT}/pairs.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['方法', '对照', '判据', '难度', '配对回合', '世界数', '差%', '区间下%', '区间上%'])
    for key in ['out1m', 'out05']:
        for cat in ['总体', '稀疏', '适中', '密集']: w.writerow(pair('P6', 'P0', key, cat))
        w.writerow(pair('EGO', 'P6', key))
lost = collections.Counter(r['method'] for r in rows if r['monitor'] == 'lost')
trans = collections.Counter((idx[('P0', r['task'], r['rep'])]['out1m'], r['out1m']) for r in rows if r['method'] == 'P6')
coll_after = collections.Counter(r['method'] for r in rows if r['out1m'] == '成功' and r['monitor'] in ('collision', 'lost'))
json.dump(dict(lost=lost, p0_to_p6_1m={f'{a}->{b}': n for (a, b), n in trans.items()}, success_then_collision_1m=coll_after),
          open(f'{OUT}/checks.json', 'w'), ensure_ascii=False, indent=1)
print(open(f'{OUT}/table5_1m.csv').read()); print(open(f'{OUT}/s2_gazebo_05m.csv').read()); print(open(f'{OUT}/pairs.csv').read()); print(open(f'{OUT}/checks.json').read())
