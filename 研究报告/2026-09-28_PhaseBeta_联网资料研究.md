# 2026-09-28 Phase Beta 联网资料研究

| 字段 | 内容 |
|---|---|
| 文档类型 | 定期联网资料研究报告 |
| 检索日期 | 2026-09-28（Asia/Shanghai） |
| 状态 | 本期结论已归档；不构成训练或算法变更授权 |
| 资料元数据 | `论文/被参考/metadata/2026-09-28_PhaseBeta_联网资料研究_metadata.md` |
| 方法边界 | 保持 DDPM/DPPO、Reward v1.7、H4、11d action、冻结 EGO 数据与 eval-only 世界隔离 |

## 1. 本期项目上下文摘要

[FACT] `AGENTS.md` 要求将 RL lightweight/kinematic 结果与 Gazebo/PX4 闭环分开，并以 safe-arrival 为主终点；w4/w8/w11/w12/w18 仅可作评估/回归世界，不能重用于训练或 replay。

[FACT] 截至本期，最新本地设计是 2026-09-23 的 D1-F failure-state 只读诊断冻结补充：主阶段演化检验固定为 `preterminal`，禁止从 `divergence`、后续阶段或 `closest_goal` 中事后挑选最显著的 late stage。9 月 27 日的指导仍在定位同一原始 `SynthPointCloud.generate_with_metadata` 两次调用首次产生差异的计算边界；尚未确定具体 CUDA 算子或 RL 退化根因。

[JUDGMENT] 因而本周正确的问题不是“再选一个更强 RL 算法”，而是：在 input/replay/阶段身份仍待审计时，如何保持对三项最终能力目标、信用机制和统计分母的可解释性。任何切换 DDPM→FM、DPPO→其他 DPRL、或 H4→其他 horizon 都会新增不可分离变量，当前不应启动。

## 2. 检索范围与关键词

[FACT] 检索在 2026-09-28 进行，优先使用 arXiv 原始页面；搜索结果聚合页只用于发现，不作为结论来源。

- 近期组合：`online diffusion policy RL robot control 2026`、`safe reinforcement learning credit assignment 2026`、`UAV obstacle avoidance reinforcement learning arbitrary 3D`、`point cloud UAV navigation`、`flow matching policy reinforcement learning`。
- 经典/主线复核：`Diffusion Policy Policy Optimization`、有限期限 RL、目标条件信用、安全评估分布报告。
- 排除标准：[JUDGMENT] 仅将能够改变当前诊断解释、评估纪律或后续设计门槛的资料列为正式候选；不把搜索结果冒充系统综述，不因标题包含“safe”“UAV”或“diffusion”而采纳。

## 3. 候选资料总表

| ID | 标题；作者；年份 | 原始来源 / 标识 | 本期下载/归档 | [JUDGMENT] 采纳决定 |
|---|---|---|---|---|
| R1 | *A Review of Online Diffusion Policy RL Algorithms for Scalable Robotic Control*；Wonhyeok Choi 等；2026 | https://arxiv.org/abs/2601.06133；arXiv:2601.06133 | 未下载 PDF；本期 metadata | 采纳：作为 DPRL 家族与可扩展性风险的二级方法综述；不据此改算法。 |
| R2 | *UAV Obstacle Avoidance by Human-in-the-Loop Reinforcement in Arbitrary 3D Environment*；Xuyang Li 等；2023 | https://arxiv.org/abs/2304.05959；arXiv:2304.05959 | 未下载 PDF；本期 metadata | 有限采纳：作为“可变高度不等于完整三维泛化”的问题边界反例；不采纳其人类标签、二级目标与切换奖励。 |
| R3 | *Evaluation Metrics for Safe Reinforcement Learning*；Lindsay Spoor 等；2026 | https://arxiv.org/abs/2609.15315；arXiv:2609.15315 | 不重复下载；复核既有 metadata | 采纳：用于安全/终点/任务层分布报告纪律。 |
| R4 | *Improving Offline Goal-Conditioned Reinforcement Learning via Selective Reward Stimulation*；Jing Zhang；2026 | https://arxiv.org/abs/2609.19414；arXiv:2609.19414 | 不重复下载；复核既有 metadata | 有限采纳：仅作远端目标信用可测性的理论动机；不引入 RSIQL/IQL/额外奖励。 |
| R5 | *Diffusion Policy Policy Optimization*；Allen Z. Ren 等；2024 | https://arxiv.org/abs/2409.00588；arXiv:2409.00588 | 已有 PDF 与官方代码 metadata | 采纳：维持 DPPO 作为方法来源与实现核验对象；不外推其机器人实验为 UAV 结论。 |
| R6 | *Safe Multi-Agent Navigation guided by Goal-Conditioned Safe Reinforcement Learning*；Meng Feng 等；2025 | https://arxiv.org/abs/2502.17813；arXiv:2502.17813 | 未下载、未归档 | 未采纳：replay-state graph、边剪枝与 waypoint plan 是策略外规划。 |
| R7 | *Reinforcement Learning for Flow-Matching Policies*；Samuel Pfrommer 等；2025 | https://arxiv.org/abs/2507.15073；arXiv:2507.15073 | 未下载、未归档 | 未采纳：FM 切换不能解决当前输入/信用/阶段身份诊断，且违反单变量原则。 |

[FACT] R1–R5 的完整身份、使用目的和已存在副本路径列在本期 [metadata](../被参考/metadata/2026-09-28_PhaseBeta_联网资料研究_metadata.md)。R6/R7 未用于结论，故不进入 `论文/被参考/`。

## 4. 被采纳资料与核心贡献

### R1：算法分类是路线审计工具，不是换算法触发器

[FACT] R1 将在线 diffusion-policy RL 归为 action-gradient、Q-weighting、proximity-based 与 BPTT-based 四类，并报告不同类在计算、并行、扩散步数与鲁棒性方面存在取舍。其实验是统一 Isaac Lab 机器人基准，非 UAV/PX4，也没有本项目点云、H4 或 11d action contract。

[JUDGMENT] 对当前项目，R1 的有效贡献是审计顺序：先关闭 `raw_frame`/replay/transition/阶段定义的身份问题，再讨论 DPPO 近端目标是否应替换为别类方法。此结论与当前 D1-F 只读冻结一致；不支持现在切到 DIPO、Q-weighted DPRL、BPTT 或 FM。

### R2：三维问题需要三维终点分层，不能用“可变高度”代替

[FACT] R2 的问题设定允许高度和速度变化，但方法使用人工识别 avoidance state、二级目标点和对应奖励重组；其动力学还忽略飞行惯性。故其报告的 SR 不能证明端到端点云扩散策略在完整三维空间的能力。

[JUDGMENT] 可迁移的是评估问题：full-space support expansion 必须按起点/目标的 x、y、z 包络及目标方位分层报告 safe-arrival，而不是只报告 z 或平均 SR。人类标签、二级目标和切换奖励会改变原始任务信用，当前明确不采纳。

### R3–R5：保留“诊断优先、分布报告、DPPO 作为方法来源”

[FACT] R3 指出单个平均安全量不能描述违反频率、严重程度、任务差异或训练/最终策略差异；R4 指出稀疏远端目标下价值差可被局部估计误差淹没；R5 给出 diffusion policy 的 policy-gradient fine-tuning 框架。

[JUDGMENT] 三者合起来只支持以下受控原则：保持 current DDPM/DPPO/H4 作为诊断对象；将 goal-condition、role、阶段、collision/timeout 与 safe-arrival 分开报告；以同输入、同 transition、同生产 schedule 的只读反事实判断信用，而不是据 advantage 符号、reward 曲线或个别 seed 直接改 reward/算法。

## 5. 未采纳资料与原因

- [JUDGMENT] R6 将安全状态图与 waypoint 规划套在低层 safe-RL policy 外：虽然适合其长程多智能体任务，但改变了执行轨迹的生成归因。它不能进入本项目策略核心，也不能用作论文主结果的补救器。
- [JUDGMENT] R7 讨论 flow-matching policy 的 RL 更新，和项目 FM 长线有关；但目前 Route A 当前对象是 DDPM/DPPO 的 H4 failure-state。现在转 FM 会把“观测是否一致、动作/transition 是否同一、信用是否可解释”与“policy parameterization 差异”混在一起。
- [JUDGMENT] 既有包含 replay graph、unsafe-edge pruning、外部 shield、轨迹 projection、后处理平滑或自动二级目标的方法，均因可能重写路径或掩盖探索/成功梯度而维持未采纳；本期没有以它们支撑任何建议。

## 6. 对 iDP3-UAV 的可迁移建议

| Phase β 最终目标 | 当前应保留/新增的只读证据 | 本期文献带来的边界 |
|---|---|---|
| 提前避障 | 固定任务的 onset 提前量、到障时间/净空、绕障后恢复和最终 safe-arrival；同输入差异要先定位至原始 frame 阶段 | [JUDGMENT] R4 支持检查远端成功是否正确传播，但不授权把“远离目标”直接负奖或奖励塑形。 |
| full-space support expansion | x/y/z 起点与目标包络、目标方位分层的 safe-arrival、collision、timeout；不同高度不可代替全空间覆盖 | [JUDGMENT] R2 说明“可变高度”是较窄的问题设定；本项目须证明三维而非仅高度变化。 |
| dense-obstacle capability ceiling | dense role 的 rescue/break、collision/timeout、路径净空和安全到达；分母按任务/seed，不把重复噪声当新任务 | [JUDGMENT] R3 支持联合汇报分布与任务层结果；净空改善但困住/超时不能称能力突破。 |

[JUDGMENT] D1-F 运行若证实输入层不一致，应先把它作为观测质量/配对有效性故障处理，而不是解读 RL 能力、改变 reward 或加大 clip/KL/平滑。若 D1-F 未发现身份故障，才由既有设计流程决定下一条受控因果检验；研究报告不越过 Zread 或执行冻结。

## 7. MC 合规检查

| 约束 | [JUDGMENT] 本期结论 |
|---|---|
| MC-1 策略输出 = 执行轨迹 | 无 projection、replanning、waypoint 追踪、平滑或轨迹重写。R6 正因违反此边界被排除。 |
| MC-2 Diffusion policy 为核心 | 保持 DDPM/DPPO 诊断对象；R1/R7 只用于方法边界，不切换到 FM 或外部 planner。 |
| MC-3 约束在学习阶段处理 | 不加入部署 shield、人工 avoidance state 或二级目标；R2 的奖励切换不迁移。 |
| MC-4 EGO 数据 frozen | 不重采数据；eval-only w4/w8/w11/w12/w18 不作训练/replay。 |
| MC-5 归因可分离 | 诊断、lightweight capability、Gazebo/PX4 与实物证据分开；不让外部模块“救场”。 |

[JUDGMENT] 本期建议均为只读诊断和评价纪律，属于策略之外的证据采集，不改变推理时动作轨迹。禁止项持续有效：`yaw_loss_boost > 1`、5d action、策略外障碍排斥/GOAL-TRUNC/后平滑、DAC offline RL、decorrelation loss、`torch.compile + CFG`。任何数值稳定化仍须同时证明未抹除 update norm、动作多样性、成功条件 advantage、onset 提前量与 dense rescue 信号。

## 8. 风险与不确定性

- [UNCERTAIN] R1 是综述及 Isaac Lab 机器人实验；其分类不能证明任一类在 UAV 点云/11d H4 条件下更优。进入算法设计前需全文与官方代码/接口对照。
- [UNCERTAIN] R2 的 3D/AirSim 成功不等于点云 body-frame、PX4/Gazebo 或真实飞行可迁移；并且其人类介入和简化动力学限制了可比性。
- [JUDGMENT] 若原始帧首差异仍未定位，任何 paired endpoint、credit-gradient 或 role 分层都可能有配对混杂；不得用事后 seed/阶段筛选补救。
- [JUDGMENT] 强行提高 timeout/collision 惩罚、增加 clip/KL 或清除难样本，可能损害绕障探索与 dense rescue 的有效梯度；此类改动在当前阶段禁止以“曲线好看”为理由提出。

## 9. 下一步建议

1. [JUDGMENT] 优先完成 9 月 27 日 H4 原始帧阶段边界探针，并按 D1-F 的 `preterminal` 主检验和固定分母回传原始证据；在此之前继续 `BLOCK_FORMAL_256_AND_GAZEBO`。
2. [JUDGMENT] 若输入身份通过，下一项只读分析应并列表述 safe-arrival、collision、timeout、onset、x/y/z/目标方位分层与 dense rescue；禁止压缩为平均 reward 或净空单指标。
3. [JUDGMENT] 只有诊断合同关闭、生产路径有效且多 seed/固定 paired evaluation 可解释时，才由新的设计审查比较 DPPO 与其他 DPRL/FM 候选；届时 R1 才可作为方法分类参考。
4. [FACT] 本期只创建本报告及其 metadata，未改训练代码/配置，未运行训练，未操作 WSL、ROS、Gazebo、PX4 或 checkpoint。
