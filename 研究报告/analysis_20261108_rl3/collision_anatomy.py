"""Collision anatomy under the 1 m primary endpoint (dev420 #E2 traces; diagnosis for the next RL plan).
Usage: python3 -I collision_anatomy.py <project-repo-root> <traces-root> <out.json> bc P6 P9
traces-root = <project-repo>/jindu/routea_f5_run01/results/eval_dev/full ; each policy dir has traces/*.jsonl"""
import json, sys, os, ast, math, collections
repo, root, out = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from diffusion_policy_3d.env.collision_geom import segment_obstacle_collision, compute_obstacle_clearance, ObstacleSpec
TH = 0.1 + 2e-3                                   # physical threshold 0.1 m; +2 mm because executed paths stop at contact
def poly_hit(P, obs):
    for a, b in zip(P[:-1], P[1:]):
        h = segment_obstacle_collision(a, b, obs, TH)
        if h is not None: return h[1]
    return None
res = {}
for pol in sys.argv[4:]:
    d = os.path.join(root, pol, 'traces'); rows = []
    for f in sorted(os.listdir(d)):
        L = [json.loads(l) for l in open(os.path.join(d, f))]
        s, e = L[0], L[-1]
        task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task'])
        g, s0 = task['goal_pos'], task['start_pos']; D0 = math.dist(g, s0)
        obs = [ObstacleSpec.from_dict(o) for o in s['geometry']]; byname = {o['name']: o for o in s['geometry']}
        T = [t for t in L[1:] if t.get('type') == 'transition']
        pts = [q for t in T for q in t['executed_path']]
        mind = min(math.dist(q, g) for q in pts)
        clear = [compute_obstacle_clearance(*q[:3], obs)[0] for q in pts[::2]]
        r = dict(task=s['task_id'], rep=s['repeat'], role=s['role'], out=e['done_reason'], n=len(T),
                 succ1m=mind < 1.0, goal_z=g[2], start_z=s0[2], D0=D0, min_clear=min(clear))
        if e['done_reason'] == 'collision' and not r['succ1m']:
            k = len(T) - 1; last = T[-1]['executed_path']; p = last[-1]
            name = poly_hit(last, obs)
            if name is None: kind, top = ('ground' if p[2] < 0.3 else 'unresolved'), None
            else:
                o = byname[name]; top = o['z'] + o['height'] / 2 if o['shape'] == 'cylinder' else o['z'] + o.get('size_z', 0) / 2
                kind = 'top' if p[2] > top - 0.3 else 'side'
            lead = 0                                # consecutive decisions before k whose 8-step plan already crosses the hit obstacle
            for j in range(k - 1, -1, -1):
                h = poly_hit(T[j]['planned_policy_path'], obs)
                if h is not None and (name is None or h == name): lead += 1
                else: break
            dens = sum(1 for o in obs if compute_obstacle_clearance(*p[:3], [o])[0] < 2.0)
            r.update(kind=kind, obstacle_shape=byname[name]['shape'] if name else None, k=k, lead=lead,
                     d_goal=math.dist(p, g), progress=1 - math.dist(p, g) / D0, local_density_2m=dens,
                     z_at_hit=p[2], obstacle_top=top)
        rows.append(r)
    res[pol] = rows
json.dump(res, open(out, 'w'))
def pct(a, b): return '%d/%d (%.0f%%)' % (a, b, 100 * a / b) if b else '0/0'
for pol, R in res.items():
    C = [r for r in R if r['out'] == 'collision' and not r['succ1m']]
    print('==', pol, '| 1 m success', pct(sum(r['succ1m'] for r in R), len(R)), '| collision failures', len(C),
          '| timeout failures', sum(1 for r in R if r['out'] == 'time_limit' and not r['succ1m']))
    print('  hit kind', dict(collections.Counter(r['kind'] for r in C)), '| obstacle shape', dict(collections.Counter(r['obstacle_shape'] for r in C)))
    ks = sorted(r['k'] for r in C); print('  collision decision k: median %d, k<=2: %s, k<=5: %s' % (ks[len(ks) // 2], pct(sum(x <= 2 for x in ks), len(ks)), pct(sum(x <= 5 for x in ks), len(ks))))
    L_ = collections.Counter(min(r['lead'], 4) for r in C)
    print('  plan already crosses the hit obstacle for >=1 / >=2 / >=3 decisions before impact: %s / %s / %s; lead dist %s' % (
        pct(sum(r['lead'] >= 1 for r in C), len(C)), pct(sum(r['lead'] >= 2 for r in C), len(C)), pct(sum(r['lead'] >= 3 for r in C), len(C)), dict(sorted(L_.items()))))
    pr = sorted(r['progress'] for r in C); dg = sorted(r['d_goal'] for r in C)
    print('  progress at impact: median %.2f, p25 %.2f, p75 %.2f | distance to goal median %.1f m' % (pr[len(pr) // 2], pr[len(pr) // 4], pr[3 * len(pr) // 4], dg[len(dg) // 2]))
    dn = collections.Counter(min(r['local_density_2m'], 4) for r in C); print('  obstacles within 2 m of impact (4=4+):', dict(sorted(dn.items())))
    print('  by role:', {ro: '%s coll' % pct(sum(1 for r in R if r['role'] == ro and r in C), sum(1 for r in R if r['role'] == ro)) for ro in sorted(set(r['role'] for r in R))})
    near = [r for r in R if r['min_clear'] < 0.3]
    print('  close calls (min clearance < 0.3 m): %d episodes, of which 1 m success %s' % (len(near), pct(sum(r['succ1m'] for r in near), len(near))))
    for lab, f in (('goal z<=3', lambda r: r['goal_z'] <= 3), ('goal z>3', lambda r: r['goal_z'] > 3), ('D0<15m', lambda r: r['D0'] < 15), ('D0>=15m', lambda r: r['D0'] >= 15)):
        S = [r for r in R if f(r)]; print('  %-10s 1 m success %s, collision %s' % (lab, pct(sum(r['succ1m'] for r in S), len(S)), pct(sum(1 for r in S if r in C), len(S))))
if 'bc' in res and 'P6' in res:
    A = {(r['task'], r['rep']): r for r in res['bc']}; B = {(r['task'], r['rep']): r for r in res['P6']}
    cnt = collections.Counter(('S' if A[k]['succ1m'] else ('C' if A[k]['out'] == 'collision' else 'T')) + '->' +
                              ('S' if B[k]['succ1m'] else ('C' if B[k]['out'] == 'collision' else 'T')) for k in A)
    print('== paired BC -> P6 (1 m; S success, C collision, T timeout):', dict(sorted(cnt.items())))
