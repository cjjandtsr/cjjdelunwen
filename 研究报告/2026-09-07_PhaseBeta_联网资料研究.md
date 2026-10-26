# Phase β 联网资料研究：安全到达退化、终止语义与导航后训练

检索日期：2026-09-07（Asia/Shanghai）。文档类型：定期研究报告；状态：资料核验完成，建议待后续证据裁决；不是新算法定稿或执行指导。

## 1. 本期项目上下文摘要

[FACT] 当前主线为 E5 点云条件 DDPM BC + 碰撞辅助损失 + Official DPPO Core + Reward v1.7，执行 H=4、每点0.3s。AGENTS.md 中 FM 主力、Phase α 待重测和 w4+w18 训练等历史文字不能作为当前状态。当前依据是 9月5日主交接顶部的9月6日更新及下列独立复核。

[FACT，来自本地复核报告，非本轮重跑] `jindu/2026-09-06_Reward_v17_44对轨迹独立复核与系统归因.md` §1–5记录：Seed1完成256/256；原128对安全到达BC35、RL22，即27.34%→17.19%，下降10.16个百分点；17对丢失成功、4对新增。44对/88回合/3908步是诊断子集，不能拿44作总体成功率分母。1对初始点云hash不同，但17对丢失及4对新增的初始输入hash均相同，不能以该异常抹掉主要下降。

[FACT，来自同一复核] 高空停滞累计BC70.004s、RL272.956s；两个fallback帧均未进入actor latest3，不能据此排除稀疏非空点云、视场或编码域偏移。当前是kinematic位置推进，没有PX4跟踪动力学，不能归因于飞控50Hz控制滞后。

[FACT] 本轮读取/搜索了AGENTS.md、sheji/、zhidao/、jindu/及论文三类资料目录；`program/jindu/jindu.txt`不存在。直接读取Reward v1.7设计v1.4开头、fixed32轨迹补录指导、论文框架v1.6相关条目、9月5日论文交接、9月6日轨迹复核、8月31日续接研究及当前GAE源码。旧设计的“尚未实现”是版本形成时状态，已被新交接覆盖。本轮未访问外部执行仓库、未训练、未操作ROS/Gazebo/PX4。

[FACT] 自动化memory最新条目停在8月10日，而调度Last run为8月31日；本轮通过仓库8月31日至9月6日资料补齐，不能把memory断档说成期间没有研究。

## 2. 检索范围与关键词

[FACT] 检索覆盖经典2017–2025年基础资料及2026年导航/安全RL/FM更新；优先查看8月以来资料，时间上限为2026-09-07。实际查询包括 `site.arxiv.org UAV diffusion policy obstacle avoidance 2026 reinforcement learning`、`diffusion policy reinforcement learning safe navigation August 2026`、`AvoidBench aerial robots obstacle avoidance benchmark`、`point cloud policy 2026 navigation August`、`flow matching policy reinforcement learning August 2026`，并定向核验DPPO、DSRL、ReinFlow、iDP3、Time Limits原始arXiv页。

[JUDGMENT] 本期增量是将最新安全终止研究与当前端点退化连接，补强已有诊断问题；不再重复“需要RL”“换FM就能解决”的泛化论证。搜索聚合页只用于发现，结论仅依据原始arXiv或出版商页面。未声称穷尽全部近期论文，也没有确认9月首周存在更适合当前问题的新算法。

## 3. 候选资料总表

[FACT] 下表年份区分首发/会议年；“采纳”表示用作研究依据，不表示采用算法。每个arXiv编号同时对应DOI `10.48550/arXiv.<编号>`。本轮新归档为元数据说明，既有PDF不重复下载。

| ID | 标题、作者、年份 | 原始来源 / ID | 下载与采纳裁决 |
|---|---|---|---|
| A | Arrive and Survive: Scaling Safe Goal-Conditioned Policy Learning from One-Bit Failure Signals；Guopeng Li, Yiyang Duan, Yiru Jiao, Chengcheng Xu；2026 | https://arxiv.org/abs/2608.26571 （8月27日首发） | 采纳作终止偏差线索；新增元数据，未下载PDF |
| B | Time Limits in Reinforcement Learning；Fabio Pardo, Arash Tavakoli, Vitaly Levdik, Petar Kormushev；2017/ICML 2018 | https://arxiv.org/abs/1712.00378 （v4） | 采纳作时限语义依据；新增元数据，未下载PDF |
| C | X-NavDP: Generalizing Navigation Diffusion Policy to Novel Behavior and Embodiments with Group Q-score Reweighted Matching；Tianyu Yang, Yiming Zeng, Wenzhe Cai, Yuqiang Yang, Jiaqi Peng, Hui Cheng, Jiangmiao Pang, Tai Wang；2026 | https://arxiv.org/abs/2607.28560 （v2，8月11日） | 采纳密集/死胡同问题定位；既有X-NavDP PDF，不重复下载 |
| D | Diffusion Policy Policy Optimization；Allen Z. Ren, Justin Lidard, Lars L. Ankile, Anthony Simeonov, Pulkit Agrawal, Anirudha Majumdar, Benjamin Burchfiel, Hongkai Dai, Max Simchowitz；2024 | https://arxiv.org/abs/2409.00588 （v3） | 采纳基础算法归属；既有PDF及摘要快照 |
| E | AvoidBench: A high-fidelity vision-based obstacle avoidance benchmarking suite for multi-rotors；Hang Yu, Guido C. H. E. de Croon, Christophe De Wagter；2023 | https://arxiv.org/abs/2301.07430 （v1） | 采纳环境复杂度与真实飞行证据分层；既有PDF |
| F | Generalizable Humanoid Manipulation with 3D Diffusion Policies；Yanjie Ze, Zixuan Chen, Wenhao Wang, Tianyi Chen, Xialin He, Ying Yuan, Xue Bin Peng, Jiajun Wu；2024/IROS 2025 | https://arxiv.org/abs/2410.10803 （v3） | 采纳点云策略来源与任务边界；既有PDF及摘要快照 |
| G | ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning；Tonghe Zhang, Chao Yu, Sichang Su, Yu Wang；2025/2026修订 | https://arxiv.org/abs/2505.22094 （v7） | 本期不采纳为新增建议；既有PDF，本期不新增归档；未解决当前归因缺口 |
| H | Steering Your Diffusion Policy with Latent Space Reinforcement Learning；Andrew Wagenmaker, Mitsuhiko Nakamoto, Yunchu Zhang, Seohong Park, Waleed Yagoub, Anusha Nagabandi, Abhishek Gupta, Sergey Levine；2025 | https://arxiv.org/abs/2506.15799 （v2） | 本期不采纳；既有PDF不动；回到冻结基策略的latent RL需独立路线论证 |
| I | Flow Matching Policy Optimization with Mirror Descent and Entropy Constraints；Ting Gao, Stavros Orfanoudakis, Nan Lin, Elvin Isufi, Winnie Daamen, Serge Hoogendoorn；2026 | https://arxiv.org/abs/2603.17685 （v3） | 不下载、不采纳；搜索旧题为Flow Matching Policy with Entropy Regularization，以当前原始页为准；算法更换无直接UAV证据 |
| J | Temporally-Aware Deep Reinforcement Learning for Dynamic Obstacle Avoidance in UAVs；Chang Liu, Shan Wang；2026 | https://doi.org/10.3390/drones10070505 | 不下载、不采纳；动态任务且含velocity-projection safety shield，主结果归因不符合本项目边界 |

## 4. 被采纳资料与核心贡献

### A. Safe-CRL：只借用问题意识

[FACT] 原摘要指出，failure-terminated MDP中，对比RL仅用失败前未来目标构造正例，可能忽略被失败移除的概率质量；提出mass-weighted InfoNCE及log-survival-mass修正。[原始来源](https://arxiv.org/abs/2608.26571)

[JUDGMENT] 这支持审查“到达价值是否忠实反映失败”，但当前DPPO没有InfoNCE目标，不能把该修正直接加到PPO或认定同一偏差已发生。[UNCERTAIN] 本轮仅核验摘要，未复核其证明与实现，不能用其机器人实验替代UAV结论。

### B. Time Limits：当前最直接的理论对照

[FACT] 论文区分任务本身的有限期限与训练采样的人工截断：前者需要剩余时间信息以避免状态混叠，后者应在部分回合末端bootstrap。[原始来源](https://arxiv.org/abs/1712.00378)

[FACT] 本轮直接读取 `chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/engine/gae.py:16`：bootstrap mask为 `1-terminated`，GAE continuation为 `1-(terminated OR truncated)`。

[JUDGMENT] 首先确认60步是任务期限还是采样限制，并用真实最终配置核对调用方传入的末状态value。上述实现可符合人工截断语义，不能仅因超时bootstrap就判bug；如果任务真是有限时限且输入缺失剩余时间，则存在需要明确的建模差异。本文不要求现在改state维度或重算评估成功。

### C. X-NavDP：密集恢复与局部观测的相关工作

[FACT] 论文面向局部观测下死胡同、长障碍绕行及跨具身导航，提出行为扰动探索与group Q-score reweighted matching。[原始来源](https://arxiv.org/abs/2607.28560)

[JUDGMENT] 可作为“BC覆盖不足时需检查探索与候选动作价值排序”的相关工作。当前DPPO使用state value而非该方法的轨迹Q，不能直接搬用组内权重；也不能把其跨具身导航成功率外推为本项目三维UAV收益。本文仅据摘要做方法定位，既有PDF版本尚未与远程v2做字节同一性核验。

### D–F. 基础来源与证据分层

[FACT] DPPO提供扩散策略的policy-gradient后训练框架，并报告操作等任务的仿真到真实部署；它是当前算法基础，不是UAV安全到达保证。[来源](https://arxiv.org/abs/2409.00588)

[FACT] AvoidBench将环境复杂度指标与避障性能结合，并包含真实飞行趋势验证；其RotorS/Unity系统不同于当前kinematic环境。[来源](https://arxiv.org/abs/2301.07430)

[FACT] iDP3原工作是点云条件的人形操作系统及策略学习，不是无人机规划。[来源](https://arxiv.org/abs/2410.10803) [JUDGMENT] 本项目应明确适配来源，通过自身观测/动作/任务证据验证三维泛化，不能以编码器名字或原论文跨场景表现推定UAV full-space能力。

## 5. 未采纳资料与原因

[JUDGMENT] G/H保留历史文献地位但不新增路线建议：一个单seed端点下降尚不能分离表示、训练覆盖、优化和reward；此时换ReinFlow或DSRL会引入额外变量。I属于另一FM优化体系，当前无需为凑近期文献而替换DDPM核心。J的速度投影会修改策略动作，其带shield表现不能归因于纯策略学习；也不适合作为未知静态三维轨迹规划的直接同口径比较。

[FACT] 本期只看过但未用于采纳结论的G–J没有新增到被参考目录。已有G/H历史归档不会因本期未采用而删除。

## 6. 对 iDP3-UAV 的可迁移建议

[JUDGMENT] 本期建议是诊断与评估层面的证据补充，不新增模型、reward项或实现任务；与9月6日P0/P1顺序一致。

| Phase β目标 | 可迁移问题与具体检查 | 判定边界 |
|---|---|---|
| 提前避障 | 固定开发观测及采样seed，对比BC/RL的H4轨迹、最小间距、横移/偏航与净趋近；结合观测可见性解释onset | 更早转向必须最终安全到达；间距扩大但远离目标不算提升 |
| full-space support expansion | 按冻结示范密度分层x/y/z状态，关联非空点云hit比例、目标进展和safe arrival；复核归一化及actor实际输入 | 高度、坐标跨度或停留时长不是能力；示范稀疏状态经验鲁棒性不等于任意全空间泛化 |
| dense-obstacle capability ceiling | 按真实几何和预定义trap opportunity分层，区分局部可见绕行与视野外拓扑需求；同输入检查选路改变及成功样本优势 | 不按world标签直接断言脱困；有限历史不能保证解决任意死胡同 |

[JUDGMENT] 时间语义审查记录两套mask的含义、最后真实状态和value来源，并分成功/碰撞/超时比较已有advantage统计；缺失逐样本记录必须明示，不能事后伪造历史梯度。这里没有证据支持删除hard samples、削弱成功信号、提前停训或放宽到达阈值。

[JUDGMENT] 机制验证用独立开发world；固定测试集只诊断输入配对与日志，不用于调参。后续能力裁决保留原128对及环境分层，多seed结果未齐前不宣称可复现提高；CI应说明world/config依赖，不能把同world的4个配置当完全独立环境样本。

## 7. MC 合规检查

| 约束 | 本期裁决 |
|---|---|
| MC-1 策略输出=执行轨迹 | [JUDGMENT] 保留原H4路径，不做GOAL-TRUNC、平滑、障碍排斥或速度投影 |
| MC-2 diffusion核心 | [JUDGMENT] 保留DDPM/DPPO；相关FM/latent RL不自动变成主线 |
| MC-3 学习阶段处理约束 | [JUDGMENT] 仅审查训练目标与终止语义，不新增推理后安全shield |
| MC-4 EGO frozen | [JUDGMENT] 只读示范密度与统计，不重采集；w4/w8/w11/w12/w18保持eval-only，不进入训练/replay |
| MC-5 归因可分离 | [JUDGMENT] 区分M2基础任务DPPO与M3完整reward、观测/优化/reward机制，以及kinematic、Gazebo/PX4与实物证据 |

[JUDGMENT] 策略内训练loss、reward、denoising优化可被研究；其他规划器也能套用的post-hoc修轨不计策略能力。未建议yaw_loss_boost>1、5d动作、DAC offline RL、TransDiffuser decorrelation或torch.compile+CFG；保持11d step-wise动作和当前H4合同。未来H8必须独立标定，不能由本报告直接开启。

## 8. 风险与不确定性

- [UNCERTAIN] 当前根因未定。单seed下降是真实端点信号，但不能证明DPPO不适用或reward是唯一原因；44对是定向诊断子集。
- [UNCERTAIN] A/B本轮经web工具读到原始摘要，PowerShell下载摘要HTML遇SSL错误；已保存元数据与有限内容转述，不声称下载了全文或验证了全文证明。其他引用复用既有资料，不声称重新阅读全文。
- [JUDGMENT] Safe-CRL与DPPO的目标函数不同；误用理论会造成错误修复。先核对具体mask与任务定义，证据指向后才另立设计。
- [JUDGMENT] 同闭环不同状态的观测质量与动作差异具有双向因果，必须用同输入配对控制；无fallback不等于无感知问题。
- [JUDGMENT] 稳定化可能抹平学习信号；任何后续更改必须保留动作多样性、actor更新、成功条件优势与dense失败样本，不以平滑曲线代替安全到达。
- [FACT] 本报告未更改生产代码、训练配置、评估阈值或项目状态文件；没有新增可宣称为Gazebo/PX4或实物的结果。

## 9. 下一步建议

1. [JUDGMENT] 先完成9月6日既定P0：解释唯一reset点云hash差异，拿原始数组区分排列/数值/采样变化，测同输入动作影响；不篡改原端点结局。
2. [JUDGMENT] 按既定P1取得真实final resolved config与已存在的成功/超时/碰撞学习信号，核对60步任务语义及GAE末状态value；这比新增算法试跑更直接。
3. [JUDGMENT] 证据指向优化/遗忘或reward排序后，再选择单变量设计；若需新设计，进入sheji及Zread流程，本报告不代替定稿或指导文件。
4. [JUDGMENT] 下期以P0/P1是否关闭为入口；优先查已有训练统计与同输入差异是否支持具体机制，不再泛扫DPPO/ReinFlow/DSRL。论文继续以安全到达为唯一主要终点，不预写正结果。

[FACT] 归档入口：`论文/被参考/metadata/2026-09-07_PhaseBeta_联网资料研究_metadata.md`；资料转述：`论文/被参考/2026-09-07_PhaseBeta_联网资料研究_sources.md`。
