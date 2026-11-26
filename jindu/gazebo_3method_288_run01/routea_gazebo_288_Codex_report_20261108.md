# Gazebo 三方法 288 条件闭环 — WSL 执行完成报告 v1.0

日期：2026-11-08
执行端：AutoDL 服务器（conda idp3，torch 2.4.1+cu121，Python 3.8，ROS Noetic + Gazebo 11 + PX4 SITL）
角色：执行者。所有数字为执行端实测；判读与裁决归 Codex。
回传位置：`wsl_snapshot/gazebo_3method_288_run01/`（WSL 侧，同步完成后与 Windows 共享）

---

## 1. 结论

**288/288 条件全部完成，基础设施失败 0。** 三种方法（P0 BC / P6@u256 / EGO）各 96 条件，按 `routea_gazebo_a1_tasks_run01/tasks.json` 的 schedule（48 任务 × 2 repeats）在 Gazebo 真实闭环跑完，逐条件 monitor JSON + 逐帧轨迹 CSV + planner 日志全部落盘。

执行期间修复 4 处工程阻塞（EGO 地图包络、monitor world_id 类型、越界判据、EGO 目标入口），均为部署层问题，**未改任何策略算法、训练参数、控制增益或感知算法**；P0/P6 共用同一 backbone（`state_dicts['model']`，identity 040a3378…），唯一差别是 LoRA gate 开关。1 条硬超时按规则队尾重排队 1 次后成功。

## 2. 时间线（2026-11-07 22:44 → 11-08 20:45，约 22h）

| 时间 | 相位 | 事件 |
|---|---|---|
| 11-07 22:44 | Phase F 启动 | 第 1-2 条 no_result（monitor `--world_id` int 冲突，22:46-22:48） |
| 11-07 22:55 | Phase F 重启 | world_id 改 str 后第 1 条正常落盘（P6 collision） |
| 11-07 22:55 → 11-08 18:24 | Phase F 主循环 | 288 条完成（其中 1 条 subprocess_timeout>660s） |
| 11-08 20:40 → 20:44 | 队尾重排队 | 该条重跑后 reached |
| 11-08 20:45 | Phase G | 1.0m 离线重判 + 双口径汇总完成 |

（Phase E 三方法 pilot：11-07 白天完成，不计入分母。）

## 3. 关键数字

### 3.1 判据口径

- **1.0 m 口径（本次指定）**：轨迹任意帧 3D 欧氏距离 ≤ 1.0 m 记到达（closed boundary），first-event 语义（collision > lost > reached > timeout）。与运动学 `terminal_contract.reached_goal(radius)` 同结构，仅半径 0.5 → 1.0。
- monitor 原口径（对照）：`success_deploy` = dxy<0.5 且 dz<0.3 且 v_xy<1.0（5 帧 debounce）。
- 坐标：轨迹 CSV 为 odom 系（原点 = spawn = 任务起点）；goal_odom = goal_world − start_xy（SPAWN_Z=0，odom z 原点在地面 ⇒ z 直接相等）。

### 3.2 结果（96 条件/方法，全部有效，无无效分母）

**1.0 m 口径**

| 方法 | reached | collision | timeout | lost | 到达率 |
|---|---|---|---|---|---|
| EGO | 64 | 15 | 17 | 0 | 66.7% |
| P6@u256 | 46 | 45 | 4 | 1 | 47.9% |
| P0 BC | 39 | 36 | 21 | 0 | 40.6% |

**monitor 原口径（dxy<0.5）**

| 方法 | reached | collision | timeout | lost | 到达率 |
|---|---|---|---|---|---|
| EGO | 64 | 15 | 17 | 0 | 66.7% |
| P6@u256 | 39 | 45 | 11 | 1 | 40.6% |
| P0 BC | 23 | 36 | 37 | 0 | 24.0% |

1.0m 放宽的增量：P0 +16 条（timeout 37→21）、P6 +7 条；EGO 两条口径完全相同（到达时均进入 0.5 m 圈内）。

### 3.3 权重与身份

- P0/P6 backbone：`data/outputs/2026.08.16/08.53.26_e5_lambda0p5/checkpoints/latest.ckpt`，bc_identity_hash `040a337820f10745d158192c4b80737dd028adbf2dd559c037f3112c2bc8b151`（load_native_e5 构造，与 P6 carrier header 逐位一致；非 ema_model）
- P6 LoRA：`dppo_uav_rebuild/routea_a2_selective_keep_run01/T/checkpoint_update_000256`，rank=8/alpha=8.0，lora_identity `4f91a995cff7da0e…`，adapter 1,022,568 参数；gate ON= P6 / OFF= P0
- EGO：无扩散权重，goal 经 `single_run_in_gazebo_task.launch` 的 point0 + 运行时 `/move_base_simple/goal` 下发

## 4. 执行期间修复的工程阻塞（均为部署层，不改算法）

1. **EGO 地图包络**：原 map_size 50×25×3（z ∈ [-0.01, 2.99]，虚拟天花 2.9）装不下任务高度（goal_z 最高 4.50）→ 规划恒失败（`plan_success=0`）。判据实验：同起点只把 goal z 压到 2.0 即成功。放大到 58×58×10、虚拟天花 9.9，仅改实验专用 launch 副本，分辨率 0.1/膨胀 0.3/max_vel 0.5/max_acc 0.25 不变。
2. **monitor `--world_id` 类型**：任务表 world_id 为字符串，monitor argparse 原为 int → 前 2 条 no_result（已重跑，不计失败）。
3. **越界判据**：lost 判据 z 上界 20→10、xy ±15→±25（任务工作包络：dx ∈ [-23.96, 26.28]、dy ∈ [-25.81, 27.58]、z ≤ 4.70）。
4. **EGO 目标入口**：flight_type=2（PRESET_TARGET）在本仓库不可用——`ego_replan_fsm.cpp::init()` 在 exec_state_ 仍为 INIT 时调 `readGivenWps()→planNextWaypoint()`，走进阻塞 else 分支永远停在 WAIT_TARGET（90s 零规划）。改用 flight_type=1（MANUAL_TARGET）+ 建图缓冲后单次发布 `/move_base_simple/goal`。

## 5. 产物

- 服务器与 WSL 同构目录：`program/results/gazebo_3method_288_run01/`，每条件 `{method}/{task_id[:12]}_r{repeat}/`：
  - `result.json`（monitor 原始 JSON）、`result_state.csv`（odom 系逐帧轨迹）、`result_pos_cmd.csv`、`stdout.log`、`planner_logs/`、`condition.json`（方法/任务/权重/命令/环境全记录）
- 汇总：`regrade_1m.csv`（288 条逐条明细，双口径）、`summary_1m.json`、`summary_monitor.json`、`run_log.jsonl`、`run_config.json`（含 tasks.json sha256、ckpt sha256、runner sha256）
- 回传状态：1.2 GB 打包，rsync 断点续传中（网络间歇波动，完整性由 rsync 校验保证）

## 6. 进行中：8 月条件（固定 spawn/goal）重飞

用户指令复刻 8 月三路对比条件（固定 spawn world(-8,0,0)、起飞 2.0 m、goal odom(12,0,2)、layerA 20 world、超时 1200s），三方法各 100 trials = 300 flights。pilot 三方法全部 reached（P6 42.9s / P0 42.4s / EGO 31.1s）。正式批量 11-08 21:33 启动，预计 ~65 小时。完成后单独出报告（与 8 月 E5=79% 同口径对比）。

## 7. 需要 Codex 注意

- 到达判据已按用户指令从 0.5 m 放宽到 **1.0 m**（3D 欧氏，closed boundary），汇总双口径并列，两条口径数字都保留。
- EGO 地图范围（存在范围）放大是本报告唯一"环境参数"级改动，规划算法与代价参数未动；如需核对，改动全部在 `single_run_in_gazebo_task.launch` 文件头注释中。
- 8 月条件实验中 EGO 同样使用放大地图（58×58×10），与 288 条件同口径。
