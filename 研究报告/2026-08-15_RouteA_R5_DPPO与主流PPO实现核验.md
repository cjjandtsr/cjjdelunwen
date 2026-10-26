# Route A R5 DPPO 与主流 PPO 实现核验

| 字段 | 内容 |
|------|------|
| 日期 | 2026-08-15 |
| 研究类型 | 官方代码与主流 on-policy RL 实现对照 |
| 项目阶段 | Route A R5 修复后、G7 诊断运行中、G8/G9 尚未准入 |
| 直接输出 | `sheji/RouteA_R5_DPPO训练系统代码级二次审查与ENGINE_CORRECT补完设计_v1_0_20260815.md` |

## 1. 项目进展摘要

[FACT] 当前生产 kernel 已解决旧版最严重的去噪 step 更新漏洞：冻结 DPPO vendor 数值 parity 、联合 environment×denoising `randperm`、真 microbatch 梯度累积与 5 个去噪 step 的 LoRA 梯度都已有证据。

[JUDGMENT] 这些成果证明 DPPO core 已经形成，但不足以证明“可靠的完整 RL 训练系统”。总预算控制、跨进程 active-slot 恢复、vector-env GAE、reward/outcome 同一性、checkpoint release、paired-eval RNG 绑定、方差坐标系和数值交易边界仍有生产级缺口。

## 2. 检索范围与来源

检索日期为 2026-08-15。采用的一手来源如下：

- DPPO 官方仓库：https://github.com/irom-princeton/dppo
- DPPO 论文（arXiv:2409.00588）：https://arxiv.org/abs/2409.00588
- CleanRL PPO continuous action：https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo_continuous_action.py
- Stable-Baselines3 OnPolicyAlgorithm：https://github.com/DLR-RM/stable-baselines3/blob/master/stable_baselines3/common/on_policy_algorithm.py
- Stable-Baselines3 RolloutBuffer：https://github.com/DLR-RM/stable-baselines3/blob/master/stable_baselines3/common/buffers.py
- OpenAI Spinning Up PPO：https://spinningup.openai.com/en/latest/algorithms/ppo.html
- Gymnasium terminated/truncated：https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/

详细引用用途与相关性见 `论文/被参考/Mainstream_PPO_Implementation_References_20260815_metadata.md`。

## 3. 官方/主流不可破坏的实现语义

1. [FACT] DPPO 将 diffusion denoising 步作为额外 MDP 维度，重新计算新策略 logprob 与 rollout 期保存的旧 logprob，再做 PPO clipped ratio。
2. [FACT] 主流 on-policy PPO 把“训练总 timesteps”与“每次 policy update 收集的 rollout horizon”分开。最后一次可以是短 rollout，但总计数必须可解释。
3. [FACT] vector environment 的 GAE 必须沿同一 env/slot 的时间轴递归，而不是沿 flatten 后的相邻 record 递归。
4. [FACT] `terminated` 与 `truncated` 对 bootstrap 影响不同；任务成功、碰撞和超时必须由同一 outcome 真值源定义。
5. [JUDGMENT] 只有当 rollout、update、checkpoint、resume 和 eval 组成的整体系统经过真入口、断点、冷启动与负向故障注入测试，才能排除“组件测试全过但生产接线仍错”。

## 4. 对 iDP3-UAV 的可迁移结论

- [JUDGMENT] 必须保留：冻结 official DPPO core/oracle、准确 old/new logprob、executed horizon、denoising discount、联合 shuffle、on-policy 数据一次性、时间轴 GAE、可恢复训练进度。
- [JUDGMENT] 可合理适配：Phase1aPolicyFM/DDIM adapter、point-cloud observation、11d action、LoRA-only actor、mean-pool critic、CFG=1.5、Route A role sampler。
- [JUDGMENT] 不应机械照搬：普通 Gaussian PPO 的 entropy 形式、KL 阈值、learning rate、epochs 或 action std schedule。这些要在引擎正确后用 DPPO 实际数值标定。

## 5. 对三个项目能力目标的意义

[JUDGMENT] 提前避障、full-space support expansion 与密集障碍脱困不能由“PPO loss 可以 backward”保证。先建立 `ENGINE_CORRECT`，再检验 reward/role/task 是否对这三种能力提供可学信号，最后用固定 paired evaluation 和 multi-seed 终点指标判定。训练曲线平滑不是最终目标。

## 6. MC-1～MC-5 合规核对

[PROVEN] 本研究只要求修复训练语义、事务安全、证据绑定和可观测性，不引入策略外轨迹修剪，不重采集 EGO 数据，不使用 projection 美化结果，因此与 MC-1～MC-5 相容。

## 7. 未采纳的简化做法

- 不以“已经有 549 个测试”代替 canonical entrypoint 组成测试。
- 不以当前 G7 的 update norm 非零代替总预算、resume、outcome 和 eval 正确性。
- 不因 KL/clip fraction 偏大就立即压平更新；必须先排除引擎漏洞，再完成预注册预算，最后裁决超参。
