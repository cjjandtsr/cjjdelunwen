"""只读：EGO 示范的飞行速度（冻结示范 demo_frames.csv.gz，0.3 s 一帧），与 forward_free_rows.json 中 EGO/BC/P6 执行速度对照。
用法：python3 -I demo_speed.py <demo_frames.csv.gz> <demo_episodes.csv> <forward_free_rows.json>
速度 = 相邻帧位置差 / 0.3 s；回合速度 = 回合内中位数。只统计 split_e5_bc = train 的回合与全部回合两种。"""
import csv, gzip, json, sys, collections
import numpy as np
fr, epf, rows = sys.argv[1:4]
split = {r['episode_id']: r['split_e5_bc'] for r in csv.DictReader(open(epf))}
P = collections.defaultdict(list)
for r in csv.DictReader(gzip.open(fr, 'rt')):
    P[r['episode_id']].append((int(r['frame_in_episode']), float(r['x_world']), float(r['y_world']), float(r['z_world'])))
ep_v, all_v, ep_v_tr = [], [], []
for k, L in P.items():
    L.sort(); X = np.array([l[1:] for l in L])
    if len(X) < 3: continue
    v = np.linalg.norm(np.diff(X, axis=0), axis=1) / .3; all_v += list(v); ep_v.append(np.median(v))
    if split.get(k) == 'train': ep_v_tr.append(np.median(v))
def q(a): a = np.array(a); return f'{np.median(a):.2f} [{np.percentile(a,25):.2f}, {np.percentile(a,75):.2f}]，p90 {np.percentile(a,90):.2f}，n={len(a)}'
print('示范回合', len(ep_v), '；回合中位速度 m/s', q(ep_v)); print('示范 train 回合中位速度', q(ep_v_tr)); print('示范逐帧速度', q(all_v))
print('示范逐帧速度 >0.6 m/s 的占比 %.3f；>0.5 的占比 %.3f' % (np.mean(np.array(all_v) > .6), np.mean(np.array(all_v) > .5)))
R = json.load(open(rows))
for n, L in R.items():
    print(n, '全部回合中位速度', q([r['v_med'] for r in L if r['v_med'] == r['v_med']]))
b = {(r['task'], r['rep']): r['v_med'] for r in R['BC #E2（dev420）']}; p = {(r['task'], r['rep']): r['v_med'] for r in R['P6@u256 #E2（dev420）']}
K = sorted(set(b) & set(p)); d = np.array([p[k] - b[k] for k in K])
print('dev420 配对（P6 − BC）回合中位速度差 m/s', q(d), '；P6 更快的回合比例 %.2f' % np.mean(d > 0))
