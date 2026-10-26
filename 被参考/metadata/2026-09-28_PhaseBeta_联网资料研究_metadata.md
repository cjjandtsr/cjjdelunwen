# 2026-09-28 Phase Beta 联网资料研究：资料元数据

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-09-28（Asia/Shanghai） |
| 对应报告 | `论文/研究报告/2026-09-28_PhaseBeta_联网资料研究.md` |
| 归档方式 | 本期新采纳资料以可复核的官方 arXiv 元数据说明归档；未下载 PDF。既有资料仅核验身份并引用其已有归档，不重复副本。 |
| 范围 | Phase β、DDPM/DPPO、信用诊断、点云观测一致性、三维 UAV 避障与安全评估。 |

## A1. Online diffusion-policy RL 分类与瓶颈（本期新采纳）

- 标题：A Review of Online Diffusion Policy RL Algorithms for Scalable Robotic Control。
- 作者：Wonhyeok Choi, Shutong Ding, Minwoo Choi, Jungwan Woo, Kyumin Hwang, Jaeyeul Kim, Ye Shi, Sunghoon Im。
- 年份/版本：2026，arXiv v2（2026-02-09）。
- 原始来源：https://arxiv.org/abs/2601.06133
- 标识：arXiv:2601.06133；DOI https://doi.org/10.48550/arXiv.2601.06133 。
- 本期下载：否；本文件为实际引用的元数据说明。
- 实际引用用途：[FACT] 原页面将在线 diffusion-policy RL 按 action-gradient、Q-weighting、proximity 与 BPTT 分类，并报告计算/优化可扩展性瓶颈。报告据此只支持“算法家族选择应晚于当前合同/观测失败关闭”，不采纳其任何算法替换或性能数值。
- 与 iDP3-UAV 的相关性：[JUDGMENT] 高（diffusion-policy RL 方法层）；但其统一 Isaac Lab 机器人基准不是 UAV、不是本项目 H4/11d contract，故不能外推能力。

## A2. 可变高度三维 UAV 避障的奖励切换反例（本期新采纳）

- 标题：UAV Obstacle Avoidance by Human-in-the-Loop Reinforcement in Arbitrary 3D Environment。
- 作者：Xuyang Li, Jianwu Fang, Kai Du, Kuizhi Mei, Jianru Xue。
- 年份：2023。
- 原始来源：https://arxiv.org/abs/2304.05959
- 标识：arXiv:2304.05959。
- 本期下载：否；本文件为实际引用的元数据说明。
- 实际引用用途：[FACT] 原页面研究可变高度/速度的三维连续控制，但通过人工识别避障状态、设置二级目标并切换奖励。报告仅用其问题设定说明“变量高度”不等同于完整 x/y/z support expansion；不采纳其人工标签、二级目标或动态奖励切换。
- 与 iDP3-UAV 的相关性：[JUDGMENT] 中等（UAV、三维避障）；方法与本项目固定奖励合同、端到端轨迹归因及 MC-5 不兼容，不能作为实现来源。

## A3. 安全评估分布报告（既有资料，本期复核并引用）

- 标题：Evaluation Metrics for Safe Reinforcement Learning。
- 作者：Lindsay Spoor, Aske Plaat, Thomas Moerland。
- 年份：2026。
- 原始来源：https://arxiv.org/abs/2609.15315
- 标识：arXiv:2609.15315；DOI https://doi.org/10.48550/arXiv.2609.15315 。
- 本期下载：否；已有引用记录：`metadata/2026-09-21_PhaseBeta_联网资料研究_metadata.md`。
- 实际引用用途：[FACT] 原摘要主张平均安全指标不足，应联合报告聚合、分布和任务/安全界限特异结果。本期仅将其用于 safe-arrival、collision、timeout 与 role/任务分层并列呈现的报告纪律。

## A4. 远端目标信用的机制线索（既有资料，本期复核并引用）

- 标题：Improving Offline Goal-Conditioned Reinforcement Learning via Selective Reward Stimulation。
- 作者：Jing Zhang。
- 年份：2026。
- 原始来源：https://arxiv.org/abs/2609.19414
- 标识：arXiv:2609.19414。
- 本期下载：否；已有引用记录：`metadata/2026-09-21_PhaseBeta_联网资料研究_metadata.md`。
- 实际引用用途：[FACT] 原摘要讨论稀疏、远端 goal reward 下 value separation 可小于局部估计误差。本期只用作“目标响应/信用应通过冻结反事实测量”的问题动机；不采纳 RSIQL、off-policy IQL 或额外奖励。

## A5. 主线 DPPO 方法来源（既有资料，本期复核并引用）

- 标题：Diffusion Policy Policy Optimization。
- 作者：Allen Z. Ren 等。
- 年份/版本：2024，arXiv v3（2024-12-09）。
- 原始来源：https://arxiv.org/abs/2409.00588
- 标识：arXiv:2409.00588；DOI https://doi.org/10.48550/arXiv.2409.00588 。
- 本期下载：否；既有副本/来源说明：`论文/被参考/Diffusion Policy Policy Optimization.pdf` 与 `论文/被参考/DPPO_Official_Code_cc7234a_metadata.md`。
- 实际引用用途：[FACT] 原摘要给出 diffusion policy 的 policy-gradient fine-tuning 框架及其实验条件。本期仅复核 DPPO 仍是项目方法来源；不将其机器人实验外推为本项目 UAV 能力或现有实现正确性。

## 本期未归档候选

- Safe Multi-Agent Navigation guided by Goal-Conditioned Safe Reinforcement Learning，Meng Feng 等，2025，arXiv:2502.17813，https://arxiv.org/abs/2502.17813：未采纳。其 replay-state graph、unsafe-edge pruning 和 waypoint plan 属于策略外高层规划，破坏 MC-1/MC-5 归因边界。
- Reinforcement Learning for Flow-Matching Policies，Samuel Pfrommer 等，2025，arXiv:2507.15073，https://arxiv.org/abs/2507.15073：未采纳。已知 FM-RL 方向但不能解决当前 DDPM/H4 观测与诊断合同；切换会新增不可分离变量。

[FACT] 本文件不包含从未用于报告结论的资料副本；所有 URL 于本期通过原始 arXiv 页面核验。
