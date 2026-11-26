"""前置研究 ①：在已有训练采集（P18、P19，对照臂，reward v2，随机采样）上离线比较三种进度信号。
用法：python3 -I pre1_geodesic_vs_euclid.py <项目仓库根目录> [每类最多回合数，默认 250]
数据：jindu/routea_f7_run01/train/{P18,P19}/metrics_update_*.json.gz 的 transition_records；世界几何取自 eval_dev/P18 原迹回合头（dev420 世界即训练世界）。
三种信号（每决策）：
  E = 记录中的 reward_terms.newbest（欧氏、只奖励刷新历史最近）；
  Gn = 10 × (测地历史最近的减少量) / 回合起点测地距离（把 newbest 中的欧氏距离换成测地距离）；
  Gs = 10 × (决策前测地距离 − 决策后测地距离) / 回合起点测地距离（有符号差分，对应 arXiv 2602.08653 式 4 的形式）。
回合：以终止或截断结束的回合；直线被挡 = 回合首个记录位置到目标的直线净空 < 0.3 m。"仍被挡的决策" = 决策起点到目标的直线净空 < 0.3 m。"""
import glob, gzip, json, os, sys, collections, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_field import World, line_clear
repo = sys.argv[1]; NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 250
geo = {}
for f in glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P18/traces/*.jsonl.gz'):
    s = json.loads(gzip.open(f, 'rt').readline()); geo.setdefault(s['world_id'], s['geometry'])
eps = collections.defaultdict(list)
for P in ('P18', 'P19'):
    for f in sorted(glob.glob(f'{repo}/jindu/routea_f7_run01/train/{P}/metrics_update_*.json.gz')):
        for t in json.load(gzip.open(f))['rollout_audit']['transition_records']:
            eps[(P, t['episode_id'])].append({k: t[k] for k in ('decision_index', 'world_id', 'goal_xyz', 'position_before_xyz', 'position_after_xyz', 'terminated', 'truncated', 'reward_terms', 'executed_path', 'value', 'advantage_raw', 'return_target')})
E = []
for k, T in eps.items():
    T.sort(key=lambda t: t['decision_index'])
    if T[-1]['terminated'] or T[-1]['truncated']:
        term = T[-1]['reward_terms'].get('terminal', 0) if T[-1]['terminated'] else 0
        E.append((('S' if term > 0 else 'C') if T[-1]['terminated'] else 'T', T))
print('完整回合', len(E), dict(collections.Counter(o for o, _ in E)))
print('不同 (世界, 目标) 数：', len({(T[0]['world_id'], tuple(np.round(T[0]['goal_xyz'], 2))) for _, T in E}), '；世界数', len({T[0]['world_id'] for _, T in E}))
byw = collections.defaultdict(list)
for o, T in E: byw[T[0]['world_id']].append((o, T))
random.seed(20261116); rows = []; cnt = collections.Counter()
for wid, lst in sorted(byw.items()):
    P = np.array([p for _, T in lst for t in T for p in (t['position_before_xyz'], t['position_after_xyz'], t['goal_xyz'])])
    lo = P.min(0) - 5; hi = P.max(0) + 5; lo[2], hi[2] = min(1.0, P[:, 2].min()), max(5.0, P[:, 2].max())
    W = World(geo[wid], lo, hi); fields = {}
    random.shuffle(lst)
    for o, T in lst:
        g = T[0]['goal_xyz']; blk = line_clear(W, T[0]['position_before_xyz'], g) < .3; key = (o, blk)
        if cnt[key] >= NMAX: continue
        cnt[key] += 1; gk = tuple(np.round(g, 2))
        if gk not in fields: fields[gk] = W.field(g)
        F = fields[gk]; G0 = F.dist(T[0]['position_before_xyz'])
        if not np.isfinite(G0) or G0 < 1: continue
        gbest = G0
        for i, t in enumerate(T):
            a, b = F.dist(t['position_before_xyz']), F.dist(t['position_after_xyz'])
            if not (np.isfinite(a) and np.isfinite(b)): continue
            gn = 10 * max(gbest - b, 0) / G0; gbest = min(gbest, b)
            rows.append(dict(o=o, blk=blk, ep=id(T), i=i, to_end=len(T) - 1 - i, E=t['reward_terms']['newbest'], Gn=gn, Gs=10 * (a - b) / G0,
                             still=line_clear(W, t['position_before_xyz'], g) < .3,
                             step=float(np.linalg.norm(np.subtract(t['position_after_xyz'], t['position_before_xyz']))),
                             G0=G0, D0=float(np.linalg.norm(np.subtract(g, T[0]['position_before_xyz']))), value=t['value'], adv=t['advantage_raw'], n=len(T)))
    print(wid[-45:], dict(cnt), flush=True)
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pre1_rows.json'), 'w'))
def auc(pos, neg):
    x = np.concatenate([pos, neg]); r = x.argsort().argsort() + 1.
    # 并列取平均秩
    from scipy.stats import rankdata
    r = rankdata(x); return (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
R = rows; med = lambda v: float(np.median(v)) if len(v) else float('nan')
print('\n== (a) 每回合进度合计的中位数（直线被挡的回合）')
for o in 'SCT':
    ep = collections.defaultdict(lambda: [0, 0, 0])
    for r in R:
        if r['blk'] and r['o'] == o:
            for j, k in enumerate(('E', 'Gn', 'Gs')): ep[r['ep']][j] += r[k]
    v = np.array(list(ep.values()))
    if len(v): print('  结局 %s（%d 回合）：E %.2f，Gn %.2f，Gs %.2f' % (o, len(v), *np.median(v, 0)))
print('== (b) 碰撞回合最后 4 个决策（不含碰撞决策本身）每决策均值，直线被挡回合')
X = [r for r in R if r['blk'] and r['o'] == 'C' and 1 <= r['to_end'] <= 4]
print('  n=%d：E %.3f，Gn %.3f，Gs %.3f；E>0 而 Gs≤0 的比例 %.0f%%；Gs<0 的比例 %.0f%%' % (len(X), np.mean([r['E'] for r in X]), np.mean([r['Gn'] for r in X]), np.mean([r['Gs'] for r in X]),
      100 * np.mean([r['E'] > 0 and r['Gs'] <= 0 for r in X]), 100 * np.mean([r['Gs'] < 0 for r in X])))
print('== (c) 区分能力：在"直线仍被挡"的决策上，用单个决策的进度信号区分"最终到达的回合"与"最终碰撞的回合"（AUC，0.5 = 无区分）')
S = [r for r in R if r['blk'] and r['still'] and r['o'] == 'S']; C = [r for r in R if r['blk'] and r['still'] and r['o'] == 'C' and r['to_end'] >= 1]
print('  决策数：到达回合 %d，碰撞回合 %d' % (len(S), len(C)))
for k in ('E', 'Gn', 'Gs'):
    print('  %s：AUC %.3f；到达回合均值 %.3f，碰撞回合均值 %.3f' % (k, auc(np.array([r[k] for r in S]), np.array([r[k] for r in C])), np.mean([r[k] for r in S]), np.mean([r[k] for r in C])))
print('  每飞 1 m 的测地进度（m/m）：到达回合中位 %.2f，碰撞回合中位 %.2f；欧氏 newbest/步长：%.2f 对 %.2f' % (
    med([r['Gs'] / max(r['step'], 1e-6) for r in S if r['step'] > .05]), med([r['Gs'] / max(r['step'], 1e-6) for r in C if r['step'] > .05]),
    med([r['E'] / max(r['step'], 1e-6) for r in S if r['step'] > .05]), med([r['E'] / max(r['step'], 1e-6) for r in C if r['step'] > .05])))
print('== (d) 对照：直线可通过的回合，三种信号每回合合计中位数')
for o in 'SCT':
    ep = collections.defaultdict(lambda: [0, 0, 0])
    for r in R:
        if not r['blk'] and r['o'] == o:
            for j, k in enumerate(('E', 'Gn', 'Gs')): ep[r['ep']][j] += r[k]
    v = np.array(list(ep.values()))
    if len(v): print('  结局 %s（%d 回合）：E %.2f，Gn %.2f，Gs %.2f' % (o, len(v), *np.median(v, 0)))
print('== (e) 到达回合是否只是几何更容易：直线被挡回合的绕行比（起点测地距离 / 直线距离）与起点距离')
for o in 'SCT':
    ep = {r['ep']: r for r in R if r['blk'] and r['o'] == o}
    if ep: print('  结局 %s（%d 回合）：绕行比中位 %.3f，75%% 分位 %.3f；起点直线距离中位 %.1f m；回合决策数中位 %d' % (o, len(ep), med([r['G0'] / r['D0'] for r in ep.values()]), float(np.percentile([r['G0'] / r['D0'] for r in ep.values()], 75)), med([r['D0'] for r in ep.values()]), med([r['n'] for r in ep.values()])))
print('== (f) 评论家能否提前看出碰撞：直线被挡回合中，按"距回合结束的决策数"比较最终碰撞与最终到达回合的 value（AUC：到达回合 value 更高的概率）')
for lo_, hi_ in ((1, 1), (2, 2), (3, 4), (5, 8), (9, 16)):
    S_ = np.array([r['value'] for r in R if r['blk'] and r['o'] == 'S' and r['still']]); C_ = np.array([r['value'] for r in R if r['blk'] and r['o'] == 'C' and lo_ <= r['to_end'] <= hi_])
    if len(C_): print('  碰撞前第 %d—%d 个决策（n=%d）：碰撞回合 value 中位 %.1f；到达回合仍被挡决策 value 中位 %.1f；AUC %.3f' % (lo_, hi_, len(C_), np.median(C_), np.median(S_), auc(S_, C_)))
X_ = [r for r in R if r['blk'] and r['o'] == 'C']
for lo_, hi_ in ((0, 0), (1, 1), (2, 2), (3, 4), (5, 8)):
    v = [r['adv'] for r in X_ if lo_ <= r['to_end'] <= hi_]
    if v: print('  碰撞回合，距结束 %d—%d 个决策：原始优势中位 %.2f，均值 %.2f（n=%d）' % (lo_, hi_, np.median(v), np.mean(v), len(v)))
