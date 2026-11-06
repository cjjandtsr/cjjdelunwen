"""Run: python3 strata_recompute.py <code_repo_root> <bank.json> <split> <out.json> [--check <frozen.json>]. Expected: dev420 check 0 mismatches; test12 counts zero 39, low 5, high 4.
Compute frozen difficulty strata for a fixed bank using the project's own geometry code (read-only).
Usage: python3 strata_test12.py <code_repo_root> <bank.json> <split_label> <out.json> [--check <frozen_strata.json>]
Thresholds are copied from scripts/analyze_routea_f5.py::labels (frozen on dev420)."""
import json, sys, os
repo, bank_path, split, out = sys.argv[1:5]
sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from scripts.routea_paired_support.task_geometry_metrics import compute, band_density
from scripts.analyze_routea_f5 import labels
bank = json.load(open(bank_path))
rows = []
for t in bank['tasks']:
    p = t['payload']
    item = dict(task_id=t['task_id'], world=t['world_id'], role=t['role'], split=split,
                start=p['start_pos'], goal=p['goal_pos'], geometry=bank['worlds'][t['world_id']]['geometry'])
    r = compute(item); r['band_rho'] = band_density(item); r.pop('path', None); r['labels'] = labels(r)
    rows.append(r)
json.dump(dict(schema='routea_f5_strata_v1_claude_recompute', split=split, bank_hash=bank['content_hash'], tasks=rows),
          open(out, 'w'), indent=1, default=float)
if '--check' in sys.argv:
    ref = {x['task_id']: x for x in json.load(open(sys.argv[sys.argv.index('--check') + 1]))['tasks']}
    bad = [r['task_id'] for r in rows if r['labels'] != ref[r['task_id']]['labels'] or abs(r['rho_1.0'] - ref[r['task_id']]['rho_1.0']) > 1e-9]
    print('check vs frozen:', len(rows), 'tasks,', len(bad), 'mismatches')
import collections
print(split, dict(collections.Counter((r['labels']['w1'], r['blocked']) for r in rows)))
