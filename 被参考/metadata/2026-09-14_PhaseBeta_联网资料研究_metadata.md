# 2026-09-14 Phase β 联网资料研究：引用元数据

[FACT] 检索/核验日期：2026-09-14（Asia/Shanghai）；对应报告：`论文/研究报告/2026-09-14_PhaseBeta_联网资料研究.md`。本文件即本期引用资料归档载体：使用元数据说明形式，未下载PDF、未保存原始网页快照、未复现代码。非原文副本；下列为人工概述，不是逐字引用。只包含实际用于报告判断的4项来源。

## A. CAVEAT

- [FACT] 标题：CAVEAT: Recurrent Multimodal Diffusion Planning for Mapless Aerial Exploration。
- [FACT] 作者：Steven Visch; Nicolò Botteghi; Antonio Franchi; Barbara Bazzana。
- [FACT] 年份/版本：2026；v1，2026-09-06提交。
- [FACT] 原始页：https://arxiv.org/abs/2609.06623v1 ；方法全文：https://arxiv.org/html/2609.06623v1 。
- [FACT] arXiv：2609.06623；DOI：10.48550/arXiv.2609.06623（原始页提示DOI注册待完成）。
- [FACT] 下载：否；归档：本元数据；核验范围：摘要、HTML §II-B、式(2)–(3)。
- [FACT] 核验内容：循环状态融合多模态历史；rolling初始化；最后四步去噪时对低净空航点直接施加二维SDF梯度位置修正。
- [JUDGMENT] 引用用途：报告§4A、§6密集障碍/历史信息、§7策略内外边界。采纳历史信息分解，不采纳通用航点修正或专家重采集；不证明本地三维到达性能。

## B. Lightweight Safe RL

- [FACT] 标题：Lightweight Safe Reinforcement Learning for End-to-End UAV Navigation。
- [FACT] 作者：Shenghui Zhang; YuXuan Gao; Songwei Zhao; Jifeng Hu; Zijing Zhang; Hechang Chen。
- [FACT] 年份/版本：2026；v1，2026-07-02提交。
- [FACT] 原始页：https://arxiv.org/abs/2607.01794v1 ；方法全文：https://arxiv.org/html/2607.01794v1 。
- [FACT] arXiv：2607.01794；DOI：10.48550/arXiv.2607.01794。
- [FACT] 下载：否；归档：本元数据；核验范围：摘要、HTML §III-C/III-D及§IV速度/密度结果段。
- [FACT] 核验内容：稀疏感知、Lagrangian safe PPO；3维body velocity动作、Beta分布和几何控制器；评估密度与速度影响。
- [JUDGMENT] 引用用途：报告§4B、§6提前避障与观测压力。与UAV密集避障直接相关，但动作/动力学合同不同；不迁移其数值结果、奖励系数或策略核心。

## C. Air Learning

- [FACT] 标题：Air Learning: A Deep Reinforcement Learning Gym for Autonomous Aerial Robot Visual Navigation。
- [FACT] 作者：Srivatsan Krishnan; Behzad Boroujerdian; William Fu; Aleksandra Faust; Vijay Janapa Reddi。
- [FACT] 年份/版本：2019首发；v5，2022-11-13修订。
- [FACT] 原始页：https://arxiv.org/abs/1906.00421v5 。
- [FACT] arXiv：1906.00421；DOI：10.48550/arXiv.1906.00421。
- [FACT] 下载：否；归档：本元数据；核验范围：摘要与版本史，未核验全文实验细节。
- [FACT] 核验内容：评估桌面与资源受限机载计算的飞行差距；以目标硬件延迟分布研究延迟注入。
- [JUDGMENT] 引用用途：报告§4C与§6未来sim-to-real延迟记录。不能以此归因当前kinematic失败；真实闭环需独立证据。

## D. DPPO

- [FACT] 标题：Diffusion Policy Policy Optimization。
- [FACT] 作者：Allen Z. Ren; Justin Lidard; Lars L. Ankile; Anthony Simeonov; Pulkit Agrawal; Anirudha Majumdar; Benjamin Burchfiel; Hongkai Dai; Max Simchowitz。
- [FACT] 年份/版本：2024；v3，2024-12-09修订。
- [FACT] 原始页：https://arxiv.org/abs/2409.00588v3 。
- [FACT] arXiv：2409.00588；DOI：10.48550/arXiv.2409.00588。
- [FACT] 下载：本期未新增；归档：本轮元数据核验记录；核验范围：摘要与作者/版本信息，未重审历史PDF或官方代码。
- [JUDGMENT] 引用用途：报告§4D算法归属与本地parity证据边界。其机器人结果不直接证明UAV三能力或本地实现等价。

## 归档与筛选边界

[FACT] 本期候选E/ReinFlow、F/DSRL仅列在研究报告筛选表，未为其在被参考目录新增材料。已有历史资料保持不动。元数据归档满足本期允许的资料类型，不等同于PDF下载或全文复现。

[FACT] 本轮状态来自9月14日本地状态文档，历史训练数字仅作历史背景；论文判断与项目判断分别标记。四项来源URL均已在线访问，其标识对应原始arXiv页。
