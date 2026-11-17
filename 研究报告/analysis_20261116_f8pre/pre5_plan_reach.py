"""补充检验：8 步规划能"看"多远，相对于到碰撞点的距离（dev420 #E2 原迹，直线被挡的 33 个任务，P6、P18、P19 的碰撞回合；只作诊断）。
用法：python3 -I pre5_plan_reach.py <项目仓库根目录> <blocked_tasks_dev420.json>
规划长度 = planned_policy_path 的折线长度；到碰撞点的剩余路程 = 从该决策起点沿实际执行路径到回合终点的长度。
"规划够得着" = 规划长度 ≥ 到碰撞点的剩余路程。"""
import ast, glob, gzip, json, math, sys, numpy as np
repo, blk = sys.argv[1], set(json.load(open(sys.argv[2])))
plen = lambda P: sum(math.dist(a, b) for a, b in zip(P[:-1], P[1:]))
SRC = glob.glob(f'{repo}/jindu/routea_f5_run01/results/eval_dev/full/P6/traces/*.jsonl') + glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P18/traces/*.jsonl.gz') + glob.glob(f'{repo}/jindu/routea_f7_run01/eval_dev/P19/traces/*.jsonl.gz')
R = {b: [] for b in range(1, 9)}; n = 0
for f in SRC:
    L = [json.loads(l) for l in (gzip.open if f.endswith('.gz') else open)(f, 'rt')]
    if L[0]['task_id'] not in blk or L[-1]['done_reason'] != 'collision': continue
    T = [t for t in L if t.get('type') == 'transition']; n += 1
    ex = [plen(t['executed_path']) for t in T]
    for b in R:
        k = len(T) - 1 - b
        if k >= 0: R[b].append((plen(T[k]['planned_policy_path']), sum(ex[k:])))
print('碰撞回合数', n)
for b, v in R.items():
    v = np.array(v); print('碰撞前第 %d 个决策（n=%d）：规划长度中位 %.2f m；到碰撞点剩余路程中位 %.2f m；规划够得着的比例 %.0f%%' % (b, len(v), np.median(v[:, 0]), np.median(v[:, 1]), 100 * np.mean(v[:, 0] >= v[:, 1])))
