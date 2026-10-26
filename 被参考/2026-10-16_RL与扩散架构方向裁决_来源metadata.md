# RL与扩散架构方向裁决：来源metadata

- 检索、阅读与归档日期：2026-10-16。
- 用途：比较继续RL与实质非RL架构转向；全部为研究建议，未运行外部训练或实机。
- 主报告：`论文/研究报告/2026-10-16_继续RL还是转向扩散策略架构_证据比较与下一阶段裁决_v1_0.md`。
- 逐项实际阅读位置、方法、消融/反证、监督依赖与适配：`论文/研究报告/2026-10-16_RL与扩散架构方向裁决_原文阅读与迁移证据.md`。
- 去重口径：36篇不同论文；同论文不同版本只算1篇，HDP两人阅读不重复；README、源码、issue、指南与项目页不计论文数。包含2020—2026论文；不是声称每篇每页均已读或已独立复现。
- 新增来源直接放既有`论文/被参考/`，未新建文献子目录。历史已存在的子目录仅复用，不迁移或覆盖。

## 1. 论文索引与实际用途

| 编号 | 论文 / 年份、标识与原文 | 本次用途与相关性 |
|------|--------------------------|--------------------|
| R01 | DPPO，2024/2025，[2409.00588](https://arxiv.org/abs/2409.00588) | 最直接的扩散连续机器人后训；不使用固定BC正则也可提高，需限定迁移条件 |
| R02 | DSRL，2025，[2506.15799](https://arxiv.org/abs/2506.15799) | 固定生成器的竞争RL；受可引导性与历史Route B风险限制 |
| R03 | ReinFlow，2025，[2505.22094](https://arxiv.org/abs/2505.22094) | flow随机链后训；E5不是flow，不能即插 |
| R04 | DiPOD，2026，[2606.13795](https://arxiv.org/abs/2606.13795) | 区分ELBO/似然漂移与BC遗忘，机器人不属于BC后训 |
| R05 | FDPP，2025，[2501.08259](https://arxiv.org/abs/2501.08259) | fixed-reference KL的收益与代价；不保证原任务零损失 |
| R06 | D²PPO，2025/2026，[2508.02644](https://arxiv.org/abs/2508.02644) | 表示预训练与后训的相互影响；不构成新架构 |
| R07 | AWAC，2020/2021，[2006.09359](https://arxiv.org/abs/2006.09359) | 旧数据保留与在线改进；非PPO补丁 |
| R08 | RLPD，2023，[2302.02948](https://arxiv.org/abs/2302.02948) | 混合数据、critic与UTD组织；非固定BC项 |
| R09 | Cal-QL，2023，[2303.05479](https://arxiv.org/abs/2303.05479) | critic值尺度可造成unlearning；不直接给本地PPO定因 |
| R10 | IBRL，2023/2024，[2311.02198](https://arxiv.org/abs/2311.02198) | 保留IL候选与表示差异；原执行核心需重新审MC-2 |
| R11 | Bootstrapping RL with IL for Vision-Based Agile Flight，2024，[2403.12203](https://arxiv.org/abs/2403.12203) | 与早期提高后期退化相近的UAV证据；teacher/DAgger及动作不同 |
| R12 | FQL，2025，[2502.02538](https://arxiv.org/abs/2502.02538) | 策略提取影响性能；最终one-step actor不是当前扩散执行核心 |
| N01 | Diffusion Policy，2023/2025，[2303.04137](https://arxiv.org/abs/2303.04137) | 滚动生成/执行、CNN/Transformer、BC分布偏移；本项目已属此家族 |
| N02 | DP3，2024，[2403.03954](https://arxiv.org/abs/2403.03954) | 点云表示与简单模型反证；不能重新当待引入路线 |
| N03 | iDP3，2024/2025，[2410.10803](https://arxiv.org/abs/2410.10803) | 当前编码器背景及消融；不是全SE3等变策略 |
| N04 | 3D Diffuser Actor，2024/2025，[2402.10885](https://arxiv.org/abs/2402.10885) | 场景/动作空间关系与相对注意力；准静态操作、动作接口不同 |
| N05 | Past-Token Prediction，2025，[2505.09561](https://arxiv.org/abs/2505.09561) | 过去动作监督、冻结缓存、自验证分离；不等同输入上一计划 |
| N06 | Training and Evaluating Diffusion Policies with Long Context Lengths，2026，[2606.16447](https://arxiv.org/abs/2606.16447) | 对读PTP，结构/数据/冻结的交互；官方代码尚未公开 |
| N07 | Diffusion Forcing，2024，[2407.01392](https://arxiv.org/abs/2407.01392) | 因果状态与逐token噪声；maze/记忆不等于未知UAV到达 |
| N08 | Streaming Diffusion Policy / TEDi，2024起，[2406.04806](https://arxiv.org/abs/2406.04806) | 实读v2 TEDi；生成buffer改变，速度与性能有代价，不混用旧版摘要 |
| N09 | Streaming Flow Policy，2025，[2505.21851](https://arxiv.org/abs/2505.21851) | 连续生成组织；边际匹配不保证整段联合分布 |
| N10 | Equivariant Diffusion Policy，2024，[2407.01812](https://arxiv.org/abs/2407.01812) | 合法群作用需全链推导；不是任意三维/尺度泛化 |
| N11 | EquiBot，2024，[2407.01479](https://arxiv.org/abs/2407.01479) | 全架构等变的实质候选；UAV物理尺度/布局限制适配 |
| N12 | Flow Matching for Generative Modeling，2022/2023，[2210.02747](https://arxiv.org/abs/2210.02747) | 概率生成时间与物理飞行时间分离；本项目已有FM |
| N13 | FlowPolicy，2024/2025，[2412.04987](https://arxiv.org/abs/2412.04987) | 一致性FM加速；主体仍DP3，不能充当重大结构转向 |
| N14 | Consistency Policy，2024，[2405.07503](https://arxiv.org/abs/2405.07503) | 蒸馏延迟、教师与多样性代价；非规划周期一致性保证 |
| N15 | NoMaD，2023/2024，[2310.07896](https://arxiv.org/abs/2310.07896) | 导航真实项目，需拆拓扑图/数据/低层控制；不属同信息3DUAV对照 |
| N16 | Point Transformer，2020/2021，[2012.09164](https://arxiv.org/abs/2012.09164) | 局部点关系算子；分类/分割成功不等于到达 |
| N17 | Learning High-Speed Flight in the Wild，2021，[2110.05113](https://arxiv.org/abs/2110.05113)，DOI10.1126/scirobotics.abg5810 | 非RL UAV的额外教师/DAgger/cost及多项式投影，不能整套归纯架构 |
| N18 | HDP，2024，[2403.03890](https://arxiv.org/abs/2403.03890) | 层次条件化；关键帧与推理后修改不直接兼容MC |
| D01 | FLaRe，2024/2025，[2409.16578](https://arxiv.org/abs/2409.16578) | 视觉后训更新消融；正文/附录LR冲突用源码限定 |
| D02 | NavRL，2024/2025，[2409.15634](https://arxiv.org/abs/2409.15634)，DOI10.1109/LRA.2025.3546069 | UAV reward/训练实项目；屏障与3d速度输出不可归当前轨迹策略 |
| D03 | Beyond Imitation，2026，[2603.12868](https://arxiv.org/abs/2603.12868) | 扩散导航后训；局部解析reward和一行SR/SPL不一致限制结论 |
| A01 | What Matters In On-Policy RL，2020/2021，[2006.05990](https://arxiv.org/abs/2006.05990) | 更新组织实证，不给UAV批量数值处方 |
| A02 | Statistical Precipice，2021，[2108.13264](https://arxiv.org/abs/2108.13264) | 训练seed、选择协议、区间及聚类解释 |
| A03 | What Matters in Learning from Offline Human Demonstrations，2021/2022，[2108.03298](https://arxiv.org/abs/2108.03298) | 时序BC、机器/人类数据差异、checkpoint选择；不证明offline结果可外推onlineDPPO |

## 2. 作者代码、复现讨论与指南

- DPPO：[固定cc7234a源码](https://github.com/irom-princeton/dppo/tree/cc7234ad7ff39a8f32de3af903606723a16f0648)、[finetuning](https://github.com/irom-princeton/dppo/blob/main/cfg/finetuning.md)、[#27](https://github.com/irom-princeton/dppo/issues/27)、[#34](https://github.com/irom-princeton/dppo/issues/34)、[#56](https://github.com/irom-princeton/dppo/issues/56)、[#58](https://github.com/irom-princeton/dppo/issues/58)、[v0.8](https://github.com/irom-princeton/dppo/releases/tag/v0.8)。区分作者定位修复与第三方未闭环复现。
- [SB3维护者指南](https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html)：评价/shape/环境调试类别，复用现有快照`SB3_RL_tips_20261014.html`，不复制其所有默认设置。
- 各论文作者代码、固定commit、实际阅读文件见证据附录；第三方仓库若称unofficial、但代码由第一作者提供，已在Point Transformer卡中说明，不冒充原论文逐字节复现实验。
- GitHub main会变化；本轮DPPO main实查仍cc7234a，原始API保留于`DPPO_main_identity_20261016.json`。其他main快照标检索日期，固定commit源码另列。没有声称运行这些项目。

## 3. 副本路径与完整性记录

- 非RL分支44份原文/源码URL、大小、SHA256：[`2026-10-16_非RL实质架构研究_来源metadata.json`](2026-10-16_非RL实质架构研究_来源metadata.json)。HDP由根节点与分支复用同一个文件，未重复算篇数。
- RL既有原件路径、新增3份来源的URL/大小/hash：阅读证据附录B16。旧DSRL PDF缺EOF，新增完整官方HTML而未覆盖原件。
- 调试/导航新增来源与复用原件：阅读证据附录D14。DSRL官方env_utils由两分支复用同一份，不重复算新增材料。
- 根节点新增Robomimic论文：`WhatMatters_OfflineHumanDemonstrations_2108.03298.pdf`；来源`https://proceedings.mlr.press/v164/mandlekar22a/mandlekar22a.pdf`；8,700,215bytes；SHA256 `963aaa01b922f07c6d67848c06d1d5bd80664dd96e5e4a209b76d2e281318c66`。
- 其余根节点直接读过的on-policy与统计PDF复用旧件，原路径和阅读范围在A01/A02，不重复下载。自动提取的txt仅供检索，不替代原论文。未将Google/搜索结果摘要存作全文证据。

## 4. 同日独立审查修订所用的补充来源

- **Ng、Harada、Russell，1999，Policy invariance under reward transformations**：[作者全文](https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf)。复用`Ng_1999_Policy_Invariance_Reward_Shaping.pdf`，核§3定理、边界条件与潜势望远镜关系。用途：区分完整目标排序、终止补偿与局部shaping，不声称PPO函数逼近必收敛。
- **Schulman等，GAE，2015预印本/ICLR2016，1506.02438**：[全文v6](https://arxiv.org/html/1506.02438v6)。核§4式20—24：正确势变换下Q/V同减潜势，优势及TD残差可不变。新增原件`Schulman2015_GAE_1506.02438v6_full_20261016.html`，309423bytes，SHA256 `b77a508c4efb68f021b574969c24017e2ce7407c98f5db6542111d24227f6329`；同名metadata保留URL与阅读位置。
- **Pardo等，Time Limits in Reinforcement Learning，2018，1712.00378**：[正式作者论文](https://proceedings.mlr.press/v80/pardo18a.html)。复用`Pardo2018_Time_Limits_in_Reinforcement_Learning_arXiv1712.00378.pdf`，核有限任务与外部收集截断的差异。
- 以上为审查公式所需的经典基础，不加入前述“2020—2026年36篇”的去重数。本轮没有新铺一批文献或声称37/39篇同范围论文。
- 再核DPPO固定cc7234a loss与本地`official_loss_components.py`、`trainer.py`、`pair_schedule.py`、schema、`training_audit.py`和credit helper；原件复用，实际行号见主报告§10.2—10.4。DiPOD直接重读本地PDF §3及§4.3，区分ELBO漂移与本地chain概率代理，不据附件转述抬为默认处方。
- 用户同日补充的EGO来源、实际执行为主及训练集未变属于用户确认。后从A0源码归档找到已验收的位置导出，988条示范的几何返回/高度覆盖已实际复算，见主报告§11；action、点云与时间映射尚未由该导出补齐，位置几何不等于安全恢复。

## 5. 三份意见综合裁决的同日复核

- 日期：2026-10-16；主报告现为v1.3，新增§12三份意见取舍及首轮实施方向。未将三份共享相同项目证据的意见计为三次独立实验，也未新增论文篇数。
- 再次联网核[DPPO issue #27](https://github.com/irom-princeton/dppo/issues/27)、[v0.8发布记录](https://github.com/irom-princeton/dppo/releases/tag/v0.8)、[finetuning](https://github.com/irom-princeton/dppo/blob/main/cfg/finetuning.md)，复用`DPPO_issue27_作者讨论_20261014.json`、`DPPO_finetuning_cc7234a.md`及既有发布记录快照。用途：区分官方已修的配置遗漏与当前待检验的1280/2560更新组织，不声称同一bug复现。
- 再次联网核[FDPP](https://arxiv.org/html/2501.08259v1)，复用原HTML/PDF。用途：固定参照保持的可迁移机制、强KL限制适应及任务差异；不套通用λ。
- 再次联网核[DiPOD](https://arxiv.org/html/2606.13795v1)，复用本地PDF及官方README。用途：核其VI/ELBO问题、denoising-chain MDP区别及机器人实验范围，反对仅凭表象把它作为E5默认处方。
- 再次联网核[3D Diffuser Actor](https://arxiv.org/html/2402.10885v3)，复用`3DDiffuserActor_2402.10885_full_20261016.html`与官方源码。用途：保留局部空间信息直达动作生成的架构依据；不当作UAV恢复已获证明。
- 再次联网核[Agile Flight Bootstrapping](https://arxiv.org/html/2403.12203v1)，复用既有全文。用途：与模仿初始化后训练组织及退化现象相近的无人机证据；动作、教师和数据限制仍见阅读证据B11。
- 本轮无新增文献下载或新文献子目录；网页核查与既有原件互证。新增项目数据只有既有位置导出的派生统计，原始归档未修改。
