"""前置研究 ②：直线被挡任务中，绕行路线的类型与可观测性（dev420 #E2 原迹，P6、P18、P19；只作诊断，不用于调参）。
# 2026-11-17：项目仓库整理后，这些原迹改为精简的 *.jsonl.gz（所用字段均保留）；本脚本同时接受 *.jsonl 与 *.jsonl.gz。
用法：python3 -I pre2_observability.py <项目仓库根目录> <blocked_tasks_dev420.json>
(A) 每个被挡任务的测地最短路线（从起点）：是从障碍上方越过还是侧向绕行；路线最高点；开始偏离直线方向的位置。
(B) 碰撞回合，在碰撞前第 1—4 个决策的起点：测地路线前方 3 m 处的点相对机头朝向的水平方位角、俯仰角；
    目标方向与测地方向的夹角；策略实际位移方向与测地方向的夹角。相机：水平视场 60°（±30°），量程 10 m，朝机头方向；竖直视场未知，只报告俯仰角。"""
import ast, glob, gzip, json, math, os, sys, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_field import World, line_clear
repo, blkf = sys.argv[1], sys.argv[2]; BLK = set(json.load(open(blkf)))
def load(f):
    op = gzip.open if f.endswith('.gz') else open; L = [json.loads(l) for l in op(f, 'rt')]
    s = L[0]; task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task']); return s, task, [t for t in L if t.get('type') == 'transition'], L[-1]
SRC = {'P6': glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_dev/full/P6/traces/*.jsonl*'),
       'P18': glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P18/traces/*.jsonl.gz'), 'P19': glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P19/traces/*.jsonl.gz')}
EP = collections.defaultdict(list)
for pol, fs in SRC.items():
    for f in fs:
        s, task, T, e = load(f)
        if s['task_id'] in BLK: EP[s['task_id']].append((pol, s, task, T, e))
ang = lambda u, v: math.degrees(math.acos(np.clip(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-12), -1, 1)))
A, B = [], []
for tid, lst in sorted(EP.items()):
    s, task = lst[0][1], lst[0][2]; s0, g = np.array(task['start_pos']), np.array(task['goal_pos']); geom = s['geometry']
    P = np.array([p for _, _, _, T, _ in lst for t in T for p in t['executed_path']] + [s0, g]); lo = P.min(0) - 5; hi = P.max(0) + 5; lo[2], hi[2] = task['z_range'][0], task['z_range'][1]
    W = World(geom, lo, hi); F = W.field(g); path = F.path(s0, 1e9)
    tops = [(o, o['z'] + (o['height'] if o['shape'] == 'cylinder' else o['size_z']) / 2) for o in geom]
    def over(q):
        for o, top in tops:
            if o['shape'] == 'cylinder': inside = math.hypot(q[0] - o['x'], q[1] - o['y']) <= o['radius'] + .3
            else:
                c, s_ = math.cos(o['yaw']), math.sin(o['yaw']); dx, dy = q[0] - o['x'], q[1] - o['y']
                inside = abs(c * dx + s_ * dy) <= o['size_x'] / 2 + .3 and abs(-s_ * dx + c * dy) <= o['size_y'] / 2 + .3
            if inside and q[2] > top: return True
        return False
    ov = any(over(q) for q in path); d = (g - s0) / np.linalg.norm(g - s0)
    lat = max(float(np.linalg.norm((q - s0) - np.dot(q - s0, d) * d)) for q in path)
    zline = lambda q: s0[2] + np.dot(q - s0, d) / np.linalg.norm(g - s0) * (g[2] - s0[2])
    dz = max(float(q[2] - zline(q)) for q in path)
    latxy = max(float(np.linalg.norm(((q - s0) - np.dot(q - s0, d) * d)[:2])) for q in path)
    maxtop = max(top for _, top in tops)
    A.append(dict(task=tid, over=ov, lat=lat, dz=dz, latxy=latxy, zmax=float(path[:, 2].max()), start_z=float(s0[2]), goal_z=float(g[2]), maxtop=maxtop, zhi=task['z_range'][1]))
    for pol, s, task, T, e in lst:
        if e['done_reason'] != 'collision': continue
        for back in (1, 2, 3, 4):
            k = len(T) - 1 - back
            if k < 0: continue
            p = np.array(T[k]['pre_state']['position']); yaw = T[k]['pre_state']['yaw']; pth = F.path(p, 3.0); q = pth[-1]
            if np.linalg.norm(q - p) < 1.0: continue
            v = q - p; head = np.array([math.cos(yaw), math.sin(yaw)])
            bearing = math.degrees(math.atan2(head[0] * v[1] - head[1] * v[0], head[0] * v[0] + head[1] * v[1])); elev = math.degrees(math.atan2(v[2], np.linalg.norm(v[:2])))
            gv = g - p; gb = math.degrees(math.atan2(head[0] * gv[1] - head[1] * gv[0], head[0] * gv[0] + head[1] * gv[1]))
            mv = np.array(T[k]['executed_path'][-1]) - p
            B.append(dict(pol=pol, back=back, bearing=bearing, elev=elev, goal_bearing=gb, geo_vs_goal=ang(v, gv), move_vs_geo=ang(mv, v) if np.linalg.norm(mv) > .05 else None,
                          move_vs_goal=ang(mv, gv) if np.linalg.norm(mv) > .05 else None, z=float(p[2]), over=ov))
json.dump(dict(A=A, B=B), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pre2_rows.json'), 'w'))
print('== (A) 33 个直线被挡任务的测地最短路线')
print('  从障碍上方越过的任务：%d；侧向绕行：%d' % (sum(a['over'] for a in A), sum(not a['over'] for a in A)))
print('  路线相对起终点直线的最大水平偏移 m：中位 %.2f，最大 %.2f；最大向上偏移 m：中位 %.2f，最大 %.2f' % (np.median([a['latxy'] for a in A]), max(a['latxy'] for a in A), np.median([a['dz'] for a in A]), max(a['dz'] for a in A)))
print('  路线最高点 z：中位 %.2f；障碍最高顶面：中位 %.2f；允许高度上限：%s' % (np.median([a['zmax'] for a in A]), np.median([a['maxtop'] for a in A]), sorted({a['zhi'] for a in A})))
for a in A: print('   ', a['task'].split('__rl_train__')[1][:44], '越顶' if a['over'] else '侧绕', '水平偏移 %.1f 向上 %.1f 最高 %.1f（起 %.1f 终 %.1f 障碍顶 %.1f）' % (a['latxy'], a['dz'], a['zmax'], a['start_z'], a['goal_z'], a['maxtop']))
print('== (B) 碰撞前各决策起点（P6、P18、P19 的碰撞回合）')
for back in (1, 2, 3, 4):
    X = [b for b in B if b['back'] == back]
    print('  碰撞前第 %d 个决策（n=%d）：测地前方 3 m 点在水平视场内（|方位|≤30°）%.0f%%；|方位| 中位 %.0f°；俯仰中位 %.0f°，|俯仰|>20° 的比例 %.0f%%；测地方向与目标方向夹角中位 %.0f°；实际位移与测地方向夹角中位 %.0f°，与目标方向夹角中位 %.0f°' % (
        back, len(X), 100 * np.mean([abs(b['bearing']) <= 30 for b in X]), np.median([abs(b['bearing']) for b in X]), np.median([b['elev'] for b in X]), 100 * np.mean([abs(b['elev']) > 20 for b in X]),
        np.median([b['geo_vs_goal'] for b in X]), np.median([b['move_vs_geo'] for b in X if b['move_vs_geo'] is not None]), np.median([b['move_vs_goal'] for b in X if b['move_vs_goal'] is not None])))
for ov in (True, False):
    X = [b for b in B if b['over'] == ov and b['back'] == 3]
    if X: print('  %s任务，碰撞前第 3 个决策（n=%d）：水平视场内 %.0f%%；俯仰中位 %.0f°；实际位移与测地方向夹角中位 %.0f°' % ('越顶' if ov else '侧绕', len(X), 100 * np.mean([abs(b['bearing']) <= 30 for b in X]), np.median([b['elev'] for b in X]), np.median([b['move_vs_geo'] for b in X if b['move_vs_geo'] is not None])))
