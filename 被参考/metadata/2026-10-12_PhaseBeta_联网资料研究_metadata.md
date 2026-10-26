# 2026-10-12 Phase Beta 联网资料研究：资料元数据

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-10-12（Asia/Shanghai） |
| 对应报告 | `论文/研究报告/2026-10-12_PhaseBeta_联网资料研究.md` |
| 归档方式 | 本期三项实际引用资料以已有本地副本或官方网页/代码元数据说明归档；未下载新的 PDF。 |
| 使用边界 | 只支撑 Route A 当前配对评价、几何分层和仿真—部署证据边界；不授权算法、奖励、H4、点云编码或控制链变更。 |

## A1. DPPO 方法身份与政策梯度边界

- 标题：Diffusion Policy Policy Optimization。
- 作者：Allen Z. Ren、Justin Lidard、Lars L. Ankile、Anthony Simeonov、Pulkit Agrawal、Anirudha Majumdar、Benjamin Burchfiel、Hongkai Dai、Max Simchowitz。
- 年份：2024。
- 原始来源：https://arxiv.org/abs/2409.00588；项目页：https://diffusion-ppo.github.io/；官方代码：https://github.com/irom-princeton/dppo。
- 标识：arXiv:2409.00588；DOI：https://doi.org/10.48550/arXiv.2409.00588。
- 本期下载：否；已有副本：`论文/被参考/Diffusion Policy Policy Optimization.pdf`。
- 实际引用用途：[FACT] 支持当前 DDPM/DPPO 作为 Route A 方法身份，并界定其结论仍必须由本项目固定配对 safe-arrival 原始证据裁决。
- 与 iDP3-UAV 的相关性：[JUDGMENT] 高（diffusion policy 的 PPO 微调）；机器人基准不等价于 UAV、3D 点云、H4 或 Gazebo/PX4 的能力证明。

## A2. UAV 避障基准的环境—性能分层

- 标题：AvoidBench: A High-Fidelity Vision-Based Obstacle Avoidance Benchmarking Suite for Multi-Rotors。
- 作者：Hang Yu、Guido C. H. E. de Croon、Christophe De Wagter。
- 年份：2023。
- 原始来源：https://arxiv.org/abs/2301.07430；官方代码：https://github.com/tudelft/AvoidBench；出版社页：https://ieeexplore.ieee.org/document/10161097/。
- 标识：arXiv:2301.07430；DOI：https://doi.org/10.1109/ICRA48891.2023.10161097。
- 本期下载：否；已有来源说明：`论文/被参考/2026-06-29_PhaseBeta_联网资料研究_sources.md`。
- 实际引用用途：[FACT] 支持将真实几何/可通行性和多项飞行表现指标分层，并保持仿真与实机结果分开解释。
- 与 iDP3-UAV 的相关性：[JUDGMENT] 高（UAV 避障与复杂度评价）；其视觉、Flightmare/Unity 与控制接口不同，不能直接复用为当前点云策略或评估环境。

## A3. 密集环境中安全—推进并报的反例边界

- 标题：MAVRL: Learn to Fly in Cluttered Environments With Varying Speed。
- 作者：Hang Yu、Christophe De Wagter、Guido C. H. E. de Croon。
- 年份：2025。
- 原始来源：官方代码 https://github.com/tudelft/mavrl；出版社页：https://ieeexplore.ieee.org/document/10816139。
- 标识：IEEE Robotics and Automation Letters 10(2):1441-1448；DOI：https://doi.org/10.1109/LRA.2024.3522778。
- 本期下载：否；本文件为实际引用的官方代码/书目元数据说明。
- 实际引用用途：[FACT] 官方仓库公开其 depth-VAE/LSTM/PPO、复杂度相关变速和 AvoidBench/实机评估的系统构成。报告只用它支持同时报告安全到达、碰撞、超时与目标推进，拒绝迁移其模型或控制链。
- 与 iDP3-UAV 的相关性：[JUDGMENT] 中等（UAV、RL、杂乱避障）；输入、表征、动作、速度控制、训练流程均与当前项目不同，不能外推性能或实现。

## 本期未归档候选

- D²PPO: Diffusion Policy Policy Optimization with Dispersive Loss；Guowei Zou 等；2025；arXiv:2508.02644；https://arxiv.org/abs/2508.02644：未采纳。当前没有项目点云表征坍塌的可复现证据，新增正则会破坏当前退化归因。
- Flow Policy Gradients for Robot Control；Brent Yi 等；2026；arXiv:2602.02481；https://arxiv.org/abs/2602.02481：未采纳。FM-RL 不解决当前 DDPM/DPPO 同任务配对退化归因。
- AEOS: Active Environment-aware Optimal Scanning Control for UAV LiDAR-Inertial Odometry in Complex Scenes；Jianping Li 等；2025；arXiv:2509.09141；https://arxiv.org/abs/2509.09141：未采纳。MPC 与主动扫描属于不同的里程计/感知控制任务。

[FACT] 本文件不保存未采用候选的副本；上述实际引用资料均于本期通过作者/项目维护的官方页、官方代码或 IEEE/arXiv 页面核验。
