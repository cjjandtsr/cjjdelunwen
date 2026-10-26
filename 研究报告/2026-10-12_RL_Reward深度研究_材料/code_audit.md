# Route A RL / Reward：代码、设计与测试独立审查笔记

| 字段 | 内容 |
|---|---|
| 日期 / 版本 | 2026-10-12 / v1.0 |
| 范围 | Windows当前源码、既有设计、既有研究记录和聚焦本地测试；供总研究报告合并 |
| 状态 | 只读代码审查完成；未修改生产程序、测试或配置，未操作WSL，未形成新训练参数 |
| 源码根目录（下文源码引用相对此目录） | `C:\Users\cjj\Desktop\IDP3\chengxu\Improved-3D-Diffusion-Policy` |
| 当前运行约束 | fresh384保持原版本；用户报告34/384不等于本轮读取运行日志；完成及保存原版本证据后再按v3.0指导复制评价修复 |

## 1. 可以确认的结论及其边界

1. [FACT] R1不是“缺少旧onset/trap/support字段，所以没有提前避障、恢复或空间学习”。真实执行包含连续三维几何、执行H4和计划tail H4的风险、历史最好进展、最终三维安全到达以及覆盖anticipatory/support_expansion/dense/recovery的任务采样；PPO概率比使用完整policy的8步。具体承接机制须与旧版公式区别。
2. [FACT] R1四项标量reward在环境事务内计算，经adapter直接交给rollout/GAE，没有叠加旧v1.7十四项。公式参与计算、轨迹出现局部收益、某项reward具有训练因果作用是三层不同证据。
3. [PROVEN] critic的历史扩展实际只有`beta=b/D0`；这个标量不足以唯一表达newbest奖励状态。critic也没有剩余决策预算。后者需要先裁决“60是采集截断还是任务期限”；不能直接把time-limit bootstrap判为bug。
4. [FACT] 八步信用确实覆盖tail，但一个scalar advantage也会作用于未执行tail；概率比使用8×11元素的平均logprob，而非独立地只给风险对应段分配优势。安全tail分数下降不等于实际H4行动能力提升。
5. [FACT] BC基础参数冻结与RL行为保持是不同事项。LoRA启用后会改变共享denoiser的输出；代码没有保证保留所有BC成功行为。当前训练没有BC loss，固定eta且entropy coefficient为0；原有随机采样仍提供探索。
6. [PROVEN] 本轮聚焦现有测试53项通过、退出码0。这证明既有局部合同检查通过，不证明GPU训练因果、不证明扩大空间后完整评价已完成、不证明任务7的固定y增量由native clip导致。

## 2. 真实调用链与执行/评价合同

### 2.1 训练调用

[FACT] `entrypoints/build_system.py:52-70`读取BC并在denoiser安装LoRA，`rewards/select.py:14-16`按`reward_version=v2`选择R1 facade。`environments/factory.py:201-223`构建C2、policy 8步、执行4步环境，传入facade.version；`env/kinematic_uav_env.py:738-740`直接分派`step_v2`。`environments/kinematic_adapter.py:21-36`把`action_bundle.policy`交给环境，并接受真实环境reward事务。这里的`entrypoints`/`environments`路径前缀均为`diffusion_policy_3d/rl/dppo_uav_rebuild/`。

[FACT] `env/reward_v2_support/environment.py:59-90`从8×11动作得到本轮9点计划，先查H1–H3事件，再在无事件时形成H4实际末点及噪声/扰动。若首事件在段内，提交该段分数位置、插值yaw/velocity与实际前缀。`environment.py:96-116`以实际前缀计算终止和reward，再更新best；`environment.py:118-145`仅为走过的帧生成观测并记录实际物理时间。未执行tail不更新位置、到达、碰撞、best或观测。

[FACT] `engine/contracts.py:141-169`的完整输出16×11、policy `2:10`、rollout `2:6`仍然成立。`ActionSpec.e5()`还有deployment默认2步，不能据此把当前lightweight RL的实际H4改成H2；本审查只判断当前训练/同任务评价合同，不对Gazebo执行作新结论。

### 2.2 高频首次事件和空间v3

[FACT] `env/reward_v2_support/first_event.py:81-129`沿连续执行线段寻找0.5m目标球、障碍、地面首事件，同位置容差内失败优先。`environment.py:102`仍在第60次决策检查time_limit；`environments/terminal_contract.py:86-117`让reached/真实失败优先于time_limit，并区分terminated/truncated。

[FACT] 当前`first_event.py:108-119`仍保留默认True的人工xy±30、z_max+1事件，供当前训练与历史轨迹规则使用。统一评价`scripts/routea_paired_support/runtime.py:166-179`显式置`terminate_at_space_limits=False`，统一v2/H4/8、0.3s、60次决策、碰撞margin0.1；`environment.py:63-77`两处事件调用都传入开关。测试v3不再把旧空间阈值当真实失败，也没有空间软惩罚。

[FACT] `scripts/run_routea_paired_comparison.py:82-98`仍为统一入口，读取运行时权重地址，执行smoke/full；`runtime.py:36-73`读取实际checkpoint信息，`workflow.py:108-128`按descriptor创建真实BC/RL分支。`scripts/evaluate_dppo_uav_formal_endpoint.py:366-404`将实际`use_base_policy`传到runtime：BC=True、RL=False。`third_party/dppo_official_cc7234a/model/diffusion/diffusion_vpg.py:145-163`据此选择基础或LoRA actor，而不是依据绘图标签。

[FACT] `episodes.py:138-148`保存实际分支和空间规则；`episodes.py:157-188`最多60次决策、只保存真实执行前缀并记录完整计划；`episodes.py:17-82`重算H4首事件、验证分数位置/时间/连续性/结局。旧缺开关header按True读取（`:43`），不能仅修改旧标签使截断轨迹变成成功。

[FACT] `workflow.py:142-180`当前新比较读取新out/full中的BC与RL，reference_full为0；旧BC只核对初始观测/禁用LoRA首动作。原bank hash保证任务输入一致，不保证评价规则相同。A0/R1/BC统一评价的reward_version都是v2；因此A0评价轨迹的v2高分，不能叫作A0真实v1.7训练分数。

### 2.3 旧终点与新判据

[FACT] 旧v1.7真实事务`env/reward_v17_support/environment.py:68-108`执行完整H4五点，在整个路径检查碰撞/触地/人工边界，但只在H4末点判reached。R1改为连续首次入球，避免H1/H2曾进入目标球而H4已穿过的末点漏判。v3是在现有R1首次事件合同上取消人工空间失败，不能将三个时期的到达率混成同一终点。

[JUDGMENT] 主终点仍为真实路径首次安全入0.5m三维球，yaw、末速和驻留不加入成功条件。扩大允许空间不增加预算、不把未执行tail当轨迹、不重新采集EGO示范；lightweight结果不能称PX4/Gazebo闭环结果。

## 3. 新旧reward的真实作用、替换与局限

### 3.1 R1四项公式

[FACT] `env/reward_v2_support/reward.py:93-122`为：

$$b_{k+1}=\min\left(b_k,\min_{p\in\mathcal P_k^{exec}}\|p-g\|\right),\qquad R_k=R_{terminal}+10\frac{b_k-b_{k+1}}{D_0}-C_{risk}-0.05.$$

安全到达+100；当前训练中的碰撞/触地/人工出界/超高/invalid为−50；time_limit终局项为0。有效决策的newbest回合总预算不超过10，往返到旧best不重复领奖。risk仅在`done_reason=none`时评价tail；终止的未执行tail不扣分（`:110-112`）。

$$C_{risk}=\tfrac12\max_j w_j\{B(c_j;0.45,0.10)+B(z_j;1.0,0.20)\},\quad B(x;u,l)=\operatorname{clip}\left(\tfrac{u-x}{u-l},0,1\right)^2.$$

[FACT] `reward.py:49-67`中执行段权重1，tail段为$2^{-(j-4)/4}$。max而非sum避免同一危险沿多个点重复累计；距离警戒外risk严格为0；障碍风险与地面风险各自组成半额，risk总上界1。连续box/cylinder净空来自v1.7 geometry，球障碍另有连续解析最近距离（`:24-45`）。

[JUDGMENT] 此结构可让模型在当前计划窗口中提前规避未来危险，容忍必要退距，并通过后续value/最终到达学到长期绕行。它没有直接保证所有障碍布局的早期选边、错过目标后的恢复或密集障碍脱困成功；窗口之外的危险、计划tail下一轮被改写、risk为0的错误选边是具体边界。

### 3.2 v1.7仍可借鉴的情境与实际替换

| 功能 | v1.7实际代码 | R1的承接 / 确实未执行的旧公式 | 局限与正确解释 |
|---|---|---|---|
| 目标推进 | `reward_v17.py:100-109`按本轮起末点距离差乘w_goal，可有负奖；`:124-129`另有free-potential PBRS | R1只奖励刷新整回合best，且已执行线段中间最近点也可刷新 | 能防重复领进展；risk为0且没刷新best时，有效返回与继续偏离都只扣时间，未来信用应区分其后果 |
| 提前避障 | `:131-152`风险门控、横移/yaw幅度、历史低风险基线或直连反事实、净空改善与cap | R1替换为8步连续风险+8步动作信用；旧onset公式未叠加 | 少字段不等于无预见；0.45m阈值和短窗口如何触发，需逐轮看真实danger/tail与下一轮prefix |
| 三维安全/飞越 | `:112-122`净空、地面、相关障碍的飞越不足/过高；`:110-111`爬升和平滑成本 | R1复用连续几何，但旧overflight/climb/smoothness独立代价不执行 | R1没有直接表达每米额外路程或无益爬升成本；不能默认加入强惩罚，因为必要侧绕/飞越也消耗路程高度 |
| 安全前景 | `:154-163`窗口进展门控的future_clearance及cap | R1不给更大安全净空living bonus，只处罚危险 | 可避免把长时间停在空旷区误当收益；但远处安全区域的停滞与推进仍靠进展/value区分 |
| trap/恢复 | `reward_v17_support/state.py:17-47`窗口低进展且近障、进入/退出滞回、安全恢复后的escape与stall；`reward_v17.py:167-173`风险情境下flip处罚 | R1保留dense/recovery任务、风险、best、到达；旧状态机/escape/flip不执行 | 功能思想仍受优化；没有独立历史恢复直接分项也属事实，不能据此宣称必然没学恢复 |
| xyz支持扩展 | `reward_v17.py:176-186`低示范密度单元、连续安全/进展门控，成功后support_escrow结算 | R1 facade的offline_density=None；旧低密度成功结算不执行；C2采样xy±14、z1–5及3D到达仍在 | “不依赖旧density公式”与“空间任务不存在”不同。当前训练人工硬边界与用户允许扩大空间相冲突；v3只修评价 |
| 无益往返/额外路程 | `reward_v17.py:188-193`直连安全、无相关障碍、低风险等情境；`state.py:50-66`局部超额路程与多次进展符号变化 | R1只有每决策0.05，不按米数收费，不使用旧loop gate | 旧guard也不是通用长路线处罚；是否复用其情境，必须对必要绕行和恢复反例一起检查 |

[FACT] 三类能力任务参数由`environments/factory.py:69-88`记录：C2 xy[-14,14]、z[1,5]、H4/8、0.5m目标，角色取真实`KinematicUAVEnv._ROLE_SAMPLING_PARAMS`。训练带扰动（概率0.2、位置尺度0.3）和30% mid-state；统一评价关扰动/执行噪声/mid-state（`runtime.py:173-175`）。这属于实际训练与评价分布差别，尚不能据此定因。

[FACT] 旧设计`sheji/Reward_v1_7_ObstacleRelativeHeight_and_ActiveCapability_Design_v1_4.md:121-128`明确采样高度不是绝对飞行上限，R1设计`:29`又把超高/出界写成物理失败。实际两版训练代码仍有这些条件。应以最新用户允许扩大xyz要求为准，并保留历史设计与运行证据；不能用设计文字替代当前实现。

### 3.3 A0正式density / calibration真实可用性

[PROVEN] 当前源码目录真实存在`data/reward_v17/frozen_density_v1.json`，本轮计算SHA256为`ceedeb04b3904b02baa66f4a76c0de3a49b1cbf53b9bd5b99fba658739ae1769`，匹配A0三seed YAML的`reward_density`声明（seed201文件`:145-147`；其他两份同路径/hash）。calibration真实路径为`data/reward_v17/calibration_report_v2.json`，本轮实算SHA256为`d8d5f26365959830a5f9404ff40d6690c30a8e75b71d4cd78e0965fdb013d88c`，匹配A0配置（seed201`:148-150`）。

[FACT] `rewards/select.py:23-50`同时验证真实cfg、calibration/density文件hash、语义content_hash和reward源码身份；不允许隐式替代density。v1.7真实GeometryContext入参为默认ground_z=0、xy±30（`reward_v17_support/geometry.py:18-22`，真实调用`environment.py:105-108`）。`reward_v17.py:58-80`要求完整实际H4五点、端点等于真实状态以及真实history/density，不能把R1分数前缀补点凑五点，也不能用单元测试density假装正式训练分数。

## 4. critic、GAE与有限预算：确定事实和待裁决语义

### 4.1 beta已传入，但未完整表达history尺度

[PROVEN] `engine/critic_state.py:8-19`从真实history取D0、b，仅构造beta；`engine/value.py:36-55`接收ordered3×192特征和beta。`entrypoints/pipeline.py:449-458`用于当前value，`:477-486`用于next value；`:529-542`保存入buffer。actor采样不接收beta。

[PROVEN] 以下是算法级输入别名反例，不依赖某个训练seed：当前观测及近期轨迹相同、当前距离6m，A的D0=10/b=5，B的D0=8/b=4，两者beta=0.5；下一H4执行线段最近到4.5m。A的newbest=0.5，B=0，同一critic输入却对应不同即时reward。环境9维状态（`kinematic_uav_env.py:905-916`）只有pos、goal_body、当前距离、yaw，没有D0或b；3帧condition不能普遍恢复整个回合起点。它证明“beta足够恢复进展奖励状态”不成立，未证明critic必然发散或这是三seed退化唯一原因。

[JUDGMENT] 下一候选首先讨论补充D0或等价尺度信息，并检查reset、current/next value、buffer、checkpoint一致传递；具体网络/参数待方案审查。只修critic信息不保证策略保留BC能力，也不应顺带改变actor动作/输入合同。

### 4.2 time_limit与collection boundary都bootstrap，但意义不同

[FACT] `terminal_contract.py:116-117`将第60次无物理终止设为truncated；`pipeline.py:483-486`只在terminated清零next_value。`engine/gae.py:17-24`为：

$$\delta_t=r_t+\gamma(1-terminated_t)V_{t+1}-V_t,\quad A_t=\delta_t+\gamma\lambda(1-terminated_t)(1-truncated_t)A_{t+1}.$$

[FACT] 因此time-limit保留next value，却停止跨重置的GAE递推；buffer末端collection boundary也是截断（`pipeline.py:467-468`），两者不能混称任务失败。next value读的是实际执行后的观测/history，不是reset后新episode（`:469-486`）。

[JUDGMENT] 若60只是数据采集截断，bootstrap表达截断后的继续价值；若60就是必须完成任务的期限，剩余预算属于目标状态，而当前critic和actor均无明确时间输入。先明确研究任务语义，再检查相应target；不能为提高SR随意切bootstrap，也不能用“标准GAE”自动证明它符合本项目有限期目标。

[FACT] `tests/dppo_uav_rebuild/engine/test_buffer_and_gae.py:9-18`明确断言terminated切bootstrap、time-limit不切。`tests/dppo_uav_rebuild/rewards/test_reward_v2.py:131-152`检查time-limit终局0/tail0以及纯代数奖励界，但未调用critic/GAE；不能据此证明所有真实训练target都严格偏好预算内成功。

## 5. 八步PPO信用、归一化与审计值的解释

### 5.1 真正进入loss的信号

[FACT] `build_system.py:115-124`按R1设reward_horizon=8，A0=4。`engine/official_loss_components.py:65-95`只给actor传state/global_cond，用vendor logprob，对new/old相同动作索引clamp[-5,2]并在8×11上求平均，指数得到ratio；advantage在逻辑批次内归一化、分位边界裁剪，再乘$\gamma_{denoising}^{K-k-1}$。`:122-136`为PPO裁剪loss和critic回归。

[FACT] 当前E5 runtime默认advantage分位0/1，不会主动去掉困难或成功极端样本（`third_party/dppo_official_cc7234a/uav_idp3/e5_runtime.py:165-166,286-297`）；logprob clamp、PPO ratio clip、global gradient clip分别作用在不同位置，不能统称reward剪裁。`trainer.py:255-287`在逻辑批次先统计advantage，microbatch按样本比例加权，再一次提交；`:320-356`还有KL/ratio门禁与梯度norm检查/裁剪。

[JUDGMENT] 把reward各项统一乘常数，经advantage归一化后不等于同比放大actor方向；更改终局项、risk等相对强度会改变target、符号与critic拟合。应沿真实reward→value/GAE→逻辑批归一化→denoising权重→ratio/clip→更新量核查，不能用即时reward正负判断该动作最终被强化。

### 5.2 8步与4步：真实影响和未证实因果

[FACT] 8步mean令prefix和tail同时进入同一ratio。若tail不变而prefix变化相同，8步平均logratio是4步平均的一半；若二者方向相反，可在full平均中抵消。每个转移只有一个scalar advantage，success/failure/newbest/time及risk共同影响整个8步，包括终止时未实际执行的原prefix余段和tail。其结构不保证某段只受与该段对应的reward影响。

[FACT] `official_loss_components.py:106-120`已记录prefix/tail/full的KL、clip、logprob漂移、action variance；`trainer.py:309-318`汇总。这些是可复用诊断，不必为每个seed/update新增专用程序。action variance当前汇总是各microbatch方差的均值，不能直接当完整逻辑批/整回合/世界空间动作多样性。

[JUDGMENT] 八步信用让tail风险具有对应score信号，这是设计所需；同时终局信用分散到未执行意图，可能降低样本效率。当前并未完成固定条件下H4/H8信用的因果消融，也不能自动改回H4后称保留了原tail风险训练的公平检验。尾段计划安全必须与下一轮prefix改变和最终安全到达同看。

### 5.3 新发现：`advantage_normalized_for_update`不是每次实际optimizer优势

[PROVEN] `audit/training_audit.py:524-530`明确该审计是在更新后，为每转移按identity挑一个denoising k、只读不backward。`:574-580`用全buffer 1024个转移计算mean/std；`:641-642`将结果命名为`advantage_normalized_for_update`。

[PROVEN] 实际S2先随机打散1024×10个transition/denoising pair（`engine/pair_schedule.py:82-87`），再切1280对逻辑批次（`:129-138`），5pass共40次提交（`pipeline.py:588-617`）。每个逻辑批次的mean/std由`trainer.py:255-257`单独计算；其转移组成和重复次数并不等于全1024审计批次。因此该审计字段可作统一后验描述，不能证明一个动作在全部40次实际更新中使用了该精确值，甚至不能单凭该字段正负证明实际更新方向。

[JUDGMENT] 同日研究报告§9.3的u128:t277原reward、value、next_value、GAE raw advantage及bootstrap算式仍是可核查事实；所引−0.03979应称全rollout后验审计归一化值。单凭该字段不应写“actor最终抑制了该动作”。本轮随后完成匹配真实pair permutation的只读还原，详见§10：50个概率对中48负、2正；仍未还原模型梯度与clip后的净参数影响。

## 6. LoRA、native sample clip与行为退化

[FACT] `actor_ddpm/lora.py:21-27,175-221`只在denoiser14 Linear+33 Conv1d安装rank8/alpha8 LoRA，base冻结；Linear/Conv1d分别以scale=alpha/rank附加低秩输出（`:35-60,63-102`）。`build_system.py:97-104`优化器只接adapter参数；冻结BC并不会限制adapter输出偏离幅度。

[FACT] `third_party/dppo_official_cc7234a/uav_idp3/e5_runtime.py:269-283`基础actor关LoRA、actor_ft开LoRA，共享base模型。`official_loss_components.py:63-64`BC loss禁用，真实trainer调用`use_bc_loss=False`（`:272`）。没有“所有BC成功必须保留”的代码硬保证，也不能因原BC参数没变就断言RL不会遗忘。

[FACT] native scheduler的clip_sample/clip_sample_range被直接转入denoised_clip_value，禁用clip时为None；runtime禁止另设不同clip，且final_action_clip_value=None（`e5_runtime.py:242-258`）。vendor direct-x0分支预测sample（`diffusion_vpg.py:206-214`），随后clamp x_recon（`:215-221`），而E5不在clip后重算epsilon。此为采样过程内native合同，当前没有轨迹后处理修剪。

[UNCERTAIN] 本Windows源码树没有`data/outputs/2026.08.16/08.53.26_e5_lambda0p5/checkpoints/latest.ckpt`本体；本轮没有实际加载E5权重/normalizer，因此未独立确认固定y delta −0.205954是否恰为某一native归一化边界反变换值。仅凭重复数值不能排除方向饱和、goal敏感性下降、观测/encoder分布或LoRA偏移，不能定因。

[JUDGMENT] 最少诊断是在现有采样/探针内针对同任务的靠近、穿过、离开、返回目标几个真实condition，同时核对BC/RL的goal_body、before-clip x0、clip频率、最终normalized/unnormalized y，以及prefix/tail和BC差异；须看随目标误差符号改变的输出响应。不要见clamp就宣称整条采样链全部零梯度：native未重算epsilon的方向项仍可能保留对未clip预测的依赖；应检查实际采样步而非只看单个源码字段。

## 7. 现有测试覆盖、盲区和本轮验证

| 现有测试 / 精确断言位置 | 覆盖 | 不能证明的事项 |
|---|---|---|
| `tests/dppo_uav_rebuild/rewards/test_reward_v2.py:32-101` | 段中目标/碰撞顺序、球体/旋转box、同点失败、旧默认空间事件、v3跨界到达/边界外真实碰撞 | 新完整5880 full回放已完成；实际策略跨界后有效泛化 |
| `test_reward_v2.py:104-152` | best不重复领、risk max、tail provenance、time-limit tail/terminal为0、固定代数奖励界 | best之外有用返回/无益偏离的学习可区分；有限预算critic target语义 |
| `test_reward_v2_integration.py:29-67,69-149` | 真实Kinematic事务经统一make_adapter跨界后到达；H4不执行tail；H1/H2分数入球、观测帧与时间 | 使用mock点云的测试不是E5神经策略/GPU闭环；不能证明所有远空间观测质量 |
| `tests/routea_paired/test_environment_contract.py:13-54` | 真CPU SynthPointCloud固定reset数组一致，真实H4首次碰撞 | 模型goal响应、native clip和LoRA退化因果 |
| `tests/routea_paired/test_comparison.py:14-69,231-272,274-310` | 新BC/RL分母、完整tail/观测身份、动作16/8/4切片、事件、真实LoRA gate禁用后不受加载影响、拒绝partial trace | 小Linear gate测试不能替代真实E5 checkpoint上的所有任务能力保持 |
| `tests/dppo_uav_rebuild/engine/test_r1_critic.py:53-87` | beta当前/next不同、actor未修改、初始A0 value/RNG一致、buffer保留beta | D0/b奖励别名及remaining-budget完整性 |
| `tests/dppo_uav_rebuild/engine/test_r1_credit.py:30-95` | beta不传actor logprob、8步new/old相同索引mean、prefix/tail诊断、只准4/8信用范围 | 每段因果信用独立；H8比H4更有效；真实gradient贡献/BC成功保持 |
| `tests/dppo_uav_rebuild/engine/test_buffer_and_gae.py:9-18,21-71` | terminated与truncated不同bootstrap；buffer形状和批量 | 60次任务目标是否应continuing；审计归一化是否等同每次实际提交 |
| `tests/routea_paired/test_python38_compatibility.py:10` | 交付源代码Python3.8语法/API静态合同 | 实际WSL Python3.8.20/CUDA整批运行已通过 |

[PROVEN] 本轮复用仓库已有`.venv-routea/Lib/site-packages`，没有安装依赖或新增测试；解释器`D:\miniconda3\python.exe`。在源码根目录设置PYTHONPATH为上述目录、PYTHONDONTWRITEBYTECODE=1后运行：

```text
python -B -m pytest -p no:cacheprovider tests/dppo_uav_rebuild/rewards/test_reward_v2.py tests/dppo_uav_rebuild/rewards/test_reward_v2_integration.py tests/dppo_uav_rebuild/engine/test_r1_critic.py tests/dppo_uav_rebuild/engine/test_r1_credit.py tests/dppo_uav_rebuild/engine/test_buffer_and_gae.py tests/routea_paired -q --basetemp .test_tmp/code_audit_reward_20261012
```

输出`53 passed in 5.93s`，退出码0。此前直接默认python尝试因缺pytest退出1；随后使用交接已说明的现有仓库依赖路径成功。产生的只有pytest自动临时数据；未修改活动源码、测试、配置。交接原42 passed为旧修复回执，本轮53另包含critic/credit/GAE聚焦检查。

## 8. 下一阶段的最少诊断顺序与不应改变的事项

1. [JUDGMENT] 完成fresh384原方案并保存原源码、配置、身份、完整日志/metrics/权重；再用统一评价v3重采BC及所有已选RL完整轨迹。新旧规则明确分开，保留所有失败/partial证据。未回传前不预言扩空间后到达率。
2. [JUDGMENT] 在现有训练metrics与原轨迹中按具体行为分层：开放空间有效推进、必要绕行、近目标错过后的返回、dense/recovery；逐轮看reward分项、b/D0、真实exec/tail净空、value/next_value/GAE和结局。A0只用真实v1.7训练metrics回答旧分项是否参与，不能用统一v2评价回报替代。
3. [JUDGMENT] 明确60次预算的研究任务语义，再决定是否需要有限期限state/target；当前只报告bootstrap差别，不直接修改gamma/GAE/终止类型。核对collection boundary与真正deadline分别处理。
4. [JUDGMENT] 对少量有正反证据的转移，复用当前buffer与固定pair schedule还原实际逻辑批归一化、denoising权重和clip，再讨论成功/失败信用。后验审计字段作为描述值保留，不冒充每次实际更新日志。
5. [JUDGMENT] 对任务7等固定增量现象，优先在现有统一探针/采样调用检查goal响应、LoRA相对BC偏移及native clip；在证据支持前不改clip/normalizer、不直接加大terminal/risk/time全部系数、不因普通曲线波动提前停训。
6. [JUDGMENT] 新候选讨论的确定起点是训练人工空间语义和critic历史尺度；风险预警时机、恢复deadzone与必要绕行成本作为待比较的设计问题。先保留成功高分、真实碰撞、首次入球、有效探索、H4/11D与eval-only隔离，再审查最少可区分的变化；本笔记不冻结新公式或新数值。

[MC CHECK] 没有轨迹后处理、A*/直连替代执行或外部安全投影；EGO数据不重采集；所有几何反事实只作分析；不借easy/dense标签替代几何和完整结局；不把实际参与说成能力已实现或因果证明。w4/w8/w11/w12/w18及fixed32继续eval-only，不能用于调reward/选超参。

## 9. 实际读取清单与证据归属

[FACT] 本轮直接分块读取/定位下列现行文件；超长文件读取了上述引用相关函数/章节，不声称逐字读过所有训练日志或全部原始轨迹。

- 项目约束：`AGENTS.md` v1.15。
- 首读/纠偏：`jindu/2026-10-12_RouteA_测试端取消人工空间截断修复与交接_v1_0.md`、`jindu/2026-10-12_RouteA_人工空间边界与测试失败判据纠偏_v1_0.md`、`jindu/2026-10-12_RouteA_Reward设计实现与轨迹表现逐项判断_v1_0.md`。
- 设计：`sheji/2026-09-28_RouteA_RL_循环规划整套Reward与高频到达训练候选设计_v1_3.md`全篇；`sheji/Reward_v1_7_ObstacleRelativeHeight_and_ActiveCapability_Design_v1_4.md`索引及执行/物理不变量章节。
- 研究记录：`论文/研究报告/2026-10-12_BC成功能力保持与再获得_双向钢人与2020至2026文献复核_v1_0.md`§9。其2940原轨迹统计与任务案例作为既有研究证据，本独立代码审查未再次打开全部JSONL；总报告的独立轨迹核查由主任务完成。
- reward与环境：`diffusion_policy_3d/env/reward_v17.py`、`reward_v17_support/{config,state,geometry,environment}.py`、`reward_v2_support/{reward,environment,first_event}.py`、`kinematic_uav_env.py`相关分派/state/默认合同；正式`data/reward_v17/frozen_density_v1.json`hash。
- 训练：`diffusion_policy_3d/rl/dppo_uav_rebuild/entrypoints/{build_system,pipeline,config_schema_v2}.py`、`environments/{factory,kinematic_adapter,terminal_contract}.py`、`engine/{critic_state,value,gae,official_loss_components,trainer,pair_schedule,rollout_buffer,contracts}.py`、`audit/training_audit.py`、`actor_ddpm/{lora,rollout_sampler}.py`、`rewards/select.py`与`rewards/v2/facade.py`；`bc_runtime/native_loader.py`scheduler校验；A0三seed YAML的density路径/hash，R1 seed203 fresh384 YAML。
- native/vendor：`third_party/dppo_official_cc7234a/uav_idp3/e5_runtime.py`、`model/diffusion/diffusion_vpg.py`相关actor/clip/mean分支；不把adapter文件自述当作wrapper直接调用vendor loss的证据。
- 统一评价：`scripts/run_routea_paired_comparison.py`、`scripts/evaluate_dppo_uav_formal_endpoint.py`相关policy/adapter/旧指标分支、`scripts/routea_paired_support/{runtime,episodes,workflow,core}.py`相关合同，以及`policy_catalog_v1.json`配置/身份索引。
- 测试：本笔记§7列出的全部聚焦测试，另定位`tests/routea_paired/test_analysis.py`新分母断言；实际执行53项命令如§7。

[UNCERTAIN] 本审查未访问WSL、未重训、未读取当前fresh384的运行日志、未加载缺失的原BC checkpoint，也未开展网络/论文检索；这些未获证据不由猜测补齐。原设计文件仍保留当时状态字样，应以当前源码/运行身份和最新交接判断已实现状态。

## 10. 补充原件核查：u128:t277在实际逻辑批次中的优势

[PROVEN] 本轮直接读取`C:\Users\cjj\Desktop\IDP3\wsl_snapshot\20261009_185302_routea_r1_resetfix_s2_3seed256_run01_pack\outputs\seed202609203\metrics\metrics_update_000128.json`。1024条`rollout_audit.transition_records`依次是u128:t0…t1023；目标t277为真实time_limit、collection_boundary=False。原reward=−0.05、value=18.1808795929、next_value=24.3417797089、return_target=24.0483627319、raw advantage=5.8674831390。原outer audit归一化值−0.0397917293、dppo_credit审计值−0.0397722945；两者均不同于逐逻辑批值。

[PROVEN] 先读取不可改写回传`source_archives/r1_source_before_merge.tar.gz`，确认归档pipeline第592行使用`seed + update_index * 1009`；当前pipeline对应第600行同样如此。归档与当前完整pipeline hash不同，不能宣称整个pipeline同版本；本次所需trainer、pair_schedule、official_loss_components逐字节hash一致：

| 文件（前缀`diffusion_policy_3d/rl/dppo_uav_rebuild/engine/`） | 归档和当前共同SHA256 |
|---|---|
| trainer.py | c05174d731d475f8fc6db7d25db845d60b122a013ec89c911a2795d46503f19c |
| pair_schedule.py | c8ce82eb500f4527b94c5e11db49ddca3523d697e419966ee69b0c843b990985 |
| official_loss_components.py | 43d9068d092706521202daa1ad0bd25b7778ee80d287b18649cccd3116d386ac |

[PROVEN] 用现有PyTorch2.7.1+cpu、`torch.Generator().manual_seed(202738355)`（202609203+128×1009），连续生成5次`torch.randperm(10240)`；用现有`pair_schedule._permutation_hash`重算dtype/shape/bytes hash。全部与原`formal_training.pair_schedule_audits`逐pass一致，匹配后才计算优势：

| pass_id | 原件与本轮相同permutation_sha256 |
|---:|---|
| 0 | d853e75a4f3590d6a5464e915a13a27b30260353c56b868d69de0f7f3cf86475 |
| 1 | 4827cac32c705ab2bc74f5c4c6326e55da78a50d09feb3fbc23d56dc9bb333a2 |
| 2 | cd98f0620a4412f56c403ec0ab35037057a7e698648a3d1cf56ee911dd19e906 |
| 3 | 7e5f008a8f84eb8b04ea5e2af73ee81fdd3a583d41602c94df432e0791cf1ee0 |
| 4 | 7e6240bcd3342513d3eea7b48a23d19a52f2fe8f81d60443c6f285a1a5a98d03 |

[PROVEN] 把原记录raw advantages恢复为float32张量，对每个1280对批次按flat//10取对应转移优势，用现有`AdvantageStats.from_tensor(...,0,1)`得到mean/std/边界，恢复target的normalized advantage，并乘原$0.8^{9-k}$。t277每个pass含10个k，共50个对：

| pass_id | 正 / 负 / 零个数 | normalized最小值 | normalized最大值 |
|---:|---:|---:|---:|
| 0 | 0 / 10 / 0 | −0.07847819 | −0.01855966 |
| 1 | 0 / 10 / 0 | −0.07214706 | −0.02331680 |
| 2 | 0 / 10 / 0 | −0.06182545 | −0.00956673 |
| 3 | 2 / 8 / 0 | −0.09265266 | +0.00796204 |
| 4 | 0 / 10 / 0 | −0.06341957 | −0.00478732 |
| 合计 | 2 / 48 / 0 | −0.09265266 | +0.00796204 |

乘denoising权重后范围为−0.06477687到+0.00260900。两个正值均出现在pass3逻辑batch0（从0计批次，整个update第25次optimizer提交）的k1/k4；该batch平均raw advantage=5.6813497543，低于本转移5.8674831390，std=23.3776130676，因此其normalized约+0.00796204；权重分别0.16777216和0.32768。

[JUDGMENT] 这是匹配原排列、复用真实公式的实际逻辑批优势重构，进一步证实不能用单一全rollout审计正负取代实际批次。原metrics记录40 committed、0 rejected；本轮未加载模型、未重算每次ratio/clip或梯度，CPU reduction也不声称与原CUDA逐bit相等。因此可说该转移50个PPO概率对的优势多数为负且有2个小正值，不能说“净参数更新必然抑制这个动作”或“timeout策略总体被强化”。

[JUDGMENT] 该转移在60次末段从4.471m返回到3.475m，保持旧best2.090m，未到达。其本轮动作是有效返回还是应被判为无益行为，须与任务期限、此前偏离动作的信用及安全路线一起解释；不能因最终time_limit就要求每一个末段返回动作都受负奖。本轮计算是one-shot只读命令，没有新建执行程序或改训练参数。
