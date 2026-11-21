"""Gazebo 288 回合碰撞分析（从原始轨迹出发，只读）。
运行：python3 -I gazebo_collision.py <jindu/gazebo_3method_288_run01> <gazebo/gazebo_rows.json> <输出目录> <运动学 traces 目录 ...>
坐标：result_state.csv 与 diffusion 规划日志为 odom 系，world = odom + (start_x, start_y, 0)。障碍几何取运动学评价同一世界的 episode_start.geometry（obstacle_sha256 已在 gazebo_verify.py 核对一致）。
d = 机体中心到最近障碍表面的距离。所有阈值为工程阈值，非统计检验。
- 碰撞回合（监视器 collision/lost，且碰撞前未进入目标 1 m）按结束前 5 s 内离地 > 0.5 m 时的最小 d 分两类：
  A 障碍接触：最小 d < 0.5 m；B 远离障碍坠地：最小 d ≥ 0.5 m。
- A 类：接触起点 t_c = 从最小 d 时刻向前回溯、d 仍 < 0.4 m 的最早时刻；记录 t_c 时的 d、高度相对障碍顶部、水平速度（前 0.5 s 平均）、
  接近角（水平速度与指向障碍中心的夹角）、接触到坠落的时间、接触前最后一次规划（8 个规划点连同当前位置的折线）到该障碍的最小 d（plan_d）、
  接触时位置指令与实际位置的距离（跟踪误差）；接触点相对机头的水平方位角（bearing_deg，机头取接触前最后一次规划时的偏航），≤ 30° 记为在相机水平视场内（相机水平视场 60°）。
- 全部 288 回合：飞行段（碰撞回合截至 t_c 或结束前 5 s，其余到结束；离地 > 0.5 m）的最小 d，用于比较安全余量。"""
import csv, json, math, sys, glob, os, collections, statistics as st
G, ROWS, OUT, *TR = sys.argv[1:]; os.makedirs(OUT, exist_ok=True)
geo = {}
for D in TR:
    for fn in glob.glob(f'{D}/*.jsonl'):
        s = json.loads(open(fn).readline()); geo.setdefault(s['world_id'], s['geometry'])
def dsurf(p, o):
    x, y, z = p[0] - o['x'], p[1] - o['y'], p[2] - o['z']
    if o['shape'] == 'cylinder':
        dr = math.hypot(x, y) - o['radius']; dz = abs(z) - o['height'] / 2
    else:
        c, s_ = math.cos(-o['yaw']), math.sin(-o['yaw']); lx, ly = c * x - s_ * y, s_ * x + c * y
        qx, qy = abs(lx) - o['size_x'] / 2, abs(ly) - o['size_y'] / 2; dz = abs(z) - o['size_z'] / 2
        dr = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0)
    return math.hypot(max(dr, 0), max(dz, 0)) + min(max(dr, dz), 0)
top = lambda o: o['z'] + (o['height'] if o['shape'] == 'cylinder' else o['size_z']) / 2
def seg_pts(a, b, n=6): return [[a[i] + (b[i] - a[i]) * k / n for i in range(3)] for k in range(n + 1)]
rows = json.load(open(ROWS)); out = []; clear = []
def series(d, c):
    sx, sy = c['start_pos'][0], c['start_pos'][1]
    return [(float(x['timestamp']), float(x['px']) + sx, float(x['py']) + sy, float(x['pz'])) for x in csv.DictReader(open(d + '/result_state.csv'))]
for r in rows:
    d = glob.glob(f"{G}/{r['method']}/{r['task'][:12]}_r{r['rep']}")[0]
    c = json.load(open(d + '/condition.json')); res = json.load(open(d + '/result.json'))
    sx, sy = c['start_pos'][0], c['start_pos'][1]; g = c['goal_pos']; s0 = c['start_pos']; D0 = math.dist(s0, g)
    S = series(d, c); O = geo[c['world_id']]; tend = S[-1][0]
    dd = [min((dsurf(p[1:], o), k) for k, o in enumerate(O)) for p in S]
    fail_coll = r['monitor'] in ('collision', 'lost') and r['out1m'] != '成功'
    cut = len(S)
    e = dict(method=r['method'], task=r['task'][:12], rep=r['rep'], world=c['world_id'].replace('routeA_rl_v1__', ''), cat=r['cat'], out1m=r['out1m'],
             crash=(res.get('crash_reason') or r['monitor']) if r['monitor'] in ('collision', 'lost') else '', goal_z=round(g[2], 2))
    if fail_coll:
        W = [i for i in range(len(S)) if tend - S[i][0] <= 5 and S[i][3] > 0.5]
        im = min(W, key=lambda i: dd[i][0]) if W else len(S) - 1
        e['d_min_last5s'] = round(dd[im][0], 2)
        if W and dd[im][0] < 0.5:
            o = O[dd[im][1]]; ic = im
            while ic > 0 and dd[ic - 1][0] < 0.4 and dd[ic - 1][1] == dd[im][1]: ic -= 1
            cut = ic; t, *p = S[ic]
            e.update(kind='A 障碍接触', obstacle=o['name'], shape=o['shape'], d_contact=round(dd[ic][0], 2), z_rel_top=round(p[2] - top(o), 2),
                     t_contact_to_end=round(tend - t, 1), progress=round(1 - math.dist(p, g) / D0, 2))
            j = next((i for i in range(ic, -1, -1) if t - S[i][0] >= 0.5), 0)
            vx, vy = (p[0] - S[j][1]) / max(t - S[j][0], 1e-3), (p[1] - S[j][2]) / max(t - S[j][0], 1e-3)
            e['v_xy'] = round(math.hypot(vx, vy), 2)
            e['approach_deg'] = round(math.degrees(abs(math.atan2(vx * (o['y'] - p[1]) - vy * (o['x'] - p[0]), vx * (o['x'] - p[0]) + vy * (o['y'] - p[1])))))
            f = glob.glob(d + '/planner_logs/diffusion_*.csv')
            if f:
                P = collections.defaultdict(list)
                for x in csv.DictReader(open(f[0])):
                    P[int(x['plan_id'])].append((float(x['ros_time']), [float(x['world_pos_x']) + sx, float(x['world_pos_y']) + sy, float(x['world_pos_z'])], [float(x['cur_x']) + sx, float(x['cur_y']) + sy, float(x['cur_z'])]))
                prev = [k for k in P if P[k][0][0] <= t]
                if prev:
                    k = max(prev); pts = [P[k][0][2]] + [w for _, w, _ in P[k]]
                    e['plan_d'] = round(min(dsurf(q, o) for a, b in zip(pts, pts[1:]) for q in seg_pts(a, b)), 2)
                    e['plan_age_s'] = round(t - P[k][0][0], 2)
                    yaw = None
                    for x in csv.DictReader(open(f[0])):
                        if float(x['ros_time']) <= t: yaw = float(x['cur_yaw'])
                    if yaw is not None:
                        # 接触点方向：机体到障碍表面最近点（圆柱取中心方向，箱体取局部最近点）
                        if o['shape'] == 'cylinder': qx, qy = o['x'], o['y']
                        else:
                            c_, s_ = math.cos(-o['yaw']), math.sin(-o['yaw']); lx, ly = c_ * (p[0] - o['x']) - s_ * (p[1] - o['y']), s_ * (p[0] - o['x']) + c_ * (p[1] - o['y'])
                            lx, ly = max(-o['size_x'] / 2, min(o['size_x'] / 2, lx)), max(-o['size_y'] / 2, min(o['size_y'] / 2, ly))
                            c2, s2 = math.cos(o['yaw']), math.sin(o['yaw']); qx, qy = o['x'] + c2 * lx - s2 * ly, o['y'] + s2 * lx + c2 * ly
                        e['bearing_deg'] = round(abs(math.degrees(math.atan2(math.sin(math.atan2(qy - p[1], qx - p[0]) - yaw), math.cos(math.atan2(qy - p[1], qx - p[0]) - yaw)))))
                        e['in_fov'] = e['bearing_deg'] <= 30
            pc = [(float(x['timestamp']), float(x['cmd_px']) + sx, float(x['cmd_py']) + sy, float(x['cmd_pz'])) for x in csv.DictReader(open(d + '/result_pos_cmd.csv'))]
            if pc:
                q = min(pc, key=lambda z: abs(z[0] - t)); e['track_err'] = round(math.dist(q[1:], p), 2); e['cmd_d'] = round(dsurf(q[1:], o), 2)
        else:
            iz = max((i for i in range(len(S)) if S[i][3] > 1.0), default=0); cut = iz
            e.update(kind='B 远离障碍坠地', z_before=round(S[iz][3], 2), progress=round(1 - math.dist(S[-1][1:], g) / D0, 2),
                     d_goal_end=round(math.dist(S[-1][1:], g), 2), t_fall=round(tend - S[iz][0], 1))
        out.append(e)
    elif r['monitor'] in ('collision', 'lost'):
        W = [i for i in range(len(S)) if tend - S[i][0] <= 5]; cut = min(W) if W else len(S)
    air = [dd[i][0] for i in range(cut) if S[i][3] > 0.5]
    clear.append(dict(method=r['method'], task=r['task'][:12], rep=r['rep'], cat=r['cat'], out1m=r['out1m'], fail_coll=fail_coll,
                      min_clear=round(min(air), 3) if air else None))
keys = list(dict.fromkeys(k for e in out for k in e))
with open(f'{OUT}/collision_episodes.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(out)
with open(f'{OUT}/clearance_all.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(clear[0])); w.writeheader(); w.writerows(clear)
print(len(out), len(clear))
