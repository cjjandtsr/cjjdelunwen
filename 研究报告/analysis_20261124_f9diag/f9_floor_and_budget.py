"""只读：F9 阶段 A/A2 教师层的损失底噪、优化器步长预算与门槛量复算（只需 numpy）。

用法：
  python3 f9_floor_and_budget.py <stageA2_return 解包根> <stageA2_restart 解包根> <stageA_return 解包根>
  三个根目录分别是项目仓库分支 f9-pack/run01-20261122（提交 aab9a49）中
    jindu/f9_run01_20261122/stageA2/routea_f9_stageA2_return_20261124.tar.gz
    jindu/f9_run01_20261122/stageA2_restart/routea_f9_stageA2_restart_20261124.tar.gz
    jindu/f9_run01_20261122/stageA/routea_f9_stageA_return_20261122.tar.gz
  解包后的顶层目录（含 measure/、run/ 或 P28/）。
读取：
  measure/offline/{grid,P6,P35|P36}.json —— 留出集逐决策、逐去噪时间步的 x0 回归损失
  run/<P>/metrics_update_*.json        —— 每次优化器提交前的诊断（教师层损失、梯度比、余弦、KL）
  run/<P>/f9_update_*.json             —— 每轮 94 个 LoRA 张量的更新范数
  run/<P>/gate.json                    —— 门槛判定用的 r、D
"""
import glob, json, sys
from pathlib import Path
import numpy as np

A2, A2R, A = map(Path, sys.argv[1:4])
RUN = {'P35': A2/'run/P35', 'P36': A2R/'run/P36', 'P28': A/'P28'}
OFF = {'P35': A2/'measure/offline', 'P36': A2R/'measure/offline'}

print('== 1. 留出集逐时间步损失（P6 与处理臂，同一冻结噪声）')
for k, d in OFF.items():
    grid = json.load(open(d/'grid.json'))
    p6 = np.array([r['timestep_losses'] for r in json.load(open(d/'P6.json'))['rows']])
    t = np.array([r['timestep_losses'] for r in json.load(open(d/(k+'.json')))['rows']])
    print(k, '留出决策数', len(t))
    print('  时间步       ', grid['timesteps'])
    print('  alpha_bar    ', np.round(grid['alphas'], 4).tolist())
    print('  P6 损失      ', np.round(p6.mean(0), 4).tolist())
    print('  %s 损失     ' % k, np.round(t.mean(0), 4).tolist())
    print('  比值         ', np.round(t.mean(0)/p6.mean(0), 3).tolist())
    print('  r = %.4f；P6 在 t=0 的损失占其总均值 %.1f%%；%s 在 t=0 的损失 / P6 总均值 = %.3f'
          % (t.mean()/p6.mean(), 100*p6.mean(0)[-1]/p6.mean(), k, t.mean(0)[-1]/p6.mean()))

print('== 2. 每次提交前的诊断（160 次提交）')
for k, b in RUN.items():
    rows = []
    for f in sorted(glob.glob(str(b/'metrics_update_*.json'))):
        for u in json.load(open(f))['updates']:
            p = u['pre_update']; g = p['f8_keep_diagnostics']; q = p['keep_diagnostics']
            rows.append((g['keep_loss'], q['keep_loss'], g['ratio'], g['cosine'], g['layers_cosine'],
                         p['actor_grad_clipped'], p['approx_kl'], p['clip_fraction']))
    x = np.array(rows, float)
    print('%s 提交 %d；教师层损失 前40 %.4f 后40 %.4f；原保持层损失中位 %.4f；梯度比中位 %.3f；'
          '与PPO余弦中位 %.3f；与原保持层余弦中位 %.3f；被裁剪 %d 次；每轮末次提交前 approx_kl 最大 %.2e；clip_fraction 最大 %.4f'
          % (k, len(x), x[:40, 0].mean(), x[-40:, 0].mean(), np.median(x[:, 1]), np.median(x[:, 2]),
             np.median(x[:, 3]), np.median(x[:, 4]), int(x[:, 5].sum()), x[:, 6].max(), x[:, 7].max()))

print('== 3. LoRA 更新量与 Adam 步长预算')
n, lr, commits = 1022568, 1e-5, 160
bound = lr*commits*np.sqrt(n)
print('逐元素每步约 lr 时的向量上限 lr*提交数*sqrt(元素数) = %.3f（每轮 20 次提交为 %.3f）' % (bound, bound/8))
for k, b in RUN.items():
    per, ra, rb = [], [], []
    for f in sorted(glob.glob(str(b/'f9_update_*.json'))):
        d = json.load(open(f))['lora_update_by_parameter']
        v = np.array(list(d.values())); per.append(np.sqrt((v**2).sum()))
        ra.append(np.sqrt(sum(x**2 for m, x in d.items() if m.endswith('lora_a'))))
        rb.append(np.sqrt(sum(x**2 for m, x in d.items() if m.endswith('lora_b'))))
    g = json.load(open(b/'gate.json'))
    print('%s 每轮范数 %s；逐轮之和 %.3f（上限的 %.0f%%）；A/B 每轮均值 %.3f/%.3f；r=%s D_T=%.4f D_C=%.4f 到达 %d/%d'
          % (k, np.round(per, 3).tolist(), sum(per), 100*sum(per)/bound, np.mean(ra), np.mean(rb),
             None if g['r'] is None else round(g['r'], 4), g['D_T'], g['D_C'], g['T_arrivals'], g['C_arrivals']))
print('端到端范数（WSL 侧报告，本脚本未复算，缺检查点）：P29 0.302，P28 0.884，P36 1.366')
