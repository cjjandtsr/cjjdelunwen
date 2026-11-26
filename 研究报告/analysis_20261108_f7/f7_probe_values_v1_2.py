"""F7 v1_2 行为探针手算期望值（只读，numpy）。
提前接近速率项 approach_cbf（v1_2：无回合预算，只依赖本决策的执行路径与几何）：
  b_k = c_k - d_safe；对执行路径相邻两点 k→k+1（时长 dt_k）：
  dt_k = 0 的段贡献记 0；否则 v_k = -[(b_{k+1}-b_k)/dt_k + gamma*(b_k+b_{k+1})/2]
  term = -w * sum_k dt_k * clip(v_k, 0, vmax)
参数：d_safe=0.30 m, gamma=1/3 s^-1, w=2.0（标定备选 1.0）, vmax=2.0 m/s
自适应学习率（v1_2）：m_0=5；每轮后按该轮 clip_fraction 均值 c：c<0.05 → m*1.5；c>0.15 → m/1.5；m 限制在 [1,20]
"""
import numpy as np
D, G, VMAX = .30, 1/3, 2.

def cbf(c, dt, w=2.):
    b = np.asarray(c, float) - D; dt = np.asarray(dt, float); tot = 0.
    for k in range(len(dt)):
        if dt[k] == 0: continue
        v = -((b[k+1] - b[k]) / dt[k] + G * (b[k] + b[k+1]) / 2)
        tot += dt[k] * min(max(v, 0.), VMAX)
    return -w * tot

def line(c0, speed, n=4, dt=.3):
    return [c0 - speed * dt * k for k in range(n + 1)], [dt] * n

cases = [
    ("正面接近 0.45 m/s，起点净空 1.6 m", *line(1.6, .45)),
    ("正面接近 0.45 m/s，起点净空 1.3 m", *line(1.3, .45)),
    ("正面接近 0.45 m/s，起点净空 2.5 m（应为 0）", *line(2.5, .45)),
    ("减速到 0.10 m/s，起点净空 1.0 m（应为 0）", *line(1.0, .10)),
    ("切向掠过，净空恒 0.5 m（应为 0）", [.5] * 5, [.3] * 4),
    ("切向掠过，净空恒 0.25 m（b<0）", [.25] * 5, [.3] * 4),
    ("远离障碍 0.45 m/s，起点 0.8 m（应为 0）", [0.8 + .45 * .3 * k for k in range(5)], [.3] * 4),
    ("碰撞截断：两段 0.3 s + 一段 0.1 s", [0.40, 0.25, 0.12, 0.10], [.3, .3, .1]),
    ("首点即事件：零时长段（应为 0，无 NaN）", [0.10, 0.10], [0.]),
    ("零时长段夹在中间：0.3 s + 0 s", [0.60, 0.465, 0.465], [.3, 0.]),
]
for name, c, dt in cases:
    print("%-40s w=2: %.6f   w=1: %.6f" % (name, cbf(c, dt), cbf(c, dt, 1.)))
print("单决策上界 |term| ≤ w*1.2*vmax = %.3f（w=2）" % (2 * 1.2 * VMAX))

def lr_mult(seq, m=5.):
    out = [m]
    for c in seq:
        if c < .05: m = min(m * 1.5, 20.)
        elif c > .15: m = max(m / 1.5, 1.)
        out.append(m)
    return out
s = [0.0, 0.0, 0.20, 0.08, 0.03, 0.0, 0.0, 0.0, 0.0]
print("clip_fraction 序列", s)
print("倍率序列（第 1 个为 u257 所用）", ["%.6g" % x for x in lr_mult(s)])
print("对应 actor 学习率", ["%.4g" % (1e-5 * x) for x in lr_mult(s)])
