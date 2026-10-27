# B1 LoRA 缩放评价（论文 4.x 用）

生成日期：2026-10-27。评价清单 `bank.json`，content_hash `863bf1fb2a41c991`，共 420 个任务—重复单元；策略权重为 u32（identity `2f3f9914db78`），仅运行时改变 LoRA 缩放 s，checkpoint 字节与 LoRA identity hash 不变。

## 主表

| LoRA 缩放 s | 到达率 | 95% CI (Wilson) | 到达 / 回合 | 超时 | 碰撞 | 平均决策步 |
|---|---|---|---|---|---|---|
| 0 | 0.269 | [0.229, 0.313] | 113 / 420 | 174 | 133 | 38.52 |
| 0.5 | 0.260 | [0.220, 0.303] | 109 / 420 | 153 | 158 | 35.13 |
| 1 | 0.283 | [0.242, 0.328] | 119 / 420 | 139 | 162 | 36.15 |

## 按任务角色分档

| 角色 | 回合 | s=0 | s=0.5 | s=1 |
|---|---|---|---|---|
| anticipatory | 40 | 0.575 | 0.600 | 0.725 |
| dense_recovery | 300 | 0.200 | 0.207 | 0.250 |
| support_expansion | 40 | 0.500 | 0.275 | 0.250 |
| yaw_lateral_recovery | 40 | 0.250 | 0.300 | 0.125 |

## 逐回合配对差

| 对比 | 增益 | 损失 | 净差 | 不一致对 | 精确 McNemar p |
|---|---|---|---|---|---|
| s=0 → s=0.5 | 28 | 32 | -4 | 60 | 0.6989 |
| s=0.5 → s=1 | 56 | 46 | +10 | 102 | 0.3729 |
| s=0 → s=1 | 68 | 62 | +6 | 130 | 0.6612 |

## 与存档 u32 全量评价的一致性校验

同清单、同协议（`terminate_at_space_limits=false`、reward v2、`jit_optimized_execution=False`）的存档运行：到达率 0.2976，420 回合；本机 s=1.0 与之逐回合一致率 0.9714（增益 3 / 损失 9，McNemar p=0.146）。

存档来源：`/home/cjj/AUV/program/results/routea_paired_evaluation/routea_space_open_v3_run01/full/rl_2f3f9914db78_u32`。
