"""G16（F3@u256 三个 seed）分析：预先登记判定 R1 与 C3b（只读）。Claude，2026-11-05。
依据：执行指引/2026-11-04_F3u256补训seed与评价_Codex方案_v1_1.md §四。

输入
  G16 : G16 实验数据包目录（routea_f3_u256_e2_run02_audit_20261105/）：{dev,val,test,ext}_{P9,P11}_episode_package.json，reference_O/
  G3E : g3_analysis.py 生成的 episodes_all.csv（P0/P2/P4/P6 的 dev420、val20、test12）
  C5  : C5 实验数据包目录（P0/P2/P4/P6 扩展集）
运行：python3 -I g16_analysis.py <G16> <G3E> <C5> <OUT>
输出：g16_main.csv（各策略×集合结局）、g16_pairs.csv（配对差与区间）、g16_class.csv（O 上分类）、g16_timeouts.csv、checks.txt
统计：世界聚类 bootstrap 20000 次，种子 2026102601。O = test12 ∪ 扩展集。"""
import csv, json, os, sys, random, collections
G16, G3E, C5, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
B, SEED = 20000, 2026102601
DUP = 'routeA_rl_v1__yaw_lateral_recovery__rl_test__initial_yaw_offset_corridor__000015'
CAT = {'zero': 'Sparse', 'low': 'Moderate', 'high': 'Dense'}
SPL = {'dev': 'dev420', 'val': 'val20', 'test': 'test12', 'ext': 'ext'}
rows, checks = [], []
for r in csv.DictReader(open(G3E)):
    rows.append(dict(policy=r['policy'], split=r['split'], task=r['task'], rep=int(r['rep']), world=r['world'],
                     outcome=r['outcome'], cat=r['cat'], mind=float(r['mind'])))
for pol, fn in (('P0', 'bc'), ('P2', 'P2'), ('P4', 'P4'), ('P6', 'P6')):
    for r in json.load(open(os.path.join(C5, f'{fn}_episode_package.json')))['records']:
        rows.append(dict(policy=pol, split='ext', task=r['task_id'], rep=int(r['repeat']), world=r['world_id'],
                         outcome=r['done_reason'], cat=CAT[r['category']], mind=float(r['trajectory_metrics']['min_goal_distance_m'])))
for s in ('dev', 'val', 'test', 'ext'):
    for pol in ('P9', 'P11'):
        pk = json.load(open(os.path.join(G16, f'{s}_{pol}_episode_package.json')))
        for r in pk['records']:
            assert r['protocol'] == 'E2' and r['status'] == 'valid' and r['policy'] == pol
            rows.append(dict(policy=pol, split=SPL[s], task=r['task_id'], rep=int(r['repeat']), world=r['world_id'],
                             outcome=r['done_reason'], cat=CAT[r['category']], mind=float(r['trajectory_metrics']['min_goal_distance_m'])))
idx = {(r['policy'], r['split'], r['task'], r['rep']): r for r in rows}
# 核对：参考包与本地来源结局一致；各策略条件集合一致；类别一致
for f in os.listdir(os.path.join(G16, 'reference_O')):
    s, p = f[:-5].split('_'); pol = 'P0' if p == 'bc' else p
    pk = json.load(open(os.path.join(G16, 'reference_O', f)))
    mism = sum(idx[(pol, SPL[s], r['task_id'], int(r['repeat']))]['outcome'] != r['done_reason'] for r in pk['records'])
    checks.append(f'reference_O {f}: {len(pk["records"])} records, outcome mismatches vs local sources = {mism}')
cnt = collections.Counter((r['policy'], r['split']) for r in rows)
checks.append('counts ' + str(sorted(cnt.items())))
for s in ('dev420', 'val20', 'test12', 'ext'):
    ks = {p: {(r['task'], r['rep']) for r in rows if r['policy'] == p and r['split'] == s} for p in ('P0', 'P2', 'P4', 'P6', 'P9', 'P11')}
    checks.append(f'{s}: identical condition sets = {len({frozenset(v) for v in ks.values()}) == 1}')
    cats = collections.defaultdict(set)
    for r in rows:
        if r['split'] == s: cats[(r['task'])].add(r['cat'])
    checks.append(f'{s}: tasks with inconsistent category across sources = {sum(len(v) > 1 for v in cats.values())}')

SETS = {'dev420': ('dev420',), 'val20': ('val20',), 'test12': ('test12',), 'ext': ('ext',), 'O': ('test12', 'ext')}
def sel(p, s, cat=None, drop=None):
    return [r for r in rows if r['policy'] == p and r['split'] in SETS[s] and (cat is None or r['cat'] == cat) and r['world'] != drop]
def boot(sl, stat):
    ws = sorted({r['world'] for r in sl})
    if len(ws) < 5: return None
    by = collections.defaultdict(list)
    for r in sl: by[r['world']].append(r)
    rng = random.Random(SEED); v = []
    for _ in range(B):
        v.append(stat([x for w in (rng.choice(ws) for _ in ws) for x in by[w]]))
    v.sort(); return v[int(.025 * B)], v[int(.975 * B) - 1]
fmt = lambda ci: '' if ci is None else f'[{100*ci[0]:.1f}, {100*ci[1]:.1f}]'
def pair(a, b, s, cat=None, drop=None):
    return [dict(world=r['world'], a=r['outcome'], b=idx[(b, r['split'], r['task'], r['rep'])]['outcome']) for r in sel(a, s, cat, drop)]
dst = lambda x: (sum(e['a'] == 'reached' for e in x) - sum(e['b'] == 'reached' for e in x)) / len(x)

POL = ('P0', 'P2', 'P4', 'P6', 'P9', 'P11')
main = []
for s in ('dev420', 'val20', 'test12', 'ext', 'O'):
    for p in POL:
        c = collections.Counter(r['outcome'] for r in sel(p, s)); n = sum(c.values())
        main.append(dict(set=s, policy=p, n=n, reached=c['reached'], collision=c['collision'], time_limit=c['time_limit'],
                         arrival_pct=f"{100*c['reached']/n:.1f}"))
prs = []
for s, drop in (('O', None), ('O', DUP), ('dev420', None), ('val20', None), ('test12', None), ('ext', None)):
    for a, b in (('P6', 'P0'), ('P9', 'P0'), ('P11', 'P0'), ('P9', 'P6'), ('P11', 'P6'), ('P9', 'P4'), ('P11', 'P4'), ('P6', 'P4'), ('P9', 'P2'), ('P11', 'P2'), ('P6', 'P2')):
        pr = pair(a, b, s, drop=drop); ci = boot(pr, dst)
        prs.append(dict(set=s + ('_dedup' if drop else ''), a=a, b=b, n=len(pr), diff_pct=f'{100*dst(pr):.1f}', ci=fmt(ci),
                        lower_gt0='' if ci is None else str(ci[0] > 0),
                        new=sum(e['a'] == 'reached' and e['b'] != 'reached' for e in pr),
                        lost=sum(e['b'] == 'reached' and e['a'] != 'reached' for e in pr)))
cls = []
for cat in ('Sparse', 'Moderate', 'Dense'):
    for p in POL:
        c = collections.Counter(r['outcome'] for r in sel(p, 'O', cat)); n = sum(c.values())
        cls.append(dict(category=cat, policy=p, n=n, reached=c['reached'], collision=c['collision'], time_limit=c['time_limit'],
                        arrival_pct=f"{100*c['reached']/n:.1f}"))
tout = []
for s in ('dev420', 'val20', 'test12', 'ext'):
    for p in ('P9', 'P11', 'P6'):
        ts = sorted(r['mind'] for r in sel(p, s) if r['outcome'] == 'time_limit')
        tout.append(dict(set=s, policy=p, timeouts=len(ts), lt2m=sum(x < 2 for x in ts), lt1m=sum(x < 1 for x in ts)))
for name, tab in (('g16_main', main), ('g16_pairs', prs), ('g16_class', cls), ('g16_timeouts', tout)):
    with open(os.path.join(OUT, name + '.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(tab[0])); w.writeheader(); w.writerows(tab)
open(os.path.join(OUT, 'checks.txt'), 'w').write('\n'.join(checks) + '\n')
print('\n'.join(checks))
