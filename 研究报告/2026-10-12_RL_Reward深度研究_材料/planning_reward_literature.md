# 循环轨迹规划、UAV RL 与 Reward 设计：17 篇原文及官方源码方法卡

| 字段 | 内容 |
|---|---|
| 文档类型 | 独立文献研究材料；供综合研究报告引用 |
| 检索日期 / 文献截止 | 2026-10-12 / 2026-10-12 |
| 版本 / 状态 | v1.0 / 原文研究与源码核查；候选方向尚未批准为新训练方案 |
| 范围 | 2020—2026 的循环规划、RL 飞行、条件奖励、课程和奖励误设研究 |
| 已读项目证据 | 2026-10-12 Reward逐项判断交接；当前 reward.py、critic_state.py、build_system.py |
| 文献与源码原件 | `论文/被参考/2026-10-12_RL_Reward综合研究/planning_reward/` |
| 与其他研究材料的分工 | 不重复计入 DPPO、AWAC、RLPD、IBRL、CalQL、ReinFlow、FDPP、Beyond Imitation、Immiscible Policy、PPO |

## 0. 阅读范围与结论边界

[FACT] 本材料包括 17 篇论文。逐篇核查方法、实际奖励或训练目标、验证环境与局限；7 个作者或官方 GitHub 仓库读取了实际实现，均固定 commit，日期早于本次文献截止。来源包含论文正文、方法附录、作者代码及出版社元数据，未以博客或产品文档填充论文数量。

[FACT] 已复用项目原存 APEX v3 HTML 和 Wild v1 PDF。其他成功下载的 PDF/HTML、提取文本和源码快照按原件归档。文本提取是自动生成的阅读副本，不是新活动程序。部分网站直接下载失败：Swift 的方法与公式通过出版社索引读取，完整 PDF 未取得；其证据级别及下载失败记录见归档清单。不能把未下载的文件说成已经保存。

[FACT] 文献中的监督模仿、离线条件生成、可微物理训练、低层位置控制、已知赛道 RL 和未知障碍导航分别标注。论文报告的成功率只适用于其原任务和分母，不能当成 iDP3-UAV 的预期成功率。

[JUDGMENT] 研究目标是让复杂布局获得净能力提升，同时维护简单任务到达；允许部分旧成功任务退步并不等于允许简单任务整体失去推进能力。当前 fresh384 的训练运行版本保持冻结。本材料不改变 reward、采样、H4 执行或 60 次决策预算，不操作 WSL，不提出策略外修剪或 BC 接管作为 RL 能力。

## 1. 17 篇文献索引

| ID | 核实的论文名称 | 年份 / 发表信息 | 原文 ID / DOI | 对当前问题的主要用途 |
|---|---|---|---|---|
| P01 | APEX: Learning Adaptive High-Platform Traversal for Humanoid Robots | 2026；本次读 v3，2026-08-13 | arXiv:2602.11143 | 历史最好进展、防往返、critic 历史输入 |
| P02 | Champion-level drone racing using deep reinforcement learning | Nature 2023 | 10.1038/s41586-023-06419-4 | 每步进展、感知、安全与命令成本的配合 |
| P03 | Learning High-Speed Flight in the Wild | Science Robotics 2021 | arXiv:2110.05113；10.1126/scirobotics.abg5810 | 未知环境、多模态预测与循环执行；监督学习边界 |
| P04 | Learning to Fly in Seconds | 2023 预印本；RA-L 2024 | arXiv:2311.13081；10.1109/LRA.2024.3396025 | 奖励成本课程、历史动作、非对称 critic |
| P05 | Learning Perception-Aware Agile Flight in Cluttered Environments | 2022 预印本；ICRA 2023 | arXiv:2210.01841；10.1109/ICRA48891.2023.10160563 | 参考路径进展与感知约束；已知环境边界 |
| P06 | Bootstrapping Reinforcement Learning with Imitation for Vision-Based Agile Flight | CoRL 2024 | arXiv:2403.12203v3 | BC/IL 起点的遗忘、critic warm-up、表现自适应 |
| P07 | Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | RSS 2023 | arXiv:2303.04137 | 预测时域与执行时域分离；闭环响应成本 |
| P08 | Planning with Diffusion for Flexible Behavior Synthesis | ICML 2022 | arXiv:2205.09991 | 轨迹回报指导、长程规划、单步再规划 |
| P09 | Is Conditional Generative Modeling All You Need for Decision-Making? | 2022 预印本；ICLR 2023 | arXiv:2211.15657 | Decision Diffuser；整段回报/约束条件 |
| P10 | Eureka: Human-Level Reward Design via Coding Large Language Models | 2023 预印本；ICLR 2024 | arXiv:2310.12931 | 以独立任务分数优化奖励，分项反思 |
| P11 | Text2Reward: Reward Shaping with Language Models for Reinforcement Learning | 2023 预印本；ICLR 2024 | arXiv:2309.11489v3 | 任务阶段门控、reward 注入、独立 success |
| P12 | DrEureka: Language Model Guided Sim-To-Real Transfer | RSS 2024 | arXiv:2406.01967 | 安全与任务项交互，reward 与环境共同影响 |
| P13 | Emergent Complexity and Zero-shot Transfer via Unsupervised Environment Design | NeurIPS 2020 | arXiv:2012.02096 | PAIRED；可解但尚未掌握的任务 |
| P14 | Evolving Curricula with Regret-Based Environment Design | ICML 2022，PMLR 162 | arXiv:2203.01302 | ACCEL；任务编辑和能力边界课程 |
| P15 | Back to Newton's Laws: Learning Vision-based Agile Flight via Differentiable Physics | 2024 预印本；Nature Machine Intelligence 2025 | arXiv:2407.10648v2；10.1038/s42256-025-01048-0 | 接近速度门控与长短时域目标；非 PPO 边界 |
| P16 | Defining and Characterizing Reward Hacking | 2022 | arXiv:2209.13085 | proxy return 与任务成功的排序条件 |
| P17 | The Perils of Trial-and-Error Reward Design: Misdesign through Overfitting and Invalid Task Specifications | AAAI 2023，37(5):5920–5929 | 10.1609/aaai.v37i5.25733 | 单步好坏与累计任务规范；奖励对算法过拟合 |

[FACT] ACCEL 是方法名，论文正式标题为 **Evolving Curricula with Regret-Based Environment Design**，PMLR 主源确认 ICML **2022**。它不是 arXiv:2306.05367，也不是一篇名为“Adapting Curricula by Editing Levels”的 2023 论文。Text2Reward 的早期标题与最终 ICLR 题名有变化，本材料使用已下载 v3 的题名。

## 2. UAV、历史进展与能力保持方法卡

### P01 — APEX：历史进展有依据，奖励公式必须区分

**原文**：[arXiv v3](https://arxiv.org/html/2602.11143v3)，§III-A、§III-B、§IV-C、附录VI-A；作者 Yikai Wang、Tingxuan Leng、Changyi Lin 等。归档 `APEX_2602.11143v3.html`。

[FACT] 论文用任务状态 $x_t$ 表示接触丰富的爬上、爬下、起身、躺下过程，以 $x_t^*=\max(x_0,\ldots,x_{t-1})$ 记录历史最好状态。实际任务项是**二值 0/−1**：

$$r_t^{task}=\begin{cases}0,&x_t>x_t^*,\\-1,&\text{其他。}\end{cases}$$

[FACT] 它不按进展幅度付款；总奖励另有 alive、regularization、force、terminal-pose 四类项。历史最好状态直接作为 critic 的额外输入。验证包含随机初始位姿与平台高度、每个对照 1000 次任务试验，以及 G1 真机高平台通过；该结果不是 UAV 避障证据。作者与本文均未在本轮确认可用的完整官方训练 reward 仓库，故不计入源码核查仓库数。

[JUDGMENT] 可迁移的是“避免退后再前进重复领奖”和“历史奖励所需状态供 critic 获知”。R1 是 $10(b_{before}-b_{after})/D_0$ 的有限增量预算，不能称为照搬 APEX 的原公式。若把 APEX 的每次未刷新 −1 直接加入 UAV，会持续处罚必须先远离终点的绕障；$x$ 的任务定义、控制频率和接触约束也不一致。需要分析每回合累计成本和复杂路线承受的代价，不能以 ratchet 名称证明适用。

### P02 — Swift：进展、感知与安全联合优化，但赛道已知

**原文**：[Nature 正文](https://www.nature.com/articles/s41586-023-06419-4)，Methods “Reward formulation”，式(7)—(10)、Code availability。作者 Elia Kaufmann、Leonard Bauersfeld、Antonio Loquercio 等。

[FACT] Swift 用 on-policy RL 学习质量归一化总推力和机体系角速度，奖励包含下一道门进展、摄像机朝向、命令成本和碰撞项。进展是 $\lambda_1(d_{t-1}^{Gate}-d_t^{Gate})$，不是历史最好距离；感知项是随视线角度变化的指数函数，命令项抑制大角速度及动作变化；碰撞/触地处罚并结束回合。固定赛道地图、视觉惯性估计、门检测和残差模型共同参与。

[FACT] 论文在真实竞速中对比冠军飞手。它明确不公开完整训练源码，只在 [Zenodo](https://doi.org/10.5281/zenodo.7955278) 提供伪代码和比赛数据，不能把民间复现当成作者完整源码。直接 PDF/HTML 下载失败；本轮通过出版社索引读取了实际方法与公式，归档记录此限制。

[JUDGMENT] 可借鉴“推进收益与安全/动态成本共同定标”，以及门通过时切换子目标使进度重新有意义。其已知门序列提供了当前未知静态环境没有的拓扑任务信息；不能用无限重复门奖励代替首次终点入球，也不能复制论文边界盒终止规则成为用户禁飞区。其低层高频控制数值不适用于每 1.2 秒再规划的 H4 轨迹块。

### P03 — Wild：未知环境的轨迹循环执行，主训练是监督学习

**原文**：[arXiv](https://arxiv.org/abs/2110.05113)、[Science Robotics DOI](https://doi.org/10.1126/scirobotics.abg5810)，Methods、式(2)—(7)。作者 Antonio Loquercio、Elia Kaufmann、René Ranftl、Matthias Müller、Vladlen Koltun、Davide Scaramuzza。归档 `Wild_2110.05113v1.pdf`。

[FACT] 输入深度、速度、姿态和参考飞行方向，网络给出三个轨迹候选与估计碰撞成本。具有完整几何的采样专家生成多模态示范，训练采用 relaxed winner-takes-all 轨迹损失与碰撞成本监督损失；部署循环预测并跟踪候选。真机包括未训练过的森林、雪地和建筑环境。

[FACT] 这是 privileged imitation，论文轨迹成本与网络监督损失不等于 RL reward。专家使用全局无碰撞轨迹帮助采样，部署还包含候选选择和轨迹表示处理。作者代码链接是 [agile_autonomy](https://github.com/uzh-rpg/agile_autonomy)，不是名字相近的 agile_flight；本轮主要用于论文方法边界，未把该仓库算入已读实现数。

[JUDGMENT] 支持“整段多模态轨迹和短前缀循环执行可以用于未知障碍”，不支持“直接提高进展项就突破 BC 上限”。受 MC-1 与 MC-5 约束，不能迁入其任何会改变输出轨迹形状的拟合/候选工程并把改善归因于 R1 学习。成本是新专家、额外候选/碰撞网络与部署链路；当前 frozen EGO 数据不应重采。

### P04 — Learning to Fly：奖励课程与完整状态须沿真实调用核查

**原文**：[arXiv](https://arxiv.org/abs/2311.13081)、[RA-L DOI](https://doi.org/10.1109/LRA.2024.3396025)，PDF p4–6。作者 Jonas Eschmann、Dario Albani、Giuseppe Loianno。归档 `FlySeconds_2311.13081v1.pdf`。

[FACT] 学习任务为到原点并归零速度的低层 RPM 位置控制，采用非对称 actor-critic、动作历史、转子延迟和 TD3。实际奖励以常数减去位置、姿态、速度、角速度、动作相对基线的平方成本；alive 常数用于缓解主动提前终止。代价权重分阶段升高，控制噪声另按时程衰减，论文进行多 seed 和 Crazyflie 真机轨迹对比。

[PROVEN] 官方 [learning-to-fly](https://github.com/arplaboratory/learning-to-fly) 固定 commit `d07592d5c5dea3c90954d2be6f04cfa68581ebe8`。`src/config/parameters.h:32–34` 在初始/目标Squared奖励间选择；`squared.h:58` 组合成本，`:62` 对终止单独支付；`src/steps/curriculum.h:8` 每100000步调权，`:43` 在启用分支重算 replay rewards。仓库也有 abs_exp，但不能因该文件存在称当前入口用指数奖励。

[JUDGMENT] 借鉴历史状态供价值估计、reward/噪声时程分开记录，以及奖励变化时训练目标一致性。其位置/速度归零目标鼓励悬停；在 UAV 避障直接用这种每步姿态/位置惩罚可能更保守。18秒指专用低层训练与平台，不能预测 DPPO 轨迹训练时长。后续新训练才能试课程；当前 frozen384 不可动态换 reward。

### P05 — Perception-Aware Agile Flight：参考弧长进展不等于终点欧氏进展

**原文**：[arXiv v1](https://arxiv.org/html/2210.01841v1)、[ICRA DOI](https://doi.org/10.1109/ICRA48891.2023.10160563)，§III-B—D、§IV。作者 Yunlong Song、Kexin Shi、Robert Penicka、Davide Scaramuzza。归档 `PerceptionAware_2210.01841v1.pdf`。

[FACT] 先训练可见完整状态、无碰撞参考 waypoint/line segment 的 RL teacher，再用 IL 蒸馏深度学生。参考路线由概率路线图生成；task reward 汇合沿路线进展、已到达距离、waypoint通过、终止碰撞、角速度和感知朝向。新增 $r_{pa}=\exp(-\|\theta_{yaw}-\theta_{dir}\|)$，其中方向指向参考路线上当前位置可直连的最远点。

[FACT] 验证是已知 cluttered 场景及 HITL：实际无人机在动捕内飞，观察实时渲染的虚拟障碍。它具备实际动力学与传感器闭环，不能说成纯离线预测，也不能说成真实未知森林避障。

[JUDGMENT] 该参考路线能让必要外绕仍在弧长上前进，从而减少欧氏终点距离的局部误导。迁移需要额外拓扑信息/训练 teacher，不能悄悄把 PRM/A* 的路径交给 actor 执行或算作策略能力。感知门控对当前点云有效范围有启发，但是否需要转向可见性成本要由真实观测链路证实。

### P06 — Bootstrapping RL with Imitation：遗忘还可能来自更新与价值估计

**原文**：[arXiv v3](https://arxiv.org/html/2403.12203v3)，§3、Algorithm1、§4、Appendix A.2。作者 Jiaxu Xing、Angel Romero、Leonard Bauersfeld、Davide Scaramuzza。归档 `Bootstrapping_2403.12203v3.pdf`。

[FACT] 三阶段为 privileged RL teacher、视觉 IL/DAgger student、表现自适应 RL 微调。先冻结 actor 预热 critic，再用相对初始 rollout 回报调 actor/critic 学习率与 PPO clip。reward 包含门距离进展、感知、动作变化、body rate、门通过+10及碰撞−4；该六项结构本身没有免遗忘保证。

[FACT] 三赛道、随机起点、每策略100次评价、5个训练 seed；论文对比显示直接 RL 不会完成，普通 IL 起点微调早期改善后退化，自适应方式改善视觉竞速与扰动鲁棒性，并有真机比赛轨迹。§Algorithm1 的 $\alpha=r_{rollout}/r_{init}$ 对负回报、接近零分母的任务不直接稳健；本文不替作者补规则。

[JUDGMENT] 这是“reward保持相似而微调更新方式影响遗忘”的直接相关证据，反对先假定R1退化只由reward造成。适用方向是检查 critic 充分性、预热与更新幅度，并以独立 safe-arrival 作训练结果比较；不能把竞速回报比直接作为R1调参器。该论文使用 DAgger 采新示范，当前项目不采用其重采部分；新训练设计成本含另一次完整预算和多seed核验。

## 3. 循环规划与整段轨迹目标方法卡

### P07 — Diffusion Policy：预测完整计划，执行前缀再规划

**原文**：[arXiv](https://arxiv.org/abs/2303.04137)，§III、§IV、执行时域与延迟消融。作者 Cheng Chi、Siyuan Feng、Yilun Du、Zhenjia Xu、Eric Cousineau、Benjamin Burchfiel、Shuran Song。归档 `DiffusionPolicy_2303.04137v1.pdf`。

[FACT] BC 学习 $p_\theta(A_t\mid O_t)$，观察时域 $T_o$、预测 $T_p$ 与执行 $T_a$ 明确分离。完整多步动作用于表示一致的意图，机器人只执行一段后接收新观察。论文讨论：执行一步可更快反应，但容易丢失时序一致性；执行过长减弱对新观测的反应。原任务多数使用8步执行较好，属于操作任务消融，不是 UAV H4 的许可依据。

[PROVEN] 官方 [diffusion_policy](https://github.com/real-stanford/diffusion_policy) commit `5ba07ac6661db573af695b419a7947ecb704690f`，`diffusion_unet_image_policy.py:175` 反归一化完整预测，`:178–180` 从 $T_o-1$ 截取 `n_action_steps`，分别返回 `action` 与 `action_pred`。这属于执行时域选择；没有把预测尾段改成另一条轨迹。

[JUDGMENT] 当前 H8/H4 结构与这种循环执行方式一致，但该论文是监督 BC，未给出“未执行 tail 应如何分配 RL reward”的结论。必须区分计划风险、已发生首事件和跨轮累计轨迹。若每轮重新采样使上一轮安全 tail 被放弃，单轮 tail 分数良好仍不保证最后到达。缩短H4或增加调用属于独立设计、计算和时频变化，本次不采用。

### P08 — Diffuser：用整段回报塑造计划，再单步闭环执行

**原文**：[arXiv v1](https://arxiv.org/html/2205.09991v1)，§3.1–3.3、Algorithm1、§5。作者 Michael Janner、Yilun Du、Joshua B. Tenenbaum、Sergey Levine。归档 `Diffuser_2205.09991v1.html`。

[FACT] 学习的是状态与动作联合轨迹分布 $p_\theta(\tau)$；另训 $\mathcal J_\phi$ 预测累计回报，在去噪过程中用 $\mu+\alpha\Sigma\nabla\mathcal J(\mu)$ 偏置计划。算法观察当前状态、生成整条候选、执行第一个动作，再重新规划。验证包括 Maze2D、block stacking 与 D4RL locomotion，主要是离线数据控制任务，没有未知3D障碍UAV真机证明。

[PROVEN] 官方 [diffuser](https://github.com/jannerm/diffuser) commit `7ea422860cc0106e5ca5949d980f04b799d5462c`：`sampling/functions.py:20` 取得回报梯度并在去噪内部调整；`scripts/plan_guided.py:92` 每次重新得到当前条件动作、`:95` `env.step(action)`，最后累加真实reward；`datasets/sequence.py:141–143` 以整回合后续奖励的折扣和训练 value 目标。

[JUDGMENT] 支持“让计划选择考虑长程后果，而不是只奖励当前接近终点”。可借鉴整段回报诊断与长程 critic，但直接迁移需要新回报预测器、噪声级别训练及推理反向传播，成本高于小改R1。去噪内指导原则上符合策略内边界，不能因此称当前 LoRA actor 已学到指导器给出的改进；未执行计划中的预测状态也不是物理事实。

### P09 — Decision Diffuser：条件是回报与任务结构，不能凭条件标签获得未见能力

**原文**：[arXiv v1](https://arxiv.org/html/2211.15657v1)、[ICLR 2023](https://openreview.net/forum?id=sP1fo2K9DFG)，§3、Algorithm1、§4及Appendix D/F/G/K。作者 Anurag Ajay、Yilun Du、Abhi Gupta、Joshua Tenenbaum、Tommi Jaakkola、Pulkit Agrawal。归档 `DecisionDiffuser_2211.15657v1.pdf`。

[FACT] 在固定 reward 标注数据上训练状态序列模型 $p_\theta(x_0(\tau)\mid y(\tau))$，$y$ 可以是归一化整段回报、约束或技能。CFG 与低温采样产生条件状态序列，逆动力学从当前与下一个预测状态取得动作，执行一次后再规划；没有在线 PPO 或TD critic。验证 D4RL、约束导航示例和技能组合等；不等于 UAV unknown static obstacles 闭环验证。

[FACT] 原文说明状态分布较动作平滑，故使用状态生成与逆动力学。条件组合依赖训练数据覆盖各组成条件；部分技能在物理上不可同时成立。其“不受distribution-shift风险”的表述不能作为对任何OOD目标的普遍保证；生成数据的边界仍限制可学行为。

[JUDGMENT] 对当前任务有用的思想是将“安全绕障/可直接到达/远距恢复”等可观测情境与reward或价值估计关联，避免单个全球系数覆盖所有阶段。它不支持按空间坐标超过BC范围就失败，也不保证条件高回报能创造数据里从未有的能力。迁入整个状态生成/逆动力学架构改变Action11d与策略核心，不作为本轮候选。

## 4. 奖励设计、条件项与训练结果反馈方法卡

### P10 — Eureka：奖励候选由任务成绩裁决，不能由自身reward裁决

**原文**：[arXiv v1](https://arxiv.org/html/2310.12931v1)，§2、§3、§4、奖励示例附录。作者 Yecheng Jason Ma、William Liang、Guanzhi Wang 等。归档 `Eureka_2310.12931v1.pdf`。

[FACT] 把 reward 设计定义为求 $R$ 使固定学习算法 $\mathcal A$ 产出的策略在独立 fitness $F(\pi)$ 上好。提供环境源码和自然语言目标，采样奖励程序、训练、检查独立成绩与分项曲线，再迭代改奖励。论文每个环境5轮、每轮16候选，并做5次独立搜索；29环境的结果是 reward 搜索对特定算法/预算的经验成绩。

[PROVEN] 官方 [Eureka](https://github.com/eureka-research/Eureka) commit `9eee42808b52d8abc14845d1547bfde886403ccc`，`eureka/eureka.py:244–267` 同时读取原任务分数、生成reward及分项；`:288–289` 按 successes 选择；`:382` 最终读任务成绩。`eureka/envs/isaac/quadcopter.py:324–362` 的原参考任务是悬停接近(0,0,1)，以位置、姿态、自转成本组合并按位置失控重置，不能叫未知障碍导航。

[JUDGMENT] 可采用其“用真实失败轨迹解释分项怎样被优化，再做最少候选”的研究工作法，不必搭建自动LLM/GPU搜索框架。全部候选训练会显著占用预算；取训练过程最高score还可能选择过拟合结果，项目仍需固定独立同任务评价。实际分项数少不表示功能少，分项非零也不表示存在训练因果改善。

### P11 — Text2Reward：阶段门控与真实step接入，比增加名称更关键

**原文**：[arXiv v3](https://arxiv.org/html/2309.11489v3)、[ICLR 2024](https://openreview.net/forum?id=tUM39YTRxH)，§2–3、Appendix D。作者 Tianbao Xie、Siheng Zhao、Chen Henry Wu、Yitao Liu、Qian Luo、Victor Zhong、Yanchao Yang、Tao Yu。归档 `Text2Reward_2309.11489v3.pdf`。

[FACT] 用压缩环境描述和目标生成可执行 dense reward，支持 few-shot 和观察rollout后的人工反馈；验证 ManiSkill2、MetaWorld、MuJoCo，并有操纵真机展示。重要能力是自由使用状态条件组成阶段奖励，例如先接近物体，真正抓住后才支付放置进度。复杂StackCube的初始reward仍可失效，改善依赖初始候选质量与反馈。

[PROVEN] 官方 [text2reward](https://github.com/xlang-ai/text2reward) commit `e7f57efcf76b22bbfb7c3eb9d67d98ff2765a926`，`run_maniskill/ppo.py:32–43` 在真实step中换 reward，`:45–51` 用环境独立success结束，`:92–96` 注入生成函数。已读 `gold_reward_rewrite/pick_cube.py:20–28`，只有实际抓住才加物体到目标奖励；该文件是**人工oracle重写**，不是已证实的LLM输出，明确区分。

[JUDGMENT] 借鉴“安全可达情境才加入近目标效率”及实际branch审计，不借鉴操纵阶段标签本身。若门控借助全地图，它只能是训练奖励的特权信息，不能悄悄扩大actor观测；若临界几何导致门控闪烁，价值与信用会更难学。成本包括门控定义/状态一致性检查；不能只加配置字段而不修改实际调用公式。

### P12 — DrEureka：安全项的相互作用与环境分布共同决定效果

**原文**：[arXiv v1](https://arxiv.org/html/2406.01967v1)，§IV-B–D、§V及附录。作者 Yecheng Jason Ma、William Liang、Hung-Ju Wang 等。归档 `DrEureka_2406.01967v1.html`。

[FACT] 在任务描述中加入安全要求，联合探索奖励结构，再用 reward-aware physics prior 测试初始策略对物理参数的可承受范围，生成domain randomization。原文指出后加安全项可能压过任务项而保守退化；随机化过宽同样妨碍学习。验证四足前进、灵巧手和四足瑜伽球真机任务，非UAV避障。

[PROVEN] 官方 [DrEureka](https://github.com/eureka-research/DrEureka) commit `1d4e00700423170717654516f4ef4b24cb0f3a84`。`forward_locomotion/go1_gym/rewards/eureka_reward.py:49` 将velocity、height、orientation、joint-limit、smoothness**相乘**，并单独定义success；`forward_locomotion/go1_gym/envs/base/legged_robot.py:324–339` 区分原奖励求和分支与Eureka容器调用，`:1134–1140` 实际创建奖励类。

[JUDGMENT] 支持把安全、效率、任务分布和动作更新共同考察，不能把加大risk系数当成唯一解。乘积门控会在某个因子很小处同时压低任务梯度，当前强稀疏成功任务不应直接照搬。物理randomization适合部署研究阶段；当前训练空间硬终止语义错误要先改正，不能靠随机化或惩罚给错误边界找合理性。

## 5. 困难任务、危险接近与奖励规范方法卡

### P13 — PAIRED：困难课程应追逐“能成功但当前不会”的任务

**原文**：[arXiv](https://arxiv.org/abs/2012.02096)，PDF p4–8、Theorem1–2、Algorithm1。作者 Michael Dennis、Natasha Jaques、Eugene Vinitsky、Alexandre Bayen、Stuart Russell、Andrew Critch、Sergey Levine。归档 `PAIRED_2012.02096v2.pdf`。

[FACT] 训练环境生成者、主策略和对手策略，以同环境回报差 $U(\pi_A)-U(\pi_P)$ 作 regret。有限采样用对手最大回报减主策略平均回报近似。二者都无法解决的世界通常不带来高regret；主策略失败而对手成功的任务更受重视。验证迷宫导航及零样本迁移，非未知UAV实飞。

[FACT] 论文给出的“所有可解任务上成功”结论有明确条件：成功/失败回报区间分离，区间内波动小于区间间距、存在统一成功策略；minimax-regret/均衡还需最优响应或协调假设。它不是有限训练预算下的成功保证。原作者实现位于 [google-research/social_rl](https://github.com/google-research/google-research/tree/master/social_rl)，本轮读的是作者后续dcd实现，不混称原2020源码。

[JUDGMENT] 借鉴任务覆盖和恢复场景的可解性区分，避免一味增加不可能世界或只留容易世界。直接迁入三策略会增加采样与训练成本；当前可先用已验收训练世界族保持简单到达、必要绕行和恢复条件的覆盖，完整课程设计留待另案。eval-only w4/w8/w11/w12/w18不能进入训练或replay。

### P14 — ACCEL：编辑并筛选能力边界世界，不是删除失败样本

**原文**：[PMLR主源](https://proceedings.mlr.press/v162/parker-holder22a.html)、[arXiv](https://arxiv.org/abs/2203.01302)，PDF p4–5、Algorithm1及实验。作者 Jack Parker-Holder、Minqi Jiang、Michael Dennis、Mikayel Samvelyan、Jakob Foerster、Edward Grefenstette、Tim Rocktäschel。归档 `ACCEL_2203.01302v1.pdf`。

[FACT] ACCEL 在已发现世界上做少量修改，再评价regret，将高学习潜力世界留在level buffer。regret近似使用正值GAE/value loss的平均；学生使用原环境任务reward训练，regret用于选世界，不是给运动动作增加探索bonus。实验为迷宫、CarRacing、BipedalWalker；假设小环境编辑使regret较平滑变化，狭窄几何的可解性突变可能违背它。

[PROVEN] 官方 [facebookresearch/dcd](https://github.com/facebookresearch/dcd) commit `cefd88196f2696860e42405d7b32f47d3d12bbde`，`envs/runners/adversarial_runner.py:274–297` 计算PAIRED/flexible scores；`:548` 从真实环境取reward；`:651–652` 计算回报；`:929–1008` 编辑level后再评价，`:969–977` 对edited世界设置 `discard_grad=True`（同一调用的update字段仍为 `self.is_training`），不能只读update标签声称已训练或把它转述成 `update=False`。

[JUDGMENT] 当前优先借鉴“任务难度与学习潜力分开”，及固定家族保留简单成功机会。正value loss高也可能只是critic错误，不一定意味着世界可学；对当前critic历史信息缺口，直接用它重排全部任务会放大偏差。成本含level缓存与编辑/评价；本项目程序精简原则下，不建议立即另建完整UED平台或照搬“只训高regret”而丢失已成功任务。

### P15 — Back to Newton's Laws：安全成本可按接近行为变化，但不是PPO结果

**原文**：[arXiv v2](https://arxiv.org/html/2407.10648v2)、[期刊 DOI](https://doi.org/10.1038/s42256-025-01048-0)，§II-C—D、§III、补充S2/S4。作者 Yuang Zhang、Yu Hu、Yunlong Song、Danping Zou、Weiyao Lin。归档 `Newton_2407.10648v2.html`。

[FACT] 主方法通过可微点质点动力学反传整段loss，目标含2秒移动平均速度对目标方向的误差、障碍接近成本、加速度和jerk；每批64环境，每rollout150步，步长1/15秒。最近障碍接近速度影响安全成本，静止/远离时该因子为零。主论文比较了PPO基线，但不能把主方法改称深度RL/PPO。真机未知森林及动态障碍展示具有直接导航相关性。

[UNCERTAIN] 本次读到的arXiv HTML安全公式含 $\log(1+e^{\beta_2(d-r_q)})$ 且列出正 $\beta_2$，表面上会随净空增加而增加，与正文“近障碍barrier”描述不一致。未取得匹配源码或原公式页进一步排版核验，故不转录为可执行reward；仅采用已明示的接近速度门控思想。此处保留疑点，不擅自替作者改符号。

[JUDGMENT] 对R1的启发是把危险迫近、已安全远离和必要擦边区分，不能只把同一距离惩罚统一放大；同时保留真实碰撞后果，避免静止时所有安全/推进信号都消失。直接迁入可微仿真是高成本训练路线变化，不能在当前冻结DPPO上执行。物理loss中的jerk不提供对每轮轨迹绕行长度的自动判据。

### P16 — Reward Hacking：审查的是策略累计回报排序

**原文**：[arXiv](https://arxiv.org/abs/2209.13085)，PDF p5–6，Definition1、Theorem1、Corollary1。作者 Joar Skalse、Nikolaus H. R. Howe、Dmitrii Krasheninnikov、David Krueger。归档 `RewardHacking_2209.13085v1.pdf`。

[FACT] 两奖励相对于给定环境和策略集合，如果存在 $J_1(\pi)<J_1(\pi')$ 而 $J_2(\pi)>J_2(\pi')$，则为hackable。完整随机策略集合中，unhackable且非trivial的奖励必须在策略排序上等价；**等价非constant奖励也是unhackable**。不能转述成“所有非constant奖励都必然刷分”。有限策略子集可存在其他unhackable pair。

[JUDGMENT] 当前应用是把主终点 $F(\tau)=\mathbf1[\text{首次安全到达}]$ 与训练return排序分开核查，覆盖成功绕行、快速碰撞、近目标游走、无益循环和timeout。R1历史best阻止重复领进展，不等于已经证明全策略范围任务一致。也不能仅因训练reward正、成功率低就诊断reward hacking；可能没有找到return较高的成功动作或信用估计有误。本论文提供理论审查条件，没有UAV训练修复实验。

### P17 — Reward Design Perils：短视地评单个动作会误设任务

**原文**：[AAAI主源](https://ojs.aaai.org/index.php/AAAI/article/view/25733)、[正文PDF](https://ojs.aaai.org/index.php/AAAI/article/download/25733/25505)，§3–5、式(1)、Table2。作者 Serena Booth、W. Bradley Knox、Julie Shah、Scott Niekum、Peter Stone、Alessandro Allievi。归档 `Perils_AAAI2023.pdf`。

[FACT] 在Hungry Thirsty gridworld检验5196组reward和不同γ/LR，再用107组reward跨PPO/A2C/DDQN/Q-learning比较；独立任务指标是200步内满足饥饿的总次数。reward只有四种饥渴状态赋值，仍会对算法/超参过拟合。30位专家的观察研究发现部分人以单个状态动作好坏思考，而算法优化的是累计return；任务规范因此可能错误。

[FACT] 此研究是小型gridworld和受控reward设计研究；相关比例不是iDP3的故障概率。它区分“最优reward的任务规范错误”和“某算法预算内学不会”，两者必须各自验证。

[JUDGMENT] 这是本轮最直接的研究方法依据：先审完整轨迹排名与折扣，再审每轮进展/风险，最后审advantages及实际更新。当前同样无risk的必要退距与无益退距可有相同局部分数，但完整回合先成功后失败仍可能排序正确；这只能说明局部辨别与信用待查，不能直接宣布整套奖励无效。迁移成本低：复用已有统一评价和原轨迹做对照，不增加活动训练框架。

## 6. 对 R1 的综合判断：三个时间尺度分别审查

### 6.1 整回合结果、单轮分数和学习信用不能互相替代

[FACT] 当前Windows真实 `reward_v2_support/reward.py:70–122` 计算：

$$r_k=100\mathbf1_{reached}-50\mathbf1_{failure}+10\frac{b_k-b_{k+1}}{D_0}-\max(R_k^{exec},R_k^{tail})-0.05.$$

[FACT] $b_{k+1}$ 用真实执行连续线段的最近目标距离更新；tail只在未终止时参与风险，成功按真实前缀首事件。`build_system.py:119` 的信用时域为8；`critic_state.py:17` 提供 $\beta=b/D_0$。因此R1已有历史进展、连续三维前瞻和H8学习信用，不能按四个字段认定没有提前避障或恢复机制。

[PROVEN] 仅从当前源码奖励上界可推导：每回合newbest之和最多10、每次risk至多1、60次时间成本最多3。成功回合**未折扣**总分至少 $100-60-3=37$；timeout总分至多 $10-3=7$；碰撞回合总分小于−40。这个宽松区间说明当前整回合未折扣目标已明显偏向成功，不能凭某次绕行只有−0.05就说完整回报把失败排在成功前面。该推导不是γ=.99折扣后所有轨迹排序的证明，也不是actor能学到成功的证明。

[JUDGMENT] 单轮局部问题依然存在。历史best以下的有益回归、无益退距和安全停滞可同为−0.05；相同净进展的短直路和多折线路径可同分；近目标出现可安全入球方向却持续离开，说明已有稀疏终局和有限进展反馈未稳定形成所需行为。结合P06/P17，应分别查是否看见情境、是否估计未来价值、成功梯度是否实际更新，而非只增加所有奖励系数。

[PROVEN] γ=.99时，延后到达本身已经有较强折扣偏好：+100在第15/40次索引处的折扣贡献约86.01/66.90，差19.11；额外25次−0.05的未折扣成本仅1.25。“time系数小”不等于“总目标没有急于到达的压力”。该数值只是折扣代数例，不是当前轨迹重新评估结果。

### 6.2 状态充分性与任务时序

[FACT] R1当前只把 $b/D_0$ 加给critic。2026-10-12项目交接已提供真实函数反例：相同观测、相同当前距离和相同 $b/D_0$，不同 $D_0,b$ 可以对同一下一段路径支付不同newbest。因此“历史标量已接入”与“奖励状态信息充分”是不同结论。P01、P04、P06均支持审查critic可用信息，而非从字段数量判断。

[JUDGMENT] 下一版先让训练所需历史尺度可分辨；若加入情境门控、到达阶段或时间相关奖励，其状态也必须使价值估计可解释。60次预算若定义真正有限时域任务，剩余预算影响价值；若只是采样截断，则bootstrap语义不同。不能以教程名词替代用户任务的实际定义。补输入后也不能宣称已定因三seed退化。

## 7. 候选方向：只保留与具体失败机制有关的修改

| 候选 | 文献依据与实际用途 | 成本 / 主要失败模式 | 本轮判断 |
|---|---|---|---|
| 奖励状态补全与终止语义一致 | P01/P04/P06；分辨best、D0及必要的任务阶段，明确真正终止与预算截断 | 网络输入与权重兼容需核查；只补信息不保证学到新能力 | 有确定的输入歧义依据，应优先进入下一版审查 |
| 有界势能差分作为稠密方向提示 | P16/P17要求审全回报；具体PBRS证明由综合报告另行给出 | γ/terminal潜能/timeout bootstrap不一致会破坏目标排序；势能受阻时不能当可行距离 | 不替换成功主终点；现阶段仅影子重算与理论核验 |
| 条件局部效率成本 | P11的阶段奖励，P15的行为门控；在已有安全到达方向的近目标情境区分停滞和无益往返 | 全局或单凭未刷新best惩罚会压掉正确大绕行；门控不连续或privileged信息未供critic会增加歧义 | 与原近目标游走证据相关，保留候选，尚未定系数 |
| 风险对迫近与恢复响应 | P02/P05/P15；用运动方向/速度/时间到碰撞等具体信息调安全成本 | 系数乘risk0仍是0；扩大范围会罚正确窄通道；静止门控可能鼓励停住 | 先审风险覆盖与真实失败时刻；不能统一加大阈值作为结论 |
| 训练世界族保留简单到达与复杂可解任务 | P13/P14；学习难度取决于任务分布，维护可实现成功机会 | 只按critic误差挑任务可能放大信息缺口；只训困难世界可忘记简单成功 | 先复用现有采样/角色配额，不新建完整UED平台 |
| 微调更新与critic适应审查 | P06/P17；reward相似情况下仍可能遗忘 | 极低更新幅度/大KL束缚可能抹掉探索；训练曲线好看不能代替到达 | 与reward并列审查，不提前指定唯一原因 |

[JUDGMENT] 条件局部效率可先在原轨迹上比较 $L_{exec}$ 与净接近 $\max(d_{before}-d_{after},0)$：两条净接近1m的自由空间轨迹，1m直路与1.281m折线的“多走路程”分别为0与0.281m。**这不是通用绕行惩罚公式**：障碍阻断时合理外绕也多走且可能退距，必须保留其终局到达梯度；安全直达条件不存在时不得据此认定行为无益。低效成本还需区分原地不走、掉头和障碍恢复，不能仅靠路径长度一项解决所有问题。

[JUDGMENT] 如果有界潜能候选取 $\Phi(d,D_0)=-d/(d+D_0)$、$F=\eta(\gamma\Phi_{next}-\Phi_{now})$，则应把初始距离纳入奖励状态并在所有真终止统一 $\Phi=0$。从同一初始状态完整折扣和为 $-\eta\Phi_0=\eta/2$，表示改善局部提示而保持原整回合排序。对γ=.99、$0\le\eta\le4$，无newbest、无risk的hover最多获0.04势能增益，配−0.05仍为负；相同奖励状态的完整循环也有这一成本上界。**这些是候选的代数性质，不是已批准系数、不说明真实训练一定提高到达。** timeout按真正有限预算终止或采样截断处理须先裁决；不能只对成功把潜能清零。

### 7.1 三种候选失败模式应在现有证据上先排除

1. **压掉必要绕行。** 成功S形柱链外绕早期进展较小，不得以未刷新best、飞高或横移本身追加失败；新评分须保留它完整成功优于失败路线，并报告早期局部分数和累计分数。
2. **维护简单任务仍失败。** 近goal且有安全几何方向时，候选必须能区分低效往返与持续入球推进；若只在碰撞危险处增强风险，不能指望风险0的简单世界自然被修复。
3. **局部分项有变化而信用无变化。** 影子reward重新排序不说明训练改善；后续新训练要核查success/failed条件advantages、实际actor更新与原H8信用，再看完整固定同任务safe-arrival。

## 8. 合规与后续使用

[FACT] 当前测试v3取消z>6m和xy±30m人工终止，保留真实碰撞、触地和原60次预算；训练端尚待未来reward一起调整。扩大允许xyz不等于新增空间软罚已经实现，也不能把原有限域结果直接重标签为新成功。

| 项目约束 | 本材料的使用方式 |
|---|---|
| MC-1 输出=执行轨迹 | 局部效率/风险仅作训练评分；不执行直连检查构造的轨迹，不后处理修剪 |
| MC-2 Diffusion核心 | 不迁入状态生成+逆动力学替换当前策略，不把外部控制器收益归因于LoRA |
| MC-3 学习阶段约束 | 候选用于未来批准训练；不加推理后轨迹改写 |
| MC-4 frozen EGO | 不迁入DAgger重采或新PRM专家示范；已有数据可复用 |
| MC-5 归因可分离 | 同一实际RL分支评价；不把BC接管、A*帮助执行或extra安全层算学习效果 |
| H4/原轨迹/eval-only | 保持现执行时域、完整原件和隔离世界，未来比较统一入口运行 |
| 有效学习信号 | 不丢掉困难样本或普遍压低更新来维护曲线；同时观察复杂收益与简单成功 |

[JUDGMENT] 可用于综合报告的主结论是：**R1的整回合成功偏好、局部行为辨别、价值估计信息和微调更新需要共同判断。** 文献支持保留历史最好/首次到达/前瞻风险的合理功能，先修人工空间语义与状态信息，再以少量条件候选补当前明确失败；未支持一个可直接照搬、保证改善iDP3三个能力目标的完整reward。

## 9. 官方源码证据表与归档说明

| 仓库 | 已读实际实现 | 固定commit日期 | 证据边界 |
|---|---|---|---|
| arplaboratory/learning-to-fly | active squared reward、参数选择、curriculum、replay reward重算 | 2025-05-22 | RPM位置控制，非障碍规划 |
| real-stanford/diffusion_policy | 完整预测与action前缀选择 | 2024-12-24 | BC执行方式，非RL信用证明 |
| jannerm/diffuser | 去噪内value指导、真实env.step、整段折扣目标 | 2022-12-21 | 离线计划任务 |
| eureka-research/Eureka | reward生成/训练/score选择、quadcopter原任务 | 2024-05-03 | 奖励搜索与悬停，非UAV障碍能力 |
| xlang-ai/text2reward | step注入、独立success、人工oracle条件奖励 | 2024-12-17 | 操纵例子；oracle不标LLM输出 |
| eureka-research/DrEureka | 乘积reward、独立success、实际容器分支 | 2024-08-26 | 四足例子，不直接迁数值 |
| facebookresearch/dcd | 实际环境reward、regret计算、编辑世界再评价 | 2024-08-20 | PAIRED/ACCEL后续作者实现 |

[FACT] `connector_source_inventory.json`记录14份已读源码的来源commit、GitHub blob SHA和本地SHA256，覆盖7个仓库；13份插件副本机械还原末尾与换行后、1份HTTP原件均核对Git blob SHA完全一致。`archive_manifest.json`记录本地实际文件SHA256。直接HTTP失败和GitHub插件补取分别记录；源码快照仅存于论文归档目录，不成为项目运行入口。`papers.json`提供逐篇书目、用途、原文状态与阅读定位。
