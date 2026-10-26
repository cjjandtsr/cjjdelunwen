# 2026-07-06 PhaseBeta 联网资料研究：被采纳资料元数据说明

| 字段 | 内容 |
|------|------|
| 说明类型 | 被参考资料元数据说明 / 网页快照替代说明 |
| 检索日期 | 2026-07-06 |
| 对应研究报告 | `C:\Users\cjj\Desktop\IDP3\论文\研究报告\2026-07-06_PhaseBeta_联网资料研究.md` |
| 保存原因 | 本轮实际引用资料以 arXiv / 官方项目页为主；本文件记录 URL、arXiv ID、采纳用途与归档状态，作为未下载 PDF 时的可追溯元数据说明。 |

## 被采纳资料

| # | 标题 | 作者 | 年份 | 来源 URL | DOI / arXiv ID | 下载状态 | 引用用途 |
|---|---|---|---|---|---|---|---|
| 1 | Reverse Flow Matching: A Unified Framework for Online Reinforcement Learning with Diffusion and Flow Policies | Zeyang Li, Sunbochen Tang, Navid Azizan | 2026 | https://arxiv.org/abs/2601.08136 | arXiv:2601.08136 | 未下载；保存元数据说明 | 支撑 Route A v2 可考虑 Q-value + Q-gradient 的 flow-policy update，但需先完成 critic/Q-scale gate。 |
| 2 | Reinforcement Learning for Flow-Matching Policies | Samuel Pfrommer, Yixiao Huang, Somayeh Sojoudi | 2025 | https://arxiv.org/abs/2507.15073 | arXiv:2507.15073 | 未下载；保存元数据说明 | 支撑 reward-weighted FM / GRPO-style FM fine-tune 可作为 ReinFlow 后的备选。 |
| 3 | Flow Matching Policy Gradients | David McAllister et al. | 2025 | https://arxiv.org/abs/2507.21053 | arXiv:2507.21053 | 未下载；保存元数据说明 | 支撑 FPO / PPO-clip 风格 flow policy gradient，可作为 DPPO 与 ReinFlow 之间的备选。 |
| 4 | Efficient Online Reinforcement Learning Fine-Tuning Need Not Retain Offline Data | Zhiyuan Zhou, Andy Peng, Qiyang Li, Sergey Levine, Aviral Kumar | 2024 | https://arxiv.org/abs/2412.07762 | arXiv:2412.07762 | 未下载；保存元数据说明 | 支撑 warmup / recalibration phase，解释 current online immediate update 的 critic divergence 风险。 |
| 5 | Online Pre-Training for Offline-to-Online Reinforcement Learning | Yongjae Shin et al. | 2025 | https://arxiv.org/abs/2507.08387 | arXiv:2507.08387 | 未下载；保存元数据说明 | 支撑为 online distribution 单独训练 value function，再进入 fine-tune。 |
| 6 | Efficient Online RL Fine Tuning with Offline Pre-trained Policy Only | Wei Xiao et al. | 2025 | https://arxiv.org/abs/2505.16856 | arXiv:2505.16856 | 未下载；保存元数据说明 | 支撑 BC/FM policy-only 起点下需要在线快速初始化 Q，而不是假设已有可用 offline critic。 |
| 7 | Curriculum Reinforcement Learning for Quadrotor Racing with Random Obstacles | Fangyu Sun et al. | 2026 | https://arxiv.org/abs/2602.24030 | arXiv:2602.24030 | 未下载；保存元数据说明 | 支撑 obstacle-rich UAV RL 需要 curriculum、multi-scene update、domain randomization 和真实/HIL 验证。 |
| 8 | Ambient Diffusion Policy: Imitation Learning from Suboptimal Data in Robotics | Adam Wei et al. | 2026 | https://arxiv.org/abs/2606.12365 | arXiv:2606.12365 | 未下载；保存元数据说明 | 支撑 diffusion-time / noise-dependent data usage 思路；本项目只迁移为诊断，不建议重采数据。 |
| 9 | Sim-to-Real Deep Reinforcement Learning based Obstacle Avoidance for UAVs under Measurement Uncertainty | Bhaskar Joshi, Dhruv Kapur, Harikumar Kandath | 2023 | https://arxiv.org/abs/2303.07243 | arXiv:2303.07243 | 未下载；保存元数据说明 | 支撑 UAV sim-to-real 阶段必须显式处理测量噪声和真实部署验证。 |
| 10 | Cal-QL: Calibrated Offline RL Pre-Training for Efficient Online Fine-Tuning | Mitsuhiko Nakamoto et al. | 2023 | https://arxiv.org/abs/2303.05479 | arXiv:2303.05479 | 既有归档；本轮复用 | 支撑 Q-scale calibration 是正式训练前门禁，不应只看 loss finite。 |
| 11 | Diffusion Policy Policy Optimization | 作者见 arXiv | 2024 | https://arxiv.org/abs/2409.00588 | arXiv:2409.00588 | 既有归档；本轮复用 | 支撑 DPPO 仍是保守 fallback，不是当前 reward/trainer wiring 的替代品。 |
| 12 | ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning | 作者见 arXiv | 2025 | https://arxiv.org/abs/2505.22094 | arXiv:2505.22094 | 既有归档；本轮复用 | 支撑 Route A 默认仍以 FM policy 本体 fine-tune 为核心。 |

## 未采纳但记录的资料

| 标题 | 来源 URL | 未采纳原因 |
|------|----------|------------|
| Flow Matching for Offline Reinforcement Learning with Discrete Actions | https://arxiv.org/abs/2602.06138 | [JUDGMENT] 重点是离散动作 / action quantization；本项目 Action 11d chunk 不改维、不离散化，当前迁移价值低。 |
| VFP: Variational Flow-Matching Policy for Multi-Modal Robot Manipulation | https://arxiv.org/abs/2508.01622 | [JUDGMENT] 主要面向操作任务多模态；可作为后续 mode latent 背景，但不支撑当前 P0 trainer/reward 修复。 |
| Extending Group Relative Policy Optimization to Continuous Control | https://arxiv.org/abs/2507.19555 | [JUDGMENT] 偏理论框架；缺少足够实证，不作为当前 Route A 裁决依据。 |
| Sim-to-Real Transfer for Mobile Robots with Reinforcement Learning | https://arxiv.org/abs/2501.02902 | [JUDGMENT] ROS/Gazebo local navigation 有参考价值，但非 UAV/PX4，当前不用于报告结论。 |

