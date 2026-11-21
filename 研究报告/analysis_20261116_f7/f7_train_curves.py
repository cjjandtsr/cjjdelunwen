"""只读：F7 run01 四臂 u257—u320 训练采集的结局与更新幅度（每 8 轮一段）。
用法：python3 -I f7_train_curves.py <项目仓库根目录>
数据：jindu/routea_f7_run01/train/<P>/metrics_update_*.json.gz 的 rollout_audit.transition_records（terminated/truncated/terminal_facts、f7_audit）与 formal_training。
训练采集的到达按训练环境 0.5 m 结局（reward_terms.terminal > 0）计。"""
import glob, gzip, json, os, sys, statistics as st, collections, math
repo = sys.argv[1]
for P in ('P16', 'P17', 'P18', 'P19'):
    fs = sorted(glob.glob(f'{repo}/jindu/routea_f7_run01/train/{P}/metrics_update_*.json.gz'))
    rows = []
    for f in fs:
        d = json.load(gzip.open(f)); ft = d['formal_training']; s = ft['optimizer_metric_summary']; tr = d['rollout_audit']['transition_records']
        ends = [t for t in tr if t['terminated'] or t['truncated']]
        term = [t['reward_terms'].get('terminal', 0) for t in ends if t['terminated']]
        succ = sum(x > 0 for x in term); coll = sum(x < 0 for x in term); trunc = sum(1 for t in ends if t['truncated'] and not t['terminated'])
        cbf = [t['f7_audit']['approach_cbf_diagnostic'] for t in tr if t.get('f7_audit')]
        sp = [math.dist(t['position_before_xyz'], t['position_after_xyz']) / 1.2 for t in tr]
        rows.append((succ, coll, trunc, s['approx_kl']['mean'], s['clip_fraction']['mean'], ft['actor_learning_rate'], sum(c < 0 for c in cbf) / max(len(cbf), 1), st.median(sp)))
    print('==', P)
    for i in range(0, 64, 8):
        b = rows[i:i + 8]; S, C, T = (sum(r[j] for r in b) for j in range(3)); n = S + C + T
        print('  u%d—u%d：结束回合 %d，到达 %.0f%%，碰撞 %.0f%%，超时 %.0f%%；KL %.1e；clip %.3f；actor 学习率 %.2e；接近项非零 %.1f%%；决策速度中位 %.2f m/s' % (
            257 + i, 264 + i, n, 100 * S / n, 100 * C / n, 100 * T / n, st.mean(r[3] for r in b), st.mean(r[4] for r in b), st.mean(r[5] for r in b), 100 * st.mean(r[6] for r in b), st.mean(r[7] for r in b)))
