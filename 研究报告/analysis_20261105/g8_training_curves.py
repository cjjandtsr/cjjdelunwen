#!/usr/bin/env python3
"""G8 两阶段后训练过程（论文线数据）。

运行：
  第一阶段与不中断续训：B2560 运行（单阶段后训练 P2 = 其第 128 轮；P3 = 同一运行第 256 轮）
    项目仓库 jindu/2026-10-25_P1_P7信息核查/training_curve_512.csv 中 arm=b2560 的行
  第二阶段（从第 128 轮分叉）：A2 的 C 臂（两阶段后训练 P4）与 T 臂（本文方法 P6）
    项目仓库 jindu/routea_a2_selective_keep_run01/arms/{C,T}/metrics_update_000129—000256.json
注意：metrics_update_u 中的采集由第 u−1 轮参数完成；训练采集含扰动、中途状态初始化与随机任务，
采集到达率不能与确定性评价的到达率直接比较。
输出：<OUT>/g8_per_update.csv（逐轮）、<OUT>/g8_blocks.csv（每 16 轮汇总，到达率 = 块内到达总数/完成回合总数）
用法：python3 -I g8_training_curves.py <项目仓库 jindu 目录> <OUT>
"""
import csv, json, os, statistics, sys

J, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
rows = []
for r in csv.DictReader(open(os.path.join(J, '2026-10-25_P1_P7信息核查', 'training_curve_512.csv'), encoding='utf-8-sig')):
    if r['arm'] != 'b2560':
        continue
    rows.append(dict(run='不中断' if int(r['update']) > 128 else '第一阶段', update=int(r['update']),
                     completed=int(r['completed']), reached=int(r['reached']), collision=int(r['collision']),
                     time_limit=int(r['time_limit']), approx_kl=float(r['approx_kl']), keep_loss='', keep_ratio=''))
for arm, name in (('C', '两阶段后训练'), ('T', '本文方法')):
    for u in range(129, 257):
        m = json.load(open(os.path.join(J, 'routea_a2_selective_keep_run01', 'arms', arm, f'metrics_update_{u:06d}.json')))
        e = m['rollout_audit']['episodes']; pc = e['physical_done_reason_counts']
        kd = [x['pre_update'].get('keep_diagnostics') for x in m['updates']]
        kd = [k for k in kd if k]
        rows.append(dict(run=name, update=u, completed=e['completed'], reached=pc.get('reached', 0),
                         collision=pc.get('obstacle_collision', 0) + pc.get('ground_crash', 0),
                         time_limit=pc.get('time_limit', 0),
                         approx_kl=m['formal_training']['optimizer_metric_summary']['approx_kl']['mean'],
                         keep_loss=statistics.mean(k['keep_loss'] for k in kd) if kd else '',
                         keep_ratio=statistics.mean(k['ratio'] for k in kd) if kd else ''))
keys = list(rows[0].keys())
with open(os.path.join(OUT, 'g8_per_update.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT, 'g8_blocks.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['运行', '轮次', '完成回合', '到达率', '碰撞率', '超时率', 'approx_kl均值', '保持项/PPO梯度范数比均值'])
    for run in ['第一阶段', '不中断', '两阶段后训练', '本文方法']:
        rr = [r for r in rows if r['run'] == run]
        for a in range(min(r['update'] for r in rr), max(r['update'] for r in rr) + 1, 16):
            b = [r for r in rr if a <= r['update'] < a + 16]
            c = sum(r['completed'] for r in b)
            kr = [r['keep_ratio'] for r in b if r['keep_ratio'] != '']
            w.writerow([run, f'{a}-{a + 15}', c, round(sum(r['reached'] for r in b) / c, 3),
                        round(sum(r['collision'] for r in b) / c, 3), round(sum(r['time_limit'] for r in b) / c, 3),
                        f"{statistics.mean(r['approx_kl'] for r in b):.2e}", round(statistics.mean(kr), 3) if kr else ''])
print('done', len(rows))
