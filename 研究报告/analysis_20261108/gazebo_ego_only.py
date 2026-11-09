"""Gazebo 中 EGO-Planner 成功、UAV-iDP3 与本文方法都失败的条件（同一任务同一次飞行），逐条列出失败方式与 EGO 的通过方式。
运行：python3 -I gazebo_ego_only.py <jindu/gazebo_3method_288_run01> <gazebo 输出目录> <运动学 traces 目录 ...>
依赖 gazebo_collision.py 的 collision_episodes.csv。绕行侧：相对起点→目标连线，障碍中心在左/右，轨迹在障碍处经过其左侧或右侧（以轨迹最接近该障碍的点判定）。"""
import csv, json, math, sys, glob, os, collections
G, GO, *TR = sys.argv[1:]
geo = {}
for D in TR:
    for fn in glob.glob(f'{D}/*.jsonl'):
        s = json.loads(open(fn).readline()); geo.setdefault(s['world_id'], s['geometry'])
def dsurf(p, o):
    x, y, z = p[0] - o['x'], p[1] - o['y'], p[2] - o['z']
    if o['shape'] == 'cylinder':
        dr = math.hypot(x, y) - o['radius']; dz = abs(z) - o['height'] / 2
    else:
        c_, s_ = math.cos(-o['yaw']), math.sin(-o['yaw']); lx, ly = c_ * x - s_ * y, s_ * x + c_ * y
        qx, qy = abs(lx) - o['size_x'] / 2, abs(ly) - o['size_y'] / 2; dz = abs(z) - o['size_z'] / 2
        dr = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0)
    return math.hypot(max(dr, 0), max(dz, 0)) + min(max(dr, dz), 0)
rows = json.load(open(f'{GO}/gazebo_rows.json')); o = {(r['method'], r['task'], r['rep']): r for r in rows}
E = {(e['method'], e['task'], e['rep']): e for e in csv.DictReader(open(f'{GO}/collision/collision_episodes.csv'))}
conds = sorted({(r['task'], r['rep']) for r in rows})
sub = [k for k in conds if o[('EGO',) + k]['out1m'] == '成功' and all(o[(m,) + k]['out1m'] != '成功' for m in ('P0', 'P6'))]
def traj(m, t, rp):
    d = glob.glob(f'{G}/{m}/{t[:12]}_r{rp}')[0]; c = json.load(open(d + '/condition.json'))
    sx, sy = c['start_pos'][:2]
    return c, [(float(x['px']) + sx, float(x['py']) + sy, float(x['pz'])) for x in csv.DictReader(open(d + '/result_state.csv'))]
def side(c, p, ob):
    s, g = c['start_pos'], c['goal_pos']; ux, uy = g[0] - s[0], g[1] - s[1]
    return '左' if ux * (p[1] - ob['y']) - uy * (p[0] - ob['x']) > 0 else '右'
out = []
for t, rp in sub:
    row = dict(task=t[:12], rep=rp, cat=o[('EGO', t, rp)]['cat'], world=o[('EGO', t, rp)]['world'].replace('routeA_rl_v1__', ''))
    obs = None
    for m in ('P0', 'P6'):
        e = E.get((m, t[:12], rp)); r = o[(m, t, rp)]
        if r['out1m'] == '超时': row[m] = '超时'
        elif e and e['kind'].startswith('A'): row[m] = f"撞{e['obstacle']}（{e['shape']}，接触时低于障碍顶 {-float(e['z_rel_top']):.1f} m，接触前规划距障碍 {e.get('plan_d','')} m，接触→坠落 {e['t_contact_to_end']} s）"; obs = obs or e['obstacle']
        else: row[m] = f"{e['kind']}（坠地前高度 {e.get('z_before','')} m，距目标 {e.get('d_goal_end','')} m）" if e else r['out1m']
    c, S = traj('EGO', t, rp); G_ = {x['name']: x for x in geo[c['world_id']]}
    if obs:
        ob = G_[obs]
        def dmin(P):
            i = min(range(len(P)), key=lambda i: dsurf(P[i], ob)); return i, dsurf(P[i], ob)
        i, dv = dmin(S); tp = ob['z'] + (ob['height'] if ob['shape'] == 'cylinder' else ob['size_z']) / 2
        row['EGO 过该障碍'] = f"{side(c, S[i], ob)}侧，最小余量 {dv:.2f} m，高度 {S[i][2]:.1f} m（障碍顶 {tp:.1f} m）"
        for m in ('P0', 'P6'):
            _, P = traj(m, t, rp); j, _ = dmin(P); row[f'{m} 侧'] = side(c, P[j], ob)
    zs = {m: traj(m, t, rp)[1] for m in ('EGO', 'P0', 'P6')}
    row['高度范围 EGO/P0/P6'] = ' / '.join(f"{min(z for *_, z in zs[m][len(zs[m])//10:]):.1f}—{max(z for *_, z in zs[m]):.1f}" for m in ('EGO', 'P0', 'P6'))
    out.append(row)
keys = list(dict.fromkeys(k for r in out for k in r))
with open(f'{GO}/collision/ego_only_success.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(out)
for r in out: print(r)
