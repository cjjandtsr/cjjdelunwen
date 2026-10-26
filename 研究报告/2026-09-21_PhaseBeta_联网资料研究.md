# Phase β 联网资料研究：目标信用诊断与安全评估边界

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-09-21，Asia/Shanghai |
| 类型/版本 | 定期研究报告，v1.0；非算法设计定稿或训练准入 |
| 增量窗口 | 上次运行 2026-09-14 10:00:52 +08:00 至本期；兼顾此前漏检及经典资料 |
| 核心判断 | [JUDGMENT] 保持 DDPM/DPPO 与 H4，先闭合目标条件与生产信用梯度诊断；不以新论文替代本地因果证据 |
| 资料归档 | `论文/被参考/metadata/2026-09-21_PhaseBeta_联网资料研究_metadata.md`；采用资料以元数据说明归档，本期未下载新 PDF |

## 1. 本期项目上下文摘要

[FACT] 已读取/检索 AGENTS.md、sheji/、zhidao/、jindu/，以及论文/被参考、未被参考、开题报告参考文献和研究报告目录。`program/jindu/jindu.txt` 不存在。本期从上期 run03 待验收推进到三 seed pilot 结束后的诊断阶段，不能继续沿用上期状态。

[FACT] 本期状态依据为以下本地文档；其中统计为已归档独立分析的转述，本轮没有重算全部原始轨迹，也没有重跑测试或训练：

- `jindu/2026-09-16_RouteA_RL_v17_完整工作交接与下一阶段执行边界_v2_0.md` §0：当前为 E5 DDPM BC + LoRA + official-DPPO + H4；状态 `PILOT_DIAGNOSTIC_FAILURE`、`BLOCK_FORMAL_256_AND_GAZEBO`。
- `jindu/2026-09-16_RouteA_RL_v17_S2三seed_pilot独立验收与退化根因裁决_v1_7.md` §2：u32 safe-arrival 相对 BC 分别 0/128、+1/128、−28/128；此处每 seed 128 对。
- `jindu/2026-09-20_RouteA_RL_v17_目标推进与信用链根因分析_v1_0.md` §2、§5：重复轨迹分析的 seed3 BC/RL 为 201/640 与 75/640，分母不同于原 endpoint；有限时域与信用机制为当前候选链。
- `sheji/2026-09-20_RouteA_RL_v17_目标条件与信用梯度因果诊断实验设计_v1_0.md`：仍标初稿、待用户与 Zread 审查；本轮研究不将其改称已批准执行。
- `zhidao/2026-09-16_RouteA_RL_v17_3seed_pilot_credit恢复执行指导_v1_1.md`：历史恢复交付，不是新训练授权。
- `论文/研究报告/2026-09-20_RouteA_PPO有限时域与实现选择核验.md`：已有时限文献依据，本期复核并增加结论边界。

[FACT] 本轮实际读取 Windows 源码，源码前缀为 `chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/`：`environments/terminal_contract.py:116-117` 将 time_limit 设为 truncation；`engine/gae.py:17-22` 保留其 next_value bootstrap、切断跨回合 carry；`engine/official_loss_components.py:19-28,76-77` 使用全局均值/标准差；`:60-63` 禁用 BC loss。这些是代码事实，不等于已证明 seed3 退化的因果份额。

[FACT] 现行主终点是安全进入 0.5m 三维目标球；不沿用 9月7日交接中的额外 z 阈值。H4、11D step-wise action、gaussian normalizer、eval-only 世界隔离保持；lightweight/kinematic 结果不是 Gazebo/PX4 或实物证据。

## 2. 检索范围与关键词

[FACT] 检索组合包含 diffusion policy reinforcement learning September 2026 credit assignment goal；UAV navigation reinforcement learning point cloud 2026 September；diffusion policy goal conditioning sparse reward；point cloud policy navigation safe reinforcement learning。定向打开 DPPO、ReinFlow、DSRL、Time Limits 官方 arXiv/PMLR 页面。

[FACT] 搜索摘要聚合站只用于发现，表中候选均以 arXiv/PMLR 原始页面核验。时间窗口内新增为 R1（9月14日10:04 UTC，晚于上次运行）、R2（9月16日）；R3（9月13日）是本期补漏，不宣称本周新发布。R4–R9 为经典/相关候选。检索不是穷尽性系统综述。

[UNCERTAIN] 本期主要核验作者原始摘要与书目；没有逐页阅读全文、复现算法或审计新论文代码。性能表述均不作独立实证背书。原始网页获取不等于本地 PDF 下载。

## 3. 候选资料总表

[FACT] 标题、作者与年份来自原始页面；作者较多者列首作者等。所有 URL 同时给出 arXiv ID，满足资料身份追踪。下载列描述本期操作；已有副本不移动、不重复归档。

| ID | 标题；作者；年份 | 原始来源 / arXiv ID | 下载/归档 | [JUDGMENT] 决定与理由 |
|---|---|---|---|---|
| R1 | Evaluation Metrics for Safe Reinforcement Learning；Lindsay Spoor, Aske Plaat, Thomas Moerland；2026 | https://arxiv.org/abs/2609.15315 | 未下载PDF；元数据 | 采纳：区分训练安全、终点安全、分布与任务分层 |
| R2 | Improving Offline Goal-Conditioned Reinforcement Learning via Selective Reward Stimulation；Jing Zhang；2026 | https://arxiv.org/abs/2609.19414 | 未下载PDF；元数据 | 采纳机制线索：延迟目标信号；不采纳 RSIQL 算法替换 |
| R3 | Learning-Based Dynamic Obstacle Avoidance for a UAV Using Only Three Range Sensors；Mohammad Reza Ranjbar Divkoti, A. Pedro Aguiar；2026 | https://arxiv.org/abs/2609.14426 | 未下载PDF；元数据 | 采纳观测与适用域边界：定高/yaw-only不能证明XYZ扩展 |
| R4 | Time Limits in Reinforcement Learning；Fabio Pardo, Arash Tavakoli, Vitaly Levdik, Petar Kormushev；2018（预印本2017） | https://proceedings.mlr.press/v80/pardo18a.html ; arXiv:1712.00378 | 已有PDF；本期元数据 | 采纳：有限任务期限与采集截断不同 |
| R5 | Diffusion Policy Policy Optimization；Allen Z. Ren 等；2024 | https://arxiv.org/abs/2409.00588 | 本期不下载；元数据 | 采纳主线定位：不能把其他机器人成功直接迁移成UAV证据 |
| R6 | Direction-Conditioned Policies via Compositional Subgoal Scoring for Online Goal-Conditioned Reinforcement Learning；Swaminathan S K, Damiya Gondha, Theyanesh Eswaramoorthy Rajahkrishnan, Aritra Hazra；2026 | https://arxiv.org/abs/2606.16515 | 未下载PDF；元数据 | 采纳目标表征诊断动机；不替换现行goal输入 |
| R7 | ReinFlow: Fine-tuning Flow Matching Policy with Online Reinforcement Learning；Tonghe Zhang, Chao Yu, Sichang Su, Yu Wang；2025，v7于2026修订 | https://arxiv.org/abs/2505.22094 | 已有PDF；本期无新归档 | 不采纳为本期建议：不能解决尚未闭合的任务信用问题 |
| R8 | Steering Your Diffusion Policy with Latent Space Reinforcement Learning；Andrew Wagenmaker 等；2025 | https://arxiv.org/abs/2506.15799 | 已有PDF；本期无新归档 | 不采纳：本期没有重开DSRL路线的证据 |
| R9 | REASAN: Learning Reactive Safe Navigation for Legged Robots；Qihao Yuan, Ziyu Cao, Ming Cao, Kailai Li；2025 | https://arxiv.org/abs/2512.09537 | 未下载；不归档 | 不采纳：足式、多模块且含safety shielding，与当前直接轨迹归因不一致 |

## 4. 被采纳资料与核心贡献

### R1：安全不能压缩成均值

[FACT] 作者提出同时报告聚合、分布、任务/安全阈值分层结果，并区分训练过程与最终策略；论文研究 CMDP 安全评价。[原始摘要](https://arxiv.org/abs/2609.15315)

[JUDGMENT] 本项目可采纳报告组织方式：safe-arrival 为唯一主终点，collision/timeout 和各 role 结果并列给出。不能因为 seed3 净空变大或碰撞略少就称总体更安全。论文的 safety tiers 不直接套成本项目认证标准；我们没有对应 cost-budget 合同。

### R2：远端成功信号的传播是可检查机制

[FACT] RSIQL 在 offline goal-conditioned RL 中，用辅助价值识别中间进展状态并提供额外奖励；其理论讨论为简化 delayed-goal 情形，实验为 D4RL/OGBench。[原始摘要](https://arxiv.org/abs/2609.19414)

[JUDGMENT] 可迁移问题是“成功信用是否到达早期绕障决策”，不是“照搬新正奖励”。本项目已有 progress 等信号，需先分解 reached/timeout 梯度贡献。offline IQL 的价值误差分析不能直接证明 on-policy DPPO 的根因；直接增加奖励会引入新混杂。

### R3：局部历史有价值，但任务维度必须对齐

[FACT] 该 UAV 工作采用三方向测距、行为网格聚合历史、PPO；平台定高且只有 yaw 控制，作者报告仿真与实物测试。[原始摘要](https://arxiv.org/abs/2609.14426)

[JUDGMENT] 可将“单帧信息不足还是策略未利用已有历史”作为观测审计问题。不能把其结果当作本项目点云策略、完整XYZ支持域或11D轨迹性能的直接证据；不建议改成三传感器或yaw-only。

### R4：任务期限与采集边界分开

[FACT] Pardo 等区分固定期限任务与无限任务的人工截断；前者应提供剩余时间以避免状态混叠，后者应保留截断bootstrap。[PMLR原文摘要](https://proceedings.mlr.press/v80/pardo18a.html)

[JUDGMENT] 支持审查60步任务合同。仅切断timeout bootstrap不自动解决缺失时间信息，也不自动证明需要任意大小的终止惩罚。采集buffer边界不能被统一当作任务失败。增加时间输入涉及冻结9D接口，需独立设计审查，本轮不实施。

### R5：DPPO 是方法来源，不是当前UAV能力保证

[FACT] DPPO 研究用policy gradient微调diffusion policy，在连续控制和机器人任务中验证，并报告机械臂sim-to-real部署。[原始摘要](https://arxiv.org/abs/2409.00588)

[JUDGMENT] 当前失败应先在任务语义、观测及生产梯度合同下解释。外部论文不能保证本项目成功，也不能由三个pilot seed推断DPPO普遍无效；sim-to-real仍需本项目闭环证据。

### R6：目标存在于输入，不代表目标控制有效

[FACT] DCP 在学习表征中分解方向/幅值与子目标评分；理论依赖control-affine动力学、表征等假设，页面注明ICML 2026 compositional learning workshop接收。[原始摘要](https://arxiv.org/abs/2606.16515)

[JUDGMENT] 支持把“输入接线正确”和“输出对目标有响应”分开测量。沿用本地目标替换设计即可；不据此改goal_body、引入子目标规划器或声称HJB结论已覆盖受障碍约束的H4 diffusion轨迹。

## 5. 未采纳资料与原因

[JUDGMENT] R7/R8 与本期根因诊断的增量较低。保留既有文献与历史路线裁决；本轮未将它们当作改算法依据，未新建其资料副本。R9 的点云导航具有主题相关性，但足式执行器和shielding改变能力归因，不能直接并入本项目。搜索中的图像生成RL、点云配准工作因任务不同提前排除，不构成正式候选或结论依据。

## 6. 对 iDP3-UAV 的可迁移建议

[JUDGMENT] 优先使用已有只读设计区分三种解释：目标条件敏感性衰减、信用定义改变更新方向、role间梯度冲突。以下是研究建议，不新增执行授权或修改既有矩阵。

| Phase β目标 | 需要保留的证据 | 文献增量与迁移边界 |
|---|---|---|
| 提前避障 | onset提前量、到障碍时间/净空、最终safe-arrival；按任务配对 | R2/R3启发早期信用与历史信息检查；远离目标可能是必要绕行，不能逐步奖励直奔目标 |
| full-space support expansion | 按x/y/z位置包络与目标方位分层的safe-arrival及目标响应 | R6支持条件敏感性检查；R3定高结果不覆盖三维；空间覆盖扩大不能代替到达 |
| dense-obstacle capability ceiling | dense任务rescue/break、collision/timeout、绕障后的恢复与到达 | R1支持分布/role报告；R2支持成功信用传播诊断；净空变大而困住不是能力突破 |

[JUDGMENT] 对现有设计审查建议：目标替换必须同步重算历史每帧goal_body/dist，保持点云与扩散噪声一致；无法保证替换目标可达时只称条件响应测量。梯度比较必须使用S2 full-joint合同，不能把sampled-k probe误称生产梯度。任务/seed是统计层级，重复噪声样本不能扩充分母冒充独立任务。

[JUDGMENT] 符号翻转只是诊断量。理想未裁剪policy gradient中，动作无关baseline可不改变期望梯度；有限batch、PPO clipping、多轮更新及全局统计使实际效果需要测量。因此不能将所有“远离目标且正advantage”判为错误，也不能仅据符号比例停训或删除困难样本。使用梯度方向、子组投影与后续受控证据裁决。

## 7. MC 合规检查

| 约束 | [JUDGMENT] 本期结论 |
|---|---|
| MC-1 策略输出=执行轨迹 | 只研究诊断与评价，无projection、裁剪、平滑或GOAL-TRUNC |
| MC-2 Diffusion为核心 | 保持DDPM/DPPO；DCP/RSIQL均不是已批准替代方案 |
| MC-3 学习阶段处理约束 | 讨论信用与观测；不增部署shield或外部路径修正 |
| MC-4 数据frozen | 不重采EGO；不把w4/w8/w11/w12/w18用于训练或replay |
| MC-5 归因可分离 | 程序健康、机制诊断、lightweight能力、Gazebo及实物分别表述 |

[JUDGMENT] “策略内”不能仅按代码位置判定。外部几何纠偏即便放进采样循环也需核验是否重写路径与改变归因；本期没有采纳此类方案。不建议yaw_loss_boost>1、5D action、DAC offline RL、decorrelation loss或torch.compile+CFG。H4与现有学习信号保持，不能用更强clamp或删失败样本换好看曲线。

## 8. 风险与不确定性

- [UNCERTAIN] 新预印本只做摘要级核验：缓解方式是在进入设计前读取全文、核对假设与官方实现，不能直接照搬性能数字。
- [UNCERTAIN] 本地根因链尚未量化因果份额：缓解方式是同输入、同transition、同生产schedule的只读反事实；不把相关性写成已证实故障。
- [JUDGMENT] timeout负奖励或BC锚定过强可能抹平绕障探索：任何后续提案必须同时保留成功梯度、动作多样性、update norm和dense rescue证据。
- [JUDGMENT] fixed32事后诊断存在测试集适配风险：不可据此调参后继续宣称同一测试集为未见泛化评估；后续方案用隔离dev bank审查。
- [UNCERTAIN] 本期未找到足以直接覆盖本项目完整三维点云diffusion-UAV部署的新证据；这不是断言不存在此类论文。

## 9. 下一步建议

1. [JUDGMENT] 先审查9月20日诊断设计，重点核验S2 full-joint与目标替换身份；保持当前formal/Gazebo阻断，不以研究报告越过Zread。
2. [JUDGMENT] 将有限任务期限、采集截断、剩余时间可观测性分别列清；仅在因果证据和设计审查后决定是否改终止语义或观测接口。
3. [JUDGMENT] 下一版分析同时呈现safe-arrival、collision、timeout及三能力role分层，保留所有seed和终点；不挑最好checkpoint。
4. [JUDGMENT] 下周从目标替换/生产梯度回传状态续接；若仍未执行，继续补相关理论边界，不重复泛扫DPPO/ReinFlow/DSRL，不擅自启动训练。

[FACT] 本轮只产生研究文档与资料元数据，未改训练代码/配置，未操作WSL、ROS、Gazebo或PX4。
