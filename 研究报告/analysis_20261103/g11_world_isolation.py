"""G11 (read-only): test-world geometry isolation vs train/val worlds, and floating-box enumeration.
Run: python3 -I g11_world_isolation.py <code_repo_root> <test12_bank.json>
Inputs: PX4-Autopilot-Tools/sitl_gazebo/worlds/{train,val,test}/*.obstacles.json ; test12 bank (for the 12 evaluated worlds)."""
import json, sys, glob, os, hashlib, collections
root, bank_path = sys.argv[1], sys.argv[2]
W = os.path.join(root, 'PX4-Autopilot-Tools/sitl_gazebo/worlds')
def obs_list(path):
    d = json.load(open(path))
    items = d['obstacles'] if isinstance(d, dict) and 'obstacles' in d else d
    return items
def canon(items, nd=2):
    rows = []
    for o in items:
        rows.append(tuple([o.get('shape', o.get('type'))] + [round(float(o.get(k, 0.0)), nd) for k in
                     ('x', 'y', 'z', 'radius', 'height', 'size_x', 'size_y', 'size_z', 'yaw')]))
    return tuple(sorted(rows))
worlds = {}
for split in ('train', 'val', 'test'):
    for f in sorted(glob.glob(os.path.join(W, split, '*.obstacles.json'))):
        worlds[(split, os.path.basename(f).replace('.world.obstacles.json', '').replace('.obstacles.json', ''))] = obs_list(f)
print({s: sum(k[0] == s for k in worlds) for s in ('train', 'val', 'test')})
bank = json.load(open(bank_path))
test12 = sorted(bank['worlds'])
# 1) exact / rounded geometry duplicates
by_hash = collections.defaultdict(list)
for k, v in worlds.items():
    by_hash[hashlib.sha256(repr(canon(v)).encode()).hexdigest()].append(k)
for w in test12:
    h = hashlib.sha256(repr(canon(worlds[('test', w)])).encode()).hexdigest()
    others = [k for k in by_hash[h] if k[0] != 'test']
    # 2) max obstacle-set overlap with any train/val world
    a = set(canon(worlds[('test', w)]))
    best = max(((len(a & set(canon(v))) / max(1, len(a | set(canon(v)))), k) for k, v in worlds.items() if k[0] != 'test'))
    print(f"{w}: n={len(a)} exact_dup={others} max_jaccard={best[0]:.3f} with {best[1][0]}/{best[1][1]}")
# 3) floating boxes (bottom above ground by >0.05 m)
def floating(items):
    n = 0
    for o in items:
        if o.get('shape', o.get('type')) == 'box':
            bottom = float(o['z']) - float(o['size_z']) / 2
            n += bottom > 0.05
    return n
for split in ('train', 'val', 'test'):
    c = [(k[1], floating(v)) for k, v in worlds.items() if k[0] == split]
    print(split, 'worlds with floating boxes:', sum(n > 0 for _, n in c), '/', len(c), 'boxes:', sum(n for _, n in c))
print('test12 evaluated worlds with floating boxes:', [(w, floating(worlds[('test', w)])) for w in test12 if floating(worlds[('test', w)])])
