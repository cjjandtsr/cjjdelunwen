# ReinFlow 官方代码快照元数据

| 字段 | 内容 |
|------|------|
| 检索与下载日期 | 2026-08-22 |
| 上游仓库 | https://github.com/ReinFlow/ReinFlow |
| 本地只读快照 | `论文/被参考/ReinFlow_official/` |
| commit | `e722e151bed767f3ffef47527cf697f2358af55d` |
| 上游 commit 日期 | 2026-04-24 18:34:21 -0400 |
| commit 标题 | `Update README.md` |
| 许可证 | MIT License；复用或修改包含其代码的文件时必须保留版权与许可声明 |
| 对应论文 | ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning，arXiv:2505.22094，NeurIPS 2025 |
| 项目网页 | https://reinflow.github.io/ |
| 引用用途 | 审计官方随机 Flow sampler、noise injection network、Markov-chain logprob、PPO loss、buffer、GAE、checkpoint 与 action chunking 实现；用于设计 iDP3-UAV 的 FM 强化学习后训练系统 |
| 当前状态 | 上游快照未修改；尚未接入 iDP3-UAV 训练分支 |

## 首要审计入口

- `model/flow/ft_ppo/ppoflow.py`：随机 Flow sampler、chain logprob、PPO ratio/loss。
- `model/flow/mlp_flow.py`：`FlowMLP`、`ExploreNoiseNet`、`NoisyFlowMLP`。
- `agent/finetune/reinflow/train_ppo_flow_agent.py`：rollout、buffer、更新、noise schedule、checkpoint。
- `agent/finetune/reinflow/buffer.py`：`PPOFlowBuffer` 与 environment-time GAE。
- `docs/Implement.md`：官方超参数与扩展建议。
- `docs/Custom.md`：自定义 observation history 与环境 wrapper 边界。

## 使用边界

- 该快照是上游证据和后续移植基准，不是本项目当前可运行训练代码。
- 上游原生策略为 MLP/ViT 风格 Flow policy，不直接支持 iDP3 点云编码、conditional U-Net、CFG、LoRA 或现有 UAV environment contract。
- 后续若采用上游代码，应保留 MIT 声明，并记录相对该 commit 的修改清单与 parity tests。
