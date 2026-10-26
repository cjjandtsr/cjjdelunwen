# 2026-10-19 Phase β 联网资料研究：采用来源 metadata

检索日期：2026-10-19（Asia/Shanghai）  
归档原则：本文件仅登记实际支撑 `2026-10-19_PhaseBeta_联网资料研究.md` 结论的资料。既有 PDF/metadata 已存在时不重复下载；本轮未新增 PDF。所有 URL 均在本次运行通过来源官方页面核验。

## 1. Diffusion Policy Policy Optimization（DPPO）

- Authors: Allen Z. Ren, Justin Lidard, Lars L. Ankile, Anthony Simeonov, Pulkit Agrawal, Anirudha Majumdar, Benjamin Burchfiel, Hongkai Dai, and Max Simchowitz.
- Year / identifier: 2024; arXiv:2409.00588.
- Official source: https://arxiv.org/abs/2409.00588
- Download status: 既有项目归档，未重复下载。
- Used for: 区分 chunk-policy 优化正确性/数值健康与最终避障能力，限定其作为当前 DDPM RL 基线的解释边界。
- Relevance: 提前避障、full-space、dense obstacle 三项均只经最终固定配对能力指标裁决；不以 PPO/DPPO 的正确性替代能力证据。
- Local provenance: 既有 `论文/被参考/` 的 DPPO 资料与此前周期 metadata。

## 2. Generalizable Humanoid Manipulation with 3D Diffusion Policies（iDP3）

- Authors: Yanjie Ze, Zixuan Chen, Wenhao Wang, Tianyi Chen, Xialin He, Ying Yuan, Xue Bin Peng, and Jiajun Wu.
- Year / identifier: 2024; arXiv:2410.10803.
- Official source: https://arxiv.org/abs/2410.10803
- Download status: 既有项目归档，未重复下载。
- Used for: 3D point-cloud-conditioned diffusion policy 的相邻表征背景；不用于声称 UAV 上的可迁移成功。
- Relevance: 仅支持把点云观测质量与 x/y/z 覆盖作为策略内评价字段。
- Local provenance: 既有 `论文/被参考/` 的 iDP3 资料与此前周期 metadata。

## 3. Time Limits in Reinforcement Learning

- Authors: Fabio Pardo, Arash Tavakoli, Vitaly Levdik, and Petar Kormushev.
- Year / identifier: 2018; arXiv:1712.00378.
- Official source: https://arxiv.org/abs/1712.00378
- Download status: 既有项目归档，未重复下载。
- Used for: 真终止与 time-limit/truncation 的 bootstrap 语义区分。
- Relevance: 支撑 A1 的真 60 决策期限语义审计；不推导新的 reward 或安全惩罚。
- Local provenance: `论文/被参考/RouteA_RL_Global_Audit_sources_20260910/Time_Limits_arxiv_1712.00378.pdf`。

## 4. AvoidBench: A High-Fidelity Vision-Based Obstacle Avoidance Benchmarking Suite for Multi-Rotors

- Authors: Hang Yu, Guido C. H. E. de Croon, and Christophe De Wagter.
- Year / identifier: 2023; arXiv:2301.07430; DOI:10.1109/ICRA48891.2023.10161097.
- Official sources: https://arxiv.org/abs/2301.07430 ; https://doi.org/10.1109/ICRA48891.2023.10161097
- Download status: 既有项目归档，未重复下载。
- Used for: 把多旋翼密集障碍评价同 traversability/任务难度联系，而非仅以障碍物数量或 world 名称代表难度。
- Relevance: 支撑 dense-obstacle capability ceiling 的分层与 lightweight/Gazebo-PX4 边界；不作为当前 21 几何的泛化证据。
- Local provenance: 既有 `论文/被参考/` 的 AvoidBench 资料与此前周期 metadata。

## 5. Flying on Point Clouds with Reinforcement Learning

- Authors: Guangtong Xu, Tianyue Wu, Zihan Wang, Qianhao Wang, and Fei Gao.
- Year / identifier: 2025; arXiv:2503.00496.
- Official source: https://arxiv.org/abs/2503.00496
- Download status: 既有项目归档，未重复下载。
- Used for: 点云—飞行 RL 的相邻任务证据，限定点云几何观测在评价中应可审计。
- Relevance: 与 full-space 和 dense-obstacle 的观测/任务分层相关；不迁移其动作、控制或训练实现。
- Local provenance: `论文/被参考/2026-10-05_PhaseBeta_联网资料研究_sources.md`。

## 本轮明确未归档候选

- Flow Policy Gradients for Robot Control, arXiv:2602.02481：https://arxiv.org/abs/2602.02481。原因：其 flow-policy objective 会与 A1 当前 DDPM/DPPO 共同协议的归因混淆。
- Reinforcement Learning for Flow-Matching Policies, arXiv:2507.15073：https://arxiv.org/abs/2507.15073。原因：variable horizon、GRPO 与 learned reward surrogate 改变合同，且主体任务为 unicycle。
- High-Speed Vision-Based Flight in Clutter with Safety-Shielded Reinforcement Learning, arXiv:2602.08653：https://arxiv.org/abs/2602.08653。原因：部署期安全 filter/action projection 与 MC-1/MC-3 不兼容。

[FACT] 这些条目只作为筛选记录，不被作为报告支撑资料复制至 `论文/被参考/`。
