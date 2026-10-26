# Route A PPO 有限时域与实现选择核验

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-09-20 |
| 用途 | 核验 Route A v1.7 time-limit、GAE bootstrap、advantage normalization 根因解释 |
| 资料范围 | 原始论文 / 官方论文入口 |

## 1. Time Limits in Reinforcement Learning

- 来源：Fabio Pardo et al., ICML 2018, arXiv:1712.00378
- URL：https://arxiv.org/abs/1712.00378
- 本地副本：`论文/被参考/Pardo2018_Time_Limits_in_Reinforcement_Learning_arXiv1712.00378.pdf`
- SHA256：`5BB677EE1A3D6916AEDF7D6DF74463238CFE792FC348976502F46C14998067C6`
- 关键结论：论文明确区分两类 time limit。若固定期限就是任务目标的一部分，剩余时间必须进入状态以保持 Markov 性；若 time limit 只是无限时域任务的训练截断，则应在截断点 bootstrap。
- 与本项目关系：Route A 的正式目标是“在 60 step 内安全到达原始目标”，属于前一种有限时域语义。当前实现却采用后一种 bootstrap 语义，且 9D 状态不含剩余时间；本项目数据又显示 timeout 获得正 actor 信用，因此该不一致是实质根因候选，而非纯理论洁癖。

## 2. Proximal Policy Optimization Algorithms

- 来源：John Schulman et al., arXiv:1707.06347
- URL：https://arxiv.org/abs/1707.06347
- 本地副本：`论文/被参考/Schulman2017_Proximal_Policy_Optimization_Algorithms_arXiv1707.06347.pdf`
- SHA256：`E78FEADADBDBB0B601B3C2BCC81404722CD431A489B307545F9B7BEA1E8C4F5B`
- 关键结论：PPO 的核心是基于 advantage 的 clipped surrogate objective 与同一批样本上的多轮优化。论文并不意味着任意全局 advantage 重中心化在异质 outcome/role 混合下都保持任务语义。
- 与本项目关系：当前 Route A actor 更新直接使用全逻辑 batch 标准化后的 advantage；因此本地观测到的符号翻转必须作为实现行为实测，而不能以“PPO 常见做法”直接判为无害。

## 3. What Matters In On-Policy Reinforcement Learning?

- 来源：Marcin Andrychowicz et al., arXiv:2006.05990
- URL：https://arxiv.org/abs/2006.05990
- 本地副本：`论文/被参考/Andrychowicz2020_What_Matters_In_On-Policy_RL_arXiv2006.05990.pdf`
- SHA256：`2BB27A66690D6F8163680235847BB4AB670F8F455A8F360E701E7BBE4FA6D7FB`
- 关键结论：on-policy RL 的大量低层实现选择会显著改变结果，且选择之间存在交互；应在统一框架内进行受控比较，而不是从单一 benchmark 默认值推断。
- 与本项目关系：支持当前“同 transition、同 checkpoint、只替换信用定义并比较梯度方向”的反事实设计；不支持一次同时改 reward、学习率、训练世界与正则项。

## 4. 综合裁决

1. [SUPPORTED] 文献与本地代码/数据共同支持：Route A 当前把有限时域任务按训练截断处理，语义不一致。
2. [PROVEN BY LOCAL DATA] 文献不能证明 seed3 根因；真正使该问题落地的是本地 96 update ledger、15 probe 与 3840 条轨迹中的 timeout 正信用、成功曝光枯竭和目标恢复失败。
3. [JUDGMENT] 下一步应做受控梯度反事实与目标条件敏感性测量；在此之前，不应仅凭通用 PPO 经验直接改 reward 或延长训练。
