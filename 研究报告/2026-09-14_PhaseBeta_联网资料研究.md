# Phase β 联网资料研究：无训练准入、稀疏感知与导航记忆边界

[FACT] 检索日期：2026-09-14，Asia/Shanghai。类型：每周研究报告；版本：v1.0。本文是资料筛选与迁移判断，不是新算法定稿、执行指导或训练许可。

## 1. 本期项目上下文摘要

[FACT] 本轮已读取/搜索 AGENTS.md、sheji/、zhidao/、jindu/、论文/被参考/、论文/未被参考/、论文/开题报告参考文献/，以及上期自动化记录。program/jindu/jindu.txt 不存在。已读9月7日主交接、9月7日周报、9月10日全链研究与设计v1.2，以及9月14日状态和无训练指导。状态依据为本地文档，本轮没有重跑历史实验。

[FACT] 当前主线为 E5 DDPM BC + 官方 DPPO 核心 + Reward v1.7，H=4、11维 step-wise action。9月14日状态记录：run02在Reward源与校准身份不一致处、BC probe采样前失败；Windows修复后交付清单102文件、source-set 111文件，本地回归记录329 passed。WSL run03仍待执行，不能称12门禁已通过或允许训练。依据：`jindu/2026-09-14_RouteA_RL_v17_F0_G1_Reward身份闭合状态_v1_1.md` §1–4。

[FACT] 9月10日设计v1.2纠正了早期讨论：均匀 sampled-k 的 mean estimator 可无偏，不能仅凭未展开全部pair断定算法错误；仍须测量方差、更新规模和逐role梯度。依据：`sheji/RouteA_RL_v17_全链根因闭合与正式训练恢复设计_v1_2_20260910.md:130`、`:138`、`:150`。本期不沿用9月10日研究报告中“先恢复联合索引”的早期简化建议。

[FACT] 当前目标契约为安全条件下三维距离 <=0.5m，不附加z/yaw/末速/驻留硬门槛。Windows调用已在 `chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/env/kinematic_uav_env.py:1046` 使用 `reached_goal(..., 0.5)`；本轮仅核对调用，不替代完整路径或WSL验收。9月7日交接的旧z阈值不可作为新合同。旧128对BC35、RL22是历史轻量结果，不能与新终止合同直接混算。

[JUDGMENT] 本期优先级仍是run03证据闭合。新增资料用于识别未来研究问题，不能绕过准入去换FM、重设Reward或提前宣称三能力改善。

## 2. 检索范围与关键词

[FACT] 覆盖2019–2026年资料，重点补查截至9月14日的近期UAV导航、safe RL、点云/稀疏感知、diffusion/flow matching后训练与机载延迟。实际查询包括：`site.arxiv.org diffusion policy reinforcement learning September 2026 UAV obstacle navigation`、`site.arxiv.org UAV navigation point cloud reinforcement learning 2026 safe diffusion policy`、`site.arxiv.org/abs/ "2026" "September" "flow" "policy" reinforcement learning`、`site.arxiv.org/abs/ "2026" "September" UAV diffusion navigation`；并定向核验DPPO、DSRL、ReinFlow原始页。

[FACT] 聚合结果仅用于发现，以下候选的结论依据均为arXiv原始页。CAVEAT为9月6日提交、本期新增关注，不能称9月7日以后首发。9月关键词检索噪声较大，未发现不等于近期没有其他工作。

[FACT] CAVEAT与Lightweight Safe RL阅读了HTML方法片段；Air Learning和DPPO核验摘要；ReinFlow和DSRL核验书目信息及摘要线索。未进行PDF版面核验或官方代码复现。归档采用用户允许的元数据说明，不声称已下载PDF。

## 3. 候选资料总表

[FACT] 年份以arXiv首发年为准；以下URL均为本轮访问来源，arXiv DOI统一为 `10.48550/arXiv.<编号>`。采纳仅指用作本报告依据。

| ID | 标题；作者；年份 | 来源 / arXiv ID | 下载、采纳与理由 |
|---|---|---|---|
| A | CAVEAT: Recurrent Multimodal Diffusion Planning for Mapless Aerial Exploration；Steven Visch, Nicolò Botteghi, Antonio Franchi, Barbara Bazzana；2026 | https://arxiv.org/abs/2609.06623v1 | 采纳：记忆与几何修正的归因边界；新增元数据，未下载PDF |
| B | Lightweight Safe Reinforcement Learning for End-to-End UAV Navigation；Shenghui Zhang, YuXuan Gao, Songwei Zhao, Jifeng Hu, Zijing Zhang, Hechang Chen；2026 | https://arxiv.org/abs/2607.01794v1 | 采纳：稀疏感知和密度×速度评估依据；新增元数据，未下载PDF |
| C | Air Learning: A Deep Reinforcement Learning Gym for Autonomous Aerial Robot Visual Navigation；Srivatsan Krishnan, Behzad Boroujerdian, William Fu, Aleksandra Faust, Vijay Janapa Reddi；2019，v5修订2022 | https://arxiv.org/abs/1906.00421v5 | 采纳：机载延迟与仿真硬件差距；新增元数据，未下载PDF |
| D | Diffusion Policy Policy Optimization；Allen Z. Ren, Justin Lidard, Lars L. Ankile, Anthony Simeonov, Pulkit Agrawal, Anirudha Majumdar, Benjamin Burchfiel, Hongkai Dai, Max Simchowitz；2024 | https://arxiv.org/abs/2409.00588v3 | 采纳：主算法归属；新增本轮核验元数据，不重复下载历史资料 |
| E | ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning；Tonghe Zhang, Chao Yu, Sichang Su, Yu Wang；2025，v7修订2026 | https://arxiv.org/abs/2505.22094v7 | 本期不采纳为建议依据；未新增下载/归档，当前缺口不是缺少另一个FM算法 |
| F | Steering Your Diffusion Policy with Latent Space Reinforcement Learning；Andrew Wagenmaker, Mitsuhiko Nakamoto, Yunchu Zhang, Seohong Park, Waleed Yagoub, Anusha Nagabandi, Abhishek Gupta, Sergey Levine；2025 | https://arxiv.org/abs/2506.15799v2 | 本期不采纳为建议依据；未新增下载/归档，不重启已研究的DSRL路线 |

## 4. 被采纳资料与核心贡献

### A：CAVEAT——记忆研究线索与几何修正分离

[FACT] 该工作融合LiDAR、视觉与pose，通过循环状态为扩散航点规划提供历史信息；训练示范来自FUELv2。HTML §II-B式(3)明确：局部二维SDF用于对低净空航点施加位置梯度修正，发生在最后四步去噪中。来源：https://arxiv.org/html/2609.06623v1 。

[JUDGMENT] 可借鉴的是区分观测历史、前次计划和局部几何三种信息来源。直接沿SDF梯度移动航点是通用几何修正，即使放在去噪循环里，也不能直接归入本项目认可的ε预测guidance。其探索与实机概念验证不能当作本项目静态3D安全到达证明。

### B：Lightweight Safe RL——稀疏感知的联合压力

[FACT] 论文使用稀疏观测编码、Lagrangian safe PPO和分层控制；§III-D的动作是3维body velocity，采用Beta分布与几何控制器。§IV按障碍密度和最高速度比较结果。来源：https://arxiv.org/html/2607.01794v1 。

[JUDGMENT] 可借鉴密度与反应时间联合分析；不能将其动作、奖励系数、成功率搬到11维轨迹策略。稀疏感知有用不等于当前normalizer或encoder已经覆盖高空和全空间。

### C：Air Learning——推理速度需要进入闭环证据

[FACT] 该工作研究资源受限机载平台与桌面仿真之间的轨迹差异，使用目标硬件延迟分布与训练延迟注入研究硬件差距。来源：https://arxiv.org/abs/1906.00421v5 。

[JUDGMENT] 可作为未来记录观测龄期、排队和推理延迟的依据；当前kinematic失败不能因此归因为机载算力问题。延迟随机化应另行设计，不加入正在等待验收的run03。

### D：DPPO——保留基础算法归属

[FACT] DPPO提出扩散策略的策略梯度微调框架，并报告连续控制与机器人实验。来源：https://arxiv.org/abs/2409.00588v3 。

[JUDGMENT] 本项目可归因的贡献应由UAV约束学习与三能力实验支撑，不能把DPPO本身作为原创。论文摘要不证明本地实现与官方优化语义等价；该问题仍由既有D1b门禁处理。

## 5. 未采纳资料与原因

[JUDGMENT] E/ReinFlow：本期没有足够新增证据支持DDPM→FM切换；已有研究覆盖其用途，再换算法会增加归因变量。F/DSRL：本期任务是检查当前主线的准入和能力证据，不是重新开展latent steering方案。二者保留候选表与原始链接，不为本轮在被参考目录新增文件。

[FACT] A/B为部分采纳：采纳问题分解和评估依据，不采纳A的SDF航点移动、专家数据重采集，或B的3维动作/Beta策略替换。被参考不代表整套系统合规。

## 6. 对 iDP3-UAV 的可迁移建议

[JUDGMENT] 下列均为后续分析建议，须先检查已有输出能否直接支持，避免新增重复诊断；任何行为变化另行设计、Zread审查。本轮不写或修改训练程序。

| Phase β目标 | 资料启发与本项目问题 | 可观察证据及边界 |
|---|---|---|
| 提前避障 | B/C：稀疏感知、密度和延迟共同压缩反应余量 | 按role/outcome查看有效点云率、最近障碍距离、onset距离/时间；未来真实闭环加观测龄期和延迟P50/P95/P99。safe-arrival为主终点，不能用onset非零替代 |
| full-space support expansion | A/B：需分辨绝对位置、局部几何和历史信息 | 在独立dev数据上比较相同相对几何、不同xyz包络的输入/embedding/动作与终点；normalizer前后hash和有效性先闭合。跨z测试不能代表xyz全覆盖 |
| dense-obstacle capability ceiling | A：循环历史是否帮助区分局部相似、历史不同的决策 | 先分析重复访问、停滞、恢复与失败占比；按固定密度分层报告safe-arrival及分母。仅当当前输入信息不足有证据时，才考虑记忆架构设计，不能直接加GRU |

[JUDGMENT] 共同评价：保留所有预注册困难样本与合法失败，报告每seed、每role及总体paired safe-arrival差值和适用的区间估计。报告episode与transition两种分母；点云无效等硬故障单列，不以删失败提高SR。不能在w4/w8/w11/w12/w18训练、replay或调参。

## 7. MC 合规检查

| 约束 | 本期裁决 |
|---|---|
| MC-1 策略输出=执行轨迹 | [JUDGMENT] 不迁移A的SDF航点移动，不做外部平滑、GOAL-TRUNC或避障排斥；保持执行切片合同 |
| MC-2 Diffusion核心 | [JUDGMENT] 保持DDPM/DPPO；不以B的Beta velocity policy取代核心 |
| MC-3 学习阶段处理约束 | [JUDGMENT] 分析训练信号和观测质量；安全PPO只是候选研究，不附加通用projection |
| MC-4 EGO frozen | [JUDGMENT] 不照搬A的专家采集流程；988 episodes数据合同不变 |
| MC-5 归因可分离 | [JUDGMENT] 记忆、SDF、控制器、延迟必须分别归因；本地轻量结果与Gazebo/PX4、实机证据分层 |

[JUDGMENT] “策略内”判定看操作实质：修改ε预测的diffusion特有guidance与通用航点几何修正不同。前者也不能充当唯一论文main result。本期未建议yaw_loss_boost、5d缩减、DAC offline RL、TransDiffuser decorrelation或torch.compile+CFG。

## 8. 风险与不确定性

[UNCERTAIN] 文献的传感器、动力学、目标语义与本地任务不等价，本文没有复现实验；缓解方式是只迁移研究问题，不迁移其SR或超参。

[UNCERTAIN] 当前run03是否通过、三seed pilot是否改善能力仍未知。缓解方式是等待原始包独立验收；Windows测试通过不等于WSL门禁通过。

[JUDGMENT] 记忆模块可能增加漂移和延迟；安全惩罚/课程可能削弱困难样本探索。若未来立项，必须同时检查动作多样性、成功条件advantage、逐role梯度贡献及安全到达，不能靠降低更新或删难例获得稳定性。

[FACT] 本轮只归档元数据，没有新增PDF或网页原始快照；A/B方法片段已在线核验，其余主要为摘要级。检索不是系统综述，来源版本和读取范围见metadata。

## 9. 下一步建议

1. [JUDGMENT] 按现有9月14日指导完成WSL run03，回传102文件身份、111-file source-set、BC probe、100 sampled-k schedule与12门禁原始证据；本文不追加执行要求或授权训练。
2. [JUDGMENT] Codex验收后再按既有流程裁决 `ALLOW_3_SEED_PILOT`；本期文献不改变门禁、H4、Reward结构或训练预算。
3. [JUDGMENT] 下期从run03实际裁决出发，优先检查观测与逐role信用证据。若仍存在历史混叠或部署延迟缺口，再对A/C深入全文与官方代码研究，不重复泛扫DPPO/ReinFlow/DSRL。

[FACT] 自检：九节齐全；6项候选、4项采纳；作者/年份/URL/ID/下载状态齐全；三能力、MC-1~MC-5、策略内外及不确定性已显式说明。未训练、未操作ROS/Gazebo/PX4、未改原始回传证据。
