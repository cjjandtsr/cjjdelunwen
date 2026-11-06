#!/usr/bin/env python3
"""G17（第一阶段新 seed，P14@u128）在原训练外评价集 O（test12 + 扩展集 run02，540 回合）上的分析。

数据：Codex《G17 run02 工程验收》紧凑包（zip sha256 8a53080b…36f0aa）：
  P14_O_episode_records.csv（逐回合）；references/{P0,P2}_{test,ext}.json（参照记录）；test_bank.json、ext_bank.json
输出（<OUT>/）：g17_main.csv（总体与三类结局）、g17_pairs.csv（配对差、世界聚类区间、新增/流失）、g17_timeouts.csv
统计：世界聚类 bootstrap 95% 区间，20000 次，seed 2026102601（与 G3、C5 相同）。
用法：python3 -I g17_o_analysis.py <G17包目录> <OUT>
"""
import csv, json, math, os, random, statistics, sys

G, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
CAT = {'zero': '稀疏', 'low': '适中', 'high': '密集'}
D0 = {}
for b in ('test_bank.json', 'ext_bank.json'):
    for t in json.load(open(os.path.join(G, b)))['tasks']:
        D0[t['task_id']] = math.dist(t['payload']['start_pos'], t['payload']['goal_pos'])

rec = {}
for r in csv.DictReader(open(os.path.join(G, 'P14_O_episode_records.csv'), encoding='utf-8-sig')):
    rec.setdefault('P14', {})[(r['task_id'], int(r['repeat']))] = dict(world=r['world_id'], cat=r['category'], out=r['done_reason'],
                                                                        near=float(r['nearest_goal_distance_m']), ih=r['initial_hash'])
for p in ('P0', 'P2'):
    for s in ('test', 'ext'):
        for r in json.load(open(os.path.join(G, 'references', f'{p}_{s}.json')))['records']:
            rec.setdefault(p, {})[(r['task_id'], int(r['repeat']))] = dict(world=r['world_id'], cat=r['category'], out=r['done_reason'],
                                                                           near=r['nearest_goal_distance_m'], ih=r.get('initial_hash'))
keys = sorted(rec['P14'])
assert len(keys) == 540 and set(keys) == set(rec['P0']) == set(rec['P2'])
for k in keys:
    assert rec['P14'][k]['cat'] == rec['P0'][k]['cat'] and rec['P14'][k]['world'] == rec['P0'][k]['world']
    if rec['P0'][k]['ih']:
        assert rec['P14'][k]['ih'] == rec['P0'][k]['ih']

with open(os.path.join(OUT, 'g17_main.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['类别', '策略', '回合', '到达', '碰撞', '超时', '到达率%'])
    for c in ['稀疏', '适中', '密集', '总体']:
        ks = [k for k in keys if c == '总体' or CAT[rec['P0'][k]['cat']] == c]
        for p in ('P0', 'P2', 'P14'):
            n = lambda o: sum(rec[p][k]['out'] == o for k in ks)
            w.writerow([c, p, len(ks), n('reached'), n('collision'), n('time_limit'), round(100 * n('reached') / len(ks), 1)])

worlds = sorted({rec['P0'][k]['world'] for k in keys})
byw = {wd: [k for k in keys if rec['P0'][k]['world'] == wd] for wd in worlds}
def diff(a, b, ks):
    return 100 * sum((rec[a][k]['out'] == 'reached') - (rec[b][k]['out'] == 'reached') for k in ks) / len(ks)
rng = random.Random(2026102601)
with open(os.path.join(OUT, 'g17_pairs.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['比较', '差(百分点)', '区间下界', '区间上界', '新增', '流失'])
    for a, b in (('P14', 'P0'), ('P14', 'P2'), ('P2', 'P0')):
        d = diff(a, b, keys); bs = []
        for _ in range(20000):
            ks = [k for _ in worlds for k in byw[worlds[rng.randrange(len(worlds))]]]
            bs.append(diff(a, b, ks))
        bs.sort()
        gain = sum(rec[a][k]['out'] == 'reached' and rec[b][k]['out'] != 'reached' for k in keys)
        loss = sum(rec[a][k]['out'] != 'reached' and rec[b][k]['out'] == 'reached' for k in keys)
        w.writerow([f'{a}-{b}', round(d, 1), round(bs[int(0.025 * 20000)], 1), round(bs[int(0.975 * 20000) - 1], 1), gain, loss])

with open(os.path.join(OUT, 'g17_timeouts.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['策略', '超时', '最近目标距离<2m', '<1m', '中位数m'])
    for p in ('P0', 'P2', 'P14'):
        d = [rec[p][k]['near'] for k in keys if rec[p][k]['out'] == 'time_limit']
        w.writerow([p, len(d), sum(x < 2 for x in d), sum(x < 1 for x in d), round(statistics.median(d), 2)])
print('worlds', len(worlds))
