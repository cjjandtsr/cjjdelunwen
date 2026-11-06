"""任务C 第5步：扩展集 #E2 结果分析，以及与 test12 合并后的预先登记判定 C2、C3 条件②（只读）。Claude，2026-11-04。

输入
  C5 : C5 run02 实验数据包目录（routea_paper_c5_run02_audit_20261104/）：{bc,P2,P4,P6}_episode_package.json、bank.json
  G3 : G3 实验数据包目录（routea_paper_g3_e2_audit_20261103/）：episodes.csv（test12 四策略各 240 回合）、banks/
运行
  python3 -I c5_analysis.py <C5> <G3> <OUT_DIR>
输出（OUT_DIR）：checks.txt、table_main.csv、table_pairs.csv、table_class.csv、table_transitions.csv、table_timeouts.csv
统计：按世界聚类的 bootstrap，20000 次，种子 2026102601；世界数 <5 的格只报计数（与 G3 分析相同）。
预期（2026-11-04 首次运行）：ext 到达 P0/P2/P4/P6 = 107/134/128/144；合并集 C2 的 P6−P0 区间下界 >0。
"""
import csv, json, glob, os, sys, random, math, collections

C5, G3, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
B, SEED = 20000, 2026102601
DUP_WORLD = 'routeA_rl_v1__yaw_lateral_recovery__rl_test__initial_yaw_offset_corridor__000015'
CAT = {'zero': 'Sparse', 'low': 'Moderate', 'high': 'Dense'}
POL = ('P0', 'P2', 'P4', 'P6')
checks = []

bank = json.load(open(os.path.join(C5, 'bank.json')))
BANK_HASH = '0b64e3ed8e6fe7b1cc780f1b90bfdcba5e3040c6aea246c303c45a7251ad5017'
checks.append(f"ext bank content_hash = {bank['content_hash']} (expected run02: {bank['content_hash'] == BANK_HASH})")
bank_cat = {t['task_id']: t['category'] for t in bank['tasks']}
D0 = {t['task_id']: math.dist(t['payload']['start_pos'], t['payload']['goal_pos']) for t in bank['tasks']}
for f in glob.glob(os.path.join(G3, 'banks', '*.json')):
    for t in json.load(open(f))['tasks']:
        D0[t['task_id']] = math.dist(t['payload']['start_pos'], t['payload']['goal_pos'])

rows = []
for pol, fn in (('P0', 'bc'), ('P2', 'P2'), ('P4', 'P4'), ('P6', 'P6')):
    pk = json.load(open(os.path.join(C5, f'{fn}_episode_package.json')))
    for r in pk['records']:
        assert r['bank_hash'] == BANK_HASH and r['protocol'] == 'E2' and r['status'] == 'valid'
        assert r['terminate_at_space_limits'] is False
        assert r['category'] == bank_cat[r['task_id']]
        m = r['trajectory_metrics']
        rows.append(dict(policy=pol, split='ext', task=r['task_id'], rep=int(r['repeat']), world=r['world_id'],
                         outcome=r['done_reason'], cat=CAT[r['category']], t=float(r['physical_time_s']),
                         mind=float(m['min_goal_distance_m']), path=float(m['path_length_m'])))
for r in csv.DictReader(open(os.path.join(G3, 'episodes.csv'))):
    if r['split'] != 'test12' or r['is_control'] == 'True' or r['protocol'] != 'E2':
        continue
    rows.append(dict(policy=r['strategy'], split='test12', task=r['task_id'], rep=int(r['repeat']), world=r['world_id'],
                     outcome=r['done_reason'], cat=CAT[r['category']], t=float(r['physical_time_s']),
                     mind=float(r['min_goal_distance_m']), path=float(r['path_length_m'])))
checks.append('category in ext records == bank category: all (assert passed)')
cnt = collections.Counter((r['policy'], r['split']) for r in rows)
checks.append('counts ' + str(sorted(cnt.items())))
keys = collections.defaultdict(set)
for r in rows: keys[(r['policy'], r['split'])].add((r['task'], r['rep']))
for s in ('ext', 'test12'):
    ks = [keys[(p, s)] for p in POL]
    checks.append(f'{s}: identical condition sets across 4 policies: {all(k == ks[0] for k in ks)} (n={len(ks[0])})')
tw = {r['world'] for r in rows if r['split'] == 'test12'}; ew = {r['world'] for r in rows if r['split'] == 'ext'}
checks.append(f'worlds test12={len(tw)} ext={len(ew)} overlap={len(tw & ew)}')

idx = {(r['policy'], r['split'], r['task'], r['rep']): r for r in rows}
SPLITS = {'ext': ('ext',), 'test12': ('test12',), 'merged': ('test12', 'ext')}

def boot(sel, stat):
    worlds = sorted({r['world'] for r in sel})
    if len(worlds) < 5: return None
    by = collections.defaultdict(list)
    for r in sel: by[r['world']].append(r)
    rng = random.Random(SEED); vals = []
    for _ in range(B):
        samp = [x for wv in (rng.choice(worlds) for _ in worlds) for x in by[wv]]
        vals.append(stat(samp))
    vals.sort(); return vals[int(.025 * B)], vals[int(.975 * B) - 1]
fmt = lambda ci: '' if ci is None else f'[{100*ci[0]:.1f}, {100*ci[1]:.1f}]'
arr = lambda s: sum(x['outcome'] == 'reached' for x in s) / len(s)

def sel(p, split, cat=None, drop=None):
    return [r for r in rows if r['policy'] == p and r['split'] in SPLITS[split]
            and (cat is None or r['cat'] == cat) and r['world'] != drop]
def pair(a, b, split, cat=None, drop=None):
    return [dict(world=r['world'], a=r['outcome'], b=idx[(b, r['split'], r['task'], r['rep'])]['outcome'])
            for r in sel(a, split, cat, drop)]
dstat = lambda s: (sum(x['a'] == 'reached' for x in s) - sum(x['b'] == 'reached' for x in s)) / len(s)

main = []
for split in ('ext', 'test12', 'merged'):
    for p in POL:
        rs = sel(p, split); c = collections.Counter(r['outcome'] for r in rs); n = len(rs)
        reached = [r for r in rs if r['outcome'] == 'reached']
        eff = sorted(D0[r['task']] / r['path'] for r in reached if r['path'] > 0)
        main.append(dict(split=split, policy=p, n=n, worlds=len({r['world'] for r in rs}), reached=c['reached'],
                         collision=c['collision'], time_limit=c['time_limit'], arrival_pct=f"{100*c['reached']/n:.1f}",
                         arrival_ci=fmt(boot(rs, arr)), path_eff_median=f'{eff[len(eff)//2]:.3f}' if eff else ''))

pairs = []
for split, drop in (('ext', None), ('test12', None), ('merged', None), ('merged', DUP_WORLD)):
    for a, b in (('P6', 'P0'), ('P2', 'P0'), ('P4', 'P2'), ('P6', 'P2'), ('P6', 'P4')):
        pr = pair(a, b, split, drop=drop); ci = boot(pr, dstat)
        g = sum(x['a'] == 'reached' and x['b'] != 'reached' for x in pr)
        l = sum(x['b'] == 'reached' and x['a'] != 'reached' for x in pr)
        pairs.append(dict(split=split + ('_dedup' if drop else ''), a=a, b=b, n=len(pr), worlds=len({x['world'] for x in pr}),
                          diff_reached=g - l, new=g, lost=l, diff_pct=f'{100*dstat(pr):.1f}', diff_ci=fmt(ci),
                          ci_lower_gt0='' if ci is None else str(ci[0] > 0)))

cls = []
for split in ('ext', 'merged'):
    for cat in ('Sparse', 'Moderate', 'Dense'):
        for p in POL:
            rs = sel(p, split, cat); c = collections.Counter(r['outcome'] for r in rs); nw = len({r['world'] for r in rs})
            effc = sorted(D0[r['task']] / r['path'] for r in rs if r['outcome'] == 'reached' and r['path'] > 0)
            cls.append(dict(split=split, category=cat, policy=p, n=len(rs), worlds=nw, reached=c['reached'],
                            collision=c['collision'], time_limit=c['time_limit'], arrival_pct=f"{100*c['reached']/len(rs):.1f}",
                            ci=fmt(boot(rs, arr)) if nw >= 5 else 'n/a', path_eff_median=f'{effc[len(effc)//2]:.3f}' if effc else ''))
        for a, b in (('P6', 'P0'), ('P6', 'P4'), ('P4', 'P0')):
            pr = pair(a, b, split, cat); nw = len({x['world'] for x in pr})
            cls.append(dict(split=split, category=cat, policy=f'{a}-{b}', n=len(pr), worlds=nw,
                            reached=sum(x['a'] == 'reached' for x in pr) - sum(x['b'] == 'reached' for x in pr),
                            collision='', time_limit='', arrival_pct=f'{100*dstat(pr):.1f}',
                            ci=fmt(boot(pr, dstat)) if nw >= 5 else 'n/a', path_eff_median=''))

trans = []
for split in ('ext', 'merged'):
    for a, b in (('P6', 'P0'), ('P6', 'P4')):
        m = collections.Counter((x['b'], x['a']) for x in pair(a, b, split))
        for (ob, oa), k in sorted(m.items()):
            trans.append(dict(split=split, from_policy=b, to_policy=a, from_outcome=ob, to_outcome=oa, count=k))

tout = []
for split in ('ext', 'test12'):
    for p in POL:
        ts = sorted(r['mind'] for r in sel(p, split) if r['outcome'] == 'time_limit')
        tout.append(dict(split=split, policy=p, timeouts=len(ts), near_lt2m=sum(x < 2 for x in ts),
                         near_lt1m=sum(x < 1 for x in ts), median_min_goal_dist=f'{ts[len(ts)//2]:.2f}' if ts else ''))

for name, tab in (('table_main', main), ('table_pairs', pairs), ('table_class', cls),
                  ('table_transitions', trans), ('table_timeouts', tout)):
    with open(os.path.join(OUT, name + '.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(tab[0].keys())); w.writeheader(); w.writerows(tab)
open(os.path.join(OUT, 'checks.txt'), 'w').write('\n'.join(checks) + '\n')
print('\n'.join(checks))
