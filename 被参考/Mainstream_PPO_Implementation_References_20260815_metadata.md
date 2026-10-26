# 主流 PPO 官方实现核验来源元数据

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-08-15 |
| 用途 | 审核 Route A DPPO 训练控制器、rollout buffer、GAE、PPO update、断点恢复与可观测性是否具备主流 on-policy RL 实现的必要语义 |
| 采用边界 | 用于确立实现不变量和审核方法；不要求复制与 DPPO 形式不同的通用 Gaussian PPO 超参 |

## 采用来源

| 来源 | URL | 本项目引用用途 | 相关性判断 |
|------|-----|------------------|------------|
| DPPO 官方代码 | https://github.com/irom-princeton/dppo | diffusion denoising transition、PPO objective、官方训练循环的直接 oracle | [FACT] 最高优先级的算法对齐对象，但不含 UAV adapter、CFG、LoRA 与 Route A 环境 |
| DPPO 论文 | https://arxiv.org/abs/2409.00588 | 核对 DDPO/DPPO 的问题形式、denoising MDP 与 PPO 微调目标 | [FACT] 解释算法语义，不替代生产代码负向测试 |
| CleanRL continuous-action PPO | https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo_continuous_action.py | 联合 rollout shape、GAE、minibatch shuffle、clip loss、gradient clipping、训练指标 | [JUDGMENT] DPPO 官方声明主训练框架遵循 CleanRL，适合检查 on-policy 控制流 |
| Stable-Baselines3 OnPolicyAlgorithm | https://github.com/DLR-RM/stable-baselines3/blob/master/stable_baselines3/common/on_policy_algorithm.py | 固定 rollout horizon、total timesteps 外层控制、定期 dump/eval 与多环境统计 | [JUDGMENT] 用于识别“总预算”和“每次 update 的 rollout 长度”被混为同一参数的错误 |
| Stable-Baselines3 RolloutBuffer | https://github.com/DLR-RM/stable-baselines3/blob/master/stable_baselines3/common/buffers.py | `(n_steps, n_envs)` 存储与按环境时间轴计算 GAE | [FACT] 证明 vector env 不能在交错 flatten 后仅通过相邻 record 递归 |
| OpenAI Spinning Up PPO | https://spinningup.openai.com/en/latest/algorithms/ppo.html | on-policy 数据边界、clip objective、KL early stopping 语义 | [JUDGMENT] 用于审核概念边界；不直接照搬 Gaussian PPO 的 KL 阈值 |
| Gymnasium Time Limits | https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/ | terminated/truncated 对 bootstrap 的区分 | [FACT] 用于核对 GAE 与 episode boundary，不改变 Route A 的任务终止定义 |

## 引用原则

1. [JUDGMENT] 官方 DPPO 负责 diffusion-specific 数学语义；CleanRL/SB3 负责反证通用 on-policy 训练控制器是否完整。
2. [JUDGMENT] Route A 可以保留 UAV observation、11d action、LoRA、CFG=1.5、executed horizon 等适配，但不能破坏 on-policy、时间轴 GAE、旧策略 logprob、可恢复进度和交易式 optimizer step。
3. [RISK] DPPO 的 logprob 聚合维度与数值尺度不同于普通 Gaussian PPO，不得在没有标定前硬套 `target_kl=0.01` 等阈值。
