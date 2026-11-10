"""只读：dev420 #E2 原迹中的飞行速度与重规划情况（BC 与 P6@u256）。
用法：python3 -I speed_profile.py <traces-root> bc P6
traces-root = <项目仓库>/jindu/routea_f5_run01/results/eval_dev/full（每个策略目录下 traces/*.jsonl）
速度 = 执行路径相邻点距离 / 段时长（executed_time_s / 段数）；只统计未截断（done_reason=none）的完整决策。"""
import json, os, sys, math, statistics as st
root = sys.argv[1]
def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
for pol in sys.argv[2:]:
    d = os.path.join(root, pol, 'traces'); seg, dec, pre_v, post_v, nseg = [], [], [], [], []
    for f in sorted(os.listdir(d)):
        for l in open(os.path.join(d, f)):
            t = json.loads(l)
            if t.get('type') != 'transition' or t['done_reason'] != 'none': continue
            P = t['executed_path']; n = len(P) - 1; dt = t['executed_time_s'] / n; nseg.append(n)
            s = [math.dist(a, b) / dt for a, b in zip(P[:-1], P[1:])]; seg += s
            dec.append(math.dist(P[0], P[-1]) / t['executed_time_s'])
            pre_v.append(math.hypot(*t['pre_state']['velocity'])); post_v.append(math.hypot(*t['post_state'].get('velocity', [0, 0, 0])))
    print('== %s：完整决策 %d 个，每决策执行段数 %s，时长 1.2 s' % (pol, len(dec), sorted(set(nseg))))
    print('  分段速度 m/s：中位数 %.2f，p10 %.2f，p90 %.2f，最大 %.2f' % (st.median(seg), q(seg, .1), q(seg, .9), max(seg)))
    print('  每决策位移 / 1.2 s：中位数 %.2f m/s，每决策前进中位数 %.2f m' % (st.median(dec), 1.2 * st.median(dec)))
    print('  记录的决策起点速度：中位数 %.2f，非零比例 %.2f；决策终点速度中位数 %.2f' % (st.median(pre_v), sum(v > 1e-6 for v in pre_v) / len(pre_v), st.median(post_v)))
