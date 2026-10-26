# 2026-07-06 PhaseBeta 联网资料研究

| 字段 | 内容 |
|------|------|
| 文档类型 | 联网资料研究报告 |
| 日期 | 2026-07-06 |
| 检索日期 | 2026-07-06 |
| 版本 | v1.0 |
| 状态 | 已归档 |
| 前置条件 | `AGENTS.md`; `jindu/2026-07-05-routeA-RL-stage-handoff-objective-summary.md`; `sheji/RouteA_RL_GlobalHealthReview_and_NextDecision_v1.md`; `sheji/RouteA_RL_TrainingSchedule_Amendment_v1.md`; `sheji/RouteA_RL_Environment_Design_v1.md`; `zhidao/` Route A RL 指导文件；`论文/` 既有归档 |

## 1. 本期项目上下文摘要

[FACT] 本期先读取了 `AGENTS.md`、`sheji/`、`zhidao/`、`jindu/` 和 `论文/` 目录。`program/jindu/jindu.txt` 不存在；当前进度以 `jindu/` 下 2026-07-03 至 2026-07-05 的 Route A RL 交接和闭环边界纠偏文件为准。

[FACT] Route A RL v1 已完成 worldgen / validation / calibration / training integration / A0-A2 smoke / checkpoint persist / 1080ep lightweight paired rollout scaffold；但正式 A2-newenv 10k capability short-train、A3 full training、正式 RL policy checkpoint 和 Gazebo/PX4 闭环验证均未完成。

[FACT] 当前主要阻塞不是环境链路，而是 formal trainer / online update schedule：continuous online rollout data injection + immediate critic/actor update 在 new env pool 上触发 critic twin divergence。`RouteA_RL_GlobalHealthReview_and_NextDecision_v1.md` 已裁决下一步应修 reward wiring 与 trainer schedule，并做 large fixed replay critic bootstrap + Q-scale audit + phased online。

[FACT] Phase β/RL 的真实目标仍是三类能力缺口：提前避障、full-space support expansion、dense-obstacle capability ceiling。任何训练稳定化都必须证明没有抹平有效学习信号。

[JUDGMENT] 因此本期联网研究不再重复“是否需要 RL”，也不把 1080ep lightweight rollout 作为能力 claim；重点检索能支撑 Route A v2 训练调度、flow/FM policy RL 更新、Q-scale/critic bootstrap、UAV obstacle-rich curriculum 和 sim-to-real 边界的资料。

## 2. 检索范围与关键词

[FACT] 检索来源优先：arXiv 官方页、项目主页、官方代码仓库、作者页和可追溯论文页。

[FACT] 关键词覆盖：

- `flow matching policy online reinforcement learning robotics 2026`
- `reverse flow matching online RL diffusion flow policies`
- `flow matching policy gradients`
- `offline-to-online reinforcement learning warmup recalibration critic`
- `policy-only online RL fine tuning behavior cloning`
- `quadrotor random obstacles curriculum reinforcement learning`
- `UAV obstacle avoidance sim-to-real measurement uncertainty`
- `ambient diffusion policy suboptimal data robotics`

## 3. 候选资料总表

| # | 标题 | 作者 / 年份 | 来源 URL | DOI / arXiv ID | 是否下载 / 归档 | 采纳结论 |
|---|---|---|---|---|---|---|
| 1 | Reverse Flow Matching: A Unified Framework for Online RL with Diffusion and Flow Policies | Li, Tang, Azizan / 2026 | https://arxiv.org/abs/2601.08136 | arXiv:2601.08136 | 保存元数据说明 | 采纳 |
| 2 | Reinforcement Learning for Flow-Matching Policies | Pfrommer, Huang, Sojoudi / 2025 | https://arxiv.org/abs/2507.15073 | arXiv:2507.15073 | 保存元数据说明 | 采纳 |
| 3 | Flow Matching Policy Gradients | McAllister et al. / 2025 | https://arxiv.org/abs/2507.21053 | arXiv:2507.21053 | 保存元数据说明 | 采纳 |
| 4 | Efficient Online RL Fine-Tuning Need Not Retain Offline Data | Zhou et al. / 2024 | https://arxiv.org/abs/2412.07762 | arXiv:2412.07762 | 保存元数据说明 | 采纳 |
| 5 | Online Pre-Training for Offline-to-Online RL | Shin et al. / 2025 | https://arxiv.org/abs/2507.08387 | arXiv:2507.08387 | 保存元数据说明 | 采纳 |
| 6 | Efficient Online RL Fine Tuning with Offline Pre-trained Policy Only | Xiao et al. / 2025 | https://arxiv.org/abs/2505.16856 | arXiv:2505.16856 | 保存元数据说明 | 采纳 |
| 7 | Curriculum RL for Quadrotor Racing with Random Obstacles | Sun et al. / 2026 | https://arxiv.org/abs/2602.24030 | arXiv:2602.24030 | 保存元数据说明 | 采纳 |
| 8 | Ambient Diffusion Policy | Wei et al. / 2026 | https://arxiv.org/abs/2606.12365 | arXiv:2606.12365 | 保存元数据说明 | 采纳 |
| 9 | Sim-to-Real DRL based Obstacle Avoidance for UAVs under Measurement Uncertainty | Joshi, Kapur, Kandath / 2023 | https://arxiv.org/abs/2303.07243 | arXiv:2303.07243 | 保存元数据说明 | 采纳 |
| 10 | Cal-QL | Nakamoto et al. / 2023 | https://arxiv.org/abs/2303.05479 | arXiv:2303.05479 | 既有归档；本轮复用 | 采纳 |
| 11 | ReinFlow | 作者见 arXiv / 2025 | https://arxiv.org/abs/2505.22094 | arXiv:2505.22094 | 既有归档；本轮复用 | 采纳 |
| 12 | DPPO | 作者见 arXiv / 2024 | https://arxiv.org/abs/2409.00588 | arXiv:2409.00588 | 既有归档；本轮复用 | 采纳 |
| 13 | Flow Matching for Offline RL with Discrete Actions | Khan et al. / 2026 | https://arxiv.org/abs/2602.06138 | arXiv:2602.06138 | 未下载 | 未采纳 |
| 14 | VFP: Variational Flow-Matching Policy | Zhai, Hao / 2025 | https://arxiv.org/abs/2508.01622 | arXiv:2508.01622 | 未下载 | 未采纳 |
| 15 | Extending GRPO to Continuous Control | Khanda et al. / 2025 | https://arxiv.org/abs/2507.19555 | arXiv:2507.19555 | 未下载 | 未采纳 |
| 16 | Sim-to-Real Transfer for Mobile Robots with RL | Salimpour et al. / 2025 | https://arxiv.org/abs/2501.02902 | arXiv:2501.02902 | 未下载 | 未采纳 |

## 4. 被采纳资料与核心贡献

### 4.1 Reverse Flow Matching, arXiv:2601.08136

[FACT] RFM 将 diffusion / flow policy 的 online RL 目标形式化为面向 Q-induced Boltzmann distribution 的 reverse inference 问题，并把 noise-expectation 与 gradient-expectation 统一到一个估计框架中。

[FACT] 该文显式指出 online RL 中没有可直接采样的目标 action distribution，目标分布通常由 $Q(s,a)$ 定义且未归一化；这正对应 iDP3-UAV 当前 Route A 中“critic 尚未健康时不能直接信任 Q 驱动 actor 更新”的问题。

[JUDGMENT] 对 iDP3-UAV 的迁移价值是 Route A v2 的算法备选：若 large fixed replay critic bootstrap 和 Q-scale audit 通过，可以研究 Q-value + Q-gradient 的 flow-policy update；若 Q-scale 未过关，RFM 类方法只会把不健康 critic 放大到 flow policy。

### 4.2 RL for Flow-Matching Policies, arXiv:2507.15073

[FACT] 该工作针对 action chunk 的 flow-matching policy，研究 Reward-Weighted Flow Matching 与 GRPO-style flow policy fine-tune，用于超过 suboptimal demonstrator。

[JUDGMENT] 它支持本项目 Route A 不必只限于 SAC-style DQPG；可以保留 reward-weighted FM / group-relative update 作为 ReinFlow 后的低耦合备选。

[RISK] 若直接使用 reward-weighted FM 而没有 paired episode、role-balanced return normalization 和 hard/frontier sample retention，容易退化为“只模仿当前高回报短样本”，无法证明提前避障和 dense recovery 是策略学到的能力。

### 4.3 Flow Matching Policy Gradients, arXiv:2507.21053

[FACT] FPO 将 flow matching 放入 PPO-clip 风格的 policy gradient 框架，避免精确 likelihood 计算，并保持对 diffusion / flow integration choice 的相对独立。

[JUDGMENT] 对本项目的价值是 DPPO 与 ReinFlow 之间的中间备选：当 direct Q-gradient through sampler 过不稳定、DPPO 又与 OT-CFM 4-step velocity parameterization 不完全贴合时，FPO-style clipped objective 可作为 Route A.1 候选。

[JUDGMENT] 当前不建议抢跑实现 FPO；它依赖 advantage / return 的可信估计，而本项目当前更基础的问题是 support reward wiring、critic bootstrap 和 phased online schedule。

### 4.4 WSRL / OPT / PORL / Cal-QL：offline-to-online 与 Q 校准

[FACT] WSRL 指出 offline-to-online fine-tuning 初期的 value function divergence 与 offline/online rollout distribution mismatch 相关，并提出 warmup rollouts 用于 recalibration。OPT 强调为 online fine-tuning 单独训练适配 online distribution 的 value function。PORL 讨论只有 offline pretrained policy、没有 pretrained Q-function 时的 online Q 初始化问题。Cal-QL 强调 Q-value calibration 是 offline-to-online 成功条件之一。

[JUDGMENT] 这些资料共同支撑 `RouteA_RL_GlobalHealthReview_and_NextDecision_v1.md` 的裁决：下一步不是继续 immediate online update，而是 collect-only warmup / large fixed replay critic bootstrap / Q-scale audit / phased online。

[JUDGMENT] 对 iDP3-UAV 的具体门禁应是：heldout fixed replay 上 `Spearman(mean_Q_episode, return_episode) > 0`，`td_target_p95 / max_abs_empirical_return <= 2`，`twin_gap p95 <= 0.35-0.40`，actor update 必须发生在 critic digest gate PASS 之后。

### 4.5 Curriculum RL for Quadrotor Racing with Random Obstacles, arXiv:2602.24030

[FACT] 该 2026 UAV 工作面向 obstacle-rich quadrotor racing，采用 multi-stage curriculum、domain randomization、multi-scene updating，并报告 HIL 与 real-world flight 验证。论文中 obstacle generator、随机初始状态、多场景更新和 reward 冲突处理，均直接关联 dense obstacle 与 sim-to-real 主题。

[JUDGMENT] 对 iDP3-UAV 的可迁移价值不是改成 racing controller，也不是改 Action 维度；而是支持 Route A v2 的训练调度：按 formal role 分阶段提升难度、每 phase 固定场景 slice 后 digest critic、多场景更新避免单 world 过拟合。

[JUDGMENT] 它也提醒 dense obstacle capability ceiling 不能只靠更高障碍密度；reward 必须平衡 progress 与 avoidance，避免 policy 学成绕远、停滞或 late avoidance。

### 4.6 Ambient Diffusion Policy, arXiv:2606.12365

[FACT] Ambient Diffusion Policy 通过 diffusion-time / noise-dependent data usage 从 suboptimal data 中提取有用部分，避免低质数据污染全部 denoising 时间。

[JUDGMENT] 由于 MC-4 要求 EGO 数据 frozen，本项目不应因该文建议重采或混入新 demonstration；可迁移的是诊断思想：在 FM/RL 更新中记录不同 FM time、不同 role、hard/frontier 样本对 gradient 的贡献，检查稳定性修正是否抹平提前避障和 dense recovery 信号。

### 4.7 Sim-to-Real DRL UAV Obstacle Avoidance, arXiv:2303.07243

[FACT] 该 UAV sim-to-real 资料研究测量不确定性对 DRL waypoint navigation / obstacle avoidance 的影响，并在真实 UAV 上验证仿真训练策略。

[JUDGMENT] 它支持本项目的闭环口径：lightweight / kinematic rollout 只能作为 scaffold，不能替代 Gazebo/PX4 + MAVROS + px4ctrl + ML Planner，更不能替代后续 real flight。正式 claim 需要重新回到 `ml_gazebo_fm_auto.sh` 等真实仿真闭环流程，并显式记录 sensing noise / pose drift / pointcloud sparsity。

## 5. 未采纳资料与原因

| 标题 | 未采纳原因 |
|------|------------|
| Flow Matching for Offline RL with Discrete Actions | [JUDGMENT] 主体是离散动作和 action quantization；本项目 Action 11d step-wise delta 不改维、不离散化，当前阶段不采纳。 |
| VFP: Variational Flow-Matching Policy | [JUDGMENT] 多模态操作任务背景强，可能支持后续 mode latent / Route A.5，但不支撑当前 P0 wiring 与 trainer schedule 修复。 |
| Extending GRPO to Continuous Control | [JUDGMENT] 主要是理论框架，缺少足够机器人实证；不作为当前 Route A 训练裁决依据。 |
| Sim-to-Real Transfer for Mobile Robots with RL | [JUDGMENT] ROS/Gazebo local navigation 有工程背景价值，但非 UAV/PX4、非 diffusion/FM policy，不放入本期结论。 |

## 6. 对 iDP3-UAV 的可迁移建议

### 6.1 Route A v2 应先修训练调度，不应先换算法名

[JUDGMENT] 新资料共同指向：当前 critic/twin divergence 更像 offline-to-online / policy-only fine-tune 初期的 distribution shift 与 Q-scale 问题，而不是 “Route A 算法整体失败”。因此下一步优先级应保持：

```text
P0 support reward wiring + trainer order
→ collect-only warmup
→ large fixed replay critic bootstrap
→ Q-scale audit
→ phased online
→ 再比较 ReinFlow / RFM / FPO / DPPO 分支
```

### 6.2 Flow/FM policy RL 候选排序

| 候选 | 当前定位 | 进入条件 |
|---|---|---|
| ReinFlow-style direct FM fine-tune | 默认主线 | P0 wiring 修复 + fixed replay critic gate PASS |
| RFM / Q-value + Q-gradient update | Route A v2 高阶候选 | Q-scale 健康且 Q-gradient 数值稳定 |
| FPO / PPO-clip flow gradient | DPPO 与 ReinFlow 中间备选 | on-policy / advantage 估计更可信时 |
| Reward-weighted FM / GRPO-style | 低耦合备选 | paired returns 稳定，且能保留 hard/frontier 样本梯度 |
| DPPO | 保守 fallback | FM-specific 接口风险过高时 |

[JUDGMENT] 不建议在 critic 未过关时引入 RFM/Q-gradient，因为它会把错误 Q 梯度直接注入 policy。也不建议用 DPPO 替代 reward/trainer wiring 修复。

### 6.3 三类 Phase β 目标的具体映射

| Phase β 目标 | 本期资料启发 | 建议门禁 |
|---|---|---|
| 提前避障 | UAV curriculum RL 强调 progress/avoidance reward 冲突；RFM/FPO 强调 advantage/Q 驱动 policy distribution | onset 提前量、future clearance、近障前 yaw/lateral action diversity 不能因稳定化下降 |
| full-space support expansion | offline-to-online 资料强调 online distribution calibration；Ambient DP 提醒不同数据质量/时段贡献不同 | offline density 接通；low-density cell coverage；support role 不退化；x/y/z 联合包络 SR |
| dense-obstacle capability ceiling | obstacle-rich quadrotor curriculum 支持多阶段难度和多场景更新 | dense recovery SR/CR、trap_recovery_rate、deadend_dwell_steps、side_flip_count、hard/frontier advantage |

### 6.4 Gazebo/PX4 与 lightweight 边界

[FACT] 当前 1080ep paired rollout 是 lightweight / kinematic surrogate evaluation，不是 Gazebo/PX4 闭环。

[JUDGMENT] 研究报告和论文叙事中应保留三层证据链：

```text
1. lightweight scaffold: 快速筛查 trainer/reward/metadata；
2. Gazebo/PX4 closed-loop: 论文仿真主证据；
3. real flight / HIL: sim-to-real 支撑证据。
```

## 7. MC 合规检查

| 约束 | 检查结论 | 说明 |
|------|----------|------|
| MC-1 策略输出 = 执行轨迹 | PASS | 本期建议均是训练调度、reward wiring、critic/bootstrap 或 policy 内更新；不建议后处理改轨迹。 |
| MC-2 Diffusion/FM policy 是策略核心 | PASS | ReinFlow/RFM/FPO/DPPO 均围绕 diffusion/FM policy；UAV curriculum 只迁移训练调度思想。 |
| MC-3 学习阶段处理约束 | PASS | 避障、support、dense recovery 通过 reward / RL update / diffusion-time 机制学习。 |
| MC-4 EGO 数据 frozen | PASS | Ambient DP 只迁移诊断，不建议重采或混入新 demonstration。 |
| MC-5 归因可分离 | CONDITIONAL PASS | 必须保留 run manifest、paired eval、role-wise ablation、claim_allowed=false 和 Gazebo/lightweight 边界。 |

[FACT] 本期未建议 yaw_loss_boost > 1、5d action 缩减、post-hoc smoothing、KD-Tree obstacle repulsion projection、GOAL-TRUNC、DAC offline RL、torch.compile + CFG。

[JUDGMENT] multi-stage curriculum 与 phased online 是训练调度，不是策略外轨迹修剪；合规前提是不能通过删除困难样本或降低 dense role 权重换取表面稳定。

## 8. 风险与不确定性

| 风险 / 不确定性 | 标注 | 影响 | 缓解 |
|---|---|---|---|
| RFM/FPO 等新方法多在 benchmark 上验证，未必直接适配 UAV point cloud chunk policy | [UNCERTAIN] | 直接实现可能增加变量，破坏 MC-5 | 先做 P0/P1 trainer 健康修复，再做 single-batch / fixed replay algorithm smoke |
| Reward-weighted FM 可能偏向高回报易样本 | [RISK] | dense/hard/frontier 样本梯度被抹平 | role-balanced return normalization；hard/frontier retention；success-conditioned advantage 检查 |
| UAV curriculum 文献使用 direct CTBR action，不同于本项目 11d trajectory action | [FACT] | 不能迁移 action/interface | 只迁移 curriculum、multi-scene、HIL/real validation 口径 |
| offline density 缺失会让 support expansion 学习信号不完整 | [FACT] | full-space support claim 不成立 | 先修 `offline_density.json` 和 support reward smoke |
| lightweight rollout 可能存在 artifact | [JUDGMENT] | 高估 RL_A2 smoke actor 能力 | 禁止 claim；用 Gazebo/PX4 closed-loop 复核 |

## 9. 下一步建议

1. [JUDGMENT] 产出 `RouteA_RL_TrainingSchedule_Amendment_v2.md`，吸收本期资料：warmup recalibration、large fixed replay critic bootstrap、Q-scale audit、phased online、claim boundary。
2. [JUDGMENT] 指导文件优先级应为：`P0_WiringHealthFix` → `B0B1_LargeReplay_CriticBootstrap` → `B2_QScale_Audit` → `P1_PhasedOnlinePilot`，不要先写 RFM/FPO 实现。
3. [JUDGMENT] 若 fixed replay critic gate 未过，暂停所有 actor 更新；先查 reward scale、TD target、done mask、target tau、gradient clip 和 action chunk critic 输入。
4. [JUDGMENT] 若 phased online 连续 3 phase 稳定但 `actor_delta≈0`、hard/frontier advantage≈0、三类 proxy 无改善，应标记 `[RISK] 学习信号被抹平` 并准备 Route switch，而不是继续调稳定参数。
5. [JUDGMENT] 论文资料层面，下一轮可专门补 `RFM/FPO/ReinFlow/DPPO` 的公式对照表，服务 Route A v2 算法分支设计。

## 附录 A. 本轮实际用于结论的资料

- Reverse Flow Matching: https://arxiv.org/abs/2601.08136
- Reinforcement Learning for Flow-Matching Policies: https://arxiv.org/abs/2507.15073
- Flow Matching Policy Gradients: https://arxiv.org/abs/2507.21053
- WSRL: https://arxiv.org/abs/2412.07762
- OPT: https://arxiv.org/abs/2507.08387
- PORL: https://arxiv.org/abs/2505.16856
- Curriculum RL for Quadrotor Racing with Random Obstacles: https://arxiv.org/abs/2602.24030
- Ambient Diffusion Policy: https://arxiv.org/abs/2606.12365
- Sim-to-Real DRL UAV Obstacle Avoidance: https://arxiv.org/abs/2303.07243
- Cal-QL: https://arxiv.org/abs/2303.05479
- ReinFlow: https://arxiv.org/abs/2505.22094
- DPPO: https://arxiv.org/abs/2409.00588

## 附录 B. 本轮自检

- [x] 已读取 / 搜索 `AGENTS.md`
- [x] 已读取 / 搜索 `sheji/`
- [x] 已读取 / 搜索 `zhidao/`
- [x] 已检查 `program/jindu/jindu.txt`，本地不存在
- [x] 已读取 / 搜索 `jindu/`
- [x] 已读取 / 搜索 `论文/`，包含 `被参考/`、`未被参考/`、`开题报告参考文献/`
- [x] 候选资料标注标题、年份、来源 URL、arXiv / DOI 状态、归档状态、采纳理由
- [x] 显式对照 Phase beta 三类目标
- [x] 显式检查 MC-1~MC-5 与策略内外边界
- [x] 未建议已证伪方向
- [x] 实际用于结论的资料已通过 `论文/被参考/2026-07-06_PhaseBeta_联网资料研究_sources.md` 与 `论文/被参考/metadata/2026-07-06_PhaseBeta_联网资料研究_metadata.md` 归档

