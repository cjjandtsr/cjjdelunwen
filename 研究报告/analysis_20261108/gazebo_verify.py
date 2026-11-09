"""Gazebo 288 回合核验（Claude 侧，只读）。
运行：python3 -I gazebo_verify.py <jindu/gazebo_3method_288_run01> <oprime rows.json> <tasks_199.csv> <输出目录> <运动学 traces 目录 ...>
检查：A 完整性与调度；B 任务与障碍几何同源；C 权重与开关；D 运行日志与重跑；E 结局与障碍几何的一致性；F 期限；G 学习策略重规划周期；H 起飞后起点偏差。"""
import csv, json, math, sys, glob, os, collections, statistics as st
G, ROWS, TASKS, OUT, *TR = sys.argv[1:]; os.makedirs(OUT, exist_ok=True)
rep = {}
def chk(k, ok, info): rep[k] = dict(ok=bool(ok), info=info); print(('PASS ' if ok else 'FAIL ') + k, info)
R = list(csv.DictReader(open(f'{G}/regrade_1m.csv')))
cond = {}
for r in R:
    d = f"{G}/{r['method']}/{r['task_id'][:12]}_r{r['repeat']}"
    c = json.load(open(d + '/condition.json')); c['_dir'] = d; assert c['task_id'].startswith(r['task_id']); cond[(r['method'], c['task_id'], int(r['repeat']))] = c
# A
by = collections.Counter(k[0] for k in cond); tasks = {m: sorted({(k[1], k[2]) for k in cond if k[0] == m}) for m in by}
chk('A1 每方法96回合、三方法任务×重复相同', all(v == 96 for v in by.values()) and tasks['P0'] == tasks['P6'] == tasks['EGO'], dict(by))
O = {}
for r in json.load(open(ROWS)):
    O.setdefault(r['task'], r['cat'])
CAT = {'zero': '稀疏', 'low': '适中', 'high': '密集'}
tc = {k[1]: c['task_category'] for k, c in cond.items()}
chk('A2 任务均属 O′，类别与 O′ 分类一致', all(t in O and CAT[v] == O[t] for t, v in tc.items()), dict(collections.Counter(CAT[v] for v in tc.values())))
chk('A3 涉及世界数', True, len({c['world_id'] for c in cond.values()}))
# B
T = {r['task_id']: r for r in csv.DictReader(open(TASKS, encoding='utf-8-sig'))}
err = max(max(abs(c['start_pos'][i] - float(T[k[1]][f'start_{a}'])) for i, a in enumerate('xyz')) + max(abs(c['goal_pos'][i] - float(T[k[1]][f'goal_{a}'])) for i, a in enumerate('xyz')) for k, c in cond.items())
chk('B1 起终点与冻结任务库一致', err < 1e-5, f'最大偏差 {err:.2e} m')
geo, osha = {}, {}
for D in TR:
    for fn in glob.glob(f'{D}/*.jsonl'):
        s = json.loads(open(fn).readline())
        if s['world_id'] not in geo: geo[s['world_id']] = s['geometry']; osha[s['world_id']] = s['obstacle_sha256']
ws = {c['world_id'] for c in cond.values()}
chk('B2 障碍文件哈希与运动学评价同一世界一致', all(w in osha for w in ws) and all(c['obstacle_sha256'] == osha[c['world_id']] for c in cond.values()), f'{sum(w in osha for w in ws)}/{len(ws)} 个世界有运动学几何')
# C
p0 = [c for k, c in cond.items() if k[0] == 'P0']; p6 = [c for k, c in cond.items() if k[0] == 'P6']; eg = [c for k, c in cond.items() if k[0] == 'EGO']
chk('C1 P0 关 LoRA、P6 开 LoRA，主干同一检查点', all(not c['lora_enabled'] for c in p0) and all(c['lora_enabled'] for c in p6) and len({c['checkpoint'] for c in p0 + p6}) == 1 and len({c['lora_ckpt'] for c in p6}) == 1,
    dict(ckpt=p6[0]['checkpoint'].split('outputs/')[-1], lora=p6[0]['lora_ckpt'].split('outputs/')[-1]))
chk('C2 EGO 回合策略类型', True, dict(collections.Counter(c['env'].get('POLICY_TYPE', c['env'].get('ENGINE')) for c in eg)))
# D
L = [json.loads(l) for l in open(f'{G}/run_log.jsonl')]
st_ = collections.Counter(l['status'] for l in L)
last = {}
for l in L: last[(l['method'], l['task_id'], int(l['repeat']))] = l
chk('D1 运行日志：重跑后每条件最终一条，状态与结果一致', len(last) == 288 and all(last[k]['status'] == cond[k]['status'] for k in cond), dict(entries=len(L), status=dict(st_)))
# E 几何
def d_obs(p, o):
    x, y, z = p[0] - o['x'], p[1] - o['y'], p[2] - o['z']
    if o['shape'] == 'cylinder':
        dr = math.hypot(x, y) - o['radius']; dz = abs(z) - o['height'] / 2
    else:
        cy, sy = math.cos(-o['yaw']), math.sin(-o['yaw']); lx, ly = cy * x - sy * y, sy * x + cy * y
        qx, qy = abs(lx) - o['size_x'] / 2, abs(ly) - o['size_y'] / 2; dz = abs(z) - o['size_z'] / 2
        dr = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0)
        return math.hypot(max(dr, 0), max(dz, 0)) + min(max(dr, dz), 0) if True else 0
    return math.hypot(max(dr, 0), max(dz, 0)) + min(max(dr, dz), 0)
E = []
for k, c in cond.items():
    S = [(float(x['px']) + c['start_pos'][0], float(x['py']) + c['start_pos'][1], float(x['pz'])) for x in csv.DictReader(open(c['_dir'] + '/result_state.csv'))]
    g = geo[c['world_id']]
    dmin = [min(d_obs(p, o) for o in g) for p in S]
    i_end = len(S) - 1; j = min(range(len(S)), key=lambda i: dmin[i])
    res = json.load(open(c['_dir'] + '/result.json'))
    E.append(dict(method=k[0], task=k[1][:12], rep=k[2], status=c['status'], crash=res.get('crash_reason'), min_obs=round(min(dmin), 3), end_obs=round(min(dmin[-25:]), 3),
                  end_z=round(S[-1][2], 3), monitor_min_clear=round(res.get('min_clearance', float('nan')), 3), start_gap=round(math.dist(S[0], c['start_pos']), 3), n=len(S),
                  t=round(res['end_time'] - res['start_time'], 1)))
with open(f'{OUT}/episodes.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(E[0])); w.writeheader(); w.writerows(E)
coll = [e for e in E if e['status'] == 'collision']; ok = [e for e in E if e['status'] in ('reached', 'timeout')]
near = sum(e['end_obs'] < 0.6 or e['end_z'] < 0.3 for e in coll)
chk('E1 碰撞回合：末段贴近障碍(<0.6 m)或已触地(z<0.3 m)', near == len(coll), f'{near}/{len(coll)}；崩溃原因 {dict(collections.Counter(e["crash"] for e in coll))}')
pen = [e for e in ok if e['min_obs'] < 0.1]
chk('E2 非碰撞回合未穿入障碍（最小距离 ≥ 0.1 m 机体半径）', not pen, f'违例 {len(pen)}；非碰撞回合最小净距中位数 {st.median(e["min_obs"] for e in ok):.2f} m；例 {pen[:3]}')
chk('E3 碰撞回合的末段离障碍距离分布', True, dict(贴近障碍=sum(e['end_obs'] < 0.6 for e in coll), 仅触地=sum(e['end_obs'] >= 0.6 and e['end_z'] < 0.3 for e in coll)))
# F
to = [e['t'] for e in E if e['status'] == 'timeout']
chk('F1 超时回合持续时间约为 240 s 期限', all(230 <= t <= 260 for t in to), f'范围 {min(to)}—{max(to)} s，n={len(to)}')
# G 重规划周期
per = collections.defaultdict(list)
for k, c in cond.items():
    if k[0] == 'EGO': continue
    fs = glob.glob(c['_dir'] + '/planner_logs/diffusion_*.csv')
    if not fs: continue
    t0 = {}
    for x in csv.DictReader(open(fs[0])): t0.setdefault(int(x['plan_id']), float(x['ros_time']))
    ts = [t0[i] for i in sorted(t0)]; per[k[0]] += [b - a for a, b in zip(ts, ts[1:])]
chk('G1 学习策略重规划间隔（中位数，s）', True, {m: round(st.median(v), 3) for m, v in per.items()})
# H
chk('H1 记录首帧与任务起点的距离（中位数/最大，m）', True, dict(median=st.median(e['start_gap'] for e in E), max=max(e['start_gap'] for e in E)))
json.dump(rep, open(f'{OUT}/verify.json', 'w'), ensure_ascii=False, indent=1)
