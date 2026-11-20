"""只读：F8 诊断 run03（D1 闭环、D2 离线）分层分析（Claude）。
用法：python3 -I d1d2_analysis.py <run03 核验导出目录 program/f8_diag_run03_review_20261120> <F8 run01 核验导出目录 program/f8_audit_20261119>
①复算冻结判定；②按"P6 不给中间点能否解出"把 85 个库任务分成两层，比较各臂；③按建库时引导成功次数分层；
④逐任务：新层离线损失下降（相对同 seed 对照）与闭环到达变化的关系；⑤失败条件上的轨迹形态（同条件配对）。
"""
import csv, sys, collections, statistics as st
R, F1 = sys.argv[1:3]
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
J = rd(f'{R}/task_d1_d2_join.csv'); C = rd(f'{R}/conditions.csv')
ARMS = ['P6', 'P20', 'P21', 'P22', 'P23']
reach = {(r['arm'], r['task_id']): int(r['reached']) for r in J}
loss = {(r['arm'], r['task_id']): float(r['new_layer_loss']) for r in J}
tasks = sorted({r['task_id'] for r in J})
solved = lambda a, t: reach[(a, t)] >= 3
print('== ① 冻结判定复算')
S = {a: sum(solved(a, t) for t in tasks) for a in ARMS}; print('  解出任务数', S)
thr = max(S['P22'], S['P23']) + 8; print('  D1 门槛', thr, '→', '达阈值' if S['P20'] >= thr and S['P21'] >= thr else '未达阈值')
Lm = {a: st.mean(loss[(a, t)] for t in tasks) for a in ARMS}; cm = (Lm['P22'] + Lm['P23']) / 2
print('  D2 新层损失', {a: round(v, 5) for a, v in Lm.items()}, '比值', round(Lm['P20'] / cm, 4), round(Lm['P21'] / cm, 4))
G = collections.Counter(r['task_id'] for r in rd(f'{F1}/collection_flights.csv') if r['outcome'] == 'reached')
print('\n== ② 按 P6 不给中间点能否解出分层（解出=≥3/5）')
for name, sel in (('P6 已解出', lambda t: solved('P6', t)), ('P6 未解出', lambda t: not solved('P6', t))):
    T = [t for t in tasks if sel(t)]
    print(f'  {name}（{len(T)} 个任务，{5*len(T)} 条件）：' + '；'.join(f'{a} 解出 {sum(solved(a, t) for t in T)}、到达 {sum(reach[(a, t)] for t in T)}' for a in ARMS))
print('\n== ③ 按建库时引导成功次数分层（5 次引导飞行中到达次数）')
for g in (1, 2, 3, 4, 5):
    T = [t for t in tasks if G[t] == g]
    if T: print(f'  引导 {g}/5（{len(T)} 个任务）：' + '；'.join(f'{a} 解出 {sum(solved(a, t) for t in T)}' for a in ARMS))
print('\n== ④ 逐任务：处理相对同 seed 对照的新层损失比，与闭环到达次数差')
for t_, c_ in (('P20', 'P22'), ('P21', 'P23')):
    ratio = [loss[(t_, t)] / loss[(c_, t)] for t in tasks]; dR = [reach[(t_, t)] - reach[(c_, t)] for t in tasks]
    q = sorted(range(len(tasks)), key=lambda i: ratio[i]); n = len(q) // 3
    lo, hi = q[:n], q[-n:]
    print(f'  {t_}对{c_}：损失比中位 {st.median(ratio):.3f}；损失比最低三分之一 {n} 个任务的到达差合计 {sum(dR[i] for i in lo):+d}，最高三分之一 {sum(dR[i] for i in hi):+d}；'
          f'皮尔逊相关(损失比, 到达差) {st.correlation(ratio, dR):+.3f}')
print('\n== ⑤ 同条件配对、两边都失败（碰撞或超时）时的轨迹形态：处理减对照的均值')
K = {(r['arm'], r['task_id'], r['repeat']): r for r in C}
for t_, c_ in (('P20', 'P22'), ('P21', 'P23'), ('P22', 'P6'), ('P20', 'P6')):
    d = collections.defaultdict(list)
    for (a, t, rp), r in K.items():
        if a != t_: continue
        o = K[(c_, t, rp)]
        if r['outcome'] != 'reached' and o['outcome'] != 'reached':
            for f in ('max_cross_track_m', 'min_goal_distance_m', 'path_length_m', 'decisions', 'z_span_m'):
                d[f].append(float(r[f]) - float(o[f]))
    print(f'  {t_}−{c_}（{len(d["decisions"])} 对）：' + '，'.join(f'{f} {st.mean(v):+.3f}（中位 {st.median(v):+.3f}）' for f, v in d.items()))
