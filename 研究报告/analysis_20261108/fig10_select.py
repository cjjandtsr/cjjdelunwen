"""图10 选例（事先规则，总交接 v1_0 §4.5）：在 O′ 上，取同一任务同一次重复中 BC 超时或碰撞、本文方法到达的配对；
每类按 world_id 字典序取第一个世界，世界内按 task_id、repeat 字典序取第一个。另报告 Codex 候选在两策略下的结局。
运行：python3 -I fig10_select.py <O′分析脚本的行导出 rows.json>"""
import json, sys, collections
rows = json.load(open(sys.argv[1]))
idx = {(r['policy'], r['task'], r['rep']): r for r in rows}
out = {}
for c in ['稀疏', '适中', '密集']:
    cand = sorted((r['world'], r['task'], r['rep']) for r in rows if r['policy'] == 'P6' and r['cat'] == c and r['out'] == 'reached'
                  and idx[('P0', r['task'], r['rep'])]['out'] in ('time_limit', 'collision'))
    w, t, k = cand[0]
    out[c] = dict(world=w, task=t, repeat=k, part=idx[('P6', t, k)]['part'], P0=idx[('P0', t, k)]['out'], n_candidates=len(cand))
print(json.dumps(out, ensure_ascii=False, indent=1))
for t in sys.argv[2:]:
    for k in [1]:
        print(t[:10], {p: idx[(p, t, k)]['out'] for p in ('P0', 'P6')}, idx[('P0', t, k)]['cat'])
