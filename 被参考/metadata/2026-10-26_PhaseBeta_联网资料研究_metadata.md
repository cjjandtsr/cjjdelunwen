# 2026-10-26 Phase β 联网资料研究：引用资料元数据

| 字段 | 内容 |
|---|---|
| 检索/核验日期 | 2026-10-26，Asia/Shanghai |
| 对应报告 | `论文/研究报告/2026-10-26_PhaseBeta_联网资料研究.md` |
| 归档规则 | 只列出实际支撑本报告结论的资料；未采纳 SDP、Q-chunking 未复制到 `论文/被参考/`。 |
| 版本注意 | Immiscible DP 本地为 v1；本期在线核验的是 v2 摘要，未将两版本混称同一归档副本。 |

## 实际引用资料

| 标题 | 作者；年份 | 来源 URL；DOI/arXiv | 本地实际资料（下载状态） | 本报告用途与边界 |
|---|---|---|---|---|
| Diffusion Policy Policy Optimization | Allen Z. Ren, Justin Lidard, Lars L. Ankile, Anthony Simeonov, Pulkit Agrawal, Anirudha Majumdar, Benjamin Burchfiel, Hongkai Dai, Max Simchowitz；2024 | https://arxiv.org/abs/2409.00588 ；arXiv:2409.00588v3；DOI:10.48550/arXiv.2409.00588 | `论文/被参考/DPPO_2409.00588v3_full_20261018.html`，已有网页快照；SHA256 `82DC4E18B53E157AD188DB4240144D23B8BF91438CD0F191DA931B0F24B5FD10`。PDF：`论文/被参考/metadata/2409.00588v3.pdf`，已有；SHA256 `4B81907B0A8EA7118E4922720F2E7D269D5CF00D3725E44FC6D25F49D02413F3`。 | 当前 DDPM/DPPO 对照与“数值正确不等于能力成立”的边界；不是 A2 保持项的因果证明。 |
| Generalizable Humanoid Manipulation with 3D Diffusion Policies | Yanjie Ze, Zixuan Chen, Wenhao Wang, Tianyi Chen, Xialin He, Ying Yuan, Xue Bin Peng, Jiajun Wu；2024，v3 2025 | https://arxiv.org/abs/2410.10803 ；arXiv:2410.10803v3；DOI:10.48550/arXiv.2410.10803 | `论文/被参考/iDP3_2410.10803v2_full_20261016.html`，已有网页快照；SHA256 `B20F9E713717CEB644E0B3FEB3B0D39FD1FCF226A11185626F10FF3A5BF2A7D1`；另有已存 PDF。 | 点云条件 diffusion policy 的相邻背景；不外推为 UAV 或 full-space 成功。 |
| Beyond Imitation: Reinforcement Learning Fine-Tuning for Adaptive Diffusion Navigation Policies | Junhe Sheng, Ruofei Bai, Kuan Xu, Ruimeng Liu, Jie Chen, Shenghai Yuan, Wei-Yun Yau, Lihua Xie；2026 | https://arxiv.org/abs/2603.12868 ；arXiv:2603.12868v1；DOI:10.48550/arXiv.2603.12868 | `论文/被参考/BeyondImitation_2603.12868v1_full_20261018.html`，已有网页快照；SHA256 `CC4FE0A2F819479CC93575997966FABD84D315D8C61882A2B2AE2FB3F0353F70`；PDF `论文/被参考/metadata/2603.12868v1.pdf`，已有；SHA256 `1DAA2516C59B3113A703F1BEC7C3E99881830F431049D6AD51A58D05BABD88D9`。 | selective update 的近邻例证；GRPO/PointGoal/2D 视觉与本项目不同，禁止直接替换 DPPO。 |
| Immiscible Diffusion Policy: Preserving Multimodal Robot Actions through Label-Free Noise Assignment | Xiao Zhang, Yuxin Chen, Zhixuan Liang, Guojian Zhan, Chenran Li, Chenfeng Xu, Masayoshi Tomizuka, Yiheng Li；2026 | https://arxiv.org/abs/2610.09369 ；arXiv:2610.09369v2；DOI:10.48550/arXiv.2610.09369 | `论文/被参考/2026-10-12_BC成功能力保持_文献与官方源码/ImmisciblePolicy_2610.09369v1.pdf` 和 `.html`，已有 v1 原件；本期未新增下载。 | 区分 action-mode preservation 与 closed-loop successful-trajectory retention；仅作后续诊断假设。 |
| Time Limits in Reinforcement Learning | Fabio Pardo, Arash Tavakoli, Vitaly Levdik, Petar Kormushev；2018 | https://arxiv.org/abs/1712.00378 ；arXiv:1712.00378v4；PMLR 80:4042-4051；DOI:10.48550/arXiv.1712.00378 | `论文/被参考/Pardo2018_Time_Limits_in_Reinforcement_Learning_arXiv1712.00378.pdf`，已有 PDF；另有 `RouteA_RL_Global_Audit_sources_20260910/Time_Limits_arxiv_1712.00378.pdf`。 | 期限是否属于任务决定 bootstrap 解释；不替代项目具体环境语义核验。 |
| AvoidBench: A high-fidelity vision-based obstacle avoidance benchmarking suite for multi-rotors | Hang Yu, Guido C. H. E de Croon, Christophe De Wagter；2023 | https://arxiv.org/abs/2301.07430 ；arXiv:2301.07430；DOI:10.1109/ICRA48891.2023.10161097 | 已有项目引用/metadata；本期未重复下载。 | 支撑多旋翼避障按环境属性与性能共同分层；不作为当前 lightweight 的 Gazebo 等价证据。 |

## 本期检索而未采纳（不归档）

| 标题 | 作者；年份；来源 | 未采纳原因 |
|---|---|---|
| Set-Supervised Diffusion Policy: Learning Action-Chunking Diffusion through Corrections | Li et al.; 2026；https://arxiv.org/abs/2606.01865；arXiv:2606.01865v1 | 依赖人类正负纠正 action chunks；当前 A2 参考库没有这种数据。 |
| Reinforcement Learning with Action Chunking | Li, Zhou, Levine；2025；https://arxiv.org/abs/2507.07969；arXiv:2507.07969 | TD/offline-to-online Q-chunking 与当前 on-policy DPPO 不同；此时引入会破坏单因素归因。 |
