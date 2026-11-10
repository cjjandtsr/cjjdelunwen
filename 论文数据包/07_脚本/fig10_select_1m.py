"""图6（典型轨迹）选例，主标准半径 RAD（1.5 m，用户 11-09；原为 1 m）：同一任务同一次重复中 BC 未在碰撞前进入目标 RAD、
本文方法进入目标 RAD；去除 oprime/exclusions.json 中的任务；每类按 world_id、task_id、repeat 字典序取第一个。运行：python3 -I fig10_select_1m.py <oprime/rows.json> <oprime/exclusions.json> [RAD]"""
import json, sys
EXC = set(json.load(open(sys.argv[2]))['tasks']); RAD = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
R = [r for r in json.load(open(sys.argv[1])) if r['task'] not in EXC]; idx = {(r['policy'], r['task'], r['rep']): r for r in R}
ok = lambda r: r['out'] == 'reached' or r['near'] < RAD
for c in ['稀疏', '适中', '密集']:
    cand = sorted((r['world'], r['task'], r['rep']) for r in R if r['policy'] == 'P6' and r['cat'] == c and ok(r) and not ok(idx[('P0', r['task'], r['rep'])]))
    w, t, k = cand[0]; b = idx[('P0', t, k)]; o = idx[('P6', t, k)]
    print(c, w.split('__rl_test__')[-1], t, k, 'BC', b['out'], round(b['near'], 2), '本文', o['out'], round(o['near'], 2), '候选', len(cand))
