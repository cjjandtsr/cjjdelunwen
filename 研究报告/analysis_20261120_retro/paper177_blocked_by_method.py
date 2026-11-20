"""只读：论文 177 个运动学测试任务按"起点到目标直线是否被挡"分层，比较各方法（含 EGO、Fast-Planner、SUPER）的任务成功。
用法：python3 -I paper177_blocked_by_method.py <论文实验数据主表.xlsx> <障碍文件目录> <collision_geom.py 所在目录>
障碍文件 = 项目仓库 `PX4-Autopilot-Tools/sitl_gazebo/worlds/**/<场景ID>.world.obstacles.json`（main 6efc8c42）。
被挡 = 直线最小净空 <0.3 m（0.05 m 采样，与 dev420 分析同一口径）。坐标系：先用世界坐标；同时报告目标最小净空作坐标核对
（项目约定所有目标距障碍 ≥1.63 m）。任务成功 = 主表重复1—5 中“成功”≥2 次（与主表“任务成功_1或0”公式一致，1.5 m）。"""
import sys, os, json, collections, openpyxl
import numpy as np
X, WD, CG = sys.argv[1:4]
sys.path.insert(0, CG)
from collision_geom import ObstacleSpec, compute_obstacle_clearance
wb = openpyxl.load_workbook(X, read_only=True)
T = {}
for r in list(wb['任务清单'].iter_rows(values_only=True))[4:]:
    if r[0] and r[3] == 1: T[r[0]] = dict(scene=r[1], diff=r[2], s=np.array(r[5:8], float), g=np.array(r[8:11], float))
S = collections.defaultdict(dict)
for r in list(wb['运动学明细'].iter_rows(values_only=True))[4:]:
    if r[1] in T: S[r[2]][r[1]] = int(sum(x == '成功' for x in r[3:8]) >= 2)   # 与主表公式一致：5 次中“成功”≥2
def clear_pt(p, obs): return compute_obstacle_clearance(*p, obs)[0]
def line(a, b, obs):
    n = int(np.linalg.norm(b - a) / .05) + 2
    return min(clear_pt(a + t * (b - a), obs) for t in np.linspace(0, 1, n))
miss = 0; gmin = []; grp = {}
for k, t in T.items():
    f = os.path.join(WD, t['scene'] + '.world.obstacles.json')
    if not os.path.exists(f): miss += 1; continue
    obs = [ObstacleSpec.from_dict(o) for o in json.load(open(f))['obstacles']]
    gmin.append(clear_pt(t['g'], obs))
    grp[k] = 'blocked' if line(t['s'], t['g'], obs) < .3 else 'passable'
print(f'任务 {len(T)}；缺障碍文件 {miss}；目标点净空最小 {min(gmin):.2f} m、低于 1.6 m 的 {sum(x < 1.6 for x in gmin)} 个（坐标核对）')
c = collections.Counter(grp.values()); print('分层', dict(c), '；按难度', dict(collections.Counter((T[k]['diff'], g) for k, g in grp.items())))
print('\n方法                        被挡任务成功          可通过任务成功')
for m, d in S.items():
    b = [d[k] for k in grp if grp[k] == 'blocked' and k in d]; p = [d[k] for k in grp if grp[k] == 'passable' and k in d]
    print(f'  {m:26s} {sum(b):3d}/{len(b):3d} ({100*sum(b)/len(b):5.1f}%)    {sum(p):3d}/{len(p):3d} ({100*sum(p)/len(p):5.1f}%)')
