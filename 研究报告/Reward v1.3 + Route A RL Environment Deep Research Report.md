# Reward v1.3 + Route A RL Environment Deep Research Report

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-07-03 |
| 项目 | iDP3-UAV |
| 研究主题 | Phase β / Route A RL 环境设计 |
| 直接用途 | 为 `RouteA_RL_Environment_Design_v1.md` 提供可引用、可落地、可审查依据 |

## 执行摘要

- [JUDGMENT] **建议先完成 RL 环境重设计，再开始 Route A 全量训练。** 当前 Route B 的 seed bank 与训练脚本仍把 `support / course35 / default` 主要编码成 `z` 范围与 disturbance 开关，而不是能力语义；同时 `w4/w8/w11/w12/w18` 已被硬编码为 OOD/historical 评估世界。这种旧命名与旧 split 语义如果直接沿用到 Route A，会把“训练稳定”“环境难度变化”“历史 OOD 复用”混在一起，导致能力归因失真。fileciteturn0file0 fileciteturn0file1

- [FACT] **近年的 UAV benchmark 与 RL generalization benchmark 都支持“角色化环境 + 难度指标 + 重复试验”的设计，而不支持只按 obstacle count 或随机地图做 train/val/test。** FlightBench 明确把任务拆成 Forest / Maze / Multi-Waypoint 三类场景，并用 Traversability Obstruction、View Occlusion、Angle-over-Length 三类 difficulty metrics 组织八个测试；AvoidBench 也强调环境指标与性能指标要同时报告；Procgen 与 Avalon 则进一步说明，训练分布的多样性与“环境诱导技能”比单轴 easy-to-hard 更关键。citeturn7view0turn8view2turn10view7turn14view0

- [JUDGMENT] **Route A 的环境 role 应至少固定为四类：`anticipatory`、`dense_recovery`、`support_expansion`、`yaw_lateral_recovery`，并且 split 要按 role 与 generator family 双重隔离。** 这比继续使用 `canonical / support / default / dense / random_stress` 更符合论文证据链，也更符合你们对能力目标的定义。Avalon、MetaDrive 都说明：当 reward、obs、action 保持不变而环境生成器显式塑造所需技能时，更容易做能力归因与组合泛化分析。citeturn14view0turn16academia0turn7view0

- [JUDGMENT] **三层 validation 不是“额外保险”，而是 Route A 环境体系的主体。** Level 1 应确认几何合法与 start/goal surface clearance；Level 2 应做 inflated occupancy 上的 2D/3D reachability；Level 3 才是关键，即验证该世界是否真的触发 anticipatory onset、dense trap/recovery、support expansion 或 yaw recovery，而不是只“看起来像”困难。FlightBench 的 difficulty metrics、AvoidBench 的 environment metrics、RAPTOR 的 perception-aware risk formulation，都支持把“环境是否真的触发某种能力”写成数值检查。citeturn7view0turn8view0turn10view0turn10view1

- [FACT] **你们当前代码已经具备“做对这件事”的一半接口，但还缺环境语义层。** 现有运动学环境已经支持 `world_pool`、deterministic `episode_config`、扰动计划、`reward_v13`、`offline_density`；现有 Reward v1.3 也已经具备 future-clearance、risk-gate、trap、support 的接口与 history 状态。这意味着 Route A 环境重设计应以“补 split / role / validation / metadata / calibration”为主，而不是推翻现有 env API。fileciteturn0file4 fileciteturn0file14 fileciteturn0file15 fileciteturn0file16

- [JUDGMENT] **Baseline calibration 必须前置，而且要分三类：frozen BC/FM、EGO upper-bound、feasibility checker。** 如果新 world 在 inflated 3D occupancy 上都不可达，它不是“RL failed”；如果 BC/FM 与 EGO 都稳定失败，它应被标记为 `beyond_BC_EGO_boundary` 的 stress/failure-boundary，而不是直接进入 RL train pool。类似的“重复试验 + 不确定性报告”在 FLYINGTRUST 中已被当作标准 benchmark 协议；Offline-to-Online RL 文献也明确指出，在线微调最怕的是分布漂移造成 bootstrap error，因此 calibration 不能省。citeturn11academia0turn15view1

## 与 iDP3-UAV 目标对齐矩阵

| 最终论文目标 | Phase β / RL 能力目标 | 推荐环境 role | 推荐指标 | 可声明结论 | 不可声明边界 |
|------|------|------|------|------|------|
| 证明策略可**更早避障** | [FACT] 提前产生 lateral / yaw / path-shape onset | `anticipatory_train` / `anticipatory_eval` | onset distance、onset TTC、risk-window 内 `d_soft^H` 改善、碰撞率、path-stretch | [JUDGMENT] “在可测 risk window 中更早触发避障 onset，且不靠后处理。” | [JUDGMENT] 不能只因 yaw 更大、轨迹更弯就声称 anticipatory improvement。必须同时证明未来 clearance 改善且不只是绕远。 |
| 证明策略可**突破 dense clutter ceiling** | [FACT] 多障碍绕行、脱困、恢复、模式选择 | `dense_recovery_train` / `dense_recovery_eval` | SR、CR、trap entry rate、trap escape rate、time-to-escape、flip count、loop rate、min bottleneck clearance | [JUDGMENT] “在可达但困难的 dense/trap 世界中，恢复与脱困能力提升。” | [JUDGMENT] 不能把“不可能世界上的偶然通过”或 planner 不可达世界当作能力突破。 |
| 证明策略可**扩大 full-space support** | [FACT] 扩大 x/y/z 整体支持域，而非只飞高 | `support_expansion_train` / `support_expansion_eval` | low-density safe coverage、new-cell count、OOD cell success、altitude-normalized coverage、path-stretch | [JUDGMENT] “策略在低密度 support cell 中保持有效与安全。” | [JUDGMENT] 不能把单纯升高高度、无意义绕远、随机探索当作 support expansion。 |
| 证明策略可**学习闭环恢复** | [FACT] yaw drift、横向偏差、贴障后的 recovery | `yaw_lateral_recovery_train` / `yaw_lateral_recovery_eval` | recovery success、recovery time、cross-track integral、yaw error integral、post-disturb min clearance | [JUDGMENT] “策略从 BC 数据覆盖不足的偏差状态中学会恢复动作。” | [JUDGMENT] 不能把 simulator artifact、过弱扰动或重置偏置当作 recovery 能力。 |
| 证明提升来自**策略学到的新能力** | [FACT] MC-1~MC-5 要求归因可分离 | 所有 role + `historical_eval_only` | paired seeds、历史 eval consistency、Gazebo shadow eval、CI | [JUDGMENT] “能力提升来自 policy 学习，而不是 external shield / post-hoc rewrite。” | [FACT] 不能用后处理修轨、投影避障、外部 planner 接管来支撑主结果。 |

上述矩阵与当前项目现状是一致的：现有 seed bank 已把 canonical fixed-start-goal 与 deterministic disturb events 做成了可复现实验层，但 role 语义仍未显式化；训练脚本仍以 `support/course35/default` 控制 z-range 与扰动，而不是能力触发条件。fileciteturn0file0 fileciteturn0file1

## 文献与 benchmark 证据表

| 论文/系统名 | 年份 | URL / DOI / arXiv ID | 核心方法 | 可迁移到 iDP3-UAV 的部分 | 不适用或需警惕的部分 |
|------|------:|------|------|------|------|
| FlightBench | 2024 | arXiv:2406.05687 | 统一比较 learning-based 与 optimization-based quadrotor planners；提出 TO/VO/AOL 三类 difficulty metrics，并按多场景多难度组织 benchmark。citeturn7view0 | [FACT] 可直接迁移“先定义 difficulty metrics，再生成测试”的思路；尤其适合 anticipatory / dense role 的 Level-3 semantic check。 | [JUDGMENT] 它面向 ego-vision benchmark，不直接提供 RL train split 规则；需结合你们的 frozen dataset/MC 约束重写。 |
| AvoidBench | 2023 | arXiv:2301.07430 | 高保真 UAV avoidance benchmark；同时报告 performance metrics 与 environment metrics，并用真实飞行验证趋势。citeturn8view2turn8view0 | [FACT] 强烈支持 environment-semantic metrics 与 repeated evaluation；可借鉴 dense/complexity 报告格式。 | [JUDGMENT] 主要服务 benchmark，而不是 BC-to-RL fine-tune；不应把其 planner baseline 当作执行时接管器。 |
| RAPTOR | 2020 | arXiv:2007.03465 | perception-aware replanning、risk-aware refinement、yaw for active observation。citeturn10view0turn10view2 | [JUDGMENT] 特别适合启发 anticipatory role 的 risk window、unknown-risk look-ahead 与 yaw_trigger 指标。 | [FACT] 它是 planner，不可迁移为后端接管或 post-hoc rewrite。 |
| EGO-Planner | 2020 | arXiv:2008.08835 | ESDF-free gradient-based local planning，基于 guiding path 的 collision penalty。citeturn8view7 | [JUDGMENT] 适合作为 feasibility reference 与 upper-bound baseline；也适合启发 Level-2 可达性与 bottleneck 统计。 | [FACT] 不可接到策略输出后改轨；仅可用作校准与世界筛选。 |
| Learning High-Speed Flight in the Wild | 2021 | DOI: 10.1126/scirobotics.abg5810；arXiv:2110.05113 | 端到端 receding-horizon 轨迹预测；纯 simulation 训练，真实世界 zero-shot generalization。citeturn9view0 | [FACT] 强支持“复杂环境 + 感知噪声 + 多样测试环境”的 sim-to-real 逻辑；还支持以 Forest 类环境单独研究 anticipatory/high-speed。 | [JUDGMENT] 它依赖 privileged expert 生成训练数据；iDP3-UAV 不能重采 EGO 数据，因此只能借鉴测试逻辑与多模态路径观。 |
| Fly360 | 2026 | arXiv:2603.06573 | 全向感知下的 obstacle avoidance benchmark 与 fixed random-yaw training。citeturn2academia0 | [JUDGMENT] 对 yaw / heading 与运动方向不一致时的 recovery 设计很有启发。 | [UNCERTAIN] 发表较新，外部复现与基准稳定性仍有限；不宜作为主 benchmark 依据。 |
| Flightmare | 2020 | arXiv:2009.00563 | 高速 physics + decoupled rendering + RL API + point-cloud extraction。citeturn8view4turn8view5 | [FACT] 支持“快环境训练 + 慢环境 shadow validation”的双层环境架构；也支持点云接口与并行化。 | [JUDGMENT] 不是现成 split 方法学；更像工程底座。 |
| Air Learning | 2019 | arXiv:1906.00421 | UAV RL gym；domain randomization；硬件在环 latency distribution 注入。citeturn10view6turn10view5 | [FACT] 对 yaw_recovery / sim-to-real 很重要：扰动不应只来自几何，还应来自可重复延迟、执行偏差。 | [JUDGMENT] 其任务与平台较老，不能直接照搬难度设计。 |
| safe-control-gym | 2021 | arXiv:2109.06325 | Gym API + constraints + symbolic dynamics + repeatable disturbances。citeturn10view3turn10view4 | [FACT] 直接支持你们把 disturbance 做成 metadata、可复线 seed、可查询 constraint 的做法。 | [JUDGMENT] 它的 quadrotor任务偏控制层，不替代导航层语义设计。 |
| Procgen | 2019 | arXiv:1912.01588 | 程序生成 benchmark；证明多样训练分布对 generalization 至关重要。citeturn10view7 | [FACT] 用来支持“role-balanced procedural generation 优于固定小场景循环”。 | [JUDGMENT] 游戏环境与 UAV 几何不同，因此只迁移 split/generalization 原则。 |
| Avalon | 2022 | arXiv:2210.13417 | 保持 reward / dynamics / action 不变，只通过世界生成器塑造技能并研究泛化。citeturn14view0 | [JUDGMENT] 非常适合 iDP3-UAV：MC-1~MC-5 下，最应变化的是环境角色，而不是推翻 reward/action 语义。 | [JUDGMENT] Avalon 是大型 embodied benchmark；其开放世界规模远大于 UAV obstacle avoidance。 |
| MetaDrive | 2021 | arXiv:2109.12674 | 组合式场景生成，强调训练集多样性与泛化。citeturn16academia0 | [FACT] 支持 generator family + 参数组合化，而不是单一 world 池。 | [JUDGMENT] 驾驶场景有车道先验；UAV 需改写为 3D free-space 几何。 |
| DPPO | 2024 | arXiv:2409.00588 | diffusion policy 的 policy-gradient fine-tuning，强调 structured / on-manifold exploration 与稳定性。citeturn10view12turn10view13 | [JUDGMENT] 对 Route A 环境最重要的启发是：环境应提供足够 clean 的 on-manifold reward signal 与 repeated evaluation，不要把环境噪声和能力噪声混在一起。 | [UNCERTAIN] 论文重心在算法，不直接回答 UAV split 设计。 |
| ReinFlow | 2025 | arXiv:2505.22094 | flow policy 在线 RL fine-tuning；通过 learnable noise 将 deterministic flow 转成可算似然的 Markov process。citeturn10view8turn10view9 | [FACT] 对 iDP3-UAV 最直接：说明 Flow Matching policy 的在线 RL 是合理方向，因此环境应优先服务 flow actor，而不是为 chunk critic 过度定制。 | [UNCERTAIN] 目前主要在 locomotion/manipulation 上验证；UAV dense clutter 外推仍需谨慎。 |
| Flow Q-Learning | 2025 | arXiv:2502.02538 | one-step flow actor + Q-learning，避免 iterative backprop 不稳。citeturn10view10turn10view11 | [JUDGMENT] 环境接口应兼容 action-chunk value estimation，但不应把 world 设计绑死在 Q critic 需求上。 | [UNCERTAIN] iDP3-UAV 当前 11d chunk + 3D obstacle 几何是否适合直接 one-step 化，证据仍不足。 |
| Reinforcement Learning with Action Chunking | 2025 | arXiv:2507.07969 | chunk-space RL 与 unbiased n-step backups。citeturn3academia3 | [JUDGMENT] 可启发 environment logging：每个 step 应输出 chunk-level hazard/clearance metadata。 | [UNCERTAIN] 不应让环境设计过度迁就 176d critic；你们当前首要问题仍是 role semantics。 |
| Bootstrapping RL with Imitation for Vision-Based Agile Flight | 2024 | arXiv:2403.12203 | 先 RL teacher，再 IL student，再 adaptive RL fine-tune；指出 IL 受 expert state distribution 限制。citeturn15view0 | [FACT] 正好支持 yaw/lateral recovery role：BC/IL 学不到偏差恢复，必须在线交互补。 | [JUDGMENT] 任务是 drone racing，不是 obstacle planning；但 distribution-shift 逻辑高度可迁移。 |
| Offline-to-Online RL via Balanced Replay and Pessimistic Q-Ensemble | 2021 | arXiv:2107.00591 | 讨论 offline-to-online distribution shift 与 bootstrap error。citeturn15view1 | [FACT] 用来支持 baseline calibration 与 replay admission gate：新 worlds 过难会把 fine-tune 直接推入 OOD bootstrap 区。 | [JUDGMENT] 这是通用 O2O RL 论证，不直接给出 UAV geometry 指标。 |
| FLYINGTRUST | 2025 | arXiv:2510.26588 | 多平台多场景 benchmark；重复试验与 uncertainty-aware metrics。citeturn11academia0 | [FACT] 非常适合支持你们的 repeated seed / CI / platform-aware shadow eval。 | [UNCERTAIN] 重点在平台-场景联合 benchmark，不直接提供 reward/role 设计。 |
| A Benchmark Comparison of Learned Control Policies for Agile Quadrotor Flight | 2022 | arXiv:2202.10796 | 比较 learned control policy 的 sim-to-real；指出较抽象动作接口更稳。citeturn12view0 | [JUDGMENT] 支持“环境应验证恢复动作的可执行性”，而不是只看 kinematic success。 | [JUDGMENT] 它更接近控制层，不是障碍避障 benchmark。 |

## Route A RL 环境体系建议

[FACT] 当前工程里，`generate_seed_bank.py` 已把 `w4/w8/w11/w12/w18` 作为 OOD worlds 固化进 paired eval，且 `support / course35 / default` 明确映射到 `z_min/z_max` 与 disturb 配置；`train_dsrl_uav.py` 也仍按这个 env_mode 组织训练。换句话说，**历史 split 与旧 scenario 名称已经进入实验脚本，不是只有文档层遗留**。fileciteturn0file0 fileciteturn0file1

[FACT] 当前 env 侧已经支持 `world_pool`、`episode_config`、deterministic disturb schedule、`reward_version="v13"`、`reward_v13_cfg` 与 `offline_density`。因此，Route A 的正确动作不是重写环境，而是把“世界生成—验证—校准—metadata—split”变成显式系统。fileciteturn0file4 fileciteturn0file14 fileciteturn0file15

### 推荐 split 体系

| split | 用途 | world 来源 | 是否允许用于调参与早停 | 建议数量 | 备注 |
|------|------|------|------|------|------|
| `train` | [FACT] RL 采样与能力学习 | 仅来自新的 procedural role generators；**不含**历史 OOD worlds；按 role 均衡采样 | 是 | [JUDGMENT] 每个 role 先做 400–600 个已验证 worlds，8–12 episode seeds/world | 优先覆盖 generator family 多样性，而不是单纯增加 obstacle count。citeturn10view7turn14view0turn16academia0 |
| `val` | [FACT] reward/actor/ablation 选择 | 与 train 同 role，但 world seed、generator 参数区间、几何 family 持出 | 是，但**不可**参与最终 claim | [JUDGMENT] 每个 role 120–160 worlds，16 fixed seeds/world | 用于监控过拟合、reward hacking 与 curriculum 偏置。citeturn7view0turn11academia0 |
| `test` | [FACT] 新环境泛化 | unseen world seeds + held-out parameter corners + 少量组合型 worlds | 否 | [JUDGMENT] 每个 role 120–160 worlds，32 fixed seeds/world | 这是 Route A 主结论来源。citeturn14view0turn16academia0 |
| `historical_eval_only` | [FACT] 与旧结果可比 | `w4/w8/w11/w12/w18`、Phase α / OOD 旧环境、canonical route bank、旧 paired eval seeds | 否 | 全量保留 | 只做横向对比与 regression guard。fileciteturn0file0 |

### 推荐 role 设计

| role | 几何设计与触发机制 | 参数范围建议 | 核心指标 | 建议 seed 数 |
|------|------|------|------|------:|
| `anticipatory_train/eval` | [JUDGMENT] 以“直行会在 2–8 个 executed steps 内进入危险区，但左右/上下至少有一个低代价绕行 corridor”为核心；世界应保证存在明确 risk window 与 onset opportunity，而非大开阔区。可用单障碍前置、双障碍门框、前向 partial occlusion 三类模板。受 FlightBench 的 TO/VO/AOL 与 RAPTOR 的 risk-aware perception 启发。citeturn7view0turn10view0 | 直行 future soft-min clearance `0.25–0.75m`；替代 corridor clearance `>=0.75m`；最优绕行 path-stretch `<=1.25`；risk window 至少持续 2 个 RL steps。 | onset distance、onset TTC、risk-active ratio、`Δd_soft^H`、collision-free progress、path-stretch | [JUDGMENT] train 8/world；eval 32/world |
| `dense_recovery_train/eval` | [JUDGMENT] 以“可达但困难”的密集障碍为核心，不以障碍数量为核心。应显式包含 bottleneck、cul-de-sac、双侧绕行、多障碍串联恢复、局部最优诱导。FlightBench 的 Maze/MW、AvoidBench 的 environment metrics、RAPTOR/EGO 的 corridor/planning 经验都表明，困难来自窄通道、遮挡、急转与拓扑选择，而不是单纯障碍多。citeturn7view0turn8view0turn8view7turn10view1 | 占用率可控在 `8%–18%`；最窄 bottleneck 表面净空建议为 `1.1–2.0 × drone_diameter`；cul-de-sac 深度 `>=1.5m`；分支数 `>=2` 的比例不少于模板内 worlds 的 40%。 | SR、CR、trap entry、trap escape、time-to-escape、loop rate、side-flip count、min bottleneck clearance | train 8/world；eval 32/world |
| `support_expansion_train/eval` | [JUDGMENT] 目标是进入 frozen 数据低密度区域，但必须通过 safety/progress 门控，且低密度必须来自 **x/y/z 联合 cell**，不能只来自 z。当前 Reward v1.3 已采用 goal-aligned support cell 与 offline density hooks，因此环境应围绕这个表示设计。fileciteturn0file15 fileciteturn0file16 | 低密度 cell 建议用 frozen offline 计数的 `p20` 或 `p10` 阈值；单条最短可达路径中，低密度 cell 占比至少 `25%–40%`；且低密度变化必须覆盖至少两个维度。 | low-density safe coverage、new safe-cell count、OOD cell success、altitude-normalized support gain、path-stretch、out-of-support crash rate | train 8/world；eval 32/world |
| `yaw_lateral_recovery_train/eval` | [JUDGMENT] 角色核心不是“障碍更难”，而是“初始状态或中途状态偏离 nominal”。应构造 heading perturb、lateral offset、初始侧向速度、执行延迟、确定性 impulse 等。safe-control-gym 与 Air Learning 都支持把扰动做成可重复注入，可直接映射到你们现有 deterministic disturb schedule。citeturn10view3turn10view5 fileciteturn0file0 fileciteturn0file4 | start heading perturb `±15°/±30°/±60°`；lateral offset `0.3–1.2m`；deterministic impulse `0.2–0.6m`；执行延迟由 HIL latency distribution 或离散 delay bucket 模拟。 | recovery success、recovery time、cross-track integral、yaw error integral、disturb-to-clearance recovery、post-disturb SR | train 12/world；eval 40/world |

### Curriculum 建议

[JUDGMENT] **可以做 curriculum，但不建议做单轴 easy-to-hard curriculum。** 更好的做法是“role-balanced frontier curriculum”：每个训练阶段保持四类 role 同时存在，并在每个 role 内混合 `25% easier + 50% frontier + 25% harder`。这样做的依据有两层：其一，Procgen 显示训练分布多样性本身决定泛化上限；其二，Avalon/MetaDrive 显示更好的方式是让世界生成器显式要求某种技能，而不是只让难度递增。citeturn10view7turn14view0turn16academia0

[JUDGMENT] 对 iDP3-UAV，frontier 的定义不应再是“更高 z”或“更多障碍”，而应是每个 role 的**关键语义指标**接近当前 BC/FM 的失败边界。例如，anticipatory role 的 frontier 应是 onset opportunity 还存在但直行 future clearance 已明显不足的世界；dense role 的 frontier 应是 A* 可达但 bottleneck/flip/trap 指数接近 BC 失败阈值的世界。citeturn7view0turn8view0turn15view1

### Metadata schema 建议

[JUDGMENT] 每个 world/episode 至少应写入以下字段，并将它们作为 Route A 文档中的正式 schema，而不是仅在日志里临时输出：

`world_uid, split, role, role_version, generator_family, generator_params, source_build_id, start_world, goal_world, start_yaw, spawn_clearance_surface, goal_clearance_surface, inflation_radius, world_bounds, obstacle_stats, difficulty_stats, semantic_stats, baseline_stats, disturb_profile, delay_profile, fixed_seed_id, paired_eval_id`.

[FACT] 这套 schema 与当前工程是兼容的：现有 seed bank 已写入 `episode_seed, env_name, world_id, world_name_short, z_min, z_max, disturb_enable, disturb_events, fixed_start_goal` 等字段，只是还缺少 role/split/validation/baseline 语义层。fileciteturn0file0

### 一个必须写进设计文档的接口警告

[FACT] 当前 env 默认 `rl_action_steps=8`，但 `n_exec_steps` 默认值是 4；而 Reward v1.3 默认 `h_future=8`。这意味着**actor 看的 future horizon、reward 看的 future horizon 与 env 实际执行-再规划的 horizon 不是同一个概念**。如果不在环境文档里显式写清楚，`anticipatory` role 很容易出现“reward 认为该提前，但 env 实际上四步后就重规划”的语义漂移。Route A 文档应明确区分 `H_actor`、`H_exec`、`H_reward` 三个 horizon。fileciteturn0file14 fileciteturn0file15

## Validation 体系

[JUDGMENT] Route A 的 validation 应当是**世界 admission system**，不是单次 debug。推荐三层，每层都把结果写入 world metadata。

| 层级 | 输入 | 算法 | 输出 report | 失败处理 |
|------|------|------|------|------|
| Level 1 几何合法 | obstacle primitives、world bounds、start/goal | [FACT] 使用 obstacle surface distance；检查障碍参数有效、边界合法、start/goal 不在障碍内、不在地面以下。当前 `collision_geom` 已支持 surface-to-surface clearance 与 flyover 语义。fileciteturn0file8 | `spawn_clearance_surface, goal_clearance_surface, min_pairwise_obstacle_gap, world_bounds_ok` | 任一项失败直接 reject，不进入后续校准。 |
| Level 2 任务可达 | Level 1 通过的 world + inflated occupancy | [JUDGMENT] 先 2D XY coarse BFS 作快速 reject，再 3D occupancy A* / BFS 作最终 reachability；inflate 半径建议 `0.45–0.55m`，等于 `drone_radius 0.35m + margin 0.10–0.20m`。当前工程的 `drone_radius` 和碰撞语义已给出合理量纲。fileciteturn0file14 fileciteturn0file8 | `reachable, path_length_3d, path_stretch, bottleneck_clearance, homotopy_proxy` | 不可达则 reject；“过于曲折/过窄”先标 hard，再交 baseline calibration 决定去留。 |
| Level 3 能力语义有效 | reachability 路径、obstacles、reward hooks、disturb profiles、offline density map | [JUDGMENT] 用 role-specific semantic checks：anticipatory 看 risk window 和 safe alternative；dense 看 trap depth / branch count / loop诱因；support 看 low-density path ratio 与非单轴 novelty；yaw 看扰动后恢复是否在 kinematic 与 Gazebo 都可复现。FlightBench、AvoidBench、RAPTOR、Air Learning 都提供了“难度/感知/延迟/重复扰动”的外部依据。citeturn7view0turn8view0turn10view0turn10view5 | `semantic_pass, semantic_scores{...}, role_trigger_frames, recommended_bucket` | 未触发预期能力则不属于该 role；可回收到其他 role 或回炉生成。 |

### Level 1 细节建议

[JUDGMENT] 对 start/goal 的 surface clearance，建议在 Phase β 文档中给出明确数值门禁，而不是写“应离障碍远一些”。结合当前 `drone_radius=0.35m` 与 Route A 目标，我建议：

- `spawn_clearance_surface >= 0.60m`
- `goal_clearance_surface >= 0.65m`
- 若 role 为 `yaw_lateral_recovery`，允许 `spawn_clearance_surface` 下降到 `0.50m`，但必须不是由**初始化就贴障**导致，而是由 heading/offset/impulse 触发。fileciteturn0file8 fileciteturn0file14

这是一个 [JUDGMENT]，不是文献定值；但它的优点是把“能力测试”和“无意义起点碰撞”切开。

### Level 2 细节建议

[JUDGMENT] 用 A* / BFS 做可达性检查**符合**你们的方法论，只要它只出现在 world validation / dataset curation，而不出现在策略执行图中。这里与 EGO/RRT/A* 接到策略后改轨是两回事：前者是 benchmark hygiene，后者是 inference-time planner takeover。前者不违反 MC-1~MC-5。citeturn8view7turn7view0

[JUDGMENT] 为了避免 2D reachable 但 3D 不可恢复、或者 3D 过于昂贵，建议采取“双阶段 reachability”：

- `Stage-2a`: 2D XY inflated occupancy BFS，快速去掉明显封闭世界。
- `Stage-2b`: 3D voxel A*，写出 path length、最窄 surface clearance、z-range、转弯累计角等指标。
- `Stage-2c`: 对 `support_expansion` 和 `yaw_lateral_recovery` world，再做一次“执行窗口可达性”检查，确保在 `H_exec` 重规划节律下仍存在 recovery corridor。fileciteturn0file14

### Level 3 role-specific semantic checks 建议

| role | 必要 semantic checks |
|------|------|
| `anticipatory` | [JUDGMENT] 直行参考轨迹在 `2–8` 个 executed steps 内 `d_soft^H` 低于阈值；至少有一条替代 corridor 的 `d_soft^H` 高于阈值；free-cone 中前向 p20 明显差于侧向或上/下方向；open-space symmetry 不成立。依据来自 FlightBench 的 VO/AOL 与 RAPTOR 的 perception-aware risk logic。citeturn7view0turn10view1 |
| `dense_recovery` | [JUDGMENT] 必须有 trap 诱因而不只是障碍多：例如 cul-de-sac depth、branch ambiguity、loop propensity、bottleneck ratio、连续 sharp-turn 计数。FlightBench 的 Maze/MW 与 AvoidBench 的 complexity metrics 支持这种语义化难度。citeturn7view0turn8view0 |
| `support_expansion` | [JUDGMENT] 候选可达路径上低密度 cell 占比应超过阈值，且低密度不能主要来自 `z` 单轴；建议同时记录 `(x_parallel, x_perp, z)` 三维低密度贡献。当前 Reward v1.3 已使用此 goal-aligned support cell 表示。fileciteturn0file15 fileciteturn0file16 |
| `yaw_lateral_recovery` | [JUDGMENT] 扰动必须是 repeatable，并且在 Gazebo shadow eval 中能复现同方向恢复难点；否则只能算 kinematic artifact。Air Learning 与 safe-control-gym 都支持这类可重复 delay / disturbance 设计。citeturn10view3turn10view5 |

### 每个 world 应输出的 report

[JUDGMENT] 至少输出一个 `world_report.json`，字段包含：

- `geometry`: obstacle count、volume ratio、spawn/goal surface clearance、bounding box
- `reachability`: 2D reachable、3D reachable、path length、stretch、bottleneck surface clearance
- `semantics`: role-specific scores
- `baseline_calibration`: BC/FM SR、EGO SR、CI、paired seeds
- `admission`: `accepted_train / accepted_val / accepted_test / historical_only / rejected / beyond_BC_EGO_boundary`
- `audit`: generator seed、code commit、world build version、validation time

[FACT] 这种 report 与当前工程风格兼容：你们已经在 seed bank 中存 episode-level deterministic config，在 reward 中存 term/metric summary，在 env 中存 reward history 和 disturb schedule。fileciteturn0file0 fileciteturn0file12 fileciteturn0file11

## Baseline calibration 流程

[FACT] 当前项目已经有 paired evaluation 的工程基础：`generate_seed_bank.py` 会为每个 env/world 组合生成固定 episode seeds，并可固定 `start=(-8,0,2), goal=(8,0,2)`，同时将 disturb events 一并记录。对于 Route A，这正好可以升级成 calibration 与 CI 的标准入口。fileciteturn0file0

[JUDGMENT] 我建议将 calibration 分成四步，而不是“一次跑 BC 看成功率”。

| 步骤 | 基线 | 目的 | 建议 episode 数 | 输出 |
|------|------|------|------:|------|
| Feasibility precheck | inflated A* / BFS | 排除不可达世界 | 全量 | `reachable / unreachable` |
| Calibration-1 | frozen BC/FM | 测当前 policy boundary | [JUDGMENT] 每个 role-bucket 至少 50 paired episodes，3 个随机种子或 3 个 ckpt 版本 | `SR, CR, onset, trap, support, recovery metrics + 95% CI` |
| Calibration-2 | EGO 或近似上界 | 判断“世界太难”还是“当前 policy 不会” | [JUDGMENT] 每个 role-bucket 30–50 episodes | `upper-bound feasibility profile` |
| Calibration-3 | random / trivial heuristic / no-op | 给 reward hacking 提供下界对照 | 30–50 episodes | `sanity floor` |

### 进入 RL train pool 的门禁

[JUDGMENT] 某个 world 或 world-bucket 进入 `train`，应同时满足：

1. Level 1–3 全通过。  
2. frozen BC/FM **不是** 近乎完美，也**不是** 近乎全灭。  
3. 若 EGO/upper-bound 也几乎全灭，则标记为 `beyond_BC_EGO_boundary`，改放 `stress_only`。  
4. paired episodes 的 Wilson 95% CI 或 bootstrap CI 不过宽。  
5. role 指标与声明对齐，而不只是 `reward_total` 可优化。citeturn11academia0turn15view1

### 各 role 的 calibration 经验阈值

下表是 [JUDGMENT]，用于 v1 文档中的 admission gate 初稿：

| role | BC/FM 合理区间 | EGO 合理区间 | admission 判断 |
|------|------|------|------|
| `anticipatory_train` | SR 约 `35%–85%`；但 onset 指标显著落后于“理论可绕行窗口” | 通常高于 BC/FM | 若 BC 已 95%+，太容易；若 BC/EGO 都接近 0，世界设计或校准有问题。 |
| `dense_recovery_train` | SR 约 `15%–70%` | 通常明显高于 BC/FM | 目标是“可达但困难”；如果 EGO 也失败，应转 stress-only。 |
| `support_expansion_train` | safe low-density coverage 约 `5%–40%`；SR 约 `20%–70%` | 中高 | 若只看到升高高度而 coverage 没扩展，不应入池。 |
| `yaw_lateral_recovery_train` | nominal world 下 BC 应较高；加入 perturb 后下降到 `20%–70%` 更合理 | 中高 | 如果 nominal 都低，说明测试的是基础避障，不是 recovery。 |

### 为何必须有 repeated seeds 与 CI

[FACT] FLYINGTRUST 明确采用 repeated trials 与 uncertainty-aware metrics；FlightBench、AvoidBench 也都强调统一协议与 difficulty-aware performance report。对于 iDP3-UAV，这尤其重要，因为 Route A 不是比较平均 reward，而是比较“能力指标是否真实改善”。citeturn11academia0turn7view0turn8view0

[JUDGMENT] 具体实现上：

- 二值指标如 SR/CR/TrapEscapeRate：用 Wilson 95% CI。
- 连续指标如 onset distance、future clearance gain、cross-track integral：用 bootstrap 95% CI。
- 评估必须 paired：同一 `world_id + start + goal + disturb_schedule` 比 BC/FM vs RL。  
- 若 CI 大幅重叠，不应写进主结论，只能写作“趋势”。  

这比“只看均值提升”更能防止 reward hacking 被误判为能力提升。

### 与当前 Reward v1.3 的接口绑定

[FACT] 现有 Reward v1.3 已经定义并追踪 `d_soft_h`、`risk_gate`、`ttc_valid`、`trap_active`、`side_flip_count`、`loop_detected_rate`、`support_cell_density` 等量；但当前 smoke eval 的 dummy scenario 中，support 相关指标基本未被激活，这说明**环境端必须真正提供 offline density 与 role 触发条件**，否则 reward term 虽然存在，也无法成为可审查证据。fileciteturn0file15 fileciteturn0file12 fileciteturn0file11

## 风险与反例

下面这些都应写进设计文档的“失败模式”章节，并配对应 mitigation。

- [FACT] **不可达 world 被误当成策略失败。** 解决方法是先做 Level-2 inflated reachability，并把 `reachable=false` 从训练与主结论中剔除。citeturn8view7turn7view0

- [FACT] **historical eval-only 场景被意外回灌到训练。** 当前 `w4/w8/w11/w12/w18` 已在 Route B seed bank 中被显式列为 OOD worlds，因此 Route A 必须在 schema 层阻止它们进入 train/val。fileciteturn0file0

- [JUDGMENT] **support expansion 退化成飞高。** 解决方法是 support cell 采用 `(x_parallel, x_perp, z)` 三维联合计数，验收时另报 altitude-normalized support gain，并要求低密度贡献不能只来自 z。依据来自当前 Reward v1.3 的 support cell 设计。fileciteturn0file15 fileciteturn0file16

- [JUDGMENT] **dense 只是 obstacle count 多，但没有 trap / recovery。** 解决方法是 Level-3 semantic check 里强制写入 cul-de-sac depth、branch count、loop propensity、bottleneck ratio，而不是只存 `num_obstacles`。FlightBench 与 AvoidBench 都说明复杂度不能只用数量描述。citeturn7view0turn8view0

- [JUDGMENT] **onset reward 在开阔区奖励乱偏航。** 解决方法是 anticipatory role 必须满足“直行危险 + 替代 corridor 可行 + risk window 可测”，并在评估里同时检查 `Δd_soft^H` 与 path-stretch。RAPTOR 的 risk-aware / yaw-for-observation 很能说明这一点。citeturn10view1turn10view2

- [JUDGMENT] **yaw recovery 只是 simulator artifact。** 解决方法是同一 role 要在 kinematic 与 Gazebo shadow subset 上复核，并保留 latency/impulse metadata。Air Learning 与 safe-control-gym 都强调 repeatable latency/disturbance；当前工程也已支持 deterministic disturb schedule。citeturn10view3turn10view5 fileciteturn0file0 fileciteturn0file9

- [JUDGMENT] **curriculum 只学 easy case，没学能力。** 解决方法是 role-balanced frontier curriculum，不做单轴 z-range / density ramp。Procgen、Avalon、MetaDrive 都支持“多样性与生成器可控性”比线性难度更重要。citeturn10view7turn14view0turn16academia0

- [FACT] **reward_total 上升，但 SR/CR/onset/support/recovery 不改善。** 解决方法是把主门禁从 `reward_total` 切换为 role metrics；这与 AvoidBench/FlightBench 的 benchmark 做法一致。citeturn8view0turn7view0

- [JUDGMENT] **EGO 也失败的区域被错误声明为“RL 泛化成功边界”。** 正确做法是标为 `beyond_BC_EGO_boundary` 的 stress/failure-boundary，不进入 headline claim。citeturn8view7turn10view0

- [FACT] **Route A fine-tune 被 offline-to-online distribution shift 直接冲垮。** O2O RL 文献表明，online samples 会迅速进入 offline dataset 覆盖不到的 state-action 区，导致 bootstrap error。环境 admission gate 与 balanced calibration 正是为防这个问题。citeturn15view1

- [FACT] **`H_actor / H_exec / H_reward` 不一致导致语义漂移。** 你们当前 env 与 reward 已经表现出这种潜在风险；若文档不写清楚，anticipatory / recovery 结果会很难解释。fileciteturn0file14 fileciteturn0file15

## 最终建议

### 是否建议先做 RL 环境重设计，再训练

[JUDGMENT] **是，建议先做环境重设计。** 原因不是“当前环境不能跑”，而是“当前环境不够可审查”。现有 Route B 管线已经说明你们能做训练、seed bank、paired eval、reward hooks；但它还没有把 world semantics、split isolation、validation、calibration 写成系统。对于 Route A，这一层比再加一次训练更优先。fileciteturn0file0 fileciteturn0file1 fileciteturn0file14

### 给 `RouteA_RL_Environment_Design_v1.md` 的建议目录

- **§0 文档定位**  
  明确本文档只定义 Route A 的 RL 环境体系、split、validation、calibration 与 metadata，不改变 MC-1~MC-5，不引入 post-hoc planner/shield。

- **§1 最终目标与 RL 能力目标**  
  把 anticipatory avoidance、dense recovery、support expansion、yaw/lateral recovery 四类能力目标形式化，并写清楚它们不是 generic reward improvement。

- **§2 环境 role 形式化**  
  定义 `anticipatory / dense_recovery / support_expansion / yaw_lateral_recovery` 的几何模板、触发条件、关键 semantic metrics、难度 bucket。

- **§3 train / val / test split**  
  写清 train/val/test/historical_eval_only 的世界来源、用途、禁止事项、paired seeds 协议。显式废弃旧的 `support/default/dense/random_stress` 作为正式 role 名称，只保留兼容别名。当前旧脚本的命名残留可作为“迁移兼容说明”。fileciteturn0file0 fileciteturn0file1

- **§4 world metadata schema**  
  给出强制字段列表：`split, role, start_world, goal_world, spawn_clearance, goal_clearance, generator_params, disturbance_params, difficulty_stats, semantic_stats, baseline_stats` 等。

- **§5 三层 validation**  
  写明 Level 1 几何合法、Level 2 reachability、Level 3 semantic validity 的输入、算法、阈值、输出 report 与失败处理。说明 A*/BFS 只用于 validation，不用于 policy execution，因此不违反 MC。 

- **§6 baseline calibration**  
  分别定义 frozen BC/FM、EGO、feasibility checker 的校准流程、paired seeds、CI 计算、admission gate、`beyond_BC_EGO_boundary` 标签。

- **§7 与 Reward v1.3 / Route A A0-A2 的接口**  
  建议这样写：  
  - `A0 env_core`: obs/action/step/episode_config 语义。  
  - `A1 reward_side_channels`: `d_soft_h, risk_gate, support_cell, trap flags, disturbance metadata`。  
  - `A2 evaluation_bridge`: paired seed bank、historical eval-only、Gazebo shadow subset。  
  当前 Reward v1.3 与 env 代码已具备这类接口雏形。fileciteturn0file14 fileciteturn0file15 fileciteturn0file16

- **§8 风险评估**  
  将本报告“风险与反例”中的至少 8 项失败模式改写成正式 checklist，并给出 reject / relabel / stress-only / regenerate 的处理流。

- **§9 MC-1~MC-5 合规检查**  
  逐条写明：环境里的 A* / BFS / EGO 只做 validation / calibration，不做执行；historical eval-only 不进入训练；不重采 EGO 数据；性能归因来自角色化世界与策略指标，而非后处理。

### 一个适合直接写入文档的总裁决

[JUDGMENT] 可以把下面这句话原样放进文档摘要区：

> Route A 的首要任务不是再扩充训练脚本，而是把 RL 环境从“旧 world 池 + 旧命名 + 旧难度习惯”升级为“role-driven、metadata-complete、3-level validated、baseline-calibrated”的能力证据系统。只有在这一步完成后，Reward v1.3、Route A actor、以及后续 Gazebo shadow eval 才能产生可归因、可复现、可写进论文的结论。citeturn7view0turn8view0turn10view7turn11academia0 fileciteturn0file0 fileciteturn0file1