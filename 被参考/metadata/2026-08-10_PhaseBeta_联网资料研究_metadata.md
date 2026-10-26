# 2026-08-10 PhaseBeta 联网资料研究 metadata

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-08-10 |
| 下载日期 | 2026-08-10 |
| 对应报告 | `C:\Users\cjj\Desktop\IDP3\论文\研究报告\2026-08-10_PhaseBeta_联网资料研究.md` |
| 归档原则 | 只归档实际支撑报告结论的资料；候选但未采纳资料仅记录在报告中 |

## 1. 本轮新增 PDF

### 1.1 DiPOD

| 字段 | 内容 |
|------|------|
| 本地文件 | `C:\Users\cjj\Desktop\IDP3\论文\被参考\DiPOD - Diffusion Policy Optimization without Drifting Apart - arxiv_2606.13795.pdf` |
| 标题 | DiPOD: Diffusion Policy Optimization without Drifting Apart |
| 作者 | Haozhe Jiang; Haiwen Feng; Pieter Abbeel; Jiantao Jiao; Angjoo Kanazawa; Nika Haghtalab |
| 年份 | 2026 |
| 来源 URL | https://arxiv.org/abs/2606.13795 |
| PDF URL | https://arxiv.org/pdf/2606.13795 |
| 标识符 | arXiv:2606.13795v2；DOI 10.48550/arXiv.2606.13795 |
| 版本日期 | v1 2026-06-11；v2 2026-06-17 |
| 文件大小 | 1,945,581 bytes |
| SHA256 | `9931FD0DC583DBDE7FFE7EC00EB4DC46D2FF2ED069260194982149F9959BA4AE` |
| 引用用途 | double-drift 风险、variational surrogate 与真实 policy gradient 错位、post-G6 自蒸馏独立消融条件 |
| 相关性 | 高；直接讨论 diffusion policy RL 稳定性，但没有 UAV/point-cloud/Gazebo 验证 |

### 1.2 Flow Policy Gradients for Robot Control

| 字段 | 内容 |
|------|------|
| 本地文件 | `C:\Users\cjj\Desktop\IDP3\论文\被参考\Flow Policy Gradients for Robot Control - arxiv_2602.02481.pdf` |
| 标题 | Flow Policy Gradients for Robot Control |
| 作者 | Brent Yi; Hongsuk Choi; Himanshu Gaurav Singh; Xiaoyu Huang; Takara E. Truong; Carmelo Sferrazza; Yi Ma; Rocky Duan; Pieter Abbeel; Guanya Shi; Karen Liu; Angjoo Kanazawa |
| 年份 | 2026 |
| 来源 URL | https://arxiv.org/abs/2602.02481 |
| PDF URL | https://arxiv.org/pdf/2602.02481 |
| 标识符 | arXiv:2602.02481v1；DOI 10.48550/arXiv.2602.02481 |
| 版本日期 | v1 2026-02-02 |
| 文件大小 | 13,394,627 bytes |
| SHA256 | `4D139CFB248A7C863431594C40C99326EFE03BF12EC3F7399A48D5B28B40CBDF` |
| 引用用途 | 未来 FM policy-gradient 路线、expressive exploration、robot-control 与 sim-to-real 证据 |
| 相关性 | 高但非当前入口；支持后续同 bank 比较，不改变 DDPM A-Official-Core 当前裁决 |

### 1.3 Adaptive Q-Chunking

| 字段 | 内容 |
|------|------|
| 本地文件 | `C:\Users\cjj\Desktop\IDP3\论文\被参考\Adaptive Q-Chunking for Offline-to-Online RL - arxiv_2605.05544.pdf` |
| 标题 | Adaptive Q-Chunking for Offline-to-Online Reinforcement Learning |
| 作者 | Nandiraju Gireesh; Yuanliang Ju; He Wang |
| 年份 | 2026 |
| 来源 URL | https://arxiv.org/abs/2605.05544 |
| PDF URL | https://arxiv.org/pdf/2605.05544 |
| 标识符 | arXiv:2605.05544v1；DOI 10.48550/arXiv.2605.05544 |
| 版本日期 | v1 2026-05-07 |
| 文件大小 | 4,898,389 bytes |
| SHA256 | `9B336793585FE918AB6E3D28981FFCFDCD84D0167E3AE3293298DB4AE32F4B76` |
| 引用用途 | action horizon、反应性与信用分配 trade-off；后续 horizon sensitivity 诊断/消融 |
| 相关性 | 中高；action-chunk 问题直接相关，但算法是 offline-to-online Q-learning，不可直接替换 on-policy DPPO |

## 2. 复用的既有归档

| 本地资料 | 标题 / 来源 | 标识符 | 本期引用用途 |
|---|---|---|---|
| `C:\Users\cjj\Desktop\IDP3\论文\被参考\Diffusion Policy Policy Optimization.pdf` | Diffusion Policy Policy Optimization | arXiv:2409.00588 | A-Official-Core 理论与算法基线 |
| `C:\Users\cjj\Desktop\IDP3\论文\被参考\DPPO_Official_Code_cc7234a_metadata.md` | irom-princeton/dppo 官方实现 | commit `cc7234ad7ff39a8f32de3af903606723a16f0648` | per-step logprob、reward horizon、denoising credit、PPO clipping、GAE parity oracle |

## 3. 只保存元数据、未下载全文

### Vision-Guided Outdoor Flight and Obstacle Evasion via Reinforcement Learning

| 字段 | 内容 |
|------|------|
| 来源 | IEEE Robotics and Automation Letters, Vol. 11, No. 2, Feb. 2026, pp. 1202-1209 |
| 官方页 | https://ieeexplore.ieee.org/document/11282444 |
| DOI | 10.1109/LRA.2025.3641120 |
| 出版日期 | 2025-12-08（IEEE online）；期刊卷期 2026-02 |
| 下载状态 | 未下载全文；本期只核验 IEEE 官方摘要与书目信息 |
| 引用用途 | UAV curriculum、domain randomization、measurement/domain shift 与 outdoor real-flight 证据边界 |
| 不确定性 | [UNCERTAIN] 未核验全文中的精确超参、样本数和逐项结果，因此报告不引用这些细节 |

## 4. 归档完整性说明

[FACT] 本轮未把 PACE、ACH、DQC、CVPO、Flow Reversal Steering、NeuralPARC 或 VFH*/3DVFH+ 资料新增到 `论文/被参考/`，因为它们没有进入本期实施裁决；其来源和未采纳理由已记录在研究报告 §3/§5。

[FACT] 三个新增 PDF 均通过 SHA256 记录，可在后续研究中检查文件漂移。
