# 2026-08-21 审稿回应与Reward方法研究来源元数据

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-08-21 |
| 对应报告 | `论文/研究报告/2026-08-21_审稿意见回应与论文方法重构方向研究.md` |
| 检索主题 | top-k可微性、reward shaping、CMDP、安全扩散RL、扩散导航后训练、critic表征、RL统计 |
| 来源原则 | 优先论文原页、PMLR、arXiv、OpenReview、DOI/出版社 |

## 1. 本轮新增本地归档

| 本地文件 | 原始URL | SHA256 | 引用用途 |
|----------|---------|--------|----------|
| `Blondel_2020_Fast_Differentiable_Sorting_and_Ranking.pdf` | <https://proceedings.mlr.press/v119/blondel20a/blondel20a.pdf> | `848D1718874BF4F0383829F758B75A42A6983CE7BEE1D0FCC3B458C1A2F8E31F` | 排序/top-k分段可微与soft排序 |
| `Achiam_2017_Constrained_Policy_Optimization.pdf` | <https://proceedings.mlr.press/v70/achiam17a/achiam17a.pdf> | `738BA84A6CF3D6F947F91A467B13A3C888D908C050A0B9B58D097DA22959A08F` | CMDP与reward/constraint分离 |
| `Stooke_2020_PID_Lagrangian_Safe_RL.pdf` | <https://proceedings.mlr.press/v119/stooke20a/stooke20a.pdf> | `6045646926EF64D811EC7E9B8178EA7A9A022D5458F9AF4D4F87E3F8A4961E51` | 拉格朗日dual振荡与PID缓解 |
| `Agarwal_2021_Deep_RL_Statistical_Precipice.pdf` | <https://arxiv.org/pdf/2108.13264> | `A6A5ABB49E58A9E4A0BE8556C8351CE8C3B52E70216BFFC9FA80EAC0823EC5ED` | 少seed的IQM、bootstrap CI、performance profile |
| `Pinto_2017_Asymmetric_Actor_Critic.pdf` | <https://arxiv.org/pdf/1710.06542> | `E807F73E6EF36ADF219025A5DD5EC292F54A05032CBB86BA7FABA39BB6CBED6A` | 训练期特权critic |
| `Sheng_2026_Beyond_Imitation_Diffusion_Navigation_RL.pdf` | <https://arxiv.org/pdf/2603.12868> | `1DAA2516C59B3113A703F1BEC7C3E99881830F431049D6AD51A58D05BABD88D9` | critic-free GRPO扩散导航直接竞品 |
| `Ng_1999_Policy_Invariance_Reward_Shaping.pdf` | <https://www.cdf.toronto.edu/~csc2542h/fall/material/csc2542f16_reward_shaping.pdf> | `F21720E09F874C7598B0E9954C571CF73A8C925397AE5E2631E7FE0E8814635D` | 严格potential-based reward shaping |
| `Cheng_2026_ALGD_Safe_RL_Diffusion.pdf` | <https://arxiv.org/pdf/2602.02924> | `240E5D181BFB5B4C6F72C7921CD4A4EE8BDE27C977B6058AE65DD4B9EFA04471` | 增广拉格朗日安全扩散RL直接竞品 |
| `SafeDiffuser_arxiv_2306.00148.pdf` | <https://arxiv.org/pdf/2306.00148> | `E88730F95407ABFE5575F5C7CD234EAB578C0C176ABA0E6B859531010A185071` | 扩散过程内CBF/安全约束 |

## 2. 已有本地归档复用

| 本地文件 | 原始来源 | 引用用途 |
|----------|----------|----------|
| `Diffusion Policy Policy Optimization.pdf` | <https://arxiv.org/abs/2409.00588> | DPPO数学与训练范式 |
| `CGD - Constraint-Guided Diffusion Policies.pdf` | <https://arxiv.org/abs/2405.01758> | UAV约束扩散直接先例 |
| `iDP3 - Generalizable Humanoid Manipulation with 3D Diffusion Policies - arxiv_2410.10803.pdf` | <https://arxiv.org/abs/2410.10803> | iDP3通用3D策略定位 |
| `DSRL - Steering Your Diffusion Policy with Latent Space RL - arxiv_2506.15799.pdf` | <https://arxiv.org/abs/2506.15799> | 扩散策略latent RL后训练对照 |
| `DiPOD - Diffusion Policy Optimization without Drifting Apart - arxiv_2606.13795.pdf` | <https://arxiv.org/abs/2606.13795> | 预训练策略漂移与后训练稳定性背景 |

## 3. 仅保存权威网页元数据的来源

| 资料 | 权威页面 | 未保存PDF原因 | 用途 |
|------|----------|---------------|------|
| Liu et al., GRPO-MDP, Alexandria Engineering Journal 2026 | <https://doi.org/10.1016/j.aej.2026.02.024>；<https://doaj.org/article/d80290c8d8334a89a34185c532d8ca19> | 出版社页面返回403，DOAJ和出版社摘要可核验；ResearchGate标记无全文 | DDPM+GRPO+UAV+CBF直接竞品 |
| Ebi et al., Informed Asymmetric Actor-Critic | <https://arxiv.org/abs/2509.26000> | 本轮只使用摘要与理论定位，未下载全文 | 任意状态相关特权critic信号 |
| Loquercio et al., Learning High-Speed Flight in the Wild | <https://arxiv.org/abs/2110.05113> | 仅作背景定位，非方法推导依据 | UAV端到端局部轨迹策略背景 |

## 4. 状态与限制

- `Beyond Imitation` 与 `ALGD` 在本报告中按arXiv预印本处理，不把预印本状态写成已正式录用事实。
- SafeDiffuser的ICLR官方PDF下载接口在本次终端请求中返回403/空响应，已改为归档arXiv版本；论文引用时应以最终ICLR 2025版本为准。
- GRPO-MDP全文未获得，本报告关于其方法的判断仅基于出版社/DOAJ摘要中明确披露的DDPM、GRPO、hindsight relabeling和CBF，不推断摘要外实现细节。
- 所有新下载PDF已通过`pypdf`读取页数验证，未发现损坏文件。

