"""只读：F9 阶段 A2（P35）独立复算、配对与吸收强度诊断。
用法：python3 -I stageA2_recount.py <阶段A2回传包根目录 routea_f9_stageA2_return_20261124>
数据：measure/{P35_u000264,P29_u000264,P6_u000256}_conditions.csv；run/P35/gate.json、f9_prefill.json、f9_collect_*.json、metrics_update_*.json。
输出：到达/碰撞/超时与 D 重算；门槛重算（v1_3 表 + A2 §二）；逐条件配对；49/36 分层；
      每轮 20 次提交上教师层的实际梯度比（f8_keep_diagnostics.ratio = λ_g·‖g_层‖/‖g_PPO‖）、教师层训练损失、总梯度是否裁剪。"""
import csv, json, os, sys, glob, collections, statistics as st
from fractions import Fraction
R = sys.argv[1]
def load(n):
    rows = list(csv.DictReader(open(os.path.join(R, 'measure', f'{n}_conditions.csv'), encoding='utf-8-sig')))
    return {(r['task_id'], int(r['repeat'])): r for r in rows}
T, C, P = load('P35_u000264'), load('P29_u000264'), load('P6_u000256')
assert set(T) == set(C) == set(P) and len(T) == 425
def summ(n, X):
    c = collections.Counter(r['outcome'] for r in X.values())
    dn = sum(int(r['D_num']) for r in X.values()); dd = sum(int(r['D_den']) for r in X.values())
    print(f'{n}: 到达 {c["reached"]} 碰撞 {c["collision"]} 超时 {c["time_limit"]} | D = {dn}/{dd} = {dn/dd:.5f}')
    return Fraction(dn, dd), c['reached']
Dt, at = summ('P35 T@u264', T); Dc, ac = summ('P29 C@u264', C); summ('P6@u256', P)
g = json.load(open(os.path.join(R, 'run', 'P35', 'gate.json')))
dok = Dt <= Fraction(7, 10) * Dc; lok = at >= ac - 20; r = g['r']
dec = ('pass' if lok else 'behavior_changed_closed_loop_worse') if dok else ('pending_r' if r is None else ('restart' if r > .5 else 'fitted_without_student_change'))
print(f'D_T/D_C = {float(Dt/Dc):.4f}；D 达标 {dok}；闭环达标 {lok}；r = {r}；按 v1_3 表复算判定 = {dec}；gate.json = {g["decision"]}；r 分类 {g["r_by_intervention"]}')
def pair(a, b, A, B):
    gain = sum(1 for k in A if A[k]['outcome'] == 'reached' and B[k]['outcome'] != 'reached')
    lost = sum(1 for k in A if A[k]['outcome'] != 'reached' and B[k]['outcome'] == 'reached')
    diff = sum(1 for k in A if A[k]['outcome'] != B[k]['outcome'])
    print(f'{a} 对 {b}：新增 {gain}，流失 {lost}，结局不同 {diff}/425')
pair('T', 'C', T, C); pair('T', 'P6', T, P); pair('C', 'P6', C, P)
cnt = collections.Counter(k[0] for k, v in P.items() if v['outcome'] == 'reached'); solved = {t for t, v in cnt.items() if v >= 3}
tasks = {k[0] for k in T}; unsolved = tasks - solved
for lab, S in (('已解 %d' % len(solved), solved), ('未解 %d' % len(unsolved), unsolved)):
    for n, X in (('T', T), ('C', C), ('P6', P)):
        sub = [r for k, r in X.items() if k[0] in S]; c = collections.Counter(r['outcome'] for r in sub)
        dn = sum(int(r['D_num']) for r in sub); dd = sum(int(r['D_den']) for r in sub)
        solv = sum(1 for t in S if sum(X[(t, i)]['outcome'] == 'reached' for i in range(1, 6)) >= 3)
        print(f'  [{lab}] {n}: 到达 {c["reached"]} 碰撞 {c["collision"]} 超时 {c["time_limit"]} | ≥3/5 任务 {solv} | D {dn/dd:.4f}')
pf = json.load(open(os.path.join(R, 'run', 'P35', 'f9_prefill.json'))); tot = pf['accepted']; tr = pf['transitions']
for f in sorted(glob.glob(os.path.join(R, 'run', 'P35', 'f9_collect_*.json'))):
    d = json.load(open(f)); tot += d['accepted']; tr += d['transitions']
print(f'供给：预填 {pf["accepted"]}，累计入库（训练）{tot}，转移 {tr}，每 1000 条 {1000*tot/tr:.1f}')
print('轮次 | 教师层实际梯度比 中位 [最小, 最大] | 教师层训练损失 首次/末次提交 | 总梯度被裁剪的提交数')
for f in sorted(glob.glob(os.path.join(R, 'run', 'P35', 'metrics_update_*.json'))):
    m = json.load(open(f)); us = [u['pre_update'] for u in m['updates']]
    rat = [u['f8_keep_diagnostics']['ratio'] for u in us]; lo = [u['f8_keep_diagnostics']['keep_loss'] for u in us]
    clip = sum(bool(u['actor_grad_clipped']) for u in us)
    print(f'{os.path.basename(f)[15:21]} | {st.median(rat):.3f} [{min(rat):.3f}, {max(rat):.3f}] | {lo[0]:.4f} / {lo[-1]:.4f} | {clip}/{len(us)}')
