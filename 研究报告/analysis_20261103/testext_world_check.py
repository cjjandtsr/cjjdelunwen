"""Read-only: for test worlds NOT in test12, max obstacle-set Jaccard vs any train/val world, floating boxes.
Run: python3 -I testext_world_check.py <code_repo_root> <test12_bank.json>"""
import json, sys, glob, os
root, bank_path = sys.argv[1:3]
W = os.path.join(root, 'PX4-Autopilot-Tools/sitl_gazebo/worlds')
def canon(p):
    rows = []
    for o in json.load(open(p))['obstacles']:
        rows.append(tuple([o['shape']] + [round(float(o.get(k, 0.0)), 2) for k in
                     ('x', 'y', 'z', 'radius', 'height', 'size_x', 'size_y', 'size_z', 'yaw')]))
    return frozenset(rows)
name = lambda f: os.path.basename(f).replace('.world.obstacles.json', '')
ref = {(s, name(f)): canon(f) for s in ('train', 'val') for f in glob.glob(os.path.join(W, s, '*.obstacles.json'))}
used = set(json.load(open(bank_path))['worlds'])
rows = []
for f in sorted(glob.glob(os.path.join(W, 'test', '*.obstacles.json'))):
    w = name(f)
    if w in used: continue
    a = canon(f)
    j, k = max((len(a & b) / len(a | b), k) for k, b in ref.items())
    fl = sum(o['shape'] == 'box' and o['z'] - o['size_z'] / 2 > 0.05 for o in json.load(open(f))['obstacles'])
    rows.append((w, len(a), j, k, fl))
for r in rows: print(f"{r[0].split('__',1)[1]}: n={r[1]} maxJ={r[2]:.3f} ({r[3][0]}/{r[3][1].split('__')[-1]}) floating={r[4]}")
print('total', len(rows), 'maxJ>=0.5:', sum(r[2] >= .5 for r in rows), 'floating>0:', sum(r[4] > 0 for r in rows))
