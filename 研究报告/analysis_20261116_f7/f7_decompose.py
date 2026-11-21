"""只读：在 f7_episodes.py 的输出上做配对与失败分解。
用法：python3 f7_decompose.py <episodes.json>"""
import json, sys, statistics as st, collections, random
R = json.load(open(sys.argv[1]))
key = lambda r: (r['task'], r['rep'])
D = collections.defaultdict(dict)
for r in R: D[r['split']].setdefault(r['pol'], {})[key(r)] = r
def med(v): v = [x for x in v if x is not None]; return round(st.median(v), 3) if v else None
def q(v, p): v = sorted(x for x in v if x is not None); return round(v[int(p * (len(v) - 1))], 3) if v else None
dev = D['dev']; pols = ['P6', 'P16', 'P17', 'P18', 'P19']
print('== 1. dev420 结局（1 m）与碰撞率')
for p in pols:
    c = collections.Counter(r['out'] for r in dev[p].values()); print(' ', p, dict(c), '碰撞率 %.1f%%' % (100 * c['C'] / 420))
print('== 2. 配对转移（对照 → 处理）')
for a, b in (('P18', 'P16'), ('P19', 'P17'), ('P6', 'P18'), ('P6', 'P19')):
    m = collections.Counter((dev[a][k]['out'], dev[b][k]['out']) for k in dev[a]); print(' ', a, '→', b, dict(sorted(m.items())))
print('== 3. 碰撞的一致性（同一条件 task×repeat，五个策略）')
ks = list(dev['P6']); nC = collections.Counter(sum(dev[p][k]['out'] == 'C' for p in pols) for k in ks)
print('  五个策略中碰撞的个数 → 条件数：', dict(sorted(nC.items())))
tasks = collections.defaultdict(list)
for k in ks: tasks[k[0]].append(k)
tc = [sum(dev[p][k]['out'] == 'C' for p in pols for k in tasks[t]) / (5 * len(tasks[t])) for t in tasks]
print('  按任务（%d 个）的碰撞比例分布：0 → %d，(0,0.5) → %d，[0.5,1) → %d，=1 → %d' % (len(tc), sum(x == 0 for x in tc), sum(0 < x < .5 for x in tc), sum(.5 <= x < 1 for x in tc), sum(x == 1 for x in tc)))
rc = collections.defaultdict(lambda: [0, 0])
for p in pols:
    for r in dev[p].values(): rc[r['role']][0] += r['out'] == 'C'; rc[r['role']][1] += 1
print('  按角色的碰撞率（五策略合计）：', {k: '%.0f%%' % (100 * a / b) for k, (a, b) in sorted(rc.items())})
print('== 4. 碰撞前规划提前量（碰撞前第 2 个决策规划已穿过被撞障碍的比例）')
for p in pols:
    C = [r for r in dev[p].values() if r['out'] == 'C']; print('  %s：lead≥1 %.0f%%，lead≥2 %.0f%%（n=%d）' % (p, 100 * sum(r['lead'] >= 1 for r in C) / len(C), 100 * sum(r['lead'] >= 2 for r in C) / len(C), len(C)))
print('== 5. 速度与接近项（全部 dev 回合）')
for p in pols:
    V = list(dev[p].values())
    print('  %s：分段速度中位 %s，障碍 2.5 m 内 %s；每回合 approach_cbf(w=2) 合计中位 %s，10%% 分位 %s；非零决策比例中位 %s' % (
        p, med([r['v_med'] for r in V]), med([r['v_near_med'] for r in V]), med([r['cbf_sum'] for r in V]), q([r['cbf_sum'] for r in V], .1), med([r['cbf_nonzero'] for r in V])))
print('== 6. 对照成功、处理超时的回合（S→T）：处理臂与对照臂同一条件对比')
for a, b in (('P18', 'P16'), ('P19', 'P17')):
    K = [k for k in dev[a] if dev[a][k]['out'] == 'S' and dev[b][k]['out'] == 'T']
    X, Y = [dev[b][k] for k in K], [dev[a][k] for k in K]
    print('  %s→%s：%d 个' % (a, b, len(K)))
    for nm, f in (('进度 1−最近距离/初始距离', 'prog'), ('最近距目标 m', 'mind'), ('停滞决策比例（位移<0.15 m）', 'stall_frac'), ('最后 10 决策停滞比例', 'stall_last10'),
                  ('分段速度中位', 'v_med'), ('终点净空 m', 'final_clear'), ('最小净空 m', 'clear_min'), ('approach_cbf 合计', 'cbf_sum'), ('初始距离 D0', 'D0')):
        print('    %-26s 处理 %s | 对照 %s' % (nm, med([x[f] for x in X]), med([y[f] for y in Y])))
    print('    处理臂终点净空 <1 m 的比例 %.0f%%，<2.2 m %.0f%%；最后 10 决策停滞 ≥50%% 的比例 %.0f%%' % (
        100 * sum(x['final_clear'] < 1 for x in X) / len(X), 100 * sum(x['final_clear'] < 2.2 for x in X) / len(X), 100 * sum(x['stall_last10'] >= .5 for x in X) / len(X)))
    print('    按角色：', dict(collections.Counter(x['role'] for x in X)))
print('== 7. 全部超时回合（处理臂合计 vs 对照臂合计）')
for grp in (('P16', 'P17'), ('P18', 'P19')):
    X = [r for p in grp for r in dev[p].values() if r['out'] == 'T']
    print('  %s：%d 个；进度中位 %s；停滞比例中位 %s；最后10决策停滞中位 %s；终点净空中位 %s；速度中位 %s' % (
        '+'.join(grp), len(X), med([r['prog'] for r in X]), med([r['stall_frac'] for r in X]), med([r['stall_last10'] for r in X]), med([r['final_clear'] for r in X]), med([r['v_med'] for r in X])))
print('== 8. 成功回合的效率（处理 vs 对照，各自成功回合）')
for p in pols:
    S = [r for r in dev[p].values() if r['out'] == 'S']
    print('  %s：成功 %d，到 1 m 用时中位 %s s，决策数中位 %s，速度中位 %s' % (p, len(S), med([r['t1'] for r in S]), med([r['n'] for r in S]), med([r['v_med'] for r in S])))
print('== 9. 分层：目标高度 >3 m / ≤3 m 的 1 m 成功率')
for p in pols:
    hi = [r for r in dev[p].values() if r['goal_z'] > 3]; lo = [r for r in dev[p].values() if r['goal_z'] <= 3]
    print('  %s：>3 m %d/%d，≤3 m %d/%d' % (p, sum(r['out'] == 'S' for r in hi), len(hi), sum(r['out'] == 'S' for r in lo), len(lo)))
