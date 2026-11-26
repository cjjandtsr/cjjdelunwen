"""只读：正面接近平面障碍时，v2 风险项（障碍部分）、v3 risk_close 与 F7 approach_cbf 的单决策数值对比。
用法：python3 reward_compare.py ；只需 numpy。公式分别按 env/reward_v2_support/reward.py（_barrier(c,0.45,0.10)，0.5×权重，取各段最大）、
env/reward_v3.py（closing_cost）与 F7 方案 §3.1 转写；路径为 4 段 × 0.3 s，净空逐段减少 v×0.3。"""
import numpy as np
def v2_obst(cs):   # 执行段风险（只算障碍部分，权重 1；段净空取段终点，近似）
    return -max(.5 * float(np.clip((.45 - c) / .35, 0, 1) ** 2) for c in cs[1:])
def v3(cs):
    cs = np.asarray(cs); closing = np.maximum(0, cs[:-1] - cs[1:]); bar = np.clip((1.2 - cs[1:]) / 1.1, 0, 1) ** 2
    return -4 * min(float((closing * bar).sum()), .5)
def cbf(cs, dt=.3, g=1/3, ds=.3, w=2.):
    b = np.asarray(cs) - ds; v = -((b[1:] - b[:-1]) / dt + g * (b[1:] + b[:-1]) / 2)
    return -w * dt * float(np.clip(v, 0, 2).sum())
for v in (0.63, 1.0, 2.0):
    print("速度 %.2f m/s（每决策前进 %.2f m）；approach_cbf 开始扣分的净空 ≈ d_safe + 3v = %.2f m" % (v, 1.2 * v, .3 + 3 * v))
    print("  决策起点净空 |   v2 风险 |  v3 接近 | F7 approach_cbf")
    for c0 in (6.0, 4.0, 3.0, 2.5, 2.0, 1.6, 1.3, 1.0):
        cs = [c0 - v * .3 * k for k in range(5)]
        if cs[-1] < .1: continue
        print("  %10.1f m | %9.3f | %8.3f | %8.3f" % (c0, v2_obst(cs), v3(cs), cbf(cs)))
