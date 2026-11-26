"""只读：核对 P36（阶段 A2 重开）是否按预先设想的条件执行，并与 P35 对照。
用法：python3 -I p36_condition_check.py <P36 回传包根目录> <P35 回传包根目录>
核对项（来源：研究报告/2026-11-24_F9阶段A2结果分析与重开裁决_v1_0.md §三）：
  1 编号/seed/教师采样器/引导设置/系数覆盖值，且未重新标定；
  2 一切回到 P6@u256：父策略、从 u257 起、预填与 P35 逐项相同（同 seed、同父策略时应完全相同）、留出编号从 0；
  3 实际生效系数：逐提交 f8_keep_diagnostics.coefficient 是否等于覆盖值；实际梯度比是否约为 P35 的 3 倍；裁剪；
  4 首轮隔离；5 测量复用条件（P29/P6 state 与差异集合）；6 门槛复算；7 测量本身（P36 条件数、结局与 D 重算）。"""
import csv, json, os, sys, glob, collections, statistics as st
from fractions import Fraction
R36, R35 = sys.argv[1], sys.argv[2]
J = lambda *p: json.load(open(os.path.join(*p)))
COEF = 0.2484614509805812; BASE = 0.08282048366019373
cfg = open(os.path.join(R36, 'run/P36/config.yaml')).read()
conf = J(R36, 'run/P36/configured.json'); lin = J(R36, 'run/P36/fork_lineage.json')
def grep(txt, keys): return {k: [l.strip() for l in txt.splitlines() if k in l][:3] for k in keys}
print('1 配置片段：', json.dumps(grep(cfg, ['teacher_task_sampler', 'coefficient_override', 'd_safe', 'eta', 'updates_per_step', 'seed:', 'attempt', 'trial_id']), ensure_ascii=False))
print('  calibration 文件存在：', os.path.exists(os.path.join(R36, 'run/P36/f9_calibration.json')))
print('  fork_lineage：', json.dumps(lin, ensure_ascii=False)[:600])
pf36, pf35 = J(R36, 'run/P36/f9_prefill.json'), J(R35, 'run/P35/f9_prefill.json')
keys = [k for k in pf36 if not isinstance(pf36[k], (dict, list))]
print('2 预填 P36 对 P35：', {k: (pf36[k], pf35.get(k)) for k in keys})
same = {k: pf36[k] == pf35.get(k) for k in pf36 if k not in ('seconds', 'elapsed_seconds', 'wall_seconds')}
print('  预填字段逐项相同（不含耗时）：', all(same.values()), [k for k, v in same.items() if not v])
c36 = J(R36, 'run/P36/f9_collect_000257.json'); c35 = J(R35, 'run/P35/f9_collect_000257.json')
print('  u257 教师采集 P36/P35：', {k: (c36[k], c35[k]) for k in ('transitions', 'accepted', 'heldout', 'buffer')})
print('3 逐轮：实际系数（唯一值）| 梯度比中位 P36 / P35 | 教师层训练损失首/末 P36 | 裁剪')
for u in range(257, 265):
    m36 = J(R36, f'run/P36/metrics_update_{u:06d}.json')['updates']; m35 = J(R35, f'run/P35/metrics_update_{u:06d}.json')['updates']
    co = sorted({round(x['pre_update']['f8_keep_diagnostics']['coefficient'], 12) for x in m36})
    r36 = st.median(x['pre_update']['f8_keep_diagnostics']['ratio'] for x in m36); r35 = st.median(x['pre_update']['f8_keep_diagnostics']['ratio'] for x in m35)
    lo = [x['pre_update']['f8_keep_diagnostics']['keep_loss'] for x in m36]
    cl = sum(bool(x['pre_update']['actor_grad_clipped']) for x in m36)
    print(f'  {u} | {co} | {r36:.3f} / {r35:.3f}（×{r36/r35:.2f}）| {lo[0]:.4f} / {lo[-1]:.4f} | {cl}/20')
iso = glob.glob(os.path.join(R36, 'isolation', '*.json'))
for f in iso:
    d = J(f); print('4 隔离：', os.path.basename(f), {k: d[k] for k in d if not isinstance(d[k], (dict, list))})
er = J(R36, 'measure/eval_refs.json'); print('5 eval_refs：', json.dumps(er, ensure_ascii=False)[:1200])
g = J(R36, 'run/P36/gate.json'); print('6 gate：', json.dumps(g, ensure_ascii=False))
def load(n):
    rows = list(csv.DictReader(open(os.path.join(R36, 'measure', f'{n}_conditions.csv'), encoding='utf-8-sig')))
    return {(r['task_id'], int(r['repeat'])): r for r in rows}
T, C, P = load('P36_u000264'), load('P29_u000264'), load('P6_u000256')
c35csv = {(r['task_id'], int(r['repeat'])): r for r in csv.DictReader(open(os.path.join(R35, 'measure', 'P29_u000264_conditions.csv'), encoding='utf-8-sig'))}
print('7 P36 条件数', len(T), '；P29 测量与 P35 包中逐字段相同：', all(C[k] == c35csv[k] for k in C))
for n, X in (('P36', T), ('P29', C), ('P6', P)):
    c = collections.Counter(r['outcome'] for r in X.values()); dn = sum(int(r['D_num']) for r in X.values()); dd = sum(int(r['D_den']) for r in X.values())
    print(f'  {n}: 到达 {c["reached"]} 碰撞 {c["collision"]} 超时 {c["time_limit"]} D {dn}/{dd} = {dn/dd:.6f}')
Dt = Fraction(sum(int(r['D_num']) for r in T.values()), sum(int(r['D_den']) for r in T.values())); Dc = Fraction(1650, 8455)
at = sum(r['outcome'] == 'reached' for r in T.values())
dec = ('pass' if at >= 236 else 'behavior_changed_closed_loop_worse') if Dt <= Fraction(7, 10) * Dc else ('stop_after_restart' if g['r'] > .5 else 'fitted_without_student_change')
print(f'  复算判定（重开后）：{dec}；D 比 {float(Dt/Dc):.4f}')
gain = sum(1 for k in T if T[k]['outcome'] == 'reached' and C[k]['outcome'] != 'reached'); lost = sum(1 for k in T if T[k]['outcome'] != 'reached' and C[k]['outcome'] == 'reached')
print(f'  T 对 C：新增 {gain} 流失 {lost}')
pf = pf36['accepted']; tot = pf + sum(J(f)['accepted'] for f in glob.glob(os.path.join(R36, 'run/P36/f9_collect_*.json')))
print('  供给累计：', tot)
