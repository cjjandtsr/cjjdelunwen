"""Read-only: class composition (Sparse/Moderate/Dense) of the fixed-success reference bank tasks used by P6's keep term.
Run: python3 keep_bank_classes.py <code_repo_root>   (uses project geometry code; world geometry from worlds/train)"""
import json, sys, os, glob, collections
root = sys.argv[1]
sys.path.insert(0, os.path.join(root, 'Improved-3D-Diffusion-Policy'))
from scripts.routea_paired_support.task_geometry_metrics import compute
from scripts.analyze_routea_f5 import labels
from scripts.routea_paired_support.task_geometry_metrics import band_density
from diffusion_policy_3d.env.collision_geom import load_obstacles
from dataclasses import asdict
ref = os.path.join(root, 'jindu/routea_a2_selective_keep_run01/reference')
inv = json.load(open(os.path.join(ref, 'inventory.json')))['categories']
W = os.path.join(root, 'PX4-Autopilot-Tools/sitl_gazebo/worlds/train')
cnt = collections.Counter(); seen = {}
for f in glob.glob(os.path.join(ref, '*.jsonl')):
    first = json.loads(open(f).readline())['task']
    tid = first['task_id']
    if tid in seen: continue
    geo = [asdict(o) for o in load_obstacles(os.path.join(W, first['world_id'] + '.world.obstacles.json'))]
    p = first['payload']
    item = dict(task_id=tid, world=first['world_id'], role=p['role'], split='train', start=p['start_pos'], goal=p['goal_pos'], geometry=geo)
    r = compute(item); r['band_rho'] = band_density(item)
    seen[tid] = labels(r)['w1']
    cnt[(inv[tid], seen[tid])] += 1
print('tasks', len(seen)); print(sorted(cnt.items()))
eligible = {k: v for k, v in seen.items() if inv[k] != 'neither'}
print('eligible (>=1 success)', len(eligible), collections.Counter(eligible.values()))
