# Phase β 联网资料研究（2026-10-19）

> 检索日期：2026-10-19（Asia/Shanghai）  
> 范围：Phase β / Route A 的 RL finetune、diffusion/flow policy、点云避障、密集障碍导航、safe RL 与 sim-to-real。  
> 结论状态：研究与证据筛选；**不构成训练参数、算法或实验矩阵批准**。

## 1. 本期项目上下文摘要

[FACT] 当前 Windows 源码已经交付 A1 共同协议下的 B1280/40 与 B2560/20 两臂：同 seed、256 轮、每轮 1024 transition、相同 51200 pair/轮；训练人工空间终止关闭，Cs=1 的 H4 渐进空间成本、真实 60 决策期限的 bootstrap 语义、六维 critic 任务上下文已接入。依据为 `jindu/2026-10-17_RouteA_共同协议A1实现交付与下一步_v1_0.md`。

[FACT] 截至本次检索，WSL 本轮训练尚未启动；因此 A1 的能力收益、密集绕障改善和 sim-to-real 效果均没有新实证。既有 420 开发评价使用训练的 21 几何，不能据此主张未见世界泛化。

[JUDGMENT] 当前最小可裁决工作仍是执行既定 A1 两臂并用冻结的配对评价/恢复诊断分析结果，而不是插入新的 RL 家族、flow-RL 或外部安全层。这样才能把共同协议的组合效应与后续算法变化分开。

三项 Phase β 目标的本轮对应关系如下：

| 目标 | 当前可验证证据 | 本轮资料的增量用途 |
|---|---|---|
| 提前避障 | 固定状态配对、起始受阻与近障轨迹的 onset/路径比较 | DPPO 的 chunk-policy RL 语义与 AvoidBench 的任务难度分层支持评价，不规定 reward 新项 |
| full-space support expansion | 人工空间终止已关闭；仍需 x/y/z、目标方位和路线可行性分层 | iDP3 与点云 RL 仅支持三维观测/策略内学习的研究动机，不能证明扩域成功 |
| dense-obstacle capability ceiling | 固定受阻任务、恢复周期、safe-arrival 与净收益须共同报告 | AvoidBench 的 traversability 思路支持难度标注；不以障碍数或标签替代可通行性 |

## 2. 检索范围与关键词

[FACT] 已读取或搜索：`AGENTS.md`、`sheji/`、`zhidao/`、最新 A1 进度交接、`论文/被参考/`、`论文/未被参考/`、`论文/开题报告参考文献/`；`program/jindu/jindu.txt` 不存在。还复用了上次自动化记忆，以避免重复泛扫 DPPO、AvoidBench、MAVRL 与 ReinFlow。

[FACT] 本轮检索使用 arXiv 官方页面为主，关键词包括：`diffusion policy reinforcement learning safety obstacle avoidance point cloud`、`UAV obstacle avoidance reinforcement learning safety`、`safe reinforcement learning diffusion policy`、`flow matching policy reinforcement learning robot control`。

[ASSUMPTION] arXiv 预印本的实验结论尚未经同行评审；除非另有官方发表页，本报告不把其作为可部署安全保证。

## 3. 候选资料总表

| 候选资料 | 年份/标识 | 来源 | 是否下载 | 处理与理由 |
|---|---:|---|---|---|
| Diffusion Policy Policy Optimization（DPPO） | 2024, arXiv:2409.00588 | [arXiv](https://arxiv.org/abs/2409.00588) | 已有项目归档，未重复下载 | 采纳：当前 DDPM chunk-policy 的直接算法基线与日志解释边界 |
| Generalizable Humanoid Manipulation with 3D Diffusion Policies（iDP3） | 2024, arXiv:2410.10803 | [arXiv](https://arxiv.org/abs/2410.10803) | 已有项目归档，未重复下载 | 采纳：点云条件策略的表征背景，不外推为 UAV 成功证据 |
| Time Limits in Reinforcement Learning | 2018, arXiv:1712.00378 | [arXiv](https://arxiv.org/abs/1712.00378) | 已有项目归档，未重复下载 | 采纳：区分真终止和时间截断，支持本项目 bootstrap 审计 |
| AvoidBench: A High-Fidelity Vision-Based Obstacle Avoidance Benchmarking Suite for Multi-Rotors | 2023, arXiv:2301.07430 / DOI:10.1109/ICRA48891.2023.10161097 | [arXiv](https://arxiv.org/abs/2301.07430) | 已有项目归档，未重复下载 | 采纳：密集场景以可通行性/难度分层而非障碍数命名 |
| Flying on Point Clouds with Reinforcement Learning | 2025, arXiv:2503.00496 | [arXiv](https://arxiv.org/abs/2503.00496) | 已有项目归档，未重复下载 | 采纳：点云—飞行 RL 的相邻任务证据；仅支撑评估维度，不迁移其控制链 |
| Flow Policy Gradients for Robot Control（FPO++） | 2026, arXiv:2602.02481 | [arXiv](https://arxiv.org/abs/2602.02481) | 否 | 未采纳：有 flow-RL 启发，但会混淆当前 DDPM/DPPO A1 归因；后续必须独立设计/审查 |
| Reinforcement Learning for Flow-Matching Policies | 2025, arXiv:2507.15073 | [arXiv](https://arxiv.org/abs/2507.15073) | 否 | 未采纳：变量 horizon 与 GRPO/reward surrogate 改变当前合同，且实验为简化 unicycle |
| High-Speed Vision-Based Flight in Clutter with Safety-Shielded Reinforcement Learning | 2026, arXiv:2602.08653 | [arXiv](https://arxiv.org/abs/2602.08653) | 否 | 未采纳：部署期安全 filter 投影输出，违反 MC-1/MC-3 的策略内边界 |

## 4. 被采纳资料与核心贡献

### 4.1 DPPO：把优化正确性和能力证据分离

[FACT] DPPO 将 diffusion 的去噪过程组织为可用 PPO 优化的策略过程；它支持“正确实现/数值稳定”与“任务能力改善”是不同命题的判断框架。[DPPO](https://arxiv.org/abs/2409.00588)

[JUDGMENT] 对 A1 而言，它仅支持继续记录 action chunk、ratio/clip、value/advantage 与固定任务对齐，不支持在未取得 A1 能力结果前换成新的 flow-policy objective。

### 4.2 iDP3 与 Flying on Point Clouds：三维点云是策略条件，不是外部改轨器

[FACT] iDP3 报告了以 3D point cloud 作为 diffusion policy 条件的操控方法；Flying on Point Clouds with Reinforcement Learning 把点云用于飞行 RL。两者均是研究相邻性证据，而非当前 UAV 路线的可比结果。[iDP3](https://arxiv.org/abs/2410.10803) [Flying on Point Clouds](https://arxiv.org/abs/2503.00496)

[JUDGMENT] 本项目可以保留“点云观测质量、起始几何、路线可行性、x/y/z覆盖”作为 A1 的分层字段，但不能据此把点云编码器、动作链或策略外 planner 加入本轮。

### 4.3 Time Limits 与 AvoidBench：先保证终止语义与难度分母

[FACT] Time Limits 讨论时间限制下 bootstrap 与终止语义的区分；AvoidBench 给出多旋翼避障评价，并使用可通行性等场景属性来刻画难度。[Time Limits](https://arxiv.org/abs/1712.00378) [AvoidBench](https://arxiv.org/abs/2301.07430)

[JUDGMENT] 这支持既定 A1 的真 60 决策期限不 bootstrap，以及评价中把障碍数、是否直连受阻、可行路线/密集来源分开报告。它不证明当前 21 训练几何外的泛化，不能把 420 开发评价当作 test result。

## 5. 未采纳资料与原因

[FACT] FPO++ 的作者报告 flow matching policy gradient 在多个机器人任务中改进，但其 fine-tuning 以 flow 采样、chunk-level ratio 和不同目标实现为前提；不是对当前 DDPM/DPPO A1 的小补丁。[FPO++](https://arxiv.org/abs/2602.02481)

[FACT] Flow-Matching Policies 的 RL 工作引入 reward-weighted flow matching 和带 learned reward surrogate 的 GRPO，且实验主体是 simulated unicycle。[RL for Flow-Matching Policies](https://arxiv.org/abs/2507.15073)

[FACT] High-Speed Vision-Based Flight in Clutter 在部署时把动作投影到安全集；其报告本身明确该 filter 是部署机制的一部分。[Safety-Shielded RL](https://arxiv.org/abs/2602.08653)

[JUDGMENT] 前两篇可在 A1 有可解释终点结果后，作为单独 FM 分支候选；在此之前采用会把“共同协议/更新组织”与“policy family/objective”混在同一实验。第三篇的安全 filter 则直接越过 MC-1/MC-3，不能迁移。

## 6. 对 iDP3-UAV 的可迁移建议

1. [JUDGMENT] 按既定两臂完成后，优先输出固定分母的 safe-arrival、collision、净收益、早期 onset、真实受阻/密集来源和恢复周期指标；所有条目保留 BC 与旧 checkpoint 参照。不要把 reward、loss 或单个 value 指标当作三项能力的替代终点。
2. [JUDGMENT] 对 full-space，将 x/y/z、目标方位、近障起点与实际路径范围共同分层。单纯关闭人工空间终止只是去掉评价/训练伪失败，不是扩域能力证明。
3. [JUDGMENT] 若 A1 显示数值更新正常但能力仍低于 BC，先以冻结任务库审计 critic/advantage 对恢复或必要退让周期的条件化，而不是删掉困难样本、缩短期限或加策略外 shield。
4. [UNCERTAIN] 若 A1 给出稳定的多 seed safe-arrival 改善，FPO++/flow-RL 是否优于 DDPM/DPPO仍未知；需要独立同预算、同观测、同冻结任务库的设计，且必须单独审查，不可从本文直接实施。

## 7. MC 合规检查

| 约束 | 本轮结论 |
|---|---|
| MC-1（策略输出即执行轨迹） | [FACT] 未采纳部署期 filter、action projection、外部 planner 或轨迹修剪。 |
| MC-2（diffusion policy 是策略核心） | [FACT] 采纳资料仅用于策略内 diffusion/点云条件/RL 的研究边界；未增设策略外控制器。 |
| MC-3（约束在学习阶段处理） | [JUDGMENT] 继续使用 reward、训练协议和评价证据处理；shield 类方向明确拒绝。 |
| MC-4（EGO frozen） | [FACT] 本轮不要求重采集或改变 988 episode / 60151 frame 冻结集。 |
| MC-5（安全到达主终点） | [JUDGMENT] safe-arrival 与总体净收益仍优先于曲线平滑、单项损失或中间 checkpoint。 |

## 8. 风险与不确定性

- [FACT] A1 尚无 WSL/GPU/三帧真实 E5 运行证据；本地回归通过不能替代训练和能力结论。
- [UNCERTAIN] 上述近期预印本的可复现性、对 UAV 点云 action chunk 的外推和实机转移仍未经本项目验证。
- [JUDGMENT] 使用当前 21 几何的开发任务筛选模型会把训练覆盖与泛化混淆；val20/test12 和 eval-only 世界必须继续隔离。
- [JUDGMENT] 外部 shield 即使改善碰撞率，也会掩盖策略自身避障能力并破坏 MC 归因，不能作为本项目主结果。

## 9. 下一步建议

[JUDGMENT] 在 2026-10-31 节点前，先执行 A1 的两个既定共同协议臂，并用统一评价入口完成冻结配对、24 状态×50采样和恢复诊断。若其终点能力没有多 seed 改善，应按原始轨迹与条件分层决定后续的信用/更新组织诊断；不要以本文资料为由直接切换 FPO++、GRPO、ReinFlow 或安全投影。

[FACT] 本报告实际引用资料的可追溯 metadata 位于 [`C:\Users\cjj\Desktop\IDP3\论文\被参考\metadata\2026-10-19_PhaseBeta_联网资料研究_metadata.md`](../被参考/metadata/2026-10-19_PhaseBeta_联网资料研究_metadata.md)。未采纳候选未复制到 `论文/被参考/`。
