# 通过 RL 微调实现三类无人机高级机动能力的可行性评估

## TL;DR
- **横移绕行品质提升（机动2）是当前项目基础上最可能通过 RL 微调成功的方向**：它属于"流形内（in-manifold）"优化问题，专家已演示横向避障的基本动作，RL 只需重新加权偏好（更大净距、更平滑路径），与 FQL/DPPO 的"on-manifold 探索"机制天然契合，工程成功率高（基于文献与理论的工程判断约60–80%）。
- **垂直越障（机动3）风险中等偏高**：z 维信号在专家数据中极稀疏（dpos_z 中位数0.000m），属于"弱流形内/流形边缘"问题，纯离线 RL 因行为正则化（FQL 的 α 蒸馏项）难以激活未演示的 z 动作模态，必须配合在线交互 + 新建低顶/桥洞环境 + 显式 z 维 reward shaping，预估成功率30–55%。
- **后退脱困（机动1）风险最高、最不可能仅靠 RL 微调成功**：物理后退/换向动作完全在专家演示分布外（流形外，out-of-manifold），离线 RL 的行为约束和 OOD 动作 Q 值高估在理论上阻止其可靠外推；需要 DAgger 式数据增广或 residual RL + 在线交互 + 时序记忆（n_obs=3 是根本瓶颈），单纯 FQL 离线微调几乎不可行，预估成功率<25%。

## Key Findings

1. **三类机动相对当前 BC 专家分布的位置决定了一切。** 项目专家数据由 EGO-planner（前向梯度规划器）采集，几乎不演示后退、横移、爬升。RL 微调能否成功，第一性原理上取决于目标动作相对专家流形的位置：横移在流形内（部分演示）、垂直在流形边缘（极稀疏）、后退在流形外（零演示）。

2. **离线 RL 在理论上无法可靠产生专家分布外的动作。** Flow Q-Learning（Park, Li & Levine, arXiv:2502.02538, ICML 2025）把问题表述为约束优化——它训练"一个表达力强的一步策略用 RL（而非直接引导迭代式 flow 策略），同时用 BC 损失单独训练 flow 策略"，并通过一个 α 加权的 BC 蒸馏项把学习策略拉回 BC 策略的动作分布（该项是二者动作分布间 2-Wasserstein 距离的上界，α 越大约束越紧）。Fujimoto 的 BCQ（Fujimoto, Meger & Precup, "Off-Policy Deep Reinforcement Learning without Exploration", arXiv:1812.02900）证明：**"due to errors introduced by extrapolation, standard off-policy deep reinforcement learning algorithms, such as DQN and DDPG, are incapable of learning with data uncorrelated to the distribution under the current policy, making them ineffective for this fixed batch setting."** OOD 动作的 Q 值被系统性高估（CQL 用保守下界、BEAR 用 MMD support constraint 来抵消）。这是后退脱困用纯离线 FQL 几乎注定失败的根本理论原因。

3. **扩散/Flow 策略的探索是"on-manifold"的，是双刃剑。** DPPO（Ren, Lidard, Ankile et al., arXiv:2409.00588）的探索"在预训练数据流形附近结构化进行"，作者明确坦承：**"It is possible, however, that the on-manifold exploration we observe with DPPO hinders fine-tuning when aggressive, unstructured exploration is desired. We conjecture this is the case in the Lamp environment with Low randomness, in which DPPO slightly underperforms the Gaussian baseline."** 这对机动2（横移品质优化，目标就在流形内）是优势，但对机动1（后退，需流形外探索）是致命限制。

4. **后退脱困/死胡同逃逸有先例，但都不是"冻结数据集+纯离线微调"路线。** 死胡同逃逸用 SAC 从零训练 + 前进-后退多相轨迹生成器（arXiv:2511.22338）；窄环境逃逸（Embodied Escaping, arXiv:2503.03208）用 RL + A* 混合训练 + 动作掩码 + 两阶段课程；腿足 fall recovery（arXiv:1901.07517 及 2023 RA-L "Learning Complex Motor Skills for Legged Robot Fall Recovery"）全部是在线 RL 从零学 + 状态初始化设计。这些都依赖在线交互与专门的探索/课程机制。

5. **垂直机动在 DRL 文献中有成功先例但成功率偏低。** 可变高度 DRL 避障（human-in-the-loop, arXiv:2304.05959；MAVRL, arXiv:2402.08381）证明 z 维可学习；DDPG 3D 导航（arXiv:2003.10923）报告越障行为，但带障碍场景任务完成率降至82–84%（vs 无障碍100%）。

6. **n_obs=3（约0.6秒）短时序窗口对后退脱困构成 POMDP 瓶颈。** 死胡同/局部最优逃逸本质需要 belief state（记住"哪里来的、试过哪些方向"）。MAVRL 明确证明记忆对大障碍避障至关重要；POMDP 文献（如 "Success in Humanoid RL under Partial Observation", arXiv:2507.18883）显示需 RNN/Transformer/Mamba 记忆。3帧观测对反应式横移足够，对需历史的脱困不足。

## Details

### A. 理论可行性逐项分析

**机动1 后退脱困（流形外）。** 形式化为 POMDP 而非 MDP：死胡同/凹形障碍/局部最优的逃逸需要 belief state，仅靠瞬时观测无法区分"正在深入陷阱"与"正在脱困"。reward 上，"脱困成功"是天然稀疏信号（到达陷阱外某区域），需课程学习或势场逃逸塑形。最大障碍：(a) 后退动作（dpos 负向、dyaw 大幅换向）完全不在60151帧专家数据中；(b) 离线 RL 行为约束（FQL α 项、CQL、BEAR 的 support constraint）原理上禁止外推到这些未见动作；(c) OOD 动作 Q 值高估（BCQ/CQL）使 critic 不可信；(d) n_obs=3 不足以支撑 belief state。子类(a)恢复行为与子类(b)局部最优逃逸都受此约束，但(b)若局部最优区仍可前向绕出，则部分可借横移解决，纯"物理倒车"的(a)最难。

**机动2 横移绕行品质（流形内）。** 形式化为近似 MDP（点云+目标已含足够空间信息），时序记忆非必需。reward 为密集 shaping：净距项（惩罚<安全阈值的贴障）、路径开阔度项、平滑度/反震荡项（惩罚 yaw 方向横跳）、进展项。理论上这是在专家已覆盖的动作模态内重新加权偏好——正是 DPPO on-manifold 探索与 FQL 行为正则化最擅长的"在数据支撑内找更高回报模态"。无 OOD 外推问题，无 POMDP 瓶颈。

**机动3 垂直越障（流形边缘）。** 形式化为 MDP（需在 state 中确保 z 与障碍顶部高度信息可辨）。专家 z 信号极稀疏（dpos_z 中位数0.000m，最大 sustained climb 1.54m），意味着 z 动作模态在数据中近乎退化为常数。离线 RL 的行为约束会把策略 z 输出拉回≈0；要激活主动爬升必须靠在线交互注入新的 z-action 经验 + 强 z 维 reward。介于机动1与机动2之间：z 动作非完全零演示（有1.54m climb），但远未充分覆盖。

### B. 工程实现难度与方法适配

**reward shaping 难度排序（易→难）：** 机动2（密集、可解析定义净距/平滑度）< 机动3（需定义"越障成功"+ 鼓励 z 探索，半稀疏）< 机动1（"脱困成功"稀疏 + 需课程或势场逃逸塑形）。

**与现有架构兼容性。** 点云输入 + 11d action + step-wise delta + Flow/FM backbone 与 FQL 高度兼容（FQL 本就基于 flow-matching 策略，可在 actor-critic 上几行实现，单 T4 可行）。DPPO 需把每个去噪步当作 MDP 转移，计算量较大但可行。三类机动共享同一架构，差异在 reward 与是否需新增模块。

**探索难度。** 机动2：扩散多模态探索足够发现更优横移路径。机动3：纯 Gaussian/扩散探索在 on-manifold 约束下难以自发产生大幅爬升，需 reward 强驱动 + 在线 rollout。机动1：on-manifold 探索原理上发现不了流形外的倒车，需 residual RL（额外 RL 分量叠加冻结 BC 策略，如 ResiP arXiv:2407.16677、ResFiT）或 DAgger 注入后退恢复样本，或在线 RL 从特定初始态探索（PTR 类工作约需 ~20K 在线步才发现全新行为）。

### C. 文献报告成功率/先例汇总

| 机动 | 代表工作 | 方法 | 报告成功率 | 与本项目差异 |
|---|---|---|---|---|
| 横移/3D避障 | He et al. 2020 (arXiv:2008.02521) | TD3+演示(IL→RL, decayed imitation loss) | DRL 约88.5%±4.2%（文献报告，与价值迭代对比语境） | 在线交互、深度图 |
| 横移/局部规划 | TD3 局部规划 (Sci. Rep. 2024) | TD3 在线 | 无障碍93%、有障碍92%（原文） | 在线、Gazebo |
| 死胡同逃逸 | arXiv:2511.22338 | SAC 从零+前进/后退轨迹生成器 | 优于经典规划器（解出更大比例实例） | 在线、Ackermann 地面车 |
| 窄环境逃逸 | Embodied Escaping (arXiv:2503.03208) | RL+A*混合+课程+动作掩码 | 显著优于规划与RL基线 | 在线、地面车、LiDAR |
| 垂直越障 | DDPG 3D (arXiv:2003.10923) | DDPG 在线 | 越障演示，含障碍82–84% | 在线、简化动力学 |
| 可变高度 | human-in-loop (arXiv:2304.05959) | DDPG/TD3+人在环 reward | 提升收敛与成功率 | 在线、reward可调 |
| 腿足恢复 | arXiv:1901.07517 等 | 分层行为RL在线 | 真机可部署 | 在线从零、本体感受 |

**结论性判断：** 横移品质提升类任务在文献中成功率稳定在约85–93%区间，是公认可解问题；垂直机动可学但含障碍成功率掉到80%出头，属中等；后退/死胡同逃逸虽有成功案例，但**无一例**采用"冻结次优演示数据集 + 纯离线微调"，全部依赖在线交互、专门探索机制或课程——这正是本项目数据冻结约束下的最大风险。

### OOD 学习理论小结
- 离线 RL = 在数据 state-action 支撑内的约束优化（FQL）；α/χ²/MMD 等正则项是 support constraint，非外推机制。
- OOD 动作 Q 值系统性高估（BCQ 外推误差、CQL 保守下界、BEAR support constraint）。
- 扩散/Flow 微调（DPPO）on-manifold 探索：流形内优化强、流形外发现弱（作者明示其在需激进探索时反而受阻）。
- 真正发现 OOD 新动作模态需：(a) 在线 RL + 新探索/reward（PTR 类约 ~20K 步）；(b) residual RL 额外分量（ResiP/ResFiT）；(c) DAgger 专家注入。SRDP（arXiv:2307.04726）的 state-reconstruction 可改善 OOD **state** 泛化（在 D4RL 缺失目标区任务报告167%提升），但解决的是 OOD 状态下选合理动作，不等于产生全新动作模态。

## Recommendations

**第一阶段（立即，最高成功率）——主攻机动2横移品质。**
- 算法：FQL 离线微调为主（与现有 FM backbone 一行接入、单 T4 可行），或 DPPO 若可承担在线 rollout。
- reward：密集多目标 shaping = w1·进展 + w2·net-clearance（对<安全阈值贴障加重惩罚，直接打击当前0.30m刮桨级净距）+ w3·路径平滑/反 yaw 横跳 + w4·开阔度。多目标梯度冲突用 PCGrad 缓解。
- 架构：无需扩时序窗口、无需新模块。n_obs=3 足够。
- 基准：贴障净距中位数从0.30m提升至≥0.5m、yaw 方向反转频率下降、绕行成功率维持≥90% → 视为成功。

**第二阶段（中等优先）——机动3垂直越障，须新建低顶/桥洞环境。**
- 算法：offline-to-online RL（先 FQL 离线 warm-start，再在线交互注入 z 经验），或 residual RL 专学 z 修正。
- reward：半稀疏 = 越障成功（通过低顶/桥洞）+ 鼓励主动 z 调整 + 高度安全裕度。需显式在 state 中编码障碍顶部相对高度。
- 关键前置：在线交互能力（数据可冻结但环境须可交互 rollout）；否则纯离线因 z 行为约束几乎学不出主动爬升。
- 基准：在带顶障碍环境越障成功率从 BC 基线（≈0，专家不爬升）提升至>50%。

**第三阶段（探索性/高风险）——机动1后退脱困，不建议纯 RL 微调。**
- 推荐组合（按性价比）：(1) DAgger 式数据增广——在仿真中人工/脚本演示后退恢复，注入冻结数据集的"增广分区"，再 BC+RL；这是绕过 OOD 外推最直接的路径。(2) residual RL——冻结现有 BC/FM 策略，叠加一个小型在线 RL 残差策略专门输出脱困修正动作。(3) 显式时序记忆——将 n_obs 从3扩到≥8–16 或引入 Mamba/Transformer/RNN belief 编码（Mamba Policy arXiv:2409.07163 可在保持参数量下加时序），解决 POMDP 瓶颈。(4) 反向/区域增长课程 + 势场逃逸塑形提供密集引导。
- 基准/止损线：若在线交互预算受限或环境不可交互，机动1应降级为"分层架构外挂一个规则式/经典脱困控制器（如检测 trap 后触发后退-换向 heuristic）"，而非强求端到端 RL 学出。

**改变建议的阈值：** 若数据集可解冻并允许采集后退/爬升演示 → 机动1、3 难度大幅下降，可直接 BC+RL；若可承担充分在线交互（数万步）→ 机动3 成功率显著上升、机动1 变为可尝试；若坚持完全冻结数据+纯离线 → 仅机动2 值得投入。

## Caveats
- 文献报告的约85–93%成功率来自不同输入模态（深度图/LiDAR）、不同平台（地面车/腿足）、且多为在线 RL 从零训练，迁移到"点云+冻结演示+离线微调"的本项目设定时成功率会下降，应视为乐观上界。He et al. 2020 的88.5%±4.2%数字出自对比性表述语境（与价值迭代法对照），引用时应注意其条件。
- DPPO 关于"on-manifold 探索阻碍激进探索"的表述，原文是针对 Lamp-Low 环境的 **conjecture（猜想）**，非已证定理；但与离线 RL support-constraint 理论方向一致，可作为强证据但非铁证。
- "成功率区间"为基于文献与理论的工程判断，非本项目实测；实际数值依赖 reward 调参、环境难度与算力。
- 单 T4 24GB 对 FQL（轻量、flow-matching 可几行实现）友好，但对 DPPO 多去噪步在线 rollout 或大时序 Transformer 可能吃紧，需评估。