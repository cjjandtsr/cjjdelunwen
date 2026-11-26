"""只读：F9 阶段 A 独立复算与配对分析。
用法：python3 -I stageA_recount.py <阶段A回传包根目录 routea_f9_stageA_return_20261122>
数据：measure/{P28_u000264,P29_u000264,P6_u000256}_conditions.csv（训练库 85×5，确定性、不带引导；outcome 为 1 m 口径，D_num/D_den 为影子引导需求计数）；
      measure/task_strata.json；P28/f9_prefill.json、f9_collect_*.json、gate.json。
输出：各策略到达/碰撞/超时与 D（重算）；门槛重算；逐条件配对转移（T 对 C、T 对 P6、C 对 P6）；按 49/36 分层的条件级到达与碰撞；
      每回合 D 的配对差；教师供给逐轮。"""
import csv, json, os, sys, glob, collections
from fractions import Fraction
R = sys.argv[1]
def load(n):
    rows = list(csv.DictReader(open(os.path.join(R, 'measure', f'{n}_conditions.csv'), encoding='utf-8-sig')))
    return {(r['task_id'], int(r['repeat'])): r for r in rows}
T, C, P = load('P28_u000264'), load('P29_u000264'), load('P6_u000256')
assert set(T) == set(C) == set(P) and len(T) == 425
def summ(n, X):
    c = collections.Counter(r['outcome'] for r in X.values())
    dn = sum(int(r['D_num']) for r in X.values()); dd = sum(int(r['D_den']) for r in X.values())
    print(f'{n}: 到达 {c["reached"]} 碰撞 {c["collision"]} 超时 {c["time_limit"]} 其他 {425-c["reached"]-c["collision"]-c["time_limit"]} | D = {dn}/{dd} = {dn/dd:.5f}')
    return dn, dd, c['reached']
tn, td, ta = summ('P28 T@u264', T); cn, cd, ca = summ('P29 C@u264', C); pn, pd, pa = summ('P6@u256', P)
Dt, Dc = Fraction(tn, td), Fraction(cn, cd)
print(f'D_T/D_C = {float(Dt/Dc):.4f}；D 达标（≤0.7）：{Dt <= Fraction(7,10)*Dc}；闭环达标（T ≥ C−20）：{ta >= ca-20}')
g = json.load(open(os.path.join(R, 'P28', 'gate.json'))); print('gate.json 判定：', g['decision'], '；r =', g['r'])
def pair(a, b, A, B):
    m = collections.Counter((A[k]['outcome'], B[k]['outcome']) for k in A)
    gain = sum(v for (x, y), v in m.items() if x == 'reached' and y != 'reached')
    lost = sum(v for (x, y), v in m.items() if x != 'reached' and y == 'reached')
    flips = sum(v for (x, y), v in m.items() if x != y)
    print(f'{a} 对 {b}：{a} 到达而 {b} 未到达 {gain}，反之 {lost}，结局不同 {flips}/425；明细 {dict(m)}')
pair('T', 'C', T, C); pair('T', 'P6', T, P); pair('C', 'P6', C, P)
st = json.load(open(os.path.join(R, 'measure', 'task_strata.json')))
print('task_strata 键：', list(st.keys())[:10])
solved = set(st.get('P6_solved_tasks') or st.get('solved') or st.get('P6_solved', []))
if not solved:
    # 回退：由 P6 原迹按 ≥3/5 重算
    cnt = collections.Counter(k[0] for k, r in P.items() if r['outcome'] == 'reached'); solved = {t for t, v in cnt.items() if v >= 3}
tasks = {k[0] for k in T}; unsolved = tasks - solved
print(f'P6 ≥3/5 已解任务 {len(solved)}，未解 {len(unsolved)}（共 {len(tasks)}）')
for lab, S in (('已解 49', solved), ('未解 36', unsolved)):
    for n, X in (('T', T), ('C', C), ('P6', P)):
        sub = [r for k, r in X.items() if k[0] in S]; c = collections.Counter(r['outcome'] for r in sub)
        dn = sum(int(r['D_num']) for r in sub); dd = sum(int(r['D_den']) for r in sub)
        solv = sum(1 for t in S if sum(X[(t, i)]['outcome'] == 'reached' for i in range(1, 6)) >= 3)
        print(f'  [{lab}] {n}: 条件 {len(sub)} 到达 {c["reached"]} 碰撞 {c["collision"]} 超时 {c["time_limit"]} | ≥3/5 任务 {solv} | D {dd and dn/dd:.4f}')
# 每回合 D（影子需求率）配对：只比较两边都为碰撞或都到达的条件之外的全部条件
import statistics
dT = [int(T[k]['D_num'])/max(int(T[k]['D_den']),1) for k in T]; dC = [int(C[k]['D_num'])/max(int(C[k]['D_den']),1) for k in T]
diff = [a-b for a, b in zip(dT, dC)]
print(f'每回合 D 的配对差 T−C：中位 {statistics.median(diff):.4f}，均值 {statistics.mean(diff):.4f}，T 更低的条件 {sum(d<0 for d in diff)}，更高 {sum(d>0 for d in diff)}，相等 {sum(d==0 for d in diff)}')
pf = json.load(open(os.path.join(R, 'P28', 'f9_prefill.json')))
print('预填：', pf)
tot_tr = pf['transitions']; tot_acc = pf['accepted']
for f in sorted(glob.glob(os.path.join(R, 'P28', 'f9_collect_*.json'))):
    d = json.load(open(f)); tot_tr += d['transitions']; tot_acc += d['accepted']
    print(os.path.basename(f), {k: d[k] for k in ('transitions', 'triggered', 'effective', 'accepted', 'heldout', 'buffer')})
print(f'教师供给合计：转移 {tot_tr}，入库（训练）{tot_acc}，每 1000 条转移入库 {1000*tot_acc/tot_tr:.1f} 个')
