"""G3 #E2 analysis (read-only). Claude, 2026-11-03.

Inputs
  PKG : G3 data package dir (routea_paper_g3_e2_audit_20261103/) -> episodes.csv, banks/*.json
  F5  : project repo jindu/routea_f5_run01/results/ (P0 and P6@u256 dev420/val20 #E2 commits, frozen strata)
Run
  python3 -I g3_analysis.py <PKG> <F5> <OUT_DIR>
Outputs (CSV in OUT_DIR): episodes_all.csv, table_main.csv, table_pairs.csv, table_class.csv,
  table_transitions.csv, table_timeouts.csv, table_test12_dedup.csv, checks.txt
Statistics: world-cluster bootstrap, 20000 resamples, seed 2026102601; CI only when the cell has >=5 worlds.
"""
import csv, json, glob, os, sys, random, math, collections

PKG, F5, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
B, SEED = 20000, 2026102601
DUP_WORLD = 'routeA_rl_v1__yaw_lateral_recovery__rl_test__initial_yaw_offset_corridor__000015'
CAT = {'zero': 'Sparse', 'low': 'Moderate', 'high': 'Dense'}
checks = []

# ---------- load ----------
rows = []
for r in csv.DictReader(open(os.path.join(PKG, 'episodes.csv'))):
    if r['is_control'] == 'True':
        if r['strategy'] == 'P6' and r['split'] == 'val20':
            r = dict(r, source='G3_control')       # identical to the 10-31 reference (80/80, Codex)
        else:
            continue
    else:
        r = dict(r, source='G3')
    rows.append(dict(policy=r['strategy'], split=r['split'], task=r['task_id'], rep=int(r['repeat']),
                     world=r['world_id'], outcome=r['done_reason'], cat=CAT[r['category']],
                     t=float(r['physical_time_s']), mind=float(r['min_goal_distance_m']),
                     path=float(r['path_length_m']), source=r['source']))
strata = {}
for f in ('dev_strata.json', 'val_strata.json'):
    for t in json.load(open(os.path.join(F5, f)))['tasks']:
        strata[t['task_id']] = CAT[t['labels']['w1']]
for split, sub in (('dev420', 'eval_dev'), ('val20', 'eval_val')):
    for pol, d in (('P0', 'bc'), ('P6', 'P6')):
        if pol == 'P6' and split == 'val20':
            continue                                # taken from G3 control (same 80 outcomes)
        for f in glob.glob(os.path.join(F5, sub, 'full', d, 'commits', '*')):
            s = json.load(open(f))['summary']
            m = s['trajectory_metrics']
            rows.append(dict(policy=pol, split=split, task=s['task_id'], rep=int(s['repeat']), world=s['world_id'],
                             outcome=s['done_reason'], cat=strata[s['task_id']], t=float(s['physical_time_s']),
                             mind=float(m['min_goal_distance_m']), path=float(m['path_length_m']), source='F5'))
# start-goal distance from banks
D0 = {}
for f in glob.glob(os.path.join(PKG, 'banks', '*.json')):
    for t in json.load(open(f))['tasks']:
        p = t['payload']; D0[t['task_id']] = math.dist(p['start_pos'], p['goal_pos'])

# checks: counts, categories consistent between package and F5 strata
cnt = collections.Counter((r['policy'], r['split']) for r in rows)
checks.append('counts ' + str(sorted(cnt.items())))
pk_cat = {(r['task']): r['cat'] for r in rows if r['source'] == 'G3' and r['split'] in ('dev420', 'val20')}
mism = sum(1 for k, v in pk_cat.items() if strata.get(k) != v)
checks.append(f'category package vs frozen strata (dev/val): {len(pk_cat)} tasks, {mism} mismatches')
keys = collections.defaultdict(set)
for r in rows: keys[(r['policy'], r['split'])].add((r['task'], r['rep']))
for split in ('dev420', 'val20', 'test12'):
    ks = [keys[(p, split)] for p in ('P0', 'P2', 'P4', 'P6')]
    checks.append(f'{split}: identical condition sets across 4 policies: {all(k == ks[0] for k in ks)} (n={len(ks[0])})')

with open(os.path.join(OUT, 'episodes_all.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

POL = ('P0', 'P2', 'P4', 'P6')
idx = {(r['policy'], r['split'], r['task'], r['rep']): r for r in rows}

def boot_rate(sel_rows, stat):
    """world-cluster bootstrap of stat(list_of_rows); returns (lo, hi) or None if <5 worlds."""
    worlds = sorted({r['world'] for r in sel_rows})
    if len(worlds) < 5: return None
    by = collections.defaultdict(list)
    for r in sel_rows: by[r['world']].append(r)
    rng = random.Random(SEED); vals = []
    for _ in range(B):
        samp = [x for wv in (rng.choice(worlds) for _ in worlds) for x in by[wv]]
        vals.append(stat(samp))
    vals.sort(); return vals[int(.025 * B)], vals[int(.975 * B) - 1]

def fmt(ci, scale=100):
    return '' if ci is None else f'[{ci[0]*scale:.1f}, {ci[1]*scale:.1f}]'

# ---------- main table ----------
main = []
for split in ('dev420', 'val20', 'test12'):
    for p in POL:
        rs = [r for r in rows if r['policy'] == p and r['split'] == split]
        c = collections.Counter(r['outcome'] for r in rs); n = len(rs)
        ci = boot_rate(rs, lambda s: sum(x['outcome'] == 'reached' for x in s) / len(s))
        reached = [r for r in rs if r['outcome'] == 'reached']
        eff = [D0[r['task']] / r['path'] for r in reached if r['path'] > 0]
        tt = sorted(r['t'] for r in reached)
        main.append(dict(split=split, policy=p, n=n, worlds=len({r['world'] for r in rs}),
                         reached=c['reached'], collision=c['collision'], time_limit=c['time_limit'],
                         arrival_pct=f"{100*c['reached']/n:.1f}", arrival_ci=fmt(ci),
                         collision_pct=f"{100*c['collision']/n:.1f}", timeout_pct=f"{100*c['time_limit']/n:.1f}",
                         path_eff_median=f"{sorted(eff)[len(eff)//2]:.3f}" if eff else '',
                         time_reached_median_s=f"{tt[len(tt)//2]:.1f}" if tt else ''))

# ---------- paired differences ----------
PAIRS = (('P6', 'P0'), ('P2', 'P0'), ('P4', 'P2'), ('P6', 'P2'), ('P6', 'P4'))
pairs = []
def pair_rows(a, b, split, cat=None, drop_world=None):
    out = []
    for (p, s, t, rp), r in idx.items():
        if p != a or s != split: continue
        if cat and r['cat'] != cat: continue
        if drop_world and r['world'] == drop_world: continue
        o = idx[(b, s, t, rp)]
        out.append(dict(world=r['world'], a=r['outcome'], b=o['outcome']))
    return out
def dstat(s): return (sum(x['a'] == 'reached' for x in s) - sum(x['b'] == 'reached' for x in s)) / len(s)
for split in ('dev420', 'val20', 'test12'):
    for a, b in PAIRS:
        pr = pair_rows(a, b, split)
        gain = sum(x['a'] == 'reached' and x['b'] != 'reached' for x in pr)
        loss = sum(x['b'] == 'reached' and x['a'] != 'reached' for x in pr)
        ci = boot_rate(pr, dstat)
        pairs.append(dict(split=split, a=a, b=b, n=len(pr), diff_reached=gain - loss, new_arrivals=gain,
                          lost_arrivals=loss, diff_pct=f'{100*dstat(pr):.1f}', diff_ci=fmt(ci),
                          ci_excludes_0='' if ci is None else str(ci[0] > 0 or ci[1] < 0)))

# ---------- by class ----------
cls = []
for split in ('dev420', 'val20', 'test12'):
    for cat in ('Sparse', 'Moderate', 'Dense'):
        for p in POL:
            rs = [r for r in rows if r['policy'] == p and r['split'] == split and r['cat'] == cat]
            c = collections.Counter(r['outcome'] for r in rs); n = len(rs)
            nw = len({r['world'] for r in rs})
            ci = boot_rate(rs, lambda s: sum(x['outcome'] == 'reached' for x in s) / len(s))
            cls.append(dict(split=split, category=cat, policy=p, n=n, worlds=nw,
                            tasks=len({r['task'] for r in rs}), reached=c['reached'], collision=c['collision'],
                            time_limit=c['time_limit'], arrival_pct=f"{100*c['reached']/n:.1f}",
                            arrival_ci=fmt(ci) if nw >= 5 else 'n/a (<5 worlds: counts only)'))
        for a, b in (('P6', 'P0'), ('P6', 'P4')):
            pr = pair_rows(a, b, split, cat)
            ci = boot_rate(pr, dstat); nw = len({x['world'] for x in pr})
            cls.append(dict(split=split, category=cat, policy=f'{a}-{b}', n=len(pr), worlds=nw,
                            tasks='', reached=sum(x['a'] == 'reached' for x in pr) - sum(x['b'] == 'reached' for x in pr),
                            collision='', time_limit='', arrival_pct=f'{100*dstat(pr):.1f}',
                            arrival_ci=fmt(ci) if nw >= 5 else 'n/a (<5 worlds: counts only)'))

# ---------- transitions ----------
trans = []
for split in ('dev420', 'val20', 'test12'):
    for a, b in (('P6', 'P0'), ('P6', 'P4')):
        m = collections.Counter((x['b'], x['a']) for x in pair_rows(a, b, split))
        for (ob, oa), k in sorted(m.items()):
            trans.append(dict(split=split, from_policy=b, to_policy=a, from_outcome=ob, to_outcome=oa, count=k))

# ---------- timeouts ----------
tout = []
for split in ('dev420', 'val20', 'test12'):
    for p in POL:
        ts = sorted(r['mind'] for r in rows if r['policy'] == p and r['split'] == split and r['outcome'] == 'time_limit')
        tout.append(dict(split=split, policy=p, timeouts=len(ts),
                         near_lt2m=sum(x < 2 for x in ts), near_lt1m=sum(x < 1 for x in ts),
                         median_min_goal_dist=f'{ts[len(ts)//2]:.2f}' if ts else ''))

# ---------- test12 without the geometry-duplicate world ----------
dd = []
for p in POL:
    rs = [r for r in rows if r['policy'] == p and r['split'] == 'test12' and r['world'] != DUP_WORLD]
    c = collections.Counter(r['outcome'] for r in rs)
    dd.append(dict(policy=p, n=len(rs), worlds=len({r['world'] for r in rs}), reached=c['reached'],
                   collision=c['collision'], time_limit=c['time_limit']))
for a, b in (('P6', 'P0'), ('P6', 'P4')):
    pr = pair_rows(a, b, 'test12', drop_world=DUP_WORLD); ci = boot_rate(pr, dstat)
    dd.append(dict(policy=f'{a}-{b}', n=len(pr), worlds=len({x['world'] for x in pr}),
                   reached=f'{100*dstat(pr):.1f}% {fmt(ci)}', collision='', time_limit=''))

for name, tab in (('table_main', main), ('table_pairs', pairs), ('table_class', cls),
                  ('table_transitions', trans), ('table_timeouts', tout), ('table_test12_dedup', dd)):
    with open(os.path.join(OUT, name + '.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(tab[0].keys())); w.writeheader(); w.writerows(tab)
open(os.path.join(OUT, 'checks.txt'), 'w').write('\n'.join(checks) + '\n')
print('\n'.join(checks))
