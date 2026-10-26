# 扩散策略RL长训退化逐项核查：来源与用途

检索日期：2026-10-14。用于对用户提供的七类原因、诊断指标及八类缓解方法逐项审查。只使用原论文、作者网站和官方代码；外部机制不是本项目根因证明。新资料直接保存在现有`论文/被参考/`，没有新建主题文件夹；既有归档沿用原路径，不搬动历史原件。

| 来源 | 主URL / 标识 | 本地原件或既有归档 | 本次用途与限制 |
|---|---|---|---|
| DPPO，2024预印本 / ICLR 2025 | https://arxiv.org/html/2409.00588v3 ; https://diffusion-ppo.github.io/ ; https://github.com/irom-princeton/dppo/blob/main/model/diffusion/diffusion_ppo.py | `2026-10-12_RL_Reward综合研究/algorithms/DPPO_extracted.txt`、`DPPO_diffusion_ppo.py.txt`；完整PDF见`metadata/2409.00588v3.pdf` | 两层MDP、Gaussian条件似然、执行片段信用；A.1明确不使用额外微调正则，不支持固定BC KL为普遍必要条件。完整最终动作边缘似然另见C.6 |
| DDPO，2023 / v4更新2024 | https://arxiv.org/html/2305.13301v4 ; arXiv:2305.13301 | **新归档**`DDPO_2305.13301v4.html` | 去噪多步PG；A展示reward过度优化。主要图像生成，不用其纹理/FID解释无人机；解析reward也可能失配，但本项目尚未证明hacking |
| DPOK，NeurIPS 2023 | https://arxiv.org/html/2305.16381v3 ; arXiv:2305.16381 | **新归档**`DPOK_2305.16381v3.html` | 固定预训练参照KL机制；目标是图像ImageReward，与几何任务reward不同，不能照搬效果 |
| PPO，2017 | https://arxiv.org/pdf/1707.06347 ; arXiv:1707.06347 | `RouteA_RL_Global_Audit_sources_20260910/PPO_arxiv_1707.06347.pdf` | old-policy ratio/clip/adaptive KL参照本批采样策略，不等于固定BC参照；基础算法来源，年份早于2020明确保留 |
| Implementation Matters，ICLR 2020 | https://arxiv.org/html/2005.12729v1 ; arXiv:2005.12729 | `RouteA_RL_Global_Audit_sources_20260910/Implementation_Matters_arxiv_2005.12729.pdf` | 实际优化影响trust-region，clip非所有状态ratio硬边界；不是当前LoRA过大学习率的直接证据 |
| FDPP，2025 | https://arxiv.org/html/2501.08259v1 ; https://merl.com/publications/docs/TR2025-053.pdf | `2026-10-12_BC成功能力保持_文献与官方源码/FDPP_2501.08259v1.pdf`及HTML | 固定参照逐去噪KL；偏好与原目标取舍，Push-T并非零损失保持；旧式KL正负号疑点不直接照抄 |
| RLPD，ICML 2023 | https://proceedings.mlr.press/v202/ball23a/ball23a.pdf ; https://github.com/ikostrikov/rlpd | `2026-10-12_BC成功能力保持_文献与官方源码/RLPD_2302.02948.html`、`RLPD_train_finetuning.py.txt` | 持续offline/online数据与critic设计；off-policy SAC方法，不把历史轨迹直接塞入on-policy PPO |
| Bootstrapping RL with Imitation for Vision-Based Agile Flight，CoRL 2024 | https://arxiv.org/html/2403.12203v3 ; arXiv:2403.12203 | `2026-10-12_RL_Reward综合研究/planning_reward/Bootstrapping_2403.12203v3.pdf`及TXT | 非扩散无人机微调初期改善后退化，critic warm-up与自适应更新；任务为竞速控制，不是本项目逐轨迹因果结论 |
| Diffusion-DPO，2023 / CVPR 2024 | https://arxiv.org/abs/2311.12908 ; https://github.com/SalesforceAIResearch/DiffusionDPO | **新归档**`DiffusionDPO_2311.12908_官方摘要.html`；本次核读原摘要与官方项目定位 | 离线图像偏好训练，需成对偏好；不作为在线循环轨迹规划的现成替换。全文本次未取得，不冒称完整全文已读 |

## 新归档完整性

| 文件 | 字节 | SHA256 |
|---|---:|---|
| DDPO_2305.13301v4.html | 468290 | `1044593229b770487e3b409feba7a244bb9d5c55f1c71455c0398fbbd30a8e68` |
| DPOK_2305.16381v3.html | 407943 | `94a1de90c0be34b17da861d77e1829b4b46f7e1b694ec05bd89dd34ebea2e8e6` |
| DiffusionDPO_2311.12908_官方摘要.html | 43786 | `92c5186b67fe1d602e11db5ad23b65b90073c174ddc1361586d5517b2841a1ce` |

本项目证据另以fresh384冻结源码、逐轮metrics、5880条同任务轨迹及既有历史原件为依据。论文的结论、参数和成功率不替代本项目实际计算。
