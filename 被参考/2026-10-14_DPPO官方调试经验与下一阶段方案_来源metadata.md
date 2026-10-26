# DPPO官方调试经验与下一阶段方案的来源

检索日期：2026-10-14。用途：审查用户提供的四份材料，制定可复用的训练调整候选。材料直接保存到已有文献目录；不创建新的文献文件夹。项目实际效果仍由训练与原轨迹裁决。

| 来源 | URL / 标识 | 核实内容与适用边界 | 本地原件 |
|---|---|---|---|
| DPPO官方论文 | https://arxiv.org/html/2409.00588v3 | 两层MDP、条件去噪似然、探索及微调实践；不证明本项目长训原因 | 既有2026-10-12_RL_Reward综合研究/metadata/2409.00588v3.pdf及算法TXT |
| DPPO官方loss | https://github.com/irom-princeton/dppo/blob/main/model/diffusion/diffusion_ppo.py | clamp/mean、先标准化后去噪折扣确属上游；可选教师损失不是本地已经启用 | 既有DPPO_diffusion_ppo.py.txt；本地vendor亦逐段核读 |
| 官方批量调整案例 | https://github.com/irom-princeton/dppo/issues/27#issuecomment-2560754523 | 作者按去噪步数扩批并更新配置；v0.8称恢复原D3IL表现。不是无人机参数处方，也未取得报告者独立复现记录 | DPPO_issue27_作者讨论_20261014.json |
| 官方评价纠偏案例 | https://github.com/irom-princeton/dppo/issues/34#issuecomment-2634554672 | 预训练/微调checkpoint识别曾需修正；Kitchen归一得分不是全部四阶段成功率。作者及报告者确认修正可运行 | DPPO_issue34_作者讨论_20261014.json |
| 官方v0.8及当前main身份 | https://github.com/irom-princeton/dppo/releases/tag/v0.8 ; https://api.github.com/repos/irom-princeton/dppo/commits/main | cc7234a基点与release用途；不得虚构本地尚缺某个上游新补丁 | DPPO_v08与main身份_20261014.json |
| D3IL正式配置 | https://github.com/irom-princeton/dppo/blob/main/cfg/d3il/finetune/avoid_m1/ft_ppo_diffusion_mlp.yaml | batch包含环境与去噪配对；有1轮critic预热。模型、动作与奖励不同，不照抄全部系数 | DPPO_avoid_m1配置_cc7234a.txt |
| 官方训练入口及参数 | https://github.com/irom-princeton/dppo/blob/main/agent/finetune/train_ppo_diffusion_agent.py ; https://github.com/irom-princeton/dppo/blob/main/agent/finetune/train_ppo_agent.py | reward_horizon默认act_steps；actor更新延后以预热critic；teacher coefficient与target KL接口存在。仅是上游可用机制，不自动成为本地功能 | DPPO训练入口_时域定义_cc7234a.txt、DPPO训练入口_更新预热与KL_cc7234a.txt、DPPO训练参数_教师与预热_cc7234a.txt |
| DPPO配置经验 | https://github.com/irom-princeton/dppo/blob/main/cfg/finetuning.md | 官方曾提高actor LR及改变更新参数以提高样本效率，不支持学习率越小越好 | DPPO_finetuning_cc7234a.md |
| 时间限制研究 | https://proceedings.mlr.press/v80/pardo18a/pardo18a.pdf ; arXiv:1712.00378 | 区分任务期限与人为采样截断；前者需要时间信息、后者保留bootstrap | Pardo2018_Time_Limits_in_Reinforcement_Learning_arXiv1712.00378.pdf |
| 有限时域势函数研究 | https://arxiv.org/html/2404.07826v1 | 终端势函数残项与策略排序偏差；有界函数也必须处理边界 | 既有2026-10-12_RL_Reward综合研究/potential_shaping/SampleEfficiency_2404.07826v2.html |
| Agile Flight | https://arxiv.org/html/2403.12203v3 ; arXiv:2403.12203 | critic预热、依表现调整更新；有微调退化实例。非扩散、输出控制量，不直接复用为轨迹算法 | 既有2026-10-12_RL_Reward综合研究/planning_reward/Bootstrapping_2403.12203v3.pdf |
| FLaRe | https://arxiv.org/html/2409.16578v2 ; arXiv:2409.16578 | 小步更新、无熵奖励、actor与critic梯度分离具有消融依据。本地已具其中多项，不能重复当作新增解决方案 | FLaRe_2409.16578v1.html；本次在线复核v2 |
| FDPP | https://arxiv.org/abs/2501.08259 | 固定参照逐去噪KL与原任务/新偏好取舍；没有零能力损失保证 | 既有2026-10-12_BC成功能力保持_文献与官方源码/FDPP_2501.08259v1.pdf |
| SB3官方调试经验 | https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html | 核对环境、观测、终止、评价wrapper及训练随机性；不是新建一套PPO或更改本项目normalizer的依据 | SB3_RL_tips_20261014.html |

新保存的六份Github评论/代码资料保留原URL、作者或blob SHA，来源内容与本项目建议分开。main/release原API另保存原对象。报告不复制评论中的图片、邮件通知链接或其他无关内容。

本次候选距离函数与6/4系数是项目设计建议，不冒充论文已验证的无人机参数；实际原轨迹评分保存于研究报告目录的候选评分JSON，尚无该候选的新训练结果。

## 2026-10-14补充：环境分布、复访与并行采样

| 来源与年份 | URL / arXiv | 引用用途及项目限制 | 本地原件与核验 |
|---|---|---|---|
| Procgen，ICML2020 | https://proceedings.mlr.press/v119/cobbe20a.html ; https://proceedings.mlr.press/v119/cobbe20a/cobbe20a.pdf ; 1912.01588 | 训练布局数量与泛化的实验依据；游戏观察/动作与UAV不同，不能把其关卡数当本项目所需数量 | Procgen_ICML2020_arXiv1912.01588.pdf；9页；2804503 bytes；SHA256 1a3292f3dbf2187a2254cceb8af970c1022154ce90b9ae1ebb7de5a4d51c712a |
| Prioritized Level Replay，ICML2021 | https://proceedings.mlr.press/v139/jiang21b.html ; https://proceedings.mlr.press/v139/jiang21b/jiang21b.pdf ; 2010.03934 | 有学习价值的布局复访与level分布选择；复访关卡重新采on-policy数据，不是旧轨迹PPO replay；暂不复制整个优先框架 | Prioritized_Level_Replay_ICML2021_arXiv2010.03934.pdf；11页；2161126 bytes；SHA256 0da6131e2c8adef29fa096131b9e6f2c73e47fc92a8e03ad0eb985915321e878 |
| NavRL，RA-L2025 | https://github.com/Zhefan-Xu/NavRL ; https://arxiv.org/abs/2409.15634 | 官方1024机器人/350静态障碍训练例支持批量环境组织可行；不同机器人实例不自动等于不同世界。其速度动作、Isaac和部署屏障不直接复用 | NavRL_README_20261014.md；2026-10-14下载；既有NavRL论文和env快照复用，不再复制一份论文 |

两份新增PDF验证了PDF文件头、页数及第一页题名；README与线上官方项目核对。均直接存已有本目录，未新增文献子文件夹。空间椭球公式与C_s=1/3为项目候选，不冒充这些论文提出或验证的参数。应用核查见现有下一阶段方案§15—17；原轨迹自动重评分见研究报告目录的空间渐进成本JSON。

## 2026-10-15 v3分析后的复核

再次在线打开DPPO #27及v0.8、FDPP（2501.08259）和FLaRe（2409.16578）的官方页面，并复读本目录原作者评论及已保存全文/源码资料；原件复用，未新建文献文件夹或重复下载。v0.8明确列出D3IL更大batch配置修正；#27作者回复原文仍以既存API副本为准，页面本次未完整加载评论。

引用用途：将更新组织与进展reward列为首轮竞争候选，把固定BC保持列为独立路线。没有将官方D3IL配置当作本地UAV已验证修复，也未把FDPP的任务结果外推为零能力损失保证。本地v3和393216训练transition的实际GAE、KL与轨迹结果见`jindu/2026-10-15_RouteA_v3开放空间全策略轨迹分析与下一阶段方案裁决_v1_0.md`。本次未再次查询main API，main身份只沿用明确标注日期的10月14日核验。

## 2026-10-15补充：滚动规划reward原则与预训练能力保持

对应研究判断：`论文/研究报告/2026-10-15_滚动规划Reward原则与BC能力保持_研究判断_v1_0.md`。该报告§7逐项记录13篇论文与SB3官方指南的URL/arXiv、引用用途、局限和既有本地原件。Ng1999与Pardo2018为必要基础，其余论文为2021—2025年；不以少数方法当成已穷尽全部研究。

本次复用既有DPPO、FDPP、FLaRe、DSRL、Diffusion Policy、PBRS、MPC、Agile Flight、IBRL、RLPD与reward hacking原件；在线复核具体章节/表格和作者项目，不复制已有论文或建立文献子目录。补充的作者README原文直接下载到本目录，属于自动生成的来源副本，未改写其内容：

| 来源原文 | URL | 文件与完整性 | 引用用途 / 限制 |
|---|---|---|---|
| DSRL官方README | https://raw.githubusercontent.com/ajwagen/dsrl/main/README.md ; https://github.com/ajwagen/dsrl | `DSRL_official_README_20261015.md`，4580 bytes；SHA256 `83b5b09b5edb4380573aeaf9dfede9f5b1daf0404c91bc34857b473d6bdbe298` | 核实冻结基座、初始噪声控制、DDIM要求；当前E5本已有DDIM，仍需接口与算法适配，不是直接替换 |

本次再次打开DPPO固定cc7234a原始loss URL：`https://raw.githubusercontent.com/irom-princeton/dppo/cc7234ad7ff39a8f32de3af903606723a16f0648/model/diffusion/diffusion_ppo.py`，确认97—118行可选教师链辅助项。来源继续复用既有官方源码TXT，不把本地关闭/未实现分支描述为已启用。

FDPP v1式(20)(21)的正KL与最大化方向存在符号含义不一致；正文是限制偏离。研究报告自行采用最小化loss加非负成本，未冒充原式。其Push-T表II为98%→90%，保留能力不等于零损失。DSRL冻结原权重也不保证组合策略保持每个旧任务；这些均作为迁移限制记录。

同日BC辅助损失提议审查追加于上述报告§9。补充使用AWAC（2020，arXiv:2006.09359，https://arxiv.org/pdf/2006.09359）§IV的KL与加权最大似然关系，原件复用`2026-10-12_BC成功能力保持_文献与官方源码/AWAC_2006.09359v1.pdf`；用途是区分教师NLL与KL方向，不把其离策略更新移植为PPO补丁。主体13篇加该篇共14篇。再次核对DPPO固定cc7234a原loss的clamp/mean教师项、FDPP §V-D及IBRL附录A；未新增文献文件或文件夹，未据通用文字确定λ或后期衰减。BC与KL均为软惩罚、加入后总优化目标改变；现有本地无固定BC惩罚项。Spinning Up PPO及TD3+BC页面仅作检索背景，未作为该审查结论的依据。

同日架构讨论纠正：`third_party/dppo_official_cc7234a/uav_idp3/e5_runtime.py:230、238—241`与fresh训练快照相同，实际为DDIM、预测x0；训练随机DDIM Gaussian、统一评价确定性DDIM（初始噪声仍随机）。原“当前DDPM需改DDIM才能研究DSRL”的判断不准确，已在研究报告§5.3及表格纠正。该纠正降低采样家族适配门槛，不是证明DSRL有效或已经接入。
