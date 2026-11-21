"""前置研究 ② 补充：加入竖直视场后的可观测性（读 pre2_observability.py 输出的 pre2_rows.json）。
用法：python3 pre2b_vertical_fov.py pre2_rows.json
相机（Codex 11-16 提供）：竖直视场 46.83°，下俯 8°，即俯仰角范围 [-31.415°, +15.415°]；水平 ±30°。未考虑遮挡和机体姿态变化。"""
import json, sys, numpy as np
B = json.load(open(sys.argv[1]))['B']; UP, DN = -8 + 46.83 / 2, -8 - 46.83 / 2
for name, sel in (('全部', lambda b: True), ('越顶任务', lambda b: b['over']), ('侧绕任务', lambda b: not b['over'])):
    for back in (4, 3, 2, 1):
        X = [b for b in B if b['back'] == back and sel(b)]
        h = np.array([abs(b['bearing']) <= 30 for b in X]); v = np.array([DN <= b['elev'] <= UP for b in X]); up = np.array([b['elev'] > UP for b in X])
        print('%s，碰撞前第 %d 个决策（n=%d）：水平视场内 %.0f%%；竖直视场内 %.0f%%（高于上缘 %.0f%%）；两者都在 %.0f%%；俯仰中位 %.0f°' % (name, back, len(X), 100 * h.mean(), 100 * v.mean(), 100 * up.mean(), 100 * (h & v).mean(), np.median([b['elev'] for b in X])))
