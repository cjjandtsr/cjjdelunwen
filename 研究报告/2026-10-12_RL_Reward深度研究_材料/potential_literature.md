# 有界势能候选：两篇原文研究与项目推导边界

| 字段 | 内容 |
|---|---|
| 日期 / 版本 | 2026-10-12 / v1.0 |
| 范围 | S1、S2两篇独立论文；不与13篇算法和17篇规划材料重复计数 |
| 原件 | `论文/被参考/2026-10-12_RL_Reward综合研究/potential_shaping/` |
| 使用方式 | 为综合报告的局部反馈、有限期限和任务优先关系提供依据；候选未训练、未批准 |

## S1：On the Sample Efficiency of Abstractions and Potential-Based Reward Shaping in Reinforcement Learning

[FACT] 作者Giuseppe Canonaco、Leo Ardon、Alberto Pozanco、Daniel Borrajo；[arXiv:2404.07826](https://arxiv.org/abs/2404.07826)，首次2024年，本轮读[2025-08-11 v2](https://arxiv.org/html/2404.07826v2)的§2.2、§5及相关实验。完整HTML原件保存成功，初次SSL超时记录保留于inventory。

[FACT] 有界势能$F=\gamma\Phi(s')-\Phi(s)$在相应无限时域条件下保持策略排序；有限轨迹新增折扣和为$\gamma^H\Phi(s_H)-\Phi(s_0)$，末状态残项可能改变排序。作者研究抽象价值势能及其样本效率；验证一个导航环境和三个ALE游戏。其目标型MDP定理有任务/转移及势能条件，不能直接赋给当前含风险与历史进展的R1。

[JUDGMENT] 对项目的用途是先核terminal、timeout及γ，再谈势能。综合报告的全真终止设0、初始势能−1/2及悬停/闭环成本证明是本项目自行推导，不是论文保证UAV会提升。精确value下优势可能不变，收益需要实训检验。抽象求解器不是本轮实现候选，代价与信息要求另审。

## S2：HPRS: hierarchical potential-based reward shaping from task specifications

[FACT] 作者Luigi Berducci、Edgar A. Aguilar、Dejan Nickovic、Radu Grosu；[Frontiers主源及DOI](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1444188/full)，发表于**2025-02-10**，DOI为10.3389/frobt.2024.1444188。本轮读任务层级、势能构建、comfort消融和局限，完整HTML已保存；文件旧名`HPRS_2024.html`仅依DOI命名，不作为发表年份证据。

[FACT] 方法从任务规范中的安全、完成和舒适优先关系构造势能，验证八个环境。舒适目标与主要任务一致时可有收益，冲突时其作用受层级限制；连续任务需要足够有信息的函数，标量化和优先级并非自动解决所有任务。

[JUDGMENT] 本项目可借鉴“到达优先、效率为次、允许必要退距/飞高”的明确关系，而不复制安全优先成永不运动或人工禁飞。该论文没有验证当前H8/H4、BC保持、LoRA PPO的三维未知障碍任务；本轮未核其官方训练关键源码，不纳入14仓库数。

## 项目候选的独立校验

[PROVEN] 综合报告§8.2取$\Phi=-d/(d+D_0)$、β示例1/2/4、γ=.99；21条原执行轨迹影子评分的伸缩恒等式最大误差1.665×10⁻¹⁶。真终止清0，采集截断保持末状态；β≤4时无newbest/risk的悬停及同奖励状态闭环不能有正净收益。详见`bounded_potential_candidate_shadow.json`。

[UNCERTAIN] 这些性质不证明近似critic/有限样本下提升，也不证明欧氏势能能表达障碍拓扑。必要退距仍受局部分数影响；当前384保持原样，下一候选须训练域校准、设计审查与独立同任务评价。
