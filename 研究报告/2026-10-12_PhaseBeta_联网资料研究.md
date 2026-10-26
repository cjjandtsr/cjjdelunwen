# 2026-10-12 Phase Beta 联网资料研究

| 字段 | 内容 |
|---|---|
| 文档类型 | 定期联网资料研究报告 |
| 检索日期 | 2026-10-12（Asia/Shanghai） |
| 状态 | 已归档；不构成训练、奖励、环境或部署变更授权 |
| 对应 metadata | `论文/被参考/metadata/2026-10-12_PhaseBeta_联网资料研究_metadata.md` |
| 当前对象 | Route A DDPM/DPPO；Reward v1.7；H4；11d step-wise action；冻结 EGO 数据 |

## 1. 本期项目上下文摘要

[FACT] 最新统一评价记录确认：当前唯一评价入口是 `scripts/run_routea_paired_comparison.py`；权重差异由运行时 `--checkpoint` 表达。u32 专用入口和旧 shell controller 已删除，重构未改变 H4、冻结任务或策略输出（`jindu/2026-10-11_RouteA_统一评价程序精简与重复代码删除记录_v2_0.md`）。

[FACT] BC、A0、R1 三 seed 的 u256 同任务 lightweight/kinematic 配对评价已经完成，不是 PX4/Gazebo 或实飞结果。420 条件/策略的首次安全到达率为 BC 27.62%，A0 三 seed 7.62%、16.90%、14.05%，R1 三 seed 2.62%、0%、24.05%。R1 seed203 在密集来源任务相对 BC +4.67pp，但两个 R1 seed 严重退化；目前只能表述为存在局部有效行为，整体能力尚未达标（`jindu/2026-10-10_RouteA_历史轨迹与A0_R1分环境比较及独立验收_v1_1.md`）。

[FACT] 任务名称或障碍数不等于真实难度：新 84 task 中仅 29 条起点—目标直连路径受阻；R1 seed203 密集来源的净增成功主要来自直线可达任务。因此不能将“dense”名称或总体推进直接写成复杂绕障/脱困突破。

[JUDGMENT] 本期问题不是替换 DPPO、改 H4、增加表征正则或引入外部控制，而是如何将已观察的局部收益与大范围退化放入可复核的能力证据链：固定配对、几何/空间分层、完整失败分母，以及 lightweight 与 Gazebo/PX4 的分层。

## 2. 检索范围与关键词

[FACT] 本轮于 2026-10-12 检索 arXiv、IEEE/TU Delft 官方页及作者维护的官方代码仓库；搜索聚合页只用于发现候选，结论仅依托下表的原始页或官方仓库。

- 关键词：`diffusion policy PPO safe navigation`、`flow matching policy reinforcement learning robot control`、`UAV point cloud reinforcement learning obstacle avoidance sim-to-real`、`safe reinforcement learning navigation collision benchmark`、`UAV cluttered environments varying speed`。
- [JUDGMENT] 筛选原则：优先补齐三类 Phase β 目标的评价与迁移边界；只有能直接约束当前证据链且不引入不可分离变量的资料才采纳。既有 DPPO、iDP3、AvoidBench 资料不重复下载。

## 3. 候选资料总表

| ID | 标题；作者；年份 | 原始来源 / 标识 | 下载或归档 | 决定 |
|---|---|---|---|---|
| C1 | *Diffusion Policy Policy Optimization*；Allen Z. Ren 等；2024 | https://arxiv.org/abs/2409.00588；arXiv:2409.00588 | 已有 PDF；本期复核 metadata | 采纳：DDPM/DPPO 方法与 policy-gradient 边界。 |
| C2 | *AvoidBench: A High-Fidelity Vision-Based Obstacle Avoidance Benchmarking Suite for Multi-Rotors*；Hang Yu、Guido C. H. E. de Croon、Christophe De Wagter；2023 | https://doi.org/10.1109/ICRA48891.2023.10161097；arXiv:2301.07430 | 已有本地来源说明；本期补 DOI metadata | 采纳：环境可通行性与性能指标分层、仿真/实机边界。 |
| C3 | *MAVRL: Learn to Fly in Cluttered Environments With Varying Speed*；Hang Yu、Christophe De Wagter、Guido C. H. E. de Croon；2025 | https://doi.org/10.1109/LRA.2024.3522778；官方代码 https://github.com/tudelft/mavrl | 未下载 PDF；本期 metadata | 有限采纳：cluttered 场景须同时报告安全与目标推进；不迁移其模型。 |
| C4 | *D²PPO: Diffusion Policy Policy Optimization with Dispersive Loss*；Guowei Zou 等；2025 | https://arxiv.org/abs/2508.02644；arXiv:2508.02644 | 未下载、未归档 | 未采纳：新增 InfoNCE/表征损失且来自 manipulation；当前没有点云表征坍塌的可复现证据。 |
| C5 | *Flow Policy Gradients for Robot Control*；Brent Yi 等；2026 | https://arxiv.org/abs/2602.02481；arXiv:2602.02481 | 未下载、未归档 | 未采纳：FM-RL 候选，不解决当前 DDPM/DPPO 的配对退化归因。 |
| C6 | *AEOS: Active Environment-aware Optimal Scanning Control for UAV LiDAR-Inertial Odometry in Complex Scenes*；Jianping Li 等；2025 | https://arxiv.org/abs/2509.09141；arXiv:2509.09141 | 未下载、未归档 | 未采纳：MPC+主动扫描服务于里程计，不是端到端避障轨迹策略。 |

## 4. 被采纳资料与核心贡献

### C1：DPPO 只维持当前方法身份，不替代能力裁决

[FACT] DPPO 将扩散去噪过程和环境过程构造成可由 policy gradient 优化的两层 MDP，并在连续控制与机器人微调任务报告结构化、on-manifold 探索和稳定性收益（arXiv:2409.00588）。

[JUDGMENT] 它支持当前仍以 DDPM/DPPO 作为 Route A 的方法身份；但机器人基准和零样本机械臂部署不能证明本项目 R1 优于 BC。对本项目，任何 DPPO 结论仍必须以同 task/reset/观测条件的 safe-arrival、collision、timeout 和原始轨迹为准。

### C2：用几何可通行性分层，不能用场景名称代替难度

[FACT] AvoidBench 将飞行表现与环境复杂度指标结合，在仿真中比较多类避障方法，并以实机实验检查趋势；其公开材料将 success、path/energy optimality、goal velocity、progress 与计算时间并列，而非只报告单一成功率（arXiv:2301.07430；DOI:10.1109/ICRA48891.2023.10161097）。

[JUDGMENT] 对提前避障，记录首次横移/偏航 onset、最小净空与首次安全到达的联合结果；对 full-space，按起终点 x/y/z 包络、目标方位和直连受阻与否分层；对 dense ceiling，按实际几何可通行性、窄净空和任务×seed 的完整分母分层。项目不采用 AvoidBench 的视觉、Flightmare 或 Unity 栈，也不以其指标替换当前首个安全入 0.5m 三维目标球的主终点。

### C3：cluttered 场景中的安全与推进必须同报，但其机制不可直接迁移

[FACT] MAVRL 官方代码说明其采用 depth 序列的 VAE/LSTM、PPO 和随环境复杂度变化的速度策略，并报告在 AvoidBench 与真实无人机上的实验；论文书目为 IEEE RA-L 2025，DOI:10.1109/LRA.2024.3522778。

[JUDGMENT] 它仅支持一条评价纪律：密集障碍中“更少碰撞”不自动等于有用能力，必须与安全到达、目标推进、超时和计算/执行条件并报。VAE/LSTM、变速控制、depth 输入、外部 controller 及其训练流程会改变当前 3D point-cloud、11d chunk、H4 和策略归因，故不迁移。

## 5. 未采纳资料与原因

- [JUDGMENT] C4 的 dispersive loss 会修改 BC 预训练目标，且其表征坍塌命题目前未由项目的相同观测—不同动作、特征统计或可复现实验支持。直接加入会把点云观测质量、reward/credit、训练时程与新的 InfoNCE 项混为一因；因此不下载、不实现。
- [JUDGMENT] C5 是有价值的 FM-RL 后续候选，但当前 R1 是 DDPM/DPPO 的组合变化，且已获得同任务终点证据。此时切换 FM 训练目标、likelihood 语义和优化器，会破坏可归因性；仅在当前身份与分层诊断完成、且 DDPM/DPPO 的固定预算证据仍显示不可恢复缺口时重新审查。
- [JUDGMENT] C6 的主动传感和 MPC 是里程计/扫描控制系统，会在策略外改变感知与轨迹决策链，不能作为 iDP3-UAV 的策略能力来源。
- [JUDGMENT] 外部 shield、轨迹投影、后处理平滑、EGO/A*/RRT 绕行、PID 追踪补偿、人工 avoidance-state、二级目标、动态奖励切换继续排除；它们会削弱 MC-1/MC-3/MC-5 的可归因性。

## 6. 对 iDP3-UAV 的可迁移建议

| Phase β 目标 | 应保持的能力证据 | 本期文献带来的限制 |
|---|---|---|
| 提前避障 | 固定 paired task 中的 onset、最小净空、首次安全到达、collision/timeout；救回与破坏同时计数 | [JUDGMENT] C1/C3 不允许只凭训练稳定、低碰撞或进度改善宣布提前避障。 |
| full-space support expansion | 起点/目标 x/y/z、目标方位、距离、点云有效性、直连受阻分层的 safe-arrival/collision/timeout | [JUDGMENT] C2 支持以环境几何影响解释表现；不能只以高度或“3D/dense”标签代理全空间覆盖。 |
| dense-obstacle capability ceiling | 实际几何/窄净空分层，任务×seed 完整分母、rescue/break、净空和轨迹 | [JUDGMENT] C2/C3 支持安全与推进并报；R1 seed203 的局部净增不足以成为稳定 dense 脱困结论。 |

[JUDGMENT] 近期最小工作是使用现有统一评价入口补齐 R1 u32 同任务原始轨迹，并对已有 u32/u256 结果做“训练进展中的同任务”诊断；不可事后挑选最佳 update 替代终点，也不可为不同 seed 或阶段增加专用评价程序。

## 7. MC 合规检查

| 约束 | 本期检查 |
|---|---|
| MC-1 策略输出 = 执行轨迹 | [JUDGMENT] 未建议投影、外部 planner、shield 或后处理轨迹改写。 |
| MC-2 Diffusion policy 是核心 | [JUDGMENT] 维持 DDPM/DPPO 为现有对象；未将 MAVRL/C6 的独立感知—控制链拼接进来。 |
| MC-3 学习阶段处理约束 | [JUDGMENT] 安全结论只来自策略内学习输出的实际执行轨迹；不采纳外部控制或滤波收益。 |
| MC-4 EGO 数据 frozen | [FACT] 本期未重采集数据；w4/w8/w11/w12/w18 仍仅可作 eval-only 回归/参考世界。 |
| MC-5 归因可分离 | [JUDGMENT] 严格区分 lightweight/kinematic、Gazebo/PX4 和实飞；外部系统的收益不能归因于扩散策略。 |

[FACT] 已证伪方向未重新引入：`yaw_loss_boost > 1`、5d action、策略外障碍排斥/GOAL-TRUNC/后平滑、DAC offline RL、TransDiffuser decorrelation loss、`torch.compile + CFG`。

## 8. 风险与不确定性

- [UNCERTAIN] C3 的完整论文实验未在本期下载；官方代码 README 与 DOI 书目只足以支持其系统构成和报告边界，不能用于定量比较。
- [UNCERTAIN] AvoidBench 是视觉输入和 Flightmare/Unity 环境，不能验证项目点云 observation、H4 或 PX4/Gazebo 部署质量。
- [JUDGMENT] 若忽略直连受阻、几何可通行性和固定分母，R1 seed203 的目标推进收益可能被错误包装为 dense 绕障能力；反过来，若仅看总体均值也会掩盖真实的局部救回与能力损失。
- [JUDGMENT] 以大 KL/clip、过强 penalty、提前停止、删除 dense 失败样本或策略外保护换取好看的曲线，将抹掉探索、成功条件梯度、提前避障和脱困信号，持续禁止。

## 9. 下一步建议

1. [FACT] 先按 `zhidao/2026-10-11_RouteA_统一权重评价与目录整理执行指导_v2_0.md` 执行并回传 R1 u32 同任务评价的原始轨迹、日志、退出码与清单；当前仅交付 Windows 侧程序，尚无 WSL 实测结果。
2. [JUDGMENT] 以同一冻结任务库，将 u32 与 u256 作为训练时程诊断点，固定报告救回/破坏、首次事件和几何分层；不得让中间检查点取代 256 update 终点结论。
3. [JUDGMENT] 只有出现可重复的多 seed safe-arrival 改善后，才设计未参与诊断的新任务与 PX4/Gazebo 闭环；它们应与 lightweight 结果分开报告。
4. [FACT] 本期仅创建研究报告与引用 metadata；未运行训练，未操作 WSL、ROS、Gazebo、PX4、checkpoint 或训练配置。
