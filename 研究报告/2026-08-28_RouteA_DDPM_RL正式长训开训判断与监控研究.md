# Route A DDPM RL 正式长训开训判断与监控研究

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-08-28 |
| 研究类型 | 正式训练开训判断 / diffusion navigation RL / PPO 长训监控 |
| 项目对象 | E5 DDPM + LoRA actor + official-DPPO core + Route A kinematic UAV environment |
| 结论状态 | [JUDGMENT] 训练引擎已能真实更新；当前仓库还缺正式长训协议，取消 Gate 3 短训收益门禁后，应先完成最小长训化改造，再直接启动完整预算工程 seed |

## 1. 本次要回答的问题

[FACT] 用户选择的路线是：第一个长训练作为完整预算、强监控的工程 seed，允许它暴露机制和参数问题，但不把单 seed 直接当作论文最终证据。

[JUDGMENT] 因而本报告不再问“10 update 是否已经带来可见能力收益”，而回答两个更实质的问题：

1. 当前代码是否已经形成能长期、可恢复、可解释地更新策略权重的训练系统；
2. 若不做短训收益门禁，正式长训前仍必须补齐哪些非能力型工程条件，以及运行中应观察什么。

## 2. 当前本地系统事实

[FACT] `train_e5_dppo_v1.yaml` 当前是一次更新、128 transitions、1 epoch；actor LR 为 `3e-4`，critic LR 为 `1e-3`，未启用梯度裁剪。

[FACT] `pipeline.py` 将每轮 rollout 硬限制为 128，并以 minibatch 128 更新；每次 outer update 都保存 checkpoint 和 JSON metrics。它没有正式训练所需的独立 transition budget、checkpoint/eval cadence 或按总环境步结束的配置。

[FACT] `trainer.py` 已调用官方 DPPO loss，记录 policy/value/entropy loss、approx KL、ratio mean、clip fraction、actor/critic gradient norm；遇到非有限 loss/gradient/parameter、零梯度、超 KL 或超 ratio gate 会事务回滚并拒绝更新。

[FACT] `training_audit.py` 已记录 reward 八项分解、reward metrics、rewards/values/next-values/advantages/returns、episode done reason、role segment 数和 actor/critic parameter delta。

[FACT] 交接文档记录 one-update、cold-resume 和 Pilot10 均通过，Pilot10 为 `10 × 128 = 1280` transitions，10/10 updates committed；这证明训练调用链和权重更新存在，不证明长期能力收益。

[JUDGMENT] 因此系统不是“没有搭好”，也不是“已经可按当前 YAML 直接正式长训”。准确口径是：**核心训练引擎已成立，正式长训运行层尚未完成。**

## 3. 相关工作的可迁移经验

### 3.1 官方 DPPO：只采用算法共识，不复制机器人操作参数

[FACT] 官方 DPPO 说明大 batch 的原因是策略更新同时对环境步和 denoising step 取期望；当并行环境减少时，应提高每环境采样步数，使每轮总交互量近似不变。官方 D3IL avoidance 配置使用 50 个并行环境、1 个 critic warmup iteration、actor LR `1e-5`、critic LR `1e-3`、10 update epochs、`gamma=0.99`、`GAE=0.95`、`gamma_denoising=0.95`、clip `0.1`、min sampling/logprob std `0.1`。

[JUDGMENT] 可迁移的是：每轮必须有足够环境覆盖、critic 需要独立热身、actor LR 通常显著低于 critic、同一 on-policy batch 会重复多个 epoch、denoising KL/ratio/clipfrac 必须持续可见。不可迁移的是机械照抄 D3IL 的二维状态、50 MuJoCo env 或 51 iteration。

来源：

- https://github.com/irom-princeton/dppo
- https://github.com/irom-princeton/dppo/blob/main/cfg/d3il/finetune/avoid_m1/ft_ppo_diffusion_mlp.yaml
- arXiv:2409.00588

### 3.2 UAV GRPO-MDP：相近任务需要长训练，但其安全过滤不合规

[FACT] Liu 等人的 Alexandria Engineering Journal 2026 论文将 DDPM、GRPO、hindsight relabeling 和 CBF/QP 用于 UAV path planning。实验采用 5000 rounds、每 round 2048 environment steps，即约 1024 万 environment steps；32 parallel env、每 round 10 policy updates、batch 256 trajectories，并在 easy/medium/hard 和动态障碍环境上用 SR、CR、path efficiency、arrival time、safety margin、smoothness 判定。

[JUDGMENT] 该规模直接支持“1280 transitions 不能判断是否有效”。但其输入是最多 100 个障碍物的结构化相对位置/速度，输出是单步 3D acceleration，算法是 critic-free GRPO，且 CBF/QP 会修改执行动作；这些都不能直接作为本项目 11d trajectory chunk、原始点云、DPPO critic 和 MC-1/MC-3/MC-5 的实现模板。

来源：DOI:10.1016/j.aej.2026.02.024；本地正式 PDF `论文/被参考/Liu_2026_GRPO-MDP_Alexandria_Engineering_Journal.pdf`。

### 3.3 Beyond Imitation：导航 diffusion RL 的 critic 风险与选择性更新

[FACT] Sheng 等人（arXiv:2603.12868）以 NavDP 为基础，对同一 observation 采样 16 条候选轨迹，用 group-relative advantage 做 critic-free RL，并冻结视觉编码器和低层 decoder，只更新高层 decoder 与 action head。其 unseen-scene SR 从 52.0% 提升至 58.7%，SPL 从 0.49 提升至 0.54；论文明确指出从零训练 critic 可能噪声大、收敛慢并影响 actor。

[JUDGMENT] 这不构成改用 GRPO 的充分理由，但支持本项目保留 LoRA/选择性更新并增加 critic warmup、explained variance、value/return scale 和 actor-update magnitude 监控。

来源：https://arxiv.org/abs/2603.12868；本地 PDF `论文/被参考/Sheng_2026_Beyond_Imitation_Diffusion_Navigation_RL.pdf`。

### 3.4 X-NavDP：最接近当前三类能力目标的导航后训练参照

[FACT] X-NavDP（arXiv:2607.28560v2）直接针对 diffusion navigation policy 的 RL post-training，目标包括 dead-end recovery、long-obstacle detour、dense-scene detouring 和跨 embodiment 行为。公开模型在 72 scenes 上训练 24,000 vectorized simulator steps，单节点 8 GPU，报告约 12 小时；SR 从 61.20% 提升至 84.28%。

[FACT] 其训练分为 3000 vectorized-step replay warmup、100 minibatch critic-only warmup、之后 joint update；每 75 vectorized steps 优化一次，每进程抽 192 transitions，拆成 8 个 minibatch；actor/critic LR 从 `2e-5` 线性衰减到 `1e-5`，gradient norm clip 为 5.0。它对每个 state 采样 64 candidates，并按同状态 Q-score 做归一化。

[JUDGMENT] 最值得迁移的不是 GQRM 本身，而是四条导航领域经验：困难行为需要显式训练覆盖；同状态/同角色的学习信号应单独统计；critic 先稳定再带 actor；正式训练用多场景长预算和独立 held-out scenes。其执行前 trajectory truncation/correction/smoothing 属于项目 MC 风险，不能复制。

来源：

- https://arxiv.org/abs/2607.28560
- https://yty-sky.github.io/x-navdp-project-page/
- https://github.com/InternRobotics/NavDP/tree/master/baselines/x-navdp

### 3.5 通用 PPO 长训经验：loss 收敛不等于策略成功

[FACT] CleanRL 的 PPO 参考实现持续记录 episode return/length、SPS、learning rate、policy/value/entropy loss、approx KL、clipfrac 和 explained variance；RSL-RL 默认使用多 epoch/minibatch、advantage normalization、gradient clipping，并可按 desired KL 调节 LR。

[FACT] DPPO 官方 issue #56 有用户报告跑到 8M env steps 后 loss/value loss 很快收敛但 success 始终为 0；issue #58 则报告 pretrained checkpoint、observation 和 config 不匹配导致无法复现。它们是社区个案，不是论文结论，但说明“长训本身”不能替代观测、配置和能力指标的可见性。

[JUDGMENT] 这正是本项目应取消短训收益门禁、但不能盲跑当前 debug YAML 的原因：需要的是**可诊断的长训**，不是更多短训，也不是没有监控的长训。

来源：

- https://github.com/vwxyzjn/cleanrl/blob/master/docs/rl-algorithms/ppo-trxl.md
- https://github.com/leggedrobotics/rsl_rl/blob/main/rsl_rl/algorithms/ppo.py
- https://github.com/irom-princeton/dppo/issues/56
- https://github.com/irom-princeton/dppo/issues/58

## 4. 明确判断

[JUDGMENT] **取消 Gate 3 作为“先用 Pilot10/100-episode lightweight paired benefit 证明有收益，才允许长训”的前置门禁。** Gate 3 原本想降低长训浪费风险，但它把样本不足的短训结果提升为训练准入依据，确实可能误杀需要较长探索和 critic 建立过程的有效路线。

[JUDGMENT] **保留 Gate 3 中有长期价值的 evaluation/trace/bank 设计，但把它们并入正式长训的观测与终点评估，不再要求短 actor 先出现能力提升。**

[JUDGMENT] **当前不应直接用 `train_e5_dppo_v1.yaml` 开跑。** 阻止开跑的不是缺少一次短训，而是该 YAML 和 pipeline 仍明确是 first-stage/debug 形态：1 update、128 rollout、1 epoch、无 critic warmup、无 LR schedule、无 checkpoint/eval cadence、rollout size 被硬锁 128、uniform task sampling 未证明三类 role 覆盖均衡。

[JUDGMENT] **完成下节的最小长训化改造后，可以直接启动一个完整预算工程 seed；不再插入能力型短训。** 修改后的静态/import/single-batch forward-backward/checkpoint-resume 检查只验证程序合同，不判断能力，也不消耗额外短训结论。

## 5. 建议的第一个完整预算工程 seed

以下是首个可诊断长训的预注册起点，不声称是最终最优超参。

| 类别 | 建议起点 | 理由 |
|---|---:|---|
| 总预算 | 262,144 macro transitions | 每 transition 执行 4 步时约 1,048,576 executed steps；比 Pilot10 扩大 204.8 倍，属于完整工程 seed 而非 smoke |
| rollout / outer update | 1024 transitions | 接近官方 D3IL 每 iteration 的千级环境覆盖；可容纳多个完整 60-step episode 和各 role 样本 |
| minibatch | 128 | 保持已验证的 official-DPPO true batch contract |
| update epochs | 5 | 介于当前 1 与官方 avoidance 10 之间；1024 rollout 时每轮 40 optimizer steps |
| critic warmup | 首个 1024-transition rollout 仅训 critic，40 optimizer steps | 避免随机 critic 在第一轮直接驱动 LoRA actor |
| actor LR | `2e-5`，线性降至 `1e-5` | 直接采用 X-NavDP 公开导航后训练量级，并与官方 DPPO `1e-5` 同数量级；不再为 LoRA 无依据上调，不沿用当前 debug `3e-4` |
| critic LR | `1e-3` | 与官方 DPPO avoidance 一致；必须配合 explained variance 和 return/value scale 观察 |
| gamma / GAE | `0.99 / 0.95` | 当前值与 PPO/DPPO 共识一致 |
| gamma denoising | `0.8` 暂保留 | 属于项目 E5 4-step denoising 特定值；首 seed 不同时改动所有项目特定选择 |
| PPO clip | `0.1` | 官方 avoidance 起点；运行中以 clipfrac/ratio/KL 判断，不用曲线好看作为调整理由 |
| min sampling/logprob std | `0.1 / 0.1` | 当前值与官方 DPPO 一致，保留探索和 likelihood floor |
| entropy coefficient | `0` 暂保留 | diffusion sampling 已提供随机性；先测 trajectory/action diversity，再决定是否需要额外 entropy |
| gradient clip | 预注册高阈值并记录 pre/post norm；建议首值 `5.0` | 只防梯度爆炸；若频繁触发必须标为学习信号风险，不能把 clip 当作美化曲线工具 |
| checkpoint cadence | 每 8192 transitions；另存 0/25/50/75/100% milestone | 避免每 1024 transitions 保存全量状态，同时支持故障恢复和轨迹分析 |
| capability eval | 0/25/50/75/100% checkpoint 在固定 held-out bank 上评估 | 作为长训过程观察和终点裁决，不作为中途“效果不好就停”的门禁 |

[UNCERTAIN] 262,144 macro transitions 的实际墙钟时间无法从 Pilot10 交接材料中可靠恢复；正式设计需要用 Pilot10 的真实总时长换算 ETA 和磁盘量，但不应据此缩短预算。

[UNCERTAIN] WSL 权威 admission manifest 的各 role 数量未镜像到 Windows staging，当前 `TaskSampler` 是按 task 均匀抽样而非按 role 均衡。开训前必须只读核对 role counts；若数量不等，需改为预注册 role-balanced/weighted sampling。

## 6. 长训中必须观察的指标

### 6.1 决定“有没有真的学习”

- actor/critic gradient norm，actor/critic parameter delta L2/max/nonzero ratio；
- advantage、return、value 的 mean/std/quantiles，以及 success-conditioned / collision-conditioned advantage；
- policy loss、value loss、explained variance、approx KL、ratio mean 与 P1/P50/P99、clipfrac；
- actor/critic LR、sampling/logprob std、trajectory/action variance 和多模态候选分散度；
- reward 八项的 mean/std/nonzero rate/absolute contribution，按 role 分解。

### 6.2 决定“是否朝项目三类目标学习”

- anticipatory：avoidance onset distance/time、future clearance、near-obstacle lateral/yaw response；
- support expansion：x/y/z envelope coverage、越界/无效轨迹率、全空间 role SR/CR；
- dense recovery：trap/flip 激活率、脱困成功率、停滞时长、dead-end recovery、dense-world SR/CR；
- 通用能力：episode SR/CR/timeout/early-death、path efficiency、minimum clearance、smoothness/jerk、return，全部按 role、world、milestone 分解。

### 6.3 决定“数据和系统是否可信”

- 每 role/world/task 的 transition 与 completed episode 数；
- `SynthPointCloud` no-ray-hit、NaN/Inf、点数/范围、observation hash/shape；
- terminated/truncated/collection-boundary/done-reason 计数；
- rollout SPS、optimizer steps/s、GPU 显存峰值、checkpoint 写入时长和磁盘增长；
- runtime/config/BC/manifest/source hash、RNG state、resume 后首 transition 一致性。

## 7. 只允许提前停止的硬故障

[JUDGMENT] 第一个完整预算 seed 不因 reward 暂降、SR 平台、value loss 高、单 role 变差或中途 paired eval 不显著而停止。只允许在以下情况中止并修复后 resume/restart：

1. NaN/Inf、参数爆炸、持续超硬 KL/ratio gate；
2. 连续多个 optimizer window 的 actor gradient/parameter delta 为零，或所有更新持续 rejected；
3. observation/point-cloud/manifest/role admission 失效，训练输入不再代表设计任务；
4. reward term sum、done/GAE 边界或 on-policy provenance 失效；
5. checkpoint 无法原子保存、identity-validated resume 失败或恢复后轨迹不一致；
6. GPU OOM/磁盘耗尽等使训练无法继续的工程故障。

## 8. 最小长训化改造清单

1. 将 `rollout_transitions_per_update` 与 `minibatch_size=128` 解耦，允许 1024-transition rollout；保留 minibatch 的 official contract。
2. 增加按总 macro transitions 结束的完整预算，支持 checkpoint cadence、milestone 和 resume 后精确剩余预算。
3. 增加 critic-only warmup、actor/critic LR schedule，并把 scheduler state 纳入 checkpoint identity/restore。
4. 核对并实现 role-balanced sampling；继续从训练 factory 排除 w4/w8/w11/w12/w18。
5. 补 explained variance、ratio quantiles、advantage/return quantiles、per-role reward/episode/capability、action diversity、SPS/GPU/disk 指标。
6. 将固定 held-out evaluation 变成长训 milestone/final evidence，不再作为短训开训门禁。
7. 所有训练参数和停止条件在 seed 启动前冻结；运行中只记录诊断，不因曲线波动改同一 seed。

## 9. MC 合规边界

- [FACT] 本报告不建议 CBF/QP、轨迹 truncation/correction/smoothing 或外部 planner 修改策略输出。
- [JUDGMENT] X-NavDP 和 UAV GRPO-MDP 的这些组件只能作为失败模式和训练规模参照，不能迁移到本项目主结果。
- [FACT] Action 仍为 11d step-wise chunk，FM/DDPM 既有冻结不变量不因本报告改变；w4/w8/w11/w12/w18 继续 eval-only。

## 10. 归档清单

| 资料 | SHA256 | 用途 |
|---|---|---|
| `论文/被参考/X-NavDP_arxiv_2607.28560.pdf` | `A0853588074E53B428C8D3C54BAA072AE2FB2E8CBD3549FF340C6CAB3EDDF428` | 最接近的 diffusion navigation RL post-training 参照 |
| `论文/被参考/Liu_2026_GRPO-MDP_Alexandria_Engineering_Journal.pdf` | `3C9C3CD72B0BA48292235291E6E037A4AE6A1A45ABEC4D063D7541675F7EA266` | UAV diffusion+RL 训练规模和指标 |
| `论文/被参考/Sheng_2026_Beyond_Imitation_Diffusion_Navigation_RL.pdf` | `1DAA2516C59B3113A703F1BEC7C3E99881830F431049D6AD51A58D05BABD88D9` | diffusion navigation GRPO、选择性更新、critic 风险 |
| `论文/被参考/Diffusion Policy Policy Optimization.pdf` | `60A17012703CBFE2ADC752EC64A3076A7F9D4B756C1117FFE2704F04A5D721F0` | official DPPO 算法基础 |
| `论文/被参考/RouteA_FormalTraining_sources_20260828/` | 见目录内源文件 | X-NavDP README/config、CleanRL 指标说明、DPPO issues 56/58 快照 |
