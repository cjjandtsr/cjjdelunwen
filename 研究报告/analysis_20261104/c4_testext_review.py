"""C4 复核：训练外扩展集（rl_test_ext）的隔离、准入与分类独立复算。只读，不改任何项目文件。
运行：python3 -I c4_testext_review.py <code_repo_root> <bank.json> <test12_bank.json> <val_bank.json> <out.json> [--expect 60,300,20]
  code_repo_root：项目仓库根（含 Improved-3D-Diffusion-Policy/ 与 PX4-Autopilot-Tools/）。
预期输出（扩展集）：ALL_PASS；分类计数 zero 20 / low 20 / high 20。
自检（不带 --expect，用 test12 bank 作 bank）：分类计数 zero 39 / low 5 / high 4，与 2026-11-03 重算一致。
分类界限复制自 scripts/analyze_routea_f5.py::labels（dev420 冻结）；几何量用项目自带 task_geometry_metrics。"""
import json, sys, os, glob, collections, math
root, bank_path, t12_path, val_path, out = sys.argv[1:6]
expect = tuple(int(x) for x in sys.argv[sys.argv.index('--expect') + 1].split(',')) if '--expect' in sys.argv else None
code = os.path.join(root, 'Improved-3D-Diffusion-Policy')
sys.path.insert(0, code); sys.path.insert(0, os.path.join(code, 'scripts'))
from scripts.routea_paired_support.task_geometry_metrics import compute, band_density
from scripts.routea_paired_support.core import canonical_hash
from scripts.analyze_routea_f5 import labels
try:
    import gymnasium  # noqa: F401  WSL 环境中存在；仅当缺失时用最小替身，准入判定只用到 _candidate_rejection_reasons
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

bank = json.load(open(bank_path)); t12 = json.load(open(t12_path)); val = json.load(open(val_path))
fails, notes = [], []
def check(ok, msg):
    (notes if ok else fails).append(('PASS ' if ok else 'FAIL ') + msg)

# 1 计数与 hash
n = (len(bank['tasks']), len(bank['episodes']), len(bank['worlds']))
if expect: check(n == expect, f'计数 tasks/episodes/worlds = {n}，期望 {expect}')
check(canonical_hash({k: v for k, v in bank.items() if k != 'content_hash'}) == bank['content_hash'],
      f"content_hash 重算一致 {bank['content_hash'][:12]}…")
if expect: check(bank['split'] == 'rl_test_ext' and bank['repeats'] == 5, f"split={bank['split']} repeats={bank['repeats']}")
per_task = collections.Counter(e.get('task_id') for e in bank['episodes'])
check(set(per_task.values()) == {bank['repeats']} and set(per_task) == {t['task_id'] for t in bank['tasks']},
      f'每任务回合数 {sorted(set(per_task.values()))}，episode 与 task 一一对应')

# 2 隔离：世界来自 test/，不在 test12 与 val bank 中；与 train/val 世界障碍集 Jaccard < 0.5；内嵌几何与仓库文件一致
W = os.path.join(root, 'PX4-Autopilot-Tools/sitl_gazebo/worlds')
KEYS = ('x', 'y', 'z', 'radius', 'height', 'size_x', 'size_y', 'size_z', 'yaw')
canon = lambda obs: frozenset(tuple([o['shape']] + [round(float(o.get(k, 0.0) or 0.0), 2) for k in KEYS]) for o in obs)
nm = lambda f: os.path.basename(f).replace('.world.obstacles.json', '')
ref = {(s, nm(f)): canon(json.load(open(f))['obstacles']) for s in ('train', 'val') for f in glob.glob(os.path.join(W, s, '*.obstacles.json'))}
test_files = {nm(f): f for f in glob.glob(os.path.join(W, 'test', '*.obstacles.json'))}
world_rows = []
for w, info in sorted(bank['worlds'].items()):
    a = canon(info['geometry'])
    in_test = w in test_files
    same_file = in_test and a == canon(json.load(open(test_files[w]))['obstacles'])
    j, k = max((len(a & b) / len(a | b), k) for k, b in ref.items())
    ok = in_test and same_file and w not in t12['worlds'] and w not in val['worlds'] and j < 0.5
    world_rows.append(dict(world=w, n_obstacles=len(a), in_test_dir=in_test, geometry_equals_repo=same_file,
                           in_test12=w in t12['worlds'], in_val20=w in val['worlds'], max_jaccard=round(j, 3), nearest=list(k)))
    check(ok, f'隔离 {w.split("__", 1)[1]}：test/={in_test} 几何一致={same_file} maxJ={j:.3f}（{k[0]}/{k[1].split("__")[-1]}）')

# 3 每任务：采样范围、准入（ROLE_CL）、类别独立复算
FIELDS = RTB.FIELDS
rows = []
for t in bank['tasks']:
    p, w = t['payload'], t['world_id']
    s, g = p['start_pos'], p['goal_pos']
    geo = bank['worlds'][w]['geometry']
    obs = [ObstacleSpec(**{k: o[k] for k in FIELDS}) for o in geo]
    zr_ok = list(p['z_range']) == [1.0, 5.0]   # dev420/val20/test12 三个 bank 的环境高度界限均为 [1.0, 5.0]
    bearing = math.atan2(g[1] - s[1], g[0] - s[0]); dyaw = (p['start_yaw'] - bearing + math.pi) % (2 * math.pi) - math.pi
    yaw_ok = abs(dyaw) <= 0.3 + 1e-9
    rng_ok = all(-14 <= v <= 14 for v in (s[0], s[1], g[0], g[1])) and 1.3 <= s[2] <= 4.7 and 1.5 <= g[2] <= 4.5
    dist_ok = math.dist(s, g) > 0.5
    adm = RTB.admit(s, g, obs, t['role'])
    item = dict(task_id=t['task_id'], world=w, role=t['role'], split=bank['split'], start=s, goal=g, geometry=geo)
    r = compute(item); r['band_rho'] = band_density(item); r.pop('path', None); lab = labels(r)
    declared = t.get('category')
    rows.append(dict(task_id=t['task_id'], world=w, role=t['role'], rho_1=r['rho_1.0'], rho_2=r['rho_2.0'], w1=lab['w1'], declared=declared,
                     z_range=p['z_range'], yaw_ok=yaw_ok, start=s, goal=g,
                     range_ok=rng_ok, dist_ok=dist_ok, admitted=adm))
    if expect:
        check(rng_ok and dist_ok and adm and yaw_ok, f"任务 {t['task_id'][:10]} 范围={rng_ok} 距离={dist_ok} 准入={adm} 偏航={yaw_ok}")
        check(zr_ok, f"任务 {t['task_id'][:10]} 环境高度界限 z_range={p['z_range']}，应与其余三集相同 [1.0, 5.0]")
        if declared is not None: check(declared == lab['w1'], f"任务 {t['task_id'][:10]} 声明类别 {declared} = 复算 {lab['w1']}")

if '--review-input' in sys.argv:
    ri = json.load(open(sys.argv[sys.argv.index('--review-input') + 1]))
    check(ri['candidate_content_hash'] == bank.get('candidate_content_hash'), f"候选 content_hash 与 bank 一致 {ri['candidate_content_hash'][:12]}…")
    key = lambda w, a, b: (w, tuple(round(v, 9) for v in a), tuple(round(v, 9) for v in b))
    sel = {key(x['world'], x['start'], x['goal']): x for x in ri['selected']}
    check(len(sel) == len(ri['selected']) == len(rows), f"抽取清单 {len(ri['selected'])} 条与 bank 任务一一对应")
    for r in rows:
        x = sel.get(key(r['world'], r['start'], r['goal']))
        check(x is not None and x['category'] == r['w1'] and abs(x['rho_1_0'] - r['rho_1']) < 1e-9 and abs(x['rho_2_0'] - r['rho_2']) < 1e-9 and x['role'] == r['role'],
              f"任务 {r['task_id'][:10]} 抽取清单类别/ρ 与复算一致")
    seeds = collections.defaultdict(set)
    for x in ri['selected']: seeds[x['world']].add(x['sampling_seed'])
    check(all(len(v) == 1 for v in seeds.values()) and len({next(iter(v)) for v in seeds.values()}) == len(seeds),
          f"每世界一个采样种子且互不相同：{sorted(next(iter(v)) - 20261103 for v in seeds.values())}")
cnt = collections.Counter(r['w1'] for r in rows)
if expect: check(cnt == collections.Counter(zero=20, low=20, high=20), f'分类计数 {dict(cnt)}，期望 20/20/20')
pw = collections.Counter((r['world'], r['w1']) for r in rows); pt = collections.Counter(r['world'] for r in rows)
if expect:
    check(max(pw.values()) <= 2, f'每世界每类至多 2 个：实际最大 {max(pw.values())}')
    check(max(pt.values()) <= 4, f'每世界至多 4 个：实际最大 {max(pt.values())}')
roles = collections.Counter(r['role'] for r in rows)
json.dump(dict(schema='c4_testext_review_v1_claude', bank_hash=bank['content_hash'], counts=dict(cnt), roles=dict(roles),
               per_world_total=dict(pt), worlds=world_rows, tasks=rows, fails=fails),
          open(out, 'w'), indent=1, ensure_ascii=False, default=float)
for x in notes[:3] + fails: print(x)
print('PASS 项数', len(notes), '；FAIL 项数', len(fails))
print('分类计数', dict(cnt), '角色', dict(roles), '世界', len(pt))
print('ALL_PASS' if not fails else f'FAILED {len(fails)}')
