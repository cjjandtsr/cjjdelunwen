"""只读：F8 run01 结果分析（Claude）。
用法：python3 -I f8_run01_analysis.py <F8 核验导出目录> <f7_episodes.json> <blocked_tasks_dev420.json> <pre2_rows.json>
  F8 核验导出目录 = Codex 交付 `program/f8_audit_20261119/`（含 evaluation_conditions.csv 等）
  f7_episodes.json = `研究报告/analysis_20261116_f7/f7_episodes.py` 的输出（P6、P16—P19 的逐条件结局）
输出：①独立复算冻结判据；②同配方对照的跨运行差异（P18、P19、P22、P23）；③逐任务的被挡结局；
④训练采集中密集世界的到达率（前/后 32 轮）；⑤建库覆盖。结局一律为 1 m 互斥口径。"""
import csv, json, sys, collections
D, F7EP, BLK, PRE = sys.argv[1:5]
rd = lambda f: list(csv.DictReader(open(f'{D}/{f}', encoding='utf-8-sig')))
E = [r for r in rd('evaluation_conditions.csv') if r['split'] == 'dev']
ARMS = ('P20', 'P21', 'P22', 'P23')
def stats(rows):
    c = collections.Counter(r for r, _ in rows); t = collections.defaultdict(int)
    for o, task in rows: t[task] += o == 'S'
    return c['S'], c['C'], c['T'], sum(v >= 3 for v in t.values())
M = {'reached': 'S', 'collision': 'C', 'time_limit': 'T'}
cur = {(a, g): stats([(M[r['outcome']], r['task_id']) for r in E if r['arm'] == a and r['group'] == g]) for a in ARMS for g in ('lateral', 'overflight', 'passable')}
# 历史臂：按同一分组（被挡清单 + 前置研究②越顶标签）
bl = set(json.load(open(BLK))); over = {r['task'] for r in json.load(open(PRE))['A'] if r['over']}
grp = lambda t: 'passable' if t not in bl else ('overflight' if t in over else 'lateral')
H = collections.defaultdict(list)
for r in json.load(open(F7EP)):
    if r['split'] == 'dev': H[(r['pol'], grp(r['task']))].append((r['out'], r['task']))
hist = {k: stats(v) for k, v in H.items()}
print('== ① 冻结判据复算（侧绕分支：A、K 用侧绕 85 条件；P 用可通过 255 条件）')
for t, c in (('P20', 'P22'), ('P21', 'P23')):
    dA = cur[(t, 'lateral')][0] - cur[(c, 'lateral')][0]; dK = cur[(t, 'lateral')][3] - cur[(c, 'lateral')][3]; dP = cur[(t, 'passable')][0] - cur[(c, 'passable')][0]
    print(f'  {t}-{c}: ΔA={dA:+d} ΔK={dK:+d} ΔP={dP:+d}', '达标' if dA >= 8 and dK >= 2 and dP >= -10 else ('A≤0' if dA <= 0 else '未达标'))
print('\n== ② 各臂 dev420 结局（到达/碰撞/超时；K=5 次中≥3 次到达的任务数）')
print('  臂     配方                           侧绕85        越顶80        可通过255      合计到达')
def row(name, desc, s):
    L, O, P = s('lateral'), s('overflight'), s('passable')
    print(f'  {name:5s}  {desc:28s} {L[0]:3d}/{L[1]:3d}/{L[2]:2d} K{L[3]}  {O[0]:3d}/{O[1]:3d}/{O[2]:2d} K{O[3]}  {P[0]:3d}/{P[1]:3d}/{P[2]:2d}   {L[0]+O[0]+P[0]}')
row('P6', '父策略 u256', lambda g: hist[('P6', g)])
for p, d in (('P18', 'F3 续训 u320（F7 对照）'), ('P19', 'F3 续训 u320（F7 对照）')): row(p, d, lambda g, p=p: hist[(p, g)])
for p, d in (('P22', 'F3 续训 u320（F8 对照）'), ('P23', 'F3 续训 u320（F8 对照）')): row(p, d, lambda g, p=p: cur[(p, g)])
for p, d in (('P20', 'F8 处理'), ('P21', 'F8 处理')): row(p, d, lambda g, p=p: cur[(p, g)])
for p, d in (('P16', 'F7 处理'), ('P17', 'F7 处理')): row(p, d, lambda g, p=p: hist[(p, g)])
ctl = [hist[('P18', 'lateral')][0], hist[('P19', 'lateral')][0], cur[('P22', 'lateral')][0], cur[('P23', 'lateral')][0]]
ctp = [hist[('P18', 'passable')][0], hist[('P19', 'passable')][0], cur[('P22', 'passable')][0], cur[('P23', 'passable')][0]]
print(f'  同配方四次对照：侧绕到达 {ctl}（极差 {max(ctl)-min(ctl)}），可通过到达 {ctp}（极差 {max(ctp)-min(ctp)}）')
print('\n== ③ 被挡任务逐任务到达次数 [P20, P21, P22, P23]（只列至少一臂有到达的任务）')
T = collections.defaultdict(dict)
for r in rd('evaluation_tasks.csv'):
    if r['split'] == 'dev' and r['group'] in ('lateral', 'overflight'): T[(r['group'], r['task_id'])][r['arm']] = int(r['reached'])
part = 0
for (g, t), v in sorted(T.items()):
    x = [v[a] for a in ARMS]
    if any(x): print(f'  {g[:4]} {t.split("rl_train__")[1][:58]:58s} {x}')
    part += sum(1 for k in x if 0 < k < 5)
print(f'  被挡任务 {len(T)} 个；四臂都为 0 的 {sum(1 for v in T.values() if not any(v.values()))} 个；任一臂有到达的 {sum(1 for v in T.values() if any(v.values()))} 个；'
      f'臂×任务中 1—4 次（非全有全无）的 {part} / {4*len(T)}')
print('\n== ④ 训练采集：密集世界（bottleneck、cul_de_sac、s_turn）已终止回合的到达率，前 32 轮 / 后 32 轮')
W = rd('training_world_updates.csv'); dense = lambda w: any(k in w for k in ('bottleneck', 'cul_de_sac', 's_turn'))
for a in ARMS:
    out = []
    for lo, hi in ((257, 288), (289, 320)):
        n = sum(int(r['terminal_episodes']) for r in W if r['arm'] == a and lo <= int(r['update']) <= hi and dense(r['world']))
        s = sum(int(r['reached']) for r in W if r['arm'] == a and lo <= int(r['update']) <= hi and dense(r['world']))
        out.append(f'{s}/{n} ({100*s/n:.1f}%)')
    print(f'  {a}: ' + '  →  '.join(out))
print('\n== ⑤ 训练记录（新层）')
U = rd('training_updates.csv'); print('  字段：', [k for k in U[0].keys()][:40])
CW = rd('collection_worlds.csv')
print('\n== ⑥ 建库：成功任务', sum(int(r['successful_tasks']) for r in CW), '；前缀', sum(int(r['prefixes']) for r in CW),
      '；引导飞行到达', sum(int(r['reached']) for r in CW), '/', sum(int(r['flights']) for r in CW))
