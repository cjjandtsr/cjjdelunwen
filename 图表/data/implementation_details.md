# A5 实现细节参数（论文 3.6 / 4.1.1 用）

生成日期：2026-10-26
状态标注：`[FACT 代码]` 由程序实现或产物实测；`[FACT 产物]` 由 zarr/ckpt/文件时间戳实读；`[JUDGMENT]` 推断（已写明依据）；`[缺口]` 现有制品无法确证。

---

## 1 示范数据

| 项目 | 值 | 来源 | 状态 |
|---|---|---|---|
| 数据集文件 | `avoidance_dataset/merged_body_12.zarr` | ckpt `cfg.task.dataset.zarr_path` | [FACT 产物] |
| 示范回合数 | 988 | `meta/episode_ends` 长度 | [FACT 产物] |
| 总帧数 | 60151 | `meta/episode_ends[-1]` | [FACT 产物] |
| 数组形状 | point_cloud (60151,4096,6)、state (60151,9)、action (60151,11) | zarr 实读 | [FACT 产物] |
| 有效点通道 | 3（XYZ），第 4–6 通道为颜色，训练时 `use_pc_color=false` | ckpt `cfg.policy.use_pc_color` | [FACT 代码] |
| 训练/验证划分 | `val_ratio=0.1`，划分种子 42 | ckpt `cfg.task.dataset` | [FACT 产物] |
| 采样窗口 | horizon 16，pad_before 2，pad_after 7 | ckpt `cfg.task.dataset` | [FACT 产物] |
| 末段加权 | `end_weight=3.0`，`end_dist_threshold=2.0 m`（dist<2 m 的窗口采样权重 ×3） | `drone_dataset.py:60,66-67` 构造默认值；ckpt cfg 未显式记录 | [FACT 代码] |
| 采集环境（世界）数量与家族构成 | 无记录，正文亦未使用该数字 | `.zattrs` 只有格式/版本/时间字段，无 world 字段；`merged_body_12.zarr/.zattrs` 的 `merged_from` 只列 994 个 zarr 文件名 | [缺口，不入稿] |
| 采集时间分布 | 2026-04-10 ~ 04-21，9 个采集日：6 / 62 / 10 / 18 / 210 / 213 / 166 / 275 / 34 = 994 个单回合目录 | 逐个读 `zarr_body/*/.zattrs` 的 `created` 字段 | [FACT 产物] |

### 1.1 数据增强（`augment_pc=true`）

| 增强 | 参数 | 实现语义 | 来源 |
|---|---|---|---|
| 点丢弃 | `pc_dropout_range=(0.7, 1.0)` | 每帧随机保留 U(0.7,1.0) 比例的点，其余置零（不重采样） | `drone_dataset.py:189-194` |
| 坐标抖动 | `pc_jitter_std=0.02 m` | XYZ 加 N(0, 0.02) 高斯噪声 | `drone_dataset.py:197-198` |
| 深度噪声 | `pc_depth_noise_coeff=0.001`，`pc_depth_noise_max=0.03` | 每点 σ=min(0.001·d, 0.03) 加噪，d 为该点距离 | `drone_dataset.py:201-204` |
| 整场景旋转 | `pc_rotation_range=30.0°` | 偏航角 U(−30°, +30°) 同时作用于点云、状态位置与偏航表示、动作的三组三分量 | `drone_dataset.py:207-217` |

---

## 2 深度相机（合成观测，与仿真 D435i 一致）

| 项目 | 值 | 来源 | 状态 |
|---|---|---|---|
| 分辨率 | 320 × 240 | `synth_pointcloud.py:31-32` | [FACT 代码] |
| 水平视场角 | 60°（1.047198 rad），fx=fy≈277.1 px | `synth_pointcloud.py:33-38` | [FACT 代码] |
| 探测范围 | near 0.05 m，far 10.0 m | `synth_pointcloud.py:52-57` | [FACT 代码] |
| 安装位置 | 机体前向 0.12 m、侧向 0、下方 0.015 m | `synth_pointcloud.py:63-66`（对齐 `iris_D435i.sdf`） | [FACT 代码] |
| 安装朝向 | 下俯 8° | `synth_pointcloud.py:69-71` | [FACT 代码] |
| 每帧点数 | 4096 | ckpt `shape_meta` / `pointcloud_encoder_cfg.num_points` | [FACT 产物] |
| 传感器噪声（合成默认） | 深度乘性 σ=0.5%、随机点缺失 5% | `synth_pointcloud.py:263-266` | [FACT 代码] |
| 更新频率 | 每个决策周期一次（执行段 0.3 s → 名义 3.3 Hz） | 由执行协议推得，无独立实测 | [JUDGMENT] |

---

## 3 场景

### 3.1 强化学习环境世界（`PX4-Autopilot/Tools/sitl_gazebo/worlds/`）

| 项目 | 值 | 状态 |
|---|---|---|
| 世界文件数 | train 180、val 60、test 52 | [FACT 产物] |
| 家族数 | 9 | [FACT 产物] |
| 障碍区域 | x,y ∈ [−10, 10] m（180 个世界全部相同） | [FACT 产物] |
| 起点 | (0, 0, 2.0) m（180 个世界全部相同） | [FACT 产物] |
| 障碍高度 | 中心 z ∈ [0.40, 4.00] m；顶面最高 6.97 m | [FACT 产物] |

按家族的障碍规模（每世界障碍数 / 形状 / 尺寸范围）：

| 家族 | 世界数 | 障碍数 | 形状 | 尺寸范围 |
|---|---|---|---|---|
| bottleneck_corridor | 19 | 40 | 圆柱 | r 0.20–0.60 m |
| cul_de_sac_trap | 18 | 25–30 | 箱+圆柱 | 箱 0.5–6.0 × 0.5–3.5 × 3.0–5.0 m；圆柱 r 0.20–0.60 m |
| double_gate_progressive | 21 | 4 | 箱 | 0.5 × 0.5 × 5.0 m |
| front_offset_obstacle | 20 | 1 | 圆柱 | r 0.87–1.49 m |
| initial_yaw_offset_corridor | 21 | 2 | 箱 | 14.0 × 0.5 × 5.0 m |
| mid_impulse_recovery | 21 | 4 | 箱+圆柱 | 箱 6.0 × 0.5 × 2.1–4.9 m；圆柱 r 0.42–1.00 m |
| mixed_3d_low_density_route | 21 | 8 | 箱+圆柱 | 箱 0.80–1.49 × 0.80–1.46 × 0.81–6.97 m；圆柱 r 0.30–1.47 m |
| s_turn_multi_obstacle | 18 | 28 | 圆柱 | r 0.20–0.70 m |
| xy_z_combined_bypass | 21 | 6 | 箱+圆柱 | 箱 2.0–8.0 × 0.5–3.0 × 0.5–5.0 m；圆柱 r 0.30–0.70 m |

### 3.2 原任务评价几何

| 项目 | 值 | 状态 |
|---|---|---|
| 几何数 / 任务数 / 重复数 | 21 / 84 / 5（共 420 个任务—重复单元） | [FACT 产物] 已定位清单 |
| 清单文件 | `data/outputs/diagnostics/routea_bc_a0_r1_paired_dev_20261010_py38fix_run02/bank/bank.json` | [FACT 产物] |
| 计数判据 | `tasks` 长度 = 84；`world_id` 去重 = 21 | [FACT 产物] |
| 家族构成（按几何计） | bottleneck_corridor 5、s_turn_multi_obstacle 5、cul_de_sac_trap 5；front_offset_obstacle / initial_yaw_offset_corridor / xy_z_combined_bypass / mid_impulse_recovery / mixed_3d_low_density_route / double_gate_progressive 各 1 | [FACT 产物] |
| 引用方式 | `scripts/run_routea_paired_comparison.py:12` 的 `REFERENCE_NAME` 默认指向该目录，未传 `--reference` 时自动加载其 `bank/bank.json` | [FACT 代码] |
| 初始状态冻结方式 | 每个 episode 的初始观测落盘为 `initial/<key>.npz`，其 sha256 与 `observation_hash` 一并写入 `bank.json`，由 `bank.py:check_bank` 复核；评价时下发给策略的首帧观测即这些冻结数组（加载后校验 hash 相等） | [FACT 代码] |

说明：worlds/ 目录 180/60/52 是可用世界总数（train/val/test），21 个几何是从中抽取的固定评价子集，两者不冲突。

补充（初始观测的可复现性，B1 期间实测 1260 次 reset = 3 个缩放档 × 420 回合）：包内渲染器 `SynthPointCloud` 的 CUDA 光线投射与 bank 冻结数组**并非逐位可复现**。648/1260（54.5%）次实时重渲染与冻结数组不逐位相同，涉及 225/420 个回合，表现为两种形态：

- **(a) 值级 float32 差异**（634 次）：逐点最大差中位 1.4e-4 m，p95 6.7e-4 m，最大 1.8e-3 m。
- **(b) 有效射线数翻转**（5 个回合、14 次）：擦边射线在命中/未命中之间翻转（25058 → 25059 条）。每帧点云从全部命中射线中随机抽取 4096 点，多 1 条射线会整体重抽子集，逐点最大差达 8.03 m。

该差异不是随机噪声：同一进程内同配置重复渲染逐位相同（同一回合连续 4 次给出完全相同的差值 8.031587 m），两个独立进程给出完全一致的取值序列；是否与冻结数组相同取决于进程内的环境创建顺序——同一进程首个创建的环境复现 bank，其后创建的环境可能出现上述偏差。[FACT 产物]

因此评价下发的首帧观测一律取 bank 冻结数组 `initial/<key>.npz`（加载后校验 `observation_hash` 相等，且实时状态与冻结 `agent_pos` 逐位相等），实时重渲染只写入审计记录、不参与判决。三个缩放档因此共享完全相同的初始观测，逐回合配对成立：418/420 个回合三个档的重渲染偏差完全相同，2 个例外（`af2bbe06…`、`a00e6a5f…`）仅因 s=0 档中途重启、环境创建顺序与另两档不同。

---

## 4 软硬件

| 项目 | 值 | 来源 | 状态 |
|---|---|---|---|
| **训练机** | AutoDL 云实例，单卡 **RTX 4090 24 GB**，16 vCPU，120 GB 内存 | `program/jindu/IMPLEMENTATION_LOG.md:2151`（E5 全部 ckpt 自 AutoDL 下载后关机）；规格见实例记录 | [FACT 文档] |
| 训练软件环境 | Ubuntu 20.04 镜像 + Python 3.8 + CUDA 11.x（conda env `idp3`） | 同上；torch 具体版本未在产物中记录 | [FACT 文档] |
| 评价机（本机） | WSL2 Ubuntu 20.04.6，RTX 4060 Laptop 8 GB，20 vCPU，7.8 GB 可见内存 | 本机实查 | [FACT 产物] |
| 评价环境 | Python 3.8.20 / torch 2.4.1+cu121 / diffusers 0.36.0 | `python -c` | [FACT 产物] |

补充（环境事实，影响复现）：旧管线模块 `diffusion_policy_3d/policy/lora_adapters.py:152` 使用了 PEP 585 注解 `OrderedDict[str, torch.Tensor]`，在 Python 3.8 下导入即失败；生产后训练走 `dppo_uav_rebuild/actor_ddpm/lora.py`（无此问题）。引用 LoRA 参数量时须以 rebuild 实现为准。

---

## 5 预训练超参数（来自 ckpt 保存的解析后配置）

| 项目 | 值 |
|---|---|
| 优化器 | AdamW，lr 1e-4，betas (0.95, 0.999)，eps 1e-8，weight_decay 1e-6 |
| 学习率调度 | cosine，warmup 500 步 |
| 批大小 | 60 |
| 训练轮数 / 步数 | 301 epochs / 246,218 steps（ckpt `global_step`） |
| EMA | 启用 |
| 扩散步 | 训练 50、推理 10（DDIM），x0-prediction |

---

## 6 耗时

| 项目 | 值 | 依据 | 状态 |
|---|---|---|---|
| BC 预训练 | 约 9 h 56 min（2026-08-16 08:53:26 → 18:49） | 运行目录名（Hydra 启动时刻）→ `latest.ckpt` 写入时刻 | [FACT 产物] |
| 后训练 384 轮总时长 | 约 35 h 57 min（2026-10-12 13:30 → 10-14 01:27） | `metrics_update_000001.json` → `metrics_update_000384.json` 的文件时间戳；真实起点早于首条 metrics，故实际 ≥ 36 h | [FACT 产物] |
| 第 32 轮对应时长 | 约 2 h 53 min（13:30 → 16:23） | 同上，u1 到 u32 的时间戳差 | [FACT 产物] |

后训练运行目录：`program/results/routea_training/routea_r1_s2_seed202609203_fresh384_v1/`；权重目录：`data/outputs/dppo_uav_rebuild/routea_r1_s2_seed202609203_fresh384_v1/checkpoint_update_000032/`。

### 6.1 单次决策推理延迟（B2，实测）

| 项目 | 值 | 状态 |
|---|---|---|
| 硬件 / 软件 | RTX 4060 Laptop 8 GB；Python 3.8.20 / torch 2.4.1+cu121；batch size 1 | [FACT 产物] |
| 计时口径 | 一次完整 `predict`：点云编码 + 10 步 DDIM 采样 + 反归一化；每次调用后 `torch.cuda.synchronize()`，空载 GPU | [FACT 代码] |
| 预热 / 样本数 | 20 次预热 + 200 次计时 | [FACT 产物] |
| 均值 / p50 / p95 | 209.79 / 203.33 / 257.06 ms | [FACT 产物] |
| 最小 / 最大 | 174.01 / 331.06 ms | [FACT 产物] |
| 重复性 | 独立测量两次（均在上述参考 flag 下、GPU 空闲）均值 209.79 与 209.80 ms | [FACT 产物] |

对应闭环控制频率上限约 4.8 Hz（均值 209.8 ms），高于当前执行协议的名义 3.3 Hz（每 0.3 s 一次决策），推理不构成瓶颈。该数字不含环境推进（运动学积分与点云渲染）耗时。

---

## 7 仍然缺口（入稿前需决策）

1. **示范采集环境数量与家族构成**：不可恢复，但**入稿不需要**——正文只写「固定的 EGO 专家示范集，988 回合 / 60151 帧」，未断言环境数量。可用的替代实测量是采集时间分布（§1）。`avoidance_dataset/rosbags/` 只有 2 个 4 KB 的 `avoidance_1.bag`、`avoidance_3.bag`，是空壳；`catkin_ws0/scripts/merged_world_1.xlsx` 是数据集摘要表，不含世界清单。
2. **碰撞辅助损失 λ 的实参**：ckpt 存的是部署配置（`_target_` = `DiffusionPointcloudPolicy`，`cfg.policy` 无任何 collision 键）；训练用的是其子类 `Phase1aPolicy`（`phase1a_policy.py:35`），λ 默认 `0.5`（`phase1a_policy.py:67`，配套 `collision_d_safe=0.75`、`beta=20.0`、`tau_softmin=5.0`）。`logs.json.txt` 每轮记录 `collision_loss` / `coll_loss_ratio`，证明该项确实参与训练，但没有逐次 λ 记录，运行目录也没有 `.hydra/overrides.yaml`。λ=0.5 现由三条独立证据支持：（a）`phase1a_policy.py:876,879` 定义 `collision_loss = λ·coll_loss_raw` 且 `coll_loss_ratio = coll_loss_raw/diff_loss`，因此 λ 可由日志反算；（b）`logs.json.txt` 16 条记录反算得 λ = 0.4525–0.4956，中位 0.475（偏差来自日志为 epoch 级统计而非逐 iter）；（c）`program/shiyan/E5_convergence_20260816/analysis-report.md` 把该档明确记为 λ=0.5，与 λ=0.05 / 0.3 / bc_no_coll 同表对比。[FACT 代码 + FACT 文档]
3. **训练时的 torch 版本**：训练机为 AutoDL RTX 4090（见 §4），镜像/conda 的 torch 版本未进产物。[缺口] 不影响结论复现。
4. **推理延迟**：已测，见 §6.1（原缺口关闭）。
