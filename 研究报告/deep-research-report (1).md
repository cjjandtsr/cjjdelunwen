# Reward v1.3 + Route A / Hierarchical Deep Research Report

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-06-27 |
| 项目 | iDP3-UAV |
| 目标 | Reward v1.3 + Route A / hierarchical steering 设计前研究 |

文中标签含义：**[FACT]** 由项目事实或文献直接支持；**[JUDGMENT]** 基于现有证据的工程判断；**[ASSUMPTION]** 需要在实现前确认的实现假设；**[UNCERTAIN]** 证据仍不足或外推较强。

## Executive Summary

- **[FACT]** Route B 关闭的核心含义不是“RL 一概无效”，而是“当前 low-rank latent steering + SAC 这条支路在稳定性过关后，仍未能在 support/default/canonical paired evaluation 上持续超过 BC”，因此下一阶段的重点应从“再调同一路 critic / latent steering”转向“改 reward 信号与改主策略 fine-tuning 机制”。这一判断与项目给出的 paired evaluation 结果一致，也与近年的 chunked-Q / high-dimensional action RL 文献对 critic 偏差与高维动作学习难度的结论相符。citeturn31view0turn4view2turn4view3

- **[JUDGMENT]** Reward v1.3 的第一优先级应是把“提前避障”从隐含目标改成**显式、可测、风险条件化**的奖励对象：不是单独奖励横移或偏航，而是在 **TTC 下降 / future clearance 变差** 的风险窗口里，奖励更早出现、且确实提高未来最小间隙的转向或横移；否则会把策略推向无意义绕远。多机器人 / crowd navigation 文献已经证明，expected collision time、TTC-force、forecasted collision risk 这类前瞻信号可以把“快撞了才躲”改成“提前规避”。citeturn27search0turn27search3turn14search6

- **[JUDGMENT]** future clearance 不应只做一个分量。更稳妥的做法是采用**双层设计**：一层是**state-only free-space potential**，走 PBRS；另一层是**action-conditioned future clearance auxiliary reward**，直接对当前 FM 输出的执行轨迹未来 \(H\) 步最小间隙进行奖励。原因是 PBRS 虽然能保持最优策略不变，但它恰恰因此不擅长引入你真正想新增的“更早躲、更愿意进低密度支持域”的偏好；这类偏好必须允许改变最优策略。PBRS 还要求 terminal / truncation state 的 potential 为零，否则会破坏 policy invariance。citeturn29search0turn30view0

- **[JUDGMENT]** Route A 默认不应从 **QC-FQL / 176d chunk critic** 起步，而应优先做 **ReinFlow 风格的 direct flow-policy online fine-tuning**。原因很直接：Phase1aPolicyFM 本身就是 flow matching policy，ReinFlow 专门解决“如何对 flow policy 做在线 RL、且在 very few / even one denoising step 下仍可稳定优化”的问题；同时它不需要先学一个 176d chunk-Q 再把 actor 拉偏。相比之下，Q-chunking 系列虽然能提升长时 credit assignment，但论文自己也强调 chunk critic 的 open-loop / reactivity 问题与 chunk-size 扩展难题。citeturn4view1turn22view0turn22view2turn6view0turn31view0

- **[JUDGMENT]** DPPO 是可信备选，但不宜作为默认主线。DPPO 的最大优势是**structured on-manifold exploration**，且作者明确指出它最适合“pre-training 已提供足够相关成功模式覆盖”的 fine-tuning；而 iDP3-UAV 当前最棘手的问题恰恰是 full-space support 不足，尤其是 0–3m 高度之外与更大 x/y/z 组合空间覆盖不足。也就是说，DPPO 的强项与本项目最想突破的弱项并不完全对齐。citeturn4view0turn20view0turn20view3turn21view0

- **[JUDGMENT]** 如果要做 hierarchical steering，**第一候选应是离散 mode / corridor token + FM actor**，不是 residual trajectory actor。原因在于，它最容易满足 MC-1 到 MC-5：上层只负责内部模式决策，下层 FM 仍输出最终执行轨迹，且 mode token 对“左绕 / 右绕 / 上绕 / 下绕 / recover”这类 dense obstacle 分岔选择有较强可解释性。RAPTOR 的多拓扑路径、yaw 主动观察，以及 HDP 的高层目标—低层生成结构，都支持“高层做离散/稀疏决策、低层做轨迹生成”这一路线。citeturn32view1turn18view0turn34view0turn18view1

- **[UNCERTAIN]** full-space support expansion 目前在公开文献中没有一个可直接照搬到你这个 frozen-EGO、end-to-end FM UAV 设定里的标准 reward 配方。最可行的工程路线是：把它定义为**成功条件下的低密度空间覆盖扩展**，用受安全和进展门控的 novelty / occupancy bonus 绑定到“安全地进入旧数据低覆盖区域并完成任务”，而不是简单鼓励升高或飞远。这一点需要依赖你们自己的短训练 gate 来验证，而不能直接相信论文先验。citeturn30view0turn32view0

## Project Diagnosis

### Route B 为什么失败

**[FACT]** 按项目给出的结果，Route B 的 current low-rank DSRL-SAC branch 已经完成稳定性验证：无 NaN/Inf、invalid_obs_rate=0%，但在 10k 训练后平均 reward 仍低于 BC；在 support / default / canonical paired evaluation 上也没有形成持续超越 BC 的证据。尤其 canonical paired evaluation 中，BC 在固定 route 上的 default avg 达到 62%，而 SAC variants 只有 52–58%，并且经常主动偏离更优 BC 路径导致更多碰撞。  
**[JUDGMENT]** 这说明问题不再是“优化炸了”或“critic 没收敛”，而更像是：**冻结 FM 主体，只在 latent steering 上做低秩 RL，能力注入带宽不够，且 value 信号不足以稳定地把 actor 推向真正的新避障能力。**

**[JUDGMENT]** 这一结论与近年的高维动作 RL 文献是一致的：Vlearn 明确把高维动作空间中的 action-conditional critic 视为 sample inefficiency 的核心来源，并提出只用 state-value critic 来绕开显式 \(Q(s,a)\)；T-SAC 与 AC3 也都在朝“不要再把所有难度都压到一个孤立的高维 critic 上”这个方向走。对于 iDP3-UAV，若动作块是 \(11 \times 16 = 176\) 维，这个问题只会更严重。citeturn4view2turn4view3turn4view4

### 当前 reward 缺什么

**[FACT]** 当前 reward v1.x 主要由 progress、reach、collision、当前 clearance、低高度惩罚、smoothness、z 偏差和 yaw 率惩罚组成。  
**[JUDGMENT]** 它的根本缺口不在“没有安全项”，而在“**没有前瞻性安全项**”：  
当前 clearance 只看**眼前**；goal progress 只看**眼前更近**；smoothness / yaw 惩罚反而可能压制策略提早侧移或提早偏航。于是最容易学到的是“先贴近障碍、等 risk 变很高再临时改向”的 reactive behavior，而不是 anticipatory avoidance。

**[JUDGMENT]** 从 UAV 与高速飞行文献看，这恰好触碰了真实系统的两个已知痛点。RAPTOR 用 risk-aware refinement 强调“未知障碍要更早被观察到并及时避开”，并显式规划 yaw 去观察与安全相关的空间；perception-aware planning 论文也强调，动态可行轨迹如果破坏了感知质量与 FOV，闭环执行仍可能失败。换句话说，**“当前没撞”不是合格安全代理；“未来几步是否会陷入低可见度/低 clearance/高 risk”才更接近真正需要优化的对象。** citeturn32view1turn33view1turn33view2

### 下一阶段必须回答什么

**[JUDGMENT]** 下一阶段实际上只剩三个必须回答的问题。

第一，**Reward v1.3 能否把“提前避障 onset”“dense trap escape”“support expansion”变成可学习且可验收的对象**，而不仅是新的 reward 名词。PBRS 理论告诉我们，若 shaping 完全不改变最优策略，它更适合加速已有偏好，而不是引入你现在明确追求的新偏好；因此 Reward v1.3 必须区分“保持 policy invariance 的 shaping”与“有意改变策略偏好的 task-level auxiliary objective”。citeturn29search0turn30view0

第二，**Route A 应该选“直接 fine-tune flow policy”还是“先构造 chunk critic / one-step actor 再 RL”**。从 Phase1aPolicyFM 的现状看，direct FM fine-tuning 的结构匹配度明显更高，而 176d critic 路线的理论与实现风险明显更高。citeturn4view1turn23view0turn6view0turn31view0

第三，**hierarchy 是否真的是“现在就必须加”的能力瓶颈**。RAPTOR、HDP、Fly360 都支持“模式/视角/目标层”的价值，但它们也共同说明 hierarchy 的收益通常来自“多个有效通道可选、且单层策略难以稳定完成 mode selection”的场景。对于 iDP3-UAV，先用 Reward v1.3 + non-hierarchical Route A 看是否已经能显著改善 onset、future clearance 与 dense recovery，再决定是否引入 hierarchy，能让性能归因更干净。citeturn32view1turn18view0turn34view0turn32view0

## Literature Map

### RL fine-tuning 与高维动作 critic 相关资料

| 论文/资料 | URL/arXiv | 核心方法 | 可迁移点 | 不可迁移点 | 对 iDP3-UAV 的建议 |
|---|---|---|---|---|---|
| Flow Q-Learning | arXiv:2502.02538 citeturn23view0 | 用 flow-matching policy 建模复杂动作分布，但 **RL 训练的是 one-step expressive actor**，避免对 iterative flow 递归反传。citeturn23view0 | 可迁移的是“不要把 RL 难度压在多步 flow rollout 反传上”；也可借鉴 BC / distillation anchor 的思路。 | **[JUDGMENT]** 若执行 actor 变成 one-step head，会弱化 MC-2 的“FM policy 是核心”表述；且对 4-step Phase1a 来说，速度收益没有对长-step diffusion 那么大。citeturn23view0 | **[JUDGMENT]** 可做备选 exploratory branch，但不建议作为 Route A 默认主线。 |
| Reinforcement Learning with Action Chunking | arXiv:2507.07969 citeturn7search7turn6view0 | 在 chunked action space 里直接做 RL，获得 temporally coherent exploration，并用 unbiased \(n\)-step backup 改善值传播。citeturn6view0turn7search7 | 对 long-horizon sparse reward 很有启发，尤其是“critic 要看时间结构”。 | **[FACT]** 策略要输出整个 chunk；对需要高 reactivity 的避障飞行，这是天然风险点。DQC 后续工作也专门指出这一问题。citeturn31view0 | **[JUDGMENT]** 不建议首发就上 176d chunk critic。先把 chunk 价值思想转移到 critic 设计，而不是 actor 执行接口。 |
| Decoupled Q-Chunking | arXiv:2512.10926 citeturn31view0 | critic chunk 长、policy chunk 短，通过 distilled partial-chunk critic 保留多步值传播同时避免 open-loop sub-optimality。citeturn31view0 | 直接支持“critic chunk 可以长于执行 chunk”的工程判断。 | 仍然属于 Q-learning 路线，且需要额外 distilled critic；工程复杂度高。 | **[JUDGMENT]** 若以后真的走 QC-FQL，应先采用 DQC 式 decoupling，而不是 monolithic 16-step open-loop actor。 |
| Diffusion Policy Policy Optimization | arXiv:2409.00588; ICLR 2025 citeturn4view0turn5search2 | 把 diffusion denoising 过程写成 PPO 优化对象；强调 structured、on-manifold exploration，及只微调后几步 denoising、DDIM fine-tune、噪声裁剪等 best practices。citeturn21view0turn21view1turn20view3 | 最大可迁移点是：用 **state-value / advantage baseline** 避免高维 action-Q；只调最后几步、控制噪声、保留 policy manifold。 | 论文也明确指出：on-manifold exploration 最有利于“预训练已经覆盖相关成功模式”的 fine-tuning；当需要更激进、跳出旧支持域的探索时，它可能不占优。citeturn20view0turn20view3 | **[JUDGMENT]** 适合作为 ReinFlow 的备选，而不是默认。 |
| ReinFlow | arXiv:2505.22094; NeurIPS 2025 citeturn4view1turn5search11 | 给 flow policy 注入可学习噪声，把 deterministic flow 变成 discrete-time Markov process，从而得到 exact likelihood，支持 PPO 风格在线 fine-tuning，且在 very few / one-step denoising 下仍稳定。citeturn22view0turn22view2 | 与 Phase1aPolicyFM 的**结构匹配度最高**；还能保留 flow-core，不必构造 176d action-Q。 | 主要证据来自机器人 manipulation / locomotion，而不是 UAV 避障；sample efficiency 是否足够，仍需本项目短训练 gate 验证。 | **[JUDGMENT]** Route A 默认推荐。 |
| Vlearn | arXiv:2403.04453 citeturn4view2 | 不学习显式 \(Q(s,a)\)，只学 state-value critic，并配合 weighted importance sampling、twin value nets、importance weight clipping。citeturn4view2 | 对 176d 动作特别有价值：它给出一个明确方向——**先回避 action-conditional critic**。 | 不是 flow-specific，也不是 robotics FM fine-tuning 论文；迁移需要自行改 actor loss。 | **[JUDGMENT]** 最适合作为 critic 设计原则，而非完整首选算法。 |
| T-SAC | arXiv:2503.03660; ICLR 2026 Poster citeturn4view3 | sequence-conditioned critic + aggregated \(N\)-step targets；critic 侧 chunking，而不是 actor 侧 chunking。还报告 critic 冻结若干步后可稳定训练、无需 target network。citeturn4view3 | 适合把“时间上下文”放进 critic，缓解 sparse reward / 长时 credit assignment。 | 仍是 SAC / Q-learning 家族；若 actor 仍是 176d chunk，critic 难度并不会消失。 | **[JUDGMENT]** 如果后续被迫走 critic-heavy 路线，优先借鉴 T-SAC，而不是裸 SAC。 |
| AC3 | arXiv:2508.11143; AAAI 2026 Oral citeturn4view4 | 连续 action chunk RL；actor 只从 successful trajectories 学习，critic 用 intra-chunk \(n\)-step return，并加 anchor-point intrinsic rewards。citeturn4view4 | “成功样本优先 actor 更新”与“chunk 内 anchor reward”对 dense obstacle escape 很有启发。 | manipulation 任务为主，且仍需 chunk critic。 | **[JUDGMENT]** 作为稳定化插件比作为整套 Route A 更合适。 |

### UAV dense obstacle / perception-aware 飞行相关资料

| 论文/资料 | URL/arXiv | 核心方法 | 可迁移点 | 不可迁移点 | 对 iDP3-UAV 的建议 |
|---|---|---|---|---|---|
| RAPTOR | arXiv:2007.03465 citeturn32view1 | 多拓扑 path-guided optimization + perception-aware planning + risk-aware refinement + yaw 主动观察。citeturn32view1 | 抽取到的启发非常强：**更早观察、更早规避、模式选择、yaw 与安全耦合**。 | 不能把 planner / topological path 直接接到策略后面；那会违反 MC-3 与 MC-5。 | **[JUDGMENT]** 只迁移 reward / evaluation / failure taxonomy，不迁移 planner 本体。 |
| Learning High-Speed Flight in the Wild | arXiv:2110.05113; Science Robotics 2021, DOI 10.1126/scirobotics.abg5810 citeturn33view3turn11search13 | 端到端感知到 collision-free receding-horizon trajectory，减少 pipeline latency 与误差累积。citeturn33view3 | 强烈支持“策略输出=执行轨迹”的 MC-1 方向；也支持用 trajectory-level reward 代替局部 steering reward。 | 训练依赖 privileged learning 与仿真专家；不能直接照搬其数据与训练流程。 | **[JUDGMENT]** 其最大价值是证明 end-to-end trajectory policy 在 dense clutter 高速飞行中是成立路线。 |
| Fly360 | arXiv:2603.06573 citeturn32view0 | 全景感知 + 深度中间表征 + 轻量 policy 输出 body-frame velocity，强调 movement direction 与 heading 不一致时的全空间 awareness；采用 fixed random-yaw training。citeturn32view0 | 支持“support expansion 不是只加 z，而是提升 full-spatial awareness”；也提示 yaw / heading 解耦的重要性。 | **[UNCERTAIN]** 这是较新的 arXiv 预印本，且使用的是全景输入管线，与现有点云/FM 设定不完全同构。 | **[JUDGMENT]** 可借鉴其评测思路与 random-yaw / omnidirectional taxonomy，不建议照搬感知栈。 |
| EGO-Planner | arXiv:2008.08835 citeturn33view0 | ESDF-free gradient planner，通过 guiding path 构造 collision penalty，减少只看局部障碍导致的局部最优。citeturn33view0 | 说明 dense clutter 下“局部最优 / 碰壁 / 需要 guiding signal”是真问题。 | 不能把 guiding path 作为 inference 后修正接到策略后面。 | **[JUDGMENT]** 对 Reward v1.3 的启发是：trap / dead-end / wall-hugging 必须单独定义与奖励恢复，而不是指望当前 clearance 自然解决。 |
| Perception-aware receding horizon trajectory planning for multicopters with VIO | arXiv:2204.03134 citeturn33view1 | 以 perception quality 评估候选最小 jerk 轨迹，考虑 motion blur 与 feature location；比 perception-agnostic 方法减少 VIO failure。citeturn33view1 | 直接启发：future clearance 不够，**future observability / perceptual margin** 也是未来安全的一部分。 | 依然是 planner 不是 policy；不能直接搬过来当执行层。 | **[JUDGMENT]** 可在 reward 中加入“风险窗口里的 yaw/side onset + future free-space”而不是纯 z 奖励。 |
| Perception-Aware Time-Optimal Planning for Quadrotor Waypoint Flight | arXiv:2603.04305 citeturn33view2 | 把位置不确定度、顺序 FOV 约束、look-ahead alignment 与动力学一起优化；闭环成功率从 55% 提到 100%。citeturn33view2 | 很适合作为评测指标灵感：**look-ahead alignment、future reliability、trade-off between speed and perceptual safety**。 | **[UNCERTAIN]** 预印本，且赛道/waypoint 任务与避障规划并不完全一致。 | **[JUDGMENT]** 可把 “look-ahead alignment / future clearance” 纳入 Evaluation Gates。 |

## Reward v1.3 Candidate Design Inputs

### 设计原则

**[JUDGMENT]** Reward v1.3 不应再把所有 shaping 都写成一个 reward 总和然后盲调权重，而应分成三层：

第一层是**任务主目标层**：reach、collision、goal progress，决定最终行为边界。  
第二层是**安全前瞻层**：early avoidance onset、future clearance、trap escape，决定策略是否学会“早躲、会绕、能脱困”。  
第三层是**支持域扩展层**：只在安全且有进展的条件下，奖励进入旧数据低覆盖但仍能成功的空间区域。

**[JUDGMENT]** PBRS 应只用于那些“本来就希望最优策略喜欢”的状态偏好，例如更接近 goal、处在更大 free corridor、处在更可恢复的状态；而 **early onset / support expansion / trap escape** 这三类目标都带有明显的任务再定义意味，完全 PBRS 化既不必要，也会削弱作用。PBRS 理论文献与后续分析都支持这一点。citeturn29search0turn30view0

### 候选 reward 分量

| 分量 | 目标能力 | 公式草案 | 需要 info 字段 | PBRS? | 量级建议 | 风险/副作用 | 验收指标 |
|---|---|---|---|---|---|---|---|
| early avoidance onset | 提前避障 | **[JUDGMENT]** 定义风险门： \(g_{\text{risk}}=\sigma((\tau_{\text{risk}}-\text{TTC}_t)/s_\tau)\cdot \sigma((d_{\text{risk}}-d_{\text{soft}}^H(t))/s_d)\)。再给 onset 奖励： \(r_{\text{onset}}=w_o\cdot g_{\text{risk}}\cdot \text{ReLU}(\Delta |u_{\text{lat}}|+\kappa\Delta |\dot\psi|)\cdot \text{ReLU}(\Delta d_{\text{soft}}^H)\)。其中 \(d_{\text{soft}}^H\) 是当前 FM 执行轨迹未来 \(H\) 步 clearance 的 soft-min。 | \(s_t,a_t,s_{t+1}\)，当前速度，yaw/yaw-rate，pointcloud 或 obstacle json，当前 FM 输出的未来轨迹，goal | 否 | 单步 0–0.3；单回合累积 3–8 | 开阔区蛇形、过度偏航、无意义横移 | onset distance ↑，onset time ↑，future clearance ↑，route inefficiency 不显著变差 |
| future clearance potential | 前瞻安全裕量 | **[JUDGMENT]** 两段式。**PBRS 段**：\( \Phi_{\text{free}}(s)=\text{clip}(\text{goal-cone free ray length}(s),0,C)\)，\(r_{\text{PBRS}}=\gamma \Phi(s')-\Phi(s)\)。**辅助段**：\(r_{\text{fc-aux}}=w_f\tanh((d_{\text{soft}}^H-d_{\text{ref}})/s_f)\)。soft-min 用 \(d_{\text{soft}}^H=-(1/\beta)\log\sum_k \omega_k e^{-\beta d_k}\)。 | pointcloud / obstacle json，goal direction，未来 \(H\) 步执行轨迹，当前/下一状态 | 混合。state-only 部分是；action-conditioned 部分否 | PBRS 段单步约 ±0.1–0.4；aux 段单回合 4–10 | 若只保留 aux，可能变成“躲得很开但不前进”；若只保留 PBRS，可能前瞻不足 | future clearance ↑，min clearance ↑，BC 相同 SR 下 CR ↓ |
| dense obstacle recovery / trap escape | 脱困、恢复、模式选择 | **[JUDGMENT]** 先定义 trap：在窗口 \(W\) 内 goal progress \(<\epsilon_p\)、窗口内 min clearance \(<d_{\text{trap}}\)、heading / lateral sign flips \(>N_{\text{flip}}\)。给持续 stall 惩罚 \(r_{\text{stall}}=-w_s\mathbf{1}[\text{trap}]\)。当 trap 解除且 \(d_{\text{soft}}^H\) 提升、窗口 progress 恢复时给一次性 \(r_{\text{escape}}=+w_e\)。 | 最近 \(W\) 步 progress、clearance、yaw / lateral sign、未来 clearance | 否 | stall 单步 -0.05~-0.2；escape 一次 +2~+5 | trap farming，故意进陷阱再出来刷分 | trap recovery rate ↑，dead-end dwell time ↓，dense SR ↑ |
| side-commitment / anti-flip | 密障中的绕行侧选择 | **[JUDGMENT]** 当检测到 goal-line 被障碍簇阻塞且左右/上下存在可行分叉时，记录当前绕行符号 \(m_t\in\{-1,+1\}\)。在 clearance 未恢复前，如频繁 \(m_t\) 翻转，则给 \(r_{\text{flip}}=-w_{\text{flip}}\)。这不是鼓励固定走某一侧，而是鼓励**一旦进入局部绕行模式就别反复犹豫**。 | obstacle json 或 pointcloud clustering，goal-line blocking 检测，lateral sign / z sign | 否 | 单次 flip -0.2~-1.0 | 过早承诺到错误侧；需与 trap escape 联动 | side-flip count ↓，trap dwell ↓，dense SR / CR 改善 |
| support expansion | 扩大 x/y/z 支持域，不乱飞 | **[JUDGMENT]** 用离线数据估计低维状态密度 \(p_D(c)\)，其中 cell \(c\) 取 goal-aligned 相对坐标系中的 \((x,y,z)\) bin。对低密度格给 novelty： \(n_t=\mathbf{1}[p_D(c_t)<\tau]/\sqrt{N(c_t)+1}\)。再施加门控： \(r_{\text{sup}}=w_{\text{sup}}n_t\mathbf{1}[d_{\text{soft}}^H>d_{\text{safe}}]\mathbf{1}[\Delta_W \text{progress}>\epsilon]\)。可再加 success-only episode bonus，奖励成功轨迹覆盖到的新低密度格数，上限封顶。 | 离线 occupancy histogram / kNN density，当前 rel xyz，未来 clearance，窗口 progress，成功标志 | 否 | 单步 0–0.15；每回合总额上限 3–6 | 为刷 novelty 而游走，或只学升高不学横向通行 | successful low-density coverage ↑，out-of-support success ↑，OOD crash rate 不升 |
| efficiency guard | 防 reward hacking / 无意义绕远 | **[JUDGMENT]** 在低风险区加 detour penalty： \(r_{\text{eff}}=-w_{\text{eff}}\mathbf{1}[g_{\text{risk}}<\rho]\max(0, |u_{\text{lat}}|+\kappa|\dot\psi|-\eta)\)。此外对 path-length ratio、looping、过度 side-flip 做 episode penalty。 | 当前 risk gate，yaw/yaw-rate，lateral control，累计路径长度 | 可做 state-action 惩罚，非 PBRS | 单步 -0.02~-0.1；episode -0~-3 | 过度抑制真实必要绕行 | path inefficiency 受控；onset 改善不靠刷 lateral motion |

### Reward scale 与防 hack 建议

**[JUDGMENT]** 量级上不要让新 dense reward 的总和接近 `r_reach=+100` 或 `r_collision=-50`；否则策略会学会“用过程分覆盖终局错”。更稳妥的经验配平是：

- progress + reach 仍是主信号，成功回合累计通常应贡献 **+20 到 +120**；
- collision / severe failure 仍是主负信号，失败回合通常应拉到 **-20 到 -60**；
- onset / future clearance / trap escape / support expansion 的单回合总贡献应控制在 **+5 到 +20** 区间；
- 任何 novelty / escape bonus 都必须**门控、封顶、带迟滞**，避免刷分循环。  
这是因为 PBRS effectiveness 还受外部 reward 与初始 value 标度影响，不配平只会让 shaping 无效或误导。citeturn30view0

**[JUDGMENT]** 还应做三条硬防线。  
其一，**success-conditioned cap**：support expansion 的高权重 bonus 最好在 episode success 时再结算一部分。  
其二，**one-shot escape bonus**：同一 trap segment 只能领一次 escape bonus。  
其三，**low-risk detour penalty**：在 TTC 充足、future clearance 充足时，对高 lateral / yaw 行为反向约束。  
这样可以把“更早躲”与“到处乱躲”明确区分开来。TTC-force / expected collision time 文献的经验也说明，风险代理必须和 travel-time / efficiency trade-off 联合设计。citeturn27search0turn27search3

## Route A and Hierarchical Steering Candidate Inputs

### Route A candidate architecture inputs

**[JUDGMENT]** 对 iDP3-UAV，Route A 的真正选择标准不是“哪篇论文最新”，而是三件事同时满足：

- 是否保留 **FM actor 作为执行核心**；
- 是否避免把学习成败过度押在 **176d action-Q critic** 上；
- 是否能在 **frozen data support 不足** 的情况下，靠 Reward v1.3 学到新能力，而不是只在旧 manifold 内更平滑地重放旧行为。

基于这个标准，我的排序如下。

| 路线 | 结构匹配度 | 主要优点 | 主要风险 | 对 176d critic 的态度 | 结论 |
|---|---|---|---|---|---|
| **ReinFlow-style direct FM fine-tuning** | **高**。直接面向 flow matching policy。citeturn22view0turn22view2 | exact likelihood、few-step / one-step 仍可 fine-tune、保留 FM 核心、可用 PPO/clipped surrogate，不必先学 monolithic chunk-Q。citeturn22view0turn22view2 | 机器人 manipulation / locomotion 证据多于 UAV；sample efficiency 仍需本地 gate。 | **回避**显式 176d Q，优先 state-value / advantage 路线。 | **[JUDGMENT] 默认推荐** |
| **DPPO-style policy gradient fine-tuning** | 中。不是为 FM 设计，但可迁移 policy-gradient best practices。citeturn21view0turn21view1 | on-manifold exploration、只调后几步、state-value baseline、训练稳定性强。citeturn20view0turn21view0 | 论文自己强调它最适合 pretraining 已有相关 mode coverage 的 fine-tuning；对 support expansion 的突破力可能不足。citeturn20view0turn20view3 | **回避**高维 action-Q。 | **[JUDGMENT] 备选路线** |
| **FQL** | 中。flow 相关，但执行逻辑偏 one-step actor。citeturn23view0 | 避免 iterative flow rollout 反传；测试时更快。citeturn23view0 | 对 Phase1a 这种已是 4-step 的 FM actor，速度收益相对有限； actor 形式变化会削弱 MC-2 的“flow core”纯度。 | 取决于 actor / critic 设计，但通常仍要面对 chunk-valued critic 问题。 | **[JUDGMENT] 不作默认，保留为 exploratory branch** |
| **QC-FQL / QC-style critic first** | 低。与当前 UAV reactive avoidance 冲突更大。citeturn6view0turn31view0 | multi-step value propagation、temporally coherent exploration。citeturn6view0 | actor 输出整 chunk 的 open-loop / reactivity 风险，chunk 长度越大越难学；176d critic 尤其危险。citeturn31view0turn4view2 | **正面拥抱**高维 chunk-Q，但这正是最大风险。 | **[JUDGMENT] 第一阶段不推荐** |

**[JUDGMENT]** 因此，Route A 的默认技术草案应是：

- **Actor**：仍然是 Phase1aPolicyFM，本体不换。
- **RL 优化器**：ReinFlow 风格的 flow-policy 在线 fine-tuning；若实现阻塞，则退到 DPPO 风格 policy gradient fine-tuning。
- **Critic / baseline**：优先 state-value / advantage baseline，而不是高维 action-Q。
- **Regularization**：保留 offline BC / FM anchor 作为安全绳，但它应是**稳定化辅助手段**，不是像 Route B 一样把主能力增益寄托在 frozen latent steering 上。  
这一点与 Vlearn 对高维动作 critic 的回避、以及 DPPO 对 value-estimator 只依赖 state 的经验是同向的。citeturn4view2turn21view0

### action chunk critic stabilization

**[JUDGMENT]** 如果团队最终还是想保留一个 critic-heavy 备选分支，我建议只采用下面这些“受限版原则”，不要直接做 176d monolithic chunk critic：

- **critic chunk 长于执行 chunk，但执行必须 closed-loop**。这类思想由 DQC 明确支持。对 iDP3-UAV，执行 chunk 建议先保持 1–2 step，critic context 可试 4–8 step，而不是一步到位 16 step。citeturn31view0
- **critic 建模轨迹上下文，而非只看单一 state-action 对**。这是 T-SAC 的核心启发。citeturn4view3
- **actor 更新更保守，最好偏成功轨迹或高优势轨迹**。AC3 的 asymmetric actor update 给了一个有力提示。citeturn4view4
- **必要时优先尝试 value-only critics**。Vlearn 的整篇论文其实就是在告诉你：当动作太高维时，先别执着于 \(Q(s,a)\)。citeturn4view2

**[JUDGMENT]** 换成工程语言就是：  
如果你们选择 Route A 默认主线为 ReinFlow，那么 chunk critic stabilization 的正确姿势不是“再做一个平行的 176d critic 作为主干”，而是把这些成果转化成**次级 ablation 分支**与**后备机制**。尽量不要让第一阶段设计文档把主赌注押到“Q 是否终于能在 176d 上学好”。

### Hierarchical steering candidate inputs

**[JUDGMENT]** hierarchy 在 iDP3-UAV 的价值，主要不在“让轨迹更平滑”，而在**dense clutter 中的 topological mode selection**：左绕还是右绕、继续贴近还是先横移脱困、是否需要短暂爬升或下降重获 corridor。RAPTOR 的多拓扑候选与主动 yaw 观察，本质上就在说明“密障问题常常不是微分几何问题，而是模式选择问题”。citeturn32view1

| 方案 | 上层输出 | 下层执行 | 优点 | 主要风险 | MC-1~MC-5 适配性 | 短训练建议 |
|---|---|---|---|---|---|---|
| **discrete mode / corridor selection + FM actor** | 离散 token，例如 `{center, left, right, up, down, recover}`，或更保守的 `{left/right, vertical band, escape mode}` | Phase1aPolicyFM 仍输出最终执行轨迹 | 可解释性最强；最容易做 paired ablation；适合 dense clutter 的模式选择 | token 抖动、模式塌缩；需要 anti-flip 约束 | **最高**。上层只做内部 conditioning，不改写最终轨迹。 | **[JUDGMENT] 首个 hierarchical 验证分支** |
| **latent option / skill embedding + FM actor** | 连续 latent \(z\) 或低维 option embedding，每 \(K\) 步更新一次 | FM actor 条件生成最终轨迹 | 更柔性；参数化紧凑；与 skill-prior / latent-policy 文献更一致。SPiRL 证明了 skill embedding + prior 能帮助复杂导航与操控。citeturn18view2 | 可解释性差；option collapse；归因不如离散 token 干净 | **中高**。只要 latent 只是内部条件而不是后处理，原则上可通过。 | **[JUDGMENT] 第二候选** |
| **residual trajectory actor** | 上层/旁路输出 residual，和 base FM 轨迹在策略内部相加后再执行 | 合成后的轨迹直接执行 | 修正能力最强；对已有 BC 轨迹“补一点”很诱人。Residual Policy Learning 也证明了残差能改进已有控制器。citeturn19view0 | 最容易在精神上滑向“内部 post-hoc correction”；归因最差；若 residual 太强，会把 base actor 变成壳 | **技术上可过 MC-1，精神上最接近冲线** | **[JUDGMENT] 不应作为 first validation** |

**[JUDGMENT]** 我更推荐先做一个**很克制的 discrete mode 版本**。  
不是上来做“几何 corridor planner”，而是只做一个内部分类器，输出少量 mode token，再让下层 FM actor 在 token 条件下生成完整执行轨迹。这样做有四个好处：

- 可以直接测 **mode entropy、mode flip rate、各 mode 的 success / collision profile**；
- 与 reward 设计天然耦合，比如 anti-flip、trap escape、future clearance；
- 下层仍是 Phase1aPolicyFM，MC-2 更干净；
- 如果无效，结论也更明确：不是 hierarchy 本身有效，而是这个 mode vocabulary 不够。  

HDP 的高层—低层结构、以及另一篇 contact-guided HDP 中“高层 contact / 低层 diffusion trajectory” 的设计，都支持这种“上层只做稀疏条件，下层做真正轨迹生成”的结构。citeturn18view0turn34view0turn18view1

## Evaluation Gates

### 指标定义

| 指标 | 定义建议 | 备注 |
|---|---|---|
| SR | success rate | 保持与当前 Support / Default / Dense 评估协议一致 |
| CR | collision rate | 与 SR 同时看，避免“多试多撞” |
| reward | episode return 及分量分解 | 必须分解到各 reward 子项，防止 reward hacking |
| min clearance | 真实执行轨迹最小障碍间隙 | 不能只看预测值 |
| onset distance | 第一次满足“risk gate 打开且 lateral/yaw onset 超阈值并提升 future clearance”时，到相关障碍的距离 | 直接验收“更早开始躲” |
| onset time | 从 onset 到进入近障壳层或 TTC 低于阈值的时间差 | 比单纯距离更稳健 |
| future clearance | 当前执行 chunk 未来 \(H\) 步 clearance 的 soft-min 或分位数 | 核心前瞻指标 |
| trap recovery | 触发 trap 后，在 \(N\) 步内恢复 progress 且 clearance 回升的比例 | 验收 dense obstacle 脱困 |
| out-of-support rate | 处于 offline 低密度 state cell 的时间占比 | 必须与 success / crash 联合看 |
| successful low-density coverage | 成功轨迹中访问到的低密度 cell 数 / 体积 | 支持域扩张要看这个，不要只看 OSR |
| side-flip count | 单次障碍交互中左右/上下模式切换次数 | 验收 hierarchy 与 anti-flip reward |

**[JUDGMENT]** onset 指标务必采用**风险条件化定义**，而不是只要 yaw_rate 上来就算 onset。因为在 open space 的大 yaw 不是“提前避障”，只是抖动。TTC / expected collision time shaping 文献与 foresight navigation 文献都支持先定义 imminent risk，再奖励更早规避。citeturn27search0turn27search3turn14search6

### 短训练门禁

| 门禁阶段 | 数据与场景 | 通过条件 | 失败即结论 |
|---|---|---|---|
| **稳定性门** | 先跑 canonical route `start=(-8,0,2), goal=(8,0,2)`，再跑 support/default 各 20–50 episode 的短集 | 无 NaN/Inf；invalid_obs_rate=0；reward 分量可解释；SR 不低于 paired BC 超过 5 个百分点；未来 clearance 与 onset 指标可稳定计算 | 若过不了，先修实现 / reward 计算，不进入能力讨论 |
| **能力信号门** | canonical paired evaluation + random start/goal stress test，按 support/default/dense 分组 | 至少满足二选一：① canonical SR 超过 BC；或 ② canonical SR 持平但 onset time 提升 ≥20%、future clearance 提升 ≥10%、CR 下降。support 不允许明显退化（建议不低于 BC-2pp） | 若只有 reward 上升、而 onset / clearance / CR 不改善，视为 reward hack |
| **推广门** | random start/goal，三组世界各 100+ episode，固定种子与 paired seeds | default 至少出现小幅正迁移（建议 SR +2~3pp 或 CR -3~5pp）；dense 至少一项核心指标显著改善（trap recovery / future clearance / CR）；successful low-density coverage 增加，且 OOD crash rate 不增加超过 2pp | 若只在 support 变好或只在 reward 变高，不能升为主线 |
| **分支升级门** | 对非层级主线过门后，再做 hierarchical 短训练 | hierarchical 必须在 **不牺牲 support / canonical** 的前提下，显著降低 side-flip 或提升 dense trap recovery；否则保留为后备 | 若 hierarchy 只抬高复杂度不带来 dense 场景净增益，则暂缓 |

**[JUDGMENT]** 这里最关键的不是具体百分点，而是**门禁逻辑**：  
第一，看 paired BC，不看绝对 reward；  
第二，看能力目标指标，不看单一 success；  
第三，看 dense / OOD 受益是否以 support 回退为代价。  
这与 DPPO、ReinFlow、Q-chunking 系列都强调的“benchmark 内不同任务模式差异很大、不能只看一个平均 reward”完全一致。citeturn20view2turn22view1turn6view0

## Recommended Next Design Order and MC Compliance

### Recommended Next Design Order

**一，是否先写 Reward v1.3 设计文档？**  
**[JUDGMENT] 是，必须先写。**  
原因很简单：你们当前要突破的三类能力缺口——提前避障、support 扩张、dense 脱困——都首先是**credit assignment 问题**。如果 Reward v1.3 没把这些能力映射成可训练、可验收的信号，那么无论 Route A 是 ReinFlow 还是 DPPO，都只是在用更复杂的 RL 去拟合旧 reward。PBRS 与 reward shaping 文献也明确表明，shaping 的有效性依赖于外部 reward 与 value 初始化的配平，因此 reward 规范应先于 optimizer 规范。citeturn30view0turn29search0

**二，Route A 默认应选哪条？**  
**[JUDGMENT] 默认选 ReinFlow-style direct FM online fine-tuning。**  
备选是 DPPO-style policy gradient fine-tuning。  
不建议第一阶段默认 QC-FQL / 176d critic，也不建议把 FQL 作为主线执行 actor。原因分别是：  
ReinFlow 与当前 FM actor 的结构最贴合；DPPO 的 best practice 可作为 backup；QC-FQL 首发风险太高；FQL 会改变执行策略形态并削弱 MC-2 / attribution clarity。citeturn22view0turn22view2turn20view0turn21view0turn31view0turn23view0

**三，hierarchical 是否立即进入，还是作为 Route A 后的分支？**  
**[JUDGMENT] 作为 Route A 后的分支。**  
建议现在就把 hierarchical interface 写进设计文档，但实现优先级放在 non-hierarchical Route A 之后。  
只有当 Reward v1.3 + direct FM fine-tuning 已经能带来明显的 onset / clearance 提升，但 dense world 仍持续出现 side-flip、trap dwell、模式选择错误时，再把 discrete mode / corridor hierarchy 拉成下一主分支。否则 hierarchy 会和 reward / optimizer 同时变化，导致 MC-5 的归因难以分离。RAPTOR 与 HDP 都说明 hierarchy 的价值很真实，但也说明它更像“第二层解题器”，不是第一层基础训练信号的替代品。citeturn32view1turn18view0turn34view0turn18view1

### MC Compliance Check

| 约束 | 检查结果 | 说明 |
|---|---|---|
| MC-1 策略输出 = 执行轨迹 | **[JUDGMENT] 可满足** | Reward v1.3 不改执行接口；ReinFlow / DPPO 路线都仍由 FM actor 输出最终执行轨迹；hierarchical 只提供内部 conditioning。 |
| MC-2 diffusion / flow matching policy 是核心 | **[JUDGMENT] 默认推荐方案满足** | ReinFlow-style Route A 完全保留 flow core。FQL 若把执行端换成 one-step 头，则这条约束会变弱，因此不作默认。citeturn23view0turn22view0 |
| MC-3 安全约束通过训练 loss / RL reward / 策略内 guidance 学习，不做 inference 后修剪 | **[JUDGMENT] 满足** | 本报告所有建议都把安全放进 reward、policy gradient、或内部 mode conditioning；明确不建议 post-hoc projection / smoothing / external planner rewrite。 |
| MC-4 EGO 数据 frozen，不重采集 | **[JUDGMENT] 满足** | 所有方案均建立在 frozen offline data + 现有 RL 交互框架之上，不建议重采集。 |
| MC-5 性能归因必须可分离 | **[JUDGMENT] 只要按推荐顺序推进即可满足** | 先 Reward v1.3，再 non-hierarchical Route A，再 hierarchy 分支；每一步都做 paired BC / paired seeds / ablation，避免“奖励、架构、后处理一起改”的混合归因。 |

## References

- Andrew Y. Ng, Daishi Harada, Stuart J. Russell. *Policy Invariance Under Reward Transformations: Theory and Application to Reward Shaping*. ICML 1999. citeturn29search0  
- Henrik Müller, Daniel Kudenko. *Improving the Effectiveness of Potential-Based Reward Shaping in Reinforcement Learning*. 2025. citeturn30view0  
- Seohong Park, Qiyang Li, Sergey Levine. *Flow Q-Learning*. ICML 2025, arXiv:2502.02538. citeturn23view0  
- Qiyang Li, Zhiyuan Zhou, Sergey Levine. *Reinforcement Learning with Action Chunking*. NeurIPS 2025, arXiv:2507.07969. citeturn6view0turn7search7  
- Qiyang Li, Seohong Park, Sergey Levine. *Decoupled Q-Chunking*. arXiv:2512.10926. citeturn31view0  
- Allen Z. Ren et al. *Diffusion Policy Policy Optimization*. ICLR 2025, arXiv:2409.00588. citeturn4view0turn21view0  
- Tonghe Zhang et al. *ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning*. arXiv:2505.22094. citeturn4view1turn22view2  
- Fabian Otto et al. *Efficient Off-Policy Learning for High-Dimensional Action Spaces*. arXiv:2403.04453. citeturn4view2  
- Dong Tian, Onur Celik, Gerhard Neumann. *Chunking the Critic: A Transformer-based Soft Actor-Critic with N-Step Returns*. ICLR 2026 Poster, arXiv:2503.03660. citeturn4view3  
- Jiarui Yang et al. *Actor-Critic for Continuous Action Chunks*. AAAI 2026 Oral, arXiv:2508.11143. citeturn4view4  
- Boyu Zhou et al. *RAPTOR: Robust and Perception-aware Trajectory Replanning for Quadrotor Fast Flight*. arXiv:2007.03465. citeturn32view1  
- Antonio Loquercio et al. *Learning High-Speed Flight in the Wild*. Science Robotics 2021, DOI 10.1126/scirobotics.abg5810, arXiv:2110.05113. citeturn33view3turn11search13  
- Xiangkai Zhang et al. *Fly360: Omnidirectional Obstacle Avoidance within Drone View*. arXiv:2603.06573. citeturn32view0  
- Xin Zhou et al. *EGO-Planner: An ESDF-free Gradient-based Local Planner for Quadrotors*. arXiv:2008.08835. citeturn33view0  
- Xiangyu Wu et al. *Perception-aware receding horizon trajectory planning for multicopters with visual-inertial odometry*. arXiv:2204.03134. citeturn33view1  
- Chao Qin et al. *Perception-Aware Time-Optimal Planning for Quadrotor Waypoint Flight*. arXiv:2603.04305. citeturn33view2  
- Ruihua Han et al. *Reinforcement Learned Distributed Multi-Robot Navigation with Reciprocal Velocity Obstacle Shaped Rewards*. arXiv:2203.10229. citeturn27search0  
- Jinlin Chen et al. *Mitigating Imminent Collision for Multi-robot Navigation: A TTC-force Reward Shaping Approach*. AAMAS 2023. citeturn27search3  
- Foresight Social-Aware Reinforcement Learning for Robot Navigation. arXiv HTML 2021. citeturn14search6  
- Xiao Ma et al. *Hierarchical Diffusion Policy for Kinematics-Aware Multi-Task Robotic Manipulation*. CVPR 2024. citeturn18view0turn34view0  
- Dexin Wang et al. *Hierarchical Diffusion Policy: manipulation trajectory generation via contact guidance*. arXiv:2411.12982. citeturn18view1  
- Karl Pertsch et al. *Accelerating Reinforcement Learning with Learned Skill Priors*. CoRL 2020, arXiv:2010.11944. citeturn18view2  
- Tom Silver et al. *Residual Policy Learning*. arXiv:1812.06298. citeturn19view0