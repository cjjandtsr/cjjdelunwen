"""只读：独立复算 F9 第 0 步六组的选参量与描述量。
用法：python3 -I step0_recount.py <run 目录（含 step0/g0..g5/result.json 与 selection.json）>
口径：按方案 v1_3 §1.1—§1.2 与第 0 步选法，以逐条件 rows 为准重算，不使用 result.json 顶层汇总字段：
  eligible = 成功回合（reached）中 d* 之前、delta_exec ≥ 0.05 m 的决策（以 rows[*].eligible_decisions 为入库清单，另用 delta_exec 序列核对阈值）；
  eligible_failed = 其中 P6 在该条件失败者；first = 其中首次干预者。
另报：1 m 到达数、P6 失败条件上的到达数、触发（delta_exec>0）与有效纠偏（≥0.05）决策数、入库决策 delta_exec 的分位数。"""
import json, os, sys
import numpy as np
R = sys.argv[1]
sel = json.load(open(os.path.join(R, 'selection.json')))
out = []
for g in range(6):
    d = json.load(open(os.path.join(R, 'step0', f'g{g}', 'result.json')))
    rows = d['rows']; assert len(rows) == d['conditions'] == 425
    reach = sum(bool(r['reached']) for r in rows)
    failed = [r for r in rows if r['baseline_failed']]
    reach_f = sum(bool(r['reached']) for r in failed)
    el = [e for r in rows for e in r.get('eligible_decisions', [])]
    # 核对：入库决策只来自成功回合，且 delta_exec ≥ 0.05
    assert all(r['reached'] for r in rows if r.get('eligible_decisions')), 'eligible from failed episode'
    assert all(e['delta_exec'] >= 0.05 for e in el), 'eligible below threshold'
    trig = sum(sum(1 for x in r['delta_exec'] if x > 0) for r in rows)
    eff = sum(sum(1 for x in r['delta_exec'] if x >= 0.05) for r in rows)
    ef = sum(e['P6_condition_failed'] for e in el)
    first = sum(e['intervention'] == 'first_intervention' for e in el)
    first_f = sum(e['intervention'] == 'first_intervention' and e['P6_condition_failed'] for e in el)
    dx = np.array([e['delta_exec'] for e in el])
    s = d['setting']
    out.append((g, s['d_safe'], s['eta'], s['M'], reach, len(failed), reach_f, trig, eff, len(el), ef, first, first_f, d['eligible_all'], d['eligible_failed'],
                np.percentile(dx, 50), np.percentile(dx, 90), dx.max()))
print('组 d_safe eta M | 到达/425 | P6失败条件数 其中到达 | delta>0 决策 | ≥0.05 决策 | 可入库 其中P6失败 首次干预 首次且P6失败 | 汇总字段(全/失败) | 入库delta 中位 p90 最大')
for o in out:
    print(f'g{o[0]} {o[1]} {o[2]} {o[3]} | {o[4]} | {o[5]} {o[6]} | {o[7]} | {o[8]} | {o[9]} {o[10]} {o[11]} {o[12]} | {o[13]}/{o[14]} | {o[15]:.3f} {o[16]:.3f} {o[17]:.3f}')
best = sorted(out, key=lambda o: (-o[10], -o[9], o[1], o[2]))[0]
print('按选法复算的选定组：', f'g{best[0]}', '；selection.json 选定：', sel['setting'], '；一致' if (best[1], best[2], best[3]) == (sel['setting']['d_safe'], sel['setting']['eta'], sel['setting']['M']) else '；不一致')
