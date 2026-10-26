# 机器人 Flow-RL 路线资料归档元数据

| 字段 | πRL | Reinforcement Learning for Flow-Matching Policies |
|------|-----|-----------------------------------------------|
| 检索日期 | 2026-08-29 | 2026-08-29 |
| arXiv | 2510.25889v3 | 2507.15073v1 |
| URL | https://arxiv.org/abs/2510.25889 | https://arxiv.org/abs/2507.15073 |
| DOI | 10.48550/arXiv.2510.25889 | 10.48550/arXiv.2507.15073 |
| 本地文件 | `piRL_arxiv_2510.25889.pdf` | `RL_for_Flow_Matching_Policies_arxiv_2507.15073.pdf` |
| SHA256 | `484E9F8BE118BE4F7ADFD18470ABC330E29B1B4CF457D316DC85A63E65299D36` | `D8453444C3C81178B550EAAAA94D80543F5F774649FC417D7A44E76AB27F2038` |
| 采用状态 | 已采用 | 候选参考 |

## 引用用途

### πRL

- [FACT] 用于证明 Flow-Noise、Flow-SDE、PPO 与 GRPO 已经进入机器人 VLA online RL，而非停留在图像生成。
- [FACT] 用于同协议 PPO/GRPO 反证：LIBERO 上 π0 的 PPO/GRPO 平均成功率为 96.0%/90.0%，π0.5 为 97.9%/91.5%。
- [JUDGMENT] 该结果反驳“critic-free GRPO 必然优于 PPO”，但不能直接外推 UAV。

### Reinforcement Learning for Flow-Matching Policies

- [FACT] 用于核验另一条 robot FM+GRPO 路线：advantage-weighted flow matching + learned reward surrogate。
- [FACT] 用于核验同状态 group 的仿真 reset 要求，以及真实世界中改用 learned reward surrogate 的原因。
- [RISK] 论文实验为二维 fully-observed unicycle；reward surrogate 可能高估 OOD action chunks，不能直接作为 iDP3-UAV 实现模板。

## MC 边界

- 两篇工作本身不要求执行期轨迹投影，数学上可保持策略内更新。
- iDP3-UAV 迁移仍须冻结 11d chunk、body-frame、FM FP32 与无策略外轨迹修正边界。
- 任何 learned reward surrogate 必须设置真实 rollout 校准与 anti-hacking gate，否则不满足 MC-5 可分离归因要求。
