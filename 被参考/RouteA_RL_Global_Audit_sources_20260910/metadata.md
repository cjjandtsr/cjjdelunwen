# Route A RL 全链审计与修复研究来源元数据

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-09-10 |
| 用途 | Route A RL 全链诊断、官方 DPPO/PPO 语义核对、终止截断语义、实现细节敏感性与多任务梯度冲突候选方案 |
| 来源原则 | 论文原文、作者官方仓库、框架官方文档；不以博客或二手总结支撑确定性结论 |

## 已本地归档

| 文件 | 一手来源 | 本项目引用用途 |
|------|----------|----------------|
| `PPO_arxiv_1707.06347.pdf` | https://arxiv.org/abs/1707.06347 | PPO clipped surrogate 与近端更新理论基线 |
| `Time_Limits_arxiv_1712.00378.pdf` | https://arxiv.org/abs/1712.00378 | 区分真正终止与外部时间截断，裁决 bootstrap 语义 |
| `Implementation_Matters_arxiv_2005.12729.pdf` | https://arxiv.org/abs/2005.12729 | 说明 PPO 代码级实现选择会实质改变算法行为，支持对训练循环做逐项 parity |
| `PCGrad_arxiv_2001.06782.pdf` | https://arxiv.org/abs/2001.06782 | 仅作为测得跨能力梯度冲突后的二线候选；不直接视为当前修复 |

## 仓库内既有归档

| 位置 | 一手来源 | 本项目引用用途 |
|------|----------|----------------|
| `../metadata/2409.00588v3.pdf` | https://arxiv.org/abs/2409.00588 | DPPO 双层 MDP、去噪 transition、官方实验依据 |
| `../../../chengxu/Improved-3D-Diffusion-Policy/third_party/dppo_official_cc7234a/` | https://github.com/irom-princeton/dppo | 冻结提交的官方代码 oracle；联合 environment x denoising 索引空间 |
| `../RouteA_FormalTraining_sources_20260828/CleanRL_PPO_logged_metrics_20260828.md` | https://github.com/vwxyzjn/cleanrl | PPO KL、clip fraction、explained variance 等实现和日志基准 |

## 已联网核对但未新增网页快照

以下官方网页在 2026-09-10 已在线核对。追加快照时执行端额度限制触发，因此报告保留直接 URL，并不把网页未归档部分当作唯一证据；相同核心事实另有本地论文或 vendor 代码支持。

- DPPO 官方仓库：https://github.com/irom-princeton/dppo
- DPPO 当前 `diffusion_ppo.py`：https://github.com/irom-princeton/dppo/blob/main/model/diffusion/diffusion_ppo.py
- DPPO 当前训练循环：https://github.com/irom-princeton/dppo/blob/main/agent/finetune/train_ppo_diffusion_agent.py
- DPPO finetuning 说明：https://github.com/irom-princeton/dppo/blob/main/cfg/finetuning.md
- Gymnasium time-limit 文档：https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/
- PyTorch reproducibility 文档：https://docs.pytorch.org/docs/stable/notes/randomness.html
- CleanRL PPO：https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo.py
- Policy Gradient Theorem 原论文：https://papers.nips.cc/paper/1713-policy-gradient-methods-for-reinforcement-learning-with-function-approximation
- PCGrad 作者官方仓库：https://github.com/tianheyu927/PCGrad

## 使用边界

- DPPO 当前 `main` 可能相对冻结提交发生变化；实现裁决以仓库内 `cc7234a` vendor 为直接 oracle，当前 `main` 仅作交叉验证。
- 普通 Gaussian PPO 的 KL 阈值、entropy 与 batch 超参不得机械移植到 diffusion PPO。
- PCGrad 官方仓库当前公开的是 TensorFlow 实现；没有证据前不得直接引入非官方 PyTorch 复刻。
