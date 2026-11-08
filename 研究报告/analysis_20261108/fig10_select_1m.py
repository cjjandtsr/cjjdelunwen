"""图（典型轨迹）选例，1 m 标准（用户 11-08 改为主标准后重选）：同一任务同一次重复中 BC 未在碰撞前进入目标 1 m、
本文方法进入目标 1 m；每类按 world_id、task_id、repeat 字典序取第一个。运行：python3 -I fig10_select_1m.py <oprime/rows.json>"""
import json, sys
R = json.load(open(sys.argv[1])); idx = {(r['policy'], r['task'], r['rep']): r for r in R}
ok = lambda r: r['out'] == 'reached' or r['near'] < 1.0
for c in ['稀疏', '适中', '密集']:
    cand = sorted((r['world'], r['task'], r['rep']) for r in R if r['policy'] == 'P6' and r['cat'] == c and ok(r) and not ok(idx[('P0', r['task'], r['rep'])]))
    w, t, k = cand[0]; b = idx[('P0', t, k)]; o = idx[('P6', t, k)]
    print(c, w.split('__rl_test__')[-1], t, k, 'BC', b['out'], round(b['near'], 2), '本文', o['out'], round(o['near'], 2), '候选', len(cand))
