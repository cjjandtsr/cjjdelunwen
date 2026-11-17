"""只读：训练采集（随机采样）中"直线被挡"与"直线可通过"任务的结局，P18/P19（对照）与 P16/P17（F7）。
用法：python3 -I f7_train_blocked.py <项目仓库根目录>
几何：训练世界与 dev420 世界相同（dev420 = 训练世界），取 jindu/routea_f7_run01/eval_dev/P18/traces 回合头中同 world_id 的障碍几何；
起点 = 回合首个转移（decision_index 最小；含 30% 中途状态初始化回合）的 position_before_xyz，目标 = goal_xyz；直线净空按 0.05 m 采样、compute_obstacle_clearance 计算；< 0.3 m 记为被挡。
只用以终止或截断结束的回合（采集边界处未完成片段被丢弃，回合不跨更新）；到达 = 训练环境 0.5 m 终止奖励 > 0。"""
import glob, gzip, json, os, sys, collections
import numpy as np
repo = sys.argv[1]; sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from diffusion_policy_3d.env.collision_geom import ObstacleSpec, compute_obstacle_clearance
geo = {}
for f in glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P18/traces/*.jsonl.gz'):
    s = json.loads(gzip.open(f, 'rt').readline()); geo.setdefault(s['world_id'], [ObstacleSpec.from_dict(o) for o in s['geometry']])
def line_clear(a, b, obs):
    a, b = np.asarray(a), np.asarray(b); n = int(np.linalg.norm(b - a) / .05) + 2
    return min(compute_obstacle_clearance(*(a + t * (b - a)), obs)[0] for t in np.linspace(0, 1, n))
for P in ('P18', 'P19', 'P16', 'P17'):
    eps = collections.defaultdict(list)
    for f in sorted(glob.glob(f'{repo}/jindu/routea_f7_run01/train/{P}/metrics_update_*.json.gz')):
        for t in json.load(gzip.open(f))['rollout_audit']['transition_records']: eps[t['episode_id']].append(t)
    out = collections.defaultdict(collections.Counter); miss = 0
    for e, T in eps.items():
        T.sort(key=lambda t: t['decision_index'])
        if not (T[-1]['terminated'] or T[-1]['truncated']): continue
        if T[0]['world_id'] not in geo: miss += 1; continue
        blk = line_clear(T[0]['position_before_xyz'], T[0]['goal_xyz'], geo[T[0]['world_id']]) < .3
        term = T[-1]['reward_terms'].get('terminal', 0) if T[-1]['terminated'] else 0
        out['被挡' if blk else '可通过'][('S' if term > 0 else 'C') if T[-1]['terminated'] else 'T'] += 1
    print(P, '（无几何的回合 %d）' % miss)
    for k, c in sorted(out.items()):
        n = sum(c.values()); print('  直线%s：%d 回合，到达 %.0f%%，碰撞 %.0f%%，超时 %.0f%%' % (k, n, 100 * c['S'] / n, 100 * c['C'] / n, 100 * c['T'] / n))
