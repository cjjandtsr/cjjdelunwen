# 外部RL报告审查来源记录

检索日期：2026-10-14。用途：核验用户docx对DPPO似然、PBRS、有限预算和文献身份的判断。只核查决定调整建议的关键资料，不声称已逐篇验证报告全部来源。

| 来源 | URL / 标识 | 本地资料 | 阅读与用途 |
|---|---|---|---|
| 官方DPPO PPO loss | https://github.com/irom-princeton/dppo/blob/main/model/diffusion/diffusion_ppo.py | 既有算法资料与本地vendor/source_snapshot相应文件 | 公开代码及本地实际调用核对；clamp、mean已在官方实现，当前按去噪索引采样 |
| Ng等1999 PBRS | https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf | `Ng_1999_Policy_Invariance_Reward_Shaping.pdf` | 定理与适用条件；闭合路线和终止边界由本次代数推导，不当新项目实测 |
| Pardo等2018 Time Limits | https://arxiv.org/html/1712.00378v4 | `Pardo2018_Time_Limits_in_Reinforcement_Learning_arXiv1712.00378.pdf` | 固定任务时限与采样截断两种语义，反对不分任务直接改bootstrap |
| D²PPO | https://arxiv.org/html/2508.02644v1 ; https://github.com/Guowei-Zou/d2ppo-release | `D2PPO_2508.02644v1.html` | 核题名、方法简介、表示坍塌任务范围；未完成向LoRA的迁移验证，不列为已批准算法 |
| T* | https://arxiv.org/abs/2601.11214 | `Tstar_2601.11214_官方摘要.html` | 核官方摘要与身份，不声称阅读全文；正确编号与报告误写区别 |
| 报告误编号对应论文 | https://arxiv.org/abs/2602.09375 | `LatentPoincare_2602.09375_官方摘要.html` | 仅核身份：实际为Latent Poincaré Shaping，不是T* |

## 本次新保存原件

| 文件 | 字节 | SHA256 |
|---|---:|---|
| D2PPO_2508.02644v1.html | 388142 | `559b639decd6bd6ebfe4fe65713358f1d2f7bc58558f57b98413aa571c0cfe9b` |
| Tstar_2601.11214_官方摘要.html | 40361 | `55aba1cca20f8b8bd21786df5b18513477d8c7c0c299568e93a433df8a441572` |
| LatentPoincare_2602.09375_官方摘要.html | 41534 | `e70880ecf6dbfee234eb7c11c29454ac877c6cc5b32c94d1d6f2fbdf5ec14075` |

新资料直接放现有`论文/被参考/`，没有主题子文件夹；既有PDF不重复下载。报告原docx仅阅读，没有更改或执行其中的工作指令。
