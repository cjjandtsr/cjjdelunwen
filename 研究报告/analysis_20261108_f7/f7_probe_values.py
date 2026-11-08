"""F7 行为探针手算期望值（只读，无外部依赖，numpy）。
提前接近速率项（reward v5 新增项 approach_cbf）：
  b_k = c_k - d_safe；对执行路径相邻两点 k→k+1（时长 dt_k）：
  v_k = -[(b_{k+1}-b_k)/dt_k + gamma*(b_k+b_{k+1})/2]
  raw = -w * sum_k dt_k * clip(v_k, 0, vmax)
  回合预算：term = max(raw, -(B - used))，used 为本回合此前累计 |term|
参数：d_safe=0.30 m, gamma=1/3 s^-1, w=2.0, vmax=2.0 m/s, B=4.0
自适应学习率：m_0=10；每轮后按该轮 clip_fraction 均值 c：c<0.05 → m*1.5；c>0.15 → m/1.5；m 限制在 [1,50]
"""
import numpy as np
D, G, W, VMAX, B = .30, 1/3, 2., 2., 4.

def cbf_raw(c, dt):
    b = np.asarray(c, float) - D
    dt = np.asarray(dt, float)
    v = -((b[1:] - b[:-1]) / dt + G * (b[1:] + b[:-1]) / 2)
    return -W * float(np.sum(dt * np.clip(v, 0, VMAX)))

def with_budget(raw, used):
    return max(raw, -(B - used))

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
]
for name, c, dt in cases:
    print("%-40s raw = %.6f" % (name, cbf_raw(c, dt)))
print("预算：此前已用 3.9，本决策 raw=-0.5 → term = %.6f" % with_budget(-.5, 3.9))
print("预算：此前已用 4.0，本决策 raw=-0.5 → term = %.6f" % with_budget(-.5, 4.0))
print("单决策上界 |raw| ≤ w*1.2*vmax = %.3f；回合累计 ≤ B = %.1f" % (W * 1.2 * VMAX, B))
# 成功-超时次序下界（R1 v1.4 §1.4 推导 5.5108；space 再减 1；本项再减 B）
print("G_success - G_timeout 下界 = 5.5108 - 1 - %.1f = %.4f" % (B, 5.5108 - 1 - B))

def lr_mult(seq, m=10.):
    out = [m]
    for c in seq:
        if c < .05: m = min(m * 1.5, 50.)
        elif c > .15: m = max(m / 1.5, 1.)
        out.append(m)
    return out
s = [0.0, 0.0, 0.20, 0.08, 0.03, 0.0, 0.0, 0.0, 0.0]
print("clip_fraction 序列", s)
print("倍率序列", ["%.4g" % x for x in lr_mult(s)])
