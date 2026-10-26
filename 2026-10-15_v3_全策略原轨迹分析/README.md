# 2026-10-15 v3 全策略原轨迹分析数据（客观数据交付）

本目录为 2026-10-15 v3 开放空间全策略重新评价的分析数据，只提供原始数据与文件定义，
不含统计结论。

## 文件清单

| 文件 | 大小 | 内容 |
|---|---|---|
| `2026-10-15_v3_全策略原轨迹分析数据.json` | 18.4MB | 14 策略 × 420 条件 = 5880 条逐轨迹记录 |
| `2026-10-15_v3_fresh趋势数据.json` | 26.2MB | fresh203 四更新点（u32/u128/u256/u384）+ BC 共 2100 条完整原 JSONL 的趋势数据 |
| `fresh203_training_curve_384.csv` | 52KB | fresh203 训练 384 轮的逐轮计数器与回报记录 |

## 1. 全策略原轨迹分析数据

- 来源：`wsl_snapshot/routea_space_open_v3_run01/`（v3 取消人工空间边界的 5880 条原 JSONL，
  233246 个实际规划周期，84 个几何任务）
- 顶层结构：
  - `records`（5880 条）：每条含 policy / task_id / task / repeat / world / family / blocked /
    obstacle_count / outcome / success / decisions / duration / D0 / path_length_m /
    min_goal_distance_m / final_goal_distance_m / backtrack_m / max_cross_track_m /
    z_span_m / start_z / goal_z / max_z / min_z / max_abs_xy / crossed_goal_plane /
    post_cross_backtrack_ge0p5 / normalized_best_gain / closest_goal_xy / closest_goal_z_error /
    恢复周期计数、reward_sum / discounted_reward / terms 等
  - `summary`（14 策略）：每策略 32 个汇总字段，含 `groups`（blocked/unblocked/
    single_obstacle/dense_family/dense_blocked）与 `families`（9 个任务家族）分层计数
  - `selected_repeat1_cycle_curves`：选定条件的逐周期曲线
  - `geometry_tasks`：84 任务
- 校验：`errors` 数组为空；`max_recomputed_metrics_error` = 3.55e-15

## 2. fresh 趋势数据

- 来源：v3 评价中 fresh203 四个 checkpoint 更新点（u32/u128/u256/u384）+ BC，
  共 2100 条完整原 JSONL（80492 决策周期）
- 顶层结构：`definitions`（8 项口径定义）/ `audits` / `summary`（5 策略 × 27 字段）/
  `timepoint_pairs` / `old_v2_changes` / `task_meta` / `records` / `case_cycles` /
  `case_geometric_evidence` / `task_by_policy`

## 3. fresh203 训练曲线（384 轮）

- 来源：`program/results/routea_training/routea_r1_s2_seed202609203_fresh384_v1/`
  `metrics_update_000001.json` … `metrics_update_000384.json`（每文件约 9.1MB，本地未上传）
- CSV 每行一个 update（1..384），字段：
  - `attempted_updates / committed_updates / rejected_updates / env_steps /
    completed_episodes`：**累计值**（该轮结束时累计；末轮 15360 / 9502 与
    `training_check.json` 一致）
  - `return_count / return_mean / return_std / return_min / return_max`：该轮完成回合的回报统计
  - `done_reason_*`（7 键：reached / collision / time_limit / collection_boundary /
    altitude_exceed / ground_crash / out_of_bounds）：该轮各结局计数；该轮未出现的键留空
  - `rollout_seconds`：该轮 rollout 耗时（秒）
- 校验：384 行；末轮累计 committed_updates=15360、completed_episodes=9502，
  与 `training_check.json` 完全一致

## 未上传的原始文件（路径记录）

- v3 原轨迹 5932 个 jsonl（3.5GB）：`wsl_snapshot/routea_space_open_v3_run01/`，
  亦在 `program/results/routea_paired_evaluation/routea_space_open_v3_run01/`（WSL 侧）
- 384 个 metrics_update JSON（约 3.5GB）与 train.log（4.4MB）：
  `program/results/routea_training/routea_r1_s2_seed202609203_fresh384_v1/`
- 训练起止：metrics_update_000001 写入 2026-10-12 13:30:23，000384 写入
  2026-10-14 01:27:55，training_check 2026-10-14 01:33:37（约 36 小时）
