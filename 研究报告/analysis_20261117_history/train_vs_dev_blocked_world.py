"""只读：按世界比较"训练采集（P18、P19，随机采样）中直线被挡回合的到达率"与"dev420 被挡任务被任一策略解决的情况"。
用法：python3 -I train_vs_dev_blocked_world.py <项目仓库根> <转移汇总目录> <e1_blocked_by_policy_output.txt>
训练任务为每世界随机起终点，与 dev 固定任务不重合（dev 目标到最近训练目标的距离中位约 2.4 m），故只能按世界比较。
被挡 = 回合首个记录位置到目标直线净空 <0.3 m（0.05 m 采样）。到达 = tf.reached（0.5 m 训练口径）。"""
import sys, os, glob, gzip, json, csv, collections
import numpy as np
repo, sumdir, e1out = sys.argv[1:4]
sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from diffusion_policy_3d.env.collision_geom import ObstacleSpec, compute_obstacle_clearance
geo, dev = {}, {}
for f in glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P18/traces/*.jsonl.gz'):
    h = json.loads(gzip.open(f, 'rt').readline())
    geo.setdefault(h['world_id'], [ObstacleSpec.from_dict(o) for o in h['geometry']])
    dev[h['task_id']] = (h['world_id'], np.array(h['task']['start_pos']), np.array(h['task']['goal_pos']))
def clear(a, b, obs):
    n = int(np.linalg.norm(b - a) / .05) + 2
    return min(compute_obstacle_clearance(*(a + t * (b - a)), obs)[0] for t in np.linspace(0, 1, n))
txt = open(e1out).read().split('从未有策略成功的')[1]
solved = {l.split()[0] for l in txt.splitlines() if l.strip() and '__' in l.split()[0]}
devw = collections.defaultdict(lambda: [0, 0])
for k, (w, s, g) in dev.items():
    if clear(s, g, geo[w]) < .3:
        devw[w][0] += 1; devw[w][1] += k.split('rl_train__')[1] in solved
F = {}
for P in ('P18', 'P19'):
    for r in csv.DictReader(gzip.open(f'{sumdir}/train__{P}__transitions.csv.gz', 'rt')):
        k = (P, r['episode_id']); d = int(r['decision_index'])
        v = F.setdefault(k, {'d0': 10**9, 'dl': -1})
        if d < v['d0']: v.update(d0=d, w=r['world_id'], s=json.loads(r['position_before_xyz']), g=json.loads(r['goal_xyz']))
        if d > v['dl']: v.update(dl=d, term=r['terminated'] == 'True', trunc=r['truncated'] == 'True', reached=r['tf.reached'] == 'True')
tw = collections.defaultdict(collections.Counter)
for v in F.values():
    if not (v['term'] or v['trunc']): continue
    if clear(np.array(v['s']), np.array(v['g']), geo[v['w']]) >= .3: continue
    tw[v['w']]['S' if v['reached'] else ('C' if v['term'] else 'T')] += 1
print('%-60s %s' % ('世界', 'dev被挡任务(已解/共)  训练被挡回合: 到达/共 (到达率)'))
rows = []
for w in sorted(set(devw) | set(tw)):
    c = tw[w]; n = sum(c.values()); dn, ds = devw.get(w, [0, 0])
    rows.append((w, dn, ds, c['S'], n))
    print('%-60s %2d/%-2d               %3d/%-4d (%s)' % (w.split('rl_train__')[1], ds, dn, c['S'], n, '%.0f%%' % (100 * c['S'] / n) if n else '—'))
def agg(sel, name):
    S = sum(r[3] for r in rows if sel(r)); N = sum(r[4] for r in rows if sel(r))
    print('%s：训练被挡回合 %d，到达 %d（%.1f%%）' % (name, N, S, 100 * S / max(N, 1)))
agg(lambda r: r[1] > 0 and r[2] == r[1], 'dev 被挡任务全部已解的世界')
agg(lambda r: r[1] > 0 and 0 < r[2] < r[1], 'dev 被挡任务部分已解的世界')
agg(lambda r: r[1] > 0 and r[2] == 0, 'dev 被挡任务全部未解的世界')
agg(lambda r: r[1] == 0, 'dev 无被挡任务的世界')
