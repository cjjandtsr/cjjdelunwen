"""运动学 O′ 按任务统计（用户 11-09 决定为正文表 4 口径）。
口径：每个任务评价 5 次，至少 3 次成功记该任务成功；否则按失败回合中较多的一类记碰撞或超时，两类相同时记碰撞（与 Gazebo 两次均失败、任一次碰撞记碰撞一致）。
成功 = 碰撞前进入目标 R：正文 RAD = 1.5 m（用户 11-09 由 1 m 改为 1.5 m），补充材料 0.5 m（训练到达奖励半径，也是预先登记判定所用标准）。去除 oprime/exclusions.json 中的任务。
运行：python3 -I kin_task_level.py <rows.json> <analysis_20261108 目录>
输出（<目录>/oprime_task/）：main.csv、main_05m.csv、second_run.csv、pairs.csv、text_numbers.json、table3.csv、full199_episode_05m.csv（补充材料：去除前、按每次评价、0.5 m 原标准）。
区间：按世界聚类自助法 20000 次，seed 2026102601（工程阈值，非显著性检验）。"""
import json, sys, csv, collections, random, os, statistics as st
ROWS, A = sys.argv[1:3]; RAD = 1.5; OUT = f'{A}/oprime_task'; os.makedirs(OUT, exist_ok=True)
R = json.load(open(ROWS)); EXC = set(json.load(open(f'{A}/oprime/exclusions.json'))['tasks'])
NAME = {'P0': 'UAV-iDP3', 'P2': 'Reg-DPPO w/o Stage II', 'P3': 'Single-stage DPPO', 'P4': 'Reg-DPPO w/o BC reg.', 'P6': '本文方法',
        'P14': 'Reg-DPPO w/o Stage II（第二次运行）', 'P15': '本文方法（第二次运行）'}
def ep(r, rad): return '成功' if (r['out'] == 'reached' or r['near'] < rad) else ('碰撞' if r['out'] == 'collision' else '超时')
def tasks(rows, rad):
    T = collections.defaultdict(list); info = {}
    for r in rows: T[(r['policy'], r['task'])].append(ep(r, rad)); info[r['task']] = (r['cat'], r['world'])
    lab = {}
    for k, v in T.items():
        c = collections.Counter(v); assert len(v) == 5, (k, len(v))
        lab[k] = '成功' if c['成功'] >= 3 else ('碰撞' if c['碰撞'] >= c['超时'] else '超时')
    return lab, info
keep = [r for r in R if r['task'] not in EXC]
PE = collections.defaultdict(list)
for r in csv.DictReader(open(f'{A}/path_eff_main/path_eff_episodes.csv')): PE[(r['策略'], r['任务'])].append(float(r['路径效率']))
H = ['方法', '任务', '成功', '稀疏任务', '稀疏成功', '适中任务', '适中成功', '密集任务', '密集成功', '碰撞', '超时', '路径效率']
def table(rows, rad, pols, fn, pe=True):
    lab, info = tasks(rows, rad); out = []
    for p in pols:
        ks = [k for k in lab if k[0] == p]; c = collections.Counter(lab[k] for k in ks); row = [NAME[p], len(ks), c['成功']]
        for d in ['稀疏', '适中', '密集']:
            kd = [k for k in ks if info[k[1]][0] == d]; row += [len(kd), sum(lab[k] == '成功' for k in kd)]
        v = [x for k in ks if lab[k] == '成功' for x in PE.get(k, [])] if pe else []
        row += [c['碰撞'], c['超时'], f'{st.median(v):.3f}' if v else '']
        out.append(row)
    with open(f'{OUT}/{fn}', 'w', newline='') as f: w = csv.writer(f); w.writerow(H); w.writerows(out)
    return lab, info
P5 = ['P0', 'P2', 'P3', 'P4', 'P6']
lab, info = table(keep, RAD, P5, 'main.csv')
table(keep, 0.5, P5, 'main_05m.csv', pe=False)
table(keep, RAD, ['P14', 'P15'], 'second_run.csv', pe=False)
# 配对差（任务级）
def boot(items):
    by = collections.defaultdict(lambda: [0, 0])
    for w, a in items: by[w][0] += a; by[w][1] += 1
    ws = sorted(by); rng = random.Random(2026102601); v = []
    for _ in range(20000):
        s = n = 0
        for _ in ws: x = by[rng.choice(ws)]; s += x[0]; n += x[1]
        v.append(s / n)
    v.sort(); return round(100 * v[500], 1), round(100 * v[19499], 1)
ts = sorted({k[1] for k in lab})
it = [(info[t][1], (lab[('P6', t)] == '成功') - (lab[('P0', t)] == '成功')) for t in ts]
lo, hi = boot(it)
with open(f'{OUT}/pairs.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['比较', '任务', '世界', '差%', '区间下%', '区间上%']); w.writerow(['本文方法 − UAV-iDP3', len(ts), len({info[t][1] for t in ts}), round(100 * sum(x for _, x in it) / len(it), 1), lo, hi])
txt = {}
for p in ['P0', 'P6']:
    for d in ['稀疏', '适中', '密集']:
        kd = [k for k in lab if k[0] == p and info[k[1]][0] == d]; c = collections.Counter(lab[k] for k in kd)
        txt[f'{NAME[p]} {d} 碰撞率/超时率%'] = f"{100*c['碰撞']/len(kd):.1f} / {100*c['超时']/len(kd):.1f}"
# 突破与保持（4.2、4.3 节）：UAV-iDP3 失败的任务中各方法完成数；UAV-iDP3、第一阶段策略已完成的任务中各方法保持数
okT = lambda p, t: lab[(p, t)] == '成功'
f0 = [t for t in ts if not okT('P0', t)]; s0 = [t for t in ts if okT('P0', t)]; s2 = [t for t in ts if okT('P2', t)]
txt['UAV-iDP3 失败任务数'] = len(f0)
for p in ['P2', 'P3', 'P4', 'P6']:
    txt[f'{NAME[p]} 在 UAV-iDP3 失败任务中完成数'] = sum(okT(p, t) for t in f0)
    txt[f'{NAME[p]} 保持 UAV-iDP3 已完成任务数（共 {len(s0)}）'] = sum(okT(p, t) for t in s0)
for p in ['P3', 'P4', 'P6']:
    txt[f'{NAME[p]} 保持第一阶段策略已完成任务数（共 {len(s2)}）'] = sum(okT(p, t) for t in s2)
json.dump(txt, open(f'{OUT}/text_numbers.json', 'w'), ensure_ascii=False, indent=1)
# 表3
TK = {r['task_id']: r for r in csv.DictReader(open(f'{A}/codex_details/tasks_199.csv', encoding='utf-8-sig'))}
G = {r['task_id']: r['outcome'] == 'reached' for r in csv.DictReader(open(f'{A}/g12/g12_tasks.csv')) if r['split'] in ('test12', 'extv2')}
GZ = json.load(open(f'{A}/gazebo/gazebo_rows.json')); GE = json.load(open(f'{A}/gazebo/exclusions.json'))
GZ = {r['task'] for r in GZ if not any(r['world'].endswith(w) for w in GE['worlds']) and not any(r['task'].startswith(t) for t in GE['tasks'])}
cat = {t: info[t][0] for t in ts}
with open(f'{OUT}/table3.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['难度', '任务数', '世界数', '直线距离中位数', '最小', '最大', '直线飞行成功任务数', 'Gazebo任务数'])
    for d in ['稀疏', '适中', '密集', '总体']:
        tt = [t for t in ts if d == '总体' or cat[t] == d]; dist = [float(TK[t]['straight_distance_3d_m']) for t in tt]
        w.writerow([d, len(tt), len({TK[t]['world_id'] for t in tt}), round(st.median(dist), 1), round(min(dist), 1), round(max(dist), 1), sum(G[t] for t in tt),
                    sum(1 for g in GZ if any(t.startswith(g) for t in tt))])
# 补充：去除前、按每次评价（原表 4）
with open(f'{OUT}/full199_episode_05m.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['方法', '回合', '成功', '稀疏回合', '稀疏成功', '适中回合', '适中成功', '密集回合', '密集成功', '碰撞', '超时'])
    for p in P5:
        x = [r for r in R if r['policy'] == p]; c = collections.Counter(ep(r, 0.5) for r in x); row = [NAME[p], len(x), c['成功']]
        for d in ['稀疏', '适中', '密集']: xd = [r for r in x if r['cat'] == d]; row += [len(xd), sum(ep(r, 0.5) == '成功' for r in xd)]
        w.writerow(row + [c['碰撞'], c['超时']])
for fn in ['main.csv', 'main_05m.csv', 'second_run.csv', 'pairs.csv', 'table3.csv']: print(fn); print(open(f'{OUT}/{fn}').read())
print(open(f'{OUT}/text_numbers.json').read())
