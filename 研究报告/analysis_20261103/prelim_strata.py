"""Preliminary #E2 stratification (read-only). Usage: python3 -I prelim_strata.py <jindu_root>"""
import json, glob, sys, os, collections
root = sys.argv[1]
def load(d):
    out = {}
    for f in glob.glob(os.path.join(d, 'commits', '*')):
        s = json.load(open(f))['summary']
        if s.get('status') != 'valid': continue
        out[(s['task_id'], s['repeat'])] = s
    return out
for split, sfile, dirs in [
    ('dev420', 'dev_strata.json', {'P0': 'routea_f5_run01/results/eval_dev/full/bc', 'P6': 'routea_f5_run01/results/eval_dev/full/P6'}),
    ('val20', 'val_strata.json', {'P0': 'routea_f5_run01/results/eval_val/full/bc', 'P6': 'routea_f5_run01/results/eval_val/full/P6'})]:
    strata = {t['task_id']: t for t in json.load(open(os.path.join(root, 'routea_f5_run01/results', sfile)))['tasks']}
    data = {k: load(os.path.join(root, v)) for k, v in dirs.items()}
    print('==', split, {k: len(v) for k, v in data.items()})
    for dim, fn in [('w1', lambda t: t['labels']['w1']), ('blocked', lambda t: t['blocked']), ('detour', lambda t: t['labels']['detour'])]:
        tab = collections.defaultdict(lambda: collections.Counter())
        for pol, d in data.items():
            for (tid, r), s in d.items():
                g = fn(strata[tid]); tab[(g, pol)][s['done_reason'] if s['done_reason'] in ('reached','collision','time_limit') else 'collision'] += 1
        groups = sorted({g for g, _ in tab}, key=str)
        for g in groups:
            row = []
            for pol in data:
                c = tab[(g, pol)]; n = sum(c.values())
                row.append(f"{pol} {c['reached']}/{c['collision']}/{c['time_limit']} (n={n}, SA={c['reached']/n:.3f})")
            print(f"  {dim}={g}: " + ' | '.join(row))
    # failure split of timeouts
    for pol, d in data.items():
        near = sum(1 for s in d.values() if s['done_reason']=='time_limit' and s['trajectory_metrics']['min_goal_distance_m'] < 2.0)
        tl = sum(1 for s in d.values() if s['done_reason']=='time_limit')
        print(f"  {pol} timeouts {tl}, of which min goal dist <2 m: {near}")
    # paired transitions
    m = collections.Counter()
    for k in data['P0']:
        if k in data['P6']: m[(data['P0'][k]['done_reason'], data['P6'][k]['done_reason'])] += 1
    print('  paired P0->P6:', dict(m))
