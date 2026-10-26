# 2026-09-01 常规 RL 策略 GitHub 基线检索元数据

- 检索日期：2026-09-01（Asia/Shanghai）
- 用途：期刊论文对比方法筛选；核对常规无人机 RL 实现、预训练权重、输入输出和部署环境
- 边界：本轮仅检索、下载 README 快照和读取 Git tree；未运行外部代码，未在本项目中加载外部 checkpoint
- 研究报告：`论文/研究报告/2026-09-01_无人机常规强化学习GitHub基线检索与期刊对比建议.md`

## 已归档项目

| 项目 | 固定提交 | 许可证 | 归档文件 | 引用用途 |
|---|---|---|---|---|
| [AirGym](https://github.com/emNavi/AirGym) | `bdaa61f6f1ce8df2e18ddec40762d08e16fa389c` | BSD-3-Clause | `AirGym_README_bdaa61f6.md` | 核对 PPO、depth input、`planning_cnn_rate.pth` 及本地播放命令 |
| [ntnu-arl/rl_nav](https://github.com/ntnu-arl/rl_nav) | `93ce43eada8ea207b57bca68876214cc83f8e2be` | BSD-3-Clause | `rl_nav_README_93ce43ea.md` | 核对 APPO+GRU、337 维观测、4 维加速度/角速度动作和仓库内 checkpoint |
| [active-perception-RL-navigation](https://github.com/ntnu-arl/active-perception-RL-navigation) | `cbdfcfcbfde4dc20aa9e1561a8a99d104c807b86` | BSD-3-Clause | `active_perception_README_cbdfcfcb.md` | 核对 `examples/pre-trained_network` 中可用预训练策略及主动感知任务边界 |

README 快照 SHA-256：

- `AirGym_README_bdaa61f6.md`：`d5195b6a143cc58b4a2fdf5070a399c0a9f9f3d83eb3cd0a94645aca98614036`
- `rl_nav_README_93ce43ea.md`：`f2207c2301d1ea4dd5029b24b587b852b5cff02e46ea18402df19c626f3ff38a`
- `active_perception_README_cbdfcfcb.md`：`56693e87e296d0a1541f523ab24ba8e710a1cd4db22cfd90b42177d5fb806d88`

## 复用的既有归档

| 项目 | 固定提交 | 现有资料 | 引用用途 |
|---|---|---|---|
| [NavRL](https://github.com/Zhefan-Xu/NavRL) | `3725bcc2e7c1be4ecf1455d922299ae85042603a` | `论文/被参考/2026-08-31_UAV_RL_Environment_GitHub/` | 预训练 PPO、ROS1 Noetic/Gazebo 部署、速度控制与 safety module 边界 |
| [Aerial Gym Simulator](https://github.com/ntnu-arl/aerial_gym_simulator) | `f0d0f05283f7897bab5a1bcc7b19b91cebbab218` | 同上 | UAV RL 训练平台、碰撞避免 PPO 工程参考 |
| [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) | `3246f5060eacd8bff4de575eaafbbc6e0baac376` | 同上；`论文/被参考/RouteA_R5_official_sources_20260815/` | 统一协议 Gaussian PPO 的成熟实现候选 |
| [CleanRL](https://github.com/vwxyzjn/cleanrl) | `fe8d8a03c41a7ef5b523e2e354bd01c363e786bb` | `论文/被参考/RouteA_R5_official_sources_20260815/cleanrl_ppo_continuous_action_master_20260815.py` | 单文件连续动作 PPO 备选，便于方法审计 |

## checkpoint 存在性核验

[FACT] 本轮使用 `git ls-tree -r --name-only HEAD` 检查仓库树，未执行权重。

- AirGym：`trained/planning_cnn_rate.pth`、`trained/vae_model.pth`。
- `rl_nav`：`models/magpie_accel_policy4/checkpoint_p0/best_*.pth` 等多个 Sample Factory checkpoint。
- active-perception：`examples/pre-trained_network/default_network/checkpoint_p0/best_*.pth`。
- NavRL：官方 README 明示提供 pretrained model 及 quick demos；已在 2026-08-31 资料中归档其论文摘要和训练/部署证据。

## 版权与复现说明

[FACT] 本目录中 README 是用于学术核验的原文快照，不表示已将外部实现合并进项目。若后续复用代码或模型，必须再核对许可证、依赖版本、权重来源和训练条件。
