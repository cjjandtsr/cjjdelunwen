#!/usr/bin/env python3
"""补充材料 S3：任务分类界限的敏感性（训练外世界，论文线数据 P0、P2、P4、P6）。

分类以航线两侧 1.0 m 范围内障碍占据体积比例 rho（记录字段 rho_1_0）为准：rho = 0 为稀疏；
0 < rho <= t 为适中；rho > t 为密集。正文 t = 0.04623（训练世界任务中位数）。此处另取 0.5t 与 2t。
用法：python3 -I s3_threshold.py <G3数据包目录> <C5数据包目录> > s3/s3_threshold.csv
"""
import json, os, sys

G3, C5 = sys.argv[1], sys.argv[2]
FILES = [(G3, {'P0': 'eval_test_bc_package.json', 'P2': 'eval_test_P2_package.json', 'P4': 'eval_test_P4_package.json', 'P6': 'eval_test_P6_package.json'}),
         (C5, {'P0': 'bc_episode_package.json', 'P2': 'P2_episode_package.json', 'P4': 'P4_episode_package.json', 'P6': 'P6_episode_package.json'})]
rec = {p: [] for p in ['P0', 'P2', 'P4', 'P6']}
for root, fs in FILES:
    for p, f in fs.items():
        rec[p] += json.load(open(os.path.join(root, f)))['records']
T0 = 0.04623
# check: the main-text threshold reproduces the frozen categories
for r in rec['P0']:
    c = 'zero' if r['rho_1_0'] == 0 else ('low' if r['rho_1_0'] <= T0 else 'high')
    assert c == r['category'], (r['task_id'], r['rho_1_0'], r['category'])
print('界限倍数,界限,类别,回合,P0到达,P2到达,P4到达,P6到达,P6−P0(百分点)')
for k in (0.5, 1.0, 2.0):
    t = T0 * k
    for cls in ('适中', '密集'):
        sel = lambda r: r['rho_1_0'] > 0 and ((r['rho_1_0'] <= t) == (cls == '适中'))
        n = sum(sel(r) for r in rec['P0'])
        a = {p: sum(sel(r) and r['done_reason'] == 'reached' for r in rec[p]) for p in rec}
        print(f"{k},{t:.5f},{cls},{n},{a['P0']},{a['P2']},{a['P4']},{a['P6']},{100 * (a['P6'] - a['P0']) / n:.1f}")
