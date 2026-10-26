# GAE 原文归档与本轮引用用途

| 字段 | 内容 |
|---|---|
| 原文文件 | `Schulman2015_GAE_1506.02438v6_full_20261016.html` |
| 标题 | High-Dimensional Continuous Control Using Generalized Advantage Estimation |
| 作者 | John Schulman, Philipp Moritz, Sergey Levine, Michael Jordan, Pieter Abbeel |
| 首次发表年份 | 2015；ICLR 2016 |
| arXiv ID / 版本 | 1506.02438v6 |
| 来源 URL | https://arxiv.org/html/1506.02438v6 |
| 检索 / 下载日期 | 2026-10-16 |
| 文件字节数 | 309423 |
| SHA256 | b77a508c4efb68f021b574969c24017e2ce7407c98f5db6542111d24227f6329 |
| 对应研究任务 | 独立审查 iDP3-UAV 下一阶段 PBRS、更新组织和验收建议；供 `2026-10-16_继续RL还是转向扩散策略架构_证据比较与下一阶段裁决` 后续审查引用 |
| 引用用途 | §4、公式20—24：potential shaping 下 Q/V 平移而真实 advantage 不变；§3、公式16—19：有限 GAE 与 lambda 的偏差/方差关系。 |
| 与项目的关系 | 项目实际使用 gamma_environment=0.99、gae_lambda=0.95；用于反驳“即时 PBRS 付款即可保证新增有效 actor 恢复信用”的过强说法。本文不证明项目退化由 GAE 或 reward 唯一导致。 |

[FACT] 原始 HTML 直接取自 arXiv，未修改其正文。本轮没有修改训练程序、评价程序、权重或原始实验材料。
