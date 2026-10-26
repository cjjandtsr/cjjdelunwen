# 2026-08-10 PhaseBeta 联网资料研究

| 字段 | 内容 |
|------|------|
| 文档类型 | 联网资料研究报告 |
| 日期 | 2026-08-10 |
| 检索日期 | 2026-08-10 |
| 版本 | v1.0 |
| 状态 | 已归档 |
| 当前设计基线 | `sheji/RouteA_RL_Training_System_A_OfficialCore_Design_v1_0.md` |
| 证据边界 | 不运行训练、ROS、Gazebo 或 PX4；只做仓库内只读审计、联网研究与资料归档 |

## 1. 本期项目上下文摘要

[FACT] 本期按 `AGENTS.md` v1.7 读取/搜索了 `sheji/`、`zhidao/`、`jindu/`、`论文/被参考/`、`论文/未被参考/`、`论文/开题报告参考文献/`。`program/jindu/jindu.txt` 不存在，因此当前阶段以最新设计与 `jindu/` 事实文档为准。

[FACT] 自动化 `memory.md` 只记录到 2026-07-06，但系统记录的上次运行时间为 2026-08-05。为避免记忆断档造成重复，本报告额外核验了 2026-08-06 生成的 `RouteA_RL_Training_System_A_OfficialCore_Design_v1_0.md` 和 `DPPO_Official_Code_cc7234a_metadata.md`。

[FACT] 2026-08-06 的最新项目裁决已经从旧 Route A critic/bootstrap 调试推进到 **A-Official-Core 重建**：固定 DPPO 官方实现 commit `cc7234ad7ff39a8f32de3af903606723a16f0648`，通过 iDP3-UAV adapter 对齐 observation、action、两层 MDP、per-denoising-step logprob、reward horizon、GAE、checkpoint 和 paired evaluation 语义。

[FACT] E040 lightweight 训练跑到外层 `3000/3000` 后 paired evaluation 为 `SR=0/128, CR=128/128`，但代码审计同时发现 oldest-observation slicing、no-ray-hit far-plane fallback、错误 action offset、episode role 丢失、reachability admission 缺失、非官方 joint-scalar DPPO ratio 和 terminated/truncated 混用等系统缺口。

[JUDGMENT] 因此 E040 只能证明该 checkpoint 灾难性退化，不能证明 reward 路径 A、DPPO 或 diffusion RL 本身无解；也不能据此直接调高 reach reward、切换算法或扩大训练预算。

[FACT] 三类 Phase β 最终能力目标保持不变：提前避障、full-space support expansion、dense-obstacle capability ceiling。训练数值健康、官方 parity 和输入/动作合同只是能力学习的前置门禁，不能替代能力验收。

[FACT] w4/w8/w11/w12/w18 保持 eval-only regression/reference worlds，不得进入训练、curriculum 或 replay。lightweight/kinematic 结果不得表述为 Gazebo/PX4 闭环结果。

## 2. 检索范围与关键词

[FACT] 检索优先使用 arXiv 官方页、IEEE Xplore 官方页、论文项目主页与官方 GitHub 仓库；检索日期为 2026-08-10。

[FACT] 本期关键词包括：

- `diffusion policy policy optimization official implementation per-step logprob reward horizon`
- `diffusion policy optimization double drift self distillation 2026`
- `flow policy gradients robot control sim-to-real 2026`
- `adaptive action chunking offline-to-online reinforcement learning 2026`
- `UAV obstacle avoidance reinforcement learning curriculum sim-to-real 2025 2026`
- `safe reinforcement learning diffusion policy constraints robotics`
- `point cloud UAV obstacle avoidance sensor noise domain randomization`
- `dense obstacle navigation reactive action chunk execution`

[JUDGMENT] 本期不再泛泛重复 ReinFlow、RFM、FPO、DPPO、DSRL 和“是否需要 RL”的旧论证；筛选标准是资料能否改变 A-Official-Core 的实施门禁、解释新的失败模式，或为三能力验收增加可分离的后续实验。

## 3. 候选资料总表

| # | 标题 | 作者 / 年份 | 可靠来源 | DOI / arXiv ID | 是否下载 | 本期裁决 |
|---:|---|---|---|---|---|---|
| 1 | Diffusion Policy Policy Optimization | Allen Z. Ren et al. / 2024 | https://arxiv.org/abs/2409.00588；https://github.com/irom-princeton/dppo | arXiv:2409.00588；固定 commit `cc7234a...` | 既有 PDF 与官方代码 metadata | 采纳并复用，当前 core/oracle |
| 2 | DiPOD: Diffusion Policy Optimization without Drifting Apart | Haozhe Jiang, Haiwen Feng, Pieter Abbeel, Jiantao Jiao, Angjoo Kanazawa, Nika Haghtalab / 2026 | https://arxiv.org/abs/2606.13795 | arXiv:2606.13795v2；DOI 10.48550/arXiv.2606.13795 | 是 | 采纳为 double-drift 风险与后续独立消融依据 |
| 3 | Flow Policy Gradients for Robot Control | Brent Yi et al. / 2026 | https://arxiv.org/abs/2602.02481 | arXiv:2602.02481v1；DOI 10.48550/arXiv.2602.02481 | 是 | 采纳为未来 FM 路线与 sim-to-real 证据，不改变当前 DDPM core |
| 4 | Adaptive Q-Chunking for Offline-to-Online Reinforcement Learning | Nandiraju Gireesh, Yuanliang Ju, He Wang / 2026 | https://arxiv.org/abs/2605.05544 | arXiv:2605.05544v1；DOI 10.48550/arXiv.2605.05544 | 是 | 采纳为 horizon/credit 诊断与后续消融依据 |
| 5 | Vision-Guided Outdoor Flight and Obstacle Evasion via Reinforcement Learning | 作者见 IEEE 官方页 / 2025-2026 | https://ieeexplore.ieee.org/document/11282444 | DOI 10.1109/LRA.2025.3641120 | 否；保存官方元数据 | 采纳为 UAV curriculum、噪声/domain shift、真实飞行证据边界 |
| 6 | PACE: Phase-Aware Chunk Execution for Robot Policies with Action Chunking | Junnan Nie et al. / 2026 | https://arxiv.org/abs/2606.00537 | arXiv:2606.00537 | 否 | 未采纳到当前 core；动态执行 horizon 会改变冻结 action contract |
| 7 | Adaptive Action Chunking via Multi-Chunk Q Value Estimation | Yongjae Shin et al. / 2026 | https://arxiv.org/abs/2605.10044 | arXiv:2605.10044 | 否 | 未采纳到当前 core；需多 horizon critic 且训练/推理同时改动 |
| 8 | Decoupled Q-Chunking | Qiyang Li, Seohong Park, Sergey Levine / 2025-2026 | https://arxiv.org/abs/2512.10926；https://github.com/ColinQiyangLi/dqc | arXiv:2512.10926；ICLR 2026 | 既有 PDF | 本期不新增；offline goal-conditioned、Q-learning 语义与当前 on-policy core 不同 |
| 9 | Constrained Variational Policy Optimization for Safe Reinforcement Learning | Zuxin Liu et al. / 2022 | https://arxiv.org/abs/2201.11927 | arXiv:2201.11927 | 否 | 未采纳；引入独立 constrained-RL optimizer 会混淆当前 root-cause 与探索信号 |
| 10 | Improving Robotic Generalist Policies via Flow Reversal Steering | Andy Tang et al. / 2026 | https://arxiv.org/abs/2606.13675 | arXiv:2606.13675 | 否 | 未采纳；语义指导/latent steering 不对应当前 frozen UAV data 与三类 reward |
| 11 | Guaranteed Reach-Avoid for Black-Box Systems through Narrow Gaps via Neural Network Reachability | 作者见 IEEE 官方页 / 2025 | https://ieeexplore.ieee.org/document/11127579 | DOI 10.1109/ICRA55743.2025.11127579 | 否 | 未采纳；作为外部 reachability filter 易越过策略内能力归因边界 |

## 4. 被采纳资料与核心贡献

### 4.1 DPPO 官方论文与固定代码快照

[FACT] DPPO 将 diffusion denoising 过程视为内层 MDP，把 environment transition × denoising transition 作为 PPO 样本；官方实现保留 per-denoising-step、per-action-step、per-action-dimension logprob，并对实际 reward horizon 对应的 action prefix 求均值后形成 ratio（arXiv:2409.00588；官方代码 commit `cc7234ad7ff39a8f32de3af903606723a16f0648`）。

[FACT] 官方仓库区分 `min_sampling_denoising_std` 与 `min_logprob_denoising_std`，并提供 denoising-index-dependent advantage discount 与 clip schedule。

[JUDGMENT] 这直接支持 A-Official-Core 的当前顺序：先做 synthetic parity、identity test、executed-action gradient mask、GAE time-limit test，再谈 reward、LoRA rank、训练预算或替代算法。

[JUDGMENT] 官方仓库没有 iDP3-UAV 的 PointNet、历史 observation、CFG、AnchorHead、11d action、Gazebo/PX4 或三类任务 role，因此只能是冻结 core/oracle，不能直接替换项目环境与策略。

### 4.2 DiPOD：double-drift 是新的训练期风险，不是当前 P0 根因

[FACT] DiPOD 指出 variational diffusion RL 可能出现 double drift：RL 更新使 ELBO 与真实 log-likelihood 分离，随后 proxy policy gradient 与真实 expected-return policy gradient 继续错位。论文用 policy-preserving self-distillation / on-policy ELBO regularizer 维持 tight-bound regime（arXiv:2606.13795v2）。

[FACT] 论文在 diffusion language model post-training 与 continuous-control diffusion policy 上报告了更稳定的训练和更高回报，但没有 iDP3-UAV 的 UAV point cloud、11d chunk、CFG/Anchor 或 Gazebo/PX4 验证。

[JUDGMENT] DiPOD 不能推翻 A-Official-Core，也不能解释 E040 的 observation/action/task contract 硬错误；这些错误发生在讨论 variational drift 之前。

[JUDGMENT] 可迁移价值是新增 **G6 之后** 的诊断：记录 reference-policy ELBO gap 或可实现的 surrogate-tightness proxy、KL、clipfrac、denoising-step ratio 与 checkpoint distance。只有官方 parity 和 one-update 机制测试通过后，若出现“初期提升、随后系统性退化”，才允许把 DiPOD-style regularizer 作为独立预注册消融。

[RISK] 若把 self-distillation/BC anchor 默认开启，可能把探索、成功样本 advantage、提前避障与 dense recovery 更新拉回 frozen BC，形成 `[RISK] 学习信号被抹平`。因此必须同时检查 update norm、action variance、success-conditioned advantage 和三能力 proxy。

### 4.3 Flow Policy Gradients for Robot Control：未来 FM 路线仍成立，但不应打断当前 DDPM 重建

[FACT] 该工作研究无需显式 action likelihood 的 flow matching policy gradient，并报告在 locomotion、humanoid tracking、manipulation以及两台 humanoid 的 sim-to-real transfer 上有效（arXiv:2602.02481v1）。

[FACT] 作者明确指出早期 flow policy gradient 在更具挑战的 robotics tasks 上不稳定，并通过改进 objective 与训练分析提升 fine-tuning robustness。

[JUDGMENT] 该证据说明 FM policy RL 仍是有价值的后续主线，尤其契合项目原始 Phase1aPolicyFM；但当前用户已裁决 A-Official-Core 以 Phase② DDPM checkpoint + 官方 DPPO 语义重建训练系统。现在切回 FM 会同时改变 likelihood、sampler、credit assignment 和 checkpoint 起点，破坏 MC-5。

[JUDGMENT] 正确顺序是：A-Official-Core 先关闭合同与训练系统 DoD；若 DDPM/DPPO multi-seed pilot 在合同完整前提下仍无三能力提升，再用同一 task bank、paired artifact 和能力门禁比较 FM policy gradient，而不是用不同环境/不同 reward 的 benchmark 回报替代项目裁决。

### 4.4 AQC：action horizon 是反应性与信用分配变量，但目前只进入诊断层

[FACT] AQC 指出固定 chunk length 在不同状态下可能次优：需要快速反应的状态偏好短 chunk，自由空间运动偏好长 chunk；其方法通过 per-horizon baseline 和 discount normalization 比较不同 chunk 的 advantage（arXiv:2605.05544v1）。

[FACT] AQC 的实验重点是 offline-to-online RL、OGBench、Robomimic 和 VLA/Robocasa，不是 UAV closed-loop 或 on-policy DPPO。

[JUDGMENT] 对 iDP3-UAV 的直接启发不是立刻动态改变 `A_e`。当前 A-Official-Core 必须先把 full trajectory → policy chunk → executed action 的 offset、reward horizon 和 Gazebo—运动学等价合同固定为唯一语义。

[JUDGMENT] 可立即加入的是诊断：按 episode phase/clearance band 记录“执行 horizon 内未来 clearance、状态陈旧度、near-obstacle replan latency”。如果 anticipatory/dense failures 明确集中在固定 horizon 的 stale-observation 区间，才设计独立的 horizon ablation；不得与 core correctness 修复混跑。

### 4.5 Vision-Guided Outdoor Flight：UAV 真实证据链与 domain shift

[FACT] IEEE RA-L 论文 DOI 10.1109/LRA.2025.3641120 使用 stereo depth + VIO 的 sensorimotor policy，经 simulation 中的 privileged learning、curriculum、domain randomization 和 reward shaping，报告对未见 obstacle environments 与未见 drone platform 的 zero-shot outdoor transfer。

[JUDGMENT] 该工作支持本项目的证据层级：curriculum/lightweight training 可以提高覆盖和筛查效率，但部署主张必须回到真实传感器、状态估计噪声和平台闭环。对本项目而言对应 Gazebo/PX4 + MAVROS + px4ctrl + ML Planner，再到实飞；不能以 kinematic SR 替代。

[JUDGMENT] 可迁移的是评估维度而非其 velocity-command architecture：point-cloud invalid rate、VIO/pose noise、latency、domain-randomization strength 和未见空间 shell 应独立报告。项目 11d action、FM/DDPM 核心与 frozen EGO data 不变。

## 5. 未采纳资料与原因

| 资料 | 未采纳原因 |
|---|---|
| PACE, arXiv:2606.00537 | [JUDGMENT] 属于 training-free test-time execution horizon selection。它不直接重写 chunk 内轨迹，但会改变 observation refresh、实际执行 prefix 和 reward attribution；在 action contract / Gazebo 等价 fixture 尚未完全绑定时引入会破坏 MC-5。 |
| ACH, arXiv:2605.10044 | [JUDGMENT] 同时改变 training/inference 的 chunk length，并新增 multi-chunk Transformer critic。变量量级远超当前 P0 合同修复，且不是 on-policy DPPO parity 的直接证据。 |
| DQC, arXiv:2512.10926 | [JUDGMENT] 已有本地 PDF；主要是 offline goal-conditioned Q-learning 与 critic/policy chunk decoupling。本期不重复归档，也不把它强行迁移到官方 DPPO core。 |
| CVPO, arXiv:2201.11927 | [JUDGMENT] safe-RL 的 trust-region/variational constraint 思路有价值，但当前 collision/task/observation 合同尚未闭合。过早加入独立 constraint optimizer 会混淆根因，并可能用保守更新压掉 dense exploration。 |
| Flow Reversal Steering, arXiv:2606.13675 | [JUDGMENT] 依赖 generalist semantic prior、latent reversal 和合理动作指导；当前 frozen UAV dataset 和 role reward 没有相同条件，不作为本期实施依据。 |
| NeuralPARC, DOI 10.1109/ICRA55743.2025.11127579 | [JUDGMENT] reach-avoid verification 可作为独立安全评估参考，但若作为执行时外部轨迹/参数筛选器，会让性能无法诚实归因于 diffusion/RL policy；本期不采纳。 |
| 传统 VFH*/3DVFH+ 动态避障，DOI 10.1109/ICRAS65818.2025.11108762 | [JUDGMENT] 属于可套在其他 planner 上的外部重规划，不符合“策略输出=执行轨迹”的论文主结果边界。 |

## 6. 对 iDP3-UAV 的可迁移建议

### 6.1 本期总裁决：不换主线，给 A-Official-Core 增加可观测性

[JUDGMENT] 本期资料不支持在 A-Official-Core parity 前切换 FPG/DiPOD/AQC，也不支持以更强 safety clamp、动态执行 horizon 或更大 reward 常数掩盖现有合同错误。

[JUDGMENT] 当前固定优先级应为：

```text
G0 provenance / frozen equivalence fixture
→ G1 observation + point-cloud validity
→ G2 action offset + executed horizon
→ G3 task role + reachability admission
→ G4 official DPPO numerical parity
→ G5 no-update / one-update mechanism
→ G6 short micro-train
→ G7 multi-seed pilot
→ G8/G9 formal lightweight training
→ G10 Gazebo/PX4 closed-loop
```

[JUDGMENT] 本周资料只建议在既有 gate 中新增三组非侵入式观测量，不改变算法：

1. **variational drift 诊断**：per-denoising-step KL、clipfrac、ratio、reference checkpoint distance；若可实现，再记录 ELBO-tightness proxy；
2. **horizon/reactivity 诊断**：实际 executed indices、observation age、near-obstacle replan latency、执行 horizon 内 future clearance；
3. **sim-to-real readiness 诊断**：invalid point-cloud rate、pose/VIO noise sensitivity、latency、domain-shift shell 与 failure taxonomy。

### 6.2 三类 Phase β 目标的显式映射

| Phase β 目标 | 本期资料的有效启发 | 当前可加入的指标 | 暂不允许的改动 |
|---|---|---|---|
| 提前避障 | AQC/PACE 提醒固定 chunk 与 observation refresh 会影响 near-obstacle reactivity；DPPO 要求 reward horizon 与 executed action 对齐 | onset distance/time、near-obstacle observation age、replan latency、future clearance、executed-action gradient mask | 在等价合同未冻结前动态改变执行 horizon；post-hoc obstacle repulsion |
| full-space support expansion | FPG 展示 expressive flow policy 的 exploration 潜力；UAV RA-L 支持 domain randomization 与未见平台/环境评估 | 预注册 x/y/z 联合 shells 的 SR/CR、low-density coverage、point-cloud validity、pose/noise sensitivity | 重新采集 EGO 数据；用只扩大 z 的结果冒充 full-space |
| dense-obstacle capability ceiling | DiPOD 提醒长训练后 proxy gradient 可能漂移；UAV curriculum 支持逐级难度与真实传感器验证 | dense SR/CR、trap recovery、deadend dwell、success-conditioned advantage、action variance、ELBO/KL drift、invalid-PC rate | 为降低 CR 删除 dense samples、过强 BC/self-distillation、外部 reachability/trajectory correction |

[JUDGMENT] 三类能力仍必须在固定 paired episode bank、多 seed 与 CI 下以最终预算裁决。训练中间 reward、KL、loss、twin-gap 或短期 SR 只用于诊断，除非出现 NaN/Inf、actor 无更新、观测/metadata/admission/配对失效等硬故障，否则不能替代终点验收。

### 6.3 DiPOD 的受控进入条件

[JUDGMENT] 只有同时满足以下条件，才允许建立 `A-Official-Core + DiPOD regularizer` 独立 ablation：

- official synthetic parity、identity test 和 one-update test 全部通过；
- baseline DPPO 至少完成预注册 micro-train，出现“先提升后持续退化”的可复现形态；
- 退化与 observation invalid、action offset、role/admission、GAE 或 checkpoint resume 无关；
- reference/ELBO proxy 与能力退化同向，至少 3 seeds 可见；
- ablation 固定 task bank、reward、seed、budget 和 adapter，只增加 regularizer；
- action variance、update norm、success-conditioned advantage 不得坍缩。

[JUDGMENT] 在上述条件前，DiPOD 是风险解释与仪表盘来源，不是默认稳定化组件。

### 6.4 FM 路线的受控回归条件

[JUDGMENT] `Flow Policy Gradients for Robot Control` 支持未来比较 FM policy gradient，但进入条件应是：DDPM A-Official-Core 已通过程序 DoD，且 multi-seed pilot 在合同完整情况下仍未产生三能力方向性提升。届时应复用同一 EpisodeTaskSpec、point-cloud gate、action/deployment adapter、paired bank、seed 和能力门禁，只替换 policy-gradient core。

[JUDGMENT] 这能区分“DDPM likelihood/DPPO 表达限制”与“环境、reward、数据支持域或评估问题”，符合 MC-5；现在直接切换则无法分离。

### 6.5 安全 RL 的边界

[JUDGMENT] 当前 collision avoidance 应继续通过训练 reward、有效 point-cloud observation、task curriculum 和 policy 内更新学习。safe-RL 文献可用于约束统计与风险预算设计，但不能默认引入外部 shield、trajectory projection 或强保守更新。

[RISK] 任何 KL clamp、advantage clipping、BC/self-distillation 或 constraint multiplier 若显著降低 update norm、action variance、success-conditioned advantage 或 dense-role gradient contribution，必须标记 `[RISK] 学习信号被抹平`，并停止把短期 CR 改善解释为能力提升。

### 6.6 lightweight、Gazebo/PX4 与实飞证据链

[FACT] 本期资料没有改变项目既有证据边界：lightweight/kinematic 负责快速训练与机制筛查；Gazebo/PX4 + MAVROS + px4ctrl + ML Planner 才是主要仿真闭环证据；实飞只在仿真门通过后启动。

[JUDGMENT] UAV RA-L 资料强化了以下要求：Gazebo/PX4 formal evaluation 应显式注入/记录点云缺失、pose/VIO 噪声、控制与推理 latency，并在未见 obstacle layouts 与空间 shells 上报告结果。不得把 simulator privileged state 暗中带入部署 policy。

## 7. MC 合规检查

| 约束 | 结论 | 本期检查 |
|---|---|---|
| MC-1 策略输出 = 执行轨迹 | PASS | 建议均针对训练 core、输入有效性、诊断与评估；不建议修改策略输出后的轨迹形状。PACE/NeuralPARC/VFH 类方向未进入当前方案。 |
| MC-2 Diffusion policy 是策略核心 | PASS | 当前主线保持官方 DPPO + diffusion policy adapter；FPG/DiPOD 只作为策略内后续候选。 |
| MC-3 学习阶段处理约束 | PASS | 避障、support、dense recovery 继续由 reward、curriculum 与 policy update 学习；不引入 post-hoc obstacle projection。 |
| MC-4 EGO 数据 frozen | PASS | 不建议重采数据；domain randomization 只用于 RL environment/validation，不改变 frozen EGO dataset。 |
| MC-5 归因可分离 | CONDITIONAL PASS | 必须先关闭 official parity 和 adapter 合同；DiPOD、FM、dynamic horizon 只能逐项独立消融。 |

[FACT] 本期未建议 yaw_loss_boost > 1、5d action 缩减、TransDiffuser decorrelation、DAC offline RL、torch.compile + CFG、KD-Tree obstacle repulsion、GOAL-TRUNC 或 post-hoc smoothing。

[JUDGMENT] point-cloud invalid hard gate 是 observation integrity gate，不是轨迹修剪；reachability admission 用于保证训练任务有效，不在策略执行后重写轨迹，因此与 MC-1~MC-3 兼容。

[JUDGMENT] 策略内/策略外边界保持明确：DPPO、FPG、DiPOD-style policy update 和训练 reward 属于策略内；VFH*/NeuralPARC shield、KD-Tree repulsion、GOAL-TRUNC 或任何执行前后的轨迹形状重写属于策略外，不进入论文主结果。

## 8. 风险与不确定性

| 风险 / 不确定性 | 标注 | 影响 | 缓解 |
|---|---|---|---|
| DiPOD 的 double-drift 是否发生在项目 DDPM/DPPO 配置 | [UNCERTAIN] | 过早加 regularizer 会增加变量并抹平 RL | 先完成 parity；只做诊断；满足 §6.3 后独立消融 |
| FPG 的 humanoid/manipulation sim-to-real 能否迁移到 UAV point-cloud trajectory policy | [UNCERTAIN] | benchmark 成功可能不能预测 UAV 能力 | 只保留未来同 bank/core 对照，不作为当前实现依据 |
| AQC 的 offline/Q-critic 结论能否适用于 on-policy DPPO | [UNCERTAIN] | 动态 horizon 可能破坏官方 loss 与部署等价 | 当前只记录 horizon/reactivity 指标，不改执行长度 |
| IEEE UAV 论文的完整实验细节未在开放摘要中核验 | [UNCERTAIN] | 不能复用其精确超参或量化结论 | 只引用官方摘要可确认的 curriculum/domain randomization/real-flight 证据边界 |
| no-ray-hit 可能同时来自相机几何、射线实现或场景覆盖 | [UNCERTAIN] | 仅 hard-drop 可能导致大量无效 rollout | 在 G1 做 10k frame calibration 与原因分类；不得恢复 far-plane 假点云 |
| 稳定化造成“看似安全但不学习” | [RISK] | 三类能力信号被压平 | 联合监控 update norm、action variance、success-conditioned advantage、role gradient 与终点能力 |
| 动态执行 horizon 看似不改轨迹，但改变闭环语义 | [RISK] | Gazebo—运动学等价与 MC-5 失效 | 维持 frozen `A_e`；以后作为单独 contract/version/ablation |
| 研究资料多数非 UAV 11d trajectory setting | [FACT] | 不能直接照搬公式参数或门禁 | 只迁移问题结构与诊断，项目阈值用自身 pilot 预注册 |

## 9. 下一步建议

1. [JUDGMENT] 不新建设计分支；先推动 `RouteA_RL_Training_System_A_OfficialCore_Design_v1_0.md` 完成 Zread 审查与 requirement closure。
2. [JUDGMENT] 在 official parity / one-update evidence 中新增 per-denoising-step KL、clipfrac、ratio、gradient mask 与 executed horizon 索引；这些是低耦合观测量，不改变算法。
3. [JUDGMENT] 在 observation/task evidence 中新增 invalid point-cloud 原因分类、observation age、near-obstacle replan latency 与 role-wise invalid rate，直接服务提前避障和 dense capability 诊断。
4. [JUDGMENT] DiPOD 仅登记为 `post-G6 conditional ablation`；在基线出现可复现的 late-training drift 前不实现、不默认启用。
5. [JUDGMENT] FPG 仅登记为 `post-A-Official-Core route comparison`；若 DDPM/DPPO 合同完整且 multi-seed pilot 仍失败，再用同一 bank/seed/budget 比较。
6. [JUDGMENT] AQC/ACH/PACE 只形成 horizon sensitivity 研究问题；当前固定执行 horizon 不变，w4/w8/w11/w12/w18 继续 eval-only。
7. [JUDGMENT] 任何 formal RL claim 仍需至少 multi-seed lightweight 能力门、随后 Gazebo/PX4；sim-to-real 仅在 Gazebo/PX4 overall SR≥80% 且三能力/CR 不退化后启动。

## 附录 A. 本轮实际归档资料

- `论文/被参考/DiPOD - Diffusion Policy Optimization without Drifting Apart - arxiv_2606.13795.pdf`
- `论文/被参考/Flow Policy Gradients for Robot Control - arxiv_2602.02481.pdf`
- `论文/被参考/Adaptive Q-Chunking for Offline-to-Online RL - arxiv_2605.05544.pdf`
- 复用：`论文/被参考/Diffusion Policy Policy Optimization.pdf`
- 复用：`论文/被参考/DPPO_Official_Code_cc7234a_metadata.md`
- IEEE UAV 资料因全文未直接开放，本轮只在 metadata 中保存官方摘要页信息，不伪称已下载 PDF。

## 附录 B. 自检

- [x] 已读取/搜索 `AGENTS.md`、`sheji/`、`zhidao/`、`jindu/` 和 `论文/`。
- [x] 已检查 `program/jindu/jindu.txt`，当前不存在。
- [x] 已对候选资料记录标题、作者/年份、来源、DOI/arXiv、下载状态及采纳/未采纳理由。
- [x] 只把实际用于报告结论的新增资料放入 `论文/被参考/`。
- [x] 显式对照提前避障、full-space support expansion、dense-obstacle capability ceiling。
- [x] 显式检查 MC-1~MC-5 与策略内/外边界。
- [x] 未建议已证伪方向。
- [x] 区分 lightweight、Gazebo/PX4 与实飞证据。
- [x] 未运行训练、ROS、Gazebo 或 PX4。
