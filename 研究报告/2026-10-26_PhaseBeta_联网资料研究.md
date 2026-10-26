# 2026-10-26 Phase β 联网资料研究

## 1. 本期项目上下文摘要

[FACT] 本期先读取了 `AGENTS.md`、`sheji/`、`zhidao/`、`jindu/`、`论文/被参考/`、`论文/未被参考/` 与 `论文/开题报告参考文献/`；`program/jindu/jindu.txt` 不存在。当前实际训练入口不是新的 flow-policy 分支：A2 是从共同协议 B2560-u128 派生的 C/T 单因素续训，唯一算法差别为 T 在原 DPPO actor 更新内增加来自训练几何成功轨迹的掩码 x0 保持项。

[FACT] A2 的首个 WSL 执行已完成父身份、参考采集、旧代码重放和 C-u129；T 的首次保持项因真实 E5 runtime 没有 `alphas_cumprod` 而停止。该报告数值（126 任务、252 回合、549 前缀、rl_only=23）尚未由 Codex 取得原始回传验收，故只作执行侧报告记录。窄修复改为按实际 `ddim_t`/`ddim_alphas` 取系数；本地真实 runtime 定向测试及相关套件 150 passed，但修复后 C/T 训练与能力评价仍未完成。

[JUDGMENT] 因此本期的研究问题冻结为：

1. 在不混入 flow-RL、外部 shield 或新 reward 的条件下，选择性成功行为保持可以检验什么，不能检验什么？
2. 对提前避障、full-space support expansion 和 dense-obstacle capability ceiling，A2 应如何报告能力而不把代理损失或开发集表现当作结论？
3. 哪些近期方向不应在 10 月 31 日节点前插入当前单因素试验？

## 2. 检索范围与关键词

[FACT] 以 arXiv 官方页面、已有全文/网页快照及官方元数据为核验来源。检索词包括 `diffusion policy RL fine-tuning preservation`, `action-chunking diffusion corrections`, `multimodal diffusion policy`, `UAV obstacle avoidance benchmark`, `point cloud diffusion policy`、`time limits reinforcement learning`。

[ASSUMPTION] 未同行评审的预印本仅提供受条件限制的方法或反例线索，不构成飞行安全、实机迁移或因果根因的证明。

## 3. 候选资料总表

| 候选资料 | 作者；年份；标识 | 官方来源 | 是否下载/已有归档 | 处理与理由 |
|---|---|---|---|---|
| Diffusion Policy Policy Optimization | Ren et al.; 2024；arXiv:2409.00588v3 | <https://arxiv.org/abs/2409.00588> | 已有 PDF/HTML | 采纳：当前 DPPO 单因素对照的算法边界。 |
| Generalizable Humanoid Manipulation with 3D Diffusion Policies | Ze et al.; 2024（v3 2025）；arXiv:2410.10803 | <https://arxiv.org/abs/2410.10803> | 已有 PDF/HTML | 采纳：点云条件 diffusion policy 的相邻证据；不外推为 UAV 结果。 |
| Beyond Imitation: RL Fine-Tuning for Adaptive Diffusion Navigation Policies | Sheng et al.; 2026；arXiv:2603.12868v1 | <https://arxiv.org/abs/2603.12868> | 已有 PDF/HTML | 采纳：选择性冻结/更新与导航 fine-tuning 的近邻反例；算法不可直接替换。 |
| Immiscible Diffusion Policy: Preserving Multimodal Robot Actions through Label-Free Noise Assignment | Zhang et al.; 2026；arXiv:2610.09369v2 | <https://arxiv.org/abs/2610.09369> | 已有 v1 PDF/HTML；本期核验 v2 摘要 | 采纳为限制性证据：动作模态保持不等于闭环旧成功保持。 |
| Time Limits in Reinforcement Learning | Pardo et al.; 2018；arXiv:1712.00378v4，PMLR 80 | <https://arxiv.org/abs/1712.00378> | 已有 PDF | 采纳：真期限/人为截断和 bootstrap 的条件边界。 |
| AvoidBench: A high-fidelity vision-based obstacle avoidance benchmarking suite for multi-rotors | Yu, de Croon, De Wagter；2023；arXiv:2301.07430；DOI 10.1109/ICRA48891.2023.10161097 | <https://arxiv.org/abs/2301.07430> | 已有项目引用资料，未重复下载 | 采纳：多旋翼避障应报告环境/性能分层，而非用障碍数或世界名代替难度。 |
| Set-Supervised Diffusion Policy: Learning Action-Chunking Diffusion through Corrections | Li et al.; 2026；arXiv:2606.01865v1 | <https://arxiv.org/abs/2606.01865> | 未下载 | 未采纳：需人工正负纠正 action chunks；本项目没有该数据，加入会变更 A2 的单因素合同。 |
| Reinforcement Learning with Action Chunking | Li, Zhou, Levine；2025；arXiv:2507.07969 | <https://arxiv.org/abs/2507.07969> | 已有历史 metadata，未重复下载 | 未采纳：其 TD/offline-to-online Q-chunking 不是现有 on-policy DPPO 的小修改。 |

## 4. 被采纳资料与核心贡献

### 4.1 保持项不是安全或新能力的代理指标

[FACT] DPPO 将 diffusion 去噪过程用于 policy-gradient fine-tuning；其公开摘要报告连续控制上的稳定微调和鲁棒性，但不声称固定 BC 保持损失是普适必要条件。Beyond Imitation 则在 PointGoal/Isaac Sim 中冻结视觉编码器、选择性更新较高 decoder/action head，并使用 GRPO；它报告未见场景的 Success Rate 提升，但其二维视觉导航、无 value network 和更新对象均不同于本项目。[DPPO](https://arxiv.org/abs/2409.00588) [Beyond Imitation](https://arxiv.org/abs/2603.12868)

[JUDGMENT] 两者合起来只支持一个窄判断：保留预训练表征/行为是可检验的工程干预，不能把 A2 的 `L_keep` 下降、参考轨迹重建，或 T 对 C 的改善写成“已定位 DPPO 失败根因”。当前 A2 采用同一父 u128、同预算 C/T、同 reward/critic/H4/H8 的设计，恰可把该问题限制为本次干预是否减少闭环能力流失。

### 4.2 模态保持与任务成功保持是不同命题

[FACT] Immiscible Diffusion Policy 的摘要指出独立 action-noise 配对可能使低维稠密动作空间的 diffusion 路径混合，并以训练期 noise assignment 保留多模态动作；论文报告的是模态比例和任务表现。它没有在本项目的三帧点云、H16/H4 执行、PPO 在线数据或 UAV 期限下验证旧成功集合保持。[Immiscible Diffusion Policy](https://arxiv.org/abs/2610.09369)

[JUDGMENT] 即使 A2 发现某些绕行/退让输出消失，也不能直接更换为 Immiscible 的噪声分配：这会同时改变扩散训练路径与当前 RL 归因。它可作为 A2 后的诊断假设（是否存在模式覆盖退化），不是 10 月节点前的训练臂。

### 4.3 三类能力需要完整轨迹分层

[FACT] iDP3 提供点云条件 diffusion policy 的跨任务背景，AvoidBench 为多旋翼避障提供环境与性能指标共同刻画的 benchmark，而 Time Limits 明确区分“固定期限本身属于任务”与“仅为收集而截断”的两种语义：前者需要让剩余时间成为状态的一部分，后者才应 bootstrap。[iDP3](https://arxiv.org/abs/2410.10803) [AvoidBench](https://arxiv.org/abs/2301.07430) [Time Limits](https://arxiv.org/abs/1712.00378)

[JUDGMENT] 这三者支持保留项目已选择的完整轨迹审计：在实际 60 决策期限下，不把近目标超时、短窗 `window_end` 或仅开环 H4 投影误作安全到达。它们也支持按可通行性、直连是否受阻、起点/目标方位和实际 x/y/z 路径范围分层；但不支持用当前 21 个训练几何上的 420 开发条件宣称未见几何泛化。

## 5. 未采纳资料与原因

[FACT] Set-Supervised Diffusion Policy 使用人类纠正所形成的正/负 action-chunk 对来训练；当前 A2 的参考库只含训练世界中 BC/u128 的成功轨迹，不具备人工纠正对。[Set-Supervised Diffusion Policy](https://arxiv.org/abs/2606.01865)

[JUDGMENT] 将其 contrastive correction 机制加入会引入新的数据来源、负样本定义和训练目标，破坏 C/T 仅差一个保持项的可解释性，因此不采纳也不归档。Q-chunking 同理：其 TD/Q 学习与离线到在线设定不能用于修改正在运行的 on-policy DPPO，而非“action chunk”一词相同就可移植。

## 6. 对 iDP3-UAV 的可迁移建议

1. [JUDGMENT] 先完成 DDIM 修复后的 C/T-u129 连续性门禁，再运行固定 u256；不要因本期文献改 reward、actor LR、critic、encoder、H4/H8、训练池或 11D 动作。
2. [JUDGMENT] 主判断必须是 T 相对 C 的配对安全到达净差与碰撞变化；随后分别报告相对 BC 的旧成功保留、相对 u128 的新增成功保留，以及 u128 失败条件中的新成功。`L_keep`、训练 reward 或单个中间 checkpoint 不能替代它们。
3. [JUDGMENT] 提前避障应使用完整轨迹中的提前转向/横移与安全到达共同报告；full-space 应联合 x/y/z、目标方位、实际路线范围与碰撞/到达；dense-obstacle 应以真实受阻/可通行性和配对转移定义，不能由世界名或障碍数代替。
4. [JUDGMENT] 若 T 只保住旧成功却压制 u128 已有的困难新成功，应判为“保持—探索权衡未达标”，不加大 λ、不重筛参考回合，也不把外部 planner/shield 作为补救。若 T 对 C 无净安全收益，否定的是本次参考库、掩码、系数和预算组合，而不是整体 diffusion 或滚动规划。

## 7. MC 合规检查

| 约束 | 本期核查 |
|---|---|
| MC-1：策略输出即执行轨迹 | [FACT] 未采纳 action projection、shield、外部 planner 或后处理修轨。 |
| MC-2：diffusion policy 是策略核心 | [FACT] A2 保持项在实际 actor FT 分支内；没有新增策略外决策器。 |
| MC-3：约束在学习阶段处理 | [JUDGMENT] 使用训练期保持项、既有 reward 与完整评价；拒绝 SDP 的人类干预链和所有部署时纠错链。 |
| MC-4：EGO/data frozen | [FACT] 参考只来自已准入 21 个训练几何；val20/test12/eval-only 及 420 开发轨迹不进参考库。 |
| MC-5：safe arrival 主终点 | [JUDGMENT] 把安全到达、碰撞与配对救回/流失作为主判据；模态保持、平滑或损失下降不能单独通过。 |

## 8. 风险与不确定性

- [FACT] A2 修复后的 WSL C/T、统一评价和原始回传尚不存在；当前任何“有效/无效”的断言都超出证据。
- [UNCERTAIN] 执行侧报告的参考库数量与 `rl_only=23` 尚未独立验收；它们不得成为论文数字或调参依据。
- [UNCERTAIN] Beyond Imitation、Immiscible DP 与 SDP 都是预印本/相邻机器人设置，未证明对 UAV 端到端点云轨迹或 Gazebo/PX4 的迁移。
- [JUDGMENT] 10 月 31 日节点前再次引入 flow-RL、TD/Q-chunking、human-correction 数据或部署 shield 会扩大变量数，并使 A2 即使成功也无法作清楚归因。

## 9. 下一步建议

[JUDGMENT] 最小可裁决动作是执行已交付的 DDIM 修复恢复链：保留 v1.1 的失败证据，从父 u128 重新分叉 C/T，先检查新的 u129 连续性、λ 有限性及 C/T 首轮同 rollout/raw GAE；通过后完成两臂固定 u256 与统一轻量评价。随后以原始轨迹作独立验收，再决定是否启用封存 test12。该顺序最直接服务于“dense-obstacle detour/escape/recovery 是否有安全净收益”的 10 月节点；它不承诺结果，也不把 lightweight 结果冒称 Gazebo/PX4 或实机结果。

[FACT] 本报告实际引用资料的在库原件、核验版本和 SHA256 见 [`C:\Users\cjj\Desktop\IDP3\论文\被参考\metadata\2026-10-26_PhaseBeta_联网资料研究_metadata.md`](../被参考/metadata/2026-10-26_PhaseBeta_联网资料研究_metadata.md)。未采纳资料未写入 `论文/被参考/`。
