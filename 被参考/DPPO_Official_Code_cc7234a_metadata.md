# DPPO 官方代码来源元数据

| 字段 | 内容 |
|------|------|
| 资料名称 | Diffusion Policy Policy Optimization 官方实现 |
| 上游仓库 | https://github.com/irom-princeton/dppo |
| 固定 commit | `cc7234ad7ff39a8f32de3af903606723a16f0648` |
| commit 查询日期 | 2026-08-06 |
| 许可证 | MIT |
| 论文 | *Diffusion Policy Policy Optimization*，arXiv:2409.00588 |
| 论文 URL | https://arxiv.org/abs/2409.00588 |
| PPO loss 源文件 | https://github.com/irom-princeton/dppo/blob/cc7234ad7ff39a8f32de3af903606723a16f0648/model/diffusion/diffusion_ppo.py |
| 训练循环源文件 | https://github.com/irom-princeton/dppo/blob/cc7234ad7ff39a8f32de3af903606723a16f0648/agent/finetune/train_ppo_diffusion_agent.py |
| 本地论文副本 | `论文/被参考/Diffusion Policy Policy Optimization.pdf` |
| iDP3-UAV 引用用途 | A-Official-Core 的 per-step logprob、reward horizon、denoising credit、PPO clipping、GAE 与训练循环语义基准 |
| 采用状态 | 已采用为设计与后续数值 parity oracle；正式实施时须固定该 commit 并保存 vendor SHA256 |

## 相关性判断

[FACT] 官方实现保留 `(B,K,H_action,D_action)` logprob，以 environment transition × denoising transition 为 PPO sample，对 logprob 逐元素裁剪后截取 executed-action reward horizon，再对 action/time 维求均值。

[JUDGMENT] 这些语义可用于纠正项目现有 joint-scalar logprob、ghost action、dead epsilon schedule 和 termination mask 问题。

[JUDGMENT] 官方仓库不包含 iDP3-UAV 的 point-cloud encoder、Phase1aPolicy、CFG、AnchorHead、LoRA、11d action、Route A task semantics 或 Gazebo/PX4 接口，因此只能作为冻结 core/oracle，通过项目 adapter 接入，不直接取代整个项目。

## 追溯要求

正式实施时需同时保存：

- 官方 commit；
- vendor 文件 SHA256；
- MIT LICENSE；
- 项目 adapter commit；
- 官方—项目数值 parity 输出。

