#!/usr/bin/env python3
"""第 4 章补充统计（只用论文线数据：P0、P2、P4、P6）。

数据：
  G3 数据包（test12）：eval_test_{bc,P2,P4,P6}_package.json，banks/test12.json
  C5 数据包（扩展集 run02）：{bc,P2,P4,P6}_episode_package.json，bank.json
训练外集合 O = test12 ∪ 扩展集（540 回合/策略）。

输出（写到 <OUT>/）：
  o_class.csv     类别 × 策略：回合数、到达、碰撞、超时
  o_timeouts.csv  策略：超时数、最近目标距离 <2 m、<1 m、中位数
  o_behavior.csv  类别 × 策略：到达回合的路径效率、最大横向偏离、高度范围、回退距离、飞行时间中位数
用法：python3 -I ch4_paperline.py <G3数据包目录> <C5数据包目录> <OUT>
"""
import csv, json, math, os, statistics, sys

G3, C5, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
CAT = {'zero': '稀疏', 'low': '适中', 'high': '密集'}
POL = ['P0', 'P2', 'P4', 'P6']
FILES = {
    'test': {'P0': 'eval_test_bc_package.json', 'P2': 'eval_test_P2_package.json',
             'P4': 'eval_test_P4_package.json', 'P6': 'eval_test_P6_package.json'},
    'ext': {'P0': 'bc_episode_package.json', 'P2': 'P2_episode_package.json',
            'P4': 'P4_episode_package.json', 'P6': 'P6_episode_package.json'},
}
D0 = {}
for path in (os.path.join(G3, 'banks', 'test12.json'), os.path.join(C5, 'bank.json')):
    for t in json.load(open(path))['tasks']:
        D0[t['task_id']] = math.dist(t['payload']['start_pos'], t['payload']['goal_pos'])

rec = {p: [] for p in POL}
for split, root in (('test', G3), ('ext', C5)):
    for p in POL:
        rs = json.load(open(os.path.join(root, FILES[split][p])))['records']
        assert len(rs) == (240 if split == 'test' else 300), (split, p, len(rs))
        rec[p] += rs
for p in POL:
    assert len(rec[p]) == 540

def med(v):
    return round(statistics.median(v), 3) if v else ''

with open(os.path.join(OUT, 'o_class.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['类别', '策略', '回合', '到达', '碰撞', '超时'])
    for c in ['稀疏', '适中', '密集', '总体']:
        for p in POL:
            rs = [r for r in rec[p] if c == '总体' or CAT[r['category']] == c]
            n = lambda k: sum(r['done_reason'] == k for r in rs)
            w.writerow([c, p, len(rs), n('reached'), n('collision'), n('time_limit')])

with open(os.path.join(OUT, 'o_timeouts.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['策略', '超时', '最近目标距离<2m', '<1m', '中位数m'])
    for p in POL:
        d = [r['nearest_goal_distance_m'] for r in rec[p] if r['done_reason'] == 'time_limit']
        w.writerow([p, len(d), sum(x < 2 for x in d), sum(x < 1 for x in d), med(d)])

with open(os.path.join(OUT, 'o_behavior.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['类别', '策略', '到达回合', '路径效率', '最大横向偏离m', '高度范围m', '回退距离m', '飞行时间s'])
    for c in ['稀疏', '适中', '密集', '总体']:
        for p in POL:
            rs = [r for r in rec[p] if r['done_reason'] == 'reached' and (c == '总体' or CAT[r['category']] == c)]
            tm = [r['trajectory_metrics'] for r in rs]
            w.writerow([c, p, len(rs),
                        med([D0[r['task_id']] / r['trajectory_metrics']['path_length_m'] for r in rs]),
                        med([m['max_cross_track_m'] for m in tm]), med([m['z_span_m'] for m in tm]),
                        med([m['backtrack_m'] for m in tm]), med([r['physical_time_s'] for r in rs])])
print('done')
