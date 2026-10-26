# UAV 轻量 RL 环境：GitHub 实践核验与风险纠偏

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-08-31 |
| 文档类型 | 联网研究报告；不是实施设计或执行指导 |
| 版本 | v1.0 |
| 状态 | 已完成公开源码核验；未运行外部项目，未修改训练代码 |
| 范围 | 轻量训练/评估环境：碰撞、地面、观测、动作分段、扰动、截断 |
| 明确排除 | Gazebo/PX4、实物部署、动态障碍任务扩展、替换 DPPO 主算法 |
| 资料归档 | `论文/被参考/2026-08-31_UAV_RL_Environment_GitHub/` |
| 元数据 | `论文/被参考/metadata/2026-08-31_UAV_RL_Environment_GitHub.json` |

## 0. 项目进展与问题定位

[FACT] 用户报告 E5 DDPM DPPO Seed1 完成 256 outer updates；128 对 lightweight endpoint 中 BC/RL SR 为 33/128、42/128。本轮没有重跑，也没有重新核验 WSL 日志。这些数字只用于确定研究阶段，不作为本报告新增实测。

[FACT] 用户已明确：安全到达是主目标；提前避障、密集障碍/死胡同恢复、低支持度 xyz 空间扩展为能力方向；没有降落任务，不能通过触地、地下绕行取得成功。本轮用户要求不关注 Gazebo，先查可借鉴的 GitHub 实践。

[FACT] 已查阅本项目 2026-08-28 正式长训研究、环境设计 v1.3、Clean Rebuild 实施计划及当前 Windows 镜像/WSL 快照。根目录 `CLAUDE.md`、`program/jindu/jindu.txt` 未找到，因此不以 AGENTS 中旧阶段描述覆盖用户的新实验报告。

[JUDGMENT] 本轮目标不是寻找一套可整体替换的无人机 RL 系统，而是找到能改善现有环境真实性、且不破坏 diffusion 策略归因的具体实现。公开仓库中的实现是参考证据，不因有论文或 star 就自动适用于本项目。

## 1. 被采纳资料与可迁移范围

| 项目 | 相似性与实际读取位置 | 本轮采用 | 不直接采用 |
|---|---|---|---|
| [NavRL](https://github.com/Zhefan-Xu/NavRL)；arXiv:2409.15634 | UAV、PPO、激光/深度、障碍导航；`isaac-training/training/scripts/env.py` | 高度失败独立于障碍失败；半径意识；range 观测语义 | velocity action、外部 safety shield、固定高度区间惩罚、其 SR 定义 |
| [Aerial Gym](https://github.com/ntnu-arl/aerial_gym_simulator)；arXiv:2503.01471 | UAV RL、ray-casting、并行训练；`env_manager.py`、`navigation_task.py`、sensor 文件 | 子步碰撞事件累计；碰撞覆盖成功；先结算旧回合再 reset/更新传感器；no-hit 分类 | Isaac 平台迁移、其 reward 数值、其超时末状态成功定义 |
| [QuadSwarm](https://github.com/Zhehui-Huang/quad-swarm-rl)；arXiv:2306.09537 | Python/Numba UAV 动力学与 RL；`quadrotor_dynamics.py`、`quadrotor_single.py` | 位置/速度/加速度的连续积分、motor lag/noise 与扰动作用层次 | direct-thrust action、群体任务、碰地/碰墙后继续飞行语义 |
| [FCL](https://github.com/flexible-collision-library/fcl) | 通用几何库，非 UAV 策略 | 碰撞/距离/连续碰撞的区别；运动中接触时间 | 本轮不安装，不强制成为新依赖 |
| [Diffusion Policy](https://github.com/real-stanford/diffusion_policy) | diffusion action chunk；`diffusion_unet_hybrid_image_policy.py` | 预测长度与执行长度可分离的直接源码证据 | 机器人任务参数、BC loss 作为 DPPO 奖励归因依据 |
| [SB3](https://github.com/DLR-RM/stable-baselines3) 与 [Gymnasium](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/) | PPO collector 与 Gym 协议 | buffer 边界与 episode 边界区分；真实终态 bootstrap | 替换官方 DPPO loss 或拷贝其 action clipping |

[FACT] 本轮固定源码提交：NavRL `3725bcc2e7c1be4ecf1455d922299ae85042603a`；Aerial Gym `f0d0f05283f7897bab5a1bcc7b19b91cebbab218`；QuadSwarm `e18d6925f73e3d3b35a8acb056817203ff7b8b07`；SB3 `3246f5060eacd8bff4de575eaafbbc6e0baac376`；Diffusion Policy `5ba07ac6661db573af695b419a7947ecb704690f`；FCL `e5efcc41b57b2d0da3bf183480f1298a6d531f44`。资料下载为原始字节副本，不执行下载的代码。

## 2. 能直接借鉴的工程实践

### 2.1 碰撞必须覆盖执行过程，且碰撞事件不能被后续状态覆盖

[FACT] Aerial Gym 在一个环境 step 内循环多个 physics step，并在各子步更新 collision tensor；该 tensor 在环境 step 开始清零，接触事件累计到最终 reward/termination。证据：归档 `AerialGym_env_manager.py:342,359,399,426`；物理接触来源见 `AerialGym_IGE_env_manager.py:296,473,494`。

[FACT] FCL 的 README 明确区分静态位置碰撞与 continuous collision detection；后者接收起止变换，查询运动过程是否接触及接触时刻。证据：归档 `FCL_README.md` 的 Continuous collision 与 `continuousCollide` 段。

[JUDGMENT] iDP3 无需因此更换仿真器。可迁移的是：检查当前位置到第一个已执行 waypoint，以及所有已执行 waypoint 之间的运动；一旦任一段触地/碰撞，该 step 必须保留失败事实。只验证终点或离散点不够。

[PROVEN] 对静态障碍集合 $O$、球形机体半径 $r$ 和线性执行段 $p(t)=(1-t)p_0+tp_1$，碰撞条件是 $\min_{t\in[0,1]}\operatorname{dist}(p(t),O)\le r$，而不是只检查 $p_0,p_1$。机体用非球形包络时应采用相应碰撞体；本报告没有证据给出本项目应取的具体半径。

[PROVEN] 对平面地面 $z_g$ 和垂直半厚度 $r_z$，触地条件为 $\min_t[p_z(t)-r_z]\le z_g$。这约束的是机体最低点，不是仅要求中心 $z>0$。具体 $r_z$、容差、地面高度须由本项目资产给出。

[FACT] 当前快照 `_check_collision()` 仅循环 waypoint，最后检查 `_drone_pos[2]<0.2`；`drone_radius=0.35` 定义与 `collision_thresh=0.10` 的几何含义未闭合。引用：`wsl_snapshot/formal_endpoint_20260830/diffusion_policy_3d/env/kinematic_uav_env.py:204,940-979`。其依赖 `collision_geom.py` 不在可见快照内，不能断言 0.10 一定是机身中心半径，也不能自行把阈值改成 0.35。

### 2.2 碰撞、成功、超时应互斥结算

[FACT] Aerial Gym 在统计成功时显式排除 crashes，在统计 timeout 时也排除 crashes。证据：`AerialGym_navigation_task.py:318-328`。同一文件 `291-347` 明确排列 reward、termination、reset、传感器更新的时序。

[FACT] NavRL 将 `z<0.2`、`z>4` 和 collision 纳入 terminated；time limit 单独作为 truncated。证据：`NavRL_env.py:570-587`。但其 `reach_goal` 仅在该位置写入统计，不加入 terminated；这不是本项目“安全到达即成功结束”的直接模板。

[FACT] 当前 clean adapter 的 `TransitionFacts.resolve()` 已优先 collision，再 early_death，再 reached，再 time_limit；base env 的 reward terminal 分支却优先 reached。引用：`chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/environments/task_spec.py:53-69`、`environments/kinematic_adapter.py:29-66`、快照 `kinematic_uav_env.py:831-840`。

[JUDGMENT] 保留 clean adapter 的失败优先语义，并统一底层调用入口；不能把重复实现风险误述为“本次正式评估已证实把碰撞算成功”。

### 2.3 no-hit 是观测状态，不自动等于坏帧

[FACT] Aerial Gym 的 ray kernel 使用独立的 no-hit 距离和 segmentation 标记；sensor 层分别处理超量程、近距无效值与噪声。证据：`AerialGym_warp_camera_kernels.py:3-4,55-59`、`AerialGym_warp_sensor.py:197-245`、`AerialGym_base_depth_camera_config.py:46-52,68-71`。

[FACT] NavRL 将量程外距离 clamp 到最大 range，再形成 range-minus-distance 的激光表示。证据：`NavRL_env.py:437-442`。这是量程编码，不是把虚构远平面当作已命中障碍面。

[JUDGMENT] 本项目应区分三件事：①合法开阔空间/超出量程；②近距、掉帧、非有限数据等传感器无效状态；③世界/坐标/raycast 实现错误。不能只因 hit_count=0 就丢弃整个 episode，也不能把 no-hit 补点直接当成障碍真值。现有 4096×3 BC 接口如何表示合法空视野，须对照 BC 预处理，不能直接增加 mask channel 或随意改 normalizer。

[FACT] 当前 `inference.py:75-83` 仅检查 shape/finite，`pointcloud_gate.py:15` 定义了 validator 但主路径未接入；这证明缺少语义分流，不证明每一条 no-ray-hit 都是坏观测。底层 `synth_pointcloud.py` 当前不可见，仍需源码确定。

[JUDGMENT] 特别对 full-space support expansion，若把开阔高空一律当作 invalid obs，反而会删掉最需要学习的状态。地面非法状态必须在环境真值层失败，不应通过抬高合成相机位置掩盖。

### 2.4 轻量仿真不等于允许位置/速度互相矛盾

[FACT] QuadSwarm 以时间步积分位置、速度和旋转，包含电机响应、推力噪声和阻尼。证据：`QuadSwarm_quadrotor_dynamics.py:498-565,643-648`。

[JUDGMENT] 可借鉴其“扰动进入动力学，再产生位移”的因果顺序；不要求引入其整套 direct-thrust 仿真。当前 11d 轨迹接口应保持，先核对 $\Delta p/\Delta t$ 与 velocity、$\Delta v/\Delta t$ 与 acceleration 的含义和一致性，再决定是否需要简化跟踪模型。

[FACT] QuadSwarm 的 `floor_interaction_numba` 会将位置放到地面、更新接触状态和动力学；单机 `_step()` 的 done 主要由时间预算决定，并对 staying-on-floor 施加代价。证据：`QuadSwarm_quadrotor_dynamics.py:570-639`、`QuadSwarm_quadrotor_single.py:45-58,341-357`。`QuadSwarm_room.py` 还模拟碰墙后的速度变化。

[JUDGMENT] 上述接触后继续模拟是它的任务选择，不应照搬。本项目碰地即失败，不允许靠落地后滑行/再次起飞完成避障。

## 3. 不能照搬的 UAV 经验

[FACT] NavRL 的高度惩罚鼓励无人机留在起点/目标点高度构成的带内，带外有二次惩罚（`NavRL_env.py:563-577`）；动态障碍可以由配置数量设为 0（`NavRL_train.yaml:24-27`）。

[JUDGMENT] 只借鉴高度底线，不借鉴其压窄高度带的目标，否则可能惩罚合法上绕/下绕，削弱 full-space expansion。类似地，不照搬 NavRL 从有限视场激光推断所有静态碰撞的做法，也不采用论文的外部 velocity-obstacle safety shield（arXiv:2409.15634 摘要明确说明）。

[FACT] Aerial Gym 的示例环境 `create_ground_plane=False`，其地面是否由其他资产构成还需检查（`AerialGym_env_with_obstacles.py:33-37`）。因此，不能因采用知名仿真器就默认本任务地面规则已经成立。

[JUDGMENT] 三个 UAV 项目证明了模块分层、物理状态和观测语义值得借鉴；没有一个直接提供“E5 DDPM+官方 DPPO+11d chunk+三类目标”的等价系统。不复制其 reward 权重、训练步数、动作维度或外部安全修正。

## 4. 对上轮风险判断的修正

### 4.1 预测 8 步、执行 4 步不是自动错误

[FACT] Diffusion Policy 先生成完整 `action_pred`，再使用 `start=To-1`、`end=start+n_action_steps` 截取执行动作。证据：`DiffusionPolicy_unet_hybrid.py:266-276`。长预测、短执行是 rolling/receding-horizon 的正常方式。

[JUDGMENT] 撤回“预测/执行长度不同本身就是 P0”的表述；不建议为了相等而把本项目未来轨迹奖励一刀切砍掉，这可能损伤提前避障学习。

[FACT] 本地 reward 调用传入 8 步 world waypoint，`h_future=8`；trainer 的官方 loss 参数为 `reward_start=2,reward_horizon=4`。引用：快照 `kinematic_uav_env.py:858-866`、`reward_v13.py:45,720,815,919-934`；`chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/engine/trainer.py:15-24,132-133`。

[JUDGMENT] 真正待核对的是奖励随机变量和策略 likelihood 的覆盖，而不是两个整数是否相等。若奖励含未执行尾部的函数，不能不加论证就认为只对执行前缀评分与完整动作评分等价。对联合动作 $a=(a_e,a_u)$，一般有 $\nabla E[R(a_e,a_u)]=E[R\nabla\log p_\theta(a_e,a_u)]$；仅保留前缀项需要条件独立、尾部边缘化或另一个有效估计器的论证。此式用于指出审计条件，不是把 DPPO 的 denoising-MDP 实现直接替换为普通 PPO。尚无证据证明 Seed1 已经利用尾部作弊。

### 4.2 训练有扰动、评估无扰动可构成合法实验

[FACT] 本地训练开启 disturb，正式 endpoint 关闭 disturb；二者确实不同。引用：`chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/config/train_e5_dppo_formal_seed1_v1.yaml:48`、`chengxu/Improved-3D-Diffusion-Policy/scripts/evaluate_dppo_uav_formal_endpoint.py:304-306`。

[JUDGMENT] 训练随机化、名义条件评估本身不违反 RL 原理；可用于测量名义性能。不能用该无扰动结果证明扰动鲁棒性，也不能据此断言 66% early_death 一定由扰动造成。若之后要回答鲁棒性，只需把同 checkpoint/同世界/同起终点的有扰动表现单独报告，不立即重训或混合不同条件的 SR。

[JUDGMENT] 应保留的风险是扰动模型的物理含义：当前最终位置跳变不等于风力；若按位移扰动模拟跟踪误差，也必须定义该段运动并检查碰撞。参数来源、作用对象、单位和时间尺度需可追溯。

### 4.3 collection boundary reset 是可优化偏差，不等于 GAE 已错

[FACT] SB3 的 `collect_rollouts()` 重置的是 rollout buffer；持续保留 `_last_obs`，边界计算下一状态价值；对 TimeLimit 使用 reset 前 `terminal_observation` bootstrap。证据：`SB3_on_policy_algorithm.py:182-187,234-262`；Gymnasium 官方说明区分 terminated 与 truncated。

[FACT] 本地 pipeline 在 collection boundary 构造 truncation 并重新 reset adapter；但 next_value 对非 terminated 状态仍会计算，因此不能断言它把 buffer 边界的 bootstrap 置零。引用：`entrypoints/pipeline.py:281-337`。

[JUDGMENT] 每轮单环境串行收集至 1024 transitions，最多在末尾切断一个未结束 episode；影响应按 `collection_boundary` 及被截断 episode 的长度/角色统计，不宜未经量化称为严重系统性丢失。推荐借鉴 SB3 跨 batch 保持 episode 状态；这是训练状态分布优化，不把它单独设为阻止一切长训练的门禁。

### 4.4 no-ray-hit 不能一概 hard-drop

[JUDGMENT] 上轮将 no-ray-hit 直接称为无效观测过于绝对。新的准确判断是：需识别合法无回波和观测生成故障，避免把 no-hit 伪装成真实障碍点，同时保证 BC 输入协议。详见 §2.3。若现有设计要求所有 hit_count=0 均拒绝，应先修订该语义，而不是直接把旧 validator 接上。

## 5. GitHub 调试个案：可以借鉴排查顺序，不能当普遍定律

[FACT] Aerial Gym [issue #52](https://github.com/ntnu-arl/aerial_gym_simulator/issues/52) 报告运行导航示例时大量第 1 step crash 和连续 reset，附有完整控制台日志。本轮只把它当作用户报告，未找到足以证实通用根因/修复的证据。归档：`AerialGym_issue52.html`。

[JUDGMENT] 对本项目的启示是：若出现大量极早死亡，先按失败时刻和类型拆分，检查 reset 初态、接触事实、观测身份和扰动，再解释为模型能力差或调整 reward；但不能套用该 issue 的故障原因，也不要求新增短训。

[FACT] NavRL 自身使用固定 seed、collector、训练统计和定期 eval；`NavRL_train.py:74-120` 可见 collector 与评估/reset 过程。其配置 `max_frame_num=12e8`、`num_envs=2` 等是该仓库模板，并非 iDP3 的推荐预算。它只能支持训练预算、并行规模、episode 预算应分别明确，不能支持直接抄数。

## 6. 未采纳或仅筛选的候选资料

| 候选 | 检索到的相关性 | 本轮未采用原因 |
|---|---|---|
| `uzh-rpg/agile_flight` | 密集障碍、视觉飞行、固定环境难度 | 本轮已有更直接的 Python 环境证据；没有深入其仿真子模块，不宣称核验了其碰撞实现 |
| `ntnu-arl/active-perception-RL-navigation` | 有限视场/主动感知 | 会扩展到新策略结构；本轮只需要保证现有观测语义 |
| `heleidsn/UAV_Navigation_DRL_AirSim` | UAV 局部导航 | 没有继续做源码级核验；不从 README 宣称已适配本项目 |
| GRPO-MDP（DOI:10.1016/j.aej.2026.02.024） | diffusion + UAV RL，用户此前给出的论文 | 已有 08-28 研究；本轮未核实到可采用的作者官方 GitHub 仿真源码，不重复推导其参数或引入 CBF |
| 聚合网站、Reddit、个人作业型 2D drone demo | 可用于发现项目 | 不作为技术结论的一手依据 |

## 7. 面向 iDP3 的最小工程建议

[JUDGMENT] 建议顺序为“环境事实正确 → 保留有效学习 → 完整预算看能力”，不另建多重门禁，也不让短训收益决定正式训练资格。

1. **优先落实物理/观测真值。** 接触与扫掠碰撞、不可恢复的触地失败、互斥终止、合法 no-hit 与生成故障分流。只修正环境，不修改策略轨迹以救场。碰撞体尺寸和 empty-cloud 表示必须取自项目实际合同。
2. **核对 reward/action 合同。** 保留预测 8 步与执行前缀，审计 future-clearance 等动作条件奖励与 likelihood 评分范围；用明确推导决定是否修改，而不是按数值相等改代码。任何改动不得抹掉提前避障和脱困奖励。
3. **把其他项并入正式训练可观测性。** collection-cut 次数/角色、名义与扰动条件、位移/速度/加速度一致性、逐类失败；不因这些“潜在风险”自动增加多个独立训练阶段。

[JUDGMENT] 最少需要保留的证据包括：ground_contact、swept_collision、首个接触位置/执行段、合法 no-hit/invalid-obs 分类、reward term、episode 秒数、collection cut、按三类 role 的安全到达表现。不存在统一适用的任意阈值；阈值来自机体、坐标/观测合同和任务时限。

[UNCERTAIN] `collision_geom.py`、`traj_utils.py`、`synth_pointcloud.py` 不在当前可见 Windows 快照；本轮不访问 WSL。最终实现仍需把这些文件的实际语义纳入核对，尤其是距离是否已经减去机体半径、11d 转换以及无回波补点。

## 8. 风险与 MC 合规

| 风险/约束 | 本报告的处理 |
|---|---|
| 机体膨胀过大，误杀真实可行的密集通道 | 不照搬 NavRL 的 0.3m，也不自行采用快照的 0.35m；区分实际机体与 soft safety margin |
| 全部 no-hit hard-drop，抹去高空/开阔区域探索 | 区分观测原因，保留合法无回波状态，兼容冻结 BC 输入 |
| 为统一 horizon 砍掉 look-ahead，损害提前避障 | 只审计归因，不默认改短预测和 future reward |
| 任意增大扰动，把学习变成反复早死 | 声明扰动的物理/统计来源、时间尺度，名义与扰动分开评价 |
| MC-1 / MC-5 | 只检验执行轨迹，不做 repulsion、projection、轨迹重写；失败不算成功 |
| MC-2 / MC-3 | 保留 diffusion/官方 DPPO 核心，约束进入环境真值与学习；不引入外部 shield |
| MC-4 | 不重采集专家数据，不把 eval-only 世界加入训练 |
| 用户流程要求 | 仅研究和归档；不改源码/配置，不在 Windows 跑测试，不新增短训收益门禁 |

[JUDGMENT] 结论：最值得采用的是 Aerial Gym 的“逐子步保留碰撞事实、失败优先和传感器分层”、NavRL 的“导航目标与底线终止分开”、QuadSwarm 的“轻量也保持动力学因果关系”；同时明确不照搬它们的完整任务语义。上轮把 horizon 差异、无扰动评估和所有 no-hit 一并列为 P0，证据不足，本报告予以纠正。

## 9. 自检与证据边界

- [x] 只讨论非 Gazebo 范围，没有建议搭建新仿真平台。
- [x] UAV 项目具体实现已读源码，提交和文件 hash 在 metadata 中固定。
- [x] 论文只使用已读取的摘要信息，未声称本轮阅读全文或复现实验。
- [x] GitHub issue 标为个案，未转述为作者确认的通用根因。
- [x] 本地证据区分 Windows 快照、用户回报与未提供的 WSL 依赖。
- [x] 所有新增建议均保留 MC 边界、三类能力目标及安全到达优先。
- [x] 已明确纠正过强判断，没有把潜在风险全部升级为训练准入门禁。
