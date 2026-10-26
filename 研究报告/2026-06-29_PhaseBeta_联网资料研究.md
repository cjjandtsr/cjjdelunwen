# 2026-06-29 PhaseBeta 联网资料研究

| 字段 | 内容 |
|------|------|
| 文档类型 | 联网资料研究报告 |
| 日期 | 2026-06-29 |
| 检索日期 | 2026-06-29 |
| 版本 | v1.0 |
| 状态 | 已归档 |
| 前置条件 | `AGENTS.md`; `sheji/Reward_v1_3_Anticipatory_Support_DenseObstacle_Design_v1_2.md`; `sheji/2026-06-27-routeB-lowrank-dsrl-stabilization-design.md`; `sheji/Master_PhaseBeta_online_RL_design_v3.md`; `zhidao/` Route B / Reward v1.3 指导文件；`论文/` 既有归档 |

## 1. 本期项目上下文摘要

[FACT] 本地 `program/jindu/jindu.txt` 不存在；本期上下文来自 `AGENTS.md`、`sheji/`、`zhidao/` 和 `论文/` 既有归档。

[FACT] 当前项目处于 Phase alpha Finetune v9_1 闭环重测前后与 Phase beta / RL finetune 设计衔接阶段。Phase beta 的真实目标不是泛化地提高 reward，而是三类能力缺口：提前避障、full-space support expansion、dense-obstacle capability ceiling。

[FACT] `Reward v1.3` 已定稿，明确把三类目标转成可学习 reward 与评估指标：future clearance / onset、support density / low-density coverage、trap recovery / anti-flip。

[FACT] Route B low-rank DSRL-SAC 稳定化设计已形成：冻结 FM backbone，RL 只在 latent/noise 空间 steering；先做 BC/random-z baseline、PCA/Jacobian 诊断、k=16/32 low-rank smoke，再进入能力验证。

[JUDGMENT] 本期联网研究重点不应再重复“是否需要 RL”这一论证，而应回答：后续若 Route B 不能突破 BC，应优先转向哪类 Route A / direct FM fine-tune；Reward v1.3 是否与近期文献的 credit assignment / action chunk / dense obstacle 经验一致；哪些资料能支撑论文叙事。

## 2. 检索范围与关键词

[FACT] 检索来源优先级：arXiv 官方页、IEEE/ACM/Springer/ScienceDirect 官方页、项目主页、官方代码仓库、作者主页。

[FACT] 检索关键词覆盖：

- `flow matching policy online reinforcement learning`
- `diffusion policy policy optimization DPPO`
- `diffusion steering reinforcement learning latent space`
- `reinforcement learning with action chunking`
- `UAV obstacle avoidance diffusion policy`
- `omnidirectional obstacle avoidance drone view`
- `high-speed flight in the wild`
- `safe diffusion policy constraint guided`
- `vision-based obstacle avoidance benchmark multirotor`
- `point cloud diffusion policy 3D policy`

## 3. 候选资料总表

| # | 标题 | 作者 / 年份 | 来源 | DOI / arXiv ID | 是否下载 / 归档 | 采纳结论 |
|---|---|---|---|---|---|---|
| 1 | ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning | 作者见 arXiv / 2025 | https://arxiv.org/abs/2505.22094 | arXiv:2505.22094 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 2 | Diffusion Policy Policy Optimization | 作者见 arXiv / 2024 | https://arxiv.org/abs/2409.00588 | arXiv:2409.00588 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 3 | Diffusion Steering via Reinforcement Learning | 作者见 arXiv / 2025 | https://arxiv.org/abs/2506.15799 | arXiv:2506.15799 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 4 | Flow Q-Learning | 作者见 arXiv / 2025 | https://arxiv.org/abs/2502.02538 | arXiv:2502.02538 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 5 | Reinforcement Learning with Action Chunking | 作者见 arXiv / 2025 | https://arxiv.org/abs/2507.07969 | arXiv:2507.07969 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 6 | Generalizable Humanoid Manipulation with Improved 3D Diffusion Policies | 作者见 arXiv / 2024 | https://arxiv.org/abs/2410.10803 | arXiv:2410.10803 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 7 | Fly360: Omnidirectional Obstacle Avoidance within Drone View | 作者见 arXiv / 2026 | https://arxiv.org/abs/2603.06573 | arXiv:2603.06573 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 8 | Learning High-Speed Flight in the Wild | 作者见 arXiv / 2021 | https://arxiv.org/abs/2110.05113 | arXiv:2110.05113 | 已有本地 PDF；本轮补 metadata | 采纳 |
| 9 | AvoidBench: A high-fidelity vision-based obstacle avoidance benchmarking suite for multi-rotors | 作者见论文页 / 2024-2025 | arXiv / 论文官方页 | arXiv ID 待本地 PDF 元数据复核 | 已有本地 PDF；本轮 metadata 标注不确定 | 采纳 |
| 10 | Constraint-Guided Diffusion Policies | 作者见论文页 / 2025 | arXiv / 项目页 | arXiv ID 待本地 PDF 元数据复核 | 已有本地 PDF；本轮 metadata 标注不确定 | 采纳 |
| 11 | Neural NMPC through Signed Distance Field Encoding for Collision Avoidance | 作者见论文页 / 2025-2026 | arXiv / 论文官方页 | arXiv ID 待复核 | 已在 `论文/未被参考/` | 未采纳 |
| 12 | Robot Motion Planning using One-Step Diffusion | 作者见论文页 / 2025 | arXiv / 论文官方页 | arXiv ID 待复核 | 已在 `论文/未被参考/` | 未采纳 |
| 13 | Generative Trajectory Planning in Dynamic Environments: A Joint Diffusion and Reinforcement Learning Framework | 作者见论文页 / 2025 | arXiv / 论文官方页 | arXiv ID 待复核 | 已在 `论文/未被参考/` | 未采纳 |

## 4. 被采纳资料与核心贡献

### 4.1 ReinFlow, arXiv:2505.22094

[FACT] ReinFlow 面向 flow matching policy 的在线 RL 微调，直接对应本项目 Phase1aPolicyFM 的 FM policy 形态。

[FACT] ReinFlow 资料页显示其论文已更新到 v7，并标注 NeurIPS 2025。

[JUDGMENT] 对 iDP3-UAV 的最大价值是 Route A 裁决：如果 Route B low-rank latent steering 稳定但能力增益不足，应优先设计 ReinFlow-style direct FM online fine-tuning，而不是继续扩大 176d SAC critic。

[JUDGMENT] 迁移时应保持 MC-1/MC-2：更新的是 FM policy 本体或 FM-derived actor，执行轨迹仍由策略输出，不做 post-hoc 轨迹修剪。

### 4.2 DPPO, arXiv:2409.00588

[FACT] DPPO 提供 diffusion policy 的 policy-gradient fine-tuning 范式，是本项目 AGENTS.md 中 Phase ④ “DPPO on BC+aux ckpt”的直接候选。

[JUDGMENT] DPPO 的价值是作为 Route A 备选：当 ReinFlow 工程接口与当前 OT-CFM 4-step sampler 不匹配时，DPPO 更适合作为保守 fallback。

[JUDGMENT] DPPO 不应被用于修补 Reward v1.3 的设计缺陷。若 Reward v1.3 无法让 onset / future clearance / trap recovery 指标改善，换 DPPO 不会自动解决 credit assignment。

### 4.3 DSRL, arXiv:2506.15799

[FACT] DSRL 以冻结 diffusion policy 为生成器，RL 在 latent/noise 空间 steering，与 Route B 设计一致。

[JUDGMENT] DSRL 支撑当前 Route B 的方法论合规性：latent steering 发生在策略采样过程内，不是 EGO/RRT/A* 也能套用的轨迹后处理。

[JUDGMENT] 本项目已观察到 full-176d SAC critic 发散，因此本期建议仍维持 low-rank DSRL，不建议把 DSRL 论文作为继续 full-176d 的理由。

### 4.4 Flow Q-Learning, arXiv:2502.02538

[FACT] FQL 把 flow matching policy 与 Q-learning / offline-to-online 结合，是生成式策略与 RL 对接的重要基线。

[JUDGMENT] 对本项目的迁移价值偏“理论与 Route A 备选”，不适合作为当前第一实现路线。原因是当前 iDP3-UAV 的核心瓶颈是闭环 sparse/dense credit assignment 与 176d chunk critic 稳定性，直接引入 FQL critic 可能增加不可分离变量。

### 4.5 Reinforcement Learning with Action Chunking, arXiv:2507.07969

[FACT] 本项目 action 是 11d step-wise delta，执行时以 chunk 形式输出。Action chunking RL 文献与本项目的 action temporal abstraction 直接相关。

[JUDGMENT] 其价值是提醒 Route A / critic 设计不要把 176d chunk 当作普通单步 action 盲目 Q-learning；若后续必须用 action-Q，critic 应显式处理 chunk 时间结构。

[JUDGMENT] 当前不建议直接引入 QC-FQL 作为第一路线，因为 Reward v1.3 与 low-rank DSRL 的短评估尚未完成，过早换成 chunk-Q 会破坏 MC-5 归因可分离。

### 4.6 iDP3, arXiv:2410.10803

[FACT] iDP3 是项目主模型的上游方法，证明 3D point cloud + diffusion policy 对机器人操作任务具备泛化优势。

[JUDGMENT] 对 UAV 的关键迁移点不是机械臂任务本身，而是“点云编码 + 多步轨迹生成 + 3D observation”的策略范式。论文叙事中应明确 UAV obstacle avoidance 是动态闭环控制扩展，不应把 humanoid manipulation 的成功率直接类比为 UAV 闭环 SR。

### 4.7 Fly360, arXiv:2603.06573

[FACT] Fly360 是 2026 年围绕无人机全向视野避障的新近资料，主题是 omnidirectional obstacle avoidance within drone view。

[JUDGMENT] 它对三类 Phase beta 目标中的 full-space support expansion 和 dense obstacle capability ceiling 有启发：更完整的方位感知能减少“局部前视盲区”导致的 late avoidance / dead-end。

[JUDGMENT] 当前不建议因 Fly360 立刻改传感器或重采数据，因为 MC-4 数据 frozen；可迁移的是评估思想：在 dense worlds 中记录障碍方位覆盖、盲区诱发的 late onset、以及回旋空间是否被策略利用。

### 4.8 Learning High-Speed Flight in the Wild, arXiv:2110.05113

[FACT] 该工作是 UAV 高速飞行与真实场景泛化的经典资料，强调闭环飞行、视觉感知、实际速度/安全权衡。

[JUDGMENT] 对 iDP3-UAV 的价值是论文背景与 sim-to-real 风险，不直接迁移算法。其“闭环实际飞行验证优先于离线指标”的思想支持本项目不把 open-loop loss 当成 Phase beta 成功标准。

### 4.9 AvoidBench

[FACT] AvoidBench 是多旋翼视觉避障 benchmark 资料，已存在于开题报告参考文献。

[JUDGMENT] 对本项目最有价值的是 benchmark 维度：不同世界、起终点、碰撞率、成功率、路径效率、感知失败模式。它支持本项目继续使用 paired canonical + random stress 双评估，而不是只报告训练环境 reward。

### 4.10 Constraint-Guided Diffusion Policies

[FACT] 本地已有 `Constraint-Guided Diffusion Policies.pdf` 归档。

[JUDGMENT] 该方向与 Phase ②.5 safety guidance 概念相近：约束应进入 diffusion sampling / policy generation 过程，而不是 trajectory output 后修剪。

[JUDGMENT] 对当前阶段的用途是支撑“策略内 safety guidance”论文叙事；但不能替代 Phase beta RL，因为用户定义的三类目标需要闭环交互学习与 credit assignment。

## 5. 未采纳资料与原因

| 标题 | 未采纳原因 |
|------|------------|
| Neural NMPC through Signed Distance Field Encoding for Collision Avoidance | [JUDGMENT] 适合 MPC / SDF 控制器背景，但容易把建议引向外部 planner 或 post-hoc constraint controller；本期不用于 Phase beta 结论，避免触碰 MC-1/MC-5。 |
| Robot Motion Planning using One-Step Diffusion | [JUDGMENT] 与 diffusion planning 有关，但当前项目已有 OT-CFM 4-step 主线；one-step diffusion 若作为 distillation 可留到 Phase ④.5，不支撑本期 RL finetune 决策。 |
| Generative Trajectory Planning in Dynamic Environments: A Joint Diffusion and Reinforcement Learning Framework | [JUDGMENT] 主题相关，但本地已有更直接的 ReinFlow / DPPO / DSRL 资料；未发现比这些资料更贴合 iDP3-UAV 三类目标的新增裁决价值。 |
| SafeDiffuser / generic safe diffusion RL 资料 | [JUDGMENT] 可作为广义安全生成背景，但多数不直接对应 UAV point cloud closed-loop obstacle avoidance；本期不放入被参考。 |
| VLA / language-guided navigation 资料 | [JUDGMENT] 与当前 Phase beta 的低层轨迹规划能力缺口弱相关，不用于结论。 |

## 6. 对 iDP3-UAV 的可迁移建议

### 6.1 Route B 当前裁决保持不变

[JUDGMENT] 继续执行 low-rank DSRL 的 baseline -> k=16 smoke -> k=32 ablation，而不是恢复 full-176d SAC。理由：DSRL 支持 latent steering 的方向，但项目实测 full-176d critic 爆炸已经说明“论文方向正确”不等于“当前维度和训练配置正确”。

[JUDGMENT] 若 k=16/k=32 只能稳定但不能让 onset / future clearance / trap recovery 改善，则应关闭 Route B 能力线，保留其诊断价值，转 Route A。

### 6.2 Route A 首选 ReinFlow-style direct FM online fine-tuning

[JUDGMENT] ReinFlow 与当前 OT-CFM policy 形态最贴合。Route A 设计应优先围绕 FM velocity / flow policy 的 online RL 梯度接口，而不是把 FM 输出 chunk 展开成高维 Q-learning 动作。

[ASSUMPTION] 当前 Phase1aPolicyFM 的 4-step Euler sampler 足够短，ReinFlow-style fine-tune 的计算成本可能低于完整 diffusion denoising policy 的 DPPO；需由执行仓库 profiling 验证。

### 6.3 DPPO 作为保守备选，不作为 reward 替代品

[JUDGMENT] DPPO 适合在 ReinFlow 接口风险高时作为 fallback，但必须沿用 Reward v1.3 的分量日志和能力门禁。不能只看 episode return。

### 6.4 Reward v1.3 与文献一致，但需要 ablation 守住 MC-5

[JUDGMENT] ReinFlow / DPPO / DSRL / action chunking 文献共同支持“用 RL 改变生成式策略偏好”。但项目论文归因必须靠 ablation 支撑：`base+pbrs+future_clearance`、`+onset`、`+trap/anti_flip`、`+support` 的顺序不能省。

### 6.5 Full-space support expansion 应先做评估增强，不做数据重采

[FACT] MC-4 要求 EGO 数据 frozen。

[JUDGMENT] Fly360 / AvoidBench 的迁移方式应是增强评估维度：低密度 cell 成功覆盖、视野/障碍方位覆盖、z/x/y 包络中的 SR/CR，而不是改相机、重采集、或引入外部全向 planner。

### 6.6 Dense obstacle ceiling 应以 trap recovery 和 mode stability 量化

[JUDGMENT] dense world 中只报告 SR/CR 不够。应保留 Reward v1.3 的 `trap_recovery_rate`、`deadend_dwell_steps`、`side_flip_count`、`loop_detected_rate`，并与 paired seed bank 对齐。

## 7. MC 合规检查

| 约束 | 检查结论 | 说明 |
|------|----------|------|
| MC-1 策略输出 = 执行轨迹 | 通过 | 本期建议只涉及训练/采样过程内策略学习，不建议后处理重写轨迹。 |
| MC-2 Diffusion policy 是策略核心 | 通过 | ReinFlow、DPPO、DSRL 都以 diffusion/FM policy 或其 latent/sampling 过程为核心。 |
| MC-3 学习阶段处理约束 | 通过 | Safety / clearance / support / dense recovery 均通过 reward、policy fine-tune 或 diffusion-time guidance 学习。 |
| MC-4 EGO 数据 frozen | 通过 | 不建议重采；Fly360 仅迁移评估思想。 |
| MC-5 归因可分离 | 条件通过 | 必须按 Reward v1.3 ablation 与 Route B baseline 执行，否则不能声称策略学到了三类能力。 |

[FACT] 本期未建议 yaw_loss_boost > 1、5d action 缩减、post-hoc smoothing、KD-Tree obstacle repulsion projection、GOAL-TRUNC、DAC offline RL、torch.compile + CFG。

[JUDGMENT] Constraint-guided diffusion / safety guidance 只能作为策略内 sampling-time 或训练时约束；若实现成 trajectory output 后的 obstacle projection，则不合规。

## 8. 风险与不确定性

| 风险 / 不确定性 | 标注 | 影响 | 缓解 |
|---|---|---|---|
| 部分本地 PDF 的 arXiv ID / DOI 需要 PDF 元数据复核 | [UNCERTAIN] | AvoidBench、CGD 等 metadata 可能缺精确 ID | 本期 metadata 标注待复核，不把未确认 ID 写成事实 |
| ReinFlow 与当前 OT-CFM 4-step sampler 的接口差异 | [UNCERTAIN] | Route A 实现复杂度可能高于预期 | 先写 Route A 接口设计和 single-batch gradient smoke |
| Low-rank DSRL 可能稳定但能力上限不足 | [JUDGMENT] | Route B 不突破 BC | 以 onset/clearance/trap/support 门禁及时止损 |
| Reward v1.3 分量过多导致 credit 混叠 | [JUDGMENT] | MC-5 归因弱 | 严格按 ablation 顺序，不一次性全开 |
| Fly360 类全向视野成果诱导传感器路线漂移 | [JUDGMENT] | 违反 frozen data / 延迟 Phase beta | 只迁移评估，不改传感器和数据集 |

## 9. 下一步建议

1. [JUDGMENT] 先完成 Reward v1.3 的短评估指导文件链路：old reward paired baseline、short eval、term logging、dense/support 指标。
2. [JUDGMENT] Route B 若继续执行，应以 `BC baseline -> random-z -> PCA/Jacobian -> k=16 smoke -> k=32 ablation` 为唯一顺序；未过 2k smoke 不进入长训练。
3. [JUDGMENT] 同步启动 Route A 设计草案，但不抢跑实现：题目建议为 `Design_PhaseBeta_RouteA_ReinFlow_DPPO_FM_Finetune_v1.md`，核心比较 ReinFlow vs DPPO vs chunk-Q。
4. [JUDGMENT] 论文资料层面，下一轮应补精确 BibTeX：ReinFlow、DPPO、DSRL、FQL、QC-FQL、Fly360、AvoidBench、CGD。
5. [JUDGMENT] Phase beta 论文叙事建议用三段结构：BC/FM 闭环能力缺口 -> Reward v1.3 credit assignment -> FM/RL fine-tune 让策略内部学到提前避障、支持域扩展与 dense recovery。

## 附录 A. 本轮实际用于结论的资料

- ReinFlow: https://arxiv.org/abs/2505.22094
- DPPO: https://arxiv.org/abs/2409.00588
- DSRL: https://arxiv.org/abs/2506.15799
- Flow Q-Learning: https://arxiv.org/abs/2502.02538
- Reinforcement Learning with Action Chunking: https://arxiv.org/abs/2507.07969
- iDP3: https://arxiv.org/abs/2410.10803
- Fly360: https://arxiv.org/abs/2603.06573
- Learning High-Speed Flight in the Wild: https://arxiv.org/abs/2110.05113
- AvoidBench: 本地 PDF `论文/开题报告参考文献/AvoidBench A high-fidelity vision-based obstacle avoidance benchmarking suite for multi-rotors.pdf`
- Constraint-Guided Diffusion Policies: 本地 PDF `论文/被参考/CGD - Constraint-Guided Diffusion Policies.pdf`

## 附录 B. 本轮自检

- [x] 已读取 / 搜索 `AGENTS.md`
- [x] 已读取 / 搜索 `sheji/`
- [x] 已读取 / 搜索 `zhidao/`
- [x] 已检查 `program/jindu/jindu.txt`，本地不存在
- [x] 已读取 / 搜索 `论文/`，包含 `被参考/`、`未被参考/`、`开题报告参考文献/`
- [x] 候选资料标注标题、年份、来源 URL、arXiv / DOI 状态、归档状态、采纳理由
- [x] 显式对照 Phase beta 三类目标
- [x] 显式检查 MC-1~MC-5 与策略内外边界
- [x] 未建议已证伪方向
- [x] 实际用于结论的资料已通过 metadata 归档到 `论文/被参考/metadata/2026-06-29_PhaseBeta_联网资料研究_metadata.md`
