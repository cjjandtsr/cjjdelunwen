# 2026-09-21 PhaseBeta 联网资料研究 metadata

[FACT] 检索/归档日期：2026-09-21（Asia/Shanghai）。对应报告：`论文/研究报告/2026-09-21_PhaseBeta_联网资料研究.md`。本文件本身是用户允许的“元数据说明”归档形式；不是PDF或网页原文快照。本期没有新下载PDF，没有宣称全文审读或代码复现。下列六项均实际支撑报告；未采用R7/R8/R9不新增归档。

## R1 — Evaluation Metrics for Safe Reinforcement Learning

- [FACT] 作者：Lindsay Spoor; Aske Plaat; Thomas Moerland。年份：2026；v1提交：2026-09-14 10:04:22 UTC。
- [FACT] 来源：https://arxiv.org/abs/2609.15315v1 。ID：arXiv:2609.15315；DOI：10.48550/arXiv.2609.15315（页面标记注册待完成）。
- [FACT] 访问层级：官方摘要/书目；未下载PDF。归档载体：本节元数据说明。
- [FACT] 核验信息：提出同时报告聚合、分布及任务/安全阈值分层结果，区分训练和最终策略安全。
- [JUDGMENT] 用途：报告§4 R1、§6、§9的分层报告建议；与三seed分化相关。不能直接套用CMDP safety tier或宣称UAV安全认证。

## R2 — Improving Offline Goal-Conditioned Reinforcement Learning via Selective Reward Stimulation

- [FACT] 作者：Jing Zhang。年份：2026；v1提交：2026-09-16 20:52:32 UTC。
- [FACT] 来源：https://arxiv.org/abs/2609.19414v1 。ID：arXiv:2609.19414；DOI：10.48550/arXiv.2609.19414（页面标记注册待完成）。
- [FACT] 访问层级：官方摘要/书目；未下载PDF。归档载体：本节元数据说明。
- [FACT] 核验信息：RSIQL使用辅助goal-conditioned value选择中间进展状态并增添奖励；研究offline GCRL。
- [JUDGMENT] 用途：报告§4 R2、§6的成功信用传播诊断。仅采纳问题分解；不是DPPO算法修正依据，不直接增加本项目reward。

## R3 — Learning-Based Dynamic Obstacle Avoidance for a UAV Using Only Three Range Sensors

- [FACT] 作者：Mohammad Reza Ranjbar Divkoti; A. Pedro Aguiar。年份：2026；v1提交：2026-09-13 10:53:43 UTC。
- [FACT] 来源：https://arxiv.org/abs/2609.14426v1 。ID：arXiv:2609.14426；DOI：10.48550/arXiv.2609.14426（页面标记注册待完成）。
- [FACT] 访问层级：官方摘要/书目；未下载PDF。归档载体：本节元数据说明。此项为本期补漏，不是上次运行后新增。
- [FACT] 核验信息：定高、yaw-only、三方向测距、行为网格历史表示、PPO；作者报告仿真和实物实验。
- [JUDGMENT] 用途：报告§4 R3、§6的观测历史与三维适用域边界。不复用跨任务成功率作iDP3-UAV对比，不推断full-space有效性。

## R4 — Time Limits in Reinforcement Learning

- [FACT] 作者：Fabio Pardo; Arash Tavakoli; Vitaly Levdik; Petar Kormushev。年份：ICML 2018；预印本2017。
- [FACT] 来源：https://proceedings.mlr.press/v80/pardo18a.html ；https://arxiv.org/abs/1712.00378 。ID：arXiv:1712.00378；PMLR 80:4045–4054。
- [FACT] 本期核验层级：PMLR官方摘要/书目。既有PDF：`论文/被参考/Pardo2018_Time_Limits_in_Reinforcement_Learning_arXiv1712.00378.pdf`；本轮未重复下载、未逐页审读。
- [FACT] 既有PDF SHA256：`5BB677EE1A3D6916AEDF7D6DF74463238CFE792FC348976502F46C14998067C6`，本期重新计算一致。
- [FACT] 核验信息：固定任务期限需考虑剩余时间；无限任务的人工截断应bootstrap。
- [JUDGMENT] 用途：报告§4 R4、§6、§9。支持合同区分，不证明具体timeout惩罚系数，不自动授权改变9D状态。

## R5 — Diffusion Policy Policy Optimization

- [FACT] 作者：Allen Z. Ren; Justin Lidard; Lars L. Ankile; Anthony Simeonov; Pulkit Agrawal; Anirudha Majumdar; Benjamin Burchfiel; Hongkai Dai; Max Simchowitz。年份：2024。
- [FACT] 来源：https://arxiv.org/abs/2409.00588v3 。ID：arXiv:2409.00588；DOI：10.48550/arXiv.2409.00588。v3日期：2024-12-09。
- [FACT] 访问层级：官方摘要/书目；本期未下载PDF。归档载体：本节元数据说明；未把旧官方代码镜像当作本期新审计。
- [FACT] 核验信息：policy gradient微调diffusion policy；连续控制、机器人任务与机械臂sim-to-real实验。
- [JUDGMENT] 用途：报告§4 R5主线定位及跨任务证据边界。不能从论文直接推出UAV三能力达标，也不据pilot宣告算法普遍失败。

## R6 — Direction-Conditioned Policies via Compositional Subgoal Scoring for Online Goal-Conditioned Reinforcement Learning

- [FACT] 作者：Swaminathan S K; Damiya Gondha; Theyanesh Eswaramoorthy Rajahkrishnan; Aritra Hazra。年份：2026；v1日期：2026-06-15。
- [FACT] 来源：https://arxiv.org/abs/2606.16515v1 。ID：arXiv:2606.16515；DOI：10.48550/arXiv.2606.16515。页面注明ICML 2026第二届Compositional Learning workshop接收，非据此声称ICML主会论文。
- [FACT] 访问层级：官方摘要/书目；未下载PDF。归档载体：本节元数据说明。
- [FACT] 核验信息：学习表征上的方向/幅值条件与子目标评分分解；理论含control-affine等适用假设。
- [JUDGMENT] 用途：报告§4 R6、§6目标条件敏感性问题。只采纳诊断动机，不移植方向接口或子目标机制，不声称其理论已验证本项目。

## 归档自检边界

[FACT] 六项元数据均包含作者、年份、原始URL、ID、下载/访问层级、引用用途与迁移边界。未保存聚合站摘要，未下载或执行外部源码。报告保留候选总表中的未采纳项，不将它们混入本文件的采用资料集合。
