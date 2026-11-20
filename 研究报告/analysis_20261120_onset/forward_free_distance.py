"""只读：沿当前运动方向的"前方自由距离"与飞行速度，EGO 对 BC、P6@u256（#E2）。不依赖起点—目标直线。
用法：python3 -I forward_free_distance.py <EGO 原迹目录> <P6 #E2 dev420 原迹目录> <BC #E2 dev420 原迹目录> <collision_geom.py 所在目录>
口径：执行路径每个 0.3 s 段的终点 p 与方向 d=(p−p_prev)/|·|（段长 <0.03 m 的跳过）；从 p 沿 d 每 0.05 m 前进至 5 m，
  第一个几何净空 <0.1 m 的距离记 F（5 m 内没有记 5）。F 是"照当前方向直飞多远会撞"。速度 = 段长/段时长。
  回合指标：F<1 m 的段占比；回合内 F 最小值（不含最后 1 个决策，避免碰撞瞬间本身）；碰撞回合另看碰撞前 2.4 s（8 段）内 F 的最小值与速度。
  被挡判定同 onset_side_switch.py（直线净空 <0.3 m）。"""
import ast, glob, gzip, json, os, sys, collections
import numpy as np
EGO, P6D, BCD, CG = sys.argv[1:5]
sys.path.insert(0, CG)
from collision_geom import ObstacleSpec, compute_obstacle_clearance
def clr(p, obs): return compute_obstacle_clearance(*p, obs)[0]
def seg(p, a, b):
    d = b - a; L = d @ d; t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))
def episode(f):
    op = gzip.open if f.endswith('.gz') else open
    L = [json.loads(l) for l in op(f, 'rt') if l.strip()]
    if L[-1].get('type') != 'episode_end': return None
    h = L[0]; task = h['task'] if isinstance(h['task'], dict) else ast.literal_eval(h['task'])
    s, g = np.array(task['start_pos'], float), np.array(task['goal_pos'], float)
    obs = [ObstacleSpec.from_dict(o) for o in h['geometry']]
    T = [t for t in L if t.get('type') == 'transition']
    P = [np.array(T[0]['executed_path'][0], float)]; dts = []; dec = []
    for i, t in enumerate(T):
        ep = t['executed_path']; dt = t['executed_time_s'] / (len(ep) - 1)
        for q in ep[1:]: P.append(np.array(q, float)); dts.append(dt); dec.append(i)
    P = np.array(P)
    mind = min(seg(g, P[k], P[k + 1]) for k in range(len(P) - 1))
    dr = L[-1]['done_reason']; out = 'S' if (dr == 'reached' or mind < 1) else ('C' if dr in ('collision', 'ground_collision') else 'T')
    D = np.linalg.norm(g - s); e = (g - s) / D
    blocked = min(clr(s + u * e, obs) for u in np.linspace(0, D, int(D / .05) + 2)) < .3
    F, V, DEC = [], [], []
    for k in range(1, len(P)):
        d = P[k] - P[k - 1]; l = np.linalg.norm(d)
        if l < .03: continue
        d /= l; f = 5.
        for x in np.arange(.05, 5.0001, .05):
            if clr(P[k] + x * d, obs) < .1: f = x; break
        F.append(f); V.append(l / dts[k - 1]); DEC.append(dec[k - 1])
    F, V, DEC = np.array(F), np.array(V), np.array(DEC)
    last = len(T) - 1
    r = dict(task=h['task_id'], rep=h['repeat'], out=out, blocked=bool(blocked), role=h.get('role'),
             frac_F1=float((F < 1).mean()) if len(F) else np.nan,
             minF=float(F[DEC < last].min()) if (DEC < last).any() else np.nan,
             v_med=float(np.median(V)) if len(V) else np.nan)
    if out == 'C' and len(F):
        w = F[-8:]; r['minF_pre'] = float(w.min()); r['v_pre'] = float(np.median(V[-8:]))
        # 碰撞前 F 第一次 <1 m 到碰撞的时间（s）
        idx = np.where(F < 1)[0]; r['t_F1_to_hit'] = float((len(F) - idx[0]) * .3) if len(idx) else np.nan
        # 碰撞前最后 8 段的转向角（相邻段方向夹角之和，度）
        return r
    return r
def load(d): return [x for x in (episode(f) for f in sorted(glob.glob(os.path.join(d, '*.jsonl*')))) if x]
def q(a):
    a = np.array([x for x in a if np.isfinite(x)])
    return '—' if not len(a) else f'{np.median(a):5.2f} [{np.percentile(a,25):.2f}, {np.percentile(a,75):.2f}] n={len(a)}'
SRC = {'EGO（论文186任务）': EGO, 'BC #E2（dev420）': BCD, 'P6@u256 #E2（dev420）': P6D}
ALL = {k: load(v) for k, v in SRC.items()}
for name, R in ALL.items():
    print(f'\n== {name}')
    for lab, sel in (('被挡-全部', lambda r: r['blocked']), ('被挡-到达', lambda r: r['blocked'] and r['out'] == 'S'), ('被挡-碰撞', lambda r: r['blocked'] and r['out'] == 'C'),
                     ('可通过-全部', lambda r: not r['blocked'])):
        S = [r for r in R if sel(r)]
        if not S: continue
        print(f'  [{lab} {len(S)}] 速度 m/s {q([r["v_med"] for r in S])}；F<1 m 段占比 {q([r["frac_F1"] for r in S])}；回合内最小 F m {q([r["minF"] for r in S])}')
        C = [r for r in S if r['out'] == 'C']
        if C and lab.endswith('碰撞'):
            print(f'      碰撞前 2.4 s：最小 F {q([r["minF_pre"] for r in C])}；速度 {q([r["v_pre"] for r in C])}；F 首次 <1 m 到碰撞 s {q([r["t_F1_to_hit"] for r in C])}')
    if name.startswith('EGO'):
        for role in sorted({r['role'] for r in R}):
            S = [r for r in R if r['role'] == role]
            c = collections.Counter(r['out'] for r in S); print(f'  角色 {role}：回合 {len(S)}，被挡 {sum(r["blocked"] for r in S)}，结局 {dict(c)}')
json.dump(ALL, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'forward_free_rows.json'), 'w'), ensure_ascii=False, default=float)
