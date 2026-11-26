#!/usr/bin/env python3
"""O′ 初步合并（只读，不含区间）。
输入：
  原 O（540 回合）各策略结局：研究报告/analysis_20261105/ch4/o_class.csv 与
  研究报告/analysis_20261106/g17/g17_main.csv（P14），此处以常量写入并在下方断言自洽；
  新增 455 回合与 P15 995 回合：Codex《最终实验v1.3工程验收与交接》(2026-11-07) 表格。
运行：python3 -I 研究报告/analysis_20261107/o_prime_prelim.py
本脚本只做计数相加；区间与分类须用逐回合原始记录重算。
"""
O = {  # 到达, 碰撞, 超时 （原 O，540）
    'P0': (187, 147, 206), 'P2': (261, 130, 149), 'P4': (273, 163, 104),
    'P6': (289, 152, 99), 'P14': (84, 119, 337)}
ADD = {  # 新增 455（适中、密集）
    'P0': (84, 236, 135), 'P2': (143, 213, 99), 'P3': (108, 217, 130),
    'P4': (126, 242, 87), 'P6': (166, 199, 90), 'P14': (29, 197, 229)}
P15 = (260, 337, 398)  # O′ 995
SPARSE_O = {'P0': 128, 'P6': 208}  # 原 O 稀疏类到达（295 回合）
for k, v in O.items(): assert sum(v) == 540, k
for k, v in ADD.items(): assert sum(v) == 455, k
assert sum(P15) == 995
op = {k: tuple(a + b for a, b in zip(O[k], ADD[k])) for k in O}
op['P15'] = P15
print('策略,O′到达,碰撞,超时,到达率%')
for k, v in op.items():
    print(f'{k},{v[0]},{v[1]},{v[2]},{100*v[0]/995:.1f}')
print('差值（百分点，O′）')
for a, b in [('P6','P0'),('P15','P0'),('P15','P14'),('P15','P6'),('P2','P0'),('P14','P0'),('P6','P4'),('P6','P2')]:
    print(f'{a}-{b},{100*(op[a][0]-op[b][0])/995:+.1f}')
print('新增 455 回合（适中+密集）到达率%')
for k, v in ADD.items(): print(f'{k},{100*v[0]/455:.1f}')
md = {k: op[k][0] - SPARSE_O[k] for k in SPARSE_O}
print('O′ 适中+密集（700 回合）到达率%', {k: round(100*v/700, 1) for k, v in md.items()})
