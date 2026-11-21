"""稀疏类中 UAV-iDP3 按任务统计失败的任务，逐任务列出，并从执行轨迹分析失败位置（只读）。
运行：python3 -I sparse_p0_fail.py <rows.json> <输出 csv> <UAV-iDP3 traces 目录 ...>
每回合：最近目标距离（near）、最近时刻的水平误差与高度误差（目标 − 无人机）、终点到目标距离、起终点高度差、结局。"""
import json, sys, glob, math, csv, collections
ROWS, OUT, *TR = sys.argv[1:]
R = json.load(open(ROWS)); EXC = set(json.load(open('研究报告/analysis_20261108/oprime/exclusions.json'))['tasks'])
ok = lambda r: r['out'] == 'reached' or r['near'] < 1
S = collections.defaultdict(list)
for r in R:
    if r['policy'] == 'P0' and r['cat'] == '稀疏' and r['task'] not in EXC: S[r['task']].append(r)
fail = [t for t, v in S.items() if sum(map(ok, v)) < 3]
tr = {}
for D in TR:
    for fn in glob.glob(f'{D}/*.jsonl'):
        L = [json.loads(l) for l in open(fn)]; s0 = L[0]
        if s0['task_id'] in fail: tr[(s0['task_id'], int(s0['repeat']))] = L
out = []
for t in fail:
    for r in S[t]:
        L = tr[(t, int(r['rep']))]; T = L[0]['task']; g = T['goal_pos']; s = T['start_pos']
        pts = []
        for x in L[1:]:
            if x.get('type') == 'transition': pts += x['executed_path']
        i = min(range(len(pts)), key=lambda i: math.dist(pts[i], g)); p = pts[i]; e = pts[-1]
        out.append(dict(task=t[:12], world=L[0]['world_id'].replace('routeA_rl_v1__', ''), rep=r['rep'], out='成功' if ok(r) else ('碰撞' if r['out'] == 'collision' else '超时'),
                        d0=round(math.dist(s, g), 1), dz_task=round(g[2] - s[2], 2), near=round(math.dist(p, g), 2), dxy_near=round(math.hypot(g[0] - p[0], g[1] - p[1]), 2),
                        dz_near=round(g[2] - p[2], 2), d_end=round(math.dist(e, g), 2), dz_end=round(g[2] - e[2], 2), z_goal=round(g[2], 2)))
with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(len(fail), len(out))
