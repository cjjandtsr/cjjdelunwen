#!/usr/bin/env python3
"""G16 补充：训练外集合 O（test12+扩展集，540 回合）上到达回合的路径效率中位数。
路径效率 = 起点到目标的直线距离 / 实际执行路径长度（trajectory_metrics.path_length_m），仅统计 done_reason=reached。
用法: python3 -I g16_patheff.py <G16 数据包目录> > g16/patheff.csv
"""
import json, math, statistics, sys, os
G = sys.argv[1]
D0 = {}
for b in ['test', 'ext']:
    for t in json.load(open(os.path.join(G, 'banks', f'{b}.json')))['tasks']:
        D0[t['task_id']] = math.dist(t['payload']['start_pos'], t['payload']['goal_pos'])
CAT = {'zero': 'Sparse', 'low': 'Moderate', 'high': 'Dense'}
src = {'P0': 'reference_O/{s}_bc.json', 'P4': 'reference_O/{s}_P4.json', 'P6': 'reference_O/{s}_P6.json',
       'P9': '{s}_P9_episode_package.json', 'P11': '{s}_P11_episode_package.json'}
print('policy,class,n_reached,path_eff_median')
for p, pat in src.items():
    e = {'All': [], 'Sparse': [], 'Moderate': [], 'Dense': []}
    for s in ['test', 'ext']:
        for r in json.load(open(os.path.join(G, pat.format(s=s))))['records']:
            if r['done_reason'] == 'reached':
                v = D0[r['task_id']] / r['trajectory_metrics']['path_length_m']
                e['All'].append(v); e[CAT[r['category']]].append(v)
    for k, v in e.items():
        print(f"{p},{k},{len(v)},{statistics.median(v):.3f}" if v else f"{p},{k},0,")
