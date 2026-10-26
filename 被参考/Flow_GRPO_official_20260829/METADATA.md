# Flow-GRPO 官方资料归档元数据

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-08-29 |
| 资料状态 | 已采用：用于 FM+Flow-GRPO 路线理论与工程可迁移性核验 |
| 论文 | *Flow-GRPO: Training Flow Matching Models via Online RL* |
| 会议 | NeurIPS 2025 |
| arXiv | 2505.05470v5 |
| arXiv URL | https://arxiv.org/abs/2505.05470 |
| DOI | 10.48550/arXiv.2505.05470 |
| 官方代码 | https://github.com/yifan123/flow_grpo |
| 本地 PDF | `论文/被参考/Flow_GRPO_official_20260829/Flow-GRPO_arxiv_2505.05470.pdf` |
| 本地 README 快照 | `论文/被参考/Flow_GRPO_official_20260829/README_20260829.md` |

## 完整性

- PDF SHA256：`30CF4C2638CF6AB85CCAE4737C5C9FD5C1FC2B42E082B70E26635C8C39A71139`
- README SHA256：`9EA3AA6A42F8DD88E4852F2171EBB33F0DF70DB393302F099B7CF4B8A9833A9B`

## 引用用途

- [FACT] 核验算法正式名称为 **Flow-GRPO**，不是 Flow-GROP / flow-grop。
- [FACT] 核验两项数学核心：ODE-to-SDE 等边际转换与 Denoising Reduction。
- [FACT] 核验原论文实验范围为文本到图像生成，而非机器人控制、UAV、三维点云或 PX4/Gazebo。
- [JUDGMENT] 该资料可支持“FM 可通过 SDE 化后进行 GRPO 优化”的理论可行性，不能直接支持“该算法已适用于 iDP3-UAV”。

## iDP3-UAV 相关性与 MC 边界

- [JUDGMENT] ODE-to-SDE 随机化发生在 flow 采样路径内部，原则上可满足 MC-1~MC-3。
- [JUDGMENT] 原项目的 T2I reward server、prompt grouping、diffusers pipeline 和图像质量 KL 不能直接迁移到 UAV 环境。
- [RISK] 当前 iDP3-UAV 只有 4 步 Euler；原论文的 40 步推理、10 步训练 Denoising Reduction 收益不能外推。
- [RISK] UAV group rollout 必须保证同一状态/同一任务条件，否则 group-relative advantage 混入场景难度差异，破坏 MC-5 归因。
