# DPPO、FM+ReinFlow 与 FM+Flow-GRPO 论文路线双向钢人研究

| 字段 | 内容 |
|------|------|
| 文档类型 | 联网研究报告 / 决策前双向钢人论证底稿 |
| 日期 | 2026-08-29 |
| 版本 | v1.1 |
| 状态 | 已完成 WSL 代码核查与官方实现复用裁决；等待后续设计立项 |
| 检索日期 | 2026-08-29 |
| 本地前置证据 | `jindu/RouteA_DDPM_RL_Gate3_Current_Status_20260827.md`；`jindu/RouteA_DDPM_RL_FormalTraining_Windows_Staging_20260829.md`；`jindu/2026-08-22-paper-algorithm-novelty-audit-current-status.md`；`jindu/2026-08-22-paper-pivot-ddpm-to-fm-handoff.md` |
| 核心外部论文 | Liu et al., AEJ 2026, DOI:10.1016/j.aej.2026.02.024；DPPO, arXiv:2409.00588；ReinFlow, arXiv:2505.22094；Flow-GRPO, arXiv:2505.05470；πRL, arXiv:2510.25889；Flow Policy Gradients for Robot Control, arXiv:2602.02481 |

## 0. 文档定位与证据边界

[JUDGMENT] 本报告不提前决定 DDPM+DPPO、FM+ReinFlow 或 FM+Flow-GRPO 哪条路线应成为论文主线。它只完成四件事：核准术语与当前证据；比较与 Alexandria 论文的真实重合；对三条路线做最强支持与最强反对论证；识别能改变结论的关键变量。

[FACT] 用户本轮明确纠正算法名为 **DPPO（Diffusion Policy Policy Optimization）**，不是图像生成领域的 DDPO（Denoising Diffusion Policy Optimization）。后文统一使用 DPPO。

[FACT] 用户本轮告知“DPPO 训练系统已搭建完成且正式训练已开始”。本地最新状态文档仍停留在 `WINDOWS_STAGED_WSL_VERIFICATION_PENDING`，并写明 WSL targeted pytest、真实 build 与正式 seed 尚待执行：`jindu/RouteA_DDPM_RL_FormalTraining_Windows_Staging_20260829.md:3-16`。

[UNCERTAIN] 因此当前最合理口径是：用户的实时状态更新晚于本地 staging 文档；正式训练“已启动”可作为用户提供的新事实，但在取得 WSL 命令、输出目录、首批 `metrics_update_*` 或 checkpoint 前，本报告不把它升级为已核验运行事实，也不声称已有正向 RL 收益。

[FACT] 2026-08-22 的既有审计已经裁决：宽泛的“DDPM/FM 用于 UAV 避障”“原始点云到 UAV 轨迹”“FM+body-frame+UAV 实时轨迹”均已有邻近工作；现有系统有条件支撑应用型期刊，但不足以只靠算法名称支撑强方法型期刊：`论文/研究报告/2026-08-22_期刊算法理论新颖性与可投稿性审计.md:12-16,170-177,434-442`。

## 1. 真正要解决的问题

[JUDGMENT] 真问题不是“怎样换一个与 Liu et al. 不同的模型或 RL 缩写”，也不是“怎样降低文字查重率”。真问题是：

> 在已经投入大量工程成本并进入 DDPM-DPPO 正式训练的前提下，选择一条既有较高概率产生可复现正向 RL 收益、又能形成足够清晰论文贡献、还能为后续学位论文保留扩展空间的研究主线；同时避免为了形式差异推翻已验证资产，或为了短期可行性留下方法贡献过弱、与 2026 年 UAV diffusion+GRPO 工作过度重合的问题。

[JUDGMENT] 这个问题同时包含四个不同目标，不能只优化其中一个：

1. **能力目标**：RL 必须真正改善提前避障、x/y/z full-space support 和密集障碍脱困，而不是只有 reward、KL 或 loss 更好看。
2. **工程目标**：首条路线应最大化利用已经通过 parity、update、resume、audit 的 DPPO 系统，减少重新引入概率核心、rollout 和训练日程漏洞。
3. **论文目标**：贡献要能被写成独立、可归因、可消融的科学命题；“换成 FM”或“换成 GRPO”本身都不是原创算法。
4. **学位目标**：期刊路线不能耗尽全部研究空间，最好为后续 FM-RL、group-relative credit、真实 PX4/Gazebo/实物迁移保留自然升级路径。

## 2. Alexandria 论文的真实方法链与重合边界

### 2.1 论文事实

[FACT] 目标论文为 Yuyue Liu et al., *Enhancing UAV path planning with diffusion models and group relative policy optimization*, Alexandria Engineering Journal 140 (2026) 33–46，DOI `10.1016/j.aej.2026.02.024`，2026-02-25 在线发表。本地归档：`论文/被参考/Liu_2026_GRPO-MDP_Alexandria_Engineering_Journal.pdf`。

[FACT] 它不是单一“DDPM+GRPO”，而是以下组合：

| 维度 | Liu et al. 2026 |
|------|------------------|
| 观测 | UAV ego state、相对目标、最多 100 个障碍物的相对位置/相对速度、历史 state-action Transformer |
| 动作 | 单步 3D body-axis acceleration，范围 $[-3,3]^3$ |
| 生成策略 | DDPM，训练 20 diffusion steps、DDIM 推理 10 steps，每状态 8 个 action candidates |
| RL | critic-free GRPO；按初始状态与目标相似度聚类，组内 trajectory-return Z-score |
| 稀疏奖励 | virtual-target hindsight relabeling + collision safe-boundary Gaussian penalty |
| 安全 | 训练期 soft CBF penalty + 执行期 QP 计算最近安全动作 |
| 仿真 | AirSim 1.8.1；Easy/Medium/Hard；训练每难度 1000 scenes，测试每难度 500 scenes |
| 训练预算 | 5000 rounds × 2048 environment steps，约 1024 万 environment steps；32 parallel envs |
| 主结果 | Hard SR 91.2%、CR 8.8%；Medium SR 94.8%、CR 5.2%；均为论文报告值 |

[FACT] 论文自己的状态定义已经包含相对目标 $p_{goal}-p_t$、相对障碍位置 $p_{o,i}-p_t$ 和相对障碍速度 $v_{o,i}-v_t$。因此，“强调以自我为中心的表示”若只指相对坐标表达，并不是与该论文的充分差异点。

[FACT] 该论文 Eq. (26) 明确在策略动作违反 CBF 时通过 QP 得到 $a_{safe}$，算法 1 也在执行前替换动作。论文把它描述为嵌入训练的安全过滤，但从本项目 MC 判据看，它仍然在执行时修改策略输出。

[JUDGMENT] 因而 CBF/QP 是双方最清楚的结构差异之一：本项目坚持“策略输出=执行轨迹”，只能借鉴训练期 reward/credit 思想，不能复制执行期安全滤波，否则违反 MC-1、MC-3、MC-5。

### 2.2 与 iDP3-UAV 的重合和差异

| 维度 | 重合 | 可形成真实差异的部分 |
|------|------|----------------------|
| 任务 | 都是 3D UAV 避障/到达 | 本项目的三类能力目标、失败恢复和 full-space support 更明确 |
| 生成模型 | 都可使用 DDPM/DDIM | 本项目是 iDP3 式原始局部点云与 11d 多步 action chunk，不是单步 3d acceleration |
| 表示 | 都有 egocentric/relative information | 本项目 body-frame 旋转不变量、原始合成/传感点云、冻结 EGO 数据与多步轨迹语义 |
| RL | 都是 diffusion policy post-training | DPPO 使用 critic/GAE/PPO；该文用组内 return GRPO、聚类与 relabeling |
| 安全 | 都在训练信号中考虑 collision/safety | 本项目禁止执行期 QP/CBF 改写，要求策略内安全学习与可分离归因 |
| 验证 | 都需仿真闭环 | 本项目目标是 PX4/Gazebo+MAVROS+px4ctrl，并最终实物；该文为 AirSim |

[JUDGMENT] 单独使用“egocentric”作为论文主创新偏弱；若走 DDPM+DPPO，必须把差异组织成完整受限问题：**原始局部点云 + body-frame 不变量 + 11d 可执行轨迹块 + 无策略外修正 + 三类能力导向 RL + PX4/Gazebo 闭环**。这更接近应用型/系统型贡献，而不是新基础算法。

## 3. 相关算法与 2025–2026 一手进展

### 3.1 DPPO

[FACT] DPPO（ICLR 2025，arXiv:2409.00588）把 diffusion denoising chain 建模为可计算 transition likelihood 的策略，并用 PPO fine-tune 预训练 diffusion robot policy；官方覆盖 Gym、D3IL、Robomimic、Furniture-Bench，支持 DDPM/DDIM 与 action chunk。

[FACT] 本项目 clean rebuild 已固定 official DPPO 数学核心，并完成 E5 native/official DDIM parity、真实 one-update、cold-resume 与 Pilot10；但这些只证明训练链路，不证明 RL 正收益：`jindu/RouteA_DDPM_RL_CleanRebuild_to_Gate3_Full_Handoff_20260828.md:343-356,402-455`。

### 3.2 ReinFlow

[FACT] ReinFlow（NeurIPS 2025，arXiv:2505.22094v7）面向连续机器人控制，向 deterministic flow path 注入可学习噪声，使每个离散 flow transition 成为 Gaussian Markov transition，联合路径 likelihood 可计算，再使用 PPO/critic/GAE fine-tune flow policy。

[FACT] ReinFlow 报告 Rectified Flow locomotion episode reward 平均净增 135.36%，Shortcut manipulation success 平均净增 40.34%；覆盖状态/视觉、长时域和稀疏奖励，并支持 4 步甚至 1 步。它的官方代码直接继承 DPPO 基础设施。

[JUDGMENT] 这使 ReinFlow 成为从现有 DDPM-DPPO 迁移到 4-step FM 时最直接的一手机器人参照，但它仍依赖 critic，不能自动消除本项目历史上的 critic/replay/训练日程风险。

### 3.3 Flow-GRPO

[FACT] 用户所称“flow-grop”应为 **Flow-GRPO**（NeurIPS 2025，arXiv:2505.05470v5）。原论文先把 deterministic Flow-ODE 转为匹配各时刻边际分布的 SDE，再用 Euler-Maruyama 得到可计算 Gaussian transition，最后使用 group-relative advantage、clipped ratio 与 KL 优化。

[FACT] 原 Flow-GRPO 的官方实验全是文本到图像：SD3.5-M GenEval 63%→95%，OCR 59%→92%；它没有机器人环境、UAV、三维点云、轨迹执行或 PX4/Gazebo 证据。

[FACT] 原论文 Denoising Reduction 把训练采样从 40 步降到 10 步而保留 40 步推理。对本项目固定 4-step Euler，这一主要加速贡献几乎不能直接迁移；若再降到 1–2 步，则需要重新证明有限步 SDE 离散误差和训练/部署一致性。

[FACT] 本次已归档官方 PDF 与 README：`论文/被参考/Flow_GRPO_official_20260829/`。

### 3.4 机器人 Flow-RL 的后续进展

[FACT] πRL（arXiv:2510.25889v3）已经把两类数学都用于 flow-based VLA：Flow-Noise 对应 learnable-noise/exact path likelihood，Flow-SDE 对应 ODE-to-SDE，并支持 PPO 与 GRPO。其摘要明确把 agent-environment interaction 与 denoising 组织为 two-layer MDP。

[FACT] RLinf 官方结果中，π0 在 LIBERO 上由 SFT 57.6% 提升到 GRPO 90.0%、PPO 96.0%；π0.5 由 77.1% 提升到 GRPO 91.5%、PPO 97.9%。因此，GRPO 已证明可迁移到机器人 flow policy，但同一公开对比中 PPO 的最终表现更高。

[FACT] Pfrommer et al.（arXiv:2507.15073）提出 reward-weighted flow matching 和带 learned reward surrogate 的 GRPO，在二维 unicycle 任务上相对 imitation flow policy 降低 50%–85% cost。该证据说明 group-relative flow optimization 可学出示范外行为，但任务规模、感知维度和闭环复杂度远低于 UAV。

[FACT] *Flow Policy Gradients for Robot Control*（arXiv:2602.02481）进一步表明 flow policy gradient 已覆盖 locomotion、humanoid tracking、manipulation 和两种 humanoid sim-to-real；它绕开 likelihood 的方式又不同于 ReinFlow/Flow-GRPO。

[JUDGMENT] 这些 2025–2026 进展改变了论文 novelty 边界：现在不能声称“首个 flow-policy online RL”“首个 flow robot GRPO”或“首个 ODE-to-SDE flow-policy RL”。潜在空白只能更窄地表述为 UAV 原始点云、11d 轨迹块、三类能力导向 credit、无策略外修正及 PX4/Gazebo/实物证据的组合；限定检索未发现完全相同工作，但不能承诺全球绝对首个。

### 3.5 UAV 生成式导航的最新压力

[FACT] FlowPilot（arXiv:2608.00635）已用 flow matching 联合预测未来 depth 与 UAV trajectory，并用 Bernstein 控制点保证 $C^2$ 可执行轨迹；其报告 Jetson Orin NX 端到端低于 18 ms、实物 5.5 m/s。这使“FM+body frame+UAV 实时轨迹”不能再作为宽泛首创。

[FACT] X-NavDP（arXiv:2607.28560）用 Group Q-score Reweighted Matching 做 navigation diffusion policy 后训练，专门针对 dead-end recovery、long-obstacle detour、dense-scene detouring 与跨 embodiment；报告 simulation SR 61.20%→84.28%、real hard cases 10%→65%。这使“group-relative diffusion navigation RL”也已成为直接邻近路线。

[JUDGMENT] 因而无论选择 DPPO、ReinFlow 还是 Flow-GRPO，论文的可信差异都必须落到**问题条件、信用分配机制和闭环证据**，不能落到算法标签。

## 4. 三条路线的双向钢人论证

### 4.1 路线一：DDPM/DDIM + DPPO

#### 最强支持论证

1. [FACT] 这是目前唯一已经完成官方数学核心固化、E5 parity、真实 optimizer update、checkpoint/resume 与正式长训化 staging 的路线；工程不确定性最低。
2. [JUDGMENT] 当前最迫切目标是先得到真实正向 RL 收益。继续训练能最快回答“Reward v1.3 + 当前环境 + action chunk DPPO 是否能突破 BC”，而不是重新把时间花在 FM likelihood/SDE/group rollout 的基础正确性上。
3. [FACT] DPPO 本身有机器人连续控制和 action-chunk 证据；本项目的 11d action、LoRA actor、三类 capability metrics、role/world metadata、paired eval 和 Gazebo 回归链路都围绕它完成了最新审计。
4. [JUDGMENT] 即使不产生新 RL 算法，完整的“原始点云—多步 UAV 轨迹—无外部修正—DPPO 能力提升—PX4/Gazebo”可以形成应用型期刊论文；学位论文再把 FM/GRPO 作为第二阶段扩展，研究叙事连续。
5. [JUDGMENT] 与 Liu et al. 的差异并不只是一处：critic-based DPPO vs critic-free GRPO、原始点云 vs structured obstacle states、11d trajectory chunk vs 3d acceleration、PX4/Gazebo vs AirSim、无 QP correction vs CBF/QP filter。若实验做实，方法链不是等价复现。

#### 最强反对论证

1. [FACT] Liu et al. 已经覆盖 DDPM+UAV+relative state+RL，DPPO 官方又覆盖 diffusion-policy PPO；简单组合两者的新颖性主要是应用适配，不是新的数学原理。
2. [FACT] 2026-08-22 审计已判定“DDPM/iDP3-UAV + collision loss + DPPO”不足以作为强方法型期刊的独立创新核心。
3. [JUDGMENT] “egocentric”本身尤其弱，因为 Liu et al. 已使用 relative goal/obstacle states，iDP3 也天然是 egocentric point-cloud policy。除非提出新的不变量、credit 或 geometry-conditioned update，审稿人可能把它视为任务接口差异。
4. [JUDGMENT] DDPM/DDIM 推理步数与实时性会受到 FlowPilot 和本项目自有 4-step FM 的双重追问：既然少步 FM 已存在，为什么最终主模型仍是 DDPM？只有同协议结果能回答。
5. [UNCERTAIN] 当前正式训练尚无已核验正收益。若完整预算后 actor update 很小、critic 失真或三类能力不涨，工程成熟并不能转化为论文结果。

### 4.2 路线二：4-step FM + ReinFlow-style PPO

#### 最强支持论证

1. [FACT] ReinFlow 是直接面向连续机器人控制的 NeurIPS 2025 方法，覆盖视觉、稀疏奖励、长时域与 few-step flow；与当前 Phase1aPolicyFM 的 4-step Euler 高度贴合。
2. [FACT] ReinFlow 官方代码继承 DPPO。现有 Gym/kinematic environment、reward、termination、metadata、vector rollout、GAE/critic、PPO minibatch、checkpoint、audit 和 paired evaluation 大部分可复用；只需重写 flow transition probability core，而非重建整套系统。
3. [JUDGMENT] FM 的 4-step 推理更适合论文实时性与后续部署叙事，也能与 FlowPilot 正面比较“原始点云/11d chunk/策略内安全学习”而不是避开 FM 趋势。
4. [JUDGMENT] learnable noise 可按 observation/time/latent 调整探索：空旷状态低噪声，dense/trap 状态保持探索，理论上比固定 SDE noise 更适合三类能力目标。
5. [JUDGMENT] 期刊与学位论文可以自然分层：先报告 FM 与 DDPM 同协议比较及 FM-PPO 后训练；学位论文再扩展 group-relative credit、sim-to-real 或硬件平台。

#### 最强反对论证

1. [FACT] ReinFlow 已是公开算法；“FM+ReinFlow 用于 UAV”仍主要是应用迁移，不能仅凭模型和 RL 算法都变了就声称强原创性。
2. [FACT] 历史 Route A 已经实现 `Phase1aPolicyFM + LoRA + ReinFlowNoiseModule`，并经历 continuous-online critic/replay divergence；Route B frozen latent steering 也稳定但未突破 BC。虽然不能据此证明 FM-RL 无效，但说明这不是一条从零风险很低的新路。
3. [JUDGMENT] ReinFlow 保留 critic/GAE，因此不能绕开当前项目历史上最难的 critic bootstrap、Q-scale 与 schedule 问题；只替换 actor 概率核心可能重现“系统稳定但能力不涨”或 Q divergence。
4. [UNCERTAIN] CFG $\lambda=1.5$、SFP、AnchorHead、4-step Euler 与 learnable-noise likelihood 的联合一致性没有现成论文保证。实际 guided velocity 必须成为 transition mean，并通过 old/new ratio=1、finite log-prob 和 zero-adapter parity 测试。
5. [RISK] 过强 BC/W2 anchor、过小 noise、过严 PPO clip 会把探索压回 BC 支持域；过大噪声又可能在 UAV dense clutter 中造成不可恢复碰撞。稳定化有抹平有效学习信号的风险。
6. [JUDGMENT] 在当前 DDPM 正式训练尚未给出终点结果前立刻切换，会放弃一次最有信息量的对照，并把论文周期重新置于实现审计阶段。

### 4.3 路线三：4-step FM + Flow-GRPO / 机器人 Flow-SDE+GRPO

#### 最强支持论证

1. [FACT] critic-free GRPO 不需要 value network，可直接避开 critic warmup、explained variance、twin gap、Q scale 和 bootstrap 偏差。
2. [FACT] Flow-GRPO 已给出 ODE-to-SDE 与 closed-form transition ratio/KL；πRL 又证明 Flow-SDE+GRPO 可迁移到机器人 VLA，并显著提升 SFT baseline。
3. [JUDGMENT] 同一状态下采样多条 action chunks，天然适合比较 UAV 的左绕、右绕、上绕、后退脱困等多模态行为；组内排序可避免跨场景绝对 return 标度不一致。
4. [JUDGMENT] Liu et al. 已展示 UAV trajectory-level group relative advantage 的应用价值；可以借鉴其“相似难度内比较”思想，同时拒绝 CBF/QP 和结构化障碍输入，形成更符合本项目边界的策略内版本。
5. [JUDGMENT] 若能提出新的 state-matched group construction、UAV capability-aware group validity 或 chunk-level temporal credit，并做严格消融，三条路线中它最可能产生一个可独立公式化的方法机制。

#### 最强反对论证

1. [FACT] 原 Flow-GRPO 只是 T2I；官方代码是 diffusers/accelerate/reward-server 栈，没有机器人/UAV rollout 接口。工程复用价值远低于 ReinFlow。
2. [FACT] πRL 的同一机器人公开对比中 PPO 一致优于 GRPO：π0 平均 96.0% vs 90.0%，π0.5 为 97.9% vs 91.5%。这直接反驳“critic-free 必然更优”。
3. [FACT] 机器人 GRPO 的组内 advantage 需要同一状态/同一任务条件。普通不同 episode 拼组会把环境难度当作策略优劣；若 simulator 不能可靠 snapshot/reset，同状态 group 的真实环境代价约乘以 group size $G$。
4. [JUDGMENT] UAV reward 很容易出现整组全失败或全成功，导致组内 $\sigma_R\approx0$、梯度消失或不稳定。Flow-GRPO 自身显示 group size 从 24 降到 12/6 会训练 collapse；Liu et al. 自适应组大小的公式与实验配置之间还存在不一致，不能照抄其数值。
5. [JUDGMENT] 使用 learned reward surrogate 可避免真实状态复位成本，却会引入 OOD action-chunk 高估与 reward hacking；这会削弱 MC-5 的“能力来自策略学习”归因。
6. [FACT] 原 Flow-GRPO 的 Denoising Reduction 对 4-step FM 几乎无用；有限步 ODE→SDE 的边际等价只在连续时间理论成立，4-step Euler-Maruyama 的离散误差必须重新验证。
7. [JUDGMENT] “综合 Flow-GRPO 官方 + Liu et al. + 本项目”若只是拼装模块，查重风险不会自动降低，反而可能让方法继承链更密、更难归因。必须有一个真正新的 group/credit 机制才值得承担高成本。

## 5. 双方真正的分歧

[JUDGMENT] 三条路线争论表面是 DDPM vs FM、DPPO vs ReinFlow vs GRPO；真正分歧是以下五项：

1. **首要优化目标**：未来 3–6 个月应优先最大化“得到可复现正收益的概率”，还是优先最大化“方法章节的算法新颖性”。
2. **论文定位**：期刊论文是否接受应用研究型贡献；如果必须是强方法型论文，现有三条“官方算法+UAV适配”都不够，必须新增机制。
3. **critic 判断**：历史 critic 问题是已经构成路线性反证，还是只是旧实现/日程问题、可由新 clean DPPO 训练证伪。前者支持 GRPO，后者支持先完成 DPPO 或 ReinFlow PPO。
4. **同状态 group 成本**：轻量 simulator 是否支持可靠 state snapshot/reset 和足够大 group；如果不支持，Flow-GRPO 的核心优势会被采样成本和无效 grouping 抵消。
5. **FM 起点质量**：现有 4-step FM 在同协议闭环中是否至少不弱于 DDPM，且其 CFG/SFP/Anchor 路径能否与 stochastic likelihood 正确结合。若 FM 基线本身弱，直接 FM-RL 的成功概率显著下降。

## 6. 最可能改变结论的关键变量

| 关键变量 | 支持 DDPM+DPPO 的结果 | 支持 FM+ReinFlow 的结果 | 支持 FM+Flow-GRPO 的结果 |
|----------|----------------------|-------------------------|---------------------------|
| DDPM 正式 seed 终点 | 三类能力有多 seed paired 正增益 | 仅正增益但实时性/推理成本不够 | critic 明确失败且 actor/环境合同健康 |
| DDPM actor/critic 诊断 | explained variance、update norm、KL/ratio 健康 | critic 可用，说明 PPO 外壳可迁移 | critic 在正确 reward/obs 下仍系统失效 |
| FM vs DDPM 同协议 BC | DDPM 显著更强 | FM 不劣且 4-step 更快 | FM 不劣且能从同状态产生有效多模态 groups |
| FM stochastic parity | 不相关 | ReinFlow ratio=1/logprob/zero-adapter 全通过 | Flow-SDE finite-step marginal/ratio tests 通过 |
| group validity | 不相关 | 不需要同状态 group | 每组 reward std、成功/失败混合、有效梯度稳定非零 |
| 论文目标 | 应用型期刊可接受 | 应用型+少步部署主线 | 强方法型，且愿意新增 UAV group-credit 机制 |
| 时间/算力 | 希望尽快形成结果 | 可接受一次概率核心迁移 | 可接受高成本重写和 $G$ 倍 rollout |

[JUDGMENT] 其中最有信息量的不是短期 reward 曲线，而是：**当前 DDPM-DPPO 完整预算、多种子和固定 paired capability 结果**。它同时回答正收益可行性、critic 是否真是路线阻塞，以及现有环境/reward 是否能提供有效学习信号。

## 7. 除三条主路线外的候选思路

### 7.1 分阶段双论文资产路线

[JUDGMENT] 不把“是否转 FM”当作立即二选一：先让正在进行的 DDPM-DPPO 形成完整、可复现的能力证据和强 baseline；只在终点合同完成后，把相同 environment/reward/eval protocol 迁移到 FM。期刊可定位为 DDPM-DPPO 的应用型闭环论文；学位论文再做 DDPM→FM 的受控比较与 FM-RL 扩展。

优点：最大化已投入资产价值，保留清楚因果对照。风险：如果期刊明确要求强算法新颖性，应用型定位可能不够。

### 7.2 Flow-SDE + PPO 中间路线

[JUDGMENT] 如果 FM 必须启动，但 learnable noise head 工程过重，可先采用 πRL 式 Flow-SDE 随机化，仍使用 PPO/critic，而不是直接跳到 GRPO。这样可先分离“FM stochastic transition 是否正确”和“critic-free grouping 是否有效”两个问题。

优点：比完整 Flow-GRPO 少一个 state-matched grouping 风险。风险：仍需 critic，算法原创性也不高。

### 7.3 新机制路线：UAV capability-matched group credit

[ASSUMPTION] 若用户明确坚持强方法型期刊，可把新机制聚焦在：对同一局部状态/目标，按三类能力构造可比较 action-chunk groups；用 onset、future clearance、dead-end recovery、full-space novelty 与可执行性组成 group-validity 和 temporal credit，而不是只用 episode scalar return。

[JUDGMENT] 这比“直接把 Flow-GRPO 搬到 UAV”更可能形成独立公式贡献，但它目前只是候选研究问题，必须先做新颖性检索、数学设计、group snapshot 可行性验证与 Zread 审查，不能直接实施或写成已成立方案。

## 8. 学术诚信、相似性与新颖性边界

[FACT] 与已有论文研究同一任务、使用相同基础模型或引用同一公开算法，不等于抄袭。抄袭风险来自复制未引用的文字、图表、代码或公式推导，以及把他人机制声称为自己提出。

[JUDGMENT] “换模型/换 RL 算法”不会自动降低查重，也不会自动提高新颖性。真正安全的做法是：

- 明确引用 iDP3、DPPO、ReinFlow、Flow-GRPO、Liu et al.、FlowPilot、X-NavDP；
- 对每个继承组件写清“采用/适配/修改/新增”；
- 只把本项目新设计且有消融的机制列为方法贡献；
- 用同协议实验说明为什么这些改变对 UAV 三类能力有作用；
- 禁止复用 Liu et al. 的图、表、措辞和公式叙述结构；若借鉴 group/relabeling 思想，需独立推导并说明差异。

## 9. 资料采用状态与迁移判断

| 来源 | 状态 | 本报告用途 | 对 iDP3-UAV 的判断 |
|------|------|------------|--------------------|
| Liu et al., AEJ 2026 | 已采用 | 直接重合矩阵、GRPO/CBF/relabeling 核验 | 任务最近邻；CBF/QP 不合规，不能整套迁移 |
| DPPO, arXiv:2409.00588 | 已采用 | 当前 DDPM 路线数学与代码来源 | 可直接作为 DDPM actor core；不是原创贡献 |
| ReinFlow, arXiv:2505.22094 | 已采用 | FM+PPO 机器人直接证据 | 高相关、可复用基础设施；需重审 4-step/CFG/SFP |
| Flow-GRPO, arXiv:2505.05470 | 已采用 | ODE→SDE+GRPO 数学与局限 | 原始 T2I，不可直接作为 UAV 实现模板 |
| πRL, arXiv:2510.25889 | 已采用 | 机器人 Flow-Noise/Flow-SDE、PPO/GRPO 对比 | 关键迁移证据；PPO 对比优于 GRPO |
| Pfrommer et al., arXiv:2507.15073 | 候选 | robot FM+GRPO、reward surrogate 风险 | 二维任务证据弱，只能作机制参考 |
| Flow Policy Gradients, arXiv:2602.02481 | 候选 | 说明 flow RL 赛道拥挤与替代数学 | 不是当前最短实现路线 |
| FlowPilot, arXiv:2608.00635 | 已采用 | UAV-FM novelty pressure、实时性基准 | 直接相关；观测/轨迹表示不同 |
| X-NavDP, arXiv:2607.28560 | 已采用 | navigation diffusion RL 最新对照 | 能力目标高度相近；其轨迹修正不应迁移 |
| 执行期 CBF/QP、trajectory smoothing/truncation | 拒绝 | 仅作差异与风险说明 | 违反 MC-1/3/5 或存在强风险 |

## 10. 一手来源登记

1. DPPO, arXiv:2409.00588, https://arxiv.org/abs/2409.00588, DOI:10.48550/arXiv.2409.00588；用途：DDPM policy-gradient 与官方实现边界。
2. ReinFlow, arXiv:2505.22094v7, https://arxiv.org/abs/2505.22094, DOI:10.48550/arXiv.2505.22094；用途：flow-policy learnable-noise PPO 与机器人实验。
3. Flow-GRPO, arXiv:2505.05470v5, https://arxiv.org/abs/2505.05470, DOI:10.48550/arXiv.2505.05470；用途：ODE→SDE、group-relative flow optimization、group/noise ablation。
4. Flow-GRPO official code, https://github.com/yifan123/flow_grpo；用途：确认官方实现范围为生成模型栈。
5. πRL, arXiv:2510.25889v3, https://arxiv.org/abs/2510.25889, DOI:10.48550/arXiv.2510.25889；用途：机器人 Flow-Noise/Flow-SDE 与 PPO/GRPO。
6. RLinf official repository/docs, https://github.com/RLinf/RLinf；用途：π0/π0.5 PPO/GRPO 公开结果和配置。
7. Reinforcement Learning for Flow-Matching Policies, arXiv:2507.15073, https://arxiv.org/abs/2507.15073；用途：robot GRPO + reward surrogate 与二维 unicycle 证据。
8. Flow Policy Gradients for Robot Control, arXiv:2602.02481, https://arxiv.org/abs/2602.02481；用途：2026 flow policy gradient 最新机器人边界。
9. FlowPilot, arXiv:2608.00635, https://arxiv.org/abs/2608.00635；用途：UAV FM、实时性、可执行轨迹最新直接工作。
10. X-NavDP, arXiv:2607.28560, https://arxiv.org/abs/2607.28560；用途：navigation diffusion RL post-training 与三类能力邻近证据。
11. Liu et al., Alexandria Engineering Journal 140 (2026) 33–46, DOI:10.1016/j.aej.2026.02.024；用途：用户指定直接比较论文。

## 11. 本报告自检

- [x] 统一使用 DPPO，不与 DDPO 混称。
- [x] 读取并渲染核验用户指定 Alexandria PDF 的方法、算法和结果页。
- [x] 核验 Flow-GRPO 官方论文与官方代码，资料已归档并记录 SHA256。
- [x] 使用 2026-08-29 一手来源刷新 ReinFlow、πRL、Flow Policy Gradients、FlowPilot、X-NavDP 边界。
- [x] 区分用户实时状态与本地 staging 文档的证据差异。
- [x] 没有把 formal training、正向收益、Gazebo/PX4 或多种子结论提前写成已证明事实。
- [x] 对照 MC-1~MC-5；拒绝执行期 CBF/QP 和策略外轨迹修正。
- [x] v1.0 停在决策前；v1.1 已在用户接受应用研究型定位后给出路线裁决。

## 12. 用户回答后的决策前提更新

[FACT] 用户接受将当前期刊论文定位为“应用研究型论文”，同时明确以下边界：

1. 当前 DDPM-DPPO 正式训练不暂停、不改参、不因中途曲线波动提前裁决；
2. 后续 FM-RL 评估允许复用已经完成官方映射的 clean DPPO 工程资产；
3. ReinFlow 必须以论文作者的官方 GitHub 项目与论文为上游实现基线；凡接口兼容的 sampler、transition/log-prob、PPO loss、配置、测试和训练控制流均允许直接复用，不限于数学公式；
4. Flow-GRPO 若进入评估，同样以作者官方 GitHub 项目与论文为实现基线，优先修改/扩展官方代码，不从零另写一套同名算法；
5. 历史自定义 ReinFlow-style、ARFM、旧 critic/replay 分支不能成为新算法实现依据，只能作为“错误模式不能继承”的代码审计证据；
6. 用户已明确授权读取 WSL 全部代码。

[FACT] 2026-08-29 本轮只读核查时，WSL 正式 DPPO 进程仍存活，输出目录已产生 `metrics_update_000001.json` 至 `metrics_update_000049.json`，并发布了 update 8/16/24/32/40/48 的完整 checkpoint。该事实证明“正式训练已经启动且正在运行”；它不证明终点正向收益。

[JUDGMENT] 因此后续路线不是“停止 DPPO 后改做 FM”，而是：**让 DDPM-DPPO 完成预注册预算；同时在不占用训练 GPU 的条件下，开展 FM checkpoint 合同、官方 ReinFlow/Flow-GRPO 接口和论文实验矩阵的独立设计。**

## 13. 当前 FM 是否属于主流 Flow Matching

### 13.1 代码事实

[FACT] `phase1a_policy_fm_v9_2.py:642-665` 的训练核心为：

$$
x_t=(1-t)x_0+t x_1,\qquad u_t=x_1-x_0,
$$

并以 $\|v_\theta(x_t,t,c)-u_t\|_2^2$ 回归条件向量场。`phase1a_policy_fm_v9_2.py:289-351` 从高斯噪声 $x_0$ 出发，在 $t=0$ 至 $1-\sigma_{\min}$ 上进行 4 步 Euler ODE 积分。该训练目标、时间方向和采样方向彼此一致。

[FACT] 现有 v9.2 checkpoint 训练日志包含持续下降的 `bc_loss`、Anchor CE 与开环相关性记录；保存脚本把 `num_fm_steps`、`sigma_min`、`fm_t_scale`、`fm_anchor_t_start` 和 solver 写入 payload。它不是把 DDIM scheduler 当作 FM sampler；DDIM scheduler 只因基类构造合同而保留。

[JUDGMENT] 因此现有模型是有效的、主流意义上的**直线路径 Conditional Flow Matching / rectified-flow 型策略**，现有 FM checkpoint 可以作为官方 ReinFlow 或 Flow-GRPO 适配的 BC 起点，不需要仅因“是否是 FM”而重新训练。

### 13.2 “OT-CFM”命名修正

[FACT] 代码中的 $x_0$ 是逐样本独立高斯噪声，$x_1$ 是当前 batch 的示范轨迹；未发现 minibatch optimal-transport plan、Hungarian/Sinkhorn/POT 求解或按 OT plan 重排 $(x_0,x_1)$ 的步骤。

[FACT] TorchCFM 官方项目区分：`ConditionalFlowMatcher` 使用独立联合 $q(x_0)q(x_1)$，而 `ExactOptimalTransportConditionalFlowMatcher` 使用 OT joint $\pi(x_0,x_1)$。来源：Alexander Tong 等官方项目及 arXiv:2302.00482。

[JUDGMENT] 当前实现不应在论文中称为严格的 **OT-CFM**；更准确的表述是“linear-path CFM with independent source-target coupling”。这是一项理论归因与写作修正，不是否定 checkpoint 有效性。若未来确实要声称 OT-CFM，必须新增 condition-aware OT coupling、重新训练并做同协议消融；它不是当前 FM-RL 的必要前置。

## 14. Anchor 机制的真实状态与 GRPO 关系

### 14.1 当前 Anchor 做了什么

[FACT] `anchor_head.py:15-44` 是三层 MLP 分类器；v9.2 的 8 帧观测使输入维度为 1536，输出 17 类。训练标签由动作轨迹在 `[dpx,dpy,dpz,dyaw]` 四维子空间内的最近 anchor 决定：`phase1a_policy_fm_v9_2.py:249-266`。

[FACT] v9.2 日志显示 AnchorHead 确实被训练，训练集 `anchor_acc` 从约 0.65 上升到约 0.916；但这只证明它能拟合“最近 BC anchor”分类标签，不证明 17 类对应稳定的避障语义，也不证明它能提高 RL return。

[FACT] 所有当前 FM 推理变体均将 `anchor_idx=None`；`phase1a_policy_fm_v9_2.py:501-524` 从纯噪声启动。历史 FM-RL loader 还显式用 `anchor_bank_path=None` 构造 no-anchor runtime，并断言 `anchor_head is None`。因此用户所说“Anchor 存在但目前没有用到”对**推理与现行 RL actor**是准确的；对**BC 辅助训练**则不是完全未使用。

[FACT] 历史文档把该状态称为 Anchor 消融裁定，但现有证据只证明 no-anchor FM 已具有可用 BC 能力，并未形成严格的“anchor-on 显著差于 anchor-off”配对实验。因此更准确的结论是：**Anchor 推理已停用且未被证明必要，不等于 Anchor 表征已被数学证伪。**

### 14.2 Anchor 不等于 GRPO

[PROVEN] GRPO 的核心组相对优势可写为

$$
\hat A_i=\frac{R_i-\operatorname{mean}_{j\in G}(R_j)}
{\operatorname{std}_{j\in G}(R_j)+\epsilon},
$$

它要求同一或严格可比条件下的多条 rollout 及其 reward。AnchorHead 的输出是动作模式分类 logits；它既不提供组内 reward baseline，也不替代 SDE transition likelihood、old/new ratio 或同状态复位。

[JUDGMENT] Anchor 可成为 GRPO 的**项目特定扩展**，但不是“有 Anchor 就能低成本实现 GRPO”：

- 只对每个状态取 AnchorHead argmax，会让整组落在同一模式，不能产生 group diversity；
- 按 softmax 采样/枚举 anchor 会新增离散策略概率，若 anchor 参与生成，则 importance ratio 必须包含离散选择概率；
- 仅把生成后的轨迹按最近 anchor 分组，工程较简单，但 Anchor 只做 post-hoc mode label，不负责探索；
- 若从 `fm_anchor_t_start=0.95` 的 anchor 轨迹启动，4 步积分只覆盖约 $[0.95,0.995]$，可能显著限制探索，必须视为独立策略变体验证；
- 当前 FM UNet 没有显式 anchor-token 输入，Anchor 主要通过初始化影响轨迹；若改成显式 mode token，需要修改条件接口并重新训练或至少适配。

[JUDGMENT] 最低风险用法是先把 AnchorHead 当作**诊断与分层标签**：记录 occupancy、entropy、nearest-anchor 一致率、per-anchor SR/CR、同状态组内模式覆盖。只有这些量证明 17 类具有稳定语义后，才考虑 Anchor-stratified GRPO；不能直接把现有 AnchorHead 写成论文贡献。

## 15. 官方上游代码基线下的复用与适配裁决

[FACT] 2026-08-29 已将两套作者官方源码快照保存到 Windows：`chengxu/official_upstream/ReinFlow`（commit `e722e151bed767f3ffef47527cf697f2358af55d`）和 `chengxu/official_upstream/Flow-GRPO`（下载时 `main` commit `879042cf5707f8b90daa98d147d7deac2317c5da`）。来源与许可证记录见 `chengxu/official_upstream/README.md`。

[JUDGMENT] 后续不是“只抄官方公式后重写”，也不是在官方目录里不可追踪地混改。正确工程形态是：保留 `official_upstream` 原样快照；从对应官方目录派生 `chengxu/official_adapted/<algorithm>_iDP3`；尽量保留官方文件、类、函数、控制流与测试，只替换无法兼容的图像/MLP/环境接口，并维护逐文件 upstream-to-adapted 映射。这样既满足“基于官方代码修改”，又能审计哪些是作者代码、哪些是项目适配。

### 15.1 允许复用的 clean DPPO 系统资产

[FACT] 当前 `dppo_uav_rebuild` 不是完全 actor-agnostic：

- `entrypoints/build_system.py:51-130` 直接构造 E5 DDPM loader、10-step `E5PPODiffusion`、DDPM LoRA 和 576d critic；
- `actor_ddpm/rollout_sampler.py:35-82` 固定 DDPM chain 与 log-prob 形状；
- `engine/rollout_buffer.py:37-122` 固定 chain=`(11,16,11)`、log-prob=`(10,16,11)` 和随机去噪步采样；
- `engine/trainer.py:105-234` 直接调用 official DPPO `runtime.loss`。

[JUDGMENT] 因此不能把 FM policy 类名替换进去就完成迁移。但以下资产可在新分支中保留或泛化：

| 资产 | Official ReinFlow | Official Flow-GRPO | 说明 |
|------|--------------------|--------------------|------|
| world admission / task sampler / train-eval 隔离 | 高复用 | 高复用 | 与 actor 数学无关；`w4/w8/w11/w12/w18` 继续只作 eval |
| kinematic env / Reward v1.3 / termination / capability metrics | 高复用 | 高复用 | 三类能力目标保持同协议 |
| action semantics 与执行 chunk 合同 | 高复用 | 高复用 | 仍为 11d step-wise trajectory；需重新核对 FM 的 8-step 输出与执行切片 |
| GAE / value 目标 | 高复用但需 FM observation adapter | 不使用 | ReinFlow 是 critic-based PPO；GRPO critic-free |
| transaction / rollback / finite gate / audit 框架 | 中高复用 | 中复用 | 指标名与 ratio 统计需按官方算法改写 |
| atomic checkpoint / resume / identity 思路 | 中高复用 | 中复用 | schema 必须加入 FM actor、noise net、group sampler identity |
| E5 loader / DDPM sampler / DDPM buffer / DDPM trainer | 不复用 | 不复用 | actor-specific，不能成为 FM 数学核心 |

[JUDGMENT] 按“功能责任”而非代码行数估计，Official ReinFlow 可复用约 **55%–65%** 的现有 DPPO 系统资产，Official Flow-GRPO 可复用约 **40%–50%**。除此之外，两条路线都应直接继承各自官方仓库中可兼容的概率计算、loss、配置与训练控制流。模型接口不兼容的部分应通过官方代码 fork 后的 adapter/subclass 修改解决，而不是从空文件重新实现 actor probability core。

### 15.2 Official ReinFlow：可行性、难度与最小改造面

[FACT] ReinFlow 官方 `PPOFlow.get_actions` 保存完整 flow chain，并令每步转移满足

$$
x_{k+1}\sim\mathcal N\!\left(x_k+\Delta t\,v_\theta(x_k,t_k,c),
\sigma_\phi^2(x_k,t_k,c)I\right).
$$

官方 `get_logprobs` 在更新阶段用保存的 `chains_prev/chains_next` 重新前向当前 actor，计算新的转移均值、标准差和 log-prob；随后用 old/new log-prob ratio 进入 PPO clipped objective。对应官方文件：`model/flow/ft_ppo/ppoflow.py:195-298,300-395,398-525`。

[FACT] 官方实现的 actor 是 `FlowMLP/NoisyFlowMLP`，observation 接口、网络结构和 action range 均不是 iDP3-UAV；不能完全不改代码地直接 import `PPOFlow` 后加载 Phase1a checkpoint。这不妨碍 fork 官方 `PPOFlow`、保留其 chain/log-prob/loss 控制流，并只替换 actor/observation/action adapter。

[JUDGMENT] 最小正确适配包括：

1. 从 `chengxu/official_upstream/ReinFlow` 派生可追溯的 `ReinFlow_iDP3` fork，保留官方目录结构、许可证和源文件归因；
2. 在官方 `PPOFlow/NoisyFlowMLP` 合同上接入现有 FM checkpoint、冻结 BC actor、可训练 LoRA actor、`ConditionalUnet1D + 1536d point-cloud global_cond` 与官方语义的 noise network；
3. 基于官方 flow-chain sampler 改造成 4-step UAV FM sampler，继续保存 $K+1$ 个 flow states、每步 old log-prob/mean/std 与执行 action；
4. 优先改造官方 buffer/log-prob/PPO loss 路径并接入 clean DPPO 外壳，在更新时保持作者代码的“由保存 chain 重算当前 log-prob”语义；
5. 复用 GAE/value 外壳，但为 FM 观测维度建立独立 critic/observation contract；
6. 扩展 checkpoint identity、rollback、ratio/KL、noise、action diversity 与三能力审计；
7. 保证 CFG 若启用，则 collection 与 log-prob recomputation 使用完全相同的 guided velocity；
8. 将 z/yaw 硬限位的饱和率纳入审计，防止“对 clamp 前路径算概率、对 clamp 后动作给 reward”的信用错配被隐藏。

[JUDGMENT] 难度为**中高（3.5/5）**，核心风险为**概率一致性高风险（4/5）**，但可通过确定性 parity、ratio=1、单 batch gradient 和 checkpoint cold-resume 门禁逐项关闭。它是两条 FM-RL 路线中最可行、最接近当前系统的路线。

[JUDGMENT] 历史 `routea_reinflow_fm_policy.py` 的 log-prob 没有按官方方式从保存的相邻 chain state 重算当前 transition mean，不能沿用。它的 LoRA/loader 也不自动成为新实现资产；新分支应从 clean DPPO 架构和官方 ReinFlow 合同重新建立。

### 15.3 Official Flow-GRPO：可行性、难度与最小改造面

[FACT] Flow-GRPO 作者官方项目面向 SD3/FLUX/Qwen Image 等生成模型。作者的“支持新模型”说明要求为目标模型新增 pipeline-with-logprob、SDE-with-logprob 和训练入口，并明确要求纯 on-policy 首轮 ratio=1。官方仓库并不包含机器人 environment、state reset、trajectory chunk 或 UAV reward。

[JUDGMENT] 可直接复用或小改复用的是：官方 SDE-with-logprob 函数、相邻 latent state 记录与 log-prob 重算、group-standardized advantage、clipped ratio/KL、ratio=1 门禁、相关配置和训练循环骨架。diffusers image pipeline、prompt/reward-server 和图像 batch 不能原样运行于 UAV，但应在官方 fork 中被 UAV observation/task/environment adapter 替换，而不是另起一套与官方无继承关系的 GRPO 程序。

[JUDGMENT] UAV 适配还必须新增：

1. 同一 observation/task state 的 $G$ 条 stochastic FM rollout；
2. 可审计的 state snapshot/reset，保证组内 reward 可比；
3. 整组全成功/全失败、$\sigma_R\approx0$、duplicate trajectory 和无效 mode coverage 的拒绝/降级规则；
4. group-aware buffer、组级 metadata、group exposure 与 capability-conditioned diagnostics；
5. 对 4-step Euler 的有限步 SDE 边际、ratio 和离散误差验证；
6. $G$ 倍 rollout 成本与 24GB GPU 内存约束下的 batching 方案。

[JUDGMENT] 难度为**高（4.5/5）**，概率与 grouping 审计风险为**很高（4.5/5）**，采样成本也显著高于 ReinFlow。它理论上可行，但不能描述为“下载少量 GRPO 模块即可”；即使复用同一环境，训练数据组织和 loss contract 仍需重写。

[JUDGMENT] 官方 Flow-GRPO 最新代码建议 no-CFG/Flow-GRPO-Fast 等图像侧设置；本项目现有 BC 使用 CFG $\lambda=1.5$ 且只有 4 个 FM steps，不能直接照搬。第一版 UAV parity 应保持 collection/recompute 完全同构，是否取消 CFG、只随机化 1–2 steps 必须分别作为消融，不可混入首个正确性版本。

## 16. 明确路线裁决

[JUDGMENT] **当前不暂停 DDPM-DPPO；同时批准启动“Official ReinFlow on iDP3-FM”的独立设计与接口审计。** 这不是转向或替换主线，而是在当前 clean DPPO 系统上抽取通用环境/审计资产，并从 ReinFlow 作者官方仓库派生 iDP3-UAV fork，保留官方概率核心和训练控制流后进行接口适配。

[JUDGMENT] **暂不把 Official Flow-GRPO 设为第一实现分支。** 它保留为第二候选：只有在 FM BC 同协议有效、Flow-SDE transition parity 已通过、同状态 group reset 可复现、且 group reward variance/模式覆盖有效后，才值得实施。

[JUDGMENT] **AnchorHead 不改变上述顺序。** 它值得先做低成本诊断，可能成为后续 `Anchor-stratified group credit` 的研究点；但它不能替代 official GRPO 的 group sampler 和 SDE likelihood，也不能用训练分类准确率直接证明可行。

[JUDGMENT] 这一路线满足“不暂停主线”：当前 DPPO 按预注册计划继续跑满 256 updates；并行阶段只在 Windows 的 `IDP3` 内做官方源码归档、文档、适配代码与静态接口工作，不直接修改 WSL，也不在同一 24GB GPU 上启动 FM 训练。用户随后把 Windows 产物复制到 WSL 对应路径，由 WSL 智能体执行测试。DPPO 完成后，再按 `FM BC parity → official ReinFlow code-path parity → smoke → formal budget` 的顺序使用 GPU。

## 17. 应用研究型论文可以具体写什么

### 17.1 建议的中心科学问题

[JUDGMENT] 论文不以“我们发明了 DPPO/ReinFlow/GRPO”为中心，而以如下问题为中心：

> 在冻结的示范数据、机体系原始点云、11d 多步可执行轨迹和无策略外轨迹修正的约束下，生成式 UAV policy 的在线 RL 后训练，能否稳定提升提前避障、全空间支持扩展与密集障碍脱困，并在 PX4/Gazebo 闭环中保持安全性、实时性与可归因性？

这个问题与 Liu et al. 的 structured-obstacle、单步 3d acceleration、GRPO、AirSim 和执行期 CBF/QP 路线有实质差异；差异来自问题条件与系统证据，而不是刻意改名。

### 17.2 期刊稿可成立的四项应用贡献

1. **UAV 问题重构**：把生成式 policy 适配为机体系点云条件下的 11d trajectory-chunk policy，保持 body-frame invariance，并明确不使用执行期 QP/轨迹重写。
2. **能力导向 RL 训练系统**：以三类真实能力缺口组织 Reward v1.3、train-world admission、metadata、on-policy audit、checkpoint/resume 和终点 paired evaluation，而不是只报告 episode reward。
3. **官方算法的非平凡 UAV 映射**：报告 clean DPPO 在高维 trajectory diffusion policy 上的接口重构、数值一致性和能力结果；若 FM-ReinFlow 完成，则报告官方 ReinFlow 从 MLP robot actor 到 point-cloud ConditionalUnet1D 的受控适配。
4. **闭环与效率证据**：同协议比较 BC 与 RL、DDPM 与 4-step FM（若完成）、lightweight 与 PX4/Gazebo，报告 SR/CR、避障 onset、future clearance、dense recovery、full-space coverage、轨迹可执行性和端到端延迟。

[JUDGMENT] 其中第 2–4 项必须有结果才能成立；仅有系统代码或模型名称不足以投稿。

### 17.3 可以继续挖掘的研究问题

| 研究问题 | 最小实验 | 论文价值 | 当前优先级 |
|----------|----------|----------|------------|
| DPPO 是否产生三类能力正收益 | BC/RL 固定 paired bank、多 seed、CI | 当前最迫切结果与期刊主证据 | P0 |
| reward 哪些分量真正贡献能力 | 删除/组合 onset、support、trap 等项 | 把工程 reward 变成可归因知识 | P0/P1 |
| DDPM 10-step 与 FM 4-step 的能力—延迟 trade-off | 同 observation/action/reward/eval 协议 | 应用型论文的重要经验结论 | P1 |
| official ReinFlow 是否比 DDPM-DPPO 更适合 few-step FM | 同预算、同 capability bank | 形成“生成骨干×后训练算法”对照 | P1/P2 |
| AnchorHead 是否编码稳定行为模式 | occupancy/entropy/一致率/per-anchor SR/CR | 决定 Anchor 能否进入后续方法 | P1，先诊断 |
| Anchor-stratified group credit 是否优于普通同状态 GRPO | official GRPO baseline 后增加单一机制 | 可升级为方法贡献，但风险高 | P2/P3 |
| lightweight 增益能否迁移到 PX4/Gazebo | 固定 checkpoint 的真实闭环 paired trials | 防止 surrogate-only 结论 | P0/P1 |
| RL 是否牺牲动作多样性或只学会保守停滞 | action variance、mode coverage、success-conditioned advantage | 回应“稳定化抹平学习信号”风险 | P0 |

### 17.4 推荐的论文分层

[JUDGMENT] 最稳妥的期刊最低闭环是：`BC/DDPM baseline → official DPPO formal multi-seed → fixed paired capability bank → PX4/Gazebo`。若 official ReinFlow 在投稿前完成，可升级为 `DDPM-DPPO vs FM-ReinFlow` 的同协议应用研究；若尚未完成，不应为了“差异更大”拖住已经具备成稿条件的 DPPO 论文。

[JUDGMENT] 学位论文可以在期刊基础上增加：4-step FM 官方 ReinFlow、Anchor/group credit、FM-DDPM 统一分析和最终实物平台验证。这样期刊与学位论文不是重复，而是“已验证应用系统 → 生成策略后训练机制扩展”的递进关系。

## 18. 下一阶段门禁（不启动训练）

1. 当前 DDPM-DPPO 完整跑完预注册 256 updates；中途只做硬故障监控，不做能力裁决。
2. 为现有 FM checkpoint 建立 identity/loader 报告，固定真实类、state dict、normalizer、n_obs、action horizon、CFG 与 projection 合同。
3. 以 `chengxu/official_upstream/ReinFlow` 为上游，撰写 Official ReinFlow→iDP3-FM 的逐文件/逐函数 fork 映射设计；旧自定义 RL 文件不进入来源列。
4. CPU/static gate：shape、frozen/trainable parameter ownership、checkpoint schema、chain storage、old/new code-path identity。
5. DPPO 训练结束后才运行 GPU parity：noise=0 与 base FM deterministic path 等价；同参数 collection/recompute ratio=1；FM velocity 与 noise network 梯度均非零且有限；cold resume 一致。
6. 只有 Official ReinFlow parity 全通过，才设计短 smoke 与正式预算。
7. Flow-GRPO 只做后续 feasibility gate：同状态 reset hash 一致、group duplicate 可检测、组内 reward 标准差非退化、4-step SDE ratio parity 通过；未通过则不立项。
