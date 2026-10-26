# Route A：Reward主因假设与其他退化原因——调试资料补充

| 字段 | 内容 |
|---|---|
| 日期 / 版本 | 2026-10-13 / v1.1 |
| 任务 | 回答reward主因及其他候选；补充“越过目标后恢复”和H8规划/H4执行的原轨迹检验、相关论文及官方实现 |
| 证据 | 已完成的原轨迹/训练分析；本轮直接核查正式R1配置、update1原metrics、critic构建与调用；重新检索论文及5份教学/经验资料，GitHub读取CleanRL完整关键文件 |
| 边界 | 不改变当前384训练，不修改活动源码/参数，不启动WSL；原因假设不冒充因果验证 |

标注：`[FACT/PROVEN]`为原件/代码事实及重算；`[SUPPORTED]`为有证据支持；`[HYPOTHESIS]`为待实验原因；`[JUDGMENT]`为判断。

## 1. 先回答用户：reward仍然是有力的主要原因候选

[JUDGMENT] **没有证据排除reward是主因。** “成功约107、超时约5”只能排除已见轨迹的严重整回合错序，不能证明局部信号适合当前H8规划/H4执行、有限样本和当前critic学习。若此前用完整成功高分去降低reward调试优先级，这个推论过强。

[SUPPORTED] 当前reward至少有两个具体疑点：目标附近历史best不再刷新时，返回/离开/停滞可同为−0.05；newbest只付款新进展，不直接区分同进展下的有效路径与低效摆动。它们与原轨迹过冲、盘旋一致，但尚未确认是整个GAE和更新失败的唯一来源。

[PROVEN] task5五次重复：BC前10轮newbest累计0、u256约8.359—8.409，但BC最终5/5成功、u2560/5。task6 u32/u256前10轮约6.942—7.037/6.901—6.915，结局分别5/5与0/5。这个结果支持研究“早期推进如何转成最终入球”，不证明早期推进动作本身是坏动作。

[JUDGMENT] reward与其他机制并非互斥。newbest引入历史状态，critic需要相应信息；改reward可减少某些状态依赖，补critic也可改善其学习。需要比较哪种改动能修复行为，而不是争论把配合不足全部归入哪一个名称。

## 2. 其他原因：具体机制、项目论据与未证实部分

### 2.1 critic信息不足或起步尚未适应

[PROVEN] 当前critic只有beta=b/D0，缺少初始距离尺度。相同观察/beta，D0=10/b=5与D0=8/b=4，下段最近到4.5m，reward分别0.45/−0.05。确定的是输入歧义，不是全环境失去Markov性或已定因全部失败。

[FACT] 本轮核查正式resetfix seed203配置没有`run.critic_warmup_updates`；当前pipeline默认0。R1构建函数新建价值网络（与A0随机初始化对齐，并非加载训练好的BC价值网络）。原`metrics_update_000001.json`有40次实际提交，全部`pre_update.actor_updated=True`：actor从首轮便与critic共同更新。首批value_loss约259.421，不能仅由这个单值宣布critic失效。

[HYPOTHESIS] 已经有可用BC actor，但刚初始化/信息不全的critic提供了不可靠优势，导致早期有益行为被不适当改变，之后进入新的状态分布。它能解释高分成功存在却没被稳定保持；需要原reward下补信息或单独critic适应的比较，不能认定预热必然有效。

来源：`chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/engine/{critic_state.py:8,initialization_parity.py:40}`、`entrypoints/{build_system.py:72,pipeline.py:144,563}`；原件`wsl_snapshot/20261009_185302_routea_r1_resetfix_s2_3seed256_run01_pack/configs/train_e5_dppo_r1_s2_seed202609203_resetfix_v1.yaml`与`outputs/seed202609203/metrics/metrics_update_000001.json`。

### 2.2 更新与训练状态分布改变，未持续训练旧有效控制

[FACT] 当前训练不使用固定BC loss；PPO相对本轮采样旧策略约束更新，未对固定BC行为设保证。LoRA虽不改base参数，仍改变组合策略。训练含20%概率位置扰动、30% mid-state；本次配对评价关闭这些机制。

[PROVEN] 50对首轮输入/seed相同的BC/RL输出确实不同；task6 u32和u256初始H4偏移量级近似，而后续成功不同。一般偏移量不能独自定位问题，需要观察近目标状态下的控制响应。

[HYPOTHESIS] 共享LoRA在新状态/困难样本上的更新同时影响简单控制，成功入球状态未得到足够、正确的持续更新。有效保持失败是已见现象；是梯度干扰、数据覆盖还是信用错误仍未区分。没有BC正则并非程序错误，DPPO主论文也不把固定BC约束作为必要条件。

### 2.3 训练价值目标与60轮内完成的评价目标可能不同

[FACT] 60轮timeout仍bootstrap；原u128:t277 reward=−0.05、next_value=24.34178，target=−0.05+0.99×24.34178=24.04836，raw优势为+5.86748。它是训练中另一任务，不能冒充task7评价优势。

[HYPOTHESIS] 若研究真正要求60轮内完成，而value仍估计60轮后的继续价值，迟到或反复返回可能保留较高训练target。这是目标/时间状态问题；若60只是采集截断，bootstrap应当保留，不能直接关掉。

### 2.4 H8联合更新与H4实际控制、采样对目标的响应

[FACT] 当前scalar advantage作用于8×11平均logprob，prefix和tail共享信用；已记录prefix/tail诊断。task7近目标阶段y增量重复约−0.205954，实际未入球。native scheduler clip存在，不等于已证明该重复值是clip饱和。

[HYPOTHESIS] 部分tail改善与执行prefix改善不同步，或采样/模型在近目标不能及时缩小/改变步幅。即使新reward评分更清楚，若对应实际动作的梯度或控制响应很弱，仍可能失败。先核现有真实采样与切片，不直接改H4/Action11或增加轨迹后处理。

## 3. 网上资料能带来什么：不是用别人结论代替我们定因

| 来源 / 类型 / 本轮读取 | 与本问题直接相关的内容 | 可迁移作用 / 限制 |
|---|---|---|
| [Bootstrapping RL with Imitation for Vision-Based Agile Flight](https://arxiv.org/html/2403.12203v3)，CoRL2024，§3/§4/App.A | 普通预训练策略微调先改善后退化；critic-only适应、表现相关更新与非对称critic有收益 | 支持在reward保持相同时研究critic/更新。竞速、视觉及控制任务不同；不迁DAgger重采，也不直接抄可能负/近零分母的回报比 |
| [Implementation Matters](https://arxiv.org/abs/2005.12729)，2020；[What Matters in On-Policy RL](https://arxiv.org/abs/2006.05990)，2020预印本 | PPO实现、优势、数据组织及学习率选择能改变实际表现 | 检查真实优势和提交，不把loss/EV好看当控制正确；MuJoCo消融不证明本项目哪项出错 |
| [The Perils of Trial-and-Error Reward Design](https://doi.org/10.1609/aaai.v37i5.25733)，AAAI2023 | 局部动作好坏不等于累计任务规范；reward可对算法/超参过拟合 | 同时核完整路线、循环分数和算法如何学习；支持调reward，但不是加更多项的证明 |
| [DPPO官方loss](https://github.com/irom-princeton/dppo/blob/main/model/diffusion/diffusion_ppo.py)；[CleanRL PPO](https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo_continuous_action.py)，实际源码 | horizon切片、logprob处理、批优势归一化、ratio/clip和实际loss | 用作对应计算核对；CleanRL此文件合并term/trunc，不能照抄其timeout逻辑来修本项目 |
| [37 PPO Implementation Details](https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/)，2022作者技术文 | 明确优势在minibatch归一化，另有数据/target与loss实践 | 支持我们已发现后验审计≠实际批优势；文章也报告归一化位置未普遍显著影响表现，不因此宣布当前归一化是根因 |
| [SB3 RL Tips](https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html)，官方教学 | 信息充分、timeout、shaped reward、简单问题起步、独立评价和wrapper影响 | 保留简单到达诊断与难任务评价；项目已有normalizer，不叠新的变换，不复制普通Gaussian动作clipping |
| [Andy Jones：Debugging RL Systems](https://andyljones.com/posts/rl-debugging.html)，2021第一手经验 | 用小问题区分价值拟合、延迟回报、策略选择；全局loss曲线不能定位 | 复用已有检查和同状态探针定位，不新增五套程序；经验范围/entropy解释不是通用规律，DPPO固定噪声需单独判断 |
| [Gymnasium Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)，官方教学 | 固定任务期限与外部采集截断不同；前者需要剩余时间信息，后者bootstrap | 明确60预算的研究目标，避免只给timeout加罚却继续估计另一个目标 |
| [Spinning Up：研究实践](https://spinningup.openai.com/en/latest/spinningup/spinningup.html)，官方教学，2018 | 分开验证设计决策、报告预定最终实验 | 为因果比较服务，不将其计入32篇2020—2026论文，也不要求扩大工程流程 |

[FACT] 5份教学/经验完整网页和CleanRL完整文件已存`论文/被参考/2026-10-13_RL调试教学与经验/`；源码Git blob `b454521b6e4a08d4a2f5ecec405132776f5e79eb`匹配，URL/日期/SHA见inventory。论文原件及DPPO源码复用既有资料，不重复计数。

## 4. 对我们最有用的选择

[JUDGMENT] 可以把reward局部恢复/入球反馈列为首要调试假设；同时将已证实的critic尺度缺口作为共同风险。改变reward和补critic如果同时完成，就只能报告共同方案效果，不能再宣称只由reward造成。

[JUDGMENT] 最少的判别是：原v2下只补critic D0；固定同一critic条件后只加恢复势能；选择性BC参考另对同一基线比较。critic-only适应可利用现有训练入口形成独立候选，但不能与补D0、reward及学习率同时新改。预算/学习率与是否补偿actor更新机会必须明示，否则预热实验也混入训练时程变化。

[JUDGMENT] 结果应区分：恢复反馈改善说明其对当前训练有实际效用，不自动证明它是原退化唯一原因；原reward下仅改critic/更新也能恢复，说明仅调reward不是唯一必要途径。两者都改善可能表明相互作用，而不是只能选一个主因。

[UNCERTAIN] 目前未取得task7评价的真实训练优势/净GPU梯度，不能宣布“reward无问题、PPO一定弄坏”；也不能宣布“改局部评分就一定恢复”。当前384继续原版本，训练后按统一新评价验证。

## 5. 新增原轨迹分析：是否因为只执行前四步而无法返回

### 5.1 范围与判定方法

[FACT] 本次直接读取seed202609203 R1 u256全部420份原始JSONL，共13411轮规划；再逐轮比较既有75条BC/u32/u256轨迹，共2520轮。没有重新运行策略，没有写新评价入口，也没有修改原件。分析仍属于原有限域协议；本seed这420条的结局为101到达、139超时、180碰撞，没有空间边界失败。

[FACT] 每轮分别读`planned_policy_path`的H8、`executed_path`的H4和下一轮实际执行路径。75条中的全部非终止轮，实际路径与记录的计划前四段逐元素一致，最大偏差0。当前转换代码`diffusion_policy_3d/env/traj_utils.py:48`用world位置增量累加；轻量环境不强迫无人机先转180度才允许反向位移，也未由惯性积分决定下一位置。不能把本次失败直接称为飞行器物理上调不了头；PX4闭环需另外验证。

[FACT] “返回”在此仅指H4终点三维目标距离比轮初减少超过0.05m；“后段才返回”指H4终点远离超过0.05m，而H8终点相对H4减少超过0.05m。这是描述性阈值，不是新reward或成功判据。“越过目标平面”指实际点满足$(p-g)\cdot(g-s)>0$，不等于进入目标球。

[FACT] H8是否安全到达，用现有`reward_v2_support/first_event.py:81`对原计划八段作连续首次事件检查，保留障碍、触地及历史空间规则。只有首次事件为到达、且位于第5—8段才计为“目标位于未执行后段”。参数为目标半径0.5m、碰撞扩展0.1m、z_max=5m，与该原评价合同一致；当前统一入口`runtime.py:177`核对H4/H8/0.3s/0.1m。将八段送入几何检查只是既有计划的反事实检查，不构成新H8执行实验。

### 5.2 用户的假设在部分案例中成立

[PROVEN] 139条超时中，**4条曾在H8未执行后段规划出安全进入目标球的路线，共6轮；下一轮H4均未到达，最后均超时。** 其余33条成功轨迹也出现过这类后段目标计划，共41轮。因此“计划有到达路线、重新规划后未兑现”确实存在，但不能把出现该现象直接等同必然失败，也不能按4/139估计H4对全部失败的因果贡献。

[PROVEN] 具体例子：S-turn world44、cfg00、repeat2，第48轮（JSONL `decision=47`）开始距目标0.899094m；执行H4后为0.507755m；原H8第5段就会安全入球，整段计划最近0.403125m。下一轮实际终点却远离到1.354168m，最终超时。第44轮（decision43）的另一原计划也会在后段入球，但下一轮实际只到0.629736m。

![原计划后段入球但下一轮偏离](C:/Users/cjj/Desktop/IDP3/论文/研究报告/2026-10-12_RL_Reward深度研究_材料/h4_h8_deferred_goal_world44_20261013.png)

[PROVEN] 全139条超时中，70条实际越过了目标平面；这70条全部至少有一次越过后实际H4重新接近目标。**它们不是完全没有返回动作，而是返回没有可靠转化为三维入球。** 其他超时不得都解释为过冲。全420条有495轮呈现“先远离、后段再接近”，其中59轮起始距目标不超过2m；它们包含正常绕障、转弯和失败，不能统一扣罚。

### 5.3 简单退化案例的主表现与上述四条不同

| 原任务；每项5次重复 | BC / u32 / u256到达 | u256实际H4接近目标轮数 | u256前段远离、后段接近轮数 | u256既有H8能安全入球轮数 | 实际最近三维距离 |
|---|---|---:|---:|---:|---|
| task5 | 5 / 5 / 0 | 145/300 | 6/300 | 0/300 | 0.907—0.935m |
| task6 | 5 / 5 / 0 | 171/300 | 1/300 | 0/300 | 1.207—2.053m |
| task7 | 5 / 5 / 0 | 161/300 | 2/300 | 0/300 | 1.128—1.171m |

[PROVEN] 这15条u256都越过目标平面，实际900轮有477轮重新接近目标。“后段才返回”仅9轮，其中8轮下一次实际H4也重新接近目标。轮初已在2m内的63轮中，没有上述“前段远离、后段接近”的形态。这不支持把这15条主要解释为回头动作一直留在后四步。

[PROVEN] task5最近点的**水平误差0.230—0.318m，但垂直误差0.877—0.879m**；俯视图看似已到附近，三维仍未入球。task6最近点水平误差1.135—2.043m，垂直0.194—0.409m；task7水平1.098—1.145m，垂直0.250—0.262m。三个案例的误差结构不同，不能全部归为同一种“调头失败”。

[JUDGMENT] 对目前数据，更准确的描述是：**部分轨迹把可到达的后段计划在重规划时放弃；另一部分能够回来，但近目标的位移方向、幅度或高度修正没有使误差继续降到0.5m以内。** H4可能参与前一类，不能由几何影子分析证明改变H4后整个闭环一定改善。BC/u32在同一H4结构下能够到达，也说明H4没有禁止返回。

### 5.4 他人如何提供到达引导：论文与代码分别核查

| 来源；检索2026-10-13 | 实际机制 | 对我们的用途与边界 |
|---|---|---|
| [NavRL](https://arxiv.org/html/2409.15634v2)，RA-L2025；[官方env.py固定提交](https://github.com/Zhefan-Xu/NavRL/blob/3725bcc2e7c1be4ecf1455d922299ae85042603a/isaac-training/training/scripts/env.py#L556) | 每步奖励$r_{vel}=\hat{(g-p)}\cdot v$，目标方向随当前位置变化，越过后继续向外则该项为负 | 借鉴“持续看当前目标关系”，不是只有刷新历史best才反馈。源码583—595的到达为统计；到达没有加入terminated或+100，不能称其有严格到达保证。外部安全shield不符合我们的归因约束，不移植；也不抄它的高度硬终止 |
| [Tovarnov与Bykov](https://arxiv.org/pdf/2203.10519)，2022，DOI 10.1088/1742-6596/2308/1/012004 | 用当前速度和机动约束构造简化Bezier轨迹，估计到达时间；逐步奖励到达时间缩短 | 提醒“距离近但运动方向错误”仍可能难以到达。实验为简化二维动力学，非已验证三维绕障方案；不能把其终点速度要求加成我们的成功判据。轻量环境位移不按该动力学积分，暂不直接移植时间估计器 |
| [Diffuser](https://arxiv.org/html/2205.09991v1)，ICML2022，§3.2/§3.3 | 可将目标状态作为生成条件；算法1仍只执行第一个动作再规划 | 执行短前缀本身并不排除到达；关键是生成/每次重新规划持续受目标约束。它生成状态动作序列，不能把inpainting简化成对我们11D轨迹尾端强行改写；不是当前reward的直接替换 |
| [Lee等：Non-differentiable Reward Optimization](https://arxiv.org/html/2507.12977)，2025预印本，§III-D/E | 给生成计划按目标距离阈值打分，动态改变阈值以改善奖励稀疏程度 | 提供“近目标仍需有区分”的研究方向；论文对生成计划评分，未证明我们H4实际恢复。不可把它理解为放宽本项目评价半径，或对没有执行的H8入球发实际成功奖励 |
| [PBRS样本效率与有限时程研究](https://arxiv.org/html/2404.07826v2)，2024/2025版本，§2.2/§5 | 以$F=\gamma\Phi(s')-\Phi(s)$提供密集反馈；分析有限时程残项及偏差 | 可在同一次RL训练内给实际返回信用；端点处理、timeout及价值bootstrap必须一致。策略排序性质不等于有限训练预算内必然学得更好 |

[FACT/JUDGMENT] NavRL使用仿真器实际速度；我们`traj_utils.py:65—76`的下一位置由DPOS累加，VEL列另行填入，不由该速度积分产生位置。**不能直接奖励模型输出的VEL列指向目标**，否则可能奖励一个与实际位移不一致的速度输出。迁移时应依据原H4真实位移/目标距离变化；控制动力学的到达时间奖励需等PX4闭环或可信动力学模型再评估。

### 5.5 对同一轮RL训练的reward建议：先评价实际执行的恢复

[JUDGMENT] 首选候选仍是对**实际执行H4前后**的当前三维目标距离给有界势能反馈，保留成功、真实失败、风险和newbest；未执行H8中的入球不作为实际成功。这样同时鼓励水平返回和高度纠正，也避免只奖励180度掉头或奖励朝向变化却没有接近。

$$
\Phi(d,D_0)=-\frac{d}{d+D_0},\qquad r'_k=r^{R1}_k+\alpha\,[0.99\Phi(d_{k+1},D_0)-\Phi(d_k,D_0)].
$$

[PROVEN] 以下直接重算world44/cfg00/repeat2原执行，$D_0=9.2490748m$；$\alpha=4$仅作评分示例，不是批准的参数：

| JSONL决策 / 人类轮次 | 实际三维距离变化 | 当前R1 | 加候选后的总分 |
|---|---|---:|---:|
| 43 / 第44轮 | 1.686411→1.027188m | −0.050000 | +0.171027 |
| 44 / 第45轮 | 1.027188→0.629736m | −0.050000 | +0.097395 |
| 47 / 第48轮 | 0.899094→0.507755m | +0.029505 | +0.177809 |
| 48 / 第49轮 | 0.507755→1.354168m | −0.050000 | −0.347578 |

[JUDGMENT] 这使“返回”和“再次离开”在实际循环上更容易区分，直接针对用户看到的现象。不能从重算宣布训练已修复：PPO更新仍经过GAE/critic/联合动作信用。必要绕障可能暂时远离，不要求每轮必须更近；PBRS真终止势能归零、外部截断保留相应势能及bootstrap，防绕圈推导和尺度/critic要求见主报告。距离势能也不能理解成在完美critic下额外创造了新优势。

[FACT/JUDGMENT] 本次配对评价案例用于解释机制，不用于从这些案例选出最优系数；eval-only世界不加入训练或回放。新参数应在训练/独立调试范围确定，再以固定评价矩阵裁决效果。

[JUDGMENT] **当前优先级：同一RL过程内的实际恢复/精确入球反馈；保持H4并观察它能否减少两类失败。** 当前证据尚不足以优先延长每次执行为H8或引入前一条计划跟踪奖励；后者会惩罚有益重规划，尾部单独得分也可能奖励永远不执行的到达。当前384训练保持原版；以上仅供下一阶段讨论，未更改算法。

### 5.6 可追溯产物

[FACT] 分析产物在`论文/研究报告/2026-10-12_RL_Reward深度研究_材料/`：`review_h4_h8_seed203_all420_20261013.json`记录420条及原source；`review_h4_h8_goal_recovery_20261013.json`、`review_h4_h8_goal_recovery_cycles_20261013.csv`记录75条/2520轮；`review_h4_h8_goal_error_20261013.json`记录最近连续线段点的xyz误差；`review_h4_h8_six_deferred_goal_details_20261013.json`记录6轮后段入球及下一次实际执行。图中蓝实线为实际当前H4、蓝虚线为原H8未执行后段、橙实线为下一轮实际H4。

[FACT] 本次实际使用的新论文原件及NavRL完整源码存`论文/被参考/2026-10-13_目标到达与循环规划恢复/`，URL、日期、用途和SHA见inventory；固定源码提交为`3725bcc2e7c1be4ecf1455d922299ae85042603a`，Git blob匹配`a2e905a4a99b3ff5a2e25ed6212bb3943b784595`。Diffuser和PBRS复用既有已归档原件，不重复计为新论文。

主报告：[联合诊断v1.1](C:/Users/cjj/Desktop/IDP3/论文/研究报告/2026-10-12_RouteA_新旧Reward与循环规划强化学习调试_综合研究报告_v1_0.md)。
