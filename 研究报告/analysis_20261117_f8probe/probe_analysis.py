"""F8 同状态采样探针 run02 的分析（只读）。
用法：python3 -I probe_analysis.py <项目仓库根目录>
数据：jindu/f8_probe_run02_20261117/{P6_full,P0_full}/{samples,flights}.jsonl.gz；原 P6 dev420 原迹 jindu/routea_f5_run01/results/eval_dev/full/P6/traces/*.jsonl（原确定性轨迹与障碍几何）。
1 m 结局取 flights 的 outcome 字段（Codex 已按 outcome_1m 复算）；本脚本另从执行路径独立复算一次并比对。
"偏移" = 该状态是原回合碰撞前第几个决策（genuine_backs）。"""
import ast, glob, gzip, json, math, os, sys, collections
import numpy as np
repo = sys.argv[1]; D = f'{repo}/jindu/f8_probe_run02_20261117'
sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from diffusion_policy_3d.env.collision_geom import ObstacleSpec, compute_obstacle_clearance
def rd(f):
    with gzip.open(f, 'rt') as h:
        for l in h: yield json.loads(l)
orig = {}
for f in glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_dev/full/P6/traces/*.jsonl'):
    L = [json.loads(l) for l in open(f)]; s = L[0]; task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task'])
    orig[(s['task_id'], s['repeat'])] = dict(goal=np.array(task['goal_pos']), start=np.array(task['start_pos']), geom=s['geometry'], T=[t for t in L if t.get('type') == 'transition'])
def seg_dist(p, a, b):
    a, b, p = map(np.asarray, (a, b, p)); d = b - a; L = d @ d
    t = 0. if L == 0 else float(np.clip((p - a) @ d / L, 0, 1)); return float(np.linalg.norm(a + t * d - p))
med = lambda v: float(np.median(v)) if len(v) else float('nan')
for pol in ('P6', 'P0'):
    S = collections.defaultdict(list)
    for r in rd(f'{D}/{pol}_full/samples.jsonl.gz'): S[r['state_id']].append(r)
    Fl = collections.defaultdict(list)
    for r in rd(f'{D}/{pol}_full/flights.jsonl.gz'): Fl[r['state_id']].append(r)
    print('=' * 20, pol, '状态', len(S), '续飞', sum(len(v) for v in Fl.values()))
    # 独立复算 1 m 结局
    bad = 0
    for sid, fl in Fl.items():
        g = orig[(S[sid][0]['task_id'], S[sid][0]['repeat'])]['goal']
        for f in fl:
            mind = min(seg_dist(g, P[k], P[k + 1]) for row in f['rows'] for P in [row['executed_path']] for k in range(len(P) - 1))
            o = 'reached' if (f['raw_outcome'] == 'reached' or mind < 1.0) else f['raw_outcome']
            bad += (o != f['outcome'])
    print('1 m 结局独立复算不一致数：', bad)
    print('-- (1) 判定量，按偏移与路线类型')
    for back in (2, 4, 6, 8):
        for name, sel in (('全部', lambda s: True), ('越顶', lambda s: s['overflight']), ('侧绕', lambda s: not s['overflight'])):
            ids = [sid for sid, v in S.items() if back in v[0]['genuine_backs'] and sel(v[0])]
            if not ids: continue
            pp = [np.mean([x['plan_obstacle_clear'] and x['plan_ground_clear'] for x in S[i] if not x['deterministic']]) for i in ids]
            fl = [f for i in ids for f in Fl.get(i, [])]
            if fl:
                pr = np.mean([np.mean([f['outcome'] == 'reached' for f in Fl[i]]) for i in ids if Fl.get(i)])
                pn = np.mean([np.mean([f['outcome'] != 'collision' for f in Fl[i]]) for i in ids if Fl.get(i)])
                anyr = sum(any(f['outcome'] == 'reached' for f in Fl[i]) for i in ids if Fl.get(i))
                print('  偏移 %d %s：状态 %d，p_plan 中位 %.3f，p_reach %.3f，p_nocol %.3f；至少一次到达的状态 %d' % (back, name, len(ids), med(pp), pr, pn, anyr))
            else: print('  偏移 %d %s：状态 %d，p_plan 中位 %.3f（无续飞）' % (back, name, len(ids), med(pp)))
    print('-- (2) 同状态 64 个随机采样的散布（m）')
    for back in (2, 4, 6, 8):
        h4h, h4v, h8h, h8v, mx, dev, near = [], [], [], [], [], [], []
        for sid, v in S.items():
            if back not in v[0]['genuine_backs']: continue
            R_ = [x for x in v if not x['deterministic']]; det = [x for x in v if x['deterministic']][0]
            e4 = np.array([x['candidate_h4_path'][-1] for x in R_]); e8 = np.array([x['planned_policy_path'][-1] for x in R_])
            p0 = np.array(v[0]['pre_state']['position'])
            h4h.append(float(np.sqrt(e4[:, :2].var(0).sum()))); h4v.append(float(e4[:, 2].std())); h8h.append(float(np.sqrt(e8[:, :2].var(0).sum()))); h8v.append(float(e8[:, 2].std()))
            mx.append(float(max(np.linalg.norm(e8 - e8[i], axis=1).max() for i in range(len(e8)))))
            dev.append(float(np.linalg.norm(e8 - np.array(det['planned_policy_path'][-1]), axis=1).max()))
            d8 = e8 - p0; d8 /= np.linalg.norm(d8, axis=1, keepdims=True) + 1e-9; dd = np.array(det['planned_policy_path'][-1]) - p0; dd /= np.linalg.norm(dd) + 1e-9
            near.append(float(np.degrees(np.arccos(np.clip(d8 @ dd, -1, 1))).max()))
        print('  偏移 %d（%d 状态）：4 步终点水平标准差中位 %.3f、竖直 %.3f；8 步终点水平 %.3f、竖直 %.3f；8 步终点最大两两距离中位 %.2f；离确定性规划终点最远中位 %.2f；与确定性规划方向的最大夹角中位 %.1f°' % (
            back, len(h4h), med(h4h), med(h4v), med(h8h), med(h8v), med(mx), med(dev), med(near)))
    print('-- (3) 采样方向与该走方向（最短路线前方 3 m 的点）的夹角，偏移 4')
    a_det, a_best, need = [], [], []
    for sid, v in S.items():
        if 4 not in v[0]['genuine_backs'] or not v[0]['geodesic_direction'].get('direction_valid'): continue
        p0 = np.array(v[0]['pre_state']['position']); q = np.array(v[0]['geodesic_direction']['point']) - p0; q /= np.linalg.norm(q) + 1e-9
        ang = lambda x: float(np.degrees(np.arccos(np.clip(((np.array(x['planned_policy_path'][-1]) - p0) / (np.linalg.norm(np.array(x['planned_policy_path'][-1]) - p0) + 1e-9)) @ q, -1, 1))))
        det = [x for x in v if x['deterministic']][0]; a_det.append(ang(det)); a_best.append(min(ang(x) for x in v if not x['deterministic']))
    print('  状态 %d：确定性规划与该走方向的夹角中位 %.0f°；64 个采样中最接近者的夹角中位 %.0f°；最接近者夹角 < 10° 的状态比例 %.0f%%' % (len(a_det), med(a_det), med(a_best), 100 * np.mean(np.array(a_best) < 10)))
    print('-- (4) 续飞后是否回到原轨迹（各偏移；与原确定性轨迹比较）')
    for back in (2, 4, 6, 8):
        dcol, same, d1, d2, dend = [], [], [], [], []
        for sid, fl in Fl.items():
            v0 = S[sid][0]
            if back not in v0['genuine_backs']: continue
            o = orig[(v0['task_id'], v0['repeat'])]; T = o['T']; k0 = len(T) - 1 - back; cpt = np.array(T[-1]['executed_path'][-1])
            for f in fl:
                rows = f['rows']
                if len(rows) >= 1 and k0 < len(T): d1.append(math.dist(rows[0]['executed_path'][-1], T[k0]['executed_path'][-1]))
                if len(rows) >= 2 and k0 + 1 < len(T): d2.append(math.dist(rows[1]['executed_path'][-1], T[k0 + 1]['executed_path'][-1]))
                if f['outcome'] == 'collision':
                    dcol.append(math.dist(f['final_position'], cpt)); same.append(len(rows) == back + 1)
        if d1: print('  偏移 %d：第 1 个决策结束时离原轨迹 %.2f m（中位），第 2 个决策结束时 %.2f m；碰撞续飞中碰撞点离原碰撞点中位 %.2f m，<0.5 m 的比例 %.0f%%；与原回合在同一决策碰撞的比例 %.0f%%（n=%d）' % (
            back, med(d1), med(d2), med(dcol), 100 * np.mean(np.array(dcol) < .5), 100 * np.mean(same), len(dcol)))
    print('-- (5) 到达的续飞与同状态碰撞的续飞：首个动作块有何不同（全部偏移）')
    rows_ = []
    for sid, fl in Fl.items():
        v0 = S[sid][0]; det = [x for x in S[sid] if x['deterministic']][0]; p0 = np.array(v0['pre_state']['position']); de = np.array(det['candidate_h4_path'][-1])
        if not any(f['outcome'] == 'reached' for f in fl): continue
        for f in fl:
            e = np.array(f['rows'][0]['executed_path'][-1]); rows_.append((f['outcome'] == 'reached', float(np.linalg.norm((e - de)[:2])), float(e[2] - de[2]), float(np.linalg.norm(e - p0))))
    if rows_:
        A = np.array([r[1:] for r in rows_ if r[0]]); B = np.array([r[1:] for r in rows_ if not r[0]])
        print('  有到达的状态里：到达续飞 %d 个，未到达 %d 个' % (len(A), len(B)))
        if len(B): print('  首块终点相对确定性规划的水平偏移中位：到达 %.3f m，未到达 %.3f m；竖直偏移中位：到达 %+.3f，未到达 %+.3f；首块位移中位：到达 %.2f，未到达 %.2f' % (med(A[:, 0]), med(B[:, 0]), med(A[:, 1]), med(B[:, 1]), med(A[:, 2]), med(B[:, 2])))
    st = collections.Counter()
    for sid, fl in Fl.items():
        n = sum(f['outcome'] == 'reached' for f in fl); st[n] += 1
    print('  每个状态 8 次续飞中到达次数的分布（到达次数: 状态数）：', dict(sorted(st.items())))
