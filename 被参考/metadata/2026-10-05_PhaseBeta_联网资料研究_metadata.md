# 2026-10-05 Phase Beta 联网资料研究：资料元数据

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-10-05（Asia/Shanghai） |
| 对应报告 | `论文/研究报告/2026-10-05_PhaseBeta_联网资料研究.md` |
| 归档方式 | 本期两项新采纳资料以官方 arXiv 元数据说明归档，未下载 PDF；三项既有实际引用资料仅核验已有本地副本/metadata，不重复副本。 |
| 使用边界 | 支撑评价、观测溯源和 sim-to-real 证据分层；不构成算法/奖励/传感器/控制器变更。 |

## A1. 点云端到端飞行与 sim-to-real 证据链（本期新采纳）

- 标题：Flying on Point Clouds with Reinforcement Learning。
- 作者：Guangtong Xu, Tianyue Wu, Zihan Wang, Qianhao Wang, Fei Gao。
- 年份：2025。
- 原始来源：https://arxiv.org/abs/2503.00496
- 标识：arXiv:2503.00496；DOI：https://doi.org/10.48550/arXiv.2503.00496。
- 本期下载：否；本文件为实际引用的官方元数据说明。
- 实际引用用途：[FACT] 原始摘要称其使用机载 3D LiDAR、点云 surrogate 和 sim-to-real RL，并以窄自由空间/细障碍的几何表示与实飞验证为关键。报告只据此要求把 R1 point-cloud identity/几何可分辨性、lightweight 和 Gazebo/PX4/实飞证据分层留痕。
- 与 iDP3-UAV 的相关性：[JUDGMENT] 高（UAV、点云、密集障碍、sim-to-real）；但其 RL policy、低层控制、传感器和训练环境不同，不能外推为 DDPM/DPPO/H4 的性能或实施方案。

## A2. 安全 RL 的能力—安全权衡评价纪律（本期新采纳）

- 标题：HASARD: A Benchmark for Vision-Based Safe Reinforcement Learning in Embodied Agents。
- 作者：Tristan Tomilin, Meng Fang, Mykola Pechenizkiy。
- 年份：2025。
- 原始来源：https://arxiv.org/abs/2503.08241
- 标识：arXiv:2503.08241；DOI：https://doi.org/10.48550/arXiv.2503.08241。
- 本期下载：否；本文件为实际引用的官方元数据说明。
- 实际引用用途：[FACT] 原始页面通过不同难度、reward/cost 及多种安全 RL baseline 展示了安全—任务完成权衡和过度保守风险。报告仅用其支持同时报告 safe-arrival、collision、timeout、dense rescue/break、onset 与训练健康，而不以单一安全量裁决。
- 与 iDP3-UAV 的相关性：[JUDGMENT] 中等（安全 RL 评价原则）；其视觉 Doom、动作空间、算法与项目点云 UAV 不同，不能作为 reward 系数或安全控制器实现来源。

## A3. 既有 DPPO 方法来源（本期复核并引用）

- 标题：Diffusion Policy Policy Optimization。
- 作者：Allen Z. Ren 等。
- 年份：2024。
- 原始来源：https://arxiv.org/abs/2409.00588
- 标识：arXiv:2409.00588；DOI：https://doi.org/10.48550/arXiv.2409.00588。
- 本期下载：否；已有副本：`论文/被参考/Diffusion Policy Policy Optimization.pdf`；已有官方代码说明：`论文/被参考/DPPO_Official_Code_cc7234a_metadata.md`。
- 实际引用用途：[FACT] 作为现有 diffusion-policy PPO fine-tuning 方法来源；本期仅支持维持 R1 的 DPPO 归因和先关 smoke 身份链，不外推其机器人结果为 UAV 能力。

## A4. 既有 iDP3 上游方法来源（本期复核并引用）

- 标题：Generalizable Humanoid Manipulation with 3D Diffusion Policies。
- 作者：Tao Chen 等。
- 年份：2024。
- 原始来源：https://arxiv.org/abs/2410.10803
- 标识：arXiv:2410.10803；DOI：https://doi.org/10.48550/arXiv.2410.10803。
- 本期下载：否；已有副本：`论文/被参考/iDP3 - Generalizable Humanoid Manipulation with 3D Diffusion Policies - arxiv_2410.10803.pdf`。
- 实际引用用途：[FACT] 用作项目 3D point-cloud diffusion-policy 的上游方法边界；本期不将 humanoid manipulation 结果外推为 UAV 避障能力。

## A5. 既有测量不确定性与 UAV sim-to-real 边界（本期复核并引用）

- 标题：Sim-to-Real Deep Reinforcement Learning based Obstacle Avoidance for UAVs under Measurement Uncertainty。
- 作者：Bhaskar Joshi, Dhruv Kapur, Harikumar Kandath。
- 年份：2023。
- 原始来源：https://arxiv.org/abs/2303.07243
- 标识：arXiv:2303.07243；DOI：https://doi.org/10.48550/arXiv.2303.07243。
- 本期下载：否；已有归档说明：`论文/被参考/2026-07-06_PhaseBeta_联网资料研究_sources.md` 与 `metadata/2026-07-06_PhaseBeta_联网资料研究_metadata.md`。
- 实际引用用途：[FACT] 原页面区分观测偏差/方差并报告仿真到实机的测试。报告仅据此要求未来将 bias/variance 与空间/近障碍分层记录；不采纳其外部 LPF/Kalman 或二维高层 PPO 设计。

## 本期未归档候选

- Learning-Based Dynamic Obstacle Avoidance for a UAV Using Only Three Range Sensors；Mohammad Reza Ranjbar Divkoti, A. Pedro Aguiar；2026；arXiv:2609.14426；https://arxiv.org/abs/2609.14426：未采纳。固定高度、单 yaw、行为栅格与 PID 控制不满足当前端到端 3D/11d H4 trajectory contract，迁移会引入不可分离变量。

[FACT] 本文件不保存未采用候选的副本；所有列出的原始 URL 均于本期通过官方 arXiv 页面核验。
