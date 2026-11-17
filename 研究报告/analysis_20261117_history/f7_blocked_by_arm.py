"""只读：F7 四臂与 P6@u256（#E2，1 m）在 dev420 直线被挡 33 个任务上的结果，用作 F8 判据的运行间噪声参照。
用法：python3 -I f7_blocked_by_arm.py <f7_episodes.json（f7_episodes.py 输出）> <blocked_tasks_dev420.json>"""
import json, sys, collections
R = json.load(open(sys.argv[1])); bl = set(json.load(open(sys.argv[2])))
c = collections.defaultdict(collections.Counter); t = collections.defaultdict(lambda: collections.defaultdict(int))
for r in R:
    if r['split'] != 'dev': continue
    k = '被挡' if r['task'] in bl else '可通过'
    c[(r['pol'], k)][r['out']] += 1
    if k == '被挡': t[r['pol']][r['task']] += r['out'] == 'S'
for k in sorted(c): print(k, dict(c[k]))
for p in sorted(t): print(p, '被挡任务：至少成功 1 次', sum(v > 0 for v in t[p].values()), '；≥3/5', sum(v >= 3 for v in t[p].values()))
