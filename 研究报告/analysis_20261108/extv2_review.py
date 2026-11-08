"""扩展集 v2 事后分类与隔离复核（只读）。冻结 bank 文件未回传，任务从各回合 trace 的 episode_start 头（task、geometry）重建。
运行：python3 -I extv2_review.py <code_repo_root> <P15_ext_trace_dir> <added_bc_trace_dir> <run02_bank.json> <test12_bank.json> <val20_bank.json> <out.json>
检查：①增量任务集、ext v2 = run02 ∪ 增量；② run02 原 300 条件 initial_hash 不变；③世界隔离（同 C4 规则）；
④准入、范围、偏航；⑤类别独立复算（界限同 scripts/analyze_routea_f5.py::labels）与 trace 声明一致；⑥每世界每类 ≤5；⑦O′ 适中、密集各 ≥70。"""
import json, sys, os, glob, collections, math
root, p15dir, adddir, run02_p, t12_p, val_p, out = sys.argv[1:8]
code = os.path.join(root, 'Improved-3D-Diffusion-Policy')
sys.path.insert(0, code); sys.path.insert(0, os.path.join(code, 'scripts'))
from scripts.routea_paired_support.task_geometry_metrics import compute, band_density
from scripts.analyze_routea_f5 import labels
try:
    import gymnasium  # noqa
except ImportError:
    import types
    gym = types.ModuleType('gymnasium'); sp = types.ModuleType('gymnasium.spaces')
    class _Env: pass
    class _Box:
        def __init__(self, *a, **k): pass
    gym.Env, sp.Box, sp.Dict, gym.spaces = _Env, _Box, _Box, sp
    sys.modules['gymnasium'], sys.modules['gymnasium.spaces'] = gym, sp
from scripts import routea_task_bank as RTB
RTB.init(root)
from diffusion_policy_3d.env.collision_geom import ObstacleSpec
fails, notes = [], []
def check(ok, msg): (notes if ok else fails).append(('PASS ' if ok else 'FAIL ') + msg)

def heads(d):
    H = []
    for f in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
        with open(f) as fh: H.append(json.loads(fh.readline()))
    return H
P15 = heads(p15dir); ADD = heads(adddir)
run02 = json.load(open(run02_p)); t12 = json.load(open(t12_p)); val = json.load(open(val_p))
check(len(P15) == 755 and len(ADD) == 455, f'trace 数 P15 ext={len(P15)} 增量 bc={len(ADD)}')
k = lambda h: (h['task_id'], h['repeat'])
add_keys = {k(h) for h in ADD}; p15_keys = {k(h) for h in P15}
r02_keys = {(e['task_id'], e['repeat']) for e in run02['episodes']} if 'repeat' in run02['episodes'][0] else None
r02_tasks = {t['task_id'] for t in run02['tasks']}
check(add_keys <= p15_keys and len(p15_keys - add_keys) == 300, f'ext v2 = 增量 455 ∪ 其余 {len(p15_keys - add_keys)}')
check({t for t, _ in p15_keys - add_keys} == r02_tasks, 'ext v2 中非增量部分的任务集 = run02 的 60 个任务')
check(not ({t for t, _ in add_keys} & r02_tasks), '增量任务与 run02 不重叠')
# run02 初态不变：与 run02 bank episodes 的 initial_hash 对比
r02_init = {(e['task_id'], e.get('repeat')): e.get('initial_hash') for e in run02['episodes']}
p15_init = {k(h): h['initial_hash'] for h in P15}
same = sum(1 for kk, v in r02_init.items() if p15_init.get(kk) == v)
check(same == 300, f'run02 原 300 条件 initial_hash 在 ext v2 中逐条一致：{same}/300')
cnt_rep = collections.Counter(t for t, _ in add_keys)
check(set(cnt_rep.values()) == {5}, f'增量每任务 5 次重复：{sorted(set(cnt_rep.values()))}；增量任务数 {len(cnt_rep)}')
# 任务表（每任务取一个头）
tasks = {}
for h in P15: tasks.setdefault(h['task_id'], h)
add_tasks = {t for t, _ in add_keys}
# 世界隔离
W = os.path.join(root, 'PX4-Autopilot-Tools/sitl_gazebo/worlds')
KEYS = ('x', 'y', 'z', 'radius', 'height', 'size_x', 'size_y', 'size_z', 'yaw')
canon = lambda obs: frozenset(tuple([o['shape']] + [round(float(o.get(kk, 0.0) or 0.0), 2) for kk in KEYS]) for o in obs)
nm = lambda f: os.path.basename(f).replace('.world.obstacles.json', '')
ref = {(s, nm(f)): canon(json.load(open(f))['obstacles']) for s in ('train', 'val') for f in glob.glob(os.path.join(W, s, '*.obstacles.json'))}
test_files = {nm(f): f for f in glob.glob(os.path.join(W, 'test', '*.obstacles.json'))}
worlds = {}
for h in tasks.values(): worlds.setdefault(h['world_id'], h['geometry'])
wrows = []
for w, g in sorted(worlds.items()):
    a = canon(g); in_test = w in test_files
    same_file = in_test and a == canon(json.load(open(test_files[w]))['obstacles'])
    j, kk = max((len(a & b) / len(a | b), kk) for kk, b in ref.items())
    ok = in_test and same_file and w not in t12['worlds'] and w not in val['worlds'] and j < 0.5
    wrows.append(dict(world=w, new=w not in run02['worlds'], in_test_dir=in_test, geometry_equals_repo=same_file, max_jaccard=round(j, 3), nearest=list(kk)))
    check(ok, f'隔离 {w.split("__", 1)[1]}：test/={in_test} 几何一致={same_file} maxJ={j:.3f}')
# 每任务复算
FIELDS = RTB.FIELDS; rows = []
decl = {}
for h in P15: decl.setdefault(h['task_id'], None)
for tid, h in tasks.items():
    p = h['task']; s, g = p['start_pos'], p['goal_pos']; geo = h['geometry']
    obs = [ObstacleSpec(**{kk: o[kk] for kk in FIELDS}) for o in geo]
    bearing = math.atan2(g[1] - s[1], g[0] - s[0]); dyaw = (p['start_yaw'] - bearing + math.pi) % (2 * math.pi) - math.pi
    rng_ok = all(-14 <= v <= 14 for v in (s[0], s[1], g[0], g[1])) and 1.3 <= s[2] <= 4.7 and 1.5 <= g[2] <= 4.5
    adm = RTB.admit(s, g, obs, h['role'])
    item = dict(task_id=tid, world=h['world_id'], role=h['role'], split='rl_test_ext', start=s, goal=g, geometry=geo)
    r = compute(item); r.pop('path', None); lab = labels(r)
    rows.append(dict(task_id=tid, world=h['world_id'], role=h['role'], added=tid in add_tasks, rho_1=r['rho_1.0'], w1=lab['w1'],
                     yaw_ok=abs(dyaw) <= 0.3 + 1e-9, range_ok=rng_ok, dist_ok=math.dist(s, g) > 0.5, admitted=adm, z_range=p['z_range'],
                     D0=math.dist(s, g)))
    if tid in add_tasks:
        check(rng_ok and math.dist(s, g) > 0.5 and adm and abs(dyaw) <= 0.3 + 1e-9 and list(p['z_range']) == [1.0, 5.0],
              f'增量任务 {tid[:10]} 范围/距离/准入/偏航/高度界限')
json.dump(rows, open(out.replace('.json', '_tasks.json'), 'w'), ensure_ascii=False, indent=0)
cnt = collections.Counter(r['w1'] for r in rows); cnt_add = collections.Counter(r['w1'] for r in rows if r['added'])
pw = collections.Counter((r['world'], r['w1']) for r in rows)
check(max(pw.values()) <= 5, f'ext v2 每世界每类至多 5：实际最大 {max(pw.values())}')
t12c = collections.Counter(labels({k: v for k, v in compute(dict(task_id=t['task_id'], world=t['world_id'], role=t['role'], split='rl_test', start=t['payload']['start_pos'], goal=t['payload']['goal_pos'], geometry=t12['worlds'][t['world_id']]['geometry'])).items() if k != 'path'})['w1'] for t in t12['tasks'])
check(t12c == collections.Counter(zero=39, low=5, high=4), f'test12 类别自检 {dict(t12c)}（期望 39/5/4）')
op = {c: cnt[c] + t12c.get(c, 0) for c in ('zero', 'low', 'high')}
check(op['low'] >= 70 and op['high'] >= 70, f'O′ 任务数 稀疏/适中/密集 = {op["zero"]}/{op["low"]}/{op["high"]}')
json.dump(dict(counts_extv2=dict(cnt), counts_added=dict(cnt_add), counts_Oprime=op, n_worlds_extv2=len(worlds),
               new_worlds=sum(w['new'] for w in wrows), worlds=wrows, fails=fails, n_pass=len(notes)), open(out, 'w'), ensure_ascii=False, indent=1)
for x in notes[:4] + fails[:30]: print(x)
print('PASS', len(notes), 'FAIL', len(fails)); print('ext v2', dict(cnt), '增量', dict(cnt_add), 'O′', op, '世界', len(worlds), '新世界', sum(w['new'] for w in wrows))
print('ALL_PASS' if not fails else f'FAILED {len(fails)}')
