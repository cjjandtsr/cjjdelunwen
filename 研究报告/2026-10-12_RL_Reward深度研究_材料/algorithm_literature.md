# PPO、扩散/流策略微调与 BC 能力变化：独立文献核验材料

| 字段 | 内容 |
|---|---|
| 文档类型 | 文献研究与源码核验材料；供综合报告合并 |
| 日期、版本 | 2026-10-12，v1.0 |
| 检索边界 | 2020—2026，截至 2026-10-12；13 篇独立论文，不声称穷尽 |
| 状态 | 原文方法、相关实验与适用边界已阅读；6 个官方 GitHub 仓库关键源码已通过 GitHub 插件读取；另复用 AWAC 官方源码原件 |
| 行为边界 | 当前 fresh BC seed202609203 的 384 轮保持冻结；本文不是新训练参数或算法批准文件 |
| 原件与元数据 | `论文/被参考/2026-10-12_RL_Reward综合研究/algorithms/papers.json` 与 `github_source_inventory.json` |

## 1. 先明确本项目需要判断的对象

源码路径基准：下文 `engine/`、`config/` 属于 `chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/`；`reward_v2_support/` 属于 `chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/env/`。

[FACT] 本地 fresh384 配置为 384 updates、每轮 1024 rollout transitions，环境 60 次决策预算，环境折扣 0.99、GAE λ=0.95、denoising 折扣 0.8。来源：`chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/config/train_e5_dppo_r1_s2_seed202609203_fresh384_v1.yaml:12`、`:33`、`:53`。运行到 34/384 是用户报告，本次没有访问 WSL 验证运行进度。

[FACT] R1 实际 reward 由终点、历史最好距离进展、连续风险、时间四个顶层量构成。`reward_v2_support/reward.py:93`—`:120` 实际计算八步计划中的尾段风险与已执行连续段风险的最大值；历史进展为 $10(b_t-b_{t+1})/D_0$，到达 +100、真实失败及旧人工空间终止 −50、time_limit 终点为 0、时间 −0.05。内部八步前瞻与历史状态确实存在，不能用“没有旧 onset/trap 同名项”判断能力机制缺失。

[FACT] R1 PPO 信用使用动作索引 `[2:10]` 的八步片段；`engine/official_loss_components.py:76`—`:83` 对该片段 log probability 取平均，已有 prefix/tail/full 诊断。实际执行 H4 与八步计划参与风险、损失的职责不同。`engine/critic_state.py:11`—`:24` 把 $b/D_0$ 送给 critic；actor 的输入不增加该历史标量。`engine/gae.py:16`—`:25` 在 time_limit/truncated 时保留 next V bootstrap，同时断开跨 episode 的 GAE 递推。

[FACT] 训练 `use_bc_loss=False`，启用该分支会抛 NotImplementedError：`engine/trainer.py:272`、`engine/official_loss_components.py:63`。BC 参数冻结并不保证启用 LoRA 后的组合策略保持 BC 行为。旧成功退化、单障碍清障后近目标盘旋等项目观察以 `jindu/2026-10-12_RouteA_Reward设计实现与轨迹表现逐项判断_v1_0.md` 和 `论文/研究报告/2026-10-12_BC成功能力保持与再获得_双向钢人与2020至2026文献复核_v1_0.md` 为项目证据来源；本文不重复声称重新验收其全部原始轨迹。

[FACT] 测试 v3.0 已取消人为高度/横向截断，训练规则暂保留原版本。新判据下必须重采 BC 与 RL 完整轨迹；旧截断失败后面会发生什么不能靠改标签得知。来源：`jindu/2026-10-12_RouteA_测试端取消人工空间截断修复与交接_v1_0.md:1`。

[JUDGMENT] 研究目标是同一 RL 策略获得更高总体安全到达、明显提高复杂避障，同时能完成简单场景；用户允许部分旧成功下降，并不要求精确保持 BC 路线。保护旧能力、恢复已丢失能力、学习新能力需要分别观察。下面的论文不能代替本项目实际训练因果证据。

## 2. 核实后的论文身份与读取范围

年份以首次 arXiv 年份为主；已读版本可能更晚。每条原件的 URL、日期、版本、SHA256、保存状态与用途记录于 `papers.json`。11 份已有原件直接复用，2 份缺失原文新归档；不复制同一论文来增加计数。

| # | 首发年 | 独立论文与 ID | 本次实际读取 |
|---|---:|---|---|
| A1 | 2020 | [Implementation Matters in Deep Policy Gradients: A Case Study on PPO and TRPO，2005.12729](https://arxiv.org/abs/2005.12729) | v1 PDF，§3—5、Fig.1—2；ICLR 常用标题为 Deep RL，是同一篇 |
| A2 | 2020 | [What Matters In On-Policy Reinforcement Learning? A Large-Scale Empirical Study，2006.05990](https://arxiv.org/abs/2006.05990) | v1 PDF，§2、§3.3—3.7、App.B |
| A3 | 2020 | [Revisiting Fundamentals of Experience Replay，2007.06700](https://arxiv.org/abs/2007.06700) | [ICML/PMLR 原文](https://proceedings.mlr.press/v119/fedus20a/fedus20a.pdf)，§3—4、Table 1、Fig.2—7 |
| A4 | 2021 | [Deep Reinforcement Learning at the Edge of the Statistical Precipice，2108.13264](https://arxiv.org/abs/2108.13264) | v4 PDF，§2—4、Table 1、Fig.2—6 |
| A5 | 2020 | [AWAC: Accelerating Online Reinforcement Learning with Offline Datasets，2006.09359](https://arxiv.org/abs/2006.09359) | v1 PDF，§3—4、§6、式6—10 |
| A6 | 2023 | [Efficient Online Reinforcement Learning with Offline Data，2302.02948](https://arxiv.org/abs/2302.02948) | RLPD HTML，§4、§5.1、Fig.7—11 |
| A7 | 2023 | [Cal-QL: Calibrated Offline RL Pre-Training for Efficient Online Fine-Tuning，2303.05479](https://arxiv.org/abs/2303.05479) | v4 PDF，§4—7、式5.1、Table 1—2 |
| A8 | 2023 | [Imitation Bootstrapped Reinforcement Learning，2311.02198](https://arxiv.org/abs/2311.02198) | v1 PDF，§4—5、Algorithm 1、Fig.3、Table 1 |
| A9 | 2024 | [Diffusion Policy Policy Optimization，2409.00588](https://arxiv.org/abs/2409.00588) | v3 PDF/HTML，§4、App.A.1、B、C.1—C.2 |
| A10 | 2025 | [FDPP: Fine-tune Diffusion Policy with Human Preference，2501.08259](https://arxiv.org/abs/2501.08259) | v1 HTML，§IV-C、V-B—V-D、式18—21、Table II |
| A11 | 2025 | [ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning，2505.22094](https://arxiv.org/abs/2505.22094) | v7 PDF（2026-01-08），§4—7、式6—9、Fig.4—6 |
| A12 | 2026 | [Beyond Imitation: Reinforcement Learning Fine-Tuning for Adaptive Diffusion Navigation Policies，2603.12868](https://arxiv.org/abs/2603.12868) | v1 HTML，§IV、V-D、VII、Table II/V/VI |
| A13 | 2026 | [Immiscible Diffusion Policy: Preserving Multimodal Robot Actions through Label-Free Noise Assignment，2610.09369](https://arxiv.org/abs/2610.09369) | v1 HTML，§III—V、式1—5、Table I/III、limitations；2026-10-07 预印本 |

## 3. 逐篇方法、证据与项目边界

### A1. Implementation Matters：实现细节会改变 PPO 实际更新

[FACT] §3 区分 value clipping、reward scaling、初始化、学习率退火等实现选项，对前四项做组合消融。PPO 核心目标为

$$L_{\rm clip}=\mathbb E\left[\min\left(\rho_t\hat A_t,\operatorname{clip}(\rho_t,1-\epsilon,1+\epsilon)\hat A_t\right)\right].$$

[FACT] §4 指出首个优化步骤的 ratio 全为 1，梯度与未裁剪目标相同；clip 目标不是对每个状态 ratio 或 KL 的硬约束。Fig.1—2 显示实现选择显著影响回报与 trust-region 行为。完整组合消融只覆盖前四种优化、特定 MuJoCo 任务，不能解释任意 UAV 退化。[原文](https://arxiv.org/abs/2005.12729)

[JUDGMENT] 适合核查项目 actor LR、多次样本使用、logprob 平均、梯度裁剪后真实更新、critic 尺度及累计 BC 偏离。降低 LR/clip 可能稳定更新，也可能压低困难成功样本贡献；需用已有损失/梯度/轨迹证据检验。成本低至中；不据此一次叠加所有优化。

### A2. What Matters：优势、尺度、数据组织与时间语义

[FACT] 在五个连续控制环境中调查 50 多项选择，训练 250000 多个 agent；使用分组随机搜索并把学习率放入每个组，明确相互作用不能靠孤立单项解释。§3.3—3.6 发现 value normalization 的收益因任务不同；GAE/V-trace 优于所测 N-step，value clipping 在所测任务不利，重复更新中的 stale advantage 可影响表现。GAE 为

$$\hat A_t=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l},\qquad \delta_t=r_t+\gamma V(s_{t+1})-V(s_t).$$

[FACT] §3.6 对 1000 步时限未发现明显处理差异，作者说明可能因时限很大；这不适用于本项目 60 次预算。[原文](https://arxiv.org/abs/2006.05990)

[JUDGMENT] 适合检查价值拟合、优势产生/标准化、重用时旧优势、有限预算目标。上游 λ=0.9 或 LR=3e-4 是该研究推荐起点，不是本项目新参数。成本低至中；尺度修正必须保持终点稀疏信号，不把异常值直接裁掉来改善曲线。

### A3. Experience Replay：数据量、年龄与更新量是不同变量

[FACT] §3 定义 replay capacity、以 learner 梯度步计的样本年龄，以及

$$\text{replay ratio}=\frac{\text{gradient updates}}{\text{environment transitions}}.$$

[FACT] Table 1 中 buffer 从 1M 增至 10M，固定 replay ratio 的 Rainbow 改善 28.7%，DQN 仅 0.1%；§4 的加法/删减消融指向 n-step returns 对大 buffer 收益的作用。稀疏困难游戏又可能需要较旧策略数据，不能把“越新越好”当成普遍法则。[原文](https://proceedings.mlr.press/v119/fedus20a/fedus20a.pdf)

[JUDGMENT] 可借鉴的是分别记录训练域成功样本覆盖、来源策略与重用次数。它研究 off-policy Q-learning，不能授权把 BC/旧 RL 轨迹未经概率和算法处理塞进当前 on-policy PPO。改成 AWAC/RLPD 级 replay 路线成本高；先复用已有 rollout 和训练日志检查，不新增同类诊断框架。

### A4. Statistical Precipice：可解释的提升需要配对与不确定性

[FACT] §3 的 Atari100k case study 用每算法每任务 100 个独立 training runs 检查少 run 估计。论文推荐 stratified bootstrap CI、performance profiles、IQM 等；Fig.5 显示选取训练中最大评价值会改变算法排序。IQM 是删去两端四分之一后的平均，但本项目主终点仍应为安全到达，不能用 IQM 替代。

[FACT] §4.1 说明少 run 的 bootstrap 也可能低估区间，汇总多任务有助于统计效率而不产生新的独立 seed。[原文](https://arxiv.org/abs/2108.13264)

[JUDGMENT] 项目应同时给总体、简单/复杂场景、旧成功保留/丢失、新增成功；同一世界的多任务与五次采样有相关性。若计算配对提升 CI，BC/RL 要共享重采样索引，并保留世界/任务的层级；不能把 420 个条件写成 420 个独立世界。统计成本低；优先复用统一评价和已有统计入口。

### A5. AWAC：有选择地利用旧动作，而非无差别保持

[FACT] §4 从接近经验分布的优势最大化推导非参数目标 $\pi^*\propto\pi_\beta\exp(A/\lambda)$，再投影为加权似然：

$$\max_\theta\mathbb E_{(s,a)\sim\beta}\left[\frac{1}{Z(s)}\exp\left(A^{\pi_k}(s,a)/\lambda\right)\log\pi_\theta(a\mid s)\right].$$

[FACT] critic 通过 off-policy TD 更新，buffer 保留旧数据并加入在线经验。§3 的对比说明单纯 BC 初始化、直接 off-policy 更新、过强 behavior constraint 各有局限，§6 在模拟/机器人任务展示数据效率收益。[原文](https://arxiv.org/abs/2006.09359)

[JUDGMENT] 适合形成“训练时旧有效动作持续提供学习信号”的候选；优势错误会把不良动作高权重复制。它不是当前 DPPO 的保持开关；新 Q-learning 体系、概率与动作 chunk 语义需独立设计。成本高；eval-only 世界不得进 buffer，EGO 数据仍 frozen。

### A6. RLPD：旧经验有效，需要 critic 与抽样同时可靠

[FACT] §4 将 offline/online batch 各取一半，结合 critic LayerNorm、ensemble 和高 UTD；LayerNorm 限制对状态动作输入的无界外推，并不直接要求策略接近 BC。其理论 bound 对固定参数的网络输出成立，不是训练过程中参数和 Q 都永远有固定上界。

[FACT] §5.1 的窄 expert Adroit 数据中移除 LayerNorm 会出现性能崩溃；Fig.10—11 说明持续对称采样不同于只在开头填充 buffer，Fig.8 又显示 clipped double Q 等选项存在任务依赖。[原文](https://arxiv.org/abs/2302.02948)

[JUDGMENT] 可用于提出 critic 外推/拟合与成功样本稀释的检查。它不保证旧任务保持，也未证明本项目 on-policy V critic 正在发生同类 Q 外推。官方 50% 或 ensemble 数不能直接照搬；off-policy 替换成本高，已有 critic 数据诊断成本低。

### A7. Cal-QL：初始能力高不代表价值尺度已经正确

[FACT] §4 的诊断显示 CQL 在 offline 阶段低估 Q，切换 online 后新坏动作可能相对显得更好，能力先下降再恢复。校准定义为对参考策略 $\mu$，$\mathbb E_{a\sim\pi}Q_\theta(s,a)\ge V^\mu(s)$。在 CQL 保守项中改为

$$\mathbb E_{s\sim D,a\sim\pi}\max\left(Q_\theta(s,a),V^\mu(s)\right)-\mathbb E_{(s,a)\sim D}Q_\theta(s,a).$$

[FACT] Table 1 的 final score 在 11 个任务中的 9 个领先，Table 2 的累计 regret 在 8/11 最低；§5 明确神经网络/梯度优化不能保证每个状态动作都满足校准条件，§6 理论采用理想化 finite-horizon/bilinear 条件。[原文](https://arxiv.org/abs/2303.05479)

[JUDGMENT] 适合提醒“高分成功存在”仍须检查 critic 排序与尺度。但它校准的是 CQL 保守目标中的 Q，不是直接 clamp 当前 PPO 的 V 或 advantage。迁移成本高；本项目没有 CQL 初始化，不能把其特定 unlearning 原因认定为本项目根因。

### A8. IBRL：提高混合系统表现与 RL 自身能力要分开

[FACT] §4 明确最终输出为 hybrid policy，执行时在 BC 与 RL 候选中按 critic 选动作；bootstrap target 也比较两者：

$$a_t=\arg\max_{a\in\{a_{\rm BC},a_{\rm RL}\}}Q(s_t,a),\quad y_t=r_t+\gamma\max_{a'\in\{a'_{\rm BC},a'_{\rm RL}\}}Q_{\rm target}(s_{t+1},a').$$

[FACT] §5 在 Robomimic/Meta-World 与共享实现细节的 RLPD+ 比较；例如 Can 100K 样本下有显著效率优势。Table 1 的机器人回合长度缩短属于该混合系统结果；论文同时指出 BC Gaussian 在 Square 的局限。[原文](https://arxiv.org/abs/2311.02198)

[JUDGMENT] 可借鉴训练中利用高质量候选与目标，但其部署动作选择会改变论文对象。当前目标要求 RL 同一策略执行，不能把 BC 救回的成功称作 LoRA PPO 已恢复能力，也不能直接按该式增加外部选轨迹控制器。该路线工程/归因成本高，当前优先级低。

### A9. DPPO：两层 MDP 与动作信用需要逐项对应

[FACT] §4 把环境决策与 denoising transitions 构成两层 MDP；高斯 reverse transition 的似然可计算，环境状态 critic 估计 GAE，再乘 denoising 折扣：

$$\hat A_{t,k}=\gamma_{\rm denoise}^{k}\hat A_t^{\rm GAE}.$$

[FACT] App.A.1 主实验不使用固定预训练策略正则；App.C.2 比较环境状态 critic、含 denoising-action 的 critic 和 Q，后两者未普遍优于前者。App.B 提供较大 batch、任务相关 clip fraction 等建议；App.C.1 中把 RLPD/Cal-QL 也换成 diffusion 并未普遍解决困难操作任务。[原文](https://arxiv.org/html/2409.00588v3)

[FACT] 官方 `diffusion_ppo.py` 先切 `reward_horizon` 再对动作与时间维 logprob 取 mean；可选 BC loss 在当前访问状态上由冻结 base policy 采样，再最大化当前策略对教师链的似然。这个可选分支存在不等于主论文使用，也不等于本项目已经实现。

[JUDGMENT] 项目应该首先核对已有 prefix/tail/full 信用与实际 H4/计划 H8 的对应。八步 PPO 不自动错误：计划尾段本就参与 reward；它也不自动等同上游“执行片段”方案。必须按新奖励对计划与实际控制的作用解释。迁移比较成本低至中；不为照搬论文而改冻结 H4。

### A10. FDPP：固定 BC 约束有保持与适应的真实取舍

[FACT] §IV-C 用固定 pretrained diffusion policy 的 KL 约束新偏好微调，并用 reverse-transition KL 之和界定最终动作分布 KL：

$$D_{\rm KL}(\pi_\theta\Vert\pi_{\rm pre})\le\mathbb E_{\theta}\sum_k D_{\rm KL}\left(p_\theta(a^{k-1}\mid a^k,s)\Vert p_{\rm pre}(a^{k-1}\mid a^k,s)\right).$$

[FACT] §V-D 展示小 KL 权重下更易改变偏好但旧任务表现下降，强权重又限制适应；Table II 中 Push-T 成功率仍由 98% 变 90%，另两个 Stack 偏好提升。其 learned preference reward 没有直接包含原任务完成目标，和本项目 +100 到达设定不同。[原文](https://arxiv.org/html/2501.08259v1)

[UNCERTAIN] v1 式20—21 在最大化目标中写 $+\alpha\,KL$，与约束偏离的文字目的存在符号矛盾。本次未核实作者训练源码，不照抄该符号，也不把“保持”概述解释为旧能力零损失保证。

[JUDGMENT] 固定 BC 正则是训练候选，需限定保护什么状态、何种成功能力，并比较复杂任务是否被约束抹平。增加参考策略前向和链 likelihood，成本中至高；不能作为执行时 BC 救场。

### A11. ReinFlow：少步流策略的概率与探索路线

[FACT] 正确 ID 为 2505.22094。§4 给 flow integration 加可学习噪声：

$$a^{k+1}\sim\mathcal N\left(a^k+v_\theta(a^k,t_k,o)\Delta t_k,\sigma_{\theta'}^2(a^k,t_k,o)\right),$$

并用完整噪声链的 joint log likelihood 做 policy gradient。式7 是 joint chain probability，不是最终 action 的 marginal probability；式8—9 提供利用 latent chain 求 policy gradient 的理论。

[FACT] §5—6 在 locomotion、Kitchen、Robomimic 展示少步微调；噪声过小限制探索，W2 约束过强限制超过 BC。§7 指出 on-policy 的 sample 成本、噪声幅度敏感性及当时模型规模限制。[原文](https://arxiv.org/abs/2505.22094)

[FACT] 读取的官方 `ppoflow.py:259` 会 clamp 中间均值，`:368` 又 clamp 最终动作，并计算 Gaussian logprob。因此理论对无额外截断的 joint chain 的精确性，不能未经核验直接赋给含动作截断的工程分布；边界概率与采样/似然一致性需另外检查。

[JUDGMENT] 它适合后续独立 FM 强化学习路线研究，不能作为当前 DDPM/LoRA PPO 的参数开关。新增 noise network、采样/似然/部署一致性与 FM/CFG/SFP 兼容核验，成本高；上游 clamp 也不能授权项目外部重写轨迹。

### A12. Beyond Imitation：分组规划评分有价值，也有闭环边界

[FACT] §IV 在同一观测下采样 16 条计划，直接用当前深度构成的局部 2D occupancy/inflation grid 在内存评分，不执行这 16 条候选；GRPO 优势为

$$A_i=\frac{R_i-\overline R}{\operatorname{std}(R)+\varepsilon}.$$

[FACT] 冻结视觉编码和较低 decoder，更新上层/action head；Table II unseen SR 为 0.520→0.587，Table VI 真机为 10/20→14/20。§VII 承认 reactive 策略缺全局 routing 与细致 embodiment 能力。其 reward 用计划终点到达而测试用真实执行，不能直接当本项目 safe-arrival 保证。[原文](https://arxiv.org/html/2603.12868v1)

[UNCERTAIN] §IV-D 声称无 KL 消融支持选择，但展示的 Table III—V 未提供 KL 开/关比较；式3 的 notation 把 chain joint 与最终轨迹 marginal 混用，需核实 latent-chain 更新实现。本次未获得已验证官方关键源码，不据此宣称可直接迁移。

[JUDGMENT] 可借鉴同观测比较多计划、冻结表征与检查 surrogate 误差；3D UAV 的 H4 重规划、遮挡、恢复与长时到达需独立闭环验证。16 倍候选采样和评分增加成本；不能以局部高分计划替代完整执行证据。

### A13. Immiscible：增加模式频率不等于改善安全到达

[FACT] 2026-10-07 预印本研究监督 diffusion training；warm-up 后将 minibatch 标准化动作与既有高斯噪声做 Hungarian assignment：

$$\pi^*=\arg\min_{\pi\in\mathcal S_B}\sum_i\|\widetilde a_i-\epsilon_{\pi(i)}\|_2.$$

[FACT] 不重采 demonstrations、不改 architecture/test sampler；Table I 的 Push-T 非主模式频率由 2.4% 变 35%，但其他任务也有成功率下降，例如单 seed 人形 Fruit-to-Plate 75%→60%、Place Shoe 100%→93.33%。limitations 明确恢复模式的成功率可能较低。[原文](https://arxiv.org/html/2610.09369v1)

[JUDGMENT] 它支持检查同观测噪声到路线模式的敏感性，而不证明本项目退化是 mode collapse。该机制不是 PPO 后期旧成功保持方案；若研究，须另建 BC 训练身份、保留 frozen 数据、考虑 $B^2$ cost matrix/assignment 成本和激活时点，成本中至高。当前近目标过冲/盘旋应先查真实控制与更新证据。

## 4. 官方 GitHub 关键源码核验

[FACT] 本次使用 GitHub 插件 `fetch_file` 获取完整文件后阅读关键计算，不把 README 当作实现核验。新原件以 UTF-8 `.py.txt` 保存，避免它们成为项目活动入口；保存过程属于原件自动归档，未改活动源码。Git blob SHA 与本地 SHA256 在 `github_source_inventory.json`；默认 branch URL 可能以后变化，blob SHA 和原件固定本次读取的内容。

下表中 `O/` 代表 `论文/被参考/2026-10-12_RL_Reward综合研究/algorithms/`，`E/` 代表 `论文/被参考/2026-10-12_BC成功能力保持_文献与官方源码/`。

| 官方项目 | 实际读取与保存 | 核实的关键计算 | 对项目判断的限制 |
|---|---|---|---|
| [DPPO](https://github.com/irom-princeton/dppo/blob/main/model/diffusion/diffusion_ppo.py) | `O/DPPO_diffusion_ppo.py.txt:97`、`:105`、`:129` | reward_horizon 切片、logprob mean、教师链 BC loss、标准化/分位裁剪、denoising discount | 本项目 H8 片段位置不同；官方可选项不等于本项目可用开关 |
| [RLPD](https://github.com/ikostrikov/rlpd/blob/main/rlpd/agents/sac/sac_learner.py) | `O/RLPD_sac_learner.py.txt:106`、`:220`、`:255`；`E/RLPD_train_finetuning.py.txt:184` | LayerNorm 参数传递、ensemble target、UTD 多次 critic/一次 actor 更新、offline/online batch 合并 | constructor 默认不证明实验已经启用该配置；off-policy Q 不能等同 PPO V |
| [Cal-QL](https://github.com/nakamotoo/Cal-QL/blob/main/JaxCQL/conservative_sac.py) | `O/CalQL_conservative_sac.py.txt:228`—`:240` | mc_returns 构造 lower bound，对 CQL policy action Q 正则中的值取 maximum | 不是对所有 Q 输出或部署动作做 clamp，更不是直接给 PPO advantage 设保底 |
| [IBRL](https://github.com/hengyuan-hu/ibrl/blob/main/rl/q_agent.py) | `O/IBRL_q_agent.py.txt:253`—`:295`、`:417` | BC/RL 两动作，critic argmax；eval_mode 仍可能选 BC；target update 重用 IBRL 选择 | 混合执行的成功不可归因为 RL 独立行为 |
| [ReinFlow](https://github.com/ReinFlow/ReinFlow/blob/release/model/flow/ft_ppo/ppoflow.py) | `O/ReinFlow_ppoflow.py.txt:254`—`:275`、`:363`—`:372` | learnable noise、高斯 transition logprob 的维度求和；截噪声/最终 action clamp | 无截断 joint probability 理论与含截断工程采样须区分；没有 UAV 迁移验证 |
| [rliable](https://github.com/google-research/rliable/blob/master/rliable/library.py) | `O/rliable_library.py.txt:114`—`:123`、`:126` | task strata 中 run 重采样，另有独立样本 bootstrap 类 | 默认维度假设不是自动理解 UAV world/task/repeat 配对关系 |
| [AWAC/rlkit](https://github.com/rail-berkeley/rlkit/blob/1bfe7d983bbe32c997462a0cfd8aeab20c44e2a4/rlkit/torch/sac/awac_trainer.py) | 复用 `E/AWAC_awac_trainer.py.txt:572`、`:624`—`:644` | Q−V 的 score、温度/归一化选项、detach 权重后的负 log likelihood loss | 该 trainer 有多种分支，未执行上游完整实验配置；不宣称任意默认分支复现论文 |

## 5. 跨论文综合：为什么高分成功仍可能丢失

### 5.1 四层证据不要混为一层

[JUDGMENT] 依次区分：①完整 reward 是否正确偏好安全到达；②在当轮循环规划状态下，正确控制是否获得合适的 return-to-go/advantage；③这些样本是否进入更新并保留梯度；④共享参数更新后，其产生概率及完整闭环成功是否提高。论文分别提供其中的机制或局部实验，没有“①成立必然推出④”的一般保证。

[PROVEN，代码公式条件下] 当前 R1 每回合进展总和不超过 10，单次风险在 [0,1]，时间为 −0.05，预算最多 60。故未折扣成功回报至少 $100-60-3=37$；60 次超时回报至多 $10-3=7$。这是有效回合、当前固定公式下的粗下/上界，说明完整未折扣评分对成功有明确偏好；不保证 critic、折扣目标或实际动作更新正确，也不取代真实轨迹重算。

[FACT] 当前 GAE 直接 trace 权重为 $(0.99\times0.95)^l=0.9405^l$；隔 10/20/40/59 次决策分别约 0.5415/0.2932/0.0860/0.0268。相同距离下纯 reward discount $0.99^l$ 为 0.9044/0.8179/0.6690/0.5527。这些是公式计算，未声称所有终点奖励的完整学习作用只有这些比例：critic 的各步 TD 项可补充未来成功信息。

[JUDGMENT] 因此“成功整体约 108、超时约 6”的实例与近目标失败并不矛盾。需要观察关键决策的 $V_t$、$\delta_t$、raw/normalized advantage、成功样本出现频率及实际梯度贡献，而不直接推出终点系数太小或 RL 必然先丢旧能力。

### 5.2 当前优先核查的具体问题

| 问题 | 现有证据已经说明什么 | 仍需用项目证据辨识什么 |
|---|---|---|
| 近目标过冲/盘旋 | 简单场景存在清障后未入目标球、progress 不再增加的原实例 | 当前状态/速度/yaw、H4 实际位移、计划 H8 的目标最近点、normalizer/denoising clip 与更新后的动作敏感性；不能凭恒定位移就定因边界饱和 |
| 稀疏到达信用 | GAE trace 会衰减，critic 应提供未来价值 | 接近目标的成功/超时是否被 critic 区分；相同局部奖励是否被错误 value 赋同样优势 |
| 时限 | 当前代码把 timeout 当 external truncation 并 bootstrap | 优化目标是可无限继续的到达，还是“60 次内到达”；后者要讨论 remaining-time 状态与有限时域 target，前者要诚实解释预算评价差距 |
| history/尺度 | critic 显式接收 $b/D_0$，actor 保持原条件 | 若 reward 仍依赖 $D_0$ 与 remaining budget，现有条件是否足以区分其未来回报；不要仅看变量名判断 Markov 完整性 |
| 八步信用/四步执行 | 风险包括计划尾段，PPO 更新八步片段，已有切片诊断 | prefix 和 tail 是否对学习目标贡献一致；未执行尾段是否压过实际近目标控制；改变 horizon 需独立比较，H4 不动 |
| 能力保持与新增 | 旧统计能区分保留、丢失、新增，用户允许取舍 | 新 v3 判据下重新配对后总体和复杂场景是否净提升，简单任务失败是否仍集中于特定控制阶段 |
| 多任务梯度冲突 | 共享 LoRA 可能同时影响多类状态；这是机制候选 | 成功/近目标/密集绕行样本在同一更新的梯度方向及下一轮行为变化是否支持干扰解释；未测不能定因 |

[JUDGMENT] 检查应优先复用已有 `training_audit`、rollout arrays 和 prefix/tail/full 指标。若现有证据缺关键值，再以最少修改补到已有采集/分析入口；不为每个 seed、update 建一套程序。

### 5.3 稳定与学习同时成立才有意义

[FACT] 项目 loss 对优势标准化，对 logprob clamp 后取 mean，并有梯度门限。若所有 rewards 与已匹配 values 同比乘常数，标准化优势大体保持不变；这不等于只增终点奖励完全没有作用，后者会改变相对优势结构。论文 A1/A2/A9 支持“真实更新依赖尺度和实现”这一检查方向，不能据此替换本地梯度证据。

[JUDGMENT] 增大 KL、缩小 clip/LR、裁优势/降低探索噪声时，需同时检查：实际 actor update、成功条件下正优势与梯度、动作多样性、复杂场景新成功与近目标到达。数值曲线平滑且成功样本贡献接近零应标为“学习信号被抹平”；不能通过删除困难 rollout、旧失败或新空间样本获得表面稳定。

## 6. 项目候选与优先级：研究依据不是已批准方案

| 候选 | 适用前提与目的 | 成本、主要失败模式、可测观察 | 当前判断 |
|---|---|---|---|
| C1：明确预算目标与 critic 条件/target | 若要优化 60 次内到达，检查 remaining time、$D_0$、history 的可辨识性与终点语义；借鉴 A2/A9 的 advantage 实践 | 低至中。风险一：时限语义改错造成有偏 target；风险二：新增状态仍不解决 actor 近目标控制。观察分阶段 value/return、接近目标后超时比例、完整 safe-arrival | 优先研究，当前384不改；现有 bootstrap 实现不能直接标 bug |
| C2：先辨识更新与近目标控制，再校准 reward | 用当前完整成功/超时、循环计划与执行证明局部信用缺口；与另一 reward 研究材料合并 | 低至中。风险一：只惩盘旋同时惩必要脱困绕行；风险二：近目标奖励可被反复刷分。观察新best/velocity/H4 控制、成功/超时优势和困难外绕成功 | 优先研究，不能先认定终点加分不足，不给未经批准系数 |
| C3：训练内有选择的固定 BC 参考 | 在训练域中保护确实有效的控制，同时允许 BC 失败/OOD 状态改变；A9 可选教师链/A10 的固定KL作为机制线索 | 中至高。风险一：教师在新空间本身无效；风险二：约束抹掉复杂避障梯度。观察参考项梯度与PPO梯度、BC偏离、旧成功保留、新增复杂成功；需要独立RL actor评价 | 备选，当前BC loss未实现；不以全状态强保持精确路线作为默认 |
| C4：持续旧经验训练，AWAC/RLPD/Cal-QL路线 | 当前训练域有效状态动作确实稀缺，且同意改成 off-policy 学习体系 | 高。风险一：高维chunk Q估计错误；风险二：旧数据/保守项限制新空间探索。观察critic校准、数据来源/年龄、抽样率和实际闭环成功 | 后置候选；不是给当前PPO添加一个replay开关 |
| C5：同观测多计划GRPO | 能证明3D计划评分与H4重规划后的长时结果一致，并承担多候选采样 | 中至高。风险一：局部无碰撞计划不能保证后续脱困；风险二：组内相对优势提高坏候选中的“相对较好”。观察评分与完整执行回报关联、同组方差/梯度、safe-arrival | 仅研究候选，A12没有解决本项目长时信用证明 |
| C6：独立ReinFlow/FM路线 | 策略核心与采样概率重新设计，保持FM FP32和冻结推理契约的要求 | 高。风险一：探索噪声破坏精准到达；风险二：clip/likelihood或train/deploy语义不一致。观察核验一致性、时间成本和完整到达 | 不替换当前DDPM训练；需独立设计与来源核验 |
| C7：监督模式保留/Immiscible | 已证实BC或新训练的同观测模式覆盖不足，愿意研究新的BC训练身份 | 中至高。风险一：恢复频率但不恢复成功；风险二：噪声匹配与任务条件产生非预期耦合。观察模式频率与模式条件成功率、总体safe-arrival | 非当前默认路线；不得把近目标退化直接称mode collapse |

[JUDGMENT] 当前最小路径是完成 frozen384 的原版本证据保存/独立验收，按 v3 统一入口重新采 BC 与 RL，然后结合上述 C1/C2 的已有证据决定下一设计。不能因文献展示其他场景收益，就在当前训练中途切换 reward、bootstrap、reference loss 或算法。

## 7. 方法约束与归因核验

| 约束 | 本材料判断 |
|---|---|
| MC-1，输出即执行 | 不提出外部轨迹裁剪、重写或纠偏；IBRL hybrid 只作归因边界例子 |
| MC-2，diffusion/flow策略核心 | 训练内正则/信用候选可讨论，算法切换须独立设计，不把BC控制器救场称RL提升 |
| MC-3，学习阶段约束 | 候选机制放在训练公式、状态、采样/信用中，不在inference后替策略改路径 |
| MC-4，数据frozen | 复用已有数据不等于重采示范；新实验仅训练世界，eval-only世界不得训练或replay |
| MC-5，归因可分离 | 单一RL actor的完整轨迹评价，保留原件/运行身份；总体与简单/复杂、保留/新增分别报告 |
| H4与空间允许 | 实际执行H4不改；xyz扩展允许，旧人工空间终止暂是冻结训练代码条件，不冒充物理禁飞 |
| 有效学习信号 | 不以丢困难样本、强参考约束或曲线平滑替代复杂场景能力提升 |

## 8. 归档状态与可追溯性

[FACT] 13 篇论文中复用 11 份原件，新保存 `StatisticalPrecipice_2108.13264v4.pdf` 与 `Replay_ICML2020.pdf`。Replay 的 arXiv PDF 下载发生 SSL handshake timeout，已改用经网页核实的 PMLR 官方 publisher PDF；失败历史在 papers.json 保留，最终没有未取得原文的计数项。六份新 GitHub 源码均保存成功；另复用两份既有 AWAC/RLPD 官方源码。

[FACT] PDF 用现有 pypdf 文本抽取生成阅读副本；HTML 阅读副本保留 MathML `alttext` 公式，跳过脚本/样式内容。抽取副本不是论文原件，表格/公式以 PDF 或 HTML 原件为准。未安装依赖，未新增活动执行程序，未接触 WSL。

[UNCERTAIN] FDPP、Beyond Imitation、Immiscible 的作者官方训练关键源码未在本次任务中验证；其结论只按已读论文证据引用，明确不纳入“官方代码已核验”计数。本文不声称全部上游仓库可完整复现，也不把 branch 快照当完整环境验证。
