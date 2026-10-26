# 2026-10-05 Phase Beta 联网资料研究

| 字段 | 内容 |
|---|---|
| 文档类型 | 定期联网资料研究报告 |
| 检索日期 | 2026-10-05（Asia/Shanghai） |
| 状态 | 本期结论已归档；不构成训练、奖励或算法变更授权 |
| 对应 metadata | `论文/被参考/metadata/2026-10-05_PhaseBeta_联网资料研究_metadata.md` |
| 当前对象 | DDPM/DPPO、Reward v1.7、H4、11d step-wise action、冻结 EGO 数据 |

## 1. 本期项目上下文摘要

[FACT] 截至 2026-10-04，A0 三 seed 各完成 256 updates；回传包报告 847/847 hash 通过、三份训练 `.rc=0`、每 seed 256 份 metrics 与 33 个 checkpoint。该证据仅支持训练流程完整和数值健康，尚没有固定 paired dev 的 closed-loop safe-arrival 能力结论（`jindu/2026-10-04_RouteA_A0三seed收官与R1启动裁决_v1_0.md`）。

[FACT] R1 尚未开始训练。其第一次 smoke 因进程从 A0 editable-install 导入 `config_schema_v2.py` 而停止；已交付的修复只为 R1 smoke/训练进程显式设置 `PYTHONPATH="$ROOT"`，并要求实际导入来源、smoke 及其结果门禁均为 `.rc=0` 后才可训练（`jindu/2026-10-04_RouteA_R1_首次smoke导入路径阻断与续跑状态_v1_0.md`；`zhidao/2026-10-04_RouteA_R1_导入路径修复与续跑指导_v1_0.md`）。

[JUDGMENT] 因而本期研究问题是：在 R1 身份链与固定 paired dev 尚未关闭时，什么外部证据能收紧点云观测、safe-arrival 与 sim-to-real 的评价边界。不是换 RL 家族、替换点云编码、修改 H4、增加过滤器或以训练曲线裁决能力。

## 2. 检索范围与关键词

[FACT] 本轮于 2026-10-05 查询原始 arXiv 页面，优先使用论文作者提交的摘要/全文 HTML；搜索聚合页只用于发现候选，不作结论来源。

- 关键词：`point cloud UAV reinforcement learning sim-to-real cluttered flight`、`safe reinforcement learning embodied benchmark reward cost trade-off`、`diffusion policy PPO evaluation`、`UAV obstacle avoidance sparse sensing PPO`。
- 筛选规则：[JUDGMENT] 仅纳入能补充当前 R1 观测—策略身份、能力主终点或后续 Gazebo/实飞证据分层的资料。现有 DPPO/iDP3/测量不确定性资料仅复核身份，不重复下载；不把与当前静态三维点云、H4、11d action 不同的成果转写为可直接迁移的实现。

## 3. 候选资料总表

| ID | 标题；作者；年份 | 原始来源 / 标识 | 下载/归档 | 决定 |
|---|---|---|---|---|
| C1 | *Flying on Point Clouds with Reinforcement Learning*；Guangtong Xu, Tianyue Wu, Zihan Wang, Qianhao Wang, Fei Gao；2025 | https://arxiv.org/abs/2503.00496；arXiv:2503.00496 | 未下载 PDF；本期 metadata | 采纳：点云—轻量仿真—实飞证据链与窄空隙感知边界。 |
| C2 | *HASARD: A Benchmark for Vision-Based Safe Reinforcement Learning in Embodied Agents*；Tristan Tomilin, Meng Fang, Mykola Pechenizkiy；2025 | https://arxiv.org/abs/2503.08241；arXiv:2503.08241 | 未下载 PDF；本期 metadata | 有限采纳：难度、reward/cost 和过度保守行为的评价纪律。 |
| C3 | *Diffusion Policy Policy Optimization*；Allen Z. Ren 等；2024 | https://arxiv.org/abs/2409.00588；arXiv:2409.00588 | 已有 PDF，未重复下载 | 复核采纳：项目 DPPO 方法来源；不从机器人实验外推 UAV 能力。 |
| C4 | *Generalizable Humanoid Manipulation with 3D Diffusion Policies*；Tao Chen 等；2024 | https://arxiv.org/abs/2410.10803；arXiv:2410.10803 | 已有 iDP3 PDF，未重复下载 | 复核采纳：3D point-cloud diffusion policy 的项目上游方法边界。 |
| C5 | *Learning-Based Dynamic Obstacle Avoidance for a UAV Using Only Three Range Sensors*；Mohammad Reza Ranjbar Divkoti, A. Pedro Aguiar；2026 | https://arxiv.org/abs/2609.14426；arXiv:2609.14426 | 未下载、未归档 | 未采纳：固定高度、单 yaw 和行为栅格/PID 链与当前端到端三维轨迹 contract 不同。 |
| C6 | *Sim-to-Real Deep Reinforcement Learning based Obstacle Avoidance for UAVs under Measurement Uncertainty*；Bhaskar Joshi, Dhruv Kapur, Harikumar Kandath；2023 | https://arxiv.org/abs/2303.07243；arXiv:2303.07243 | 已有 2026-07 metadata，未重复下载 | 复核采纳：测量偏差与方差必须分开评估；不迁移其外部去噪器。 |

## 4. 被采纳资料与核心贡献

### C1：点云飞行的正确用途是收紧感知和证据层，不是替换当前策略

[FACT] C1 报告使用机载 3D LiDAR、轻量点云 surrogate 与 sim-to-real RL，在杂乱环境中以低层控制接口飞行，并将窄自由空间/细障碍的保留视作点云表示的关键；论文报告有实机飞行，但其策略、控制层、传感器和训练环境均不同于 iDP3-UAV。

[JUDGMENT] 对本项目最直接的增量是：R1/R1 后评估应把“观测身份正确”与“障碍几何可分辨性仍足够”分开留证。R1 导入来源门禁、H4 point-cloud metadata 历史、同输入重复一致性和窄净空/dense 分层应构成连续证据链；它们不是让项目改用 C1 surrogate、低层控制或新传感器的授权。

### C2：避免把低碰撞或平滑曲线误当作有效安全能力

[FACT] C2 的安全 RL 基准把 performance 与 safety cost 的权衡、不同难度和观察条件显式分开，并显示安全约束方法可能出现过度保守、低回报或不稳定约束满足。它是视觉 Doom 基准，不是 UAV、点云、DPPO 或 Gazebo/PX4。

[JUDGMENT] 本项目只能迁移其评价纪律：报告 safe-arrival、collision、timeout、dense rescue/break、onset 提前量及动作/更新健康，而不是用单一 reward、平均 cost、KL 或“无碰撞”宣布突破。此建议支持保持预注册预算和固定 paired dev；不支持立刻引入 Lagrangian、PID safety controller、硬 cost budget 或 curriculum。

### C3、C4、C6：复核既有主线和部署边界

[FACT] C3 仍是现有 DPPO 的方法来源，C4 是已有 iDP3 3D diffusion-policy 上游资料；两者已有本地 PDF。C6 显示测量偏差和随机噪声会产生不同的安全到达响应，并报告从仿真向真机的测试，但其二维高层 PPO 与外部低通/Kalman 去噪不符合当前策略内归因边界。

[JUDGMENT] 因此 R1 若通过 smoke 和完整训练，也只能先进入 lightweight/kinematic 的固定 paired dev；通过后才可设计与执行 Gazebo/PX4 闭环。未来进入 sim-to-real 时，观测扰动应至少分 bias/variance、近障碍/细障碍、空间包络三轴记录；不能把部署滤波后的改善归到扩散策略本身。

## 5. 未采纳资料与原因

- [JUDGMENT] C5 使用固定高度、单自由度 yaw、栅格状态和 PID 跟踪，其动态障碍与三测距传感器结果不能回答本项目的 full-space support 或 11d chunk trajectory 问题。将行为栅格或 PID 链接入会额外改变感知与执行归因，故不归档、不迁移。
- [JUDGMENT] 含 waypoint 图搜索、外部 shield、trajectory projection、后处理平滑、人工 avoidance-state、二级目标或动态奖励切换的候选持续排除：它们会重写或间接重写执行轨迹，违反 MC-1/MC-3/MC-5。
- [JUDGMENT] 本轮未再采纳新的 FM-RL、DSRL、离线 IQL 或 action-chunking 算法。R1 当前是 DDPM/DPPO 的导入来源与最小 smoke 阻断；切换算法会把工程身份故障、观测契约与参数化差异混为一因。

## 6. 对 iDP3-UAV 的可迁移建议

| Phase β 最终目标 | 应保留的证据与门禁 | 本期资料带来的边界 |
|---|---|---|
| 提前避障 | paired dev 的首次偏航/横移 onset、到障时间、最小净空、绕障后 safe-arrival；同任务/输入/噪声下比较 BC、A0、R1 | [JUDGMENT] C2 表明不能只优化 cost 或碰撞计数；提前量必须与终点成功并列。 |
| full-space support expansion | 按起点和目标 x/y/z 包络、目标方位、距离分层报告 safe-arrival/collision/timeout；记录 point-cloud 有效性与细障碍/窄净空覆盖 | [JUDGMENT] C1 支持把几何可分辨性保留为单独证据，不允许只用 z 变化或平均成功率代替全空间覆盖。 |
| dense-obstacle capability ceiling | dense role 的 safe-arrival、collision、timeout、rescue/break、净空与分母（任务×seed）；保留失败样本和动作多样性 | [JUDGMENT] C1/C2 都不支持删去困难 world、把超时藏入均值或用强约束把策略压成不动。 |

[JUDGMENT] 当前可立即执行的下一步仍是现有 R1 导入来源—smoke—结果门禁；本报告不新建代码、配置或实验。R1 训练完整后，先冻结 paired dev 的任务/reset/采样流和统计分母，再进行 BC/A0/R1 的多 seed capability 比较。

## 7. MC 合规检查

| 约束 | 本期检查 |
|---|---|
| MC-1 策略输出 = 执行轨迹 | [JUDGMENT] 未建议 projection、外部避障、waypoint 跟踪或后处理平滑。 |
| MC-2 Diffusion policy 是核心 | [JUDGMENT] 保持 DDPM/DPPO 和 iDP3 point-cloud policy 为当前对象；C1/C2 仅约束证据链。 |
| MC-3 学习阶段处理约束 | [JUDGMENT] 不采纳 C6 的外部 LPF/Kalman、C5 的 PID/栅格链，安全约束仍须通过策略内学习与训练 reward。 |
| MC-4 EGO 数据 frozen | [FACT] 本期没有重采数据；w4/w8/w11/w12/w18 继续仅用于评估/回归，不可进入训练或 replay。 |
| MC-5 归因可分离 | [JUDGMENT] lightweight/kinematic、Gazebo/PX4 与实机证据分层；观测滤波、控制器或外部 planner 的收益不能归因于策略。 |

[JUDGMENT] 本期建议仅涉及评价、溯源与后续证据分层，不改变推理时轨迹。已证伪方向持续排除：`yaw_loss_boost > 1`、5d action、策略外障碍排斥/GOAL-TRUNC/后平滑、DAC offline RL、TransDiffuser decorrelation loss、`torch.compile + CFG`。

## 8. 风险与不确定性

- [UNCERTAIN] C1 的全文实验合同与项目不同，且本期仅核验原始 arXiv 页面；它不能证明 R1 点云 encoder、H4 或 Gazebo/PX4 部署可靠。
- [UNCERTAIN] C2 的任务为视觉 Doom，不能据其基准比较推导项目 reward 系数、cost threshold 或算法优劣。
- [JUDGMENT] 若 R1 导入来源仍未实际指向独立 checkout，则任意 smoke/训练输出都缺失可信源码身份，不得用于能力比较。
- [JUDGMENT] 用滤波、过强惩罚、过度 KL/clip、早停或删除 dense/失败样本换取漂亮曲线，会抹掉探索、成功条件梯度、提前避障与脱困信号；继续按既有学习信号门禁裁决。

## 9. 下一步建议

1. [FACT] 先执行并回传现有 R1 `PYTHONPATH` 导入来源门禁、smoke 与 smoke-gate 的完整日志和 `.rc`；未通过前不启动 R1 三 seed。
2. [JUDGMENT] R1 完整训练后，先冻结 paired dev 的任务、reset、噪声流、点云 metadata 与任务×seed 分母，再比较 BC/A0/R1；训练期 reward/KL 不是安全到达结论。
3. [JUDGMENT] paired dev 若显示改善，才设计 Gazebo/PX4 闭环验证，并将点云有效性、近障碍/窄净空与 x/y/z support 分层随原始轨迹归档；不得把 lightweight 结果写成 Gazebo/PX4 结论。
4. [FACT] 本期仅新增本报告和 metadata；未运行训练、未操作 WSL、ROS、Gazebo、PX4、checkpoint，也未改动训练代码或配置。
